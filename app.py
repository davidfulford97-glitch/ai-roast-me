# AI Roast Me - Flask Application (Gemini + Cash App + Referral version)

import os
import uuid
import json
import time
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory, session
from flask_cors import CORS
from config import (
    GEMINI_API_KEY, VISION_MODEL, CASHAPP_TAG, VENMO_TAG,
    SECRET_KEY, UPLOAD_FOLDER, ALLOWED_EXTENSIONS, ROAST_STYLES,
    ROAST_MODES, MODE_PROMPTS, FREE_ROASTS,
)

app = Flask(__name__)
app.secret_key = SECRET_KEY
CORS(app)

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Referral storage (simple JSON file - works for free tier)
REFERRALS_FILE = Path(__file__).parent / "referrals.json"
if not REFERRALS_FILE.exists():
    REFERRALS_FILE.write_text("{}")

def load_referrals():
    try:
        return json.loads(REFERRALS_FILE.read_text())
    except:
        return {}

def save_referrals(data):
    REFERRALS_FILE.write_text(json.dumps(data))

# Google Gemini client
from google import genai
from google.genai import types

gemini_client = None
if GEMINI_API_KEY:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_user_id():
    """Get or create a unique user ID for this session."""
    if "user_id" not in session:
        session["user_id"] = uuid.uuid4().hex[:12]
    return session["user_id"]


def get_referral_link(user_id):
    """Generate a referral link for a user."""
    base_url = request.host_url.rstrip("/")
    return f"{base_url}?ref={user_id}"


def get_total_free_roasts(user_id):
    """Calculate total free roasts: base + referral bonuses."""
    referrals = load_referrals()
    user_data = referrals.get(user_id, {"referrals": 0, "bonus_roasts": 0})
    bonus = user_data.get("bonus_roasts", 0)
    return FREE_ROASTS + bonus


def generate_roast(image_paths, style="savage", mode="solo"):
    """Send image(s) to Gemini and get a roast back."""
    if not gemini_client:
        raise RuntimeError("GEMINI_API_KEY not set. Get a free key at aistudio.google.com/apikey")

    style_prompt = ROAST_STYLES.get(style, ROAST_STYLES["savage"])["prompt"]
    mode_template = MODE_PROMPTS.get(mode, MODE_PROMPTS["solo"])
    final_prompt = mode_template.format(style_prompt=style_prompt)

    parts = []
    for img_path in image_paths:
        image_bytes = Path(img_path).read_bytes()
        ext = Path(img_path).suffix.lower()
        mime_type = {
            ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".png": "image/png", ".webp": "image/webp",
        }.get(ext, "image/jpeg")
        parts.append(types.Part(inline_data=types.Blob(mime_type=mime_type, data=image_bytes)))

    parts.append(types.Part(text=final_prompt))

    response = gemini_client.models.generate_content(
        model=VISION_MODEL,
        contents=[types.Content(parts=parts)],
        config=types.GenerateContentConfig(max_output_tokens=500, temperature=0.95),
    )
    return response.text


@app.route("/")
def index():
    user_id = get_user_id()

    if "roasts_used" not in session:
        session["roasts_used"] = 0

    # Check for referral code in URL
    ref_code = request.args.get("ref")
    if ref_code and ref_code != user_id:
        # This visitor was referred by someone
        referrals = load_referrals()
        if ref_code in referrals:
            # Mark this user as referred (only count once)
            if session.get("referred_by") != ref_code:
                session["referred_by"] = ref_code
                # Give the referrer a bonus roast
                referrals[ref_code]["referrals"] = referrals[ref_code].get("referrals", 0) + 1
                referrals[ref_code]["bonus_roasts"] = referrals[ref_code].get("bonus_roasts", 0) + 2
                save_referrals(referrals)
        elif ref_code not in referrals:
            # Referrer doesn't exist yet, but track it
            pass

    # Make sure this user exists in referrals
    referrals = load_referrals()
    if user_id not in referrals:
        referrals[user_id] = {"referrals": 0, "bonus_roasts": 0}
        save_referrals(referrals)

    total_free = get_total_free_roasts(user_id)
    referral_link = get_referral_link(user_id)
    user_referrals = referrals.get(user_id, {}).get("referrals", 0)

    return render_template(
        "index.html",
        cashapp_tag=CASHAPP_TAG,
        venmo_tag=VENMO_TAG,
        gemini_configured=bool(GEMINI_API_KEY),
        styles=ROAST_STYLES,
        modes=ROAST_MODES,
        free_roasts=total_free,
        roasts_used=session.get("roasts_used", 0),
        referral_link=referral_link,
        user_referrals=user_referrals,
        user_id=user_id,
    )


@app.route("/upload", methods=["POST"])
def upload():
    if "photo" not in request.files:
        return jsonify({"error": "No photo uploaded"}), 400

    file = request.files["photo"]
    if file.filename == "":
        return jsonify({"error": "No photo selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Use PNG, JPG, or WebP."}), 400

    ext = file.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = UPLOAD_FOLDER / filename
    file.save(filepath)

    session["uploaded_photo"] = filename

    return jsonify({
        "success": True,
        "photo_url": f"/static/uploads/{filename}",
        "filename": filename,
    })


@app.route("/upload-second", methods=["POST"])
def upload_second():
    """Upload second photo for roast battle mode."""
    if "photo" not in request.files:
        return jsonify({"error": "No photo uploaded"}), 400

    file = request.files["photo"]
    if file.filename == "":
        return jsonify({"error": "No photo selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Use PNG, JPG, or WebP."}), 400

    ext = file.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = UPLOAD_FOLDER / filename
    file.save(filepath)

    session["uploaded_photo2"] = filename

    return jsonify({
        "success": True,
        "photo_url": f"/static/uploads/{filename}",
        "filename": filename,
    })


@app.route("/roast", methods=["POST"])
def roast():
    data = request.json or {}
    filename = data.get("filename") or session.get("uploaded_photo")
    filename2 = data.get("filename2") or session.get("uploaded_photo2")
    mode = data.get("mode", "solo")
    style = data.get("style", "savage")

    if not filename:
        return jsonify({"error": "No photo uploaded. Upload a photo first."}), 400

    filepath = UPLOAD_FOLDER / filename
    if not filepath.exists():
        return jsonify({"error": "Photo not found. Please upload again."}), 400

    # For battle mode, need second photo
    image_paths = [str(filepath)]
    if mode == "battle":
        if not filename2:
            return jsonify({"error": "Upload a second photo for Roast Battle!"}), 400
        filepath2 = UPLOAD_FOLDER / filename2
        if not filepath2.exists():
            return jsonify({"error": "Second photo not found. Upload again."}), 400
        image_paths.append(str(filepath2))

    if style not in ROAST_STYLES:
        style = "savage"
    if mode not in ROAST_MODES:
        mode = "solo"

    user_id = get_user_id()
    total_free = get_total_free_roasts(user_id)
    roasts_used = session.get("roasts_used", 0)

    if roasts_used >= total_free:
        return jsonify({
            "error": "Free roast limit reached",
            "needs_payment": True,
            "cashapp": CASHAPP_TAG,
            "venmo": VENMO_TAG,
            "referral_link": get_referral_link(user_id),
            "user_referrals": load_referrals().get(user_id, {}).get("referrals", 0),
            "message": f"You've used all your free roasts! Share your link with friends to get 2 FREE roasts per person who visits. Or donate $3 via Cash App ({CASHAPP_TAG}).",
        }), 402

    try:
        roast_text = generate_roast(image_paths, style, mode)
        session["roasts_used"] = roasts_used + 1
        session.modified = True

        # Privacy: delete photos after roasting
        for p in image_paths:
            try:
                Path(p).unlink()
            except Exception:
                pass

        remaining = total_free - (roasts_used + 1)
        return jsonify({
            "success": True,
            "roast": roast_text,
            "style": ROAST_STYLES[style]["name"],
            "style_emoji": ROAST_STYLES[style]["emoji"],
            "mode": ROAST_MODES[mode]["name"],
            "mode_emoji": ROAST_MODES[mode]["emoji"],
            "roasts_remaining": remaining,
            "total_free": total_free,
        })

    except Exception as e:
        return jsonify({"error": f"Roast failed: {str(e)}"}), 500


@app.route("/share-unlock", methods=["POST"])
def share_unlock():
    """Unlock one more free roast after user shares (viral loop)."""
    session["roasts_used"] = max(0, session.get("roasts_used", 0) - 1)
    session.modified = True
    user_id = get_user_id()
    total_free = get_total_free_roasts(user_id)
    return jsonify({
        "success": True,
        "roasts_remaining": total_free - session["roasts_used"],
        "message": "Unlocked! Share your referral link for 2 more free roasts per friend 🔥",
    })


@app.route("/referral-stats")
def referral_stats():
    """Get referral stats for the current user."""
    user_id = get_user_id()
    referrals = load_referrals()
    user_data = referrals.get(user_id, {"referrals": 0, "bonus_roasts": 0})
    return jsonify({
        "user_id": user_id,
        "referral_link": get_referral_link(user_id),
        "total_referrals": user_data.get("referrals", 0),
        "bonus_roasts": user_data.get("bonus_roasts", 0),
        "total_free_roasts": get_total_free_roasts(user_id),
        "roasts_used": session.get("roasts_used", 0),
        "roasts_remaining": get_total_free_roasts(user_id) - session.get("roasts_used", 0),
    })


@app.route("/static/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
