from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
import os

app = Flask(__name__)
CORS(app)  # allow all origins; tighten in production if needed

# Load model components at startup
MODEL_PATH = os.getenv("MODEL_PATH", ".")

model = None
soil_encoder = None
crop_encoder = None
fertilizer_encoder = None
scaler = None


def load_pickle(name):
    path = os.path.join(MODEL_PATH, name)
    with open(path, "rb") as f:
        return pickle.load(f)


def load_components():
    global model, soil_encoder, crop_encoder, fertilizer_encoder, scaler
    model = load_pickle("Fertilizer_RF.pkl")
    soil_encoder = load_pickle("soil_encoder.pkl")
    crop_encoder = load_pickle("crop_encoder.pkl")
    fertilizer_encoder = load_pickle("fertilizer_encoder.pkl")
    # scaler is optional
    try:
        scaler_path = os.path.join(MODEL_PATH, "feature_scaler.pkl")
        if os.path.exists(scaler_path):
            scaler = load_pickle("feature_scaler.pkl")
    except Exception:
        scaler = None


load_components()


FERTILIZER_INFO = {
    "Urea": {
        "description": "High nitrogen content fertilizer (46% N)",
        "benefits": ["Promotes leafy growth", "Improves protein content", "Quick nitrogen release"],
        "best_for": ["Cereals", "Leafy vegetables", "Grass crops"],
        "application_rate": "100-200 kg/ha",
        "timing": "Pre-planting and top-dressing",
    },
    "DAP": {
        "description": "Di-ammonium Phosphate (18% N, 46% P₂O₅)",
        "benefits": ["Root development", "Early plant growth", "Flower and fruit formation"],
        "best_for": ["All crops", "Especially during planting"],
        "application_rate": "50-100 kg/ha",
        "timing": "At planting time",
    },
    "14-35-14": {
        "description": "NPK complex fertilizer (14% N, 35% P₂O₅, 14% K₂O)",
        "benefits": ["Balanced nutrition", "Root development", "Overall plant health"],
        "best_for": ["Fruit crops", "Vegetables", "Cash crops"],
        "application_rate": "150-250 kg/ha",
        "timing": "At planting and flowering",
    },
    "28-28": {
        "description": "NPK fertilizer (28% N, 28% P₂O₅)",
        "benefits": ["Balanced N-P nutrition", "Strong root system", "Healthy growth"],
        "best_for": ["Field crops", "Vegetables"],
        "application_rate": "100-150 kg/ha",
        "timing": "At planting and vegetative stage",
    },
    "17-17-17": {
        "description": "Balanced NPK fertilizer (17% each of N, P₂O₅, K₂O)",
        "benefits": ["Complete balanced nutrition", "All-round growth", "Stress tolerance"],
        "best_for": ["All crops", "General purpose"],
        "application_rate": "150-200 kg/ha",
        "timing": "Throughout growing season",
    },
    "20-20": {
        "description": "NPK fertilizer (20% N, 20% P₂O₅)",
        "benefits": ["Good N-P balance", "Vigorous growth", "High yield potential"],
        "best_for": ["Cereals", "Pulses", "Oilseeds"],
        "application_rate": "125-175 kg/ha",
        "timing": "At sowing and top-dressing",
    },
    "10-26-26": {
        "description": "NPK fertilizer (10% N, 26% P₂O₅, 26% K₂O)",
        "benefits": ["High P-K content", "Root development", "Disease resistance"],
        "best_for": ["Fruit crops", "Vegetables", "High K requirement crops"],
        "application_rate": "100-200 kg/ha",
        "timing": "At planting and fruit development",
    },
}


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/")
def root():
    return jsonify({"service": "fertilizer-recommendation", "status": "ready"})


@app.get("/api/classes")
def get_classes():
    if soil_encoder is None or crop_encoder is None:
        return jsonify({"error": "encoders_not_loaded"}), 500
    return jsonify({
        "soil_types": list(getattr(soil_encoder, "classes_", [])),
        "crop_types": list(getattr(crop_encoder, "classes_", [])),
    })


def validate(payload):
    required = [
        "temperature",
        "humidity",
        "moisture",
        "soil_type",
        "crop_type",
        "nitrogen",
        "potassium",
        "phosphorous",
    ]
    missing = [k for k in required if k not in payload]
    if missing:
        return [f"Missing field(s): {', '.join(missing)}"]
    errs = []
    t = payload["temperature"]
    h = payload["humidity"]
    m = payload["moisture"]
    n = payload["nitrogen"]
    k = payload["potassium"]
    p = payload["phosphorous"]
    if not (0 <= t <= 60):
        errs.append("Temperature must be between 0 and 60 C")
    if not (0 <= h <= 100):
        errs.append("Humidity must be between 0 and 100 %")
    if not (0 <= m <= 100):
        errs.append("Moisture must be between 0 and 100 %")
    if not (0 <= n <= 300):
        errs.append("Nitrogen must be between 0 and 300 mg/kg")
    if not (0 <= k <= 300):
        errs.append("Potassium must be between 0 and 300 mg/kg")
    if not (0 <= p <= 300):
        errs.append("Phosphorous must be between 0 and 300 mg/kg")
    return errs


@app.post("/api/predict")
def predict():
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "invalid_json"}), 400

    errors = validate(data)
    if errors:
        return jsonify({"errors": errors}), 400

    try:
        soil_encoded = soil_encoder.transform([data["soil_type"]])[0]
        crop_encoded = crop_encoder.transform([data["crop_type"]])[0]
    except Exception:
        return jsonify({"error": "invalid_soil_or_crop"}), 400

    features = np.array([
        [
            float(data["temperature"]),
            float(data["humidity"]),
            float(data["moisture"]),
            soil_encoded,
            crop_encoded,
            float(data["nitrogen"]),
            float(data["potassium"]),
            float(data["phosphorous"]),
        ]
    ])

    try:
        if scaler is not None:
            features = scaler.transform(features)
        pred = model.predict(features)[0]
        proba = getattr(model, "predict_proba", lambda x: None)(features)
        confidence = float(np.max(proba)) if proba is not None else None
        fert_name = fertilizer_encoder.inverse_transform([pred])[0]
        details = FERTILIZER_INFO.get(
            fert_name,
            {
                "description": "Specialized fertilizer blend",
                "benefits": ["Optimized nutrition", "Improved yield", "Better quality"],
                "best_for": ["As recommended for your specific crop"],
                "application_rate": "As per soil test recommendations",
                "timing": "As per crop growth stage",
            },
        )
        return jsonify(
            {
                "fertilizer": fert_name,
                "confidence": confidence,
                "details": details,
            }
        )
    except Exception as e:
        return jsonify({"error": "prediction_failed", "message": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
