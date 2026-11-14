import pandas as pd
import numpy as np
import pymannkendall as mk
from scipy.stats import linregress
import calendar

# Load cleaned NASA dataset
df = pd.read_csv("cleaned_kerala_climate.csv")

df["Date"] = pd.to_datetime(df["Date"])

# Extract year and month
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month

# Convert rainfall rate (mm/day) into monthly rainfall (mm)
df["Monthly_Rainfall"] = df.apply(
    lambda row: row["Rainfall"] *
    calendar.monthrange(row["Year"], row["Month"])[1],
    axis=1
)

# Calculate annual climate statistics
annual_data = df.groupby(
    ["Location", "Year"]
).agg({
    "Temperature": "mean",
    "Monthly_Rainfall": "sum"
}).reset_index()

print("\nANNUAL CLIMATE DATA")
print(annual_data.head(10))

# Trend analysis
print("\nCLIMATE TREND ANALYSIS")

for location in annual_data["Location"].unique():

    location_data = annual_data[
        annual_data["Location"] == location
    ]

    years = location_data["Year"].values
    temperature = location_data["Temperature"].values
    rainfall = location_data["Monthly_Rainfall"].values

    # Temperature trend
    temp_result = mk.original_test(temperature)

    temp_regression = linregress(years, temperature)

    # Rainfall trend
    rain_result = mk.original_test(rainfall)

    rain_regression = linregress(years, rainfall)

    print("\nLocation:", location)

    print("\nTemperature:")
    print("Trend:", temp_result.trend)
    print("Change per year:",
          round(temp_regression.slope, 4), "°C")
    print("P-value:", round(temp_result.p, 4))

    print("\nRainfall:")
    print("Trend:", rain_result.trend)
    print("Change per year:",
          round(rain_regression.slope, 2), "mm")
    print("P-value:", round(rain_result.p, 4))

# Save annual results
annual_data.to_csv(
    "annual_climate_trends.csv",
    index=False
)

print("\nTrend analysis completed successfully!")