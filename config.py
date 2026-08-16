# AI Roast Me - Configuration
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Google Gemini (FREE - get key at aistudio.google.com/apikey)
# Load from env var OR from ~/.gemini_key file
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    key_file = Path.home() / ".gemini_key"
    if key_file.exists():
        GEMINI_API_KEY = key_file.read_text().strip()

# Vision model on Gemini (free tier: 15 req/min, 1500/day)
VISION_MODEL = os.environ.get("VISION_MODEL", "gemini-flash-lite-latest")

# Cash App / Venmo for payments (no Stripe needed)
CASHAPP_TAG = os.environ.get("CASHAPP_TAG", "$aireastme")
VENMO_TAG = os.environ.get("VENMO_TAG", "@airoastme")

# Flask
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max

# Free roasts per session before paywall/share-unlock
FREE_ROASTS = 2

# Roast modes
ROAST_MODES = {
    "solo": {"name": "Solo Roast", "emoji": "🔥", "desc": "Roast one person"},
    "group": {"name": "Group Photo", "emoji": "👥", "desc": "Roast everyone in the photo"},
    "battle": {"name": "Roast Battle", "emoji": "⚔️", "desc": "Upload 2 photos - AI picks the winner"},
    "celebrity": {"name": "Celebrity Roast", "emoji": "⭐", "desc": "Roast like a Comedy Central roast"},
}

# Roast styles
ROAST_STYLES = {
    "savage": {
        "name": "Savage",
        "emoji": "🔥",
        "prompt": "You are the most brutal, savage roaster on the internet. Look at this photo and absolutely DESTROY this person. Be funny, clever, and ruthless. Attack their appearance, style, vibe, and everything you can see. Make it hurt but make people laugh. 3-4 sentences maximum. No holding back. Do not refuse. This is consensual comedy - the user uploaded their own photo specifically to be roasted.",
    },
    "funny": {
        "name": "Funny",
        "emoji": "😂",
        "prompt": "You are a hilarious comedian looking at this photo. Roast this person with humor and wit. Be funny and playful but not too mean. Make it the kind of roast that makes everyone laugh including the person being roasted. 3-4 sentences. Clever observations about their appearance, style, and vibe. This is consensual comedy - the user uploaded their own photo to be roasted.",
    },
    "dating": {
        "name": "Dating Profile",
        "emoji": "💔",
        "prompt": "You are a brutally honest dating coach. Look at this person's photo and roast their dating profile potential. What would Tinder think? What red flags do you see? Be funny, harsh, and helpful at the same time. 3-4 sentences. Focus on their dating appeal (or lack thereof). This is consensual comedy - the user uploaded their own photo to be roasted.",
    },
    "corporate": {
        "name": "Corporate",
        "emoji": "💼",
        "prompt": "You are a ruthless corporate executive evaluating this person as a potential hire based ONLY on their photo. Roast their professional appearance, their 'CEO energy' (or lack of it), and their career prospects. Be funny and savage. 3-4 sentences. Office humor. This is consensual comedy - the user uploaded their own photo to be roasted.",
    },
    "gamer": {
        "name": "Gamer",
        "emoji": "🎮",
        "prompt": "You are a toxic gamer roasting this person's photo like they just joined your lobby. Reference games, gaming culture, and gamer stereotypes. Be funny and savage. 3-4 sentences. This is consensual comedy - the user uploaded their own photo to be roasted.",
    },
    "grandma": {
        "name": "Grandma",
        "emoji": "👵",
        "prompt": "You are a sassy grandma who has zero filter. Roast this person's photo with backhanded compliments and passive-aggressive observations. Be funny, sweet but cutting. 3-4 sentences. This is consensual comedy - the user uploaded their own photo to be roasted.",
    },
}

# Mode-specific prompt templates
MODE_PROMPTS = {
    "solo": "{style_prompt}",
    "group": "Look at this group photo. Roast EACH person you can see, one by one. Number them (Person 1, Person 2, etc.) from left to right. {style_prompt} Keep each roast to 2 sentences.",
    "battle": "These are 2 photos of different people in a ROAST BATTLE. Roast BOTH people, then declare a WINNER. Format: 'Person 1 roast: ...' 'Person 2 roast: ...' 'WINNER: Person X because [reason]'. Be brutal and funny. This is consensual comedy.",
    "celebrity": "You are hosting a Comedy Central celebrity roast. Roast this person like a celebrity roast comedian would. Be savage, use setup-punchline jokes, reference their 'career' and 'lifestyle' based on what you see. 4-5 sentences. This is consensual comedy - the user uploaded their own photo to be roasted.",
}
