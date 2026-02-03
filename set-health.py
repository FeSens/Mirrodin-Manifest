#!/usr/bin/env python3
"""
Set Health Check - Compare current set against design guidelines
Checks rarity balance, color balance, creature ratios, and more.
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

    if isinstance(color_value, list):
        return [c.strip().title() for c in color_value]

    color_str = str(color_value).strip()

    if '/' in color_str:
        return [c.strip().title() for c in color_str.split('/')]

    if ',' in color_str:
        return [c.strip().title() for c in color_str.split(',')]

    if color_str.lower() == 'colorless':
        return ['Colorless']

    return [color_str.title()]

def get_color_identity(colors):
    """Get color identity (mono/multi/colorless)."""
    if colors == ['Colorless']:
        return 'Colorless'
    if len(colors) > 1:
        return 'Multicolor'
    return colors[0]

def check_passed(condition):
    return "✓" if condition else "✗"

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

    total = len(cards)

    # Gather data
    rarity_counts = defaultdict(int)
    color_by_rarity = defaultdict(lambda: defaultdict(int))
    type_counts = defaultdict(int)
    cmc_counts = defaultdict(int)

    for card in cards:
        rarity = normalize_rarity(card.get('rarity'))
        rarity_counts[rarity] += 1

        colors = normalize_colors(card.get('color'))
        identity = get_color_identity(colors)
        color_by_rarity[rarity][identity] += 1

        # Also track individual colors for balance
        for color in colors:
            if color not in ['Colorless']:
                color_by_rarity[rarity][f'_mono_{color}'] += 1

        card_type = card.get('type', 'Unknown')
        type_counts[card_type] += 1

        cmc = card.get('cmc')
        if cmc is not None:
            try:
                cmc_counts[int(cmc)] += 1
            except (ValueError, TypeError):
                pass

    # Target sizes (Standard Set)
    TARGETS = {
        'Common': 101,
        'Uncommon': 80,
        'Rare': 60,
        'Mythic': 20,
    }

    # Color targets per rarity (approximate)
    COLOR_TARGETS = {
        'Common': 18,  # per color
        'Uncommon': 13,
        'Rare': 10,
        'Mythic': 3,
    }

    print("=" * 60)
    print("SET HEALTH CHECK")
    print("=" * 60)
    print(f"\nTotal Cards: {total}")

    # Rarity Check
    print("\n" + "-" * 40)
    print("RARITY TARGETS (Standard Set: 261 cards)")
    print("-" * 40)
    total_target = sum(TARGETS.values())
    pct_complete = (total / total_target) * 100
    print(f"  Overall Progress: {total}/{total_target} ({pct_complete:.1f}%)")
    print()

    for rarity in ['Common', 'Uncommon', 'Rare', 'Mythic']:
        current = rarity_counts.get(rarity, 0)
        target = TARGETS[rarity]
        pct = (current / target) * 100 if target > 0 else 0
        status = check_passed(current >= target)
        print(f"  {status} {rarity}: {current}/{target} ({pct:.1f}%)")

    # Color Balance Check
    print("\n" + "-" * 40)
    print("COLOR BALANCE BY RARITY")
    print("-" * 40)

    colors = ['White', 'Blue', 'Black', 'Red', 'Green']

    for rarity in ['Common', 'Uncommon', 'Rare', 'Mythic']:
        if rarity not in color_by_rarity:
            continue

        target = COLOR_TARGETS[rarity]
        rarity_data = color_by_rarity[rarity]

        # Count mono-colored cards per color
        color_counts = {}
        for color in colors:
            # Count cards that contain this color
            count = rarity_data.get(color, 0)  # Mono only
            color_counts[color] = count

        multi = rarity_data.get('Multicolor', 0)
        colorless = rarity_data.get('Colorless', 0)

        # Check balance
        values = [color_counts[c] for c in colors]
        if values:
            min_val = min(values)
            max_val = max(values)
            is_balanced = (max_val - min_val) <= 3  # Allow 3 card variance
        else:
            is_balanced = True

        status = check_passed(is_balanced)

        print(f"\n  {status} {rarity} (target ~{target}/color):")
        for color in colors:
            count = color_counts[color]
            diff = count - target
            diff_str = f"+{diff}" if diff > 0 else str(diff)
            print(f"      {color}: {count} ({diff_str})")
        print(f"      Multicolor: {multi}")
        print(f"      Colorless: {colorless}")

    # Creature Ratio Check
    print("\n" + "-" * 40)
    print("CREATURE/SPELL RATIO")
    print("-" * 40)

    creature_count = type_counts.get('Creature', 0)
    creature_pct = (creature_count / total) * 100 if total > 0 else 0

    # Target: 60-65% creatures at common
    common_creatures = sum(1 for c in cards
                          if c.get('type') == 'Creature'
                          and normalize_rarity(c.get('rarity')) == 'Common')
    common_total = rarity_counts.get('Common', 0)
    common_creature_pct = (common_creatures / common_total) * 100 if common_total > 0 else 0

    creature_status = check_passed(55 <= creature_pct <= 70)
    common_status = check_passed(55 <= common_creature_pct <= 70)

    print(f"  {creature_status} Overall Creature Ratio: {creature_pct:.1f}% (target: 55-70%)")
    print(f"  {common_status} Common Creature Ratio: {common_creature_pct:.1f}% (target: 60-65%)")

    # Mana Curve Check
    print("\n" + "-" * 40)
    print("MANA CURVE HEALTH")
    print("-" * 40)

    total_cmc = sum(cmc * count for cmc, count in cmc_counts.items())
    total_with_cmc = sum(cmc_counts.values())
    avg_cmc = total_cmc / total_with_cmc if total_with_cmc > 0 else 0

    # Good limited set has avg CMC around 2.5-3.5
    cmc_status = check_passed(2.5 <= avg_cmc <= 3.5)
    print(f"  {cmc_status} Average CMC: {avg_cmc:.2f} (target: 2.5-3.5)")

    # Check for 2-drops (critical for limited)
    two_drops = cmc_counts.get(2, 0)
    two_drop_pct = (two_drops / total_with_cmc) * 100 if total_with_cmc > 0 else 0
    two_drop_status = check_passed(two_drop_pct >= 15)
    print(f"  {two_drop_status} 2-drops: {two_drops} ({two_drop_pct:.1f}%) (target: 15%+)")

    # Missing Data Check
    print("\n" + "-" * 40)
    print("DATA QUALITY")
    print("-" * 40)

    missing_cmc = sum(1 for c in cards if c.get('cmc') is None)
    missing_color = sum(1 for c in cards if c.get('color') is None)
    missing_rarity = sum(1 for c in cards if normalize_rarity(c.get('rarity')) == 'Unknown')
    missing_type = sum(1 for c in cards if c.get('type') is None or c.get('type') == 'Unknown')

    cmc_quality = check_passed(missing_cmc == 0)
    color_quality = check_passed(missing_color == 0)
    rarity_quality = check_passed(missing_rarity == 0)
    type_quality = check_passed(missing_type == 0)

    print(f"  {cmc_quality} Cards missing CMC: {missing_cmc}")
    print(f"  {color_quality} Cards missing color: {missing_color}")
    print(f"  {rarity_quality} Cards missing/unknown rarity: {missing_rarity}")
    print(f"  {type_quality} Cards missing type: {missing_type}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    issues = []
    if total < total_target * 0.5:
        issues.append(f"Set is less than 50% complete ({total}/{total_target})")
    if not (2.5 <= avg_cmc <= 3.5):
        issues.append(f"Average CMC ({avg_cmc:.2f}) outside ideal range")
    if missing_cmc > 0 or missing_color > 0 or missing_rarity > 0:
        issues.append("Some cards have missing data fields")

    if issues:
        print("\nIssues to address:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\nNo major issues detected!")

    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()
