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
    """Display inventory analysis for a specific hotel"""
    st.title("📦 Warehouse Inventory Analysis")
    
    inventory = get_warehouse_inventory(hotel_name)
    
    if inventory.empty:
        st.info(f"No inventory data available for {hotel_name}")
        return
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 By Category", "💰 Valuation", "📋 Details"])
    
    with tab1:
        st.subheader("Inventory Overview")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_items = len(inventory)
            st.metric("Total Items Tracked", total_items)
        
        with col2:
            categories = inventory['category'].nunique()
            st.metric("Categories", categories)
        
        with col3:
            warehouses = inventory['warehouse'].nunique()
            st.metric("Warehouses", warehouses)
        
        with col4:
            total_balance_value = inventory['balance_value'].sum()
            st.metric("Total Balance Value", f"€{total_balance_value:,.2f}")
        
        st.divider()
        
        # Warehouse breakdown
        st.subheader("Inventory by Warehouse")
        
        warehouse_data = inventory.groupby('warehouse').agg({
            'balance_value': 'sum',
            'purchases_value': 'sum',
            'outflow_value': 'sum',
            'item_name': 'count'
        }).reset_index()
        
        warehouse_data.columns = ['Warehouse', 'Balance Value', 'Purchases', 'Outflow', 'Item Count']
        
        st.dataframe(warehouse_data, use_container_width=True, hide_index=True)
        
        # Pie chart: Distribution by warehouse
        fig = px.pie(
            warehouse_data,
            values='Balance Value',
            names='Warehouse',
            title='Inventory Distribution by Warehouse'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Inventory by Category")
        
        category_data = inventory.groupby('category').agg({
            'balance_value': 'sum',
            'purchases_value': 'sum',
            'outflow_value': 'sum',
            'item_name': 'count'
        }).reset_index()
        
        category_data.columns = ['Category', 'Balance Value', 'Purchases', 'Outflow', 'Item Count']
        category_data = category_data.sort_values('Balance Value', ascending=False)
        
        st.dataframe(category_data, use_container_width=True, hide_index=True)
        
        # Bar chart: Top categories by value
        fig = px.bar(
            category_data.head(10),
            x='Category',
            y='Balance Value',
            title='Top 10 Categories by Inventory Value',
            labels={'Balance Value': 'Value (€)'},
            color='Balance Value',
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Movement analysis
        st.subheader("Category Movement Analysis")
        
        movement_data = category_data[['Category', 'Purchases', 'Outflow', 'Balance Value']].head(10)
        
        fig = go.Figure(data=[
            go.Bar(name='Purchases', x=movement_data['Category'], y=movement_data['Purchases']),
            go.Bar(name='Outflow', x=movement_data['Category'], y=movement_data['Outflow']),
        ])
        
        fig.update_layout(
            title='Purchases vs Outflow by Category (Top 10)',
            xaxis_title='Category',
            yaxis_title='Value (€)',
            barmode='group',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Inventory Valuation Analysis")
        
        # Total valuations
        col1, col2, col3 = st.columns(3)
        
        total_balance = inventory['balance_value'].sum()
        total_purchases = inventory['purchases_value'].sum()
        total_outflow = inventory['outflow_value'].sum()
        
        with col1:
            st.metric("Total Balance Value", f"€{total_balance:,.2f}")
        
        with col2:
            st.metric("Total Purchases", f"€{total_purchases:,.2f}")
        
        with col3:
            st.metric("Total Outflow", f"€{total_outflow:,.2f}")
        
        st.divider()
        
        # Sankey-like visualization: flow analysis
        st.subheader("Inventory Flow")
        
        flow_data = {
            'Metric': ['Purchases', 'Current Balance', 'Outflow'],
            'Value': [total_purchases, total_balance, total_outflow],
            'Color': ['green', 'blue', 'red']
        }
        
        fig = px.bar(
            flow_data,
            x='Metric',
            y='Value',
            color='Metric',
            color_discrete_map={'Purchases': 'green', 'Current Balance': 'blue', 'Outflow': 'red'},
            title='Inventory Flow Summary'
        )
        
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("Detailed Inventory List")
        
        # Display options
        col1, col2 = st.columns(2)
        
        with col1:
            selected_warehouse = st.selectbox(
                "Filter by Warehouse",
                ["All"] + inventory['warehouse'].unique().tolist()
            )
        
        with col2:
            selected_category = st.selectbox(
                "Filter by Category",
                ["All"] + inventory['category'].unique().tolist()
            )
        
        # Apply filters
        filtered = inventory.copy()
        
        if selected_warehouse != "All":
            filtered = filtered[filtered['warehouse'] == selected_warehouse]
        
        if selected_category != "All":
            filtered = filtered[filtered['category'] == selected_category]
        
        # Display table
        display_cols = ['warehouse', 'category', 'item_name', 'balance_value', 'purchases_value', 'outflow_value', 'source_file']
        
        df_display = filtered[display_cols].copy()
        df_display.columns = ['Warehouse', 'Category', 'Item', 'Balance Value', 'Purchases', 'Outflow', 'Source']
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Download option
        csv = df_display.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"inventory_{hotel_name}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

def show_group_inventory_analysis():
    """Display inventory analysis for all hotels"""
    st.title("📦 Group Inventory Analysis")
    
    tab1, tab2, tab3 = st.tabs(["📊 Group Overview", "🏨 By Hotel", "🏢 By Warehouse"])
    
    with tab1:
        st.subheader("All Hotels Inventory Summary")
        
        inventory = get_all_hotels_inventory()
        
        if inventory.empty:
            st.info("No inventory data available")
            return
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Hotels", inventory['hotel_name'].nunique())
        
        with col2:
            st.metric("Total Items", len(inventory))
        
        with col3:
            st.metric("Total Warehouses", inventory['warehouse'].nunique())
        
        with col4:
            total_value = inventory['balance_value'].sum()
            st.metric("Total Inventory Value", f"€{total_value:,.2f}")
        
        st.divider()
        
        # Hotels ranking
        st.subheader("Inventory Value by Hotel")
        
        hotel_data = inventory.groupby('hotel_name').agg({
            'balance_value': 'sum',
            'purchases_value': 'sum',
            'outflow_value': 'sum',
            'item_name': 'count'
        }).reset_index()
        
        hotel_data.columns = ['Hotel', 'Balance Value', 'Purchases', 'Outflow', 'Item Count']
        hotel_data = hotel_data.sort_values('Balance Value', ascending=False)
        
        st.dataframe(hotel_data, use_container_width=True, hide_index=True)
        
        # Chart
        fig = px.bar(
            hotel_data,
            x='Hotel',
            y='Balance Value',
            title='Inventory Balance Value by Hotel',
            color='Balance Value',
            color_continuous_scale='Blues'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Select Hotel for Detailed View")
        
        inventory = get_all_hotels_inventory()
        
        if inventory.empty:
            st.info("No inventory data available")
            return
        
        hotels = inventory['hotel_name'].unique().tolist()
        selected_hotel = st.selectbox("Hotel", sorted(hotels))
        
        if selected_hotel:
            show_inventory_dashboard(selected_hotel)
    
    with tab3:
        st.subheader("Inventory by Warehouse (All Hotels)")
        
        inventory = get_all_hotels_inventory()
        
        if inventory.empty:
            st.info("No inventory data available")
            return
        
        warehouse_data = inventory.groupby(['warehouse', 'hotel_name']).agg({
            'balance_value': 'sum',
            'item_name': 'count'
        }).reset_index()
        
        warehouse_data.columns = ['Warehouse', 'Hotel', 'Balance Value', 'Item Count']
        
        st.dataframe(warehouse_data, use_container_width=True, hide_index=True)
        
        # Visualization
        fig = px.sunburst(
            warehouse_data,
            labels=warehouse_data['Warehouse'],
            parents=warehouse_data['Hotel'],
            values=warehouse_data['Balance Value'],
            title='Inventory Hierarchy: Hotels → Warehouses',
            color='Balance Value',
            color_continuous_scale='RdYlGn'
        )
        
        st.plotly_chart(fig, use_container_width=True)
