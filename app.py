import streamlit as st
import pandas as pd
import plotly.express as px
import pymannkendall as mk
from scipy.stats import linregress

# Page configuration
st.set_page_config(
    page_title="EarthTrend",
    page_icon="🌍",
    layout="wide"
)

# Load dataset
# Load dataset
@st.cache_data
def load_data():

    df = pd.read_csv("annual_climate_trends_verified.csv")

    # Use only complete annual records
    df = df[df["Complete_Year"] == True].copy()

    return df


df = load_data()

# Title
st.title("🌍 EarthTrend")
st.subheader("NASA-Powered Environmental Intelligence")

st.write(
    "Explore temperature and rainfall patterns "
    "across selected locations in Kerala."
)

st.divider()

# Sidebar
st.sidebar.header("Dashboard Controls")

locations = ["All Locations"] + sorted(
    df["Location"].unique().tolist()
)

selected_location = st.sidebar.selectbox(
    "Select Location",
    locations
)

# Filter data
if selected_location == "All Locations":
    filtered_df = df.copy()
else:
    filtered_df = df[
        df["Location"] == selected_location
    ]
    # TEMPERATURE ANOMALY CALCULATION

baseline_data = df[
    df["Year"].between(2001, 2020)
]

baseline = baseline_data.groupby(
    "Location"
)["Temperature"].mean()

filtered_df["Temperature_Anomaly"] = (
    filtered_df["Temperature"]
    - filtered_df["Location"].map(baseline)
)

# KPI calculations
avg_temp = filtered_df["Temperature"].mean()

avg_rainfall = filtered_df[
    "Annual_Rainfall_mm"
].mean()

highest_temp = filtered_df["Temperature"].max()

# KPI cards
st.header("Climate Overview")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Average Temperature",
    f"{avg_temp:.2f} °C"
)

col2.metric(
    "Average Annual Rainfall",
    f"{avg_rainfall:.2f} mm"
)

col3.metric(
    "Highest Annual Temperature",
    f"{highest_temp:.2f} °C"
)

st.divider()

# Temperature graph
st.header("🌡️ Temperature Analysis")

fig1 = px.line(
    filtered_df,
    x="Year",
    y="Temperature",
    color="Location",
    markers=True,
    title="Annual Temperature Trends"
)

fig1.update_layout(
    xaxis_title="Year",
    yaxis_title="Average Temperature (°C)"
)

st.plotly_chart(fig1, width="stretch")
# TEMPERATURE ANOMALY ANALYSIS

st.divider()

st.header("🌡️ Temperature Anomaly Analysis")

st.write(
    "Temperature differences compared with "
    "the 2001–2020 baseline average."
)

fig_anomaly = px.bar(
    filtered_df,
    x="Year",
    y="Temperature_Anomaly",
    color="Location",
    barmode="group",
    title="Annual Temperature Anomalies"
)

fig_anomaly.add_hline(
    y=0,
    line_dash="dash",
    line_color="white"
)

fig_anomaly.update_layout(
    xaxis_title="Year",
    yaxis_title="Temperature Anomaly (°C)"
)

st.plotly_chart(
    fig_anomaly,
    width="stretch"
)
# =====================================
# DECADAL WARMING ANALYSIS
# =====================================

st.divider()

st.header("📈 Decadal Temperature Change")

st.write(
    "Estimated temperature change per decade "
    "using linear regression of annual averages."
)

decadal_results = []

for location in filtered_df["Location"].unique():

    location_data = filtered_df[
        filtered_df["Location"] == location
    ].sort_values("Year")

    years = location_data["Year"].values
    temperatures = location_data["Temperature"].values

    valid = (
        pd.notna(years) &
        pd.notna(temperatures)
    )

    years = years[valid]
    temperatures = temperatures[valid]

    if len(years) >= 3:

        result = linregress(years, temperatures)

        change = result.slope * 10

        mk_result = mk.original_test(temperatures)

        decadal_results.append({
            "Location": location,
            "Change per Decade (°C)": round(change, 4),
            "Trend": mk_result.trend,
            "P-value": round(mk_result.p, 4)
        })

decadal_df = pd.DataFrame(decadal_results)

# Display results
st.dataframe(
    decadal_df,
    width="stretch",
    hide_index=True
)

# Visualization
fig_decadal = px.bar(
    decadal_df,
    x="Location",
    y="Change per Decade (°C)",
    color="Location",
    title="Temperature Change per Decade"
)

fig_decadal.add_hline(
    y=0,
    line_dash="dash"
)

st.plotly_chart(
    fig_decadal,
    width="stretch"
)

st.info(
    "Positive values indicate warming and negative "
    "values indicate cooling. P-values indicate "
    "statistical evidence of a monotonic trend."
)
# =====================================
# AUTOMATED CLIMATE INSIGHTS
# =====================================

st.divider()

st.header("🧠 Automated Climate Insights")

st.write(
    "Important environmental findings generated "
    "automatically from NASA climate data."
)

# 1. Highest average temperature
avg_location_temp = (
    filtered_df.groupby("Location")["Temperature"]
    .mean()
)

hottest_location = avg_location_temp.idxmax()

hottest_value = avg_location_temp.max()

# 2. Highest warming rate
if not decadal_df.empty:

    fastest_warming = decadal_df.loc[
        decadal_df["Change per Decade (°C)"].idxmax()
    ]

    # 3. Warmest year
    warmest_row = filtered_df.loc[
        filtered_df["Temperature"].idxmax()
    ]

    # 4. Significant trends
    significant = decadal_df[
        decadal_df["P-value"] < 0.05
    ]

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Highest Average Temperature",
            hottest_location
        )

        st.metric(
            "Highest Average Temperature Value",
            f"{hottest_value:.2f} °C"
        )

    with col2:
        st.metric(
            "Highest Estimated Warming",
            fastest_warming["Location"]
        )

        st.metric(
            "Warming Rate",
            f'{fastest_warming["Change per Decade (°C)"]:.4f} °C/decade'
        )

    st.subheader("🔍 Key Findings")

    st.info(
        f"{fastest_warming['Location']} has the "
        f"highest estimated warming rate of "
        f"{fastest_warming['Change per Decade (°C)']:.4f} °C per decade."
    )

    st.success(
        f"{len(significant)} out of {len(decadal_df)} "
        "selected locations show statistically significant "
        "increasing or decreasing trends at the 0.05 level."
    )

    st.warning(
        f"The highest annual average temperature in the "
        f"selected dataset occurred in {int(warmest_row['Year'])} "
        f"at {warmest_row['Location']}, reaching "
        f"{warmest_row['Temperature']:.2f} °C."
    )
# Rainfall graph
st.header("🌧️ Rainfall Analysis")

fig2 = px.line(
    filtered_df,
    x="Year",
    y="Annual_Rainfall_mm",
    color="Location",
    markers=True,
    title="Annual Rainfall Trends"
)

fig2.update_layout(
    xaxis_title="Year",
    yaxis_title="Annual Rainfall (mm)"
)

st.plotly_chart(fig2, width="stretch")
# =====================================
# EXTREME RAINFALL DETECTION
# =====================================

st.divider()

st.header("🌧️ Extreme Rainfall Detection")

st.write(
    "Identifying unusually wet and dry years "
    "using historical NASA rainfall data."
)

# Calculate rainfall thresholds for each location
filtered_df = filtered_df.copy()

filtered_df["Wet_Threshold"] = (
    filtered_df.groupby("Location")["Annual_Rainfall_mm"]
    .transform(lambda x: x.quantile(0.90))
)

filtered_df["Dry_Threshold"] = (
    filtered_df.groupby("Location")["Annual_Rainfall_mm"]
    .transform(lambda x: x.quantile(0.10))
)

# Classify rainfall
filtered_df["Rainfall_Category"] = "Normal"

filtered_df.loc[
    filtered_df["Annual_Rainfall_mm"] >=
    filtered_df["Wet_Threshold"],
    "Rainfall_Category"
] = "Unusually Wet"

filtered_df.loc[
    filtered_df["Annual_Rainfall_mm"] <=
    filtered_df["Dry_Threshold"],
    "Rainfall_Category"
] = "Unusually Dry"

# Wettest and driest years
st.subheader("🏆 Wettest and Driest Years")

extreme_rows = []

for location in filtered_df["Location"].unique():

    location_data = filtered_df[
        filtered_df["Location"] == location
    ]

    wettest = location_data.loc[
        location_data["Annual_Rainfall_mm"].idxmax()
    ]

    driest = location_data.loc[
        location_data["Annual_Rainfall_mm"].idxmin()
    ]

    extreme_rows.append({
        "Location": location,
        "Wettest Year": int(wettest["Year"]),
        "Highest Rainfall (mm)": wettest["Annual_Rainfall_mm"],
        "Driest Year": int(driest["Year"]),
        "Lowest Rainfall (mm)": driest["Annual_Rainfall_mm"]
    })

extreme_df = pd.DataFrame(extreme_rows)

st.dataframe(
    extreme_df,
    width="stretch",
    hide_index=True
)

# Rainfall classification
st.subheader("📊 Unusual Rainfall Years")

unusual_df = filtered_df[
    filtered_df["Rainfall_Category"] != "Normal"
].copy()

st.dataframe(
    unusual_df[
        [
            "Location",
            "Year",
            "Annual_Rainfall_mm",
            "Rainfall_Category"
        ]
    ],
    width="stretch",
    hide_index=True
)

# Rainfall anomaly calculation
st.subheader("📈 Annual Rainfall Anomalies")

rain_baseline = (
    df[df["Year"].between(2001, 2020)]
    .groupby("Location")["Annual_Rainfall_mm"]
    .mean()
)

filtered_df["Rainfall_Anomaly_Percent"] = (
    (
        filtered_df["Annual_Rainfall_mm"]
        - filtered_df["Location"].map(rain_baseline)
    )
    / filtered_df["Location"].map(rain_baseline)
) * 100

fig_rain_anomaly = px.bar(
    filtered_df,
    x="Year",
    y="Rainfall_Anomaly_Percent",
    color="Location",
    barmode="group",
    title="Annual Rainfall Anomalies (2001–2020 Baseline)"
)

fig_rain_anomaly.add_hline(
    y=0,
    line_dash="dash"
)

fig_rain_anomaly.update_layout(
    xaxis_title="Year",
    yaxis_title="Rainfall Anomaly (%)"
)

st.plotly_chart(
    fig_rain_anomaly,
    width="stretch"
)

st.info(
    "Rainfall anomalies show percentage differences "
    "from the 2001–2020 average. The 10th and 90th "
    "percentiles identify unusually dry and wet years."
)

# Statistical trend analysis
st.header("📊 Statistical Trend Detection")

results = []

for location in filtered_df["Location"].unique():

    location_data = filtered_df[
        filtered_df["Location"] == location
    ].sort_values("Year")

    temp = location_data[
        "Temperature"
    ].dropna().values

    rainfall = location_data[
        "Annual_Rainfall_mm"
    ].dropna().values

    temp_result = mk.original_test(temp)
    rain_result = mk.original_test(rainfall)

    results.append({
        "Location": location,
        "Temperature Trend": temp_result.trend,
        "Temperature P-value": round(temp_result.p, 4),
        "Rainfall Trend": rain_result.trend,
        "Rainfall P-value": round(rain_result.p, 4)
    })

results_df = pd.DataFrame(results)

st.dataframe(
    results_df,
    width="stretch",
    hide_index=True
)

st.info(
    "A p-value below 0.05 indicates statistically "
    "significant evidence of a monotonic trend."
)

# Dataset
st.header("📁 Climate Dataset")

st.dataframe(
    filtered_df,
    width="stretch",
    hide_index=True
)

# Download
csv = filtered_df.to_csv(index=False)

st.download_button(
    "Download Climate Data",
    csv,
    "earthtrend_climate_data.csv",
    "text/csv"
)

st.divider()

st.caption(
    "Data source: NASA POWER | "
    "Analysis period: 2001–2025 | "
    "Locations: Kerala, India"
)
# ==========================================
# CLIMATE RISK CLASSIFICATION
# ==========================================

st.divider()

st.header("⚠️ Climate Risk Classification")

st.write(
    "Comparative climate risk assessment based on "
    "temperature warming, rainfall variability "
    "and extreme rainfall frequency."
)

# Use complete annual dataset
risk_data = df.copy()

risk_results = []

# Calculate indicators for each location
for location in risk_data["Location"].unique():

    data = risk_data[
        risk_data["Location"] == location
    ].sort_values("Year")

    # 1. Temperature warming rate
    temp_result = linregress(
        data["Year"],
        data["Temperature"]
    )

    warming_rate = temp_result.slope * 10

    # 2. Rainfall variability
    rainfall_mean = data["Annual_Rainfall_mm"].mean()

    rainfall_std = data["Annual_Rainfall_mm"].std()

    rainfall_cv = (
        rainfall_std / rainfall_mean
    ) * 100 if rainfall_mean != 0 else 0

    # 3. Extreme rainfall frequency
    wet_threshold = data[
        "Annual_Rainfall_mm"
    ].quantile(0.90)

    extreme_years = (
        data["Annual_Rainfall_mm"] >= wet_threshold
    ).sum()

    extreme_frequency = (
        extreme_years / len(data)
    ) * 100

    risk_results.append({
        "Location": location,
        "Warming Rate (°C/decade)": warming_rate,
        "Rainfall Variability (%)": rainfall_cv,
        "Extreme Rainfall Frequency (%)": extreme_frequency
    })


# Create risk dataframe
risk_df = pd.DataFrame(risk_results)


# Normalize scores between 0 and 100
risk_columns = [
    "Warming Rate (°C/decade)",
    "Rainfall Variability (%)",
    "Extreme Rainfall Frequency (%)"
]

for column in risk_columns:

    minimum = risk_df[column].min()
    maximum = risk_df[column].max()

    if maximum != minimum:

        risk_df[column + "_Score"] = (
            (risk_df[column] - minimum)
            / (maximum - minimum)
        ) * 100

    else:

        risk_df[column + "_Score"] = 50


# Calculate overall climate risk score
score_columns = [
    column + "_Score"
    for column in risk_columns
]

risk_df["Climate Risk Score"] = (
    risk_df[score_columns].mean(axis=1)
).round(2)


# Risk classification
def classify_risk(score):

    if score < 33:
        return "Low"

    elif score < 67:
        return "Moderate"

    else:
        return "High"


risk_df["Risk Level"] = (
    risk_df["Climate Risk Score"]
    .apply(classify_risk)
)


# Display results
st.subheader("📊 Climate Risk Assessment")

st.dataframe(
    risk_df[
        [
            "Location",
            "Warming Rate (°C/decade)",
            "Rainfall Variability (%)",
            "Extreme Rainfall Frequency (%)",
            "Climate Risk Score",
            "Risk Level"
        ]
    ].round(2),
    width="stretch",
    hide_index=True
)


# Climate Risk Visualization
st.subheader("🌍 Comparative Climate Risk Scores")

fig_risk = px.bar(
    risk_df,
    x="Location",
    y="Climate Risk Score",
    color="Risk Level",
    text="Climate Risk Score",
    title="Comparative Climate Risk Assessment",
    color_discrete_map={
        "Low": "green",
        "Moderate": "orange",
        "High": "red"
    }
)

fig_risk.update_layout(
    xaxis_title="Location",
    yaxis_title="Climate Risk Score (0–100)",
    yaxis=dict(range=[0, 110])
)

st.plotly_chart(
    fig_risk,
    width="stretch"
)


# Highest comparative risk
highest_risk = risk_df.loc[
    risk_df["Climate Risk Score"].idxmax()
]

st.warning(
    f"{highest_risk['Location']} has the highest "
    f"comparative climate risk score of "
    f"{highest_risk['Climate Risk Score']:.2f}."
)

st.info(
    "Note: These are exploratory, relative climate "
    "indicators for the selected study locations. "
    "They are not official disaster-risk classifications "
    "or predictions."
)
# ==================================
# INTERACTIVE KERALA MAP
# ==================================
# =====================================
# INTERACTIVE KERALA CLIMATE MAP
# =====================================

st.divider()

st.header("🗺️ Geographical Distribution")

st.write(
    "Explore the three geographical locations "
    "selected for our NASA climate analysis."
)

map_data = pd.DataFrame({
    "Location": [
        "Kollam",
        "Trivandrum",
        "Idukki"
    ],
    "Latitude": [
        8.8932,
        8.5241,
        9.8494
    ],
    "Longitude": [
        76.6141,
        76.9366,
        76.9680
    ]
})

if selected_location != "All Locations":
    map_data = map_data[
        map_data["Location"] == selected_location
    ]

fig_map = px.scatter_geo(
    map_data,
    lat="Latitude",
    lon="Longitude",
    text="Location",
    hover_name="Location",
    hover_data=["Latitude", "Longitude"],
    title="Climate Study Locations – Kerala, India"
)

fig_map.update_geos(
    fitbounds="locations",
    showland=True,
    landcolor="#e8eadf",
    showocean=True,
    oceancolor="#dceef7",
    showcountries=True,
    showcoastlines=True
)
fig_map.update_traces(
    marker=dict(size=15),
    textposition="top center"
)
   
fig_map.update_layout(
    height=550,
    margin=dict(l=10, r=10, t=60, b=10)
)

st.plotly_chart(
    fig_map,
    width="stretch"
)
# ==========================================
# MACHINE LEARNING CLIMATE FORECASTING
# ==========================================

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

st.divider()

st.header("🤖 Machine Learning Climate Forecasting")

st.write(
    "Explore future temperature and rainfall trends "
    "using historical NASA POWER climate data."
)

# Forecast period
future_years = np.arange(2026, 2031)

forecast_results = []
evaluation_results = []

# Select climate parameters
parameters = {
    "Temperature": "Temperature (°C)",
    "Annual_Rainfall_mm": "Annual Rainfall (mm)"
}

for location in df["Location"].unique():

    location_data = df[
        df["Location"] == location
    ].sort_values("Year")

    for column, label in parameters.items():

        data = location_data[
            ["Year", column]
        ].dropna()

        X = data[["Year"]]
        y = data[column]

        if len(data) < 10:
            continue

        # Chronological train-test split
        split = int(len(data) * 0.8)

        X_train = X.iloc[:split]
        X_test = X.iloc[split:]

        y_train = y.iloc[:split]
        y_test = y.iloc[split:]

        # Linear Regression
        linear_model = LinearRegression()

        linear_model.fit(X_train, y_train)

        linear_predictions = linear_model.predict(X_test)

        # Random Forest
        rf_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=4,
            random_state=42
        )

        rf_model.fit(X_train, y_train)

        rf_predictions = rf_model.predict(X_test)

        # Model evaluation
        for model_name, predictions in [
            ("Linear Regression", linear_predictions),
            ("Random Forest", rf_predictions)
        ]:

            mae = mean_absolute_error(
                y_test, predictions
            )

            rmse = np.sqrt(
                mean_squared_error(y_test, predictions)
            )

            r2 = r2_score(
                y_test, predictions
            )

            evaluation_results.append({
                "Location": location,
                "Parameter": label,
                "Model": model_name,
                "MAE": round(mae, 3),
                "RMSE": round(rmse, 3),
                "R2 Score": round(r2, 3)
            })

        # Refit linear model using all historical data
        final_model = LinearRegression()

        final_model.fit(X, y)

        future_predictions = final_model.predict(
            pd.DataFrame({"Year": future_years})
        )

        # Rainfall cannot be negative
        if column == "Annual_Rainfall_mm":
            future_predictions = np.maximum(
                future_predictions, 0
            )

        # Store predictions
        for year, prediction in zip(
            future_years, future_predictions
        ):

            forecast_results.append({
                "Location": location,
                "Year": year,
                "Parameter": label,
                "Predicted Value": round(
                    float(prediction), 2
                )
            })


# Convert results to DataFrames
forecast_df = pd.DataFrame(forecast_results)

evaluation_df = pd.DataFrame(evaluation_results)


# ==========================================
# MODEL PERFORMANCE
# ==========================================

st.subheader("📊 Machine Learning Model Evaluation")

st.write(
    "Models are evaluated using the last five historical "
    "years as a chronological test set."
)

st.dataframe(
    evaluation_df,
    width="stretch",
    hide_index=True
)


# ==========================================
# TEMPERATURE FORECAST
# ==========================================

st.subheader("🌡️ Temperature Forecast (2026–2030)")

temp_forecast = forecast_df[
    forecast_df["Parameter"] == "Temperature (°C)"
]

st.dataframe(
    temp_forecast,
    width="stretch",
    hide_index=True
)

fig_temp_forecast = px.line(
    temp_forecast,
    x="Year",
    y="Predicted Value",
    color="Location",
    markers=True,
    title="Predicted Annual Temperature (2026–2030)"
)

fig_temp_forecast.update_layout(
    xaxis_title="Year",
    yaxis_title="Predicted Temperature (°C)"
)

st.plotly_chart(
    fig_temp_forecast,
    width="stretch"
)


# ==========================================
# RAINFALL FORECAST
# ==========================================

st.subheader("🌧️ Rainfall Forecast (2026–2030)")

rain_forecast = forecast_df[
    forecast_df["Parameter"] == "Annual Rainfall (mm)"
]

st.dataframe(
    rain_forecast,
    width="stretch",
    hide_index=True
)

fig_rain_forecast = px.line(
    rain_forecast,
    x="Year",
    y="Predicted Value",
    color="Location",
    markers=True,
    title="Predicted Annual Rainfall (2026–2030)"
)

fig_rain_forecast.update_layout(
    xaxis_title="Year",
    yaxis_title="Predicted Rainfall (mm)"
)

st.plotly_chart(
    fig_rain_forecast,
    width="stretch"
)


# ==========================================
# IMPORTANT NOTE
# ==========================================

st.info(
    "Forecasts are exploratory linear trend projections "
    "based on 2001–2025 historical data. Random Forest "
    "is evaluated separately on historical test data. "
    "These projections do not account for future climate "
    "drivers or extreme weather events."
)

st.success(
    "Climate forecasting and model evaluation completed!"
)