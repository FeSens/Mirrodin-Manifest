#!/usr/bin/env python3
"""
MTG Set Dashboard Generator
Generates a comprehensive statistics dashboard for set design analysis.
"""

import os
import re
import yaml
import json
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from collections import Counter, defaultdict

# Color definitions
COLORS = ['White', 'Blue', 'Black', 'Red', 'Green']
COLOR_CODES = {
    'White': '#f8f6d8',
    'Blue': '#0e68ab',
    'Black': '#4b3d44',
    'Red': '#d3202a',
    'Green': '#00733e',
    'Colorless': '#a19891',
    'Multicolor': '#c9a227',
    'Land': '#8b7355',
}

RARITY_ORDER = ['Common', 'Uncommon', 'Rare', 'Mythic']
RARITY_COLORS = {
    'Common': '#1a1a1a',
    'Uncommon': '#707883',
    'Rare': '#b8941c',
    'Mythic': '#d35f10',
}

# Set structure targets from set-guidelines.md
SET_TARGETS = {
    'standard': {
        'Common': 101,
        'Uncommon': 80,
        'Rare': 60,
        'Mythic': 20,
        'per_color_common': 18,
        'per_color_uncommon': 13,
        'per_color_rare': 10,
        'per_color_mythic': 3,
        'signpost_uncommons': 10,
    },
    'small': {
        'Common': 60,
        'Uncommon': 40,
        'Rare': 35,
        'Mythic': 10,
        'per_color_common': 10,
        'per_color_uncommon': 6,
        'per_color_rare': 6,
        'per_color_mythic': 2,
        'signpost_uncommons': 10,
    },
}

# Color pairs for archetypes and signposts
COLOR_PAIRS = [
    ('White', 'Blue', 'Azorius'),
    ('Blue', 'Black', 'Dimir'),
    ('Black', 'Red', 'Rakdos'),
    ('Red', 'Green', 'Gruul'),
    ('Green', 'White', 'Selesnya'),
    ('White', 'Black', 'Orzhov'),
    ('Blue', 'Red', 'Izzet'),
    ('Black', 'Green', 'Golgari'),
    ('Red', 'White', 'Boros'),
    ('Green', 'Blue', 'Simic'),
]

# NWO (New World Order) complexity thresholds
NWO_THRESHOLDS = {
    'Common': {'max_words': 40, 'target_words': 25},
    'Uncommon': {'max_words': 60, 'target_words': 40},
    'Rare': {'max_words': 80, 'target_words': 50},
    'Mythic': {'max_words': 100, 'target_words': 60},
}

# Removal keywords to detect
REMOVAL_PATTERNS = {
    'White': ['exile', 'destroy target', 'pacifism', "can't attack", "can't block", 'tap target'],
    'Blue': ['return.*to.*hand', 'bounce', "doesn't untap", 'tap target', 'counter target'],
    'Black': ['destroy target', '-.*/-.*', 'loses.*life', 'sacrifice', 'kill', 'dies'],
    'Red': ['deals.*damage', 'destroy target artifact', 'destroy target land'],
    'Green': ['fight', 'destroy target artifact', 'destroy target enchantment', 'bite'],
}


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
        self.colors = []  # List of colors for multicolor
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
        self.cmc = fm.get('cmc', 0) or 0
        self.rarity = fm.get('rarity', 'Common')
        self.power = str(fm.get('power', ''))
        self.toughness = str(fm.get('toughness', ''))
        self.set_name = fm.get('set', 'Mirrodin Manifest')

        # Handle color
        color = fm.get('color', '')
        if isinstance(color, list):
            self.colors = color
            self.color = 'Multicolor' if len(color) > 1 else (color[0] if color else 'Colorless')
        elif '/' in str(color):
            self.colors = [c.strip() for c in str(color).split('/')]
            self.color = 'Multicolor'
        else:
            self.color = color if color else 'Colorless'
            self.colors = [color] if color and color != 'Colorless' else []

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
            elif 'design notes' in header:
                self.design_notes = body

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

    def is_creature(self) -> bool:
        """Check if this is a creature card."""
        return 'Creature' in self.card_type or (self.power and self.toughness)

    def is_spell(self) -> bool:
        """Check if this is an instant or sorcery."""
        return self.card_type in ['Instant', 'Sorcery']

    def get_creature_types(self) -> List[str]:
        """Extract creature types from type line."""
        if '—' in self.type_line:
            subtypes = self.type_line.split('—')[1].strip()
            return subtypes.split()
        if self.subtype:
            return str(self.subtype).split()
        return []

    def get_keywords(self) -> List[str]:
        """Extract keywords from rules text."""
        keywords = []
        known_keywords = [
            'Flying', 'First strike', 'Double strike', 'Deathtouch', 'Haste',
            'Hexproof', 'Indestructible', 'Lifelink', 'Menace', 'Reach',
            'Trample', 'Vigilance', 'Flash', 'Defender', 'Ward', 'Crew',
            'Gamble', 'Compound', 'Redistribute', 'Scry', 'Mill'
        ]
        for kw in known_keywords:
            if kw.lower() in self.rules_text.lower():
                keywords.append(kw)
        return keywords

    def word_count(self) -> int:
        """Count words in rules text."""
        return len(self.rules_text.split())


class SetAnalyzer:
    """Analyzes a set of MTG cards."""

    def __init__(self, cards: List[Card]):
        self.cards = cards
        self.stats = {}
        self._analyze()

    def _analyze(self):
        """Run all analysis."""
        # Detect set size based on card count
        total = len(self.cards)
        self.set_size = 'small' if total < 150 else 'standard'
        self.targets = SET_TARGETS[self.set_size]

        # Initialize stats dict - order matters for dependencies
        self.stats = {}

        # Basic stats (no dependencies)
        self.stats['overview'] = self._overview_stats()
        self.stats['color_distribution'] = self._color_distribution()
        self.stats['color_pair_distribution'] = self._color_pair_distribution()
        self.stats['type_distribution'] = self._type_distribution()
        self.stats['rarity_distribution'] = self._rarity_distribution()
        self.stats['mana_curve'] = self._mana_curve()
        self.stats['mana_curve_by_color'] = self._mana_curve_by_color()
        self.stats['creature_stats'] = self._creature_stats()
        self.stats['creature_types'] = self._creature_types()
        self.stats['keywords'] = self._keyword_stats()
        self.stats['complexity'] = self._complexity_stats()
        self.stats['card_list'] = self._card_list()

        # Guidelines-based analysis
        self.stats['set_skeleton'] = self._set_skeleton_analysis()
        self.stats['signpost_analysis'] = self._signpost_analysis()
        self.stats['nwo_compliance'] = self._nwo_compliance()
        self.stats['removal_analysis'] = self._removal_analysis()
        self.stats['archetype_support'] = self._archetype_support()
        self.stats['creature_ratio_analysis'] = self._creature_ratio_analysis()
        self.stats['mana_curve_health'] = self._mana_curve_health()

        # Health metrics depends on the above
        self.stats['health_metrics'] = self._health_metrics()

        # Balance report depends on health_metrics
        self.stats['balance_report'] = self._balance_report()
        self.stats['missing_slots'] = self._missing_slots()

    def _overview_stats(self) -> Dict:
        """General overview statistics."""
        creatures = [c for c in self.cards if c.is_creature()]
        spells = [c for c in self.cards if c.is_spell()]

        return {
            'total_cards': len(self.cards),
            'creatures': len(creatures),
            'noncreatures': len(self.cards) - len(creatures),
            'instants_sorceries': len(spells),
            'avg_cmc': round(sum(c.cmc for c in self.cards) / len(self.cards), 2) if self.cards else 0,
            'avg_creature_cmc': round(sum(c.cmc for c in creatures) / len(creatures), 2) if creatures else 0,
            'set_name': self.cards[0].set_name if self.cards else 'Unknown',
        }

    def _color_distribution(self) -> Dict:
        """Distribution of cards by color."""
        color_counts = Counter()
        for card in self.cards:
            if card.card_type == 'Land':
                color_counts['Land'] += 1
            elif card.color:
                color_counts[card.color] += 1
            else:
                color_counts['Colorless'] += 1

        return dict(color_counts)

    def _color_pair_distribution(self) -> Dict:
        """Distribution of multicolor cards by color pair."""
        pairs = Counter()
        for card in self.cards:
            if len(card.colors) == 2:
                pair = tuple(sorted(card.colors))
                pairs[f"{pair[0]}/{pair[1]}"] += 1
            elif len(card.colors) > 2:
                pairs['3+ colors'] += 1
        return dict(pairs)

    def _type_distribution(self) -> Dict:
        """Distribution of cards by type."""
        types = Counter(c.card_type for c in self.cards)
        return dict(types)

    def _rarity_distribution(self) -> Dict:
        """Distribution of cards by rarity."""
        rarities = Counter(c.rarity for c in self.cards)
        return {r: rarities.get(r, 0) for r in RARITY_ORDER}

    def _mana_curve(self) -> Dict:
        """Overall mana curve."""
        curve = Counter()
        for card in self.cards:
            if card.card_type != 'Land':
                cmc = min(card.cmc, 7)  # Group 7+ together
                curve[cmc] += 1
        return {str(k): curve[k] for k in sorted(curve.keys())}

    def _mana_curve_by_color(self) -> Dict:
        """Mana curve broken down by color."""
        curves = defaultdict(lambda: Counter())
        for card in self.cards:
            if card.card_type != 'Land':
                cmc = min(card.cmc, 7)
                if card.colors:
                    for color in card.colors:
                        curves[color][cmc] += 1
                else:
                    curves['Colorless'][cmc] += 1

        result = {}
        for color in COLORS + ['Colorless']:
            if color in curves:
                result[color] = {str(k): curves[color][k] for k in sorted(curves[color].keys())}
        return result

    def _creature_stats(self) -> Dict:
        """Statistics about creatures."""
        creatures = [c for c in self.cards if c.is_creature()]

        power_dist = Counter()
        toughness_dist = Counter()
        pt_combos = Counter()

        for c in creatures:
            try:
                p = int(c.power) if c.power and c.power != '*' else 0
                t = int(c.toughness) if c.toughness and c.toughness != '*' else 0
                power_dist[p] += 1
                toughness_dist[t] += 1
                pt_combos[f"{c.power}/{c.toughness}"] += 1
            except ValueError:
                pass

        return {
            'total': len(creatures),
            'power_distribution': dict(power_dist),
            'toughness_distribution': dict(toughness_dist),
            'pt_combinations': dict(pt_combos.most_common(15)),
            'avg_power': round(sum(power_dist.keys()) / len(power_dist), 2) if power_dist else 0,
            'avg_toughness': round(sum(toughness_dist.keys()) / len(toughness_dist), 2) if toughness_dist else 0,
        }

    def _creature_types(self) -> Dict:
        """Distribution of creature types."""
        types = Counter()
        for card in self.cards:
            for ct in card.get_creature_types():
                types[ct] += 1
        return dict(types.most_common(20))

    def _keyword_stats(self) -> Dict:
        """Keyword usage statistics."""
        keywords = Counter()
        cards_with_keywords = 0

        for card in self.cards:
            kws = card.get_keywords()
            if kws:
                cards_with_keywords += 1
            for kw in kws:
                keywords[kw] += 1

        return {
            'distribution': dict(keywords.most_common()),
            'cards_with_keywords': cards_with_keywords,
            'keyword_density': round(cards_with_keywords / len(self.cards) * 100, 1) if self.cards else 0,
        }

    def _complexity_stats(self) -> Dict:
        """Text complexity analysis."""
        word_counts = [c.word_count() for c in self.cards]

        by_rarity = defaultdict(list)
        for card in self.cards:
            by_rarity[card.rarity].append(card.word_count())

        rarity_avg = {}
        for rarity, counts in by_rarity.items():
            rarity_avg[rarity] = round(sum(counts) / len(counts), 1) if counts else 0

        # Cards with longest rules text
        sorted_by_length = sorted(self.cards, key=lambda c: c.word_count(), reverse=True)
        longest = [(c.name, c.word_count()) for c in sorted_by_length[:5]]

        return {
            'avg_word_count': round(sum(word_counts) / len(word_counts), 1) if word_counts else 0,
            'max_word_count': max(word_counts) if word_counts else 0,
            'min_word_count': min(word_counts) if word_counts else 0,
            'by_rarity': rarity_avg,
            'longest_cards': longest,
        }

    def _card_list(self) -> List[Dict]:
        """List of all cards with key stats."""
        return [{
            'name': c.name,
            'type': c.card_type,
            'color': c.color,
            'cmc': c.cmc,
            'rarity': c.rarity,
            'power': c.power,
            'toughness': c.toughness,
            'mana_cost': c.mana_cost,
            'rules_text': c.rules_text,
        } for c in sorted(self.cards, key=lambda x: (x.color, x.cmc, x.name))]

    def _set_skeleton_analysis(self) -> Dict:
        """Analyze set structure against targets."""
        targets = self.targets
        analysis = {
            'set_size': self.set_size,
            'rarity_status': {},
            'color_by_rarity': {},
        }

        # Rarity totals vs targets
        for rarity in RARITY_ORDER:
            count = len([c for c in self.cards if c.rarity == rarity])
            target = targets.get(rarity, 0)
            pct = (count / target * 100) if target > 0 else 0
            analysis['rarity_status'][rarity] = {
                'count': count,
                'target': target,
                'percent': round(pct, 1),
                'status': 'good' if 80 <= pct <= 120 else ('warning' if 50 <= pct <= 150 else 'bad'),
            }

        # Color balance per rarity (mono-color only, per guidelines)
        for rarity in RARITY_ORDER:
            rarity_cards = [c for c in self.cards if c.rarity == rarity]
            color_counts = {}
            for color in COLORS:
                # Count only mono-color cards (where this is the only color)
                count = len([c for c in rarity_cards
                           if c.color == color and len(c.colors) <= 1])
                target_key = f'per_color_{rarity.lower()}'
                target = targets.get(target_key, 0)
                pct = (count / target * 100) if target > 0 else 0
                color_counts[color] = {
                    'count': count,
                    'target': target,
                    'percent': round(pct, 1),
                }
            # Also track multicolor and colorless for context
            multicolor_count = len([c for c in rarity_cards if len(c.colors) > 1])
            colorless_count = len([c for c in rarity_cards if c.color == 'Colorless' or not c.colors])
            color_counts['Multicolor'] = {'count': multicolor_count, 'target': 0, 'percent': 0}
            color_counts['Colorless'] = {'count': colorless_count, 'target': 0, 'percent': 0}
            analysis['color_by_rarity'][rarity] = color_counts

        return analysis

    def _signpost_analysis(self) -> Dict:
        """Analyze signpost uncommons for each color pair."""
        signposts = {}
        multicolor_uncommons = [c for c in self.cards if c.rarity == 'Uncommon' and len(c.colors) == 2]

        for color1, color2, guild_name in COLOR_PAIRS:
            matching = [c for c in multicolor_uncommons
                       if set(c.colors) == {color1, color2}]
            signposts[guild_name] = {
                'colors': f'{color1}/{color2}',
                'cards': [c.name for c in matching],
                'count': len(matching),
                'has_signpost': len(matching) >= 1,
            }

        total_with_signpost = sum(1 for s in signposts.values() if s['has_signpost'])

        return {
            'signposts': signposts,
            'total_covered': total_with_signpost,
            'total_needed': 10,
            'percent': round(total_with_signpost / 10 * 100, 1),
        }

    def _nwo_compliance(self) -> Dict:
        """Check New World Order compliance for commons."""
        commons = [c for c in self.cards if c.rarity == 'Common']
        violations = []
        warnings = []

        for card in commons:
            word_count = card.word_count()
            threshold = NWO_THRESHOLDS['Common']

            if word_count > threshold['max_words']:
                violations.append({
                    'name': card.name,
                    'words': word_count,
                    'max': threshold['max_words'],
                    'reason': 'Exceeds maximum word count for common',
                })
            elif word_count > threshold['target_words']:
                warnings.append({
                    'name': card.name,
                    'words': word_count,
                    'target': threshold['target_words'],
                    'reason': 'Above target complexity for common',
                })

        avg_words = sum(c.word_count() for c in commons) / len(commons) if commons else 0
        compliant_count = len(commons) - len(violations)

        return {
            'total_commons': len(commons),
            'compliant': compliant_count,
            'compliance_rate': round(compliant_count / len(commons) * 100, 1) if commons else 0,
            'avg_word_count': round(avg_words, 1),
            'target_avg': NWO_THRESHOLDS['Common']['target_words'],
            'violations': violations,
            'warnings': warnings,
        }

    def _removal_analysis(self) -> Dict:
        """Analyze removal spells by color."""
        removal_by_color = {}

        for color in COLORS:
            color_cards = [c for c in self.cards if c.color == color or color in c.colors]
            removal_cards = []

            for card in color_cards:
                rules = card.rules_text.lower()
                for pattern in REMOVAL_PATTERNS.get(color, []):
                    if re.search(pattern, rules):
                        removal_cards.append({
                            'name': card.name,
                            'rarity': card.rarity,
                            'type': card.card_type,
                        })
                        break

            common_removal = len([r for r in removal_cards if r['rarity'] == 'Common'])
            uncommon_removal = len([r for r in removal_cards if r['rarity'] == 'Uncommon'])

            removal_by_color[color] = {
                'total': len(removal_cards),
                'common': common_removal,
                'uncommon': uncommon_removal,
                'cards': removal_cards,
                'meets_target': common_removal >= 2,  # Target: 2-3 common removal per color
            }

        colors_with_removal = sum(1 for r in removal_by_color.values() if r['meets_target'])

        return {
            'by_color': removal_by_color,
            'colors_meeting_target': colors_with_removal,
            'percent': round(colors_with_removal / 5 * 100, 1),
        }

    def _archetype_support(self) -> Dict:
        """Analyze support for each two-color draft archetype."""
        archetypes = {}

        for color1, color2, guild_name in COLOR_PAIRS:
            # Find cards that support this color pair
            supporting_cards = []
            for card in self.cards:
                # Multicolor cards of this pair
                if set(card.colors) == {color1, color2}:
                    supporting_cards.append({'name': card.name, 'type': 'gold', 'rarity': card.rarity})
                # Monocolor cards (count as half support)
                elif card.color == color1 or card.color == color2:
                    # Only count if it seems to support themes (simplified check)
                    pass

            gold_cards = len([c for c in supporting_cards if c['type'] == 'gold'])
            gold_commons = len([c for c in supporting_cards if c['type'] == 'gold' and c['rarity'] == 'Common'])
            gold_uncommons = len([c for c in supporting_cards if c['type'] == 'gold' and c['rarity'] == 'Uncommon'])

            archetypes[guild_name] = {
                'colors': f'{color1}/{color2}',
                'gold_cards': gold_cards,
                'gold_uncommons': gold_uncommons,
                'cards': supporting_cards,
                'has_signpost': gold_uncommons >= 1,
            }

        supported = sum(1 for a in archetypes.values() if a['has_signpost'])

        return {
            'archetypes': archetypes,
            'supported_count': supported,
            'total': 10,
            'percent': round(supported / 10 * 100, 1),
        }

    def _creature_ratio_analysis(self) -> Dict:
        """Analyze creature ratio at common (target: 60-65%)."""
        commons = [c for c in self.cards if c.rarity == 'Common']
        common_creatures = [c for c in commons if c.is_creature()]

        ratio = len(common_creatures) / len(commons) if commons else 0
        target_min, target_max = 0.60, 0.65

        return {
            'common_creatures': len(common_creatures),
            'common_total': len(commons),
            'ratio': round(ratio * 100, 1),
            'target_min': target_min * 100,
            'target_max': target_max * 100,
            'status': 'good' if target_min <= ratio <= target_max else (
                'warning' if 0.50 <= ratio <= 0.70 else 'bad'
            ),
        }

    def _mana_curve_health(self) -> Dict:
        """Analyze mana curve health (peak should be at 2-3 CMC)."""
        creatures = [c for c in self.cards if c.is_creature() and c.card_type != 'Land']
        curve = Counter(min(c.cmc, 7) for c in creatures)

        # Find the peak
        if curve:
            peak_cmc = max(curve.keys(), key=lambda k: curve[k])
        else:
            peak_cmc = 0

        # Calculate early drops (1-2 CMC)
        early_drops = curve.get(1, 0) + curve.get(2, 0)
        early_ratio = early_drops / len(creatures) if creatures else 0

        # Check for finishers (5+ CMC)
        finishers = sum(curve.get(cmc, 0) for cmc in range(5, 8))
        finisher_ratio = finishers / len(creatures) if creatures else 0

        return {
            'peak_cmc': peak_cmc,
            'peak_is_healthy': peak_cmc in [2, 3, 4],
            'early_drops': early_drops,
            'early_drop_ratio': round(early_ratio * 100, 1),
            'has_enough_early': early_ratio >= 0.20,  # At least 20% at 1-2 CMC
            'finishers': finishers,
            'finisher_ratio': round(finisher_ratio * 100, 1),
            'has_finishers': finisher_ratio >= 0.10,  # At least 10% at 5+ CMC
            'status': 'good' if (peak_cmc in [2, 3, 4] and early_ratio >= 0.20) else 'warning',
        }

    def _health_metrics(self) -> Dict:
        """Calculate overall set health metrics based on guidelines."""
        metrics = []

        # 1. Rarity Distribution
        skeleton = self.stats['set_skeleton']
        rarity_score = sum(
            1 for r in skeleton['rarity_status'].values()
            if r['status'] == 'good'
        ) / 4 * 100
        metrics.append({
            'name': 'Rarity Distribution',
            'score': round(rarity_score),
            'description': f"Tracking against {self.set_size} set targets",
            'status': 'good' if rarity_score >= 75 else ('warning' if rarity_score >= 50 else 'bad'),
        })

        # 2. Color Balance
        # Check how balanced colors are relative to each other (not vs target)
        # A balanced set has similar card counts across colors at each rarity
        balance_scores = []
        imbalanced_rarities = []
        for rarity, colors in skeleton['color_by_rarity'].items():
            counts = [data['count'] for color, data in colors.items() if color in COLORS]
            if counts and max(counts) > 0:
                # Calculate balance as: min/max ratio (1.0 = perfectly balanced)
                balance_ratio = min(counts) / max(counts) if max(counts) > 0 else 1.0
                balance_scores.append(balance_ratio)
                # Also check absolute spread
                spread = max(counts) - min(counts)
                if spread > 5:  # More than 5 card difference is notable
                    imbalanced_rarities.append(f"{rarity} ({min(counts)}-{max(counts)})")

        # Average balance across rarities, convert to 0-100 scale
        avg_balance = sum(balance_scores) / len(balance_scores) if balance_scores else 1.0
        color_score = round(avg_balance * 100)

        # Build description
        if imbalanced_rarities:
            color_desc = f"Spread in: {', '.join(imbalanced_rarities[:2])}"
        else:
            color_desc = "Colors well balanced across rarities"

        metrics.append({
            'name': 'Color Balance',
            'score': color_score,
            'description': color_desc,
            'status': 'good' if color_score >= 75 else ('warning' if color_score >= 50 else 'bad'),
        })

        # 3. Signpost Uncommons
        signpost = self.stats['signpost_analysis']
        metrics.append({
            'name': 'Signpost Uncommons',
            'score': round(signpost['percent']),
            'description': f"{signpost['total_covered']}/10 color pairs have signposts",
            'status': 'good' if signpost['percent'] >= 80 else ('warning' if signpost['percent'] >= 50 else 'bad'),
        })

        # 4. NWO Compliance
        nwo = self.stats['nwo_compliance']
        metrics.append({
            'name': 'NWO Compliance',
            'score': round(nwo['compliance_rate']),
            'description': f"Commons avg {nwo['avg_word_count']} words (target: {nwo['target_avg']})",
            'status': 'good' if nwo['compliance_rate'] >= 90 else ('warning' if nwo['compliance_rate'] >= 70 else 'bad'),
        })

        # 5. Removal Coverage
        removal = self.stats['removal_analysis']
        metrics.append({
            'name': 'Removal Coverage',
            'score': round(removal['percent']),
            'description': f"{removal['colors_meeting_target']}/5 colors have adequate removal",
            'status': 'good' if removal['percent'] >= 80 else ('warning' if removal['percent'] >= 60 else 'bad'),
        })

        # 6. Creature Ratio
        creature = self.stats['creature_ratio_analysis']
        creature_score = 100 if creature['status'] == 'good' else (70 if creature['status'] == 'warning' else 40)
        metrics.append({
            'name': 'Creature Ratio',
            'score': creature_score,
            'description': f"{creature['ratio']}% creatures at common (target: 60-65%)",
            'status': creature['status'],
        })

        # 7. Mana Curve Health
        curve = self.stats['mana_curve_health']
        curve_score = 100 if curve['status'] == 'good' else 60
        metrics.append({
            'name': 'Mana Curve',
            'score': curve_score,
            'description': f"Peak at {curve['peak_cmc']} CMC, {curve['early_drop_ratio']}% early drops",
            'status': curve['status'],
        })

        # Calculate overall health score
        overall_score = sum(m['score'] for m in metrics) / len(metrics)

        return {
            'metrics': metrics,
            'overall_score': round(overall_score),
            'overall_status': 'good' if overall_score >= 75 else ('warning' if overall_score >= 50 else 'bad'),
        }

    def _balance_report(self) -> Dict:
        """Report on set balance issues using guidelines-based analysis."""
        issues = []
        warnings = []
        suggestions = []

        total = len(self.cards)
        targets = self.targets

        # 1. Rarity targets
        for rarity in RARITY_ORDER:
            count = len([c for c in self.cards if c.rarity == rarity])
            target = targets.get(rarity, 0)
            if target > 0:
                pct = count / target
                if pct < 0.5:
                    issues.append(f"{rarity}s severely under target: {count}/{target} ({pct:.0%})")
                elif pct < 0.8:
                    warnings.append(f"{rarity}s below target: {count}/{target} ({pct:.0%})")
                elif pct > 1.2:
                    warnings.append(f"{rarity}s exceed target: {count}/{target} ({pct:.0%})")

        # 2. Color balance at common
        commons = [c for c in self.cards if c.rarity == 'Common']
        if commons:
            common_colors = Counter(c.color for c in commons if c.color in COLORS)
            target_per_color = targets.get('per_color_common', 18)
            for color in COLORS:
                count = common_colors.get(color, 0)
                if count == 0:
                    issues.append(f"No {color} commons")
                elif count < target_per_color * 0.5:
                    warnings.append(f"{color} commons low: {count}/{target_per_color}")

        # 3. Signpost uncommons
        signpost = self.stats.get('signpost_analysis', {})
        missing_signposts = [name for name, data in signpost.get('signposts', {}).items()
                           if not data.get('has_signpost')]
        if len(missing_signposts) > 5:
            issues.append(f"Missing signposts for {len(missing_signposts)} archetypes")
        elif missing_signposts:
            suggestions.append(f"Missing signposts: {', '.join(missing_signposts)}")

        # 4. NWO compliance
        nwo = self.stats.get('nwo_compliance', {})
        if nwo.get('violations'):
            warnings.append(f"{len(nwo['violations'])} commons exceed NWO complexity limits")

        # 5. Removal coverage
        removal = self.stats.get('removal_analysis', {})
        colors_lacking = [color for color, data in removal.get('by_color', {}).items()
                        if not data.get('meets_target')]
        if len(colors_lacking) >= 3:
            issues.append(f"Removal lacking in {len(colors_lacking)} colors: {', '.join(colors_lacking)}")
        elif colors_lacking:
            warnings.append(f"Consider more removal in: {', '.join(colors_lacking)}")

        # 6. Creature ratio at common
        creature = self.stats.get('creature_ratio_analysis', {})
        if creature.get('status') == 'bad':
            issues.append(f"Common creature ratio {creature.get('ratio')}% (target: 60-65%)")
        elif creature.get('status') == 'warning':
            warnings.append(f"Common creature ratio {creature.get('ratio')}% (target: 60-65%)")

        # 7. Mana curve
        curve = self.stats.get('mana_curve_health', {})
        if not curve.get('has_enough_early'):
            warnings.append(f"Low early drops: {curve.get('early_drop_ratio')}% (need 20%+)")
        if not curve.get('has_finishers'):
            suggestions.append("Consider adding more 5+ CMC finishers")

        # 8. Missing card types
        types_present = set(c.card_type for c in self.cards)
        common_types = {'Creature', 'Instant', 'Sorcery', 'Enchantment', 'Artifact'}
        missing = common_types - types_present
        if missing:
            suggestions.append(f"Missing card types: {', '.join(missing)}")

        # Calculate health score from the metrics
        health = self.stats.get('health_metrics', {})
        health_score = health.get('overall_score', 0)

        return {
            'issues': issues,
            'warnings': warnings,
            'suggestions': suggestions,
            'health_score': health_score,
        }

    def _missing_slots(self) -> Dict:
        """Identify missing slots for a balanced set."""
        # For a small set, suggest what's missing
        current = {
            'colors': set(c.color for c in self.cards),
            'types': set(c.card_type for c in self.cards),
            'rarities': set(c.rarity for c in self.cards),
            'cmcs': set(c.cmc for c in self.cards if c.card_type != 'Land'),
        }

        suggestions = []

        # Check each color has cards at different CMCs
        for color in COLORS:
            color_cards = [c for c in self.cards if color in c.colors or c.color == color]
            if color_cards:
                cmcs = set(c.cmc for c in color_cards)
                if 1 not in cmcs and 2 not in cmcs:
                    suggestions.append(f"{color} needs early drops (1-2 CMC)")
                if not any(c >= 5 for c in cmcs):
                    suggestions.append(f"{color} needs finishers (5+ CMC)")

        return {
            'suggestions': suggestions,
        }


def _generate_nwo_violations_html(violations: List[Dict]) -> str:
    """Generate HTML for NWO violations."""
    if not violations:
        return '<div style="padding: 20px; text-align: center; color: var(--success);">No violations!</div>'

    items = []
    for v in violations[:10]:
        items.append(f'''<div class="nwo-violation">
            <strong>{v['name']}</strong>
            <span style="float: right; color: var(--error);">{v['words']} words</span>
            <div style="font-size: 0.85em; color: var(--text-secondary); margin-top: 4px;">{v['reason']}</div>
        </div>''')

    html = '<div style="padding: 10px;">' + ''.join(items)
    if len(violations) > 10:
        html += f'<div style="color: var(--text-secondary); text-align: center;">...and {len(violations) - 10} more</div>'
    html += '</div>'
    return html


def _generate_nwo_warnings_html(warnings: List[Dict]) -> str:
    """Generate HTML for NWO warnings."""
    if not warnings:
        return '<div style="padding: 20px; text-align: center; color: var(--success);">No warnings!</div>'

    items = []
    for w in warnings[:10]:
        items.append(f'''<div class="nwo-warning">
            <strong>{w['name']}</strong>
            <span style="float: right; color: var(--warning);">{w['words']} words</span>
        </div>''')

    html = '<div style="padding: 10px;">' + ''.join(items)
    if len(warnings) > 10:
        html += f'<div style="color: var(--text-secondary); text-align: center;">...and {len(warnings) - 10} more</div>'
    html += '</div>'
    return html


def _generate_card_html(card: Dict) -> str:
    """Generate HTML for a single card in the spoiler grid."""
    import html as html_lib

    name = html_lib.escape(card['name'] or '')
    card_type = html_lib.escape(card['type'] or '')
    color = card['color'] or 'Colorless'
    rarity = card['rarity'] or 'Common'
    cmc = card['cmc'] or 0
    mana_cost = html_lib.escape(card.get('mana_cost') or str(cmc))
    rules_text = html_lib.escape(card.get('rules_text') or '')
    power = card.get('power') or ''
    toughness = card.get('toughness') or ''

    # Determine base type for filtering
    type_lower = card_type.lower()
    if 'creature' in type_lower:
        base_type = 'Creature'
    elif 'instant' in type_lower:
        base_type = 'Instant'
    elif 'sorcery' in type_lower:
        base_type = 'Sorcery'
    elif 'enchantment' in type_lower:
        base_type = 'Enchantment'
    elif 'artifact' in type_lower:
        base_type = 'Artifact'
    elif 'land' in type_lower:
        base_type = 'Land'
    else:
        base_type = 'Other'

    # Header color class
    header_class = color
    if base_type == 'Land' and color == 'Colorless':
        header_class = 'Land'

    # P/T display
    pt_html = ''
    if power and toughness:
        pt_html = f'<span class="card-pt">{power}/{toughness}</span>'

    # Rules text display
    rules_html = rules_text if rules_text else '<em>View card file for rules text</em>'

    return f'''
            <div class="mtg-card"
                 data-name="{name.lower()}"
                 data-color="{color}"
                 data-rarity="{rarity}"
                 data-type="{base_type}">
                <div class="card-header {header_class}">
                    <span class="card-name">{name}</span>
                    <span class="card-mana">{mana_cost}</span>
                </div>
                <div class="card-type-line">{card_type}</div>
                <div class="card-text-box">
                    <div class="rules-text">{rules_html}</div>
                </div>
                <div class="card-footer">
                    <div>
                        <span class="rarity-gem {rarity}"></span>
                        <span class="card-rarity-label">{rarity}</span>
                    </div>
                    {pt_html}
                </div>
            </div>'''


def generate_dashboard_html(analyzer: SetAnalyzer) -> str:
    """Generate the HTML dashboard."""
    stats = analyzer.stats

    # Prepare chart data as JSON
    color_data = json.dumps(stats['color_distribution'])
    type_data = json.dumps(stats['type_distribution'])
    rarity_data = json.dumps(stats['rarity_distribution'])
    curve_data = json.dumps(stats['mana_curve'])
    curve_by_color = json.dumps(stats['mana_curve_by_color'])
    keywords_data = json.dumps(stats['keywords']['distribution'])
    creature_types_data = json.dumps(stats['creature_types'])
    pt_data = json.dumps(stats['creature_stats']['pt_combinations'])

    # New health metrics data
    health_metrics = stats['health_metrics']
    set_skeleton = stats['set_skeleton']
    signpost = stats['signpost_analysis']
    nwo = stats['nwo_compliance']
    removal = stats['removal_analysis']
    archetype = stats['archetype_support']
    creature_ratio = stats['creature_ratio_analysis']
    curve_health = stats['mana_curve_health']

    overview = stats['overview']
    balance = stats['balance_report']
    complexity = stats['complexity']
    creature_stats = stats['creature_stats']

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{overview['set_name']} - Set Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        :root {{
            --bg-primary: #0f0f1a;
            --bg-secondary: #1a1a2e;
            --bg-card: #252540;
            --text-primary: #e8e8e8;
            --text-secondary: #a0a0a0;
            --accent: #c9a227;
            --accent-light: #e5d08f;
            --success: #4caf50;
            --warning: #ff9800;
            --error: #f44336;
            --white: #f8f6d8;
            --blue: #0e68ab;
            --black: #4b3d44;
            --red: #d3202a;
            --green: #00733e;
            --colorless: #a19891;
            --multicolor: #c9a227;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }}

        .header {{
            background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
            padding: 40px 20px;
            text-align: center;
            border-bottom: 2px solid var(--accent);
        }}

        .header h1 {{
            font-family: 'Cinzel', serif;
            font-size: 2.5em;
            color: var(--accent);
            letter-spacing: 3px;
            margin-bottom: 10px;
        }}

        .header .subtitle {{
            color: var(--text-secondary);
            font-size: 1.1em;
        }}

        .dashboard {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 30px;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}

        .stat-card {{
            background: var(--bg-card);
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .stat-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.3);
        }}

        .stat-value {{
            font-size: 2.5em;
            font-weight: 700;
            color: var(--accent);
            line-height: 1;
        }}

        .stat-label {{
            color: var(--text-secondary);
            font-size: 0.9em;
            margin-top: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .section {{
            margin-bottom: 40px;
        }}

        .section-title {{
            font-family: 'Cinzel', serif;
            font-size: 1.5em;
            color: var(--accent);
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}

        .chart-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
        }}

        .chart-card {{
            background: var(--bg-card);
            border-radius: 12px;
            padding: 24px;
            border: 1px solid rgba(255,255,255,0.1);
        }}

        .chart-card h3 {{
            font-size: 1.1em;
            color: var(--text-primary);
            margin-bottom: 20px;
            font-weight: 500;
        }}

        .chart-container {{
            position: relative;
            height: 300px;
        }}

        .balance-report {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}

        .report-section {{
            background: var(--bg-card);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }}

        .report-section h4 {{
            font-size: 1em;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .report-section.issues h4 {{ color: var(--error); }}
        .report-section.warnings h4 {{ color: var(--warning); }}
        .report-section.suggestions h4 {{ color: var(--success); }}

        .report-list {{
            list-style: none;
        }}

        .report-list li {{
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            font-size: 0.9em;
            color: var(--text-secondary);
        }}

        .report-list li:last-child {{
            border-bottom: none;
        }}

        .health-score {{
            text-align: center;
            padding: 30px;
            background: var(--bg-card);
            border-radius: 12px;
            margin-bottom: 20px;
        }}

        .health-value {{
            font-size: 4em;
            font-weight: 700;
        }}

        .health-value.good {{ color: var(--success); }}
        .health-value.warning {{ color: var(--warning); }}
        .health-value.bad {{ color: var(--error); }}

        .health-label {{
            color: var(--text-secondary);
            font-size: 1.1em;
            margin-top: 10px;
        }}

        .card-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
        }}

        .card-table th {{
            text-align: left;
            padding: 12px;
            background: rgba(0,0,0,0.3);
            color: var(--accent);
            font-weight: 500;
            position: sticky;
            top: 0;
        }}

        .card-table td {{
            padding: 10px 12px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}

        .card-table tr:hover td {{
            background: rgba(255,255,255,0.03);
        }}

        .color-dot {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
            vertical-align: middle;
        }}

        .color-dot.White {{ background: var(--white); }}
        .color-dot.Blue {{ background: var(--blue); }}
        .color-dot.Black {{ background: var(--black); }}
        .color-dot.Red {{ background: var(--red); }}
        .color-dot.Green {{ background: var(--green); }}
        .color-dot.Colorless {{ background: var(--colorless); }}
        .color-dot.Multicolor {{ background: var(--multicolor); }}

        .rarity-badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: 500;
        }}

        .rarity-badge.Common {{ background: rgba(26,26,26,0.5); color: #888; }}
        .rarity-badge.Uncommon {{ background: rgba(112,120,131,0.3); color: #a0a8b0; }}
        .rarity-badge.Rare {{ background: rgba(184,148,28,0.3); color: #d4c060; }}
        .rarity-badge.Mythic {{ background: rgba(211,95,16,0.3); color: #e88040; }}

        .table-container {{
            max-height: 500px;
            overflow-y: auto;
            border-radius: 12px;
            background: var(--bg-card);
        }}

        .complexity-bars {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .complexity-bar {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}

        .complexity-label {{
            width: 100px;
            font-size: 0.9em;
            color: var(--text-secondary);
        }}

        .complexity-track {{
            flex: 1;
            height: 24px;
            background: rgba(0,0,0,0.3);
            border-radius: 12px;
            overflow: hidden;
        }}

        .complexity-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--accent) 0%, var(--accent-light) 100%);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 10px;
            font-size: 0.8em;
            font-weight: 500;
            color: var(--bg-primary);
            min-width: 40px;
        }}

        .tabs {{
            display: flex;
            gap: 5px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}

        .tab {{
            padding: 10px 20px;
            background: var(--bg-card);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9em;
            transition: all 0.2s;
        }}

        .tab:hover {{
            background: rgba(255,255,255,0.1);
        }}

        .tab.active {{
            background: var(--accent);
            color: var(--bg-primary);
            border-color: var(--accent);
        }}

        .tab-content {{
            display: none;
        }}

        .tab-content.active {{
            display: block;
        }}

        /* Health Metrics Styles */
        .health-metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 16px;
            margin-bottom: 30px;
        }}

        .metric-card {{
            background: var(--bg-card);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }}

        .metric-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }}

        .metric-name {{
            font-weight: 500;
            color: var(--text-primary);
        }}

        .metric-score {{
            font-size: 1.5em;
            font-weight: 700;
        }}

        .metric-score.good {{ color: var(--success); }}
        .metric-score.warning {{ color: var(--warning); }}
        .metric-score.bad {{ color: var(--error); }}

        .metric-bar {{
            height: 8px;
            background: rgba(0,0,0,0.3);
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 8px;
        }}

        .metric-fill {{
            height: 100%;
            border-radius: 4px;
            transition: width 0.5s ease;
        }}

        .metric-fill.good {{ background: var(--success); }}
        .metric-fill.warning {{ background: var(--warning); }}
        .metric-fill.bad {{ background: var(--error); }}

        .metric-description {{
            font-size: 0.85em;
            color: var(--text-secondary);
        }}

        .skeleton-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 12px;
        }}

        .skeleton-card {{
            background: rgba(0,0,0,0.2);
            border-radius: 8px;
            padding: 16px;
            text-align: center;
        }}

        .skeleton-card.good {{ border-left: 3px solid var(--success); }}
        .skeleton-card.warning {{ border-left: 3px solid var(--warning); }}
        .skeleton-card.bad {{ border-left: 3px solid var(--error); }}

        .skeleton-count {{
            font-size: 1.8em;
            font-weight: 700;
            color: var(--accent);
        }}

        .skeleton-target {{
            font-size: 0.9em;
            color: var(--text-secondary);
        }}

        .skeleton-label {{
            font-size: 0.85em;
            color: var(--text-secondary);
            margin-top: 4px;
        }}

        .signpost-grid {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 10px;
        }}

        .signpost-card {{
            background: rgba(0,0,0,0.2);
            border-radius: 8px;
            padding: 12px;
            text-align: center;
            transition: transform 0.2s;
        }}

        .signpost-card:hover {{
            transform: scale(1.02);
        }}

        .signpost-card.has-signpost {{
            border: 2px solid var(--success);
        }}

        .signpost-card.missing {{
            border: 2px solid var(--error);
            opacity: 0.7;
        }}

        .signpost-name {{
            font-weight: 600;
            font-size: 0.9em;
            margin-bottom: 4px;
        }}

        .signpost-colors {{
            font-size: 0.75em;
            color: var(--text-secondary);
        }}

        .signpost-status {{
            margin-top: 6px;
            font-size: 0.75em;
        }}

        .removal-grid {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 12px;
        }}

        .removal-card {{
            background: rgba(0,0,0,0.2);
            border-radius: 8px;
            padding: 16px;
            text-align: center;
        }}

        .removal-card.meets-target {{
            border-bottom: 3px solid var(--success);
        }}

        .removal-card.below-target {{
            border-bottom: 3px solid var(--warning);
        }}

        .removal-count {{
            font-size: 1.5em;
            font-weight: 700;
        }}

        .nwo-violation {{
            background: rgba(244, 67, 54, 0.1);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 8px;
            border-left: 3px solid var(--error);
        }}

        .nwo-warning {{
            background: rgba(255, 152, 0, 0.1);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 8px;
            border-left: 3px solid var(--warning);
        }}

        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8em;
            }}

            .chart-grid {{
                grid-template-columns: 1fr;
            }}

            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}

            .signpost-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}

            .removal-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}

            .spoiler-grid {{
                grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
            }}
        }}

        /* Card Spoiler View Styles */
        .filter-bar {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-bottom: 20px;
            padding: 16px;
            background: var(--bg-card);
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.1);
            align-items: center;
        }}

        .filter-group {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}

        .filter-group label {{
            font-size: 0.75em;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .filter-group select,
        .filter-group input {{
            padding: 8px 12px;
            background: rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 6px;
            color: var(--text-primary);
            font-size: 0.9em;
            min-width: 140px;
        }}

        .filter-group select:focus,
        .filter-group input:focus {{
            outline: none;
            border-color: var(--accent);
        }}

        .filter-group input::placeholder {{
            color: var(--text-secondary);
        }}

        .filter-count {{
            margin-left: auto;
            font-size: 0.9em;
            color: var(--text-secondary);
        }}

        .filter-count span {{
            color: var(--accent);
            font-weight: 600;
        }}

        .clear-filters {{
            padding: 8px 16px;
            background: transparent;
            border: 1px solid var(--accent);
            border-radius: 6px;
            color: var(--accent);
            cursor: pointer;
            font-size: 0.85em;
            transition: all 0.2s;
        }}

        .clear-filters:hover {{
            background: var(--accent);
            color: var(--bg-primary);
        }}

        .spoiler-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
            padding: 10px 0;
        }}

        .mtg-card {{
            width: 100%;
            height: 400px;
            background: #1a1a1a;
            border-radius: 12px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            border: 3px solid #333;
            box-shadow: 0 4px 15px rgba(0,0,0,0.4);
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .mtg-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.5);
        }}

        .mtg-card.hidden {{
            display: none;
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 14px;
            min-height: 48px;
        }}

        .card-header.White {{ background: linear-gradient(135deg, #f8f6d8 0%, #e8e6c8 100%); color: #333; }}
        .card-header.Blue {{ background: linear-gradient(135deg, #1a7dc4 0%, #0e68ab 100%); color: #fff; }}
        .card-header.Black {{ background: linear-gradient(135deg, #5b4d54 0%, #3b2d34 100%); color: #ddd; }}
        .card-header.Red {{ background: linear-gradient(135deg, #e33030 0%, #c31a1a 100%); color: #fff; }}
        .card-header.Green {{ background: linear-gradient(135deg, #1a8a4e 0%, #00633e 100%); color: #fff; }}
        .card-header.Colorless {{ background: linear-gradient(135deg, #b1a8a1 0%, #918881 100%); color: #333; }}
        .card-header.Multicolor {{ background: linear-gradient(135deg, #d9b237 0%, #b99217 100%); color: #333; }}
        .card-header.Land {{ background: linear-gradient(135deg, #9b8365 0%, #7b6345 100%); color: #fff; }}

        .card-name {{
            font-family: 'Cinzel', serif;
            font-size: 0.95em;
            font-weight: 600;
            line-height: 1.2;
            flex: 1;
            margin-right: 8px;
        }}

        .card-mana {{
            font-size: 0.85em;
            font-weight: 600;
            white-space: nowrap;
            background: rgba(0,0,0,0.2);
            padding: 2px 6px;
            border-radius: 4px;
        }}

        .card-type-line {{
            padding: 8px 14px;
            background: rgba(255,255,255,0.05);
            font-size: 0.85em;
            color: var(--text-secondary);
            border-top: 1px solid rgba(255,255,255,0.1);
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}

        .card-text-box {{
            flex: 1;
            padding: 14px;
            overflow-y: auto;
            font-size: 0.85em;
            line-height: 1.5;
            color: var(--text-primary);
            background: rgba(0,0,0,0.2);
        }}

        .card-text-box::-webkit-scrollbar {{
            width: 6px;
        }}

        .card-text-box::-webkit-scrollbar-track {{
            background: rgba(0,0,0,0.2);
        }}

        .card-text-box::-webkit-scrollbar-thumb {{
            background: rgba(255,255,255,0.2);
            border-radius: 3px;
        }}

        .rules-text {{
            color: var(--text-primary);
        }}

        .rules-text em {{
            color: var(--text-secondary);
            font-style: italic;
        }}

        .card-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 14px;
            background: rgba(0,0,0,0.3);
            border-top: 1px solid rgba(255,255,255,0.1);
        }}

        .rarity-gem {{
            width: 14px;
            height: 14px;
            border-radius: 50%;
            display: inline-block;
        }}

        .rarity-gem.Common {{ background: radial-gradient(circle at 30% 30%, #888 0%, #444 100%); }}
        .rarity-gem.Uncommon {{ background: radial-gradient(circle at 30% 30%, #c0c8d0 0%, #606870 100%); }}
        .rarity-gem.Rare {{ background: radial-gradient(circle at 30% 30%, #ffd700 0%, #b8941c 100%); }}
        .rarity-gem.Mythic {{ background: radial-gradient(circle at 30% 30%, #ff6b35 0%, #d35f10 100%); }}

        .card-pt {{
            font-size: 1.1em;
            font-weight: 700;
            color: var(--text-primary);
            background: rgba(255,255,255,0.1);
            padding: 4px 10px;
            border-radius: 4px;
        }}

        .card-rarity-label {{
            font-size: 0.75em;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .no-results {{
            grid-column: 1 / -1;
            text-align: center;
            padding: 60px 20px;
            color: var(--text-secondary);
        }}

        .no-results h3 {{
            color: var(--accent);
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <header class="header">
        <h1>{overview['set_name'].upper()}</h1>
        <p class="subtitle">Set Design Dashboard</p>
    </header>

    <div class="dashboard">
        <!-- Overview Stats -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{overview['total_cards']}</div>
                <div class="stat-label">Total Cards</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{overview['creatures']}</div>
                <div class="stat-label">Creatures</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{overview['noncreatures']}</div>
                <div class="stat-label">Non-Creatures</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{overview['avg_cmc']}</div>
                <div class="stat-label">Avg CMC</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{complexity['avg_word_count']}</div>
                <div class="stat-label">Avg Words/Card</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['keywords']['keyword_density']}%</div>
                <div class="stat-label">Keyword Density</div>
            </div>
        </div>

        <!-- Health Score -->
        <div class="section">
            <h2 class="section-title">Set Health (Based on Guidelines)</h2>
            <div class="health-score">
                <div class="health-value {health_metrics['overall_status']}">{health_metrics['overall_score']}</div>
                <div class="health-label">Overall Health Score ({set_skeleton['set_size'].title()} Set)</div>
            </div>

            <!-- Health Metrics Grid -->
            <div class="health-metrics-grid">
                {''.join(f"""
                <div class="metric-card">
                    <div class="metric-header">
                        <span class="metric-name">{m['name']}</span>
                        <span class="metric-score {m['status']}">{m['score']}%</span>
                    </div>
                    <div class="metric-bar">
                        <div class="metric-fill {m['status']}" style="width: {m['score']}%"></div>
                    </div>
                    <div class="metric-description">{m['description']}</div>
                </div>
                """ for m in health_metrics['metrics'])}
            </div>

            <!-- Issues/Warnings/Suggestions -->
            <div class="balance-report">
                <div class="report-section issues">
                    <h4>Issues ({len(balance['issues'])})</h4>
                    <ul class="report-list">
                        {''.join(f'<li>{issue}</li>' for issue in balance['issues']) or '<li>No critical issues</li>'}
                    </ul>
                </div>
                <div class="report-section warnings">
                    <h4>Warnings ({len(balance['warnings'])})</h4>
                    <ul class="report-list">
                        {''.join(f'<li>{w}</li>' for w in balance['warnings']) or '<li>No warnings</li>'}
                    </ul>
                </div>
                <div class="report-section suggestions">
                    <h4>Suggestions ({len(balance['suggestions'])})</h4>
                    <ul class="report-list">
                        {''.join(f'<li>{s}</li>' for s in balance['suggestions']) or '<li>No suggestions</li>'}
                    </ul>
                </div>
            </div>
        </div>

        <!-- Tabs for different views -->
        <div class="tabs">
            <button class="tab active" data-tab="skeleton">Set Skeleton</button>
            <button class="tab" data-tab="distribution">Distribution</button>
            <button class="tab" data-tab="curve">Mana Curve</button>
            <button class="tab" data-tab="creatures">Creatures</button>
            <button class="tab" data-tab="mechanics">Mechanics</button>
            <button class="tab" data-tab="complexity">NWO Compliance</button>
            <button class="tab" data-tab="cardlist">Card List</button>
        </div>

        <!-- Set Skeleton Tab -->
        <div class="tab-content active" id="skeleton">
            <!-- Rarity Targets -->
            <div class="chart-card" style="margin-bottom: 20px;">
                <h3>Rarity Distribution vs {set_skeleton['set_size'].title()} Set Targets</h3>
                <div class="skeleton-grid">
                    {''.join(f"""
                    <div class="skeleton-card {set_skeleton['rarity_status'][r]['status']}">
                        <div class="skeleton-count">{set_skeleton['rarity_status'][r]['count']}</div>
                        <div class="skeleton-target">/ {set_skeleton['rarity_status'][r]['target']} target</div>
                        <div class="skeleton-label">{r}s ({set_skeleton['rarity_status'][r]['percent']}%)</div>
                    </div>
                    """ for r in RARITY_ORDER)}
                </div>
            </div>

            <!-- Color Balance by Rarity -->
            <div class="chart-card" style="margin-bottom: 20px;">
                <h3>Color Balance by Rarity</h3>
                <table class="card-table">
                    <thead>
                        <tr>
                            <th>Rarity</th>
                            {''.join(f'<th style="text-align:center;"><span class="color-dot {c}"></span>{c}</th>' for c in COLORS)}
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(f"""
                        <tr>
                            <td><span class="rarity-badge {r}">{r}</span></td>
                            {''.join(f'<td style="text-align:center;">{set_skeleton["color_by_rarity"][r][c]["count"]}/{set_skeleton["color_by_rarity"][r][c]["target"]}</td>' for c in COLORS)}
                        </tr>
                        """ for r in RARITY_ORDER)}
                    </tbody>
                </table>
            </div>

            <!-- Signpost Uncommons -->
            <div class="chart-card" style="margin-bottom: 20px;">
                <h3>Signpost Uncommons ({signpost['total_covered']}/10 Archetypes)</h3>
                <div class="signpost-grid">
                    {''.join(f"""
                    <div class="signpost-card {'has-signpost' if data['has_signpost'] else 'missing'}">
                        <div class="signpost-name">{guild}</div>
                        <div class="signpost-colors">{data['colors']}</div>
                        <div class="signpost-status">
                            {'<span style="color: var(--success);">' + str(data['count']) + ' card(s)</span>' if data['has_signpost'] else '<span style="color: var(--error);">Missing</span>'}
                        </div>
                    </div>
                    """ for guild, data in signpost['signposts'].items())}
                </div>
            </div>

            <!-- Removal Coverage -->
            <div class="chart-card" style="margin-bottom: 20px;">
                <h3>Removal Coverage by Color (Target: 2+ at Common)</h3>
                <div class="removal-grid">
                    {''.join(f"""
                    <div class="removal-card {'meets-target' if removal['by_color'][c]['meets_target'] else 'below-target'}">
                        <span class="color-dot {c}" style="display:block; width:20px; height:20px; margin: 0 auto 8px;"></span>
                        <div class="removal-count">{removal['by_color'][c]['total']}</div>
                        <div style="font-size: 0.85em; color: var(--text-secondary);">
                            {removal['by_color'][c]['common']}C / {removal['by_color'][c]['uncommon']}U
                        </div>
                        <div style="font-size: 0.75em; margin-top: 4px;">
                            {'Target Met' if removal['by_color'][c]['meets_target'] else 'Needs More'}
                        </div>
                    </div>
                    """ for c in COLORS)}
                </div>
            </div>

            <!-- Creature Ratio & Curve Health -->
            <div class="chart-grid">
                <div class="chart-card">
                    <h3>Creature Ratio at Common</h3>
                    <div style="text-align: center; padding: 20px;">
                        <div class="stat-value" style="font-size: 3em;">{creature_ratio['ratio']}%</div>
                        <div style="color: var(--text-secondary); margin-top: 10px;">
                            {creature_ratio['common_creatures']} creatures / {creature_ratio['common_total']} commons
                        </div>
                        <div style="margin-top: 15px;">
                            <span style="color: {'var(--success)' if creature_ratio['status'] == 'good' else 'var(--warning)' if creature_ratio['status'] == 'warning' else 'var(--error)'};">
                                Target: 60-65% | Status: {creature_ratio['status'].upper()}
                            </span>
                        </div>
                    </div>
                </div>
                <div class="chart-card">
                    <h3>Mana Curve Health</h3>
                    <div style="padding: 20px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                            <div style="text-align: center;">
                                <div style="font-size: 2em; font-weight: 700; color: var(--accent);">{curve_health['peak_cmc']}</div>
                                <div style="font-size: 0.85em; color: var(--text-secondary);">Peak CMC</div>
                            </div>
                            <div style="text-align: center;">
                                <div style="font-size: 2em; font-weight: 700; color: {'var(--success)' if curve_health['has_enough_early'] else 'var(--warning)'};">{curve_health['early_drop_ratio']}%</div>
                                <div style="font-size: 0.85em; color: var(--text-secondary);">Early Drops (1-2)</div>
                            </div>
                            <div style="text-align: center;">
                                <div style="font-size: 2em; font-weight: 700; color: {'var(--success)' if curve_health['has_finishers'] else 'var(--warning)'};">{curve_health['finisher_ratio']}%</div>
                                <div style="font-size: 0.85em; color: var(--text-secondary);">Finishers (5+)</div>
                            </div>
                        </div>
                        <div style="text-align: center; color: {'var(--success)' if curve_health['status'] == 'good' else 'var(--warning)'};">
                            Curve Status: {curve_health['status'].upper()}
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Distribution Tab -->
        <div class="tab-content" id="distribution">
            <div class="chart-grid">
                <div class="chart-card">
                    <h3>Color Distribution</h3>
                    <div class="chart-container">
                        <canvas id="colorChart"></canvas>
                    </div>
                </div>
                <div class="chart-card">
                    <h3>Card Type Distribution</h3>
                    <div class="chart-container">
                        <canvas id="typeChart"></canvas>
                    </div>
                </div>
                <div class="chart-card">
                    <h3>Rarity Distribution</h3>
                    <div class="chart-container">
                        <canvas id="rarityChart"></canvas>
                    </div>
                </div>
                <div class="chart-card">
                    <h3>Color Identity Breakdown</h3>
                    <div class="chart-container">
                        <canvas id="colorPieChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- Mana Curve Tab -->
        <div class="tab-content" id="curve">
            <div class="chart-grid">
                <div class="chart-card" style="grid-column: span 2;">
                    <h3>Overall Mana Curve</h3>
                    <div class="chart-container">
                        <canvas id="curveChart"></canvas>
                    </div>
                </div>
                <div class="chart-card" style="grid-column: span 2;">
                    <h3>Mana Curve by Color</h3>
                    <div class="chart-container">
                        <canvas id="curveByColorChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- Creatures Tab -->
        <div class="tab-content" id="creatures">
            <div class="chart-grid">
                <div class="chart-card">
                    <h3>Power/Toughness Combinations</h3>
                    <div class="chart-container">
                        <canvas id="ptChart"></canvas>
                    </div>
                </div>
                <div class="chart-card">
                    <h3>Creature Types</h3>
                    <div class="chart-container">
                        <canvas id="creatureTypeChart"></canvas>
                    </div>
                </div>
            </div>
            <div class="chart-card" style="margin-top: 20px;">
                <h3>Creature Statistics</h3>
                <div class="stats-grid" style="margin-bottom: 0;">
                    <div class="stat-card">
                        <div class="stat-value">{creature_stats['total']}</div>
                        <div class="stat-label">Total Creatures</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{creature_stats['avg_power']}</div>
                        <div class="stat-label">Avg Power</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{creature_stats['avg_toughness']}</div>
                        <div class="stat-label">Avg Toughness</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{overview['avg_creature_cmc']}</div>
                        <div class="stat-label">Avg Creature CMC</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Mechanics Tab -->
        <div class="tab-content" id="mechanics">
            <div class="chart-grid">
                <div class="chart-card" style="grid-column: span 2;">
                    <h3>Keyword Distribution</h3>
                    <div class="chart-container">
                        <canvas id="keywordsChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- NWO Compliance Tab -->
        <div class="tab-content" id="complexity">
            <!-- NWO Summary -->
            <div class="chart-card" style="margin-bottom: 20px;">
                <h3>New World Order (NWO) Compliance</h3>
                <div class="stats-grid" style="margin-bottom: 20px;">
                    <div class="stat-card">
                        <div class="stat-value" style="color: {'var(--success)' if nwo['compliance_rate'] >= 90 else 'var(--warning)' if nwo['compliance_rate'] >= 70 else 'var(--error)'};">{nwo['compliance_rate']}%</div>
                        <div class="stat-label">Compliance Rate</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{nwo['avg_word_count']}</div>
                        <div class="stat-label">Avg Words (Commons)</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{nwo['target_avg']}</div>
                        <div class="stat-label">Target Max</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" style="color: {'var(--success)' if len(nwo['violations']) == 0 else 'var(--error)'};">{len(nwo['violations'])}</div>
                        <div class="stat-label">Violations</div>
                    </div>
                </div>
                <p style="color: var(--text-secondary); font-size: 0.9em; margin-bottom: 15px;">
                    NWO states that commons should be simple. Target word count for commons: {NWO_THRESHOLDS['Common']['target_words']} words. Max allowed: {NWO_THRESHOLDS['Common']['max_words']} words.
                </p>
            </div>

            <div class="chart-grid">
                <!-- Violations -->
                <div class="chart-card">
                    <h3>NWO Violations (Commons exceeding {NWO_THRESHOLDS['Common']['max_words']} words)</h3>
                    {_generate_nwo_violations_html(nwo['violations'])}
                </div>

                <!-- Warnings -->
                <div class="chart-card">
                    <h3>Complexity Warnings (Commons above {NWO_THRESHOLDS['Common']['target_words']} words)</h3>
                    {_generate_nwo_warnings_html(nwo['warnings'])}
                </div>
            </div>

            <!-- Text Complexity by Rarity -->
            <div class="chart-grid" style="margin-top: 20px;">
                <div class="chart-card">
                    <h3>Text Complexity by Rarity</h3>
                    <div class="complexity-bars">
                        {''.join(f"""
                        <div class="complexity-bar">
                            <span class="complexity-label">{rarity}</span>
                            <div class="complexity-track">
                                <div class="complexity-fill" style="width: {min(100, complexity['by_rarity'].get(rarity, 0) * 2)}%">{complexity['by_rarity'].get(rarity, 0)}</div>
                            </div>
                        </div>
                        """ for rarity in RARITY_ORDER)}
                    </div>
                </div>
                <div class="chart-card">
                    <h3>Longest Cards (by word count)</h3>
                    <div class="complexity-bars">
                        {''.join(f"""
                        <div class="complexity-bar">
                            <span class="complexity-label" style="width: 150px;">{name[:20]}{'...' if len(name) > 20 else ''}</span>
                            <div class="complexity-track">
                                <div class="complexity-fill" style="width: {min(100, count * 1.5)}%">{count}</div>
                            </div>
                        </div>
                        """ for name, count in complexity['longest_cards'])}
                    </div>
                </div>
            </div>
        </div>

        <!-- Card List Tab -->
        <div class="tab-content" id="cardlist">
            <!-- Filter Controls -->
            <div class="filter-bar">
                <div class="filter-group">
                    <label>Search</label>
                    <input type="text" id="searchFilter" placeholder="Card name...">
                </div>
                <div class="filter-group">
                    <label>Color</label>
                    <select id="colorFilter">
                        <option value="">All Colors</option>
                        <option value="White">White</option>
                        <option value="Blue">Blue</option>
                        <option value="Black">Black</option>
                        <option value="Red">Red</option>
                        <option value="Green">Green</option>
                        <option value="Colorless">Colorless</option>
                        <option value="Multicolor">Multicolor</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Rarity</label>
                    <select id="rarityFilter">
                        <option value="">All Rarities</option>
                        <option value="Common">Common</option>
                        <option value="Uncommon">Uncommon</option>
                        <option value="Rare">Rare</option>
                        <option value="Mythic">Mythic</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Type</label>
                    <select id="typeFilter">
                        <option value="">All Types</option>
                        <option value="Creature">Creature</option>
                        <option value="Instant">Instant</option>
                        <option value="Sorcery">Sorcery</option>
                        <option value="Enchantment">Enchantment</option>
                        <option value="Artifact">Artifact</option>
                        <option value="Land">Land</option>
                    </select>
                </div>
                <button class="clear-filters" onclick="clearFilters()">Clear Filters</button>
                <div class="filter-count">Showing <span id="visibleCount">0</span> of <span id="totalCount">0</span> cards</div>
            </div>

            <!-- Spoiler Grid -->
            <div class="spoiler-grid" id="spoilerGrid">
                {''.join(_generate_card_html(card) for card in stats['card_list'])}
            </div>
        </div>
    </div>

    <script>
        // Chart.js configuration
        Chart.defaults.color = '#a0a0a0';
        Chart.defaults.borderColor = 'rgba(255,255,255,0.1)';

        const colorPalette = {{
            'White': '#f8f6d8',
            'Blue': '#0e68ab',
            'Black': '#4b3d44',
            'Red': '#d3202a',
            'Green': '#00733e',
            'Colorless': '#a19891',
            'Multicolor': '#c9a227',
            'Land': '#8b7355',
        }};

        const rarityColors = {{
            'Common': '#666666',
            'Uncommon': '#707883',
            'Rare': '#b8941c',
            'Mythic': '#d35f10',
        }};

        // Color Distribution Chart
        const colorData = {color_data};
        new Chart(document.getElementById('colorChart'), {{
            type: 'bar',
            data: {{
                labels: Object.keys(colorData),
                datasets: [{{
                    data: Object.values(colorData),
                    backgroundColor: Object.keys(colorData).map(c => colorPalette[c] || '#888'),
                    borderRadius: 6,
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }}
                }}
            }}
        }});

        // Type Distribution Chart
        const typeData = {type_data};
        new Chart(document.getElementById('typeChart'), {{
            type: 'bar',
            data: {{
                labels: Object.keys(typeData),
                datasets: [{{
                    data: Object.values(typeData),
                    backgroundColor: '#c9a227',
                    borderRadius: 6,
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }}
                }}
            }}
        }});

        // Rarity Distribution Chart
        const rarityData = {rarity_data};
        new Chart(document.getElementById('rarityChart'), {{
            type: 'doughnut',
            data: {{
                labels: Object.keys(rarityData),
                datasets: [{{
                    data: Object.values(rarityData),
                    backgroundColor: Object.keys(rarityData).map(r => rarityColors[r]),
                    borderWidth: 0,
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'right' }}
                }}
            }}
        }});

        // Color Pie Chart
        new Chart(document.getElementById('colorPieChart'), {{
            type: 'pie',
            data: {{
                labels: Object.keys(colorData),
                datasets: [{{
                    data: Object.values(colorData),
                    backgroundColor: Object.keys(colorData).map(c => colorPalette[c] || '#888'),
                    borderWidth: 2,
                    borderColor: '#1a1a2e',
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'right' }}
                }}
            }}
        }});

        // Mana Curve Chart
        const curveData = {curve_data};
        new Chart(document.getElementById('curveChart'), {{
            type: 'bar',
            data: {{
                labels: Object.keys(curveData).map(k => k === '7' ? '7+' : k),
                datasets: [{{
                    label: 'Cards',
                    data: Object.values(curveData),
                    backgroundColor: '#c9a227',
                    borderRadius: 6,
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ title: {{ display: true, text: 'Mana Value' }} }},
                    y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }}, title: {{ display: true, text: 'Count' }} }}
                }}
            }}
        }});

        // Mana Curve by Color
        const curveByColor = {curve_by_color};
        const allCmcs = ['0', '1', '2', '3', '4', '5', '6', '7'];
        const colorDatasets = Object.entries(curveByColor).map(([color, data]) => ({{
            label: color,
            data: allCmcs.map(cmc => data[cmc] || 0),
            backgroundColor: colorPalette[color] || '#888',
            borderRadius: 4,
        }}));

        new Chart(document.getElementById('curveByColorChart'), {{
            type: 'bar',
            data: {{
                labels: allCmcs.map(k => k === '7' ? '7+' : k),
                datasets: colorDatasets
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ position: 'top' }} }},
                scales: {{
                    x: {{ stacked: true, title: {{ display: true, text: 'Mana Value' }} }},
                    y: {{ stacked: true, beginAtZero: true, title: {{ display: true, text: 'Count' }} }}
                }}
            }}
        }});

        // Keywords Chart
        const keywordsData = {keywords_data};
        new Chart(document.getElementById('keywordsChart'), {{
            type: 'bar',
            data: {{
                labels: Object.keys(keywordsData),
                datasets: [{{
                    data: Object.values(keywordsData),
                    backgroundColor: '#c9a227',
                    borderRadius: 6,
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }}
                }}
            }}
        }});

        // Creature Types Chart
        const creatureTypesData = {creature_types_data};
        new Chart(document.getElementById('creatureTypeChart'), {{
            type: 'bar',
            data: {{
                labels: Object.keys(creatureTypesData),
                datasets: [{{
                    data: Object.values(creatureTypesData),
                    backgroundColor: '#00733e',
                    borderRadius: 6,
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }}
                }}
            }}
        }});

        // P/T Chart
        const ptData = {pt_data};
        new Chart(document.getElementById('ptChart'), {{
            type: 'bar',
            data: {{
                labels: Object.keys(ptData),
                datasets: [{{
                    data: Object.values(ptData),
                    backgroundColor: '#d3202a',
                    borderRadius: 6,
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }}
                }}
            }}
        }});

        // Tab functionality
        document.querySelectorAll('.tab').forEach(tab => {{
            tab.addEventListener('click', () => {{
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

                tab.classList.add('active');
                document.getElementById(tab.dataset.tab).classList.add('active');
            }});
        }});

        // ========================================
        // Card Spoiler Grid Filtering
        // ========================================

        // Filter cards based on current filter values
        function filterCards() {{
            const searchValue = document.getElementById('searchFilter').value.toLowerCase();
            const colorValue = document.getElementById('colorFilter').value;
            const rarityValue = document.getElementById('rarityFilter').value;
            const typeValue = document.getElementById('typeFilter').value;

            const cards = document.querySelectorAll('.mtg-card');

            cards.forEach(card => {{
                const name = card.dataset.name;
                const color = card.dataset.color;
                const rarity = card.dataset.rarity;
                const type = card.dataset.type;

                let show = true;

                // Search filter
                if (searchValue && !name.includes(searchValue)) {{
                    show = false;
                }}

                // Color filter
                if (colorValue && color !== colorValue) {{
                    show = false;
                }}

                // Rarity filter
                if (rarityValue && rarity !== rarityValue) {{
                    show = false;
                }}

                // Type filter
                if (typeValue && type !== typeValue) {{
                    show = false;
                }}

                card.classList.toggle('hidden', !show);
            }});

            updateVisibleCount();
        }}

        // Update visible card count
        function updateVisibleCount() {{
            const allCards = document.querySelectorAll('.mtg-card');
            const visibleCards = document.querySelectorAll('.mtg-card:not(.hidden)');
            document.getElementById('visibleCount').textContent = visibleCards.length;
            document.getElementById('totalCount').textContent = allCards.length;
        }}

        // Clear all filters
        function clearFilters() {{
            document.getElementById('searchFilter').value = '';
            document.getElementById('colorFilter').value = '';
            document.getElementById('rarityFilter').value = '';
            document.getElementById('typeFilter').value = '';
            filterCards();
        }}

        // Add event listeners for filters
        document.getElementById('searchFilter').addEventListener('input', filterCards);
        document.getElementById('colorFilter').addEventListener('change', filterCards);
        document.getElementById('rarityFilter').addEventListener('change', filterCards);
        document.getElementById('typeFilter').addEventListener('change', filterCards);

        // Initialize counts on page load
        updateVisibleCount();
    </script>
</body>
</html>
'''
    return html


def main():
    """Main function to generate the dashboard."""
    script_dir = Path(__file__).parent

    # Find all markdown files (in root and cards/ folder)
    md_files = list(script_dir.glob('*.md')) + list(script_dir.glob('cards/*.md'))

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

    print(f"\nAnalyzing {len(cards)} cards...")

    # Analyze
    analyzer = SetAnalyzer(cards)

    # Generate HTML
    html = generate_dashboard_html(analyzer)

    # Write output
    output_path = script_dir / 'dashboard.html'
    output_path.write_text(html, encoding='utf-8')

    print(f"\n✓ Generated: {output_path}")
    print(f"  Open in browser: file://{output_path.absolute()}")

    # Print summary
    print(f"\n{'='*60}")
    print("SET SUMMARY")
    print(f"{'='*60}")
    stats = analyzer.stats
    print(f"Set Type: {stats['set_skeleton']['set_size'].title()} Set")
    print(f"Total Cards: {stats['overview']['total_cards']}")
    print(f"Creatures: {stats['overview']['creatures']}")
    print(f"Average CMC: {stats['overview']['avg_cmc']}")

    # Health Metrics
    print(f"\n{'='*60}")
    print("HEALTH METRICS (from set-guidelines.md)")
    print(f"{'='*60}")
    print(f"Overall Health Score: {stats['health_metrics']['overall_score']}/100")
    print()
    for metric in stats['health_metrics']['metrics']:
        status_icon = '✓' if metric['status'] == 'good' else ('!' if metric['status'] == 'warning' else '✗')
        print(f"  {status_icon} {metric['name']}: {metric['score']}% - {metric['description']}")

    # Issues
    if stats['balance_report']['issues']:
        print(f"\nIssues:")
        for issue in stats['balance_report']['issues']:
            print(f"   - {issue}")

    if stats['balance_report']['warnings']:
        print(f"\nWarnings:")
        for w in stats['balance_report']['warnings']:
            print(f"   - {w}")

    if stats['balance_report']['suggestions']:
        print(f"\nSuggestions:")
        for s in stats['balance_report']['suggestions']:
            print(f"   - {s}")


if __name__ == '__main__':
    main()
