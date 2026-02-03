#!/usr/bin/env python3
"""
Color Breakdown - Distribution of colors across the set
Shows mono-color, multicolor, and colorless counts by rarity.
"""

import os
import re
import yaml
from collections import defaultdict
from pathlib import Path

def parse_frontmatter(content):
    """Extract YAML frontmatter from markdown file."""
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1))
        except yaml.YAMLError:
            return None
    return None

def is_card(frontmatter):
    """Check if the file is a card."""
    if not frontmatter:
        return False
    tags = frontmatter.get('tags', [])
    return 'card' in tags

def normalize_rarity(rarity):
    """Normalize rarity names."""
    if not rarity:
        return 'Unknown'
    rarity = rarity.lower().strip()
    if 'mythic' in rarity:
        return 'Mythic'
    elif 'rare' in rarity:
        return 'Rare'
    elif 'uncommon' in rarity:
        return 'Uncommon'
    elif 'common' in rarity:
        return 'Common'
    return rarity.title()

def normalize_colors(color_value):
    """Normalize color field to a list of colors."""
    if not color_value:
        return ['Colorless']

    # Handle list format
    if isinstance(color_value, list):
        return [c.strip().title() for c in color_value]

    # Handle string format
    color_str = str(color_value).strip()

    # Handle slash-separated (e.g., "Blue/White")
    if '/' in color_str:
        return [c.strip().title() for c in color_str.split('/')]

    # Handle comma-separated
    if ',' in color_str:
        return [c.strip().title() for c in color_str.split(',')]

    # Single color
    if color_str.lower() == 'colorless':
        return ['Colorless']

    return [color_str.title()]

def get_color_identity(colors):
    """Get color identity string (W, U, B, R, G, Multicolor, Colorless)."""
    if colors == ['Colorless']:
        return 'Colorless'
    if len(colors) > 1:
        return 'Multicolor'
    return colors[0]

def main():
    cards = []
    vault_path = Path('.')

    for md_file in vault_path.glob('*.md'):
        try:
            content = md_file.read_text(encoding='utf-8')
            frontmatter = parse_frontmatter(content)
            if is_card(frontmatter):
                frontmatter['_filename'] = md_file.stem
                cards.append(frontmatter)
        except Exception:
            continue

    if not cards:
        print("No cards found in the current directory.")
        return

    total = len(cards)

    # Color counts overall
    color_counts = defaultdict(int)
    # Color counts by rarity
    color_by_rarity = defaultdict(lambda: defaultdict(int))
    # Multicolor tracking
    multicolor_cards = []

    for card in cards:
        colors = normalize_colors(card.get('color'))
        rarity = normalize_rarity(card.get('rarity'))
        identity = get_color_identity(colors)

        color_counts[identity] += 1
        color_by_rarity[rarity][identity] += 1

        if len(colors) > 1 and colors != ['Colorless']:
            multicolor_cards.append({
                'name': card.get('_filename'),
                'colors': colors,
                'rarity': rarity
            })

    # Also count individual color appearances
    individual_colors = defaultdict(int)
    for card in cards:
        colors = normalize_colors(card.get('color'))
        for color in colors:
            if color != 'Colorless':
                individual_colors[color] += 1

    # Print results
    print("=" * 50)
    print("COLOR BREAKDOWN")
    print("=" * 50)

    print("\n" + "-" * 30)
    print("OVERALL DISTRIBUTION")
    print("-" * 30)
    color_order = ['White', 'Blue', 'Black', 'Red', 'Green', 'Multicolor', 'Colorless']
    for color in color_order:
        if color in color_counts:
            count = color_counts[color]
            pct = (count / total) * 100
            print(f"  {color}: {count} ({pct:.1f}%)")

    print("\n" + "-" * 30)
    print("COLOR APPEARANCES (including multicolor)")
    print("-" * 30)
    for color in ['White', 'Blue', 'Black', 'Red', 'Green']:
        if color in individual_colors:
            count = individual_colors[color]
            print(f"  {color}: {count}")

    print("\n" + "-" * 30)
    print("BY RARITY")
    print("-" * 30)
    rarity_order = ['Common', 'Uncommon', 'Rare', 'Mythic']
    for rarity in rarity_order:
        if rarity in color_by_rarity:
            print(f"\n  {rarity}:")
            for color in color_order:
                if color in color_by_rarity[rarity]:
                    count = color_by_rarity[rarity][color]
                    print(f"    {color}: {count}")

    if multicolor_cards:
        print("\n" + "-" * 30)
        print(f"MULTICOLOR CARDS ({len(multicolor_cards)})")
        print("-" * 30)
        for card in sorted(multicolor_cards, key=lambda x: x['name']):
            colors_str = '/'.join(card['colors'])
            print(f"  [{card['rarity']}] {card['name']} ({colors_str})")

    print("\n" + "=" * 50)

if __name__ == '__main__':
    main()
