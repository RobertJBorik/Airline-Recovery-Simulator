import streamlit as st

def render(flights_df):

    st.header("Simulation Replay")

    simulation = st.number_input("Simulation Number", min_value=0, value=1, step=1, max_value=999)

    speed = 1.25

    col1, col2, col3 = st.columns(3)

    with col1:
        st.button("Play", disabled=True)

    with col2:
        st.button("Pause", disabled=True)

    with col3:
        st.button("Reset", disabled=True)

    st.divider()

    st.info(
        """
        **Simulation Replay Coming Soon**

        Planned features:
        - Live aircraft movement across the network
        - Real-time delay propagation
        - Flight cancellations and recovery visualization
        """
    )