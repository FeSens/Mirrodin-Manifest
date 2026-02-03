#!/usr/bin/env python3
"""
MTG Spoiler Page Generator
Generates a Scryfall-style spoilers page from Obsidian markdown card files.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List

# Color mappings for MTG colors
COLOR_MAP = {
    'White': {'bg': '#f8f6e8', 'border': '#e8d8a8', 'symbol': 'W', 'gradient': 'linear-gradient(135deg, #f9f7e8 0%, #e8d8a8 100%)'},
    'Blue': {'bg': '#c1d7e9', 'border': '#0e68ab', 'symbol': 'U', 'gradient': 'linear-gradient(135deg, #c1d7e9 0%, #0e68ab 100%)'},
    'Black': {'bg': '#a69f9d', 'border': '#4b3d44', 'symbol': 'B', 'gradient': 'linear-gradient(135deg, #bab1a4 0%, #4b3d44 100%)'},
    'Red': {'bg': '#eb9f82', 'border': '#d3202a', 'symbol': 'R', 'gradient': 'linear-gradient(135deg, #f0a987 0%, #d3202a 100%)'},
    'Green': {'bg': '#9bd3ae', 'border': '#00733e', 'symbol': 'G', 'gradient': 'linear-gradient(135deg, #9bd3ae 0%, #00733e 100%)'},
    'Colorless': {'bg': '#d5ccc5', 'border': '#a19891', 'symbol': 'C', 'gradient': 'linear-gradient(135deg, #e0d8d0 0%, #a19891 100%)'},
    'Multicolor': {'bg': '#e5d08f', 'border': '#c9a227', 'symbol': 'M', 'gradient': 'linear-gradient(135deg, #f0e4a8 0%, #c9a227 100%)'},
    'Land': {'bg': '#c4b998', 'border': '#8b7355', 'symbol': 'L', 'gradient': 'linear-gradient(135deg, #d4c9a8 0%, #8b7355 100%)'},
}

RARITY_COLORS = {
    'Common': '#1a1a1a',
    'Uncommon': '#707883',
    'Rare': '#b8941c',
    'Mythic': '#d35f10',
}

MANA_SYMBOLS = {
    '{W}': ('W', '#f8f6e8', '#a88f6f'),
    '{U}': ('U', '#c1d7e9', '#0e68ab'),
    '{B}': ('B', '#a69f9d', '#4b3d44'),
    '{R}': ('R', '#eb9f82', '#d3202a'),
    '{G}': ('G', '#9bd3ae', '#00733e'),
    '{C}': ('C', '#d5ccc5', '#a19891'),
    '{X}': ('X', '#d5ccc5', '#666666'),
    '{T}': ('T', '#d5ccc5', '#666666'),
}

# Add generic mana symbols
for i in range(21):
    MANA_SYMBOLS[f'{{{i}}}'] = (str(i), '#d5ccc5', '#666666')


class Card:
    """Represents an MTG card parsed from markdown."""

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.name = ""
        self.type_line = ""
        self.rules_text = ""
        self.flavor_text = ""
        self.image_prompt = ""
        self.design_notes = ""

        # Frontmatter fields
        self.card_type = ""
        self.subtype = ""
        self.color = ""
        self.mana_cost = ""
        self.cmc = 0
        self.rarity = "Common"
        self.power = ""
        self.toughness = ""
        self.set_name = "Mirrodin Manifest"
        self.tags = []

        self._parse()

    def _parse(self):
        """Parse the markdown file."""
        content = self.filepath.read_text(encoding='utf-8')

        # Parse YAML frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1])
                    if frontmatter:
                        self._parse_frontmatter(frontmatter)
                    content = parts[2]
                except yaml.YAMLError:
                    pass

        # Parse sections
        self._parse_sections(content)

    def _parse_frontmatter(self, fm: Dict[str, Any]):
        """Parse frontmatter fields."""
        self.tags = fm.get('tags', [])
        self.card_type = fm.get('type', '')
        self.subtype = fm.get('subtype', '')
        self.mana_cost = fm.get('mana_cost', '')
        self.cmc = fm.get('cmc', 0)
        self.rarity = fm.get('rarity', 'Common')
        self.power = str(fm.get('power', ''))
        self.toughness = str(fm.get('toughness', ''))
        self.set_name = fm.get('set', 'Mirrodin Manifest')

        # Handle color
        color = fm.get('color', '')
        if isinstance(color, list):
            self.color = 'Multicolor' if len(color) > 1 else (color[0] if color else 'Colorless')
        elif '/' in str(color):
            self.color = 'Multicolor'
        else:
            self.color = color if color else 'Colorless'

    def _parse_sections(self, content: str):
        """Parse markdown sections."""
        # Get card name from H1
        name_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if name_match:
            self.name = name_match.group(1).strip()

        # Parse each section
        sections = re.split(r'^##\s+', content, flags=re.MULTILINE)

        for section in sections:
            if not section.strip():
                continue

            lines = section.strip().split('\n', 1)
            header = lines[0].strip().lower()
            body = lines[1].strip() if len(lines) > 1 else ''

            # Extract blockquote content
            blockquote_content = self._extract_blockquote(body)

            if 'card type line' in header:
                self.type_line = body.strip()
            elif 'rules text' in header:
                self.rules_text = blockquote_content or body
            elif 'flavor text' in header:
                self.flavor_text = blockquote_content or body
            elif 'image prompt' in header:
                self.image_prompt = blockquote_content or body
            elif 'design notes' in header:
                self.design_notes = body
            elif 'power/toughness' in header:
                # Handle P/T as a section (for vehicles like Glimmer-Barge)
                pt_match = re.search(r'(\d+|\*)/(\d+|\*)', body)
                if pt_match:
                    self.power = pt_match.group(1)
                    self.toughness = pt_match.group(2)

    def _extract_blockquote(self, text: str) -> str:
        """Extract content from blockquotes."""
        lines = []
        for line in text.split('\n'):
            if line.startswith('>'):
                lines.append(line[1:].strip())
        return '\n'.join(lines)

    def is_card(self) -> bool:
        """Check if this file represents a card."""
        return 'card' in self.tags or 'token' in self.tags

    def get_color_data(self) -> Dict[str, str]:
        """Get color styling data."""
        if self.card_type == 'Land':
            return COLOR_MAP['Land']
        return COLOR_MAP.get(self.color, COLOR_MAP['Colorless'])

    def get_display_type(self) -> str:
        """Get the display type line."""
        if self.type_line:
            return self.type_line
        if self.subtype:
            return f"{self.card_type} — {self.subtype}"
        return self.card_type


def render_mana_cost(mana_cost: str) -> str:
    """Render mana cost as HTML mana symbols."""
    if not mana_cost:
        return ""

    html = '<span class="mana-cost">'

    # Find all mana symbols
    pattern = r'\{[^}]+\}'
    symbols = re.findall(pattern, mana_cost)

    for symbol in symbols:
        if symbol in MANA_SYMBOLS:
            text, bg, border = MANA_SYMBOLS[symbol]
            html += f'<span class="mana-symbol" style="background:{bg};border-color:{border}">{text}</span>'
        else:
            # Unknown symbol, just show text
            html += f'<span class="mana-symbol">{symbol[1:-1]}</span>'

    html += '</span>'
    return html


def render_rules_text(text: str) -> str:
    """Render rules text with mana symbols and formatting."""
    if not text:
        return ""

    # Replace mana symbols
    pattern = r'\{([^}]+)\}'

    def replace_symbol(match):
        symbol = '{' + match.group(1) + '}'
        if symbol in MANA_SYMBOLS:
            text_char, bg, border = MANA_SYMBOLS[symbol]
            return f'<span class="mana-symbol inline" style="background:{bg};border-color:{border}">{text_char}</span>'
        return match.group(0)

    text = re.sub(pattern, replace_symbol, text)

    # Handle italic text (reminder text)
    text = re.sub(r'\*\(([^)]+)\)\*', r'<em class="reminder">(\1)</em>', text)
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)

    # Handle bold text (saga chapters, etc.)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)

    # Handle line breaks
    text = text.replace('\n', '<br>')

    return text


def render_flavor_text(text: str) -> str:
    """Render flavor text."""
    if not text:
        return ""

    # Remove markdown italics markers, will style with CSS
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = text.replace('\n', '<br>')

    return text


def generate_card_html(card: Card) -> str:
    """Generate HTML for a single card."""
    color_data = card.get_color_data()
    rarity_color = RARITY_COLORS.get(card.rarity, '#1a1a1a')

    # Determine if creature (has P/T)
    is_creature = bool(card.power and card.toughness)

    html = f'''
    <div class="card" data-color="{card.color}" data-type="{card.card_type}" data-rarity="{card.rarity}">
        <div class="card-frame" style="background:{color_data['gradient']};border-color:{color_data['border']}">
            <div class="card-header">
                <span class="card-name">{card.name}</span>
                {render_mana_cost(card.mana_cost)}
            </div>
            <div class="card-art">
                <div class="art-placeholder">
                    <span class="art-icon">🎨</span>
                </div>
            </div>
            <div class="card-type-line">
                <span class="type-text">{card.get_display_type()}</span>
                <span class="set-symbol" style="color:{rarity_color}" title="{card.rarity}">✦</span>
            </div>
            <div class="card-text-box">
                <div class="rules-text">{render_rules_text(card.rules_text)}</div>
                {f'<div class="flavor-text">{render_flavor_text(card.flavor_text)}</div>' if card.flavor_text else ''}
            </div>
            {f'<div class="card-pt"><span>{card.power}/{card.toughness}</span></div>' if is_creature else ''}
            <div class="card-footer">
                <span class="card-set">{card.set_name}</span>
            </div>
        </div>
    </div>
    '''

    return html


def generate_html(cards: List[Card]) -> str:
    """Generate the complete HTML spoiler page."""

    # Sort cards by color, then by name
    color_order = ['White', 'Blue', 'Black', 'Red', 'Green', 'Multicolor', 'Colorless', 'Land']

    def sort_key(card):
        color = card.color
        if card.card_type == 'Land':
            color = 'Land'
        try:
            color_idx = color_order.index(color)
        except ValueError:
            color_idx = 99
        return (color_idx, card.name.lower())

    cards.sort(key=sort_key)

    cards_html = '\n'.join(generate_card_html(card) for card in cards)

    # Generate filter buttons
    colors_present = sorted(set(c.color for c in cards))
    types_present = sorted(set(c.card_type for c in cards))
    rarities_present = sorted(set(c.rarity for c in cards),
                              key=lambda r: ['Common', 'Uncommon', 'Rare', 'Mythic'].index(r) if r in ['Common', 'Uncommon', 'Rare', 'Mythic'] else 99)

    color_buttons = '\n'.join(f'<button class="filter-btn" data-filter="color" data-value="{c}">{c}</button>' for c in color_order if c in colors_present or c == 'Land')
    type_buttons = '\n'.join(f'<button class="filter-btn" data-filter="type" data-value="{t}">{t}</button>' for t in types_present)
    rarity_buttons = '\n'.join(f'<button class="filter-btn" data-filter="rarity" data-value="{r}">{r}</button>' for r in rarities_present)

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mirrodin Manifest - Card Spoilers</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=EB+Garamond:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet">
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'EB Garamond', Georgia, serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f0f23 100%);
            min-height: 100vh;
            color: #e8e8e8;
            padding: 20px;
        }}

        .header {{
            text-align: center;
            padding: 40px 20px;
            margin-bottom: 30px;
        }}

        .header h1 {{
            font-family: 'Cinzel', serif;
            font-size: 3em;
            font-weight: 700;
            color: #c9a227;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            margin-bottom: 10px;
            letter-spacing: 2px;
        }}

        .header .subtitle {{
            font-size: 1.2em;
            color: #a0a0a0;
            font-style: italic;
        }}

        .header .card-count {{
            margin-top: 15px;
            font-size: 1.1em;
            color: #888;
        }}

        .filters {{
            max-width: 1400px;
            margin: 0 auto 30px;
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 20px;
        }}

        .filter-group {{
            margin-bottom: 15px;
        }}

        .filter-group:last-child {{
            margin-bottom: 0;
        }}

        .filter-label {{
            font-family: 'Cinzel', serif;
            font-size: 0.9em;
            color: #c9a227;
            margin-bottom: 8px;
            display: block;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .filter-buttons {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}

        .filter-btn {{
            font-family: 'EB Garamond', serif;
            font-size: 0.95em;
            padding: 8px 16px;
            border: 1px solid #444;
            background: rgba(255,255,255,0.05);
            color: #ccc;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .filter-btn:hover {{
            background: rgba(255,255,255,0.15);
            border-color: #666;
        }}

        .filter-btn.active {{
            background: #c9a227;
            border-color: #c9a227;
            color: #1a1a2e;
        }}

        .filter-btn.clear {{
            background: transparent;
            border-color: #c9a227;
            color: #c9a227;
        }}

        .filter-btn.clear:hover {{
            background: rgba(201, 162, 39, 0.2);
        }}

        .card-grid {{
            max-width: 1400px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 25px;
            padding: 20px;
        }}

        .card {{
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}

        .card:hover {{
            transform: translateY(-8px) scale(1.02);
            z-index: 10;
        }}

        .card.hidden {{
            display: none;
        }}

        .card-frame {{
            border-radius: 12px;
            border: 4px solid;
            padding: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
            position: relative;
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(0,0,0,0.15);
            border-radius: 6px 6px 0 0;
            padding: 8px 10px;
            min-height: 36px;
        }}

        .card-name {{
            font-family: 'Cinzel', serif;
            font-weight: 600;
            font-size: 0.95em;
            color: #1a1a1a;
            flex: 1;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .mana-cost {{
            display: flex;
            gap: 2px;
            flex-shrink: 0;
            margin-left: 8px;
        }}

        .mana-symbol {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            border: 1px solid;
            font-family: 'Cinzel', serif;
            font-size: 0.75em;
            font-weight: 700;
            color: #1a1a1a;
        }}

        .mana-symbol.inline {{
            width: 16px;
            height: 16px;
            font-size: 0.65em;
            vertical-align: middle;
            margin: 0 1px;
        }}

        .card-art {{
            background: rgba(0,0,0,0.1);
            height: 160px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid rgba(0,0,0,0.2);
        }}

        .art-placeholder {{
            text-align: center;
            color: rgba(0,0,0,0.3);
        }}

        .art-icon {{
            font-size: 3em;
        }}

        .card-type-line {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(0,0,0,0.15);
            padding: 6px 10px;
            font-size: 0.85em;
        }}

        .type-text {{
            color: #1a1a1a;
            font-weight: 500;
        }}

        .set-symbol {{
            font-size: 1.2em;
        }}

        .card-text-box {{
            background: #f8f6e8;
            border-radius: 0 0 6px 6px;
            padding: 12px;
            min-height: 100px;
            color: #1a1a1a;
            font-size: 0.85em;
            line-height: 1.4;
        }}

        .rules-text {{
            margin-bottom: 10px;
        }}

        .rules-text em.reminder {{
            font-size: 0.9em;
            color: #555;
        }}

        .rules-text strong {{
            font-weight: 600;
        }}

        .flavor-text {{
            font-style: italic;
            color: #555;
            border-top: 1px solid #ddd;
            padding-top: 10px;
            margin-top: 10px;
        }}

        .card-pt {{
            position: absolute;
            bottom: 18px;
            right: 18px;
            background: linear-gradient(135deg, #d4c9a8 0%, #8b7355 100%);
            border: 2px solid #5a4a3a;
            border-radius: 6px;
            padding: 4px 10px;
            font-family: 'Cinzel', serif;
            font-weight: 700;
            font-size: 1.1em;
            color: #1a1a1a;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}

        .card-footer {{
            text-align: center;
            padding: 6px;
            font-size: 0.7em;
            color: rgba(0,0,0,0.5);
        }}

        @media (max-width: 600px) {{
            .header h1 {{
                font-size: 2em;
            }}

            .card-grid {{
                grid-template-columns: 1fr;
                padding: 10px;
            }}

            .filter-btn {{
                padding: 6px 12px;
                font-size: 0.85em;
            }}
        }}
    </style>
</head>
<body>
    <header class="header">
        <h1>MIRRODIN MANIFEST</h1>
        <p class="subtitle">Card Spoilers Gallery</p>
        <p class="card-count">{len(cards)} cards</p>
    </header>

    <div class="filters">
        <div class="filter-group">
            <span class="filter-label">Color</span>
            <div class="filter-buttons">
                <button class="filter-btn clear" data-filter="color" data-value="all">All</button>
                {color_buttons}
            </div>
        </div>
        <div class="filter-group">
            <span class="filter-label">Card Type</span>
            <div class="filter-buttons">
                <button class="filter-btn clear" data-filter="type" data-value="all">All</button>
                {type_buttons}
            </div>
        </div>
        <div class="filter-group">
            <span class="filter-label">Rarity</span>
            <div class="filter-buttons">
                <button class="filter-btn clear" data-filter="rarity" data-value="all">All</button>
                {rarity_buttons}
            </div>
        </div>
    </div>

    <div class="card-grid">
        {cards_html}
    </div>

    <script>
        // Filter functionality
        const filters = {{
            color: 'all',
            type: 'all',
            rarity: 'all'
        }};

        function applyFilters() {{
            const cards = document.querySelectorAll('.card');
            cards.forEach(card => {{
                const colorMatch = filters.color === 'all' ||
                    card.dataset.color === filters.color ||
                    (filters.color === 'Land' && card.dataset.type === 'Land');
                const typeMatch = filters.type === 'all' || card.dataset.type === filters.type;
                const rarityMatch = filters.rarity === 'all' || card.dataset.rarity === filters.rarity;

                if (colorMatch && typeMatch && rarityMatch) {{
                    card.classList.remove('hidden');
                }} else {{
                    card.classList.add('hidden');
                }}
            }});
        }}

        document.querySelectorAll('.filter-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                const filterType = btn.dataset.filter;
                const value = btn.dataset.value;

                // Update active state
                btn.parentElement.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                if (value !== 'all') btn.classList.add('active');

                filters[filterType] = value;
                applyFilters();
            }});
        }});
    </script>
</body>
</html>
'''

    return html


def main():
    """Main function to generate the spoiler page."""
    script_dir = Path(__file__).parent

    # Find all markdown files
    md_files = list(script_dir.glob('*.md'))

    # Parse cards
    cards = []
    for md_file in md_files:
        try:
            card = Card(md_file)
            if card.is_card() and card.name:
                cards.append(card)
                print(f"✓ Parsed: {card.name}")
        except Exception as e:
            print(f"✗ Error parsing {md_file.name}: {e}")

    if not cards:
        print("No cards found!")
        return

    print(f"\nFound {len(cards)} cards")

    # Generate HTML
    html = generate_html(cards)

    # Write output
    output_path = script_dir / 'spoilers.html'
    output_path.write_text(html, encoding='utf-8')

    print(f"\n✓ Generated: {output_path}")
    print(f"  Open in browser: file://{output_path.absolute()}")


if __name__ == '__main__':
    main()
