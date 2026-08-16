"""
TikTok Demo Generator for AI Roast Me
Generates sample roasts with test images that you can screen-record for TikTok.

Usage:
    python make_tiktok_demos.py

This creates demo roasts in the /demos folder that you can screen-record.
Each demo is a JSON file with the roast text + the image used.
"""

import os
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))
from config import GEMINI_API_KEY, VISION_MODEL, ROAST_STYLES, ROAST_MODES, MODE_PROMPTS

if not GEMINI_API_KEY:
    print("ERROR: No GEMINI_API_KEY found. Get one at aistudio.google.com/apikey")
    sys.exit(1)

from google import genai
from google.genai import types

client = genai.Client(api_key=GEMINI_API_KEY)

DEMOS_DIR = Path(__file__).parent / "demos"
DEMOS_DIR.mkdir(exist_ok=True)


def create_character_image(filename, bg_color, skin_color, hair_color, accessory=""):
    """Create a simple cartoon character for demo purposes."""
    img = Image.new("RGB", (400, 500), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Hair
    draw.ellipse([120, 80, 280, 200], fill=hair_color)
    # Face
    draw.ellipse([140, 120, 260, 260], fill=skin_color)
    # Eyes
    draw.ellipse([165, 170, 185, 190], fill=(40, 40, 40))
    draw.ellipse([215, 170, 235, 190], fill=(40, 40, 40))
    # Mouth
    draw.arc([170, 210, 230, 250], 0, 180, fill=(80, 30, 30), width=3)
    # Body/shirt
    draw.rectangle([130, 260, 270, 450], fill=(60, 80, 120))

    if accessory == "sunglasses":
        draw.rectangle([155, 165, 195, 195], fill=(20, 20, 20))
        draw.rectangle([205, 165, 245, 195], fill=(20, 20, 20))
        draw.rectangle([195, 175, 205, 180], fill=(20, 20, 20))
    elif accessory == "hat":
        draw.rectangle([110, 90, 290, 130], fill=(80, 40, 20))
        draw.rectangle([100, 120, 300, 135], fill=(80, 40, 20))

    img.save(filename)
    return filename


def generate_roast(image_path, style="savage", mode="solo"):
    """Generate a roast using Gemini."""
    style_prompt = ROAST_STYLES[style]["prompt"]
    mode_template = MODE_PROMPTS[mode]
    final_prompt = mode_template.format(style_prompt=style_prompt)

    image_bytes = Path(image_path).read_bytes()
    response = client.models.generate_content(
        model=VISION_MODEL,
        contents=[types.Content(parts=[
            types.Part(inline_data=types.Blob(mime_type="image/png", data=image_bytes)),
            types.Part(text=final_prompt),
        ])],
        config=types.GenerateContentConfig(max_output_tokens=400, temperature=0.95),
    )
    return response.text


# Demo scenarios for TikTok
DEMOS = [
    {
        "name": "01_sunglasses_bro",
        "title": "Roasting the Sunglasses Indoors Bro",
        "tiktok_hook": "POV: you let AI roast your selfie 🔥",
        "bg": (180, 200, 220),
        "skin": (255, 220, 180),
        "hair": (60, 40, 20),
        "accessory": "sunglasses",
        "style": "savage",
    },
    {
        "name": "02_hat_guy",
        "title": "Roasting the Hat Guy",
        "tiktok_hook": "AI roasted my friend and he's not talking to me 💀",
        "bg": (200, 180, 150),
        "skin": (240, 200, 160),
        "hair": (40, 30, 20),
        "accessory": "hat",
        "style": "dating",
    },
    {
        "name": "03_grandma_roast",
        "title": "Grandma Style Roast",
        "tiktok_hook": "AI grandma roasted me and it was BRUTAL 👵🔥",
        "bg": (220, 180, 200),
        "skin": (255, 210, 170),
        "hair": (200, 200, 200),
        "accessory": "",
        "style": "grandma",
    },
    {
        "name": "04_gamer_roast",
        "title": "Gamer Style Roast",
        "tiktok_hook": "Toxic gamer AI roasted my profile pic 🎮💀",
        "bg": (50, 50, 80),
        "skin": (255, 215, 175),
        "hair": (30, 30, 30),
        "accessory": "",
        "style": "gamer",
    },
    {
        "name": "05_corporate_roast",
        "title": "Corporate Roast",
        "tiktok_hook": "AI evaluated my LinkedIn photo as a hire 💼🔥",
        "bg": (100, 120, 140),
        "skin": (245, 210, 170),
        "hair": (50, 40, 30),
        "accessory": "",
        "style": "corporate",
    },
]


def main():
    print("=" * 60)
    print("  AI ROAST ME - TikTok Demo Generator")
    print("=" * 60)
    print()

    results = []
    for demo in DEMOS:
        print(f"Generating: {demo['title']}...")
        img_path = DEMOS_DIR / f"{demo['name']}.png"

        create_character_image(
            img_path,
            bg_color=demo["bg"],
            skin_color=demo["skin"],
            hair_color=demo["hair"],
            accessory=demo["accessory"],
        )

        try:
            roast = generate_roast(str(img_path), style=demo["style"])
            print(f"  Roast: {roast[:100]}...")
            results.append({
                "name": demo["name"],
                "title": demo["title"],
                "tiktok_hook": demo["tiktok_hook"],
                "style": demo["style"],
                "image": str(img_path),
                "roast": roast,
            })
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({
                "name": demo["name"],
                "title": demo["title"],
                "error": str(e),
            })
        print()

    # Save all demos to JSON
    output_file = DEMOS_DIR / "demos.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print("=" * 60)
    print(f"  {len(results)} demos generated in /demos folder!")
    print(f"  Results saved to: {output_file}")
    print()
    print("  TikTok Recording Guide:")
    print("  1. Open http://localhost:5000 in your browser")
    print("  2. Screen record (Win+G or OBS)")
    print("  3. Upload a demo image, select style, hit ROAST")
    print("  4. Add the TikTok hook as your caption")
    print("  5. Post 3-5 per day for maximum virality")
    print("=" * 60)


if __name__ == "__main__":
    main()
