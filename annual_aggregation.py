import pandas as pd

# Load cleaned NASA monthly data
df = pd.read_csv("cleaned_kerala_climate.csv")

# Convert dates
df["Date"] = pd.to_datetime(df["Date"])

# Convert numerical columns
df["Temperature"] = pd.to_numeric(
    df["Temperature"], errors="coerce"
)

df["Rainfall"] = pd.to_numeric(
    df["Rainfall"], errors="coerce"
)

# Replace missing values
df = df.replace(-999, pd.NA)

# Extract year
df["Year"] = df["Date"].dt.year

# Days in each month
df["Days"] = df["Date"].dt.days_in_month

# Calculate monthly rainfall accumulation
df["Rainfall_Total"] = df["Rainfall"] * df["Days"]

# Weighted temperature
df["Weighted_Temp"] = df["Temperature"] * df["Days"]

# Count valid temperature days
df["Valid_Temp_Days"] = df["Days"].where(
    df["Temperature"].notna(), 0
)

# Annual aggregation
annual_df = df.groupby(
    ["Location", "Year"]
).agg(
    Weighted_Temp_Sum=("Weighted_Temp", "sum"),
    Valid_Temp_Days=("Valid_Temp_Days", "sum"),
    Annual_Rainfall=("Rainfall_Total", "sum"),
    Temperature_Months=("Temperature", "count"),
    Rainfall_Months=("Rainfall", "count")
).reset_index()

# Calculate annual average temperature
annual_df["Temperature"] = (
    annual_df["Weighted_Temp_Sum"] /
    annual_df["Valid_Temp_Days"]
)

# Check completeness
annual_df["Complete_Year"] = (
    (annual_df["Temperature_Months"] == 12) &
    (annual_df["Rainfall_Months"] == 12)
)

# Round values
annual_df["Temperature"] = annual_df[
    "Temperature"
].round(2)

annual_df["Annual_Rainfall_mm"] = annual_df[
    "Annual_Rainfall"
].round(2)

# Final dataset
final_df = annual_df[
    [
        "Location",
        "Year",
        "Temperature",
        "Annual_Rainfall_mm",
        "Complete_Year"
    ]
]

# Save
final_df.to_csv(
    "annual_climate_trends_verified.csv",
    index=False
)

print("Annual aggregation completed!")

print("\nFirst five records:")
print(final_df.head())

print("\nDataset shape:")
print(final_df.shape)

print("\nComplete years:")
print(final_df["Complete_Year"].value_counts())

print("\nAnnual dataset saved successfully!")