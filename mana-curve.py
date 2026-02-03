#!/usr/bin/env python3
"""
Mana Curve - Distribution of mana values (CMC) across the set
Shows CMC breakdown overall, by rarity, and by card type.
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

    # CMC counts
    cmc_counts = defaultdict(int)
    cmc_by_rarity = defaultdict(lambda: defaultdict(int))
    cmc_by_type = defaultdict(lambda: defaultdict(int))

    # Track for average
    total_cmc = 0
    cards_with_cmc = 0

    for card in cards:
        cmc = card.get('cmc')
        if cmc is not None:
            try:
                cmc = int(cmc)
                cmc_counts[cmc] += 1
                total_cmc += cmc
                cards_with_cmc += 1

                rarity = normalize_rarity(card.get('rarity'))
                cmc_by_rarity[rarity][cmc] += 1

                card_type = card.get('type', 'Unknown')
                cmc_by_type[card_type][cmc] += 1
            except (ValueError, TypeError):
                pass

    # Calculate average
    avg_cmc = total_cmc / cards_with_cmc if cards_with_cmc > 0 else 0

    # Print results
    print("=" * 50)
    print("MANA CURVE (CMC Distribution)")
    print("=" * 50)

    print(f"\nAverage CMC: {avg_cmc:.2f}")
    print(f"Cards with CMC data: {cards_with_cmc}/{total}")

    print("\n" + "-" * 30)
    print("OVERALL DISTRIBUTION")
    print("-" * 30)
    max_cmc = max(cmc_counts.keys()) if cmc_counts else 0
    for cmc in range(0, max_cmc + 1):
        count = cmc_counts.get(cmc, 0)
        if count > 0:
            pct = (count / cards_with_cmc) * 100
            bar = '█' * int(pct / 2)
            print(f"  {cmc}: {count:3d} ({pct:5.1f}%) {bar}")

    print("\n" + "-" * 30)
    print("CREATURE MANA CURVE")
    print("-" * 30)
    if 'Creature' in cmc_by_type:
        creature_cmc = cmc_by_type['Creature']
        creature_total = sum(creature_cmc.values())
        for cmc in range(0, max_cmc + 1):
            count = creature_cmc.get(cmc, 0)
            if count > 0:
                pct = (count / creature_total) * 100
                bar = '█' * int(pct / 2)
                print(f"  {cmc}: {count:3d} ({pct:5.1f}%) {bar}")

    print("\n" + "-" * 30)
    print("BY RARITY")
    print("-" * 30)
    rarity_order = ['Common', 'Uncommon', 'Rare', 'Mythic']
    for rarity in rarity_order:
        if rarity in cmc_by_rarity:
            rarity_data = cmc_by_rarity[rarity]
            rarity_total = sum(rarity_data.values())
            rarity_avg = sum(cmc * count for cmc, count in rarity_data.items()) / rarity_total if rarity_total > 0 else 0
            print(f"\n  {rarity} (avg: {rarity_avg:.2f}):")
            for cmc in range(0, max_cmc + 1):
                count = rarity_data.get(cmc, 0)
                if count > 0:
                    print(f"    CMC {cmc}: {count}")

    print("\n" + "-" * 30)
    print("BY CARD TYPE")
    print("-" * 30)
    for card_type in sorted(cmc_by_type.keys()):
        type_data = cmc_by_type[card_type]
        type_total = sum(type_data.values())
        type_avg = sum(cmc * count for cmc, count in type_data.items()) / type_total if type_total > 0 else 0
        cmc_range = f"{min(type_data.keys())}-{max(type_data.keys())}"
        print(f"  {card_type}: {type_total} cards, avg CMC {type_avg:.2f}, range {cmc_range}")

    print("\n" + "=" * 50)

if __name__ == '__main__':
    main()
