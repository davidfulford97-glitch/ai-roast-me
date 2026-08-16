# AI Roast Me 🔥

Upload your photo. Get brutally roasted by AI. $3 per roast.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your API keys (Windows PowerShell):
```powershell
$env:OPENAI_API_KEY = "sk-your-key-here"
$env:STRIPE_SECRET_KEY = "sk_test_your-stripe-secret"
$env:STRIPE_PUBLISHABLE_KEY = "pk_test_your-stripe-publishable"
```

3. Run:
```bash
python app.py
```

4. Open http://localhost:5000

## Demo Mode

Without Stripe keys configured, the app runs in **demo mode** — roasts are free. Add Stripe keys to enable $3 payments.

## Features

- Upload photo (PNG, JPG, WebP)
- 4 roast styles: Savage, Funny, Dating Profile, Corporate
- AI vision analysis via GPT-4o
- Stripe payments ($3 per roast)
- Photo auto-deleted after roasting (privacy)
- TikTok/X share buttons for virality

## Deployment

Deploy free on Render.com or Railway.app:
1. Push to GitHub
2. Connect repo
3. Set env vars
4. Deploy
