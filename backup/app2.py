# app.py
from flask import Flask, request, jsonify
import pandas as pd
from model import load_model
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the trained model
model = load_model()

@app.route('/')
def home():
    logger.info("Health check hit.")
    return "Weather Forecasting ML Model is running!"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        input_json = request.get_json()
        required_fields = ['Year', 'Month', 'Day', 'Latitude', 'Longitude',
                           'Zonal Winds', 'Meridional Winds', 'Humidity', 'Sea Surface Temp']
        
        if not all(field in input_json for field in required_fields):
            logger.warning("Missing fields in input.")
            return jsonify({'error': 'Missing one or more required fields'}), 400

        input_df = pd.DataFrame([input_json])
        prediction = model.predict(input_df)[0]

        logger.info(f"Prediction successful: {prediction}")
        return jsonify({'Predicted Air Temp (°C)': round(prediction, 2)})
    
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

