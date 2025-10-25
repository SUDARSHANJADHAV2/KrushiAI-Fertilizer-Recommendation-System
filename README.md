# Fertilizer Recommendation Microservice (Flask + HTML/JS)

Minimal, production-ready refactor of the fertilizer recommender:
- Backend: Python, Flask, scikit-learn, pandas, numpy (deploy on Render)
- Frontend: HTML/CSS/JavaScript (deploy on Netlify or embed in your existing site)

## Repo layout
```
AI-Fertilizer-Recommendation-System/
├── app.py                      # Flask API
├── requirements.txt            # Backend deps
├── render.yaml                 # Render service config (backend)
├── frontend/
│   ├── index.html              # Simple UI (copy into your Netlify project if needed)
│   ├── styles.css
│   └── main.js
├── Fertilizer_RF.pkl           # Model
├── soil_encoder.pkl            # Encoders
├── crop_encoder.pkl
├── fertilizer_encoder.pkl
└── feature_scaler.pkl          # Optional scaler
```

## Run locally
1) Create venv and install deps
```bash
python -m venv .venv
. .venv/Scripts/Activate.ps1   # PowerShell
pip install -r requirements.txt
```
2) Start API
```bash
python app.py
# API at http://localhost:5000
```
3) Open frontend
- Serve `frontend/` statically (e.g. with VSCode Live Server) or just open `frontend/index.html`.
- By default it calls `http://localhost:5000`.

## Deploy
### Backend (Render)
- Create a new Web Service from this repo.
- Render reads `render.yaml` and runs `gunicorn app:app`.
- After deploy, note your backend URL, e.g. `https://fertilizer-api.onrender.com`.

### Frontend (Netlify)
- If this is part of a larger Netlify site, copy `frontend/` contents into your project and point `API_BASE_URL` in `main.js` to the Render URL.
- Or deploy `frontend/` as a standalone static site on Netlify.

## API
- GET /health -> `{ status: "ok" }`
- GET /api/classes -> `{ soil_types: [...], crop_types: [...] }`
- POST /api/predict (JSON)
```json
{
  "temperature": 26,
  "humidity": 52,
  "moisture": 38,
  "soil_type": "Sandy",
  "crop_type": "Maize",
  "nitrogen": 37,
  "potassium": 0,
  "phosphorous": 0
}
```
Response
```json
{
  "fertilizer": "Urea",
  "confidence": 0.92,
  "details": { "description": "...", "benefits": ["..."], ... }
}
```

## Notes
- Training scripts, Streamlit code, dataset, images and extra libs were removed to keep this focused on your stack and deployment targets.
- Encoders and model files must be present in the repo root.
