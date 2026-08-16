"""
TikTok Slideshow Generator
Creates ready-to-post TikTok slideshow images with roast text overlaid.
No browser automation needed - generates images directly.
"""

import os
import json
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

KIT_DIR = Path(__file__).parent / "tiktok_kit"
OUTPUT_DIR = Path(__file__).parent / "tiktok_ready"
OUTPUT_DIR.mkdir(exist_ok=True)

# Load roasts from content kit
with open(KIT_DIR / "content_kit.json", "r", encoding="utf-8") as f:
    scenarios = json.load(f)


def get_font(size, bold=True):
    """Get a font that works on Windows."""
    font_paths = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except:
                pass
    return ImageFont.load_default()


def make_hook_slide(filename, hook, bg_color=(20, 5, 40)):
    """Create the opening hook slide (1080x1920 for TikTok)."""
    img = Image.new("RGB", (1080, 1920), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Gradient-like glow circles
    for cx, cy, r, color in [
        (540, 400, 300, (255, 0, 110, 40)),
        (200, 1500, 250, (131, 56, 236, 40)),
        (800, 1700, 200, (58, 134, 255, 30)),
    ]:
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.ellipse([cx-r, cy-r, cx+r, cy+r], fill=color)
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

    # Fire emoji
    font_emoji = get_font(120)
    draw.text((540, 500), "🔥", fill="white", anchor="mm", font=font_emoji)

    # Hook text
    font_hook = get_font(60)
    lines = textwrap.wrap(hook, width=25)
    y = 750
    for line in lines:
        draw.text((540, y), line, fill="white", anchor="mm", font=font_hook)
        y += 80

    # CTA at bottom
    font_cta = get_font(36)
    draw.text((540, 1700), "ai-roast-me.onrender.com", fill=(255, 190, 11), anchor="mm", font=font_cta)
    draw.text((540, 1760), "Try it FREE", fill=(255, 255, 255), anchor="mm", font=get_font(30))

    img.save(filename)
    return filename


def make_photo_slide(filename, photo_path, bg_color=(20, 5, 40)):
    """Create a slide showing the uploaded photo."""
    img = Image.new("RGB", (1080, 1920), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Load and resize the photo
    try:
        photo = Image.open(photo_path).convert("RGB")
        # Scale to fit width with padding
        max_w = 800
        max_h = 800
        photo.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
        # Center it
        px = (1080 - photo.width) // 2
        py = 500
        img.paste(photo, (px, py))
    except:
        pass

    # Label
    font = get_font(48)
    draw.text((540, 350), "📸 Uploading photo...", fill="white", anchor="mm", font=font)
    draw.text((540, 1400), "Let's see what AI says", fill=(255, 190, 11), anchor="mm", font=get_font(36))

    img.save(filename)
    return filename


def make_roast_slide(filename, roast_text, style_name, bg_color=(20, 5, 40)):
    """Create the roast result slide."""
    img = Image.new("RGB", (1080, 1920), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Glow
    for cx, cy, r, color in [
        (540, 300, 250, (255, 0, 110, 50)),
        (540, 1600, 300, (251, 86, 7, 30)),
    ]:
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.ellipse([cx-r, cy-r, cx+r, cy+r], fill=color)
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

    # Style badge
    font_badge = get_font(32)
    badge_text = f"🔥 {style_name.upper()} ROAST"
    bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw = bbox[2] - bbox[0]
    draw.rounded_rectangle([540-bw//2-20, 180, 540+bw//2+20, 240], radius=20, fill=(255, 0, 110))
    draw.text((540, 210), badge_text, fill="white", anchor="mm", font=font_badge)

    # Roast text - wrapped
    font_roast = get_font(42)
    wrapped = []
    for paragraph in roast_text.split("\n"):
        wrapped.extend(textwrap.wrap(paragraph, width=38))
    
    y = 350
    for line in wrapped:
        if y > 1600:
            break
        draw.text((540, y), line, fill="white", anchor="mm", font=font_roast)
        y += 60

    # CTA
    font_cta = get_font(34)
    draw.text((540, 1750), "Get roasted FREE at", fill=(180, 180, 180), anchor="mm", font=get_font(28))
    draw.text((540, 1800), "ai-roast-me.onrender.com", fill=(255, 190, 11), anchor="mm", font=font_cta)

    img.save(filename)
    return filename


def make_cta_slide(filename, bg_color=(20, 5, 40)):
    """Final CTA slide."""
    img = Image.new("RGB", (1080, 1920), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Glows
    for cx, cy, r, color in [
        (540, 700, 350, (255, 0, 110, 60)),
        (540, 1200, 300, (131, 56, 236, 40)),
    ]:
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.ellipse([cx-r, cy-r, cx+r, cy+r], fill=color)
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

    draw.text((540, 600), "🔥", fill="white", anchor="mm", font=get_font(150))
    draw.text((540, 850), "GET ROASTED", fill="white", anchor="mm", font=get_font(72))
    draw.text((540, 950), "BY AI", fill=(255, 0, 110), anchor="mm", font=get_font(72))
    draw.text((540, 1100), "FREE", fill=(0, 255, 136), anchor="mm", font=get_font(80))

    draw.text((540, 1400), "👉 ai-roast-me.onrender.com", fill=(255, 190, 11), anchor="mm", font=get_font(40))
    draw.text((540, 1470), "Link in bio", fill=(180, 180, 180), anchor="mm", font=get_font(32))

    img.save(filename)
    return filename


def main():
    print("=" * 60)
    print("  TIKTOK SLIDESHOW GENERATOR")
    print("  Creating ready-to-post TikTok photo slideshows")
    print("=" * 60)

    for i, s in enumerate(scenarios, 1):
        print(f"\nVideo {i}: {s['hook']}")

        vid_dir = OUTPUT_DIR / f"video_{i:02d}"
        vid_dir.mkdir(exist_ok=True)

        # Slide 1: Hook
        make_hook_slide(vid_dir / "slide_1_hook.png", s["hook"])
        print(f"  ✓ Slide 1: Hook")

        # Slide 2: Photo
        make_photo_slide(vid_dir / "slide_2_photo.png", s["image"])
        print(f"  ✓ Slide 2: Photo")

        # Slide 3: Roast result
        make_roast_slide(vid_dir / "slide_3_roast.png", s["roast"], s["style"].title())
        print(f"  ✓ Slide 3: Roast")

        # Slide 4: CTA
        make_cta_slide(vid_dir / "slide_4_cta.png")
        print(f"  ✓ Slide 4: CTA")

    # Write posting guide
    guide = OUTPUT_DIR / "POSTING_GUIDE.md"
    with open(guide, "w", encoding="utf-8") as f:
        f.write("# TikTok Posting Guide\n\n")
        f.write("## How to post:\n\n")
        f.write("1. Open TikTok app\n")
        f.write("2. Tap + to create\n")
        f.write("3. Tap 'Upload' then select multiple photos\n")
        f.write("4. Select the 4 slides from each video folder (in order)\n")
        f.write("5. TikTok will create a slideshow\n")
        f.write("6. Add the caption and hashtags\n")
        f.write("7. Post!\n\n")
        f.write("## Videos:\n\n")
        for i, s in enumerate(scenarios, 1):
            f.write(f"### Video {i}: {s['hook']}\n")
            f.write(f"**Caption:** {s['caption']}\n")
            f.write(f"**Folder:** tiktok_ready/video_{i:02d}/\n")
            f.write(f"**Slides:** slide_1_hook.png → slide_2_photo.png → slide_3_roast.png → slide_4_cta.png\n\n")

    print(f"\n{'='*60}")
    print(f"  {len(scenarios)} TikTok slideshows ready!")
    print(f"  Location: tiktok_ready/")
    print(f"  Each video folder has 4 slides:")
    print(f"    1. Hook (catchy text)")
    print(f"    2. Photo (the uploaded photo)")
    print(f"    3. Roast (the AI roast result)")
    print(f"    4. CTA (call to action)")
    print(f"")
    print(f"  TO POST ON TIKTOK:")
    print(f"  1. Open TikTok → Create → Upload")
    print(f"  2. Select 4 photos from video_XX folder (in order)")
    print(f"  3. TikTok makes a slideshow automatically")
    print(f"  4. Add caption + hashtags")
    print(f"  5. Post!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
