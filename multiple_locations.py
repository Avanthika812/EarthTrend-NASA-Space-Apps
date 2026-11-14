import requests
import pandas as pd

locations = {
    "Kollam": (8.8932, 76.6141),
    "Trivandrum": (8.5241, 76.9366),
    "Idukki": (9.8494, 76.9680)
}

all_data = []

for city, coordinates in locations.items():

    latitude, longitude = coordinates

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

    print(f"Downloading data for {city}...")

    response = requests.get(url, params=params)

    if response.status_code == 200:

        data = response.json()

        temperature = data["properties"]["parameter"]["T2M"]
        rainfall = data["properties"]["parameter"]["PRECTOTCORR"]

        df = pd.DataFrame({
            "Date": list(temperature.keys()),
            "Temperature": list(temperature.values()),
            "Rainfall": list(rainfall.values()),
            "Location": city
        })

        all_data.append(df)

    else:
        print(f"Error downloading {city}")

final_df = pd.concat(all_data, ignore_index=True)

final_df.to_csv("kerala_climate_data.csv", index=False)

print("\nAll locations downloaded successfully!")
print(final_df.head())
print("\nDataset shape:", final_df.shape)