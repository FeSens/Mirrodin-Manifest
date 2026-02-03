#!/usr/bin/env python3
"""
MTG Card Image Generator
Generates card art images using AI image generation APIs.
Uses the image_prompt field from card YAML frontmatter.

Supports multiple backends:
- Google Imagen (Vertex AI) - DEFAULT
- Replicate (Flux, SDXL, etc.)
- OpenAI DALL-E
- Stability AI

Usage:
    python generate-images.py [options]

Options:
    --backend google|replicate|openai|stability  (default: google)
    --model MODEL_NAME                           (default: imagen-3.0-generate-002)
    --limit N                                    Only generate N images
    --card "Card Name"                           Generate image for specific card
    --force                                      Regenerate even if image exists
    --dry-run                                    Show what would be generated without doing it

Google Imagen Setup:
    1. Install: pip install google-cloud-aiplatform
    2. Set project: export GOOGLE_CLOUD_PROJECT=your-project-id
    3. Authenticate: gcloud auth application-default login

    Or use API key: export GOOGLE_API_KEY=your_api_key
"""

import os
import sys
import re
import json
import time
import argparse
import requests
import base64
from pathlib import Path
from typing import Optional, Dict, Any
import yaml

# Configuration
IMAGES_DIR = "images"
CARDS_DIR = "cards"
DEFAULT_BACKEND = "google"
DEFAULT_MODEL = "imagen-3.0-generate-002"  # Google Imagen 3 (latest)

# API endpoints
GOOGLE_IMAGEN_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateImages"
REPLICATE_API_URL = "https://api.replicate.com/v1/predictions"
OPENAI_API_URL = "https://api.openai.com/v1/images/generations"
STABILITY_API_URL = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"


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


def get_card_name(md_file: Path, frontmatter: Dict) -> str:
    """Get the card name from frontmatter or filename."""
    return frontmatter.get('card_name', md_file.stem)


def sanitize_filename(name: str) -> str:
    """Sanitize a string for use as a filename."""
    # Remove or replace invalid characters
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
    """Enhance the image prompt with MTG-specific styling."""
    style_suffix = (
        " Digital painting, Magic: The Gathering card art style, "
        "highly detailed, dramatic lighting, fantasy illustration, "
        "professional trading card game artwork, 4k, masterpiece quality."
    )
    return base_prompt + style_suffix


class ImageGenerator:
    """Base class for image generation backends."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def generate(self, prompt: str, card_name: str) -> Optional[bytes]:
        raise NotImplementedError


class GoogleImagenGenerator(ImageGenerator):
    """Generate images using Google Imagen API (Vertex AI / Generative AI)."""

    def generate(self, prompt: str, card_name: str) -> Optional[bytes]:
        # Try Generative AI API first (simpler setup)
        url = GOOGLE_IMAGEN_API_URL.format(model=self.model)

        headers = {
            "Content-Type": "application/json",
        }

        # Add API key to URL
        url_with_key = f"{url}?key={self.api_key}"

        payload = {
            "instances": [
                {
                    "prompt": prompt
                }
            ],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": "3:4",  # Card art aspect ratio
                "personGeneration": "allow_adult",
                "safetySetting": "block_few"
            }
        }

        try:
            response = requests.post(
                url_with_key,
                headers=headers,
                json=payload,
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                # Extract base64 image data
                predictions = result.get("predictions", [])
                if predictions:
                    image_b64 = predictions[0].get("bytesBase64Encoded")
                    if image_b64:
                        return base64.b64decode(image_b64)
            else:
                # Try alternative Vertex AI endpoint
                return self._generate_vertex_ai(prompt, card_name)

        except requests.RequestException as e:
            print(f"  ✗ API error: {e}")
            # Try Vertex AI as fallback
            return self._generate_vertex_ai(prompt, card_name)

        return None

    def _generate_vertex_ai(self, prompt: str, card_name: str) -> Optional[bytes]:
        """Fallback to Vertex AI SDK if available."""
        try:
            from google.cloud import aiplatform
            from vertexai.preview.vision_models import ImageGenerationModel

            project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
            if not project_id:
                print("  ✗ Set GOOGLE_CLOUD_PROJECT for Vertex AI")
                return None

            aiplatform.init(project=project_id, location="us-central1")

            model = ImageGenerationModel.from_pretrained(self.model)
            images = model.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio="3:4",
            )

            if images:
                # Save to temp and read bytes
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                    images[0].save(f.name)
                    return Path(f.name).read_bytes()

        except ImportError:
            print("  ✗ Install google-cloud-aiplatform for Vertex AI support")
        except Exception as e:
            print(f"  ✗ Vertex AI error: {e}")

        return None


class ReplicateGenerator(ImageGenerator):
    """Generate images using Replicate API."""

    def generate(self, prompt: str, card_name: str) -> Optional[bytes]:
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }

        # Determine input format based on model
        if "flux" in self.model.lower():
            input_data = {
                "prompt": prompt,
                "num_outputs": 1,
                "aspect_ratio": "3:4",  # Card art aspect ratio
                "output_format": "png",
                "output_quality": 90
            }
        else:
            # SDXL or other models
            input_data = {
                "prompt": prompt,
                "width": 768,
                "height": 1024,
                "num_outputs": 1
            }

        payload = {
            "version": self._get_model_version(),
            "input": input_data
        }

        try:
            # Start prediction
            response = requests.post(
                REPLICATE_API_URL,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            prediction = response.json()

            # Poll for completion
            prediction_url = prediction.get("urls", {}).get("get")
            if not prediction_url:
                print(f"  ✗ No prediction URL returned")
                return None

            # Wait for result
            for _ in range(120):  # Max 2 minutes
                time.sleep(1)
                result = requests.get(prediction_url, headers=headers, timeout=30)
                result.raise_for_status()
                status = result.json()

                if status["status"] == "succeeded":
                    output = status.get("output")
                    if output:
                        image_url = output[0] if isinstance(output, list) else output
                        img_response = requests.get(image_url, timeout=60)
                        img_response.raise_for_status()
                        return img_response.content
                    break
                elif status["status"] == "failed":
                    error = status.get("error", "Unknown error")
                    print(f"  ✗ Generation failed: {error}")
                    return None

            print(f"  ✗ Timeout waiting for image")
            return None

        except requests.RequestException as e:
            print(f"  ✗ API error: {e}")
            return None

    def _get_model_version(self) -> str:
        """Get the model version hash for Replicate."""
        # Common model versions (these may need updating)
        versions = {
            "black-forest-labs/flux-schnell": "bf53bdb93d739c9c915091f7f5e75b842d4dac08955574496f4e4165a2792c5e",
            "black-forest-labs/flux-dev": "5a43e12c20f0f83a1a0c4e5e5e7b0a42b5c5e5e5e5e5e5e5e5e5e5e5e5e5e5e5",
            "stability-ai/sdxl": "39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"
        }
        return versions.get(self.model, self.model)


class OpenAIGenerator(ImageGenerator):
    """Generate images using OpenAI DALL-E API."""

    def generate(self, prompt: str, card_name: str) -> Optional[bytes]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model or "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
            "quality": "hd",
            "response_format": "url"
        }

        try:
            response = requests.post(
                OPENAI_API_URL,
                headers=headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            result = response.json()

            image_url = result["data"][0]["url"]
            img_response = requests.get(image_url, timeout=60)
            img_response.raise_for_status()
            return img_response.content

        except requests.RequestException as e:
            print(f"  ✗ API error: {e}")
            return None


class StabilityGenerator(ImageGenerator):
    """Generate images using Stability AI API."""

    def generate(self, prompt: str, card_name: str) -> Optional[bytes]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        payload = {
            "text_prompts": [{"text": prompt, "weight": 1}],
            "cfg_scale": 7,
            "height": 1024,
            "width": 768,
            "samples": 1,
            "steps": 30
        }

        try:
            response = requests.post(
                STABILITY_API_URL,
                headers=headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            result = response.json()

            image_data = result["artifacts"][0]["base64"]
            return base64.b64decode(image_data)

        except requests.RequestException as e:
            print(f"  ✗ API error: {e}")
            return None


def get_generator(backend: str, model: str) -> ImageGenerator:
    """Get the appropriate image generator based on backend."""
    api_key_vars = {
        "google": "GOOGLE_API_KEY",
        "replicate": "REPLICATE_API_TOKEN",
        "openai": "OPENAI_API_KEY",
        "stability": "STABILITY_API_KEY"
    }

    key_var = api_key_vars.get(backend)
    if not key_var:
        raise ValueError(f"Unknown backend: {backend}")

    api_key = os.environ.get(key_var)
    if not api_key:
        raise ValueError(
            f"Missing API key. Set {key_var} environment variable.\n"
            f"Example: export {key_var}=your_api_key_here"
        )

    generators = {
        "google": GoogleImagenGenerator,
        "replicate": ReplicateGenerator,
        "openai": OpenAIGenerator,
        "stability": StabilityGenerator
    }

    # Set default model based on backend
    if not model or model == DEFAULT_MODEL:
        default_models = {
            "google": "imagen-3.0-generate-002",
            "replicate": "black-forest-labs/flux-schnell",
            "openai": "dall-e-3",
            "stability": "stable-diffusion-xl-1024-v1-0"
        }
        model = default_models.get(backend, model)

    return generators[backend](api_key, model)


def update_card_with_image(md_file: Path, image_path: Path) -> bool:
    """Update card file to include image link."""
    try:
        content = md_file.read_text(encoding='utf-8')

        # Check if image link already exists
        if 'card_image:' in content or '## Card Image' in content:
            return True

        # Add image link to frontmatter
        relative_path = f"../{image_path}"

        if content.startswith('---'):
            # Find end of frontmatter
            end_idx = content.index('---', 3)
            frontmatter = content[3:end_idx]
            rest = content[end_idx:]

            # Add card_image field
            new_frontmatter = frontmatter.rstrip() + f"\ncard_image: \"{relative_path}\"\n"
            new_content = "---" + new_frontmatter + rest
        else:
            # No frontmatter, add image section
            new_content = content + f"\n\n## Card Image\n![[{image_path.name}]]\n"

        md_file.write_text(new_content, encoding='utf-8')
        return True

    except Exception as e:
        print(f"  ✗ Failed to update card file: {e}")
        return False


def load_cards(specific_card: Optional[str] = None) -> list:
    """Load all cards or a specific card."""
    cards = []
    vault_path = Path('.')

    for md_file in list(vault_path.glob('*.md')) + list(vault_path.glob('cards/*.md')):
        try:
            content = md_file.read_text(encoding='utf-8')
            frontmatter = parse_frontmatter(content)

            if not is_card(frontmatter):
                continue

            card_name = get_card_name(md_file, frontmatter)
            image_prompt = frontmatter.get('image_prompt', '')

            if specific_card and card_name.lower() != specific_card.lower():
                continue

            cards.append({
                'name': card_name,
                'file': md_file,
                'prompt': image_prompt,
                'frontmatter': frontmatter
            })

        except Exception:
            continue

    return sorted(cards, key=lambda x: x['name'])


def main():
    parser = argparse.ArgumentParser(description='Generate MTG card art images')
    parser.add_argument('--backend', choices=['google', 'replicate', 'openai', 'stability'],
                        default=DEFAULT_BACKEND, help='Image generation backend (default: google)')
    parser.add_argument('--model', default=None, help='Model to use (default: imagen-3.0-generate-002 for Google)')
    parser.add_argument('--limit', type=int, help='Limit number of images to generate')
    parser.add_argument('--card', help='Generate image for specific card')
    parser.add_argument('--force', action='store_true', help='Regenerate existing images')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    parser.add_argument('--no-link', action='store_true', help='Do not update card files with image links')
    args = parser.parse_args()

    # Set default model based on backend if not specified
    model = args.model
    if not model:
        default_models = {
            "google": "imagen-3.0-generate-002",
            "replicate": "black-forest-labs/flux-schnell",
            "openai": "dall-e-3",
            "stability": "stable-diffusion-xl-1024-v1-0"
        }
        model = default_models.get(args.backend, DEFAULT_MODEL)

    print("=" * 60)
    print("MTG CARD IMAGE GENERATOR")
    print("=" * 60)
    print(f"Backend: {args.backend}")
    print(f"Model: {model}")
    print()

    # Create images directory
    images_dir = Path(IMAGES_DIR)
    if not args.dry_run:
        images_dir.mkdir(exist_ok=True)

    # Load cards
    cards = load_cards(args.card)
    print(f"Found {len(cards)} cards")

    if args.limit:
        cards = cards[:args.limit]
        print(f"Limited to {len(cards)} cards")

    # Filter cards without prompts
    cards_with_prompts = [c for c in cards if c['prompt']]
    cards_without_prompts = [c for c in cards if not c['prompt']]

    if cards_without_prompts:
        print(f"\n⚠ {len(cards_without_prompts)} cards have no image_prompt:")
        for c in cards_without_prompts[:5]:
            print(f"  - {c['name']}")
        if len(cards_without_prompts) > 5:
            print(f"  ... and {len(cards_without_prompts) - 5} more")

    print(f"\n{len(cards_with_prompts)} cards have image prompts")

    if args.dry_run:
        print("\n[DRY RUN] Would generate images for:")
        for card in cards_with_prompts:
            exists = "✓ exists" if image_exists(card['name']) else "○ new"
            print(f"  {exists} {card['name']}")
        return

    # Initialize generator
    try:
        generator = get_generator(args.backend, model)
    except ValueError as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)

    # Generate images
    generated = 0
    skipped = 0
    failed = 0

    print("\nGenerating images...")
    print("-" * 60)

    for i, card in enumerate(cards_with_prompts, 1):
        card_name = card['name']
        image_path = get_image_path(card_name)

        print(f"\n[{i}/{len(cards_with_prompts)}] {card_name}")

        # Check if image exists
        if image_exists(card_name) and not args.force:
            print(f"  ⏭ Image exists, skipping (use --force to regenerate)")
            skipped += 1
            continue

        # Enhance and generate
        prompt = enhance_prompt(card['prompt'])
        print(f"  Prompt: {card['prompt'][:80]}...")
        print(f"  Generating with {args.backend}...")

        image_data = generator.generate(prompt, card_name)

        if image_data:
            # Save image
            image_path.parent.mkdir(exist_ok=True)
            image_path.write_bytes(image_data)
            print(f"  ✓ Saved: {image_path}")

            # Update card file
            if not args.no_link:
                if update_card_with_image(card['file'], image_path):
                    print(f"  ✓ Updated card file with image link")

            generated += 1
        else:
            failed += 1

        # Rate limiting
        time.sleep(1)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Generated: {generated}")
    print(f"Skipped: {skipped}")
    print(f"Failed: {failed}")
    print(f"\nImages saved to: {images_dir.absolute()}")


if __name__ == "__main__":
    main()
