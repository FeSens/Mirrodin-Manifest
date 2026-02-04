#!/usr/bin/env python3
"""
MTG Spoiler Page Generator - React Version
Generates pixel-perfect MTG cards using React and mana-font.
"""

import re
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List
from difflib import SequenceMatcher

# Mana symbol mapping for mana-font
MANA_MAP = {
    '{W}': '{w}', '{U}': '{u}', '{B}': '{b}', '{R}': '{r}', '{G}': '{g}',
    '{C}': '{c}', '{X}': '{x}', '{T}': '{t}', '{Q}': '{q}',
    '{0}': '{0}', '{1}': '{1}', '{2}': '{2}', '{3}': '{3}', '{4}': '{4}',
    '{5}': '{5}', '{6}': '{6}', '{7}': '{7}', '{8}': '{8}', '{9}': '{9}',
    '{10}': '{10}', '{11}': '{11}', '{12}': '{12}', '{13}': '{13}',
    '{14}': '{14}', '{15}': '{15}', '{16}': '{16}',
    '{W/U}': '{wu}', '{U/B}': '{ub}', '{B/R}': '{br}', '{R/G}': '{rg}',
    '{G/W}': '{gw}', '{W/B}': '{wb}', '{U/R}': '{ur}', '{B/G}': '{bg}',
    '{R/W}': '{rw}', '{G/U}': '{gu}',
}

COLOR_MAP = {
    'White': 'w', 'Blue': 'u', 'Black': 'b', 'Red': 'r', 'Green': 'g',
    'Colorless': 'c', 'Multicolor': 'm', 'Land': 'land'
}

RARITY_MAP = {
    'Common': 'common', 'Uncommon': 'uncommon', 'Rare': 'rare', 'Mythic': 'mythic'
}


class Card:
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.name = ""
        self.type_line = ""
        self.rules_text = ""
        self.flavor_text = ""
        self.card_type = ""
        self.subtype = ""
        self.color = ""
        self.mana_cost = ""
        self.cmc = 0
        self.rarity = "Common"
        self.power = ""
        self.toughness = ""
        self.tags = []
        self._parse()

    def _parse(self):
        content = self.filepath.read_text(encoding='utf-8')
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    fm = yaml.safe_load(parts[1])
                    if fm:
                        self.tags = fm.get('tags', [])
                        self.card_type = fm.get('type', '')
                        self.subtype = fm.get('subtype', '')
                        self.mana_cost = fm.get('mana_cost', '')
                        self.cmc = fm.get('cmc', 0)
                        self.rarity = fm.get('rarity', 'Common')
                        self.power = str(fm.get('power', ''))
                        self.toughness = str(fm.get('toughness', ''))
                        color = fm.get('color', '')
                        if isinstance(color, list):
                            self.color = 'Multicolor' if len(color) > 1 else (color[0] if color else 'Colorless')
                        elif '/' in str(color):
                            self.color = 'Multicolor'
                        else:
                            self.color = color if color else 'Colorless'
                    content = parts[2]
                except yaml.YAMLError:
                    pass

        name_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if name_match:
            self.name = name_match.group(1).strip()

        sections = re.split(r'^##\s+', content, flags=re.MULTILINE)
        for section in sections:
            if not section.strip():
                continue
            lines = section.strip().split('\n', 1)
            header = lines[0].strip().lower()
            body = lines[1].strip() if len(lines) > 1 else ''
            blockquote = '\n'.join(l[1:].strip() for l in body.split('\n') if l.startswith('>'))

            if 'card type line' in header:
                self.type_line = body.strip()
            elif 'rules text' in header:
                self.rules_text = blockquote or body
            elif 'flavor text' in header:
                self.flavor_text = blockquote or body

    def is_card(self) -> bool:
        return 'card' in self.tags or 'token' in self.tags

    def get_display_type(self) -> str:
        if self.type_line:
            return self.type_line
        if self.subtype:
            return f"{self.card_type} — {self.subtype}"
        return self.card_type

    def get_color_code(self) -> str:
        if self.card_type == 'Land':
            return 'land'
        return COLOR_MAP.get(self.color, 'c')

    def get_normalized_text(self) -> str:
        text = self.rules_text.lower()
        return re.sub(r'\s+', ' ', text).strip()

    def to_json(self) -> Dict:
        return {
            'name': self.name,
            'manaCost': self.mana_cost,
            'type': self.get_display_type(),
            'rulesText': self.rules_text,
            'flavorText': self.flavor_text,
            'power': self.power,
            'toughness': self.toughness,
            'color': self.get_color_code(),
            'rarity': RARITY_MAP.get(self.rarity, 'common'),
            'cardType': self.card_type
        }


def compute_similarity_matrix(cards: List[Card]) -> Dict[str, Dict[str, float]]:
    matrix = {}
    texts = {card.name: card.get_normalized_text() for card in cards}
    for card in cards:
        matrix[card.name] = {}
        text1 = texts[card.name]
        for other in cards:
            if card.name == other.name:
                matrix[card.name][other.name] = 1.0
            else:
                text2 = texts[other.name]
                if len(text1) > 10 and len(text2) > 10:
                    matrix[card.name][other.name] = SequenceMatcher(None, text1, text2).ratio()
                else:
                    matrix[card.name][other.name] = 0.0
    return matrix


def generate_html(cards: List[Card]) -> str:
    color_order = ['White', 'Blue', 'Black', 'Red', 'Green', 'Multicolor', 'Colorless', 'Land']

    def sort_key(card):
        color = 'Land' if card.card_type == 'Land' else card.color
        try:
            idx = color_order.index(color)
        except ValueError:
            idx = 99
        return (idx, card.name.lower())

    cards.sort(key=sort_key)

    print("Computing similarity matrix...")
    similarity_matrix = compute_similarity_matrix(cards)

    # Sort by max similarity for selector
    similarity_scores = {
        name: max([s for n, s in sims.items() if n != name], default=0)
        for name, sims in similarity_matrix.items()
    }
    cards_by_similarity = sorted(cards, key=lambda c: similarity_scores.get(c.name, 0), reverse=True)

    cards_json = json.dumps([c.to_json() for c in cards])
    cards_by_sim_json = json.dumps([c.to_json() for c in cards_by_similarity])
    similarity_json = json.dumps(similarity_matrix)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mirrodin Manifest - Card Spoilers</title>
    <link href="https://fonts.googleapis.com/css2?family=Beleren:wght@700&family=MPlantin:ital@0;1&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/mana-font@latest/css/mana.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/keyrune@latest/css/keyrune.min.css" rel="stylesheet">
    <script src="https://unpkg.com/react@18/umd/react.production.min.js" crossorigin></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js" crossorigin></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <style>
        @font-face {{
            font-family: 'Beleren';
            src: url('https://cdn.jsdelivr.net/gh/germanyn/reactjs-mtg-card/example/public/fonts/beleren-bold.ttf');
            font-weight: 700;
        }}
        @font-face {{
            font-family: 'MPlantin';
            src: url('https://cdn.jsdelivr.net/gh/germanyn/reactjs-mtg-card/example/public/fonts/mplantin.ttf');
        }}
        @font-face {{
            font-family: 'MPlantin';
            src: url('https://cdn.jsdelivr.net/gh/germanyn/reactjs-mtg-card/example/public/fonts/mplantin-italic.ttf');
            font-style: italic;
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f0f23 100%);
            min-height: 100vh;
            color: #e8e8e8;
            padding: 20px;
        }}
        .header {{ text-align: center; padding: 40px 20px 20px; }}
        .header h1 {{
            font-family: 'Beleren', serif;
            font-size: 3em;
            color: #c9a227;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            letter-spacing: 3px;
        }}
        .header .subtitle {{ color: #888; margin-top: 10px; }}

        .tabs {{ max-width: 1600px; margin: 0 auto 20px; display: flex; gap: 10px; padding: 0 20px; }}
        .tab-btn {{
            font-family: 'Beleren', sans-serif;
            padding: 12px 24px;
            border: 2px solid #444;
            background: rgba(255,255,255,0.05);
            color: #ccc;
            border-radius: 8px 8px 0 0;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .tab-btn:hover {{ background: rgba(255,255,255,0.15); }}
        .tab-btn.active {{ background: #c9a227; border-color: #c9a227; color: #1a1a2e; }}

        .filters {{
            max-width: 1600px;
            margin: 0 auto 20px;
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 15px 20px;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            align-items: center;
        }}
        .filter-btn {{
            padding: 6px 14px;
            border: 1px solid #444;
            background: rgba(255,255,255,0.05);
            color: #ccc;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9em;
        }}
        .filter-btn:hover {{ background: rgba(255,255,255,0.15); }}
        .filter-btn.active {{ background: #c9a227; border-color: #c9a227; color: #1a1a2e; }}

        .card-grid {{
            max-width: 1600px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(265px, 1fr));
            gap: 20px;
            padding: 20px;
        }}

        /* MTG Card Styles */
        .mtg-card {{
            width: 265px;
            height: 370px;
            border-radius: 13px;
            position: relative;
            font-family: 'MPlantin', Georgia, serif;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            transition: transform 0.3s, box-shadow 0.3s;
            cursor: pointer;
        }}
        .mtg-card:hover {{
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 12px 30px rgba(0,0,0,0.6);
            z-index: 10;
        }}

        .card-border {{
            position: absolute;
            inset: 0;
            border-radius: 13px;
            border: 10px solid #171314;
            background: #171314;
        }}

        .card-frame {{
            position: absolute;
            inset: 10px;
            border-radius: 6px;
            display: flex;
            flex-direction: column;
            padding: 7px;
        }}

        /* Color backgrounds */
        .card-frame.w {{ background: linear-gradient(180deg, #f8f6e0 0%, #f0edd4 50%, #e8e0c0 100%); }}
        .card-frame.u {{ background: linear-gradient(180deg, #0e68ab 0%, #1a7bc0 50%, #0a5a95 100%); }}
        .card-frame.b {{ background: linear-gradient(180deg, #4a3e4a 0%, #5a4e5a 50%, #3a2e3a 100%); }}
        .card-frame.r {{ background: linear-gradient(180deg, #d3202a 0%, #e03030 50%, #c01020 100%)); }}
        .card-frame.g {{ background: linear-gradient(180deg, #00733e 0%, #00884a 50%, #006030 100%); }}
        .card-frame.m {{ background: linear-gradient(180deg, #c9a227 0%, #d4b040 50%, #b8901a 100%); }}
        .card-frame.c {{ background: linear-gradient(180deg, #a0a0a0 0%, #b0b0b0 50%, #909090 100%); }}
        .card-frame.land {{ background: linear-gradient(180deg, #8b7355 0%, #9a8265 50%, #7a6245 100%); }}

        .title-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: linear-gradient(180deg, rgba(255,255,255,0.35) 0%, rgba(255,255,255,0.15) 50%, rgba(0,0,0,0.1) 100%);
            border-radius: 5px 5px 0 0;
            padding: 5px 8px;
            border: 1px solid rgba(0,0,0,0.3);
            border-bottom: none;
        }}

        .card-title {{
            font-family: 'Beleren', serif;
            font-size: 0.95em;
            font-weight: 700;
            color: #1a1a1a;
            text-shadow: 0 1px 0 rgba(255,255,255,0.5);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            flex: 1;
        }}

        .mana-cost {{
            display: flex;
            gap: 2px;
            flex-shrink: 0;
            margin-left: 5px;
        }}
        .mana-cost .ms {{
            font-size: 16px !important;
        }}
        .ms-sm {{
            font-size: 13px !important;
        }}

        .art-box {{
            height: 140px;
            background: #1a1a1a;
            border: 3px solid #171314;
            margin: 0 -1px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: rgba(255,255,255,0.2);
            font-size: 2.5em;
        }}

        .type-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: linear-gradient(180deg, rgba(255,255,255,0.3) 0%, rgba(255,255,255,0.1) 50%, rgba(0,0,0,0.1) 100%);
            padding: 4px 8px;
            border: 1px solid rgba(0,0,0,0.3);
            border-top: none;
            font-size: 0.75em;
        }}
        .type-text {{
            color: #1a1a1a;
            font-weight: 600;
        }}
        .set-symbol {{
            font-size: 1.1em;
        }}
        .set-symbol.common {{ color: #1a1a1a; }}
        .set-symbol.uncommon {{ color: #a8b8c8; text-shadow: 0 0 3px #fff; }}
        .set-symbol.rare {{ color: #d4a020; text-shadow: 0 0 4px #ff0; }}
        .set-symbol.mythic {{ color: #e85820; text-shadow: 0 0 5px #f40; }}

        .text-box {{
            flex: 1;
            background: linear-gradient(180deg, #f5f0e1 0%, #ebe5d0 100%);
            border-radius: 0 0 5px 5px;
            border: 1px solid rgba(0,0,0,0.2);
            border-top: none;
            padding: 8px;
            font-size: 0.72em;
            line-height: 1.3;
            color: #1a1a1a;
            overflow: hidden;
        }}
        .text-box .ms {{ font-size: 12px !important; vertical-align: middle; }}
        .rules-text {{ margin-bottom: 5px; }}
        .flavor-text {{
            font-style: italic;
            color: #444;
            border-top: 1px solid #ccc;
            padding-top: 5px;
            margin-top: 5px;
        }}

        .pt-box {{
            position: absolute;
            bottom: 15px;
            right: 15px;
            background: linear-gradient(135deg, #e8dcc8 0%, #c4b59a 50%, #9a8a70 100%);
            border: 2px solid #171314;
            border-radius: 6px 0 6px 0;
            padding: 2px 10px;
            font-family: 'Beleren', sans-serif;
            font-weight: 700;
            font-size: 1em;
            color: #1a1a1a;
            box-shadow: 0 2px 4px rgba(0,0,0,0.4);
        }}

        /* Similarity tab */
        .similarity-container {{ max-width: 1600px; margin: 0 auto; padding: 20px; }}
        .similarity-header {{
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
        }}
        .similarity-header h3 {{ color: #c9a227; margin-bottom: 10px; }}
        .card-scroll {{
            display: flex;
            gap: 15px;
            overflow-x: auto;
            padding: 10px 0;
            scrollbar-width: thin;
            scrollbar-color: #c9a227 rgba(255,255,255,0.1);
        }}
        .card-scroll::-webkit-scrollbar {{ height: 8px; }}
        .card-scroll::-webkit-scrollbar-track {{ background: rgba(255,255,255,0.1); border-radius: 4px; }}
        .card-scroll::-webkit-scrollbar-thumb {{ background: #c9a227; border-radius: 4px; }}
        .card-scroll .mtg-card {{ flex-shrink: 0; }}
        .card-scroll .mtg-card.selected {{
            box-shadow: 0 0 0 4px #c9a227, 0 12px 30px rgba(201,162,39,0.5);
        }}
        .compare-info {{
            background: rgba(201,162,39,0.1);
            border: 1px solid #c9a227;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
            display: none;
        }}
        .compare-info.active {{ display: block; }}
        .compare-info h4 {{ color: #c9a227; }}
        .similarity-badge {{
            position: absolute;
            top: -8px;
            left: -8px;
            background: #c9a227;
            color: #1a1a2e;
            font-weight: 700;
            font-size: 0.8em;
            padding: 3px 8px;
            border-radius: 10px;
            z-index: 20;
        }}
        .similarity-badge.high {{ background: #e85820; color: white; }}
        .similarity-badge.medium {{ background: #d4a020; }}
        .similarity-badge.low {{ background: #707883; color: white; }}
        .no-selection {{ text-align: center; padding: 60px; color: #888; }}
        .hidden {{ display: none !important; }}

        /* Size classes */
        .text-short .rules-text {{ font-size: 1em; }}
        .text-medium .rules-text {{ font-size: 0.9em; }}
        .text-long .rules-text {{ font-size: 0.8em; }}
        .text-very-long .rules-text {{ font-size: 0.7em; }}
    </style>
</head>
<body>
    <header class="header">
        <h1>MIRRODIN MANIFEST</h1>
        <p class="subtitle">Card Spoilers Gallery - {len(cards)} cards</p>
    </header>
    <div id="root"></div>

    <script type="text/babel">
        const cardsData = {cards_json};
        const cardsBySimilarity = {cards_by_sim_json};
        const similarityMatrix = {similarity_json};

        function ManaSymbols({{ cost, inline }}) {{
            if (!cost) return null;
            const symbols = cost.match(/\\{{[^}}]+\\}}/g) || [];
            return symbols.map((s, i) => {{
                let code = s.replace(/[{{}}]/g, '').toLowerCase();
                // Handle special cases
                if (code === 't') code = 'tap';
                if (code === 'q') code = 'untap';
                const sizeClass = inline ? 'ms-sm' : '';
                return <i key={{i}} className={{`ms ms-${{code}} ms-cost ms-shadow ${{sizeClass}}`}} />;
            }});
        }}

        function MTGCard({{ card, onClick, selected, badge }}) {{
            const textLen = (card.rulesText?.length || 0) + (card.flavorText?.length || 0);
            const sizeClass = textLen < 150 ? 'text-short' : textLen < 250 ? 'text-medium' : textLen < 400 ? 'text-long' : 'text-very-long';
            const hasPT = card.power && card.toughness;

            const formatText = (text) => {{
                if (!text) return '';
                return text.split('\\n').map((line, i) => (
                    <span key={{i}}>
                        {{line.split(/\\{{([^}}]+)\\}}/g).map((part, j) => {{
                            if (j % 2 === 1) {{
                                let code = part.toLowerCase();
                                if (code === 't') code = 'tap';
                                if (code === 'q') code = 'untap';
                                return <i key={{j}} className={{`ms ms-${{code}} ms-cost ms-shadow ms-sm`}} />;
                            }}
                            return part;
                        }})}}
                        {{i < text.split('\\n').length - 1 && <br />}}
                    </span>
                ));
            }};

            return (
                <div className={{`mtg-card ${{selected ? 'selected' : ''}}`}} onClick={{onClick}} style={{{{position: 'relative'}}}}>
                    {{badge && <div className={{`similarity-badge ${{badge.class}}`}}>{{badge.text}}</div>}}
                    <div className="card-border" />
                    <div className={{`card-frame ${{card.color}}`}}>
                        <div className="title-bar">
                            <span className="card-title">{{card.name}}</span>
                            <span className="mana-cost"><ManaSymbols cost={{card.manaCost}} /></span>
                        </div>
                        <div className="art-box">🎨</div>
                        <div className="type-bar">
                            <span className="type-text">{{card.type}}</span>
                            <span className={{`set-symbol ${{card.rarity}}`}}>✦</span>
                        </div>
                        <div className={{`text-box ${{sizeClass}}`}}>
                            <div className="rules-text">{{formatText(card.rulesText)}}</div>
                            {{card.flavorText && <div className="flavor-text">{{formatText(card.flavorText)}}</div>}}
                        </div>
                        {{hasPT && <div className="pt-box">{{card.power}}/{{card.toughness}}</div>}}
                    </div>
                </div>
            );
        }}

        function App() {{
            const [tab, setTab] = React.useState('gallery');
            const [filter, setFilter] = React.useState('all');
            const [selectedCard, setSelectedCard] = React.useState(null);

            const filteredCards = filter === 'all' ? cardsData : cardsData.filter(c => {{
                if (filter === 'land') return c.cardType === 'Land';
                return c.color === filter;
            }});

            const getSimilarCards = () => {{
                if (!selectedCard) return [];
                const sims = similarityMatrix[selectedCard.name] || {{}};
                return Object.entries(sims)
                    .filter(([name, sim]) => name !== selectedCard.name && sim > 0)
                    .sort((a, b) => b[1] - a[1])
                    .map(([name, sim]) => ({{
                        card: cardsData.find(c => c.name === name),
                        similarity: sim
                    }}))
                    .filter(x => x.card);
            }};

            const getBadge = (sim) => ({{
                text: Math.round(sim * 100) + '%',
                class: sim >= 0.8 ? 'high' : sim >= 0.5 ? 'medium' : 'low'
            }});

            return (
                <>
                    <div className="tabs">
                        <button className={{`tab-btn ${{tab === 'gallery' ? 'active' : ''}}`}} onClick={{() => setTab('gallery')}}>Gallery</button>
                        <button className={{`tab-btn ${{tab === 'similarity' ? 'active' : ''}}`}} onClick={{() => setTab('similarity')}}>Similarity Compare</button>
                    </div>

                    {{tab === 'gallery' && (
                        <>
                            <div className="filters">
                                {{['all', 'w', 'u', 'b', 'r', 'g', 'm', 'c', 'land'].map(f => (
                                    <button key={{f}} className={{`filter-btn ${{filter === f ? 'active' : ''}}`}} onClick={{() => setFilter(f)}}>
                                        {{f === 'all' ? 'All' : f === 'w' ? 'White' : f === 'u' ? 'Blue' : f === 'b' ? 'Black' : f === 'r' ? 'Red' : f === 'g' ? 'Green' : f === 'm' ? 'Multi' : f === 'c' ? 'Colorless' : 'Land'}}
                                    </button>
                                ))}}
                            </div>
                            <div className="card-grid">
                                {{filteredCards.map(card => <MTGCard key={{card.name}} card={{card}} />)}}
                            </div>
                        </>
                    )}}

                    {{tab === 'similarity' && (
                        <div className="similarity-container">
                            <div className="similarity-header">
                                <h3>Select a card to compare (scroll horizontally)</h3>
                                <div className="card-scroll">
                                    {{cardsBySimilarity.map(card => (
                                        <MTGCard
                                            key={{card.name}}
                                            card={{card}}
                                            selected={{selectedCard?.name === card.name}}
                                            onClick={{() => setSelectedCard(card)}}
                                        />
                                    ))}}
                                </div>
                            </div>
                            <div className={{`compare-info ${{selectedCard ? 'active' : ''}}`}}>
                                <h4>Comparing: {{selectedCard?.name}}</h4>
                                <p>Cards below sorted by text similarity</p>
                            </div>
                            {{!selectedCard && <div className="no-selection">Click a card above to see similar cards</div>}}
                            {{selectedCard && (
                                <div className="card-grid">
                                    {{getSimilarCards().map(({{card, similarity}}) => (
                                        <MTGCard key={{card.name}} card={{card}} badge={{getBadge(similarity)}} />
                                    ))}}
                                </div>
                            )}}
                        </div>
                    )}}
                </>
            );
        }}

        ReactDOM.createRoot(document.getElementById('root')).render(<App />);
    </script>
</body>
</html>'''


def main():
    script_dir = Path(__file__).parent
    md_files = list(script_dir.glob('*.md')) + list(script_dir.glob('cards/*.md'))

    cards = []
    for md_file in md_files:
        try:
            card = Card(md_file)
            if card.is_card() and card.name:
                cards.append(card)
                print(f"✓ {card.name}")
        except Exception as e:
            print(f"✗ {md_file.name}: {e}")

    print(f"\nFound {len(cards)} cards")
    html = generate_html(cards)

    output = script_dir / 'spoilers.html'
    output.write_text(html, encoding='utf-8')
    print(f"✓ Generated: {output}")


if __name__ == '__main__':
    main()
