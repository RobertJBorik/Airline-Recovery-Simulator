import streamlit as st
import pandas as pd
import plotly.express as px


def render(results_df, flights_df):

    st.header("Airline Operations Overview")

    st.write(
        """
        Monte Carlo simulation results showing how operational disruptions
        propagate through an airline network.
        """
    )
