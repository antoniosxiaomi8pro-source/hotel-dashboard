"""
Inventory Analysis Dashboard
Displays warehouse inventory status, movements and trends
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from supabase_client import supabase

def get_warehouse_inventory(hotel_name: str) -> pd.DataFrame:
    """Get current warehouse inventory for a hotel"""
    try:
        response = supabase.table("warehouse_inventory").select("*").eq("hotel_name", hotel_name).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching inventory: {str(e)}")
        return pd.DataFrame()

def get_all_hotels_inventory() -> pd.DataFrame:
    """Get warehouse inventory for all hotels"""
    try:
        response = supabase.table("warehouse_inventory").select("*").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching inventory: {str(e)}")
        return pd.DataFrame()

def show_inventory_dashboard(hotel_name: str):
    """Display detailed inventory analysis for a specific hotel"""
    st.title(f"📦 {hotel_name} - Inventory Analysis")
    
    inventory = get_warehouse_inventory(hotel_name)
    
    if inventory.empty:
        st.info(f"No inventory data available for {hotel_name}")
        return
    
    # Tabs for detailed analysis
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 By Category", "💰 Valuation", "📋 Details"])
    
    with tab1:
        st.subheader("Inventory Overview")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_items = len(inventory)
            st.metric("Total Items", total_items)
        
        with col2:
            categories = inventory['category'].nunique()
            st.metric("Categories", categories)
        
        with col3:
            warehouses = inventory['warehouse'].nunique()
            st.metric("Warehouses", warehouses)
        
        with col4:
            total_balance_value = inventory['balance_value'].sum()
            st.metric("Balance Value", f"€{total_balance_value:,.2f}")
        
        st.divider()
        
        # Warehouse breakdown
        st.subheader("By Warehouse")
        
        warehouse_data = inventory.groupby('warehouse').agg({
            'balance_value': 'sum',
            'purchases_value': 'sum',
            'outflow_value': 'sum',
            'item_name': 'count'
        }).reset_index()
        
        warehouse_data.columns = ['Warehouse', 'Balance', 'Purchases', 'Outflow', 'Items']
        
        st.dataframe(warehouse_data, use_container_width=True, hide_index=True)
        
        # Pie chart
        fig = px.pie(
            warehouse_data,
            values='Balance',
            names='Warehouse',
            title='Inventory Distribution by Warehouse'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("By Category")
        
        category_data = inventory.groupby('category').agg({
            'balance_value': 'sum',
            'purchases_value': 'sum',
            'outflow_value': 'sum',
            'item_name': 'count'
        }).reset_index()
        
        category_data.columns = ['Category', 'Balance', 'Purchases', 'Outflow', 'Items']
        category_data = category_data.sort_values('Balance', ascending=False)
        
        st.dataframe(category_data, use_container_width=True, hide_index=True)
        
        # Top categories chart
        fig = px.bar(
            category_data.head(10),
            x='Category',
            y='Balance',
            title='Top 10 Categories by Value',
            color='Balance',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Movement analysis
        st.subheader("Movement Analysis (Top 10)")
        
        fig = go.Figure(data=[
            go.Bar(name='Purchases', x=category_data.head(10)['Category'], y=category_data.head(10)['Purchases']),
            go.Bar(name='Outflow', x=category_data.head(10)['Category'], y=category_data.head(10)['Outflow']),
        ])
        
        fig.update_layout(
            title='Purchases vs Outflow',
            xaxis_title='Category',
            yaxis_title='Value (€)',
            barmode='group',
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Valuation Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        total_balance = inventory['balance_value'].sum()
        total_purchases = inventory['purchases_value'].sum()
        total_outflow = inventory['outflow_value'].sum()
        
        with col1:
            st.metric("Balance Value", f"€{total_balance:,.2f}")
        
        with col2:
            st.metric("Purchases", f"€{total_purchases:,.2f}")
        
        with col3:
            st.metric("Outflow", f"€{total_outflow:,.2f}")
        
        st.divider()
        
        # Flow visualization
        flow_data = pd.DataFrame({
            'Metric': ['Purchases', 'Current Balance', 'Outflow'],
            'Value': [total_purchases, total_balance, total_outflow]
        })
        
        fig = px.bar(
            flow_data,
            x='Metric',
            y='Value',
            title='Inventory Flow Summary',
            color='Metric',
            color_discrete_map={'Purchases': 'green', 'Current Balance': 'blue', 'Outflow': 'red'}
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("Detailed Inventory List")
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_warehouse = st.selectbox(
                "Filter by Warehouse",
                ["All"] + inventory['warehouse'].unique().tolist(),
                key="inv_warehouse"
            )
        
        with col2:
            selected_category = st.selectbox(
                "Filter by Category",
                ["All"] + inventory['category'].unique().tolist(),
                key="inv_category"
            )
        
        # Filter
        filtered = inventory.copy()
        
        if selected_warehouse != "All":
            filtered = filtered[filtered['warehouse'] == selected_warehouse]
        
        if selected_category != "All":
            filtered = filtered[filtered['category'] == selected_category]
        
        # Display
        display_cols = ['warehouse', 'category', 'item_name', 'balance_value', 'purchases_value', 'outflow_value', 'source_file']
        df_display = filtered[display_cols].copy()
        df_display.columns = ['Warehouse', 'Category', 'Item', 'Balance', 'Purchases', 'Outflow', 'Source']
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Download
        csv = df_display.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"inventory_{hotel_name}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

def show_group_inventory_analysis():
    """Display inventory analysis with hotel selection (like Room Forecast)"""
    st.title("📦 Inventory Analysis")
    
    # Get all inventory data
    all_inventory = get_all_hotels_inventory()
    
    if all_inventory.empty:
        st.info("No inventory data available in the system")
        return
    
    # Get list of hotels with inventory data
    hotels_with_inventory = sorted(all_inventory['hotel_name'].unique().tolist())
    
    # Tabs: Overview and By Hotel
    tab1, tab2 = st.tabs(["📊 Group Overview", "🏨 Hotel Details"])
    
    with tab1:
        st.subheader("Group Inventory Summary")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Hotels", all_inventory['hotel_name'].nunique())
        
        with col2:
            st.metric("Total Items", len(all_inventory))
        
        with col3:
            st.metric("Warehouses", all_inventory['warehouse'].nunique())
        
        with col4:
            total_value = all_inventory['balance_value'].sum()
            st.metric("Total Value", f"€{total_value:,.2f}")
        
        st.divider()
        
        # Hotels ranking
        st.subheader("Inventory by Hotel")
        
        hotel_data = all_inventory.groupby('hotel_name').agg({
            'balance_value': 'sum',
            'purchases_value': 'sum',
            'outflow_value': 'sum',
            'item_name': 'count'
        }).reset_index()
        
        hotel_data.columns = ['Hotel', 'Balance', 'Purchases', 'Outflow', 'Items']
        hotel_data = hotel_data.sort_values('Balance', ascending=False)
        
        st.dataframe(hotel_data, use_container_width=True, hide_index=True)
        
        # Chart
        fig = px.bar(
            hotel_data,
            x='Hotel',
            y='Balance',
            title='Inventory Value by Hotel',
            color='Balance',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Select Hotel for Detailed Analysis")
        
        selected_hotel = st.selectbox(
            "🏨 Hotel",
            hotels_with_inventory,
            index=0
        )
        
        if selected_hotel:
            st.divider()
            show_inventory_dashboard(selected_hotel)
