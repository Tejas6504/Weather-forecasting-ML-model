import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from math import sqrt
import joblib
import os

MODEL_FILENAME = "model.joblib"
MODEL_VERSION = "v1.0.0"

def train_and_save_model():
    data = pd.read_csv("elnino.csv")
    features = ['Year', 'Month', 'Day', 'Latitude', 'Longitude',
                'Zonal Winds', 'Meridional Winds', 'Humidity', 'Sea Surface Temp']
    target = 'Air Temp'

    X = data[features]
    y = data[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    rmse = sqrt(mean_squared_error(y_test, predictions))
    print(f"✅ Trained model RMSE: {rmse:.2f}")

    joblib.dump(model, MODEL_FILENAME)

def load_model():
    if not os.path.exists(MODEL_FILENAME):
        train_and_save_model()
    return joblib.load(MODEL_FILENAME)

if __name__ == "__main__":
    train_and_save_model()

