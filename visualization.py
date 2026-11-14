import matplotlib

# Use a non-GUI backend
matplotlib.use("Agg")

import pandas as pd
import matplotlib.pyplot as plt

# Load annual climate data
df = pd.read_csv("annual_climate_trends.csv")

# -----------------------------
# GRAPH 1: Temperature Trends
# -----------------------------

plt.figure(figsize=(12, 6))

for location in df["Location"].unique():

    data = df[df["Location"] == location]

    plt.plot(
        data["Year"],
        data["Temperature"],
        marker="o",
        label=location
    )

plt.title("Annual Temperature Trends in Kerala")
plt.xlabel("Year")
plt.ylabel("Average Temperature (°C)")
plt.legend()
plt.grid(True)

plt.savefig("temperature_trends.png", dpi=300)
plt.close()


# -----------------------------
# GRAPH 2: Rainfall Trends
# -----------------------------

plt.figure(figsize=(12, 6))

for location in df["Location"].unique():

    data = df[df["Location"] == location]

    plt.plot(
        data["Year"],
        data["Monthly_Rainfall"],
        marker="o",
        label=location
    )

plt.title("Annual Rainfall Trends in Kerala")
plt.xlabel("Year")
plt.ylabel("Annual Rainfall (mm)")
plt.legend()
plt.grid(True)

plt.savefig("rainfall_trends.png", dpi=300)
plt.close()


# -----------------------------
# GRAPH 3: Average Temperature
# -----------------------------

average_temp = df.groupby("Location")[
    "Temperature"
].mean()

plt.figure(figsize=(8, 5))

average_temp.plot(kind="bar")

plt.title("Average Temperature Comparison")
plt.xlabel("Location")
plt.ylabel("Temperature (°C)")
plt.xticks(rotation=0)
plt.grid(axis="y")

plt.savefig("temperature_comparison.png", dpi=300)
plt.close()

print("All graphs generated successfully!")