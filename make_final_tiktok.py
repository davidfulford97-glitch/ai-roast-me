"""
Generate TikTok slideshows with REAL stock photos from Unsplash.
Downloads photos, roasts them with Gemini, and creates TikTok-ready slides.
"""

import os
import json
import textwrap
import requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import sys

sys.path.insert(0, str(Path(__file__).parent))
from config import GEMINI_API_KEY, VISION_MODEL, ROAST_STYLES

from google import genai
from google.genai import types

client = genai.Client(api_key=GEMINI_API_KEY)

PHOTO_DIR = Path(__file__).parent / "stock_photos"
OUTPUT_DIR = Path(__file__).parent / "tiktok_final"
OUTPUT_DIR.mkdir(exist_ok=True)

# Map stock photos to scenarios
SCENARIOS = [
    {"name": "01_gym_bro", "hook": "AI roasted the gym bro", "caption": "POV: you let AI roast your gym selfie #airoast #gym #roast", "photo": "gym_bro.jpg", "style": "savage"},
    {"name": "02_dating_profile", "hook": "AI reviewed my Tinder profile", "caption": "AI roasted my dating profile and I'm deleting the app #dating #tinder #airoast", "photo": "selfie_girl.jpg", "style": "dating"},
    {"name": "03_linkedin_pro", "hook": "AI evaluated my LinkedIn photo", "caption": "AI judged my LinkedIn profile pic as a hire #linkedin #corporate #airoast", "photo": "corporate_guy.jpg", "style": "corporate"},
    {"name": "04_sunglasses_douche", "hook": "AI roasted the sunglasses indoors guy", "caption": "Why are you wearing sunglasses inside bro #roast #airoast #cringe", "photo": "sunglasses3.jpg", "style": "savage"},
    {"name": "05_grandma_roast", "hook": "AI grandma roasted me and I cried", "caption": "Savage grandma AI has no filter #grandma #roast #airoast #savage", "photo": "grandma4.jpg", "style": "grandma"},
    {"name": "06_gamer_toxic", "hook": "Toxic gamer AI joined my lobby", "caption": "AI gamer roasted my profile pic #gaming #toxic #airoast", "photo": "gamer.jpg", "style": "gamer"},
    {"name": "07_funny_couple", "hook": "AI roasted me and my bestie", "caption": "AI roasted us and we're not friends anymore #bestie #roast #airoast", "photo": "bestie.jpg", "style": "funny"},
    {"name": "08_beard_guy", "hook": "AI roasted the beard oil guy", "caption": "AI destroyed this beard bro #beard #roast #airoast #savage", "photo": "beard_guy.jpg", "style": "savage"},
    {"name": "09_celebrity_roast", "hook": "AI gave me a Comedy Central roast", "caption": "AI roasted me like a celebrity #celebrity #roast #airoast #comedy", "photo": "celebrity.jpg", "style": "savage"},
    {"name": "10_selfie_queen", "hook": "AI roasted the selfie queen", "caption": "AI roasted my selfie and I'm mortified #selfie #roast #airoast", "photo": "selfie_queen.jpg", "style": "savage"},
]


def get_font(size, bold=True):
    paths = ["C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"]
    for p in paths:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()


def generate_roast(image_path, style="savage"):
    style_prompt = ROAST_STYLES[style]["prompt"]
    image_bytes = Path(image_path).read_bytes()
    response = client.models.generate_content(
        model=VISION_MODEL,
        contents=[types.Content(parts=[
            types.Part(inline_data=types.Blob(mime_type="image/jpeg", data=image_bytes)),
            types.Part(text=style_prompt),
        ])],
        config=types.GenerateContentConfig(max_output_tokens=400, temperature=0.95),
    )
    return response.text


def make_hook_slide(filename, hook, bg_color=(20, 5, 40)):
    img = Image.new("RGB", (1080, 1920), color=bg_color)
    draw = ImageDraw.Draw(img)
    for cx, cy, r, color in [(540, 400, 300, (255, 0, 110, 40)), (200, 1500, 250, (131, 56, 236, 40)), (800, 1700, 200, (58, 134, 255, 30))]:
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(overlay).ellipse([cx-r, cy-r, cx+r, cy+r], fill=color)
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)
    draw.text((540, 500), "🔥", fill="white", anchor="mm", font=get_font(120))
    font_hook = get_font(60)
    lines = textwrap.wrap(hook, width=25)
    y = 750
    for line in lines:
        draw.text((540, y), line, fill="white", anchor="mm", font=font_hook)
        y += 80
    draw.text((540, 1700), "ai-roast-me.onrender.com", fill=(255, 190, 11), anchor="mm", font=get_font(36))
    draw.text((540, 1760), "Try it FREE", fill=(255, 255, 255), anchor="mm", font=get_font(30))
    img.save(filename)


def make_photo_slide(filename, photo_path, bg_color=(20, 5, 40)):
    img = Image.new("RGB", (1080, 1920), color=bg_color)
    draw = ImageDraw.Draw(img)
    try:
        photo = Image.open(photo_path).convert("RGB")
        photo.thumbnail((800, 800), Image.Resampling.LANCZOS)
        px = (1080 - photo.width) // 2
        py = 500
        img.paste(photo, (px, py))
    except: pass
    draw.text((540, 350), "📸 Uploading photo...", fill="white", anchor="mm", font=get_font(48))
    draw.text((540, 1400), "Let's see what AI says", fill=(255, 190, 11), anchor="mm", font=get_font(36))
    img.save(filename)


def make_roast_slide(filename, roast_text, style_name, bg_color=(20, 5, 40)):
    img = Image.new("RGB", (1080, 1920), color=bg_color)
    draw = ImageDraw.Draw(img)
    for cx, cy, r, color in [(540, 300, 250, (255, 0, 110, 50)), (540, 1600, 300, (251, 86, 7, 30))]:
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(overlay).ellipse([cx-r, cy-r, cx+r, cy+r], fill=color)
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)
    font_badge = get_font(32)
    badge_text = f"🔥 {style_name.upper()} ROAST"
    bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw = bbox[2] - bbox[0]
    draw.rounded_rectangle([540-bw//2-20, 180, 540+bw//2+20, 240], radius=20, fill=(255, 0, 110))
    draw.text((540, 210), badge_text, fill="white", anchor="mm", font=font_badge)
    font_roast = get_font(42)
    wrapped = []
    for paragraph in roast_text.split("\n"):
        wrapped.extend(textwrap.wrap(paragraph, width=38))
    y = 350
    for line in wrapped:
        if y > 1600: break
        draw.text((540, y), line, fill="white", anchor="mm", font=font_roast)
        y += 60
    draw.text((540, 1750), "Get roasted FREE at", fill=(180, 180, 180), anchor="mm", font=get_font(28))
    draw.text((540, 1800), "ai-roast-me.onrender.com", fill=(255, 190, 11), anchor="mm", font=get_font(34))
    img.save(filename)


def make_cta_slide(filename, bg_color=(20, 5, 40)):
    img = Image.new("RGB", (1080, 1920), color=bg_color)
    draw = ImageDraw.Draw(img)
    for cx, cy, r, color in [(540, 700, 350, (255, 0, 110, 60)), (540, 1200, 300, (131, 56, 236, 40))]:
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(overlay).ellipse([cx-r, cy-r, cx+r, cy+r], fill=color)
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)
    draw.text((540, 600), "🔥", fill="white", anchor="mm", font=get_font(150))
    draw.text((540, 850), "GET ROASTED", fill="white", anchor="mm", font=get_font(72))
    draw.text((540, 950), "BY AI", fill=(255, 0, 110), anchor="mm", font=get_font(72))
    draw.text((540, 1100), "FREE", fill=(0, 255, 136), anchor="mm", font=get_font(80))
    draw.text((540, 1400), "👉 ai-roast-me.onrender.com", fill=(255, 190, 11), anchor="mm", font=get_font(40))
    draw.text((540, 1470), "Link in bio", fill=(180, 180, 180), anchor="mm", font=get_font(32))
    img.save(filename)


def main():
    print("=" * 60)
    print("  TIKTOK SLIDESHOW GENERATOR (REAL PHOTOS)")
    print("=" * 60)

    results = []
    for i, s in enumerate(SCENARIOS, 1):
        photo_path = PHOTO_DIR / s["photo"]
        if not photo_path.exists():
            print(f"SKIP {s['name']} - photo not found")
            continue

        print(f"\n[{i}/10] {s['hook']}...")
        
        # Generate roast
        try:
            roast = generate_roast(str(photo_path), s["style"])
            print(f"  Roast: {roast[:80]}...")
        except Exception as e:
            print(f"  Roast failed: {e}")
            continue

        # Create slides
        vid_dir = OUTPUT_DIR / f"video_{i:02d}"
        vid_dir.mkdir(exist_ok=True)
        
        make_hook_slide(vid_dir / "slide_1_hook.png", s["hook"])
        make_photo_slide(vid_dir / "slide_2_photo.png", str(photo_path))
        make_roast_slide(vid_dir / "slide_3_roast.png", roast, s["style"].title())
        make_cta_slide(vid_dir / "slide_4_cta.png")
        print(f"  ✓ 4 slides created")

        results.append({"video": i, "hook": s["hook"], "caption": s["caption"], "roast": roast})

    # Save results
    with open(OUTPUT_DIR / "results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Write guide
    with open(OUTPUT_DIR / "POSTING_GUIDE.md", "w", encoding="utf-8") as f:
        f.write("# TikTok Posting Guide\n\n## How to post:\n1. Open TikTok → Create → Upload\n2. Select 4 photos from video_XX folder (in order)\n3. Add caption + hashtags\n4. Post!\n\n")
        for r in results:
            f.write(f"### Video {r['video']}: {r['hook']}\n**Caption:** {r['caption']}\n\n> {r['roast']}\n\n---\n\n")

    print(f"\n{'='*60}")
    print(f"  {len(results)} TikTok slideshows ready in tiktok_final/")
    print(f"  Open the folder and upload to TikTok!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
