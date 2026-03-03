"""
Payroll Analysis Dashboard
Displays employee payroll and labor cost analysis
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from supabase_client import supabase

def get_hotel_payroll(hotel_name: str) -> pd.DataFrame:
    """Get payroll data for a hotel"""
    try:
        response = supabase.table("financial_costs").select("*").eq("hotel_name", hotel_name).eq("cost_type", "Payroll").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching payroll: {str(e)}")
        return pd.DataFrame()

def get_all_hotels_payroll() -> pd.DataFrame:
    """Get payroll data for all hotels"""
    try:
        response = supabase.table("financial_costs").select("*").eq("cost_type", "Payroll").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching payroll: {str(e)}")
        return pd.DataFrame()

def show_payroll_dashboard(hotel_name: str):
    """Display detailed payroll analysis for a specific hotel"""
    st.title(f"💼 {hotel_name} - Payroll Analysis")
    
    payroll = get_hotel_payroll(hotel_name)
    
    if payroll.empty:
        st.info(f"No payroll data available for {hotel_name}")
        return
    
    # Tabs for detailed analysis
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "👥 By Employee", "📈 Trends", "📋 Details"])
    
    with tab1:
        st.subheader("Payroll Overview")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_employees = payroll['employee_name'].nunique()
            st.metric("Total Employees", total_employees)
        
        with col2:
            total_payroll = payroll['amount'].sum()
            st.metric("Total Payroll", f"€{total_payroll:,.2f}")
        
        with col3:
            avg_salary = payroll['amount'].mean()
            st.metric("Avg Salary", f"€{avg_salary:,.2f}")
        
        with col4:
            periods = payroll['period'].nunique()
            st.metric("Periods", periods)
        
        st.divider()
        
        # Payroll by period
        st.subheader("Payroll by Period")
        
        period_data = payroll.groupby('period').agg({
            'amount': 'sum',
            'employee_name': 'count'
        }).reset_index()
        
        period_data.columns = ['Period', 'Amount', 'Employees']
        
        st.dataframe(period_data, use_container_width=True, hide_index=True)
        
        # Chart
        fig = px.bar(
            period_data,
            x='Period',
            y='Amount',
            title='Payroll by Period',
            color='Amount',
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Employee Payroll Analysis")
        
        employee_data = payroll.groupby('employee_name').agg({
            'amount': 'sum',
            'period': 'count'
        }).reset_index()
        
        employee_data.columns = ['Employee', 'Total Salary', 'Periods']
        employee_data = employee_data.sort_values('Total Salary', ascending=False)
        
        st.dataframe(employee_data, use_container_width=True, hide_index=True)
        
        # Top employees chart
        fig = px.bar(
            employee_data.head(15),
            x='Employee',
            y='Total Salary',
            title='Top 15 Employees by Salary',
            color='Total Salary',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(height=500, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Salary distribution
        st.subheader("Salary Distribution")
        
        fig = px.histogram(
            employee_data,
            x='Total Salary',
            nbins=10,
            title='Salary Distribution',
            labels={'Total Salary': 'Salary (€)'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Payroll Trends")
        
        # Sort by period for time series
        payroll_sorted = payroll.sort_values('period')
        
        trend_data = payroll_sorted.groupby('period').agg({
            'amount': 'sum',
            'employee_name': 'count'
        }).reset_index()
        
        trend_data.columns = ['Period', 'Total Payroll', 'Employee Count']
        
        # Line chart
        fig = px.line(
            trend_data,
            x='Period',
            y='Total Payroll',
            title='Payroll Trend Over Time',
            markers=True,
            labels={'Total Payroll': 'Total Payroll (€)'}
        )
        
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Monthly comparison
        st.subheader("Monthly Statistics")
        
        st.dataframe(trend_data, use_container_width=True, hide_index=True)
        
        # Calculate YoY or Month-over-Month if applicable
        if len(trend_data) > 1:
            trend_data['Change %'] = trend_data['Total Payroll'].pct_change() * 100
            
            st.subheader("Month-over-Month Change")
            st.dataframe(
                trend_data[['Period', 'Total Payroll', 'Change %']],
                use_container_width=True,
                hide_index=True
            )
    
    with tab4:
        st.subheader("Detailed Payroll List")
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_employee = st.selectbox(
                "Filter by Employee",
                ["All"] + sorted(payroll['employee_name'].unique().tolist()),
                key="payroll_employee"
            )
        
        with col2:
            selected_period = st.selectbox(
                "Filter by Period",
                ["All"] + sorted(payroll['period'].unique().tolist()),
                key="payroll_period"
            )
        
        # Filter
        filtered = payroll.copy()
        
        if selected_employee != "All":
            filtered = filtered[filtered['employee_name'] == selected_employee]
        
        if selected_period != "All":
            filtered = filtered[filtered['period'] == selected_period]
        
        # Display
        display_cols = ['employee_name', 'description', 'amount', 'period', 'year', 'source_file']
        df_display = filtered[display_cols].copy()
        df_display.columns = ['Employee', 'Description', 'Amount', 'Period', 'Year', 'Source']
        df_display = df_display.sort_values('Amount', ascending=False)
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Download
        csv = df_display.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"payroll_{hotel_name}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

def show_group_payroll_analysis():
    """Display payroll analysis with hotel selection (like Room Forecast)"""
    st.title("💼 Payroll Analysis")
    
    # Get all payroll data
    all_payroll = get_all_hotels_payroll()
    
    if all_payroll.empty:
        st.info("No payroll data available in the system")
        return
    
    # Get list of hotels with payroll data
    hotels_with_payroll = sorted(all_payroll['hotel_name'].unique().tolist())
    
    # Tabs: Overview and By Hotel
    tab1, tab2 = st.tabs(["📊 Group Overview", "🏨 Hotel Details"])
    
    with tab1:
        st.subheader("Group Payroll Summary")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Hotels", all_payroll['hotel_name'].nunique())
        
        with col2:
            st.metric("Total Employees", all_payroll['employee_name'].nunique())
        
        with col3:
            total_payroll = all_payroll['amount'].sum()
            st.metric("Total Payroll", f"€{total_payroll:,.2f}")
        
        with col4:
            avg_salary = all_payroll['amount'].mean()
            st.metric("Avg Salary", f"€{avg_salary:,.2f}")
        
        st.divider()
        
        # Hotels payroll ranking
        st.subheader("Payroll by Hotel")
        
        hotel_data = all_payroll.groupby('hotel_name').agg({
            'amount': 'sum',
            'employee_name': 'nunique'
        }).reset_index()
        
        hotel_data.columns = ['Hotel', 'Total Payroll', 'Employees']
        hotel_data = hotel_data.sort_values('Total Payroll', ascending=False)
        
        st.dataframe(hotel_data, use_container_width=True, hide_index=True)
        
        # Chart
        fig = px.bar(
            hotel_data,
            x='Hotel',
            y='Total Payroll',
            title='Payroll by Hotel',
            color='Total Payroll',
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Top employees across all hotels
        st.subheader("Top 10 Employees (All Hotels)")
        
        top_employees = all_payroll.groupby('employee_name').agg({
            'amount': 'sum',
            'hotel_name': 'first'
        }).reset_index()
        
        top_employees.columns = ['Employee', 'Total Salary', 'Hotel']
        top_employees = top_employees.sort_values('Total Salary', ascending=False).head(10)
        
        st.dataframe(top_employees, use_container_width=True, hide_index=True)
    
    with tab2:
        st.subheader("Select Hotel for Detailed Analysis")
        
        selected_hotel = st.selectbox(
            "🏨 Hotel",
            hotels_with_payroll,
            index=0
        )
        
        if selected_hotel:
            st.divider()
            show_payroll_dashboard(selected_hotel)
