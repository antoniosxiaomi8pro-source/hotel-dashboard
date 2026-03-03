"""
Monthly Financial Statements Dashboard
Displays comprehensive monthly financial reports
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from supabase_client import supabase

def get_monthly_revenue(hotel_name: str) -> pd.DataFrame:
    """Get monthly revenue data"""
    try:
        response = supabase.table("revenue_accounts").select("*").eq("hotel_name", hotel_name).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching revenue: {str(e)}")
        return pd.DataFrame()

def get_monthly_costs(hotel_name: str) -> pd.DataFrame:
    """Get monthly cost data"""
    try:
        response = supabase.table("financial_costs").select("*").eq("hotel_name", hotel_name).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching costs: {str(e)}")
        return pd.DataFrame()

def get_all_hotels_monthly() -> tuple:
    """Get monthly data for all hotels"""
    try:
        revenue_response = supabase.table("revenue_accounts").select("*").execute()
        costs_response = supabase.table("financial_costs").select("*").execute()
        
        revenue_df = pd.DataFrame(revenue_response.data) if revenue_response.data else pd.DataFrame()
        costs_df = pd.DataFrame(costs_response.data) if costs_response.data else pd.DataFrame()
        
        return revenue_df, costs_df
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()

def show_monthly_statements(hotel_name: str):
    """Display monthly financial statements for a specific hotel"""
    st.title(f"📈 {hotel_name} - Monthly Financial Statements")
    
    revenue = get_monthly_revenue(hotel_name)
    costs = get_monthly_costs(hotel_name)
    
    if revenue.empty and costs.empty:
        st.info(f"No financial data available for {hotel_name}")
        return
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["💰 Revenue", "💸 Costs", "📊 P&L Statement"])
    
    with tab1:
        st.subheader("Monthly Revenue Analysis")
        
        if revenue.empty:
            st.info("No revenue data available")
        else:
            # Summary
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_revenue = revenue['net'].sum()
                st.metric("Total Revenue (Net)", f"€{total_revenue:,.2f}")
            
            with col2:
                total_gross = revenue['gross'].sum()
                st.metric("Total Gross", f"€{total_gross:,.2f}")
            
            with col3:
                total_vat = revenue['vat'].sum()
                st.metric("Total VAT", f"€{total_vat:,.2f}")
            
            with col4:
                avg_monthly = revenue['net'].mean()
                st.metric("Avg Monthly", f"€{avg_monthly:,.2f}")
            
            st.divider()
            
            # Monthly breakdown
            st.subheader("Revenue by Month")
            
            monthly_data = revenue.groupby('month').agg({
                'gross': 'sum',
                'net': 'sum',
                'vat': 'sum'
            }).reset_index()
            
            st.dataframe(monthly_data, use_container_width=True, hide_index=True)
            
            # Chart
            fig = px.line(
                monthly_data,
                x='month',
                y=['gross', 'net'],
                title='Monthly Revenue Trend',
                markers=True,
                labels={'month': 'Month', 'value': 'Revenue (€)'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # By account
            st.subheader("Revenue by Account")
            
            account_data = revenue.groupby('account_name').agg({
                'gross': 'sum',
                'net': 'sum'
            }).reset_index()
            
            account_data = account_data.sort_values('net', ascending=False)
            
            st.dataframe(account_data, use_container_width=True, hide_index=True)
            
            fig = px.bar(
                account_data,
                x='account_name',
                y='net',
                title='Revenue by Account (Net)',
                color='net',
                color_continuous_scale='Greens'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Monthly Cost Analysis")
        
        if costs.empty:
            st.info("No cost data available")
        else:
            total_costs = costs['amount'].sum()
            st.metric("Total Costs", f"€{total_costs:,.2f}")
            
            st.divider()
            
            # By cost type
            st.subheader("Costs by Type")
            
            cost_type_data = costs.groupby('cost_type').agg({
                'amount': 'sum'
            }).reset_index()
            
            cost_type_data = cost_type_data.sort_values('amount', ascending=False)
            
            st.dataframe(cost_type_data, use_container_width=True, hide_index=True)
            
            fig = px.pie(
                cost_type_data,
                values='amount',
                names='cost_type',
                title='Cost Distribution by Type'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # By period
            st.subheader("Costs by Period")
            
            if 'period' in costs.columns:
                period_data = costs.groupby('period').agg({
                    'amount': 'sum'
                }).reset_index()
                
                st.dataframe(period_data, use_container_width=True, hide_index=True)
                
                fig = px.bar(
                    period_data,
                    x='period',
                    y='amount',
                    title='Monthly Costs',
                    color='amount',
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Profit & Loss Summary")
        
        if not revenue.empty:
            total_revenue = revenue['net'].sum()
        else:
            total_revenue = 0
        
        if not costs.empty:
            total_costs = costs['amount'].sum()
        else:
            total_costs = 0
        
        profit = total_revenue - total_costs
        profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Revenue", f"€{total_revenue:,.2f}")
        
        with col2:
            st.metric("Total Costs", f"€{total_costs:,.2f}")
        
        with col3:
            color = "green" if profit > 0 else "red"
            st.metric("Net Profit", f"€{profit:,.2f}", delta=f"{profit_margin:.1f}%", delta_color="off")
        
        with col4:
            st.metric("Profit Margin", f"{profit_margin:.1f}%")
        
        st.divider()
        
        # P&L statement
        st.subheader("P&L Statement")
        
        pl_data = pd.DataFrame({
            'Item': ['Revenue', 'Costs', 'Profit/Loss'],
            'Amount': [total_revenue, total_costs, profit]
        })
        
        st.dataframe(pl_data, use_container_width=True, hide_index=True)
        
        # Visual
        fig = px.bar(
            pl_data,
            x='Item',
            y='Amount',
            title='P&L Overview',
            color='Item',
            color_discrete_map={'Revenue': 'green', 'Costs': 'red', 'Profit/Loss': 'blue'}
        )
        st.plotly_chart(fig, use_container_width=True)

def show_group_monthly_statements():
    """Display monthly statements with hotel selection"""
    st.title("📈 Monthly Financial Statements")
    
    revenue, costs = get_all_hotels_monthly()
    
    if revenue.empty and costs.empty:
        st.info("No financial data available in the system")
        return
    
    hotels = pd.concat([
        revenue['hotel_name'] if not revenue.empty else pd.Series(),
        costs['hotel_name'] if not costs.empty else pd.Series()
    ]).unique().tolist()
    
    hotels = sorted([h for h in hotels if h])
    
    tab1, tab2 = st.tabs(["📊 Group Overview", "🏨 Hotel Details"])
    
    with tab1:
        st.subheader("Group Financial Summary")
        
        if not revenue.empty:
            total_revenue = revenue['net'].sum()
            st.metric("Total Revenue (Net)", f"€{total_revenue:,.2f}")
        
        if not costs.empty:
            total_costs = costs['amount'].sum()
            st.metric("Total Costs", f"€{total_costs:,.2f}")
        
        st.divider()
        
        # Hotel comparison
        st.subheader("Revenue by Hotel")
        
        if not revenue.empty:
            hotel_revenue = revenue.groupby('hotel_name')['net'].sum().reset_index()
            hotel_revenue.columns = ['Hotel', 'Revenue']
            
            st.dataframe(hotel_revenue, use_container_width=True, hide_index=True)
            
            fig = px.bar(
                hotel_revenue,
                x='Hotel',
                y='Revenue',
                title='Total Revenue by Hotel',
                color='Revenue',
                color_continuous_scale='Greens'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Select Hotel for Detailed Statements")
        
        selected_hotel = st.selectbox(
            "🏨 Hotel",
            hotels,
            index=0 if hotels else None
        )
        
        if selected_hotel:
            st.divider()
            show_monthly_statements(selected_hotel)
