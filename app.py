# AI Roast Me - Flask Application (Gemini + Cash App version)

import os
import uuid
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

# Google Gemini client
from google import genai
from google.genai import types

gemini_client = None
if GEMINI_API_KEY:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


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
    if "roasts_used" not in session:
        session["roasts_used"] = 0

    return render_template(
        "index.html",
        cashapp_tag=CASHAPP_TAG,
        venmo_tag=VENMO_TAG,
        gemini_configured=bool(GEMINI_API_KEY),
        styles=ROAST_STYLES,
        modes=ROAST_MODES,
        free_roasts=FREE_ROASTS,
        roasts_used=session.get("roasts_used", 0),
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

    roasts_used = session.get("roasts_used", 0)
    if roasts_used >= FREE_ROASTS:
        return jsonify({
            "error": "Free roast limit reached",
            "needs_payment": True,
            "cashapp": CASHAPP_TAG,
            "venmo": VENMO_TAG,
            "message": f"You've used your free roasts! Donate $3 via Cash App ({CASHAPP_TAG}) or Venmo ({VENMO_TAG}) and refresh. Or share to unlock more!",
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

        return jsonify({
            "success": True,
            "roast": roast_text,
            "style": ROAST_STYLES[style]["name"],
            "style_emoji": ROAST_STYLES[style]["emoji"],
            "mode": ROAST_MODES[mode]["name"],
            "mode_emoji": ROAST_MODES[mode]["emoji"],
            "roasts_remaining": FREE_ROASTS - (roasts_used + 1),
        })

    except Exception as e:
        return jsonify({"error": f"Roast failed: {str(e)}"}), 500


@app.route("/share-unlock", methods=["POST"])
def share_unlock():
    """Unlock one more free roast after user shares (viral loop)."""
    session["roasts_used"] = max(0, session.get("roasts_used", 0) - 1)
    session.modified = True
    return jsonify({
        "success": True,
        "roasts_remaining": FREE_ROASTS - session["roasts_used"],
        "message": "Unlocked! Share again for another free roast 🔥",
    })


@app.route("/static/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
