import random
import requests
import time
import json

url = "http://20.247.46.41/predict"

def generate_payload(valid=True):
    payload = {
        "Year": random.randint(1900, 2100),
        "Month": random.randint(1, 12),
        "Day": random.randint(1, 28),
        "Latitude": round(random.uniform(5.0, 15.0), 2),
        "Longitude": round(random.uniform(70.0, 80.0), 2),
        "Zonal Winds": round(random.uniform(0.0, 20.0), 1),
        "Meridional Winds": round(random.uniform(-5.0, 5.0), 1),
        "Humidity": round(random.uniform(60.0, 100.0), 1),
        "Sea Surface Temp": round(random.uniform(25.0, 32.0), 1),
    }

    if not valid:
        key_to_remove = random.choice(list(payload.keys()))
        del payload[key_to_remove]

    return payload

# 🔁 Send 100 requests with a mix of valid (2xx) and invalid (4xx)
for i in range(100):
    is_valid = random.random() < 0.8  # 80% valid, 20% invalid
    payload = generate_payload(valid=is_valid)

    try:
        response = requests.post(url, json=payload)
        print(f"[{i+1}] Status: {response.status_code}, Payload: {payload}")
    except Exception as e:
        print(f"[{i+1}] Request failed: {e}")

    time.sleep(0.2)  # optional delay to avoid burst

