# M&A Elite Kits eCommerce

Simple Flask storefront for Morocco team shirts.

## Structure

- `app.py` — Flask application
- `models.py` — order model
- `services.py` — security and WhatsApp helper logic
- `static/` — CSS, JavaScript, images
- `templates/ar/index.html` — Arabic landing page
- `templates/fr/index.html` — French landing page
- `templates/en/index.html` — English landing page
- `requirements.txt` — Python dependencies
- `Dockerfile` — container build file
- `Procfile` — process file for hosting platforms

## Features

- Three static language landing pages: `/ar`, `/fr`, `/en`
- Order submission via `/api/order`
- WhatsApp order confirmation link
- Secure forms with CSRF protection

## Run locally

1. Create/activate virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the app:

```powershell
python app.py
```

4. Open in browser:

- `http://127.0.0.1:5000/ar`
- `http://127.0.0.1:5000/fr`
- `http://127.0.0.1:5000/en`

## Notes

- The root route `/` redirects to `/ar`.
- Translation JSON files were removed and pages are now rendered as separate static templates.
- Orders are logged to `orders.log`.
