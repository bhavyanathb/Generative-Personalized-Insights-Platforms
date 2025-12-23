from flask import Flask, request, jsonify
import boto3
import joblib
import xgboost as xgb
import pandas as pd
import os

app = Flask(__name__)

# S3 model details
S3_BUCKET = "risk-appetite-classifier"
# MODEL_KEY = "xgboost_risk_appetite_model.pkl"

# Load model from S3
def load_model():
    s3 = boto3.client('s3')
    local_path = 'xgboost_risk_appetite_model.pkl'
    s3.download_file(S3_BUCKET, local_path)
    model = joblib.load(local_path)
    return model

model = load_model()

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        features = pd.DataFrame(data['features'])  # expecting list of dicts or 2D list
        preds = model.predict(xgb.DMatrix(features))
        return jsonify({'predictions': preds.tolist()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
