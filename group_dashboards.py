"""
COSMHOTEL Group-level Dashboards
Consolidated reporting and analytics for multi-property management
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import config
from data_parsers import (
    GroupDataAggregator,
    RevenueParser,
    ManagerReportParser,
    ForecastParser,
)


def render_group_overview():
    """Main Group Overview Dashboard"""
    st.set_page_config(
        page_title="COSMHOTEL Group Dashboard",
        page_icon="🏢",
        layout="wide",
    )
    
    st.title("🏢 COSMHOTEL GROUP - CONSOLIDATED DASHBOARD")
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Group KPIs",
        "🏨 Hotel Comparison",
        "📈 Revenue Analysis",
        "🛏️ Occupancy Trends"
    ])
    
    with tab1:
        render_group_kpis()
    
    with tab2:
        render_hotel_comparison()
    
    with tab3:
        render_revenue_analysis()
    
    with tab4:
        render_occupancy_trends()


def render_group_kpis():
    """Display key performance indicators for the entire group"""
    st.subheader("🎯 Group Key Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Total Properties",
            value=len(config.HOTEL_PROPERTIES),
            delta="Hotels active",
            delta_color="off"
        )
    
    with col2:
        total_rooms = sum(hotel.get("rooms", 0) for hotel in config.HOTEL_PROPERTIES.values())
        st.metric(
            label="Total Rooms",
            value=f"{total_rooms:,}",
            delta="Across group",
            delta_color="off"
        )
    
    with col3:
        total_capacity = sum(hotel.get("capacity_guests", 0) for hotel in config.HOTEL_PROPERTIES.values())
        st.metric(
            label="Guest Capacity",
            value=f"{total_capacity:,}",
            delta="Total guests",
            delta_color="off"
        )
    
    with col4:
        st.metric(
            label="Average Occupancy",
            value="--",
            delta="Loading from database...",
            delta_color="off"
        )
    
    with col5:
        st.metric(
            label="Group Revenue",
            value="--",
            delta="Loading from database...",
            delta_color="off"
        )
    
    st.markdown("---")
    
    # Group metrics by timeframe
    st.subheader("Revenue by Timeframe")
    
    st.info("📊 Revenue data will be loaded from database once data files are uploaded.")


def render_hotel_comparison():
    """Compare metrics across all hotels"""
    st.subheader("🏨 Hotel-by-Hotel Comparison")
    
    # Create comparison data
    comparison_data = {
        "Hotel": [],
        "Rooms": [],
        "Capacity": [],
        "Today Occupancy %": [],
        "Month Revenue": [],
        "Avg Daily Rate": [],
    }
    
    for key, hotel in config.HOTEL_PROPERTIES.items():
        comparison_data["Hotel"].append(hotel["name"])
        comparison_data["Rooms"].append(hotel.get("rooms", 0))
        comparison_data["Capacity"].append(hotel.get("capacity_guests", 0))
        comparison_data["Today Occupancy %"].append(0)  # Will be loaded from database
        comparison_data["Month Revenue"].append("€0")  # Will be loaded from database
        comparison_data["Avg Daily Rate"].append("€0")  # Will be loaded from database
    
    comparison_df = pd.DataFrame(comparison_data)
    
    st.dataframe(
        comparison_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Hotel": st.column_config.TextColumn(width="large"),
            "Rooms": st.column_config.NumberColumn(width="small"),
            "Capacity": st.column_config.NumberColumn(width="small"),
            "Today Occupancy %": st.column_config.ProgressColumn(
                min_value=0,
                max_value=100,
                width="medium"
            ),
            "Month Revenue": st.column_config.TextColumn(width="medium"),
            "Avg Daily Rate": st.column_config.TextColumn(width="medium"),
        }
    )
    
    # Create visualization
    col1, col2 = st.columns(2)
    
    with col1:
        fig_rooms = go.Figure(
            data=[
                go.Bar(
                    x=comparison_df["Hotel"],
                    y=comparison_df["Rooms"],
                    name="Rooms",
                    marker_color=config.COLOR_HOTEL,
                )
            ]
        )
        fig_rooms.update_layout(
            title="Rooms by Hotel",
            xaxis_title="Hotel",
            yaxis_title="Number of Rooms",
            hovermode="x unified",
            height=400,
        )
        st.plotly_chart(fig_rooms, use_container_width=True)
    
    with col2:
        st.info("📊 Real occupancy data will be displayed once manager reports are uploaded.")
        st.write("Waiting for data ingestion...")


def render_revenue_analysis():
    """Analyze revenue across properties"""
    st.subheader("📈 Revenue Analysis")
    
    st.info("💼 Revenue data will be loaded from uploaded financial reports and trial balance files.")


def render_occupancy_trends():
    """Display occupancy trends across the group"""
    st.subheader("🛏️ Occupancy Trends")
    
    st.info("📊 Occupancy data will be loaded from manager reports once files are uploaded.")
    st.write("The system is ready to process:")
    st.write("- Current occupancy by hotel")
    st.write("- 7-day occupancy forecasts")
    st.write("- 6-month trend analysis")


if __name__ == "__main__":
    render_group_overview()
