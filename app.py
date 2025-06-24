from flask import Flask, request, jsonify
import pandas as pd
import logging
import time
import psutil
from model import load_model
from datadog import initialize, statsd

# Flask App
app = Flask(__name__)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#  Initialize DogStatsD via Unix Socket
initialize(statsd_socket_path="/var/run/datadog/dsd.socket")

#  Track model load time
load_start = time.time()
model = load_model()
load_duration = (time.time() - load_start) * 1000  # ms
statsd.timing("ml.inference.model.load_time", load_duration, tags=["env:prod", "service:weather-forecasting-datadog"])
statsd.gauge("ml.inference.model.version", 1.0, tags=["env:prod", "service:weather-forecasting-datadog", "version:1.0.0"])

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
            statsd.increment("ml.inference.errors", tags=["env:prod", "service:weather-forecasting-datadog", "reason:missing_fields"])
            statsd.increment("ml.inference.status", tags=["env:prod", "service:weather-forecasting-datadog", "code:400"])
            return jsonify({'error': 'Missing one or more required fields'}), 400

        #  Range check (example: Latitude and Longitude)
        if input_json["Latitude"] < -90 or input_json["Latitude"] > 90:
            statsd.increment("ml.inference.input.out_of_range", tags=["env:prod", "field:Latitude"])

        if input_json["Longitude"] < -180 or input_json["Longitude"] > 180:
            statsd.increment("ml.inference.input.out_of_range", tags=["env:prod", "field:Longitude"])

        input_df = pd.DataFrame([input_json])
        prediction = model.predict(input_df)[0]

        #  Duration and latency
        duration = (time.time() - start_time) * 1000  # in ms
        statsd.increment("ml.inference.count", tags=["env:prod", "service:weather-forecasting-datadog"])
        statsd.timing("ml.inference.latency", duration, tags=["env:prod", "service:weather-forecasting-datadog"])
        statsd.gauge("ml.inference.prediction", prediction, tags=["env:prod", "service:weather-forecasting-datadog"])

        #  Memory usage
        mem = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        statsd.gauge("ml.inference.memory.usage", mem, tags=["env:prod", "service:weather-forecasting-datadog"])

        #  Timeout detection (over 500ms)
        if duration > 500:
            statsd.increment("ml.inference.timeout", tags=["env:prod", "service:weather-forecasting-datadog"])

        #  HTTP 2xx status tracking
        statsd.increment("ml.inference.status", tags=["env:prod", "service:weather-forecasting-datadog", "code:200"])

        logger.info(f"Prediction successful: {prediction}")
        return jsonify({'Predicted Air Temp (°C)': round(prediction, 2)})
    
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        statsd.increment("ml.inference.errors", tags=["env:prod", "service:weather-forecasting-datadog", "reason:exception"])
        statsd.increment("ml.inference.status", tags=["env:prod", "service:weather-forecasting-datadog", "code:500"])
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

