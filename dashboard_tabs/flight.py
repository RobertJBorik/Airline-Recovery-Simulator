import streamlit as st


def render(flights_df):

    st.header("Flight Explorer")

    filtered = flights_df.copy()

    # --------------------
    # Filters
    # --------------------


    col1, col2, col3, col4 = st.columns(4)

    with col1:
        sim_num = st.number_input(
        "Simulation Number",
        min_value=int(flights_df["simulation_num"].min()),
        max_value=int(flights_df["simulation_num"].max()),
        value=int(flights_df["simulation_num"].min()),
        step=1
        )
            
    with col2:
        origin = st.selectbox(
            "Origin Airport",
            ["All"] + sorted(flights_df["origin"].unique())
        )

    with col3:
        destination = st.selectbox(
            "Destination Airport",
            ["All"] + sorted(flights_df["destination"].unique())
        )

    with col4:
        route_options = (
            flights_df["origin"] 
            + " → " 
            + flights_df["destination"]
        ).unique()

        route = st.selectbox(
            "Route",
            ["All"] + sorted(route_options)
        )


    # --------------------
    # Display
    # --------------------
    
    # Apply filters
    filtered = filtered[
        filtered["simulation_num"] == sim_num
    ]
    
    if origin != "All":
        filtered = filtered[
            filtered["origin"] == origin
        ]
    
    if destination != "All":
        filtered = filtered[
            filtered["destination"] == destination
        ]
    
    if route != "All":
        route_origin, route_dest = route.split(" → ")
        filtered = filtered[
            (filtered["origin"] == route_origin) &
            (filtered["destination"] == route_dest)
        ]
    
    MAX_ROWS = 5000
    
    if len(filtered) > MAX_ROWS:
        st.warning(
            f"Showing first {MAX_ROWS:,} rows. "
            "Use filters to narrow results."
        )
    
    st.dataframe(
        filtered.head(MAX_ROWS),
        use_container_width=True,
        height=600
    )