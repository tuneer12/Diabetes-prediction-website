"""
Flask API to serve the Diabetes prediction model
File: flask_backend_app.py

Usage:
  - Place `reni_model.pkl` and `reni_scaler.pkl` in the same folder as this file.
  - Run: python flask_backend_app.py
  - POST JSON to /predict with either:
      {"features": [age, sex, bmi, avg_bp, cholesterol, ldl, hdl, totchol_hdl_ratio, triglycerides, hba1c]}
    or
      {"Age": ..., "Sex": ..., "BMI": ..., "Average_Blood_Pressure": ..., "Cholesterol": ..., "LDL": ..., "HDL": ..., "TotalCholesterol_to_HDL": ..., "Triglycerides": ..., "HbA1c": ...}

Response:
  {"prediction": <float>, "units": "(same units as model training target)", "input": {...}}

Notes:
  - This code uses CORS to allow cross-origin requests from a frontend hosted elsewhere (e.g. Firebase Hosting).
  - The API expects numeric values. If your model requires specific normalization, the included scaler (reni_scaler.pkl) will be applied before prediction.

"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
import os

app = Flask(__name__)
CORS(app)

# Filenames (assumed to be in same directory)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "reni_model.pkl")
SCALER_PATH = os.path.join(os.path.dirname(__file__), "reni_scaler.pkl")

# Expected feature names & order (must match what model was trained on).
FEATURE_ORDER = [
    "Age",
    "Sex",
    "BMI",
    "Average_Blood_Pressure",
    "Cholesterol",
    "LDL",
    "HDL",
    "TotalCholesterol_to_HDL",
    "Triglycerides",
    "HbA1c"
]

# Load model and scaler
try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
except Exception as e:
    model = None
    print(f"WARNING: Could not load model from {MODEL_PATH}: {e}")

try:
    with open(SCALER_PATH, "rb") as f:
        scaler = pickle.load(f)
except Exception as e:
    scaler = None
    print(f"WARNING: Could not load scaler from {SCALER_PATH}: {e}")


def _parse_features_from_json(data):
    """Return a 2D numpy array shaped (1, n_features) or raise ValueError."""
    # If user provides an explicit list under key 'features'
    if isinstance(data, dict) and "features" in data:
        feats = data["features"]
        if not isinstance(feats, (list, tuple)):
            raise ValueError("'features' must be a list or tuple of numeric values.")
        if len(feats) != len(FEATURE_ORDER):
            raise ValueError(f"Expected {len(FEATURE_ORDER)} features but got {len(feats)}.")
        arr = np.array(feats, dtype=float).reshape(1, -1)
        return arr

    # Otherwise try to map by feature names
    if isinstance(data, dict):
        try:
            values = [data[name] for name in FEATURE_ORDER]
        except KeyError as e:
            missing = str(e).strip("\"")
            raise ValueError(f"Missing feature: {missing}. Expected keys: {FEATURE_ORDER}")
        arr = np.array(values, dtype=float).reshape(1, -1)
        return arr

    raise ValueError("JSON payload must be an object with either a 'features' list or named feature keys.")


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "message": "Diabetes prediction API running."})


@app.route("/predict", methods=["POST"])
def predict():
    if model is None:
        return jsonify({"error": "Model not loaded on server."}), 500

    try:
        data = request.get_json(force=True)
        X = _parse_features_from_json(data)

        # Apply scaler if available
        if scaler is not None:
            try:
                X_scaled = scaler.transform(X)
            except Exception as e:
                # If scaler fails, fall back to raw features with a warning
                print(f"Scaler transform failed: {e}")
                X_scaled = X
        else:
            X_scaled = X

        # Predict
        pred = model.predict(X_scaled)

        # If model returns array-like, extract scalar
        if hasattr(pred, "tolist"):
            out = pred.tolist()
        else:
            out = float(pred)

        response = {
            "prediction": out,
            "units": "(same units as model target)",
            "input_features": dict(zip(FEATURE_ORDER, X.flatten().tolist()))
        }
        return jsonify(response)

    except ValueError as ve:
        return jsonify({"error": "bad request", "message": str(ve)}), 400
    except Exception as e:
        print(f"Internal error during /predict: {e}")
        return jsonify({"error": "internal_server_error", "message": str(e)}), 500


if __name__ == "__main__":
    # Run on localhost:5000. On Windows this is fine. For production, consider a proper WSGI server.
    app.run(host="0.0.0.0", port=5000, debug=True)
