import pandas as pd
import random

rows = []
for _ in range(1000):
    row = {
        "Year": random.randint(1900, 2100),
        "Month": random.randint(1, 12),
        "Day": random.randint(1, 28),  # ensures all months are valid
        "Latitude": round(random.uniform(5.0, 15.0), 2),
        "Longitude": round(random.uniform(70.0, 80.0), 2),
        "Zonal Winds": round(random.uniform(0.0, 20.0), 1),
        "Meridional Winds": round(random.uniform(-5.0, 5.0), 1),
        "Humidity": round(random.uniform(60.0, 100.0), 1),
        "Sea Surface Temp": round(random.uniform(25.0, 32.0), 1),
    }

    # Simulated target: Air Temp based on Sea Temp, Winds, and Humidity
    row["Air Temp"] = round(
        0.4 * row["Sea Surface Temp"] +
        0.1 * row["Humidity"] / 100 +
        0.05 * row["Zonal Winds"] -
        0.05 * row["Meridional Winds"] +
        5, 2
    )
    rows.append(row)

# Create and save the dataset
df = pd.DataFrame(rows)
df.to_csv("elnino.csv", index=False)
print("✅ Generated 'elnino.csv' with 1000 entries from 1900–2100.")

