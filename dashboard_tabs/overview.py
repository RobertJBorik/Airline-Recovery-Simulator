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


    # -----------------------------
    # Delay Sources
    # -----------------------------

    st.subheader("Delay Cause Breakdown")


    delay_data = pd.DataFrame({
        "Cause": [
            "Weather",
            "Gate",
            "Maintenance",
            "Propagation"
        ],
        "Minutes": [
            flights_df["weather_delay"].sum(),
            flights_df["gate_delay"].sum(),
            flights_df["maintenance_delay"].sum(),
            flights_df["propagated_delay"].sum()
        ]
    })


    fig = px.pie(
        delay_data,
        values="Minutes",
        names="Cause",
        title="Average Delay Contribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # -----------------------------
    # Flight Outcomes
    # -----------------------------

    st.subheader("Flight Outcomes")


    outcomes = (
        flights_df["status"]
        .value_counts()
        .reset_index()
    )

    outcomes.columns = [
        "Status",
        "Flights"
    ]


    fig = px.bar(
        outcomes,
        x="Status",
        y="Flights",
        title="Flight Status Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # -----------------------------
    # Cancellation Analysis
    # -----------------------------

    st.subheader("Cancellation Analysis")


    cancelled = flights_df[
        flights_df["status"] == "Cancelled"
    ]


    # -----------------------------
    # Aircraft Impact
    # -----------------------------

    st.subheader("Aircraft Delay Impact")


    aircraft_delay = (
        flights_df
        .groupby("aircraft")
        ["delay_minutes"]
        .sum()
        .reset_index()
        .sort_values(
            "delay_minutes",
            ascending=False
        )
        .head(10)
    )


    fig = px.bar(
        aircraft_delay,
        x="aircraft",
        y="delay_minutes",
        title="Top 10 Aircraft by Delay Minutes"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # -----------------------------
    # Route Impact
    # -----------------------------

    st.subheader("Route Performance")


    route_delay = (
        flights_df
        .groupby(
            [
                "origin",
                "destination"
            ]
        )
        ["delay_minutes"]
        .sum()
        .reset_index()
        .sort_values(
            "delay_minutes",
            ascending=False
        )
        .head(10)
    )


    route_delay["route"] = (
        route_delay["origin"]
        + " → "
        + route_delay["destination"]
    )


    fig = px.bar(
        route_delay,
        x="route",
        y="delay_minutes",
        title="Most Disrupted Routes"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )