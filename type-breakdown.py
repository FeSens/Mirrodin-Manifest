#!/usr/bin/env python3
"""
Type Breakdown - Detailed analysis of card types and subtypes
Shows card type distribution, creature subtypes, and tribal themes.
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

def parse_subtypes(subtype_str):
    """Parse subtype string into list of subtypes."""
    if not subtype_str:
        return []
    return [s.strip() for s in str(subtype_str).split()]

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

    # Card type counts
    type_counts = defaultdict(int)
    type_by_rarity = defaultdict(lambda: defaultdict(int))

    # Subtype (creature type) counts
    subtype_counts = defaultdict(int)

    # Creature stats
    creatures = []

    for card in cards:
        card_type = card.get('type', 'Unknown')
        rarity = normalize_rarity(card.get('rarity'))

        type_counts[card_type] += 1
        type_by_rarity[card_type][rarity] += 1

        # Parse subtypes
        subtypes = parse_subtypes(card.get('subtype'))
        for subtype in subtypes:
            subtype_counts[subtype] += 1

        # Track creatures
        if card_type == 'Creature':
            creatures.append({
                'name': card.get('_filename'),
                'subtypes': subtypes,
                'power': card.get('power'),
                'toughness': card.get('toughness'),
                'rarity': rarity
            })

    # Print results
    print("=" * 50)
    print("TYPE BREAKDOWN")
    print("=" * 50)

    print("\n" + "-" * 30)
    print("CARD TYPES")
    print("-" * 30)
    for card_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        pct = (count / total) * 100
        rarity_breakdown = ', '.join(f"{r[0]}:{c}" for r, c in sorted(type_by_rarity[card_type].items()))
        print(f"  {card_type}: {count} ({pct:.1f}%)")
        print(f"    By rarity: {rarity_breakdown}")

    print("\n" + "-" * 30)
    print("CREATURE SUBTYPES (Tribal)")
    print("-" * 30)
    for subtype, count in sorted(subtype_counts.items(), key=lambda x: -x[1]):
        if count >= 2:  # Only show subtypes that appear 2+ times
            print(f"  {subtype}: {count}")

    print("\n  (Showing subtypes with 2+ appearances)")

    print("\n" + "-" * 30)
    print("ALL SUBTYPES")
    print("-" * 30)
    for subtype, count in sorted(subtype_counts.items(), key=lambda x: x[0]):
        print(f"  {subtype}: {count}")

    print("\n" + "-" * 30)
    print("CREATURE STATS")
    print("-" * 30)

    # Power/Toughness distribution
    power_counts = defaultdict(int)
    toughness_counts = defaultdict(int)

    for creature in creatures:
        p = creature.get('power')
        t = creature.get('toughness')
        if p is not None:
            try:
                power_counts[int(p)] += 1
            except (ValueError, TypeError):
                power_counts['*'] += 1
        if t is not None:
            try:
                toughness_counts[int(t)] += 1
            except (ValueError, TypeError):
                toughness_counts['*'] += 1

    print(f"\n  Total Creatures: {len(creatures)}")

    print("\n  Power Distribution:")
    for p in sorted([k for k in power_counts.keys() if isinstance(k, int)]):
        count = power_counts[p]
        print(f"    Power {p}: {count}")
    if '*' in power_counts:
        print(f"    Power *: {power_counts['*']}")

    print("\n  Toughness Distribution:")
    for t in sorted([k for k in toughness_counts.keys() if isinstance(k, int)]):
        count = toughness_counts[t]
        print(f"    Toughness {t}: {count}")
    if '*' in toughness_counts:
        print(f"    Toughness *: {toughness_counts['*']}")

    print("\n" + "=" * 50)

if __name__ == '__main__':
    main()
