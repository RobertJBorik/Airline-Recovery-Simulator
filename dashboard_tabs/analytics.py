import streamlit as st
import plotly.express as px

def render(results_df):
    st.header("Analytics")

   # -----------------------------
    # Delay Distribution
    # -----------------------------

    st.subheader("Network Delay Distribution")

    fig = px.histogram(
        results_df,
        x="total_delay_minutes",
        nbins=50,
        title="Total Delay Minutes Across Simulations"
    )

    fig.update_layout(
        xaxis_title="Total Delay Minutes",
        yaxis_title="Simulation Count"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
