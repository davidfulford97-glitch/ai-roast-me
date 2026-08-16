"""
Automated TikTok Content Generator
Uses agent-browser to automate roasts on the live site and capture screenshots.
Creates TikTok-ready slideshow images.
"""

import os
import json
import subprocess
import time
from pathlib import Path

KIT_DIR = Path(__file__).parent / "tiktok_kit"
OUTPUT_DIR = Path(__file__).parent / "tiktok_ready"
OUTPUT_DIR.mkdir(exist_ok=True)

SITE_URL = "https://ai-roast-me.onrender.com"

def run(cmd, timeout=30):
    """Run a shell command and return output."""
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout + r.stderr
    except subprocess.TimeoutExpired:
        return "TIMEOUT"

def ab(cmd, timeout=30):
    """Run an agent-browser command."""
    return run(f"agent-browser {cmd}", timeout)

def upload_and_roast(image_path, style, video_num, hook):
    """Upload an image, select style, roast, and screenshot the result."""
    print(f"\n--- Video {video_num}: {hook} ---")

    # Navigate to site
    ab(f'open "{SITE_URL}"', 20)
    time.sleep(2)

    # Upload the image by setting the file input
    # We need to use JavaScript to set the file since agent-browser click triggers file dialog
    abs_path = str(Path(image_path).resolve()).replace("\\", "/")

    # Use agent-browser to upload via the file input
    result = ab(f'upload @e1 "{abs_path}"', 15)
    print(f"  Upload: {result.strip()}")
    time.sleep(2)

    # Take screenshot of uploaded preview
    ab(f'screenshot "{OUTPUT_DIR / f"{video_num}_01_uploaded.png"}"', 10)

    # Snapshot to find style cards
    snap = ab("snapshot -i", 10)
    print(f"  Snapshot after upload: {snap[:200]}")

    # Select the style by clicking the right style card
    # Styles: savage, funny, dating, corporate, gamer, grandma
    style_map = {
        "savage": 0, "funny": 1, "dating": 2,
        "corporate": 3, "gamer": 4, "grandma": 5
    }

    # Find style cards in snapshot
    lines = snap.split("\n")
    style_cards = [l for l in lines if "style-card" in l or ("clickable" in l and any(s in l.lower() for s in ["savage","funny","dating","corporate","gamer","grandma"]))]
    print(f"  Found {len(style_cards)} style cards")

    # Try clicking the style by evaluating JS
    style_js = f'document.querySelector("[data-style={style}]").click()'
    ab(f'eval "{style_js}"', 10)
    time.sleep(1)

    # Find and click the ROAST button
    roast_js = 'document.getElementById("roastBtn").click()'
    ab(f'eval "{roast_js}"', 10)
    print("  Clicked ROAST ME button")

    # Wait for roast to generate (can take 5-15 seconds)
    print("  Waiting for AI to roast...")
    time.sleep(15)

    # Take screenshot of result
    result_path = OUTPUT_DIR / f"{video_num}_02_roast_result.png"
    ab(f'screenshot "{result_path}"', 10)
    print(f"  Screenshot saved: {result_path}")

    # Extract the roast text
    roast_text = ab('eval "document.getElementById(\'roastText\').textContent"', 10)
    print(f"  Roast: {roast_text[:100]}...")

    return roast_text.strip()

def main():
    print("=" * 60)
    print("  AUTOMATED TIKTOK CONTENT GENERATOR")
    print("=" * 60)

    # Load the content kit
    kit_file = KIT_DIR / "content_kit.json"
    if not kit_file.exists():
        print("ERROR: Run make_viral_content.py first!")
        return

    with open(kit_file, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    results = []

    for i, s in enumerate(scenarios, 1):
        img = s["image"]
        if not Path(img).exists():
            print(f"Skipping {s['name']} - image not found")
            continue

        roast = upload_and_roast(img, s["style"], i, s["hook"])

        results.append({
            "video_num": i,
            "hook": s["hook"],
            "caption": s["caption"],
            "style": s["style"],
            "image": img,
            "roast": roast,
            "screenshot_1": str(OUTPUT_DIR / f"{i}_01_uploaded.png"),
            "screenshot_2": str(OUTPUT_DIR / f"{i}_02_roast_result.png"),
        })

    # Save results
    with open(OUTPUT_DIR / "tiktok_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print(f"  {len(results)} TikTok slideshows ready in /tiktok_ready/")
    print("  Each folder has:")
    print("    - 01_uploaded.png (showing the photo)")
    print("    - 02_roast_result.png (showing the roast)")
    print("  Upload these as TikTok photo slideshows!")
    print("=" * 60)

    ab("close", 10)

if __name__ == "__main__":
    main()
