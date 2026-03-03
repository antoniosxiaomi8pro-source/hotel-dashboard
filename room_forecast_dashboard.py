"""
Room Forecast Analysis Dashboard
Displays room availability forecasts and trends
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from supabase_client import supabase

def get_room_forecasts(hotel_name: str, days: int = 90) -> pd.DataFrame:
    """Get room forecasts for the next N days"""
    try:
        response = supabase.table("room_forecast").select("*").eq("hotel_name", hotel_name).order("forecast_date", desc=False).limit(days).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            df['forecast_date'] = pd.to_datetime(df['forecast_date'])
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching forecasts: {str(e)}")
        return pd.DataFrame()

def show_room_forecast_dashboard(hotel_name: str):
    """Display room forecast analysis"""
    st.title("📅 Room Forecast Analysis")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "📈 Trends", "📋 Details"])
    
    with tab1:
        st.subheader("Forecast Overview")
        
        forecasts = get_room_forecasts(hotel_name, days=90)
        
        if forecasts.empty:
            st.info("No forecast data available for this hotel")
            return
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        # Get unique room types
        room_types = forecasts['room_type'].unique()
        
        with col1:
            st.metric("Room Types Tracked", len(room_types))
        
        with col2:
            avg_forecast = forecasts['forecast_value'].mean()
            st.metric("Avg Forecasted Rooms", f"{avg_forecast:.0f}")
        
        with col3:
            latest_date = forecasts['forecast_date'].max()
            st.metric("Latest Forecast", latest_date.strftime("%Y-%m-%d"))
        
        with col4:
            days_ahead = (latest_date - datetime.now().date()).days
            st.metric("Forecast Days Ahead", f"{days_ahead} days")
        
        st.divider()
        
        # Room type breakdown
        st.subheader("Room Types Available")
        
        room_type_data = []
        for room_type in room_types:
            room_data = forecasts[forecasts['room_type'] == room_type]
            room_type_data.append({
                "Room Type": room_type,
                "Count": room_data['forecast_value'].iloc[-1] if len(room_data) > 0 else 0,
                "Avg (90 days)": room_data['forecast_value'].mean(),
                "Min": room_data['forecast_value'].min(),
                "Max": room_data['forecast_value'].max()
            })
        
        if room_type_data:
            df_rooms = pd.DataFrame(room_type_data)
            st.dataframe(df_rooms, use_container_width=True)
    
    with tab2:
        st.subheader("Forecast Trends")
        
        forecasts = get_room_forecasts(hotel_name, days=90)
        
        if forecasts.empty:
            st.info("No data available")
            return
        
        # Time series by room type
        fig = px.line(
            forecasts,
            x='forecast_date',
            y='forecast_value',
            color='room_type',
            title='Room Forecast Trends (90 Days)',
            labels={
                'forecast_date': 'Date',
                'forecast_value': 'Rooms Forecasted',
                'room_type': 'Room Type'
            }
        )
        
        fig.update_layout(hovermode='x unified', height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary statistics by room type
        st.subheader("Forecast Statistics by Room Type")
        
        summary = forecasts.groupby('room_type').agg({
            'forecast_value': ['count', 'mean', 'min', 'max', 'std']
        }).round(2)
        
        summary.columns = ['Days Forecasted', 'Average', 'Minimum', 'Maximum', 'Std Dev']
        st.dataframe(summary, use_container_width=True)
    
    with tab3:
        st.subheader("Forecast Details (Last 30 Days)")
        
        forecasts = get_room_forecasts(hotel_name, days=30)
        
        if forecasts.empty:
            st.info("No data available")
            return
        
        # Display detailed table
        display_cols = ['forecast_date', 'room_type', 'forecast_value', 'month', 'year', 'source_file']
        
        # Rename for display
        df_display = forecasts[display_cols].copy()
        df_display.columns = ['Date', 'Room Type', 'Rooms Forecasted', 'Month', 'Year', 'Source File']
        df_display = df_display.sort_values('Date', ascending=False)
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Download option
        csv = df_display.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"room_forecasts_{hotel_name}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

def show_group_room_forecast():
    """Display room forecast analysis for all hotels"""
    st.title("📅 Group Room Forecast Analysis")
    
    tab1, tab2 = st.tabs(["📊 Overview", "🏨 By Hotel"])
    
    with tab1:
        st.subheader("All Hotels Forecast Summary")
        
        # Get all hotels
        try:
            hotels_response = supabase.table("hotels").select("name").eq("is_active", True).execute()
            hotels = [h['name'] for h in hotels_response.data] if hotels_response.data else []
            
            if not hotels:
                st.info("No active hotels found")
                return
            
            # Aggregate forecasts
            all_forecasts = []
            for hotel in hotels:
                forecasts = get_room_forecasts(hotel, days=30)
                if not forecasts.empty:
                    forecasts['hotel_name'] = hotel
                    all_forecasts.append(forecasts)
            
            if all_forecasts:
                df_all = pd.concat(all_forecasts, ignore_index=True)
                
                # Chart: Total forecasted rooms by date
                daily_total = df_all.groupby('forecast_date')['forecast_value'].sum().reset_index()
                daily_total['forecast_date'] = pd.to_datetime(daily_total['forecast_date'])
                
                fig = px.bar(
                    daily_total,
                    x='forecast_date',
                    y='forecast_value',
                    title='Total Forecasted Rooms - All Hotels (30 Days)',
                    labels={'forecast_date': 'Date', 'forecast_value': 'Total Rooms'}
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Summary by hotel
                st.subheader("Summary by Hotel")
                
                summary_data = []
                for hotel in hotels:
                    hotel_data = df_all[df_all['hotel_name'] == hotel]
                    if not hotel_data.empty:
                        summary_data.append({
                            "Hotel": hotel,
                            "Total Rooms Forecasted": hotel_data['forecast_value'].sum(),
                            "Avg per Day": hotel_data['forecast_value'].mean(),
                            "Latest Update": hotel_data['forecast_date'].max().strftime("%Y-%m-%d")
                        })
                
                if summary_data:
                    df_summary = pd.DataFrame(summary_data)
                    st.dataframe(df_summary, use_container_width=True, hide_index=True)
            else:
                st.info("No forecast data available")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    with tab2:
        st.subheader("Select Hotel for Detailed View")
        
        try:
            hotels_response = supabase.table("hotels").select("name").eq("is_active", True).execute()
            hotels = [h['name'] for h in hotels_response.data] if hotels_response.data else []
            
            selected_hotel = st.selectbox("Hotel", hotels)
            
            if selected_hotel:
                show_room_forecast_dashboard(selected_hotel)
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
