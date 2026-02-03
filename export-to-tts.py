#!/usr/bin/env python3
"""
Export MTG Set to Tabletop Simulator

This script generates:
1. Individual card images (PNG) from card data
2. Deck sheet images (10x7 grid) for TTS import
3. TTS save file JSON for easy import

Requirements:
    pip install Pillow

Usage:
    python export-to-tts.py [options]

Options:
    --output DIR          Output directory (default: tts_export)
    --cards-per-sheet N   Cards per sheet (default: 70, i.e., 10x7)
    --card-width N        Card width in pixels (default: 409)
    --card-height N       Card height in pixels (default: 585)
    --limit N             Only export N cards (for testing)
"""

import os
import sys
import json
import math
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml
import textwrap

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("Warning: Pillow not installed. Install with: pip install Pillow")

# Card dimensions (standard MTG ratio is 63:88 mm ≈ 2.5:3.5 inches)
DEFAULT_CARD_WIDTH = 409
DEFAULT_CARD_HEIGHT = 585

# TTS deck sheet: 10 columns x 7 rows = 70 cards
SHEET_COLS = 10
SHEET_ROWS = 7

# Color definitions (RGB)
COLORS = {
    'White': (248, 246, 216),
    'Blue': (14, 104, 171),
    'Black': (75, 61, 68),
    'Red': (211, 32, 42),
    'Green': (0, 115, 62),
    'Colorless': (161, 152, 145),
    'Multicolor': (201, 162, 39),
    'Land': (139, 115, 85),
}

RARITY_COLORS = {
    'Common': (20, 20, 20),
    'Uncommon': (140, 150, 160),
    'Rare': (184, 148, 28),
    'Mythic': (211, 95, 16),
}


def parse_frontmatter(content: str) -> Dict[str, Any]:
    """Parse YAML frontmatter from markdown content."""
    if not content.startswith('---'):
        return {}
    try:
        end_idx = content.index('---', 3)
        yaml_content = content[3:end_idx].strip()
        return yaml.safe_load(yaml_content) or {}
    except (ValueError, yaml.YAMLError):
        return {}


def is_card(frontmatter: Dict) -> bool:
    """Check if frontmatter represents a card."""
    tags = frontmatter.get('tags', [])
    if isinstance(tags, list):
        return 'card' in tags
    return False


def load_cards() -> List[Dict]:
    """Load all cards from the vault."""
    cards = []
    vault_path = Path('.')

    for md_file in list(vault_path.glob('*.md')) + list(vault_path.glob('cards/*.md')):
        try:
            content = md_file.read_text(encoding='utf-8')
            frontmatter = parse_frontmatter(content)

            if not is_card(frontmatter):
                continue

            # Extract card data
            card = {
                'name': frontmatter.get('card_name', md_file.stem),
                'type': frontmatter.get('type', ''),
                'subtype': frontmatter.get('subtype', ''),
                'color': frontmatter.get('color', 'Colorless'),
                'mana_cost': frontmatter.get('mana_cost', ''),
                'cmc': frontmatter.get('cmc', 0),
                'rarity': frontmatter.get('rarity', 'Common'),
                'power': frontmatter.get('power', ''),
                'toughness': frontmatter.get('toughness', ''),
                'rules_text': frontmatter.get('rules_text', ''),
                'flavor_text': frontmatter.get('flavor_text', ''),
                'file': md_file,
            }

            # Extract rules text from content if not in frontmatter
            if not card['rules_text']:
                card['rules_text'] = extract_rules_text(content)

            cards.append(card)

        except Exception as e:
            print(f"Error loading {md_file}: {e}")
            continue

    return sorted(cards, key=lambda x: (x['color'], x['cmc'], x['name']))


def extract_rules_text(content: str) -> str:
    """Extract rules text from markdown content."""
    lines = content.split('\n')
    in_rules = False
    rules_lines = []

    for line in lines:
        if '## Rules Text' in line:
            in_rules = True
            continue
        if in_rules:
            if line.startswith('##'):
                break
            # Clean up the line
            cleaned = line.strip()
            if cleaned.startswith('>'):
                cleaned = cleaned[1:].strip()
            if cleaned:
                rules_lines.append(cleaned)

    return '\n'.join(rules_lines)


def get_type_line(card: Dict) -> str:
    """Generate the type line for a card."""
    type_line = card['type']
    if card['subtype']:
        type_line += f" — {card['subtype']}"
    return type_line


def create_card_image(card: Dict, width: int, height: int) -> 'Image.Image':
    """Create a card image from card data."""
    if not HAS_PIL:
        raise RuntimeError("Pillow is required for image generation")

    # Determine card color for background
    color = card['color']
    if color in COLORS:
        bg_color = COLORS[color]
    elif '/' in str(color):  # Multicolor
        bg_color = COLORS['Multicolor']
    else:
        bg_color = COLORS['Colorless']

    # Create base image
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Try to load fonts, fall back to default
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf", 24)
        text_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Times New Roman.ttf", 16)
        small_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Times New Roman.ttf", 14)
        mana_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 16)
    except:
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 24)
            text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 16)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 14)
            mana_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        except:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
            mana_font = ImageFont.load_default()

    # Card frame border
    border_color = (30, 30, 30)
    draw.rectangle([0, 0, width-1, height-1], outline=border_color, width=3)

    # Inner frame
    margin = 15
    inner_color = (250, 248, 235)  # Off-white for text areas

    # Header area (name + mana cost)
    header_height = 40
    draw.rectangle([margin, margin, width-margin, margin+header_height], fill=inner_color, outline=border_color)

    # Card name
    name = card['name']
    draw.text((margin+10, margin+8), name, fill=(0, 0, 0), font=title_font)

    # Mana cost (right side)
    mana_cost = card['mana_cost'] or ''
    if mana_cost:
        # Simple mana cost display
        mana_text = mana_cost.replace('{', '').replace('}', ' ').strip()
        bbox = draw.textbbox((0, 0), mana_text, font=mana_font)
        mana_width = bbox[2] - bbox[0]
        draw.text((width - margin - 10 - mana_width, margin + 12), mana_text, fill=(0, 0, 0), font=mana_font)

    # Art area (placeholder)
    art_top = margin + header_height + 5
    art_height = 200
    art_color = (200, 200, 200)
    draw.rectangle([margin, art_top, width-margin, art_top+art_height], fill=art_color, outline=border_color)

    # Art placeholder text
    art_text = "🎨"
    draw.text((width//2 - 20, art_top + art_height//2 - 20), art_text, fill=(150, 150, 150), font=title_font)

    # Type line
    type_top = art_top + art_height + 5
    type_height = 30
    draw.rectangle([margin, type_top, width-margin, type_top+type_height], fill=inner_color, outline=border_color)

    type_line = get_type_line(card)
    draw.text((margin+10, type_top+6), type_line, fill=(0, 0, 0), font=text_font)

    # Rarity symbol
    rarity = card['rarity']
    rarity_color = RARITY_COLORS.get(rarity, (0, 0, 0))
    rarity_symbol = {'Common': '●', 'Uncommon': '◆', 'Rare': '◆', 'Mythic': '◆'}.get(rarity, '●')
    draw.text((width - margin - 20, type_top + 6), rarity_symbol, fill=rarity_color, font=text_font)

    # Text box
    text_top = type_top + type_height + 5
    text_bottom = height - margin - 35 if card['power'] else height - margin - 10
    draw.rectangle([margin, text_top, width-margin, text_bottom], fill=inner_color, outline=border_color)

    # Rules text
    rules = card['rules_text'] or ''
    if rules:
        # Word wrap
        wrapper = textwrap.TextWrapper(width=40)
        wrapped = wrapper.fill(rules)
        lines = wrapped.split('\n')[:8]  # Limit lines

        y_pos = text_top + 8
        for line in lines:
            draw.text((margin+10, y_pos), line, fill=(0, 0, 0), font=small_font)
            y_pos += 18

    # Flavor text (italic, smaller)
    flavor = card.get('flavor_text', '')
    if flavor and y_pos < text_bottom - 40:
        y_pos += 10
        wrapper = textwrap.TextWrapper(width=45)
        wrapped = wrapper.fill(flavor)
        lines = wrapped.split('\n')[:3]

        for line in lines:
            if y_pos < text_bottom - 20:
                draw.text((margin+10, y_pos), f""{line}"", fill=(80, 80, 80), font=small_font)
                y_pos += 16

    # Power/Toughness box (for creatures)
    if card['power'] and card['toughness']:
        pt_width = 50
        pt_height = 30
        pt_x = width - margin - pt_width
        pt_y = height - margin - pt_height
        draw.rectangle([pt_x, pt_y, pt_x + pt_width, pt_y + pt_height], fill=bg_color, outline=border_color, width=2)

        pt_text = f"{card['power']}/{card['toughness']}"
        bbox = draw.textbbox((0, 0), pt_text, font=title_font)
        text_width = bbox[2] - bbox[0]
        draw.text((pt_x + (pt_width - text_width)//2, pt_y + 3), pt_text, fill=(0, 0, 0), font=title_font)

    # Set name at bottom
    set_name = "Mirrodin Manifest"
    draw.text((margin + 10, height - margin - 18), set_name, fill=(100, 100, 100), font=small_font)

    return img


def create_card_back(width: int, height: int) -> 'Image.Image':
    """Create a card back image."""
    if not HAS_PIL:
        raise RuntimeError("Pillow is required")

    img = Image.new('RGB', (width, height), (30, 20, 50))
    draw = ImageDraw.Draw(img)

    # Border
    draw.rectangle([0, 0, width-1, height-1], outline=(100, 80, 40), width=8)

    # Inner oval design
    center_x, center_y = width // 2, height // 2
    oval_w, oval_h = width - 60, height - 80
    draw.ellipse([center_x - oval_w//2, center_y - oval_h//2,
                  center_x + oval_w//2, center_y + oval_h//2],
                 fill=(50, 35, 70), outline=(150, 120, 60), width=4)

    # Inner design
    inner_w, inner_h = oval_w - 40, oval_h - 50
    draw.ellipse([center_x - inner_w//2, center_y - inner_h//2,
                  center_x + inner_w//2, center_y + inner_h//2],
                 fill=(40, 25, 55), outline=(120, 100, 50), width=2)

    # Text
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf", 28)
    except:
        font = ImageFont.load_default()

    text = "MIRRODIN\nMANIFEST"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    draw.text((center_x - text_width//2, center_y - 30), text, fill=(200, 180, 100), font=font, align='center')

    return img


def create_deck_sheet(cards: List[Dict], start_idx: int,
                      card_width: int, card_height: int,
                      cols: int = SHEET_COLS, rows: int = SHEET_ROWS) -> 'Image.Image':
    """Create a deck sheet image (grid of cards)."""
    if not HAS_PIL:
        raise RuntimeError("Pillow is required")

    sheet_width = card_width * cols
    sheet_height = card_height * rows
    sheet = Image.new('RGB', (sheet_width, sheet_height), (0, 0, 0))

    cards_on_sheet = cards[start_idx:start_idx + cols * rows]

    for idx, card in enumerate(cards_on_sheet):
        row = idx // cols
        col = idx % cols
        x = col * card_width
        y = row * card_height

        try:
            card_img = create_card_image(card, card_width, card_height)
            sheet.paste(card_img, (x, y))
        except Exception as e:
            print(f"  Error creating image for {card['name']}: {e}")

    return sheet


def create_tts_save(cards: List[Dict], deck_urls: List[str], back_url: str,
                    card_width: int, card_height: int) -> Dict:
    """Create a TTS save file JSON."""

    # Calculate how many cards per sheet
    cards_per_sheet = SHEET_COLS * SHEET_ROWS

    deck_ids = []
    contained_objects = []

    for i, card in enumerate(cards):
        sheet_idx = i // cards_per_sheet
        card_on_sheet = i % cards_per_sheet

        # TTS card ID format: XXYY where XX is position (1-indexed), YY is deck ID
        card_id = (card_on_sheet + 1) * 100 + (sheet_idx + 1)
        deck_ids.append(card_id)

        contained_objects.append({
            "Name": "Card",
            "Nickname": card['name'],
            "Description": f"{get_type_line(card)}\n\n{card['rules_text']}",
            "CardID": card_id,
            "Transform": {
                "posX": 0, "posY": 0, "posZ": 0,
                "rotX": 0, "rotY": 180, "rotZ": 180,
                "scaleX": 1, "scaleY": 1, "scaleZ": 1
            }
        })

    # Build custom deck definitions
    custom_deck = {}
    for sheet_idx, url in enumerate(deck_urls):
        custom_deck[str(sheet_idx + 1)] = {
            "FaceURL": url,
            "BackURL": back_url,
            "NumWidth": SHEET_COLS,
            "NumHeight": SHEET_ROWS,
            "BackIsHidden": True,
            "UniqueBack": False
        }

    save_data = {
        "SaveName": "Mirrodin Manifest - Custom Set",
        "GameMode": "",
        "Date": "",
        "Table": "",
        "Sky": "",
        "Note": "Custom MTG Set: Mirrodin Manifest\nGenerated by export-to-tts.py",
        "Rules": "",
        "PlayerTurn": "",
        "ObjectStates": [
            {
                "Name": "DeckCustom",
                "Nickname": "Mirrodin Manifest",
                "Description": f"Custom MTG Set - {len(cards)} cards",
                "Transform": {
                    "posX": 0, "posY": 1, "posZ": 0,
                    "rotX": 0, "rotY": 180, "rotZ": 180,
                    "scaleX": 1.5, "scaleY": 1, "scaleZ": 1.5
                },
                "DeckIDs": deck_ids,
                "CustomDeck": custom_deck,
                "ContainedObjects": contained_objects
            }
        ]
    }

    return save_data


def main():
    parser = argparse.ArgumentParser(description='Export MTG set to Tabletop Simulator')
    parser.add_argument('--output', default='tts_export', help='Output directory')
    parser.add_argument('--card-width', type=int, default=DEFAULT_CARD_WIDTH, help='Card width in pixels')
    parser.add_argument('--card-height', type=int, default=DEFAULT_CARD_HEIGHT, help='Card height in pixels')
    parser.add_argument('--limit', type=int, help='Limit number of cards to export')
    parser.add_argument('--no-images', action='store_true', help='Skip image generation (JSON only)')
    args = parser.parse_args()

    print("=" * 60)
    print("TABLETOP SIMULATOR EXPORT")
    print("=" * 60)

    # Load cards
    print("\nLoading cards...")
    cards = load_cards()
    print(f"Found {len(cards)} cards")

    if args.limit:
        cards = cards[:args.limit]
        print(f"Limited to {args.limit} cards")

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)
    print(f"\nOutput directory: {output_dir.absolute()}")

    if args.no_images or not HAS_PIL:
        if not HAS_PIL:
            print("\n⚠ Pillow not installed - skipping image generation")
            print("  Install with: pip install Pillow")

        # Generate JSON with placeholder URLs
        print("\nGenerating TTS save file (with placeholder URLs)...")
        deck_urls = ["REPLACE_WITH_YOUR_DECK_SHEET_URL"]
        back_url = "REPLACE_WITH_YOUR_CARD_BACK_URL"

        save_data = create_tts_save(cards, deck_urls, back_url, args.card_width, args.card_height)

        save_path = output_dir / "MirrodinManifest.json"
        with open(save_path, 'w') as f:
            json.dump(save_data, f, indent=2)
        print(f"✓ Saved: {save_path}")

        print("\n" + "=" * 60)
        print("NEXT STEPS:")
        print("=" * 60)
        print("""
1. Generate card images using another tool (Magic Set Editor, Card Conjurer)
2. Arrange images into deck sheets (10x7 grid, 70 cards per sheet)
3. Upload deck sheets and card back to an image host
4. Edit the JSON file and replace placeholder URLs
5. Import JSON into TTS: Games > Save & Load > Import
        """)
        return

    # Generate images
    print("\nGenerating card images...")

    # Individual cards
    cards_dir = output_dir / "cards"
    cards_dir.mkdir(exist_ok=True)

    for i, card in enumerate(cards):
        print(f"  [{i+1}/{len(cards)}] {card['name']}")
        try:
            img = create_card_image(card, args.card_width, args.card_height)
            safe_name = "".join(c if c.isalnum() or c in ' -_' else '_' for c in card['name'])
            img.save(cards_dir / f"{safe_name}.png")
        except Exception as e:
            print(f"    ✗ Error: {e}")

    # Card back
    print("\nGenerating card back...")
    back_img = create_card_back(args.card_width, args.card_height)
    back_path = output_dir / "card_back.png"
    back_img.save(back_path)
    print(f"✓ Saved: {back_path}")

    # Deck sheets
    print("\nGenerating deck sheets...")
    cards_per_sheet = SHEET_COLS * SHEET_ROWS
    num_sheets = math.ceil(len(cards) / cards_per_sheet)

    sheet_paths = []
    for sheet_idx in range(num_sheets):
        start_idx = sheet_idx * cards_per_sheet
        print(f"  Sheet {sheet_idx + 1}/{num_sheets} (cards {start_idx + 1}-{min(start_idx + cards_per_sheet, len(cards))})")

        sheet = create_deck_sheet(cards, start_idx, args.card_width, args.card_height)
        sheet_path = output_dir / f"deck_sheet_{sheet_idx + 1}.png"
        sheet.save(sheet_path)
        sheet_paths.append(sheet_path)
        print(f"    ✓ Saved: {sheet_path}")

    # TTS save file
    print("\nGenerating TTS save file...")

    # Use placeholder URLs - user needs to upload images and update
    deck_urls = [f"UPLOAD_deck_sheet_{i+1}.png_AND_PASTE_URL_HERE" for i in range(num_sheets)]
    back_url = "UPLOAD_card_back.png_AND_PASTE_URL_HERE"

    save_data = create_tts_save(cards, deck_urls, back_url, args.card_width, args.card_height)

    save_path = output_dir / "MirrodinManifest.json"
    with open(save_path, 'w') as f:
        json.dump(save_data, f, indent=2)
    print(f"✓ Saved: {save_path}")

    # Summary
    print("\n" + "=" * 60)
    print("EXPORT COMPLETE")
    print("=" * 60)
    print(f"""
Generated files in {output_dir}/:
  - cards/           Individual card images ({len(cards)} cards)
  - card_back.png    Card back image
  - deck_sheet_*.png Deck sheets ({num_sheets} sheets)
  - MirrodinManifest.json  TTS save file

NEXT STEPS:
1. Upload deck_sheet_*.png to an image host (Imgur, Steam Cloud, etc.)
2. Upload card_back.png to the same host
3. Edit MirrodinManifest.json and replace the placeholder URLs
4. In TTS: Games > Save & Load > Import > Select the JSON file

RECOMMENDED IMAGE HOSTS:
- Steam Cloud (via TTS Cloud Manager)
- Imgur (public links)
- Your own web server

TIP: For Steam Cloud, use TTS's built-in "Cloud Manager" in the
     Modding > Cloud menu to upload images directly.
    """)


if __name__ == "__main__":
    main()
