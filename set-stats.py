#!/usr/bin/env python3
"""
Set Statistics - Overview of the MTG set
Shows total cards, rarity breakdown, and basic counts.
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

def main():
    cards = []
    vault_path = Path('.')

    for md_file in list(vault_path.glob('*.md')) + list(vault_path.glob('cards/*.md')):
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

    # Basic counts
    total = len(cards)

    # Rarity breakdown
    rarity_counts = defaultdict(int)
    for card in cards:
        rarity = normalize_rarity(card.get('rarity', 'Unknown'))
        rarity_counts[rarity] += 1

    # Vetted vs unvetted
    vetted = sum(1 for c in cards if 'unvetted' not in c.get('tags', []))
    unvetted = total - vetted

    # Card types
    type_counts = defaultdict(int)
    for card in cards:
        card_type = card.get('type', 'Unknown')
        type_counts[card_type] += 1

    # Creatures with power/toughness
    creatures = [c for c in cards if c.get('type') == 'Creature']

    # Print results
    print("=" * 50)
    print("MTG SET STATISTICS")
    print("=" * 50)
    print(f"\nTotal Cards: {total}")
    print(f"  - Vetted: {vetted}")
    print(f"  - Unvetted: {unvetted}")

    print("\n" + "-" * 30)
    print("RARITY BREAKDOWN")
    print("-" * 30)
    rarity_order = ['Common', 'Uncommon', 'Rare', 'Mythic', 'Unknown']
    for rarity in rarity_order:
        if rarity in rarity_counts:
            count = rarity_counts[rarity]
            pct = (count / total) * 100
            print(f"  {rarity}: {count} ({pct:.1f}%)")

    print("\n" + "-" * 30)
    print("CARD TYPES")
    print("-" * 30)
    for card_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        pct = (count / total) * 100
        print(f"  {card_type}: {count} ({pct:.1f}%)")

    print("\n" + "-" * 30)
    print("CREATURES")
    print("-" * 30)
    print(f"  Total Creatures: {len(creatures)}")
    if creatures:
        creature_pct = (len(creatures) / total) * 100
        print(f"  Creature Ratio: {creature_pct:.1f}%")

    print("\n" + "=" * 50)

if __name__ == '__main__':
    main()
