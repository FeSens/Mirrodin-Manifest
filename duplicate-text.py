#!/usr/bin/env python3
"""
Find cards with duplicate or similar rules text in the MTG set.
"""

import re
import yaml
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher
from itertools import combinations


# Similarity threshold (0.0 to 1.0) - cards with similarity >= this are reported
SIMILARITY_THRESHOLD = 0.7


def extract_rules_text(filepath: Path) -> tuple[str, str]:
    """Extract card name and rules text from a markdown file."""
    content = filepath.read_text(encoding='utf-8')

    # Get card name from H1
    name_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    name = name_match.group(1).strip() if name_match else filepath.stem

    # Check if it's a card (has card tag in frontmatter)
    is_card = False
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1])
                if frontmatter:
                    tags = frontmatter.get('tags', [])
                    is_card = 'card' in tags or 'token' in tags
            except yaml.YAMLError:
                pass

    if not is_card:
        return None, None

    # Find rules text section
    rules_match = re.search(r'##\s+Rules Text\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL | re.IGNORECASE)
    if not rules_match:
        return name, ""

    rules_section = rules_match.group(1).strip()

    # Extract blockquote content if present
    lines = []
    for line in rules_section.split('\n'):
        if line.startswith('>'):
            lines.append(line[1:].strip())
        elif line.strip() and not lines:
            lines.append(line.strip())

    rules_text = '\n'.join(lines).strip()
    return name, rules_text


def normalize_text(text: str) -> str:
    """Normalize text for comparison (lowercase, collapse whitespace)."""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def similarity_ratio(text1: str, text2: str) -> float:
    """Calculate similarity ratio between two texts."""
    return SequenceMatcher(None, text1, text2).ratio()


def find_exact_duplicates(cards: dict[str, str]) -> dict[str, list[str]]:
    """Find cards with exactly identical rules text."""
    text_to_cards = defaultdict(list)

    for name, rules_text in cards.items():
        normalized = normalize_text(rules_text)
        if normalized:
            text_to_cards[normalized].append(name)

    return {text: names for text, names in text_to_cards.items() if len(names) > 1}


def find_similar_texts(cards: dict[str, str], threshold: float = SIMILARITY_THRESHOLD) -> list[tuple]:
    """Find pairs of cards with similar (but not identical) rules text."""
    similar_pairs = []
    card_items = [(name, normalize_text(text)) for name, text in cards.items() if text.strip()]

    # Compare all pairs
    for (name1, text1), (name2, text2) in combinations(card_items, 2):
        # Skip if texts are identical (handled by exact duplicates)
        if text1 == text2:
            continue

        # Skip very short texts (less meaningful comparisons)
        if len(text1) < 20 or len(text2) < 20:
            continue

        ratio = similarity_ratio(text1, text2)
        if ratio >= threshold:
            similar_pairs.append((name1, name2, ratio, text1, text2))

    # Sort by similarity (highest first)
    similar_pairs.sort(key=lambda x: x[2], reverse=True)
    return similar_pairs


def main():
    script_dir = Path(__file__).parent

    # Find all markdown files
    md_files = list(script_dir.glob('*.md')) + list(script_dir.glob('cards/*.md'))

    # Build card dictionary
    cards = {}
    original_texts = {}

    for md_file in md_files:
        try:
            name, rules_text = extract_rules_text(md_file)
            if name and rules_text:
                cards[name] = rules_text
                original_texts[name] = rules_text
        except Exception as e:
            print(f"Error parsing {md_file.name}: {e}")

    print(f"Analyzed {len(cards)} cards with rules text\n")

    # === EXACT DUPLICATES ===
    print("=" * 80)
    print("## EXACT DUPLICATES")
    print("=" * 80)

    exact_dupes = find_exact_duplicates(cards)

    if exact_dupes:
        print(f"\nFound {len(exact_dupes)} groups of cards with identical rules text:\n")
        print("| Group | Cards | Rules Text |")
        print("|-------|-------|------------|")

        for i, (text, names) in enumerate(sorted(exact_dupes.items(), key=lambda x: len(x[1]), reverse=True), 1):
            card_list = ', '.join(f"**{n}**" for n in names)
            # Get original text formatting
            preview = original_texts[names[0]][:60].replace('\n', ' ').replace('|', '\\|')
            if len(original_texts[names[0]]) > 60:
                preview += "..."
            print(f"| {i} | {card_list} | {preview} |")
    else:
        print("\nNo exact duplicates found.")

    # === SIMILAR TEXTS ===
    print("\n" + "=" * 80)
    print(f"## SIMILAR TEXTS (>= {int(SIMILARITY_THRESHOLD * 100)}% match)")
    print("=" * 80)

    similar = find_similar_texts(cards)

    if similar:
        print(f"\nFound {len(similar)} pairs of cards with similar rules text:\n")
        print("| Similarity | Card 1 | Card 2 | Text Comparison |")
        print("|------------|--------|--------|-----------------|")

        for name1, name2, ratio, text1, text2 in similar[:30]:  # Limit to top 30
            pct = f"{ratio * 100:.0f}%"
            # Show abbreviated texts
            t1_preview = text1[:40].replace('|', '\\|') + ("..." if len(text1) > 40 else "")
            t2_preview = text2[:40].replace('|', '\\|') + ("..." if len(text2) > 40 else "")
            print(f"| {pct} | **{name1}** | **{name2}** | \"{t1_preview}\" vs \"{t2_preview}\" |")

        if len(similar) > 30:
            print(f"\n... and {len(similar) - 30} more pairs")
    else:
        print(f"\nNo similar texts found above {int(SIMILARITY_THRESHOLD * 100)}% threshold.")

    # === SUMMARY ===
    print("\n" + "=" * 80)
    print("## SUMMARY")
    print("=" * 80)
    exact_count = sum(len(names) for names in exact_dupes.values())
    print(f"\n- **Exact duplicates:** {exact_count} cards in {len(exact_dupes)} groups")
    print(f"- **Similar texts:** {len(similar)} pairs above {int(SIMILARITY_THRESHOLD * 100)}% similarity")
    print(f"\nAdjust SIMILARITY_THRESHOLD in the script to find more/fewer similar texts.")


if __name__ == '__main__':
    main()
