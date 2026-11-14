import pandas as pd

# Load NASA dataset
df = pd.read_csv("kerala_climate_data.csv")

print("Original dataset:")
print(df.head())

print("\nDataset information:")
print(df.info())

# Check date formats
print("\nDate formats:")
print(df["Date"].astype(str).str.len().value_counts())

# Convert valid monthly dates
df["Date"] = pd.to_datetime(
    df["Date"].astype(str),
    format="%Y%m",
    errors="coerce"
)

# Count invalid dates
print("\nInvalid or annual records:",
      df["Date"].isna().sum())

# Remove annual summaries and invalid dates
df = df.dropna(subset=["Date"])

# Replace missing-value indicators
df.replace(-999, pd.NA, inplace=True)

# Convert numerical columns
df["Temperature"] = pd.to_numeric(
    df["Temperature"], errors="coerce"
)

df["Rainfall"] = pd.to_numeric(
    df["Rainfall"], errors="coerce"
)

# Check missing values
print("\nMissing values:")
print(df.isnull().sum())

# Remove duplicate records
df.drop_duplicates(inplace=True)

# Save cleaned dataset
df.to_csv("cleaned_kerala_climate.csv", index=False)

print("\nCleaned dataset saved successfully!")
print("Final shape:", df.shape)

print("\nRecords per location:")
print(df["Location"].value_counts())