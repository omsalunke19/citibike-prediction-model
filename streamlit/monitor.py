import streamlit as st
import pandas as pd
import mlflow
import plotly.express as px

# ======== AUTHENTICATION ========
# Hardcoded DagsHub credentials
MLFLOW_TRACKING_URI = "https://omsalunke19:816c73d273a7353039be11f982419529ac3817c8@dagshub.com/omsalunke19/cda500-final.mlflow"
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# ======== STREAMLIT APP ========
st.set_page_config(page_title="Citi Bike Monitoring Dashboard", layout="wide")
st.title("📊 Model Monitoring: Citi Bike Prediction")

# Sidebar navigation
page = st.sidebar.radio("Choose a view:", ["Model MAE Comparison", "Prediction Viewer"])

if page == "Model MAE Comparison":
    st.subheader("🔢 MAE Across Trained Models")

    # Load run data from MLflow
    df = mlflow.search_runs(experiment_ids=["0"], filter_string="", output_format="pandas")
    
    # Safely handle missing run name
    if "tags.mlflow.runName" in df.columns:
        df = df[["tags.mlflow.runName", "metrics.mae"]]
        df.columns = ["Model", "MAE"]
    else:
        df = df[["metrics.mae"]]
        df["Model"] = [f"Run {i}" for i in range(len(df))]
        df = df[["Model", "MAE"]]

    df = df.sort_values("MAE")
    st.dataframe(df.reset_index(drop=True))

    # Plot MAE Bar Chart
    fig = px.bar(df, x="Model", y="MAE", title="MAE by Model")
    st.plotly_chart(fig, use_container_width=True)

elif page == "Prediction Viewer":
    st.subheader("📊 Predicted Ride Counts")

    try:
        pred_df = pd.read_csv("../data/predictions/predictions.csv", parse_dates=["datetime"])
        pred_df["start_station_id"] = pred_df["start_station_id"].astype(str)

        station_options = pred_df["start_station_id"].unique()
        station = st.selectbox("Select a Station:", sorted(station_options))

        st.line_chart(
            pred_df[pred_df["start_station_id"] == station][["datetime", "predicted_ride_count"]].set_index("datetime")
        )
    except FileNotFoundError:
        st.warning("Prediction file not found. Please run inference first.")