import streamlit as st
import pandas as pd
import plotly.express as px

from dashboard_tabs import analytics
from dashboard_tabs import flight
from dashboard_tabs import overview
from dashboard_tabs import replay

st.set_page_config(page_title="Airline Operations Recovery Simulator", page_icon="✈️", layout="wide")

st.title("Airline Operations Recovery & Delay Propagation Simulator")

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data():
    results = pd.read_csv("results/simulation_results.csv")
    flights = pd.read_csv("results/flight_results.csv")
    return results, flights

results_df, flights_df = load_data()

st.divider()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Flights Simulated",
        f"{len(flights_df):,}"
    )

with col2:
    st.metric(
        "Average Daily Delay",
        f"{results_df['total_delay_minutes'].mean():.1f} min"
    )

with col3:
    cancel_rate = (flights_df["status"].eq("Cancelled").mean()*  100)

    st.metric(
        "Cancellation Rate",
        f"{cancel_rate:.2f}%"
    )

with col4:
    st.metric(
        "Worst Single Flight Delay",
        f"{flights_df['delay_minutes'].max()} min"
    )
    
overview_tab, analytics_tab, flights_tab, replay_tab = st.tabs(["Overview", "Analytics", "Flight Data", "Replay"])

with overview_tab:
    overview.render(results_df, flights_df)

with analytics_tab:
    analytics.render(results_df)

with flights_tab:
    flight.render(flights_df)

with replay_tab:
    replay.render(flights_df)