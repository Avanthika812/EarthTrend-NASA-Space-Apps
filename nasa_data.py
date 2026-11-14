import requests
import pandas as pd

# Kerala location - Kollam
latitude = 8.8932
longitude = 76.6141

# NASA POWER API
url = "https://power.larc.nasa.gov/api/temporal/monthly/point"

params = {
    "parameters": "T2M,PRECTOTCORR",
    "community": "AG",
    "longitude": longitude,
    "latitude": latitude,
    "start": "2001",
    "end": "2025",
    "format": "JSON"
}

print("Connecting to NASA POWER API...")

response = requests.get(url, params=params)

if response.status_code == 200:

    data = response.json()

    temperature = data["properties"]["parameter"]["T2M"]
    rainfall = data["properties"]["parameter"]["PRECTOTCORR"]

    df = pd.DataFrame({
        "Date": list(temperature.keys()),
        "Temperature_C": list(temperature.values()),
        "Rainfall_mm_day": list(rainfall.values())
    })

    df.to_csv("kollam_nasa_data.csv", index=False)

    print("\nNASA data downloaded successfully!")
    print(df.head())
    print("\nDataset shape:", df.shape)

else:
    print("Error:", response.status_code)