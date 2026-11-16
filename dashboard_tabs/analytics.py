import streamlit as st
import plotly.express as px

def render(results_df):
    st.header("Analytics")

    if "recovery_strategy" in results_df.columns:
        st.subheader("Recovery Strategy Comparison")
        comparison_columns = {
            "total_delay_minutes": "Average Total Delay",
            "propagated_delay": "Average Propagated Delay",
            "completed": "Average Completed Flights",
            "reserve_activations": "Average Reserve Activations",
            "aircraft_swaps": "Average Aircraft Swaps",
            "cyclical_aircraft_swaps": "Average Cyclical Aircraft Swaps",
            "reserve_reposition_count": "Average Reserve Repositions",
            "reserve_reposition_minutes": "Average Reserve Reposition Minutes",
            "recovered_delay_minutes": "Average Delay Avoided",
        }
        available_columns = {
            column: label
            for column, label in comparison_columns.items()
            if column in results_df.columns
        }
        comparison = (
            results_df.groupby("recovery_strategy")[list(available_columns)]
            .mean()
            .rename(columns=available_columns)
            .reset_index()
        )
        st.dataframe(comparison, hide_index=True, use_container_width=True)

        if results_df["recovery_strategy"].nunique() > 1:
            fig = px.box(
                results_df,
                x="recovery_strategy",
                y="total_delay_minutes",
                color="recovery_strategy",
                title="Total Delay by Recovery Strategy",
            )
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Network Delay Distribution")

    fig = px.histogram(
        results_df,
        x="total_delay_minutes",
        nbins=50,
        color="recovery_strategy" if "recovery_strategy" in results_df.columns else None,
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
