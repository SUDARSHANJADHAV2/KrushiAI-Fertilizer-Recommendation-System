# KrushiAI Fertilizer Recommendation System - Deployment Guide

This guide will help you deploy the Fertilizer Recommendation System to work like the Crop Recommendation System.

## Architecture Overview

- **Frontend**: Static HTML/CSS/JS deployed on Netlify
- **Backend**: Python Flask API deployed on Render
- **Connection**: Netlify proxies API requests to Render backend via `netlify.toml`

## Backend Deployment (Render)

### Prerequisites
1. Create an account on [Render](https://render.com)
2. Connect your GitHub repository

### Steps

1. **Push your code to GitHub** (if not already done)
   ```bash
   cd KrushiAI-Fertilizer-Recommendation-System
   git add .
   git commit -m "Add deployment configuration"
   git push origin main
   ```

2. **Create a new Web Service on Render**
   - Go to https://dashboard.render.com/
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository: `KrushiAI-Fertilizer-Recommendation-System`

3. **Configure the service** (Render will auto-detect `render.yaml`, but verify):
   - **Name**: `fertilizer-api` (or your preferred name)
   - **Environment**: Python 3
   - **Root Directory**: (leave empty, files are in root)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --timeout 120 app:app`
   - **Plan**: Free

4. **Add Environment Variables** (optional):
   - `WEB_CONCURRENCY`: `1` (for free tier)

5. **Deploy**
   - Click "Create Web Service"
   - Wait for the build to complete (5-10 minutes)
   - Note your backend URL (e.g., `https://fertilizer-api-kkay.onrender.com`)

6. **Verify Model Files**
   - Ensure these pickle files are committed to your repository:
     - `Fertilizer_RF.pkl` (main model)
     - `soil_encoder.pkl`
     - `crop_encoder.pkl`
     - `fertilizer_encoder.pkl`
     - `feature_scaler.pkl` (optional)

## Frontend Deployment (Netlify)

### Prerequisites
1. Create an account on [Netlify](https://www.netlify.com)

### Steps

1. **Update the API URL in `netlify.toml`**
   - Open `frontend/netlify.toml`
   - Replace the backend URLs with your actual Render backend URL:
   ```toml
   [[redirects]]
   from = "/api/*"
   to = "https://YOUR-BACKEND-URL.onrender.com/api/:splat"
   status = 200
   force = true
   ```

2. **Deploy to Netlify**

   **Option A: Drag & Drop (Easiest)**
   - Go to https://app.netlify.com/drop
   - Drag the entire `frontend` folder
   - Netlify will deploy your site and provide a URL

   **Option B: Git Integration**
   - Go to https://app.netlify.com/
   - Click "Add new site" → "Import an existing project"
   - Connect your GitHub repository
   - Configure:
     - **Base directory**: `frontend` (or leave empty and set Publish directory)
     - **Build command**: (leave empty)
     - **Publish directory**: `frontend` (if base directory is empty)
   - Click "Deploy site"

3. **Configure Site Settings**
   - Go to Site settings → Build & deploy
   - Verify the Publish directory is set correctly
   - Netlify will automatically use `netlify.toml` for redirects

4. **Test Your Deployment**
   - Visit your Netlify URL (e.g., `https://your-site-name.netlify.app`)
   - Fill in the fertilizer recommendation form
   - Click "Get Recommendation"
   - You should see fertilizer suggestions with details!

## Verification Checklist

✅ **Backend (Render)**
- [ ] Service is running and shows "Live"
- [ ] Health check endpoint works: `https://YOUR-BACKEND-URL.onrender.com/health` returns JSON with `"model_loaded": true`
- [ ] Classes endpoint works: `https://YOUR-BACKEND-URL.onrender.com/api/classes` returns soil and crop types

✅ **Frontend (Netlify)**
- [ ] Site is accessible via Netlify URL
- [ ] Page loads with proper styling
- [ ] Dropdowns populate with soil types and crop types
- [ ] Form submission triggers prediction
- [ ] Results are displayed with fertilizer details

✅ **Integration**
- [ ] Frontend can communicate with backend (check browser console for errors)
- [ ] API requests are proxied correctly (no CORS errors)
- [ ] Predictions work end-to-end

## Troubleshooting

### Backend Issues

**Problem**: "Model not loaded" error
- **Solution**: Verify all `.pkl` files are in the repository root
- **Solution**: Check Render logs for file loading errors
- **Solution**: Ensure files are not in `.gitignore`

**Problem**: Build fails on Render
- **Solution**: Check `requirements.txt` has all dependencies
- **Solution**: Verify pickle files are not corrupted
- **Solution**: Try rebuilding: Dashboard → Manual Deploy → Clear build cache & deploy

**Problem**: Backend times out
- **Solution**: Increase timeout in start command (already set to 120s)
- **Solution**: Render free tier may sleep after inactivity - first request wakes it up (may take 30-60 seconds)

**Problem**: "invalid_soil_or_crop" error
- **Solution**: The input soil/crop type doesn't match the encoder's expected values
- **Solution**: Check `/api/classes` endpoint to see valid values

### Frontend Issues

**Problem**: Dropdowns are empty
- **Solution**: Check that `/api/classes` endpoint is working
- **Solution**: Verify backend URL in `netlify.toml`
- **Solution**: Check browser console for errors

**Problem**: Form submission fails
- **Solution**: Check `netlify.toml` has correct backend URL
- **Solution**: Verify backend is running on Render
- **Solution**: Check browser console for CORS errors

**Problem**: "Backend unreachable" error
- **Solution**: Verify the backend URL in `netlify.toml`
- **Solution**: Test backend directly: `curl https://YOUR-BACKEND-URL.onrender.com/health`

**Problem**: Styling is broken
- **Solution**: Ensure all CSS files are in the `frontend` directory
- **Solution**: Check relative paths in HTML

## API Endpoints

### GET /health
Health check endpoint
```json
{
  "status": "ok",
  "model_loaded": true,
  "last_error": null
}
```

### GET /api/classes
Get available soil types and crop types
```json
{
  "soil_types": ["Sandy", "Loamy", "Black", "Red", "Clayey"],
  "crop_types": ["Maize", "Sugarcane", "Cotton", "Tobacco", "Paddy", "Barley", "Wheat", "Millets", "Oil seeds", "Pulses", "Ground Nuts"]
}
```

### POST /api/predict
Get fertilizer recommendation
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

Response:
```json
{
  "fertilizer": "Urea",
  "confidence": 0.92,
  "details": {
    "description": "High nitrogen content fertilizer (46% N)",
    "benefits": ["Promotes leafy growth", "Improves protein content", "Quick nitrogen release"],
    "best_for": ["Cereals", "Leafy vegetables", "Grass crops"],
    "application_rate": "100-200 kg/ha",
    "timing": "Pre-planting and top-dressing"
  }
}
```

## File Structure

```
KrushiAI-Fertilizer-Recommendation-System/
├── app.py                          # Flask API
├── requirements.txt                # Python dependencies
├── render.yaml                     # Render deployment config
├── Fertilizer_RF.pkl              # Trained ML model
├── soil_encoder.pkl               # Soil type encoder
├── crop_encoder.pkl               # Crop type encoder
├── fertilizer_encoder.pkl         # Fertilizer encoder
├── feature_scaler.pkl             # Feature scaler (optional)
├── frontend/
│   ├── index.html                 # Main HTML page
│   ├── main.js                    # Frontend JavaScript
│   ├── styles.css                 # Page styles
│   └── netlify.toml               # Netlify proxy configuration
├── README.md                       # Original README
└── DEPLOYMENT_GUIDE.md            # This file
```

## Custom Domain (Optional)

1. **Netlify**: Site settings → Domain management → Add custom domain
2. **Render**: Settings → Custom Domain → Add domain

## Updates

To update your deployment after making changes:

1. **Backend**: 
   - Push changes to GitHub
   - Render will auto-deploy (if auto-deploy is enabled)
   - Or manually deploy from Render Dashboard

2. **Frontend**:
   - Push changes to GitHub (if using Git integration)
   - Or drag & drop the updated `frontend` folder to Netlify

## Support

- Check the browser console for frontend errors (F12 → Console)
- Check Render logs for backend errors (Dashboard → Service → Logs)
- Test API endpoints using curl or Postman
- Verify model files are present and not corrupted

## Testing Locally

Before deploying, test locally:

1. **Backend**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   python app.py
   # API runs on http://localhost:5000
   ```

2. **Frontend**:
   - Open `frontend/index.html` with Live Server (VSCode extension)
   - Or open directly in browser
   - The JavaScript will auto-detect localhost and use `http://127.0.0.1:5001`

---

**Made by Team KrushiAI** 🌾
