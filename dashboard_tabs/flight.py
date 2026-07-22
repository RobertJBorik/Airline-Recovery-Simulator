import streamlit as st

def render(flights_df):

    st.header("Flight Explorer")

    airport = st.selectbox(
        "Origin Airport",
        ["All"] + sorted(flights_df["origin"].unique())
    )

    status = st.selectbox(
        "Status",
        ["All"] + sorted(flights_df["status"].unique())
    )

    filtered = flights_df.copy()

    if airport != "All":
        filtered = filtered[
            filtered["origin"] == airport
        ]

    if status != "All":
        filtered = filtered[
            filtered["status"] == status
        ]

    st.dataframe(
        filtered,
        use_container_width=True,
        height=600
    )