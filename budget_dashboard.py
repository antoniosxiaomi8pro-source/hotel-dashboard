"""
Budget & Forecasting Dashboard
Displays budget planning, variance analysis and forecasts
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from supabase_client import supabase

def get_hotel_revenue(hotel_name: str) -> pd.DataFrame:
    """Get revenue data for budget comparison"""
    try:
        response = supabase.table("revenue_accounts").select("*").eq("hotel_name", hotel_name).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching revenue: {str(e)}")
        return pd.DataFrame()

def get_all_hotels_revenue() -> pd.DataFrame:
    """Get revenue data for all hotels"""
    try:
        response = supabase.table("revenue_accounts").select("*").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching revenue: {str(e)}")
        return pd.DataFrame()

def show_budget_dashboard(hotel_name: str):
    """Display budget analysis for a specific hotel"""
    st.title(f"📊 {hotel_name} - Budget & Forecasting")
    
    revenue = get_hotel_revenue(hotel_name)
    
    if revenue.empty:
        st.info(f"No revenue data available for budget analysis")
        return
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["💰 Budget Overview", "📈 Variance Analysis", "🔮 Forecast"])
    
    with tab1:
        st.subheader("Budget Summary")
        
        # Calculate budgets based on historical data
        # Use average as simple budget
        avg_monthly_revenue = revenue['net'].mean()
        total_actual = revenue['net'].sum()
        months = revenue['month'].nunique()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Months Tracked", months)
        
        with col2:
            st.metric("Total Revenue", f"€{total_actual:,.2f}")
        
        with col3:
            st.metric("Average Monthly", f"€{avg_monthly_revenue:,.2f}")
        
        with col4:
            budget = avg_monthly_revenue * 12
            st.metric("Annual Budget", f"€{budget:,.2f}")
        
        st.divider()
        
        # Monthly budget vs actual
        st.subheader("Monthly Budget vs Actual")
        
        monthly = revenue.groupby('month')['net'].sum().reset_index()
        monthly['budget'] = avg_monthly_revenue
        monthly['variance'] = monthly['net'] - monthly['budget']
        monthly['variance_pct'] = (monthly['variance'] / monthly['budget'] * 100).round(1)
        
        st.dataframe(
            monthly[['month', 'budget', 'net', 'variance', 'variance_pct']],
            use_container_width=True,
            hide_index=True
        )
        
        # Chart
        fig = go.Figure(data=[
            go.Bar(name='Budget', x=monthly['month'], y=monthly['budget']),
            go.Bar(name='Actual', x=monthly['month'], y=monthly['net']),
        ])
        
        fig.update_layout(
            title='Monthly Budget vs Actual',
            xaxis_title='Month',
            yaxis_title='Revenue (€)',
            barmode='group',
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Variance Analysis")
        
        monthly = revenue.groupby('month')['net'].sum().reset_index()
        monthly['budget'] = avg_monthly_revenue
        monthly['variance'] = monthly['net'] - monthly['budget']
        monthly['variance_pct'] = (monthly['variance'] / monthly['budget'] * 100).round(1)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            favorable = (monthly['variance'] > 0).sum()
            st.metric("Favorable Months", favorable)
        
        with col2:
            unfavorable = (monthly['variance'] < 0).sum()
            st.metric("Unfavorable Months", unfavorable)
        
        with col3:
            avg_variance = monthly['variance_pct'].mean()
            st.metric("Avg Variance %", f"{avg_variance:.1f}%")
        
        st.divider()
        
        # Variance chart
        colors = ['green' if x > 0 else 'red' for x in monthly['variance']]
        
        fig = px.bar(
            monthly,
            x='month',
            y='variance',
            title='Revenue Variance from Budget',
            color=monthly['variance'],
            color_continuous_scale='RdYlGn',
            labels={'month': 'Month', 'variance': 'Variance (€)'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Details
        st.subheader("Variance Details")
        st.dataframe(monthly, use_container_width=True, hide_index=True)
    
    with tab3:
        st.subheader("Revenue Forecast")
        
        # Simple trend forecast
        monthly = revenue.groupby('month')['net'].sum().reset_index()
        
        if len(monthly) > 1:
            # Calculate trend
            x = monthly.index.values
            y = monthly['net'].values
            
            # Linear regression
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            
            # Forecast next 3 months
            future_months = len(monthly) + np.arange(1, 4)
            forecast = p(future_months)
            
            # Create forecast data
            forecast_df = pd.DataFrame({
                'month': future_months,
                'revenue': forecast,
                'type': 'Forecast'
            })
            
            historical_df = pd.DataFrame({
                'month': monthly.index + 1,
                'revenue': monthly['net'].values,
                'type': 'Actual'
            })
            
            combined = pd.concat([historical_df, forecast_df], ignore_index=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Current Trend", f"€{monthly['net'].iloc[-1]:,.2f}")
            
            with col2:
                next_month = forecast[0]
                change = ((next_month - monthly['net'].iloc[-1]) / monthly['net'].iloc[-1] * 100)
                st.metric("Next Month Forecast", f"€{next_month:,.2f}", delta=f"{change:.1f}%")
            
            with col3:
                avg_forecast = forecast.mean()
                st.metric("Avg Forecast", f"€{avg_forecast:,.2f}")
            
            st.divider()
            
            # Chart
            fig = px.line(
                combined,
                x='month',
                y='revenue',
                color='type',
                title='Revenue Forecast',
                markers=True,
                labels={'month': 'Month', 'revenue': 'Revenue (€)'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Forecast table
            st.subheader("Forecast Details")
            
            forecast_display = pd.DataFrame({
                'Month': future_months,
                'Forecasted Revenue': [f"€{x:,.2f}" for x in forecast]
            })
            
            st.dataframe(forecast_display, use_container_width=True, hide_index=True)
        else:
            st.info("Insufficient data for forecasting (need at least 2 months)")

def show_group_budget_analysis():
    """Display budget analysis with hotel selection"""
    st.title("📊 Budget & Forecasting")
    
    all_revenue = get_all_hotels_revenue()
    
    if all_revenue.empty:
        st.info("No revenue data available in the system")
        return
    
    hotels = sorted(all_revenue['hotel_name'].unique().tolist())
    
    tab1, tab2 = st.tabs(["📊 Group Overview", "🏨 Hotel Details"])
    
    with tab1:
        st.subheader("Group Budget Summary")
        
        total_revenue = all_revenue['net'].sum()
        st.metric("Total Group Revenue", f"€{total_revenue:,.2f}")
        
        st.divider()
        
        # Budget by hotel
        st.subheader("Revenue by Hotel")
        
        hotel_revenue = all_revenue.groupby('hotel_name')['net'].sum().reset_index()
        hotel_revenue.columns = ['Hotel', 'Revenue']
        hotel_revenue = hotel_revenue.sort_values('Revenue', ascending=False)
        
        st.dataframe(hotel_revenue, use_container_width=True, hide_index=True)
        
        fig = px.pie(
            hotel_revenue,
            values='Revenue',
            names='Hotel',
            title='Revenue Distribution by Hotel'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Select Hotel for Detailed Budget Analysis")
        
        selected_hotel = st.selectbox(
            "🏨 Hotel",
            hotels,
            index=0 if hotels else None
        )
        
        if selected_hotel:
            st.divider()
            show_budget_dashboard(selected_hotel)

import numpy as np
