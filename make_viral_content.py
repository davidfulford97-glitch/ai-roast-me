"""
TikTok Viral Content Kit for AI Roast Me
Generates 10 demo roasts with varied characters + writes TikTok scripts.

Run: python make_viral_content.py
Output: /tiktok_kit/ folder with images, roasts, and video scripts
"""

import os
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import sys

sys.path.insert(0, str(Path(__file__).parent))
from config import GEMINI_API_KEY, VISION_MODEL, ROAST_STYLES

if not GEMINI_API_KEY:
    print("ERROR: No GEMINI_API_KEY found.")
    sys.exit(1)

from google import genai
from google.genai import types

client = genai.Client(api_key=GEMINI_API_KEY)
KIT_DIR = Path(__file__).parent / "tiktok_kit"
KIT_DIR.mkdir(exist_ok=True)


def create_character(filename, opts):
    """Create a cartoon character with given options."""
    img = Image.new("RGB", (400, 500), color=opts.get("bg", (100, 100, 150)))
    draw = ImageDraw.Draw(img)

    skin = opts.get("skin", (255, 220, 180))
    hair = opts.get("hair", (60, 40, 20))
    shirt = opts.get("shirt", (60, 80, 120))

    # Hair
    draw.ellipse([120, 80, 280, 200], fill=hair)
    # Face
    draw.ellipse([140, 120, 260, 260], fill=skin)
    # Eyes
    draw.ellipse([165, 170, 185, 190], fill=(40, 40, 40))
    draw.ellipse([215, 170, 235, 190], fill=(40, 40, 40))
    # Eyebrows
    draw.rectangle([160, 155, 190, 162], fill=hair)
    draw.rectangle([210, 155, 240, 162], fill=hair)
    # Mouth
    if opts.get("expression") == "smile":
        draw.arc([170, 210, 230, 250], 0, 180, fill=(80, 30, 30), width=3)
    elif opts.get("expression") == "frown":
        draw.arc([170, 230, 230, 270], 180, 360, fill=(80, 30, 30), width=3)
    else:
        draw.rectangle([175, 225, 225, 232], fill=(80, 30, 30))
    # Body/shirt
    draw.rectangle([130, 260, 270, 450], fill=shirt)

    # Accessories
    acc = opts.get("accessory", "")
    if acc == "sunglasses":
        draw.rectangle([155, 165, 195, 195], fill=(20, 20, 20))
        draw.rectangle([205, 165, 245, 195], fill=(20, 20, 20))
        draw.rectangle([195, 175, 205, 180], fill=(20, 20, 20))
    elif acc == "hat":
        draw.rectangle([110, 90, 290, 130], fill=(80, 40, 20))
        draw.rectangle([100, 120, 300, 135], fill=(80, 40, 20))
    elif acc == "beanie":
        draw.rectangle([115, 85, 285, 140], fill=(40, 60, 100))
    elif acc == "earrings":
        draw.ellipse([135, 195, 145, 205], fill=(255, 215, 0))
        draw.ellipse([255, 195, 265, 205], fill=(255, 215, 0))
    elif acc == "necklace":
        draw.arc([160, 255, 240, 290], 0, 180, fill=(255, 215, 0), width=3)

    # Beard
    if opts.get("beard"):
        draw.ellipse([150, 220, 250, 270], fill=hair)

    img.save(filename)
    return filename


def generate_roast(image_path, style="savage"):
    """Generate a roast using Gemini."""
    style_prompt = ROAST_STYLES[style]["prompt"]
    image_bytes = Path(image_path).read_bytes()
    response = client.models.generate_content(
        model=VISION_MODEL,
        contents=[types.Content(parts=[
            types.Part(inline_data=types.Blob(mime_type="image/png", data=image_bytes)),
            types.Part(text=style_prompt),
        ])],
        config=types.GenerateContentConfig(max_output_tokens=400, temperature=0.95),
    )
    return response.text


# 10 viral TikTok scenarios
SCENARIOS = [
    {
        "name": "01_gym_bro",
        "hook": "AI roasted the gym bro 💪🔥",
        "caption": "POV: you let AI roast your gym selfie #airoast #gym #roast",
        "opts": {"bg": (50,50,50), "skin": (220,180,140), "hair": (30,30,30), "shirt": (50,50,50), "accessory": "beanie", "expression": "frown"},
        "style": "savage",
    },
    {
        "name": "02_dating_profile",
        "hook": "AI reviewed my Tinder profile 💀",
        "caption": "AI roasted my dating profile and I'm deleting the app #dating #tinder #airoast",
        "opts": {"bg": (255,100,100), "skin": (255,220,180), "hair": (80,50,30), "shirt": (200,50,50), "expression": "smile"},
        "style": "dating",
    },
    {
        "name": "03_linkedin_pro",
        "hook": "AI evaluated my LinkedIn photo 💼",
        "caption": "AI judged my LinkedIn profile pic as a hire #linkedin #corporate #airoast",
        "opts": {"bg": (100,120,140), "skin": (245,210,170), "hair": (50,40,30), "shirt": (30,30,60), "expression": "neutral"},
        "style": "corporate",
    },
    {
        "name": "04_sunglasses_douche",
        "hook": "AI roasted the sunglasses indoors guy 🕶️🔥",
        "caption": "Why are you wearing sunglasses inside bro #roast #airoast #cringe",
        "opts": {"bg": (180,200,220), "skin": (255,220,180), "hair": (60,40,20), "shirt": (60,80,120), "accessory": "sunglasses"},
        "style": "savage",
    },
    {
        "name": "05_grandma_roast",
        "hook": "AI grandma roasted me and I cried 👵💔",
        "caption": "Savage grandma AI has no filter #grandma #roast #airoast #savage",
        "opts": {"bg": (220,180,200), "skin": (255,210,170), "hair": (200,200,200), "shirt": (150,100,150), "accessory": "earrings", "expression": "smile"},
        "style": "grandma",
    },
    {
        "name": "06_gamer_toxic",
        "hook": "Toxic gamer AI joined my lobby 🎮💀",
        "caption": "AI gamer roasted my profile pic #gaming #toxic #airoast",
        "opts": {"bg": (30,30,60), "skin": (255,215,175), "hair": (30,30,30), "shirt": (60,60,100), "expression": "neutral"},
        "style": "gamer",
    },
    {
        "name": "07_funny_couple",
        "hook": "AI roasted me and my bestie 👯🔥",
        "caption": "AI roasted us and we're not friends anymore #bestie #roast #airoast",
        "opts": {"bg": (255,182,193), "skin": (255,220,180), "hair": (120,80,40), "shirt": (255,105,180), "accessory": "necklace", "expression": "smile"},
        "style": "funny",
    },
    {
        "name": "08_beard_guy",
        "hook": "AI roasted the beard oil guy 🧔🔥",
        "caption": "AI destroyed this beard bro #beard #roast #airoast #savage",
        "opts": {"bg": (139,90,43), "skin": (240,200,160), "hair": (40,30,20), "shirt": (80,50,30), "beard": True, "expression": "neutral"},
        "style": "savage",
    },
    {
        "name": "09_celebrity_roast",
        "hook": "AI gave me a Comedy Central roast ⭐🔥",
        "caption": "AI roasted me like a celebrity #celebrity #roast #airoast #comedy",
        "opts": {"bg": (255,215,0), "skin": (255,220,180), "hair": (40,30,20), "shirt": (0,0,0), "accessory": "hat", "expression": "smile"},
        "style": "savage",
    },
    {
        "name": "10_selfie_queen",
        "hook": "AI roasted the selfie queen 👑📸",
        "caption": "AI roasted my selfie and I'm mortified #selfie #roast #airoast",
        "opts": {"bg": (200,160,255), "skin": (255,215,175), "hair": (100,50,150), "shirt": (150,100,200), "accessory": "earrings", "expression": "smile"},
        "style": "savage",
    },
]


def main():
    print("=" * 60)
    print("  TIKTOK VIRAL CONTENT KIT GENERATOR")
    print("=" * 60)
    print()

    results = []
    for s in SCENARIOS:
        print(f"Generating: {s['hook']}...")
        img_path = KIT_DIR / f"{s['name']}.png"
        create_character(img_path, s["opts"])

        try:
            roast = generate_roast(str(img_path), s["style"])
            print(f"  → {roast[:80]}...")
            results.append({
                "name": s["name"],
                "hook": s["hook"],
                "caption": s["caption"],
                "style": s["style"],
                "image": str(img_path),
                "roast": roast,
                "script": {
                    "0-3s": f"Show the photo on screen. Text overlay: '{s['hook']}'",
                    "3-5s": "Screen record: upload photo to ai-roast-me.onrender.com",
                    "5-8s": "Select roast style, hit ROAST ME button",
                    "8-15s": "Show the roast result appearing. Zoom in on text.",
                    "15-20s": "End screen: 'Try it free at ai-roast-me.onrender.com'",
                },
            })
        except Exception as e:
            print(f"  ERROR: {e}")
        print()

    # Save results
    with open(KIT_DIR / "content_kit.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Write a readable script file
    with open(KIT_DIR / "TIKTOK_SCRIPTS.md", "w", encoding="utf-8") as f:
        f.write("# TikTok Viral Content Kit - AI Roast Me\n\n")
        f.write("## How to use:\n")
        f.write("1. Open https://ai-roast-me.onrender.com\n")
        f.write("2. Screen record (Win+G on Windows, or use OBS)\n")
        f.write("3. Upload the demo image, pick the style, hit ROAST\n")
        f.write("4. Add the hook as text overlay in first 3 seconds\n")
        f.write("5. Add the caption when posting\n")
        f.write("6. Post 3-5 per day for maximum reach\n\n")
        f.write("## Posting Schedule:\n")
        f.write("- Day 1: Post videos 1, 2, 3\n")
        f.write("- Day 2: Post videos 4, 5, 6\n")
        f.write("- Day 3: Post videos 7, 8, 9\n")
        f.write("- Day 4: Post video 10 + remix best performers\n")
        f.write("- Repeat with new images/styles\n\n")
        f.write("---\n\n")

        for i, r in enumerate(results, 1):
            f.write(f"## Video {i}: {r['hook']}\n\n")
            f.write(f"**Caption:** {r['caption']}\n")
            f.write(f"**Style:** {r['style']}\n")
            f.write(f"**Image:** {r['image']}\n\n")
            f.write(f"**Roast:**\n> {r['roast']}\n\n")
            f.write("**Script:**\n")
            for timing, action in r["script"].items():
                f.write(f"- {timing}: {action}\n")
            f.write("\n---\n\n")

    print("=" * 60)
    print(f"  {len(results)} TikTok videos ready in /tiktok_kit/")
    print(f"  Scripts: tiktok_kit/TIKTOK_SCRIPTS.md")
    print(f"  Images: tiktok_kit/*.png")
    print(f"  Data: tiktok_kit/content_kit.json")
    print()
    print("  NEXT STEPS:")
    print("  1. Open https://ai-roast-me.onrender.com")
    print("  2. Screen record while uploading each demo image")
    print("  3. Post to TikTok with the captions from the script")
    print("  4. Post 3-5 per day. Go viral. Get paid. 🔥")
    print("=" * 60)


if __name__ == "__main__":
    main()
