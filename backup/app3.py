from flask import Flask, request, jsonify
import pandas as pd
import logging
import time
from model import load_model
from datadog import initialize, statsd

# Flask App
app = Flask(__name__)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the model
model = load_model()

# ✅ Initialize DogStatsD via Unix Socket
initialize(statsd_socket_path="/var/run/datadog/dsd.socket")

@app.route('/')
def home():
    logger.info("Health check hit.")
    return "Weather Forecasting ML Model is running!"

@app.route('/predict', methods=['POST'])
def predict():
    start_time = time.time()
    try:
        input_json = request.get_json()
        required_fields = ['Year', 'Month', 'Day', 'Latitude', 'Longitude',
                           'Zonal Winds', 'Meridional Winds', 'Humidity', 'Sea Surface Temp']
        
        if not all(field in input_json for field in required_fields):
            logger.warning("Missing fields in input.")
            statsd.increment("ml.inference.errors", tags=["reason:missing_fields"])
            return jsonify({'error': 'Missing one or more required fields'}), 400

        input_df = pd.DataFrame([input_json])
        prediction = model.predict(input_df)[0]
        duration = (time.time() - start_time) * 1000  # in ms

        # ✅ Send custom metrics
        statsd.increment("ml.inference.count", tags=["env:prod", "service:weather-forecasting-datadog"])
        statsd.timing("ml.inference.latency", duration, tags=["env:prod", "service:weather-forecasting-datadog"])
        statsd.gauge("ml.inference.prediction", prediction, tags=["env:prod", "service:weather-forecasting-datadog"])

        logger.info(f"Prediction successful: {prediction}")
        return jsonify({'Predicted Air Temp (°C)': round(prediction, 2)})
    
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        statsd.increment("ml.inference.errors", tags=["env:prod", "service:weather-forecasting-datadog", "reason:exception"])
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

