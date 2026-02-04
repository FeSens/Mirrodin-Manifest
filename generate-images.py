#!/usr/bin/env python3
"""
MTG Card Image Generator
Generates card art images using OpenRouter with Gemini image generation.
Uses async/concurrent requests for faster generation.

Usage:
    python generate-images.py [options]

Options:
    --limit N                     Only generate N images
    --card "Card Name"            Generate image for specific card
    --force                       Regenerate even if image exists
    --dry-run                     Show what would be generated without doing it
    --workers N                   Number of concurrent workers (default: 3)
"""

import os
import sys
import re
import json
import time
import argparse
import asyncio
import aiohttp
import base64
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import yaml

# Configuration
IMAGES_DIR = "images"
CARDS_DIR = "cards"
PROGRESS_FILE = ".image_gen_progress.json"
CACHE_DIR = ".image_cache"

# OpenRouter Configuration
OPENROUTER_API_KEY = "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"
OPENROUTER_MODEL = "google/gemini-3-pro-image-preview"  # DO NOT CHANGE THIS
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY_BASE = 5  # seconds
REQUEST_TIMEOUT = 180  # seconds


@dataclass
class GenerationResult:
    card_name: str
    success: bool
    image_path: Optional[Path] = None
    error: Optional[str] = None
    retries: int = 0


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


def extract_image_prompt_from_content(content: str) -> str:
    """Extract image prompt from markdown content (## Image Prompt section)."""
    match = re.search(r'##\s+Image Prompt\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL | re.IGNORECASE)
    if not match:
        return ""

    section = match.group(1).strip()

    lines = []
    for line in section.split('\n'):
        if line.startswith('>'):
            lines.append(line[1:].strip())
        elif line.strip() and not lines:
            lines.append(line.strip())

    return '\n'.join(lines).strip()


def is_card(frontmatter: Dict) -> bool:
    """Check if frontmatter represents a card."""
    tags = frontmatter.get('tags', [])
    if isinstance(tags, list):
        return 'card' in tags
    return False


def get_card_name_from_content(content: str) -> str:
    """Get card name from H1 header."""
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return ""


def sanitize_filename(name: str) -> str:
    """Sanitize a string for use as a filename."""
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = re.sub(r'\s+', '_', name)
    return name


def get_image_path(card_name: str) -> Path:
    """Get the path where the image should be saved."""
    safe_name = sanitize_filename(card_name)
    return Path(IMAGES_DIR) / f"{safe_name}.png"


def image_exists(card_name: str) -> bool:
    """Check if an image already exists for a card."""
    return get_image_path(card_name).exists()


def enhance_prompt(base_prompt: str) -> str:
    """Enhance the image prompt with Mirrodin Manifest art guidelines."""
    return (
        f"ARTWORK ONLY - NO card frame, NO text, NO borders, NO title, NO mana symbols, NO card elements whatsoever. "
        f"Generate ONLY the illustration art as a standalone fantasy painting. "
        f"{base_prompt} "
        f"Setting: Mirrodin Manifest - a metallic plane of corporate dystopia where chrome reflects nothing and gold weighs everything. "
        f"All organic creatures have metal components: chrome bone plating, metallic hair strands, iron-veined skin. "
        f"Style: Painterly fantasy illustration in the style of Magic: The Gathering artists like Kev Walker, Seb McKinnon, Greg Staples. "
        f"Mood: Oppressive mundanity, gilded decay, surveillance architecture. Characters should feel tired, not heroic. "
        f"NOT generic sci-fi or cyberpunk - this is fantasy with metallic elements. "
        f"Output: Pure illustration art only, 4:3 aspect ratio."
    )


def save_image_immediately(image_data: bytes, card_name: str) -> Path:
    """Save image data to disk immediately."""
    image_path = get_image_path(card_name)
    image_path.parent.mkdir(exist_ok=True)
    image_path.write_bytes(image_data)
    return image_path


def get_cache_path(card_name: str) -> Path:
    """Get the cache file path for a card's API response."""
    safe_name = sanitize_filename(card_name)
    return Path(CACHE_DIR) / f"{safe_name}.json"


def save_response_cache(card_name: str, response: dict):
    """Save raw API response to cache."""
    cache_path = get_cache_path(card_name)
    cache_path.parent.mkdir(exist_ok=True)
    cache_path.write_text(json.dumps(response, indent=2))


def load_response_cache(card_name: str) -> Optional[dict]:
    """Load cached API response if it exists."""
    cache_path = get_cache_path(card_name)
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text())
        except:
            pass
    return None


def extract_image_from_response(result: dict, debug: bool = False) -> Optional[bytes]:
    """Extract image bytes from API response."""
    if debug:
        print(f"    DEBUG: Response keys: {list(result.keys())}")

    choices = result.get("choices", [])
    if not choices:
        if debug:
            print(f"    DEBUG: No choices in response")
        return None

    choice = choices[0]
    message = choice.get("message", {})

    # Check for images field first (OpenRouter/Gemini format)
    images = message.get("images", [])
    if images:
        if debug:
            print(f"    DEBUG: Found {len(images)} images in 'images' field")
        # Images are typically base64 encoded
        for idx, img in enumerate(images):
            if debug:
                print(f"    DEBUG: Image {idx} type: {type(img)}")
                if isinstance(img, str):
                    print(f"    DEBUG: Image {idx} starts with: {img[:100]}...")
                elif isinstance(img, dict):
                    print(f"    DEBUG: Image {idx} keys: {list(img.keys())}")
            if isinstance(img, str):
                # Direct base64 string
                if img.startswith("data:image"):
                    base64_data = img.split(",", 1)[1] if "," in img else ""
                    if base64_data:
                        return base64.b64decode(base64_data)
                else:
                    # Assume it's raw base64
                    try:
                        return base64.b64decode(img)
                    except:
                        pass
            elif isinstance(img, dict):
                # Could be {image_url: "data:..."}, {url: "data:..."} or {data: "..."}
                # Check image_url field first (OpenRouter format)
                image_url = img.get("image_url", "")
                if image_url:
                    if debug:
                        print(f"    DEBUG: image_url starts with: {str(image_url)[:100]}...")
                    if isinstance(image_url, str) and image_url.startswith("data:image"):
                        base64_data = image_url.split(",", 1)[1] if "," in image_url else ""
                        if base64_data:
                            return base64.b64decode(base64_data)
                    elif isinstance(image_url, dict):
                        # Nested format: {image_url: {url: "data:..."}}
                        nested_url = image_url.get("url", "")
                        if nested_url.startswith("data:image"):
                            base64_data = nested_url.split(",", 1)[1] if "," in nested_url else ""
                            if base64_data:
                                return base64.b64decode(base64_data)

                url = img.get("url", "")
                if url.startswith("data:image"):
                    base64_data = url.split(",", 1)[1] if "," in url else ""
                    if base64_data:
                        return base64.b64decode(base64_data)
                data = img.get("data", "")
                if data:
                    try:
                        return base64.b64decode(data)
                    except:
                        pass

    content = message.get("content", "")

    # Check if content is a list (multimodal response)
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict):
                # Check for image_url type
                if item.get("type") == "image_url":
                    image_data = item.get("image_url", {})
                    url = image_data.get("url", "")
                    if url.startswith("data:image"):
                        base64_data = url.split(",", 1)[1] if "," in url else ""
                        if base64_data:
                            return base64.b64decode(base64_data)
                # Check for inline_data
                elif "inline_data" in item:
                    inline = item["inline_data"]
                    if "data" in inline:
                        return base64.b64decode(inline["data"])
    # Check if content contains base64 image data directly
    elif isinstance(content, str):
        if content.startswith("data:image"):
            base64_data = content.split(",", 1)[1] if "," in content else ""
            if base64_data:
                return base64.b64decode(base64_data)
        # Try to find base64 image in response
        match = re.search(r'data:image/[^;]+;base64,([A-Za-z0-9+/=]+)', content)
        if match:
            return base64.b64decode(match.group(1))

    return None


async def generate_image_async(
    session: aiohttp.ClientSession,
    prompt: str,
    card_name: str,
    semaphore: asyncio.Semaphore,
    use_cache: bool = True
) -> GenerationResult:
    """Generate image using OpenRouter with retries and immediate save."""

    # Check cache first
    if use_cache:
        cached = load_response_cache(card_name)
        if cached:
            print(f"  [{card_name}] Found cached response")
            image_data = extract_image_from_response(cached, debug=False)
            if image_data:
                image_path = save_image_immediately(image_data, card_name)
                print(f"  ✓ [{card_name}] Saved from cache: {image_path}")
                return GenerationResult(
                    card_name=card_name,
                    success=True,
                    image_path=image_path,
                    retries=0
                )
            else:
                print(f"  [{card_name}] Cache exists but no valid image, re-fetching...")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/mtg-card-generator",
        "X-Title": "MTG Card Image Generator"
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Create an image: {prompt}"
                    }
                ]
            }
        ],
        "response_format": {"type": "image"}
    }

    async with semaphore:
        for attempt in range(MAX_RETRIES):
            try:
                print(f"  [{card_name}] Attempt {attempt + 1}/{MAX_RETRIES}...")

                async with session.post(
                    OPENROUTER_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
                ) as response:

                    if response.status == 200:
                        result = await response.json()

                        # Save raw response to cache immediately
                        save_response_cache(card_name, result)
                        print(f"  [{card_name}] Response cached")

                        image_data = extract_image_from_response(result, debug=False)

                        if image_data:
                            # SAVE IMMEDIATELY
                            image_path = save_image_immediately(image_data, card_name)
                            print(f"  ✓ [{card_name}] Saved: {image_path}")
                            return GenerationResult(
                                card_name=card_name,
                                success=True,
                                image_path=image_path,
                                retries=attempt
                            )
                        else:
                            error_msg = "No image in response"
                            print(f"  ✗ [{card_name}] {error_msg}")

                    elif response.status == 429:
                        # Rate limited - wait and retry
                        retry_after = int(response.headers.get('Retry-After', RETRY_DELAY_BASE * (attempt + 1)))
                        print(f"  ⏳ [{card_name}] Rate limited, waiting {retry_after}s...")
                        await asyncio.sleep(retry_after)
                        continue

                    else:
                        error_text = await response.text()
                        error_msg = f"API error {response.status}: {error_text[:200]}"
                        print(f"  ✗ [{card_name}] {error_msg}")

            except asyncio.TimeoutError:
                error_msg = f"Timeout after {REQUEST_TIMEOUT}s"
                print(f"  ✗ [{card_name}] {error_msg}")
            except aiohttp.ClientError as e:
                error_msg = f"Request error: {e}"
                print(f"  ✗ [{card_name}] {error_msg}")
            except Exception as e:
                error_msg = f"Unexpected error: {e}"
                print(f"  ✗ [{card_name}] {error_msg}")

            # Wait before retry with exponential backoff
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_DELAY_BASE * (2 ** attempt)
                print(f"  ⏳ [{card_name}] Retrying in {delay}s...")
                await asyncio.sleep(delay)

        return GenerationResult(
            card_name=card_name,
            success=False,
            error=error_msg,
            retries=MAX_RETRIES
        )


def load_cards(specific_card: Optional[str] = None) -> List[Dict]:
    """Load all cards or a specific card."""
    cards = []
    vault_path = Path('.')

    for md_file in list(vault_path.glob('*.md')) + list(vault_path.glob('cards/*.md')):
        try:
            content = md_file.read_text(encoding='utf-8')
            frontmatter = parse_frontmatter(content)

            if not is_card(frontmatter):
                continue

            card_name = get_card_name_from_content(content)
            if not card_name:
                card_name = md_file.stem

            image_prompt = extract_image_prompt_from_content(content)
            if not image_prompt:
                image_prompt = frontmatter.get('image_prompt', '')

            if specific_card and card_name.lower() != specific_card.lower():
                continue

            cards.append({
                'name': card_name,
                'file': md_file,
                'prompt': image_prompt,
                'frontmatter': frontmatter
            })

        except Exception as e:
            print(f"Error loading {md_file}: {e}")
            continue

    return sorted(cards, key=lambda x: x['name'])


def load_progress() -> Dict:
    """Load progress from previous runs."""
    progress_path = Path(PROGRESS_FILE)
    if progress_path.exists():
        try:
            return json.loads(progress_path.read_text())
        except:
            pass
    return {"completed": [], "failed": []}


def save_progress(progress: Dict):
    """Save progress to file."""
    Path(PROGRESS_FILE).write_text(json.dumps(progress, indent=2))


async def generate_batch(cards: List[Dict], max_workers: int) -> List[GenerationResult]:
    """Generate images for a batch of cards concurrently."""
    semaphore = asyncio.Semaphore(max_workers)

    connector = aiohttp.TCPConnector(limit=max_workers, force_close=True)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for card in cards:
            prompt = enhance_prompt(card['prompt'])
            task = generate_image_async(session, prompt, card['name'], semaphore)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to failed results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(GenerationResult(
                    card_name=cards[i]['name'],
                    success=False,
                    error=str(result)
                ))
            else:
                processed_results.append(result)

        return processed_results


def main():
    parser = argparse.ArgumentParser(description='Generate MTG card art images using OpenRouter')
    parser.add_argument('--limit', type=int, help='Limit number of images to generate')
    parser.add_argument('--card', help='Generate image for specific card')
    parser.add_argument('--force', action='store_true', help='Regenerate existing images')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    parser.add_argument('--workers', type=int, default=3, help='Number of concurrent workers (default: 3)')
    args = parser.parse_args()

    print("=" * 60)
    print("MTG CARD IMAGE GENERATOR")
    print("=" * 60)
    print(f"Backend: OpenRouter (async)")
    print(f"Model: {OPENROUTER_MODEL}")
    print(f"Workers: {args.workers}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Create images directory
    images_dir = Path(IMAGES_DIR)
    if not args.dry_run:
        images_dir.mkdir(exist_ok=True)

    # Load cards
    cards = load_cards(args.card)
    print(f"Found {len(cards)} cards")

    # Filter cards without prompts
    cards_with_prompts = [c for c in cards if c['prompt']]
    cards_without_prompts = [c for c in cards if not c['prompt']]

    if cards_without_prompts:
        print(f"\n⚠ {len(cards_without_prompts)} cards have no image prompt:")
        for c in cards_without_prompts[:5]:
            print(f"  - {c['name']}")
        if len(cards_without_prompts) > 5:
            print(f"  ... and {len(cards_without_prompts) - 5} more")

    print(f"\n{len(cards_with_prompts)} cards have image prompts")

    # Filter out existing images (unless --force)
    if not args.force:
        cards_to_generate = [c for c in cards_with_prompts if not image_exists(c['name'])]
        skipped = len(cards_with_prompts) - len(cards_to_generate)
        if skipped > 0:
            print(f"⏭ Skipping {skipped} cards with existing images")
    else:
        cards_to_generate = cards_with_prompts

    # Apply limit
    if args.limit:
        cards_to_generate = cards_to_generate[:args.limit]
        print(f"Limited to {len(cards_to_generate)} cards")

    if not cards_to_generate:
        print("\n✓ No images to generate!")
        return

    if args.dry_run:
        print(f"\n[DRY RUN] Would generate {len(cards_to_generate)} images:")
        for card in cards_to_generate:
            print(f"  ○ {card['name']}")
            print(f"    Prompt: {card['prompt'][:60]}...")
        return

    # Generate images
    print(f"\nGenerating {len(cards_to_generate)} images...")
    print("-" * 60)

    start_time = time.time()
    results = asyncio.run(generate_batch(cards_to_generate, args.workers))

    # Calculate stats
    elapsed = time.time() - start_time
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Generated: {len(successful)}")
    print(f"Failed: {len(failed)}")
    print(f"Time: {elapsed:.1f}s ({elapsed/len(cards_to_generate):.1f}s per image)")

    if failed:
        print(f"\nFailed cards:")
        for r in failed:
            print(f"  ✗ {r.card_name}: {r.error}")

    print(f"\nImages saved to: {images_dir.absolute()}")


if __name__ == "__main__":
    main()
