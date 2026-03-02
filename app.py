"""
COSMHOTEL BI Dashboard - Supabase Backend
Main Streamlit Application
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from auth import check_password, login_page, logout, show_user_info
from config import HOTELS, GREEK_MONTHS
from supabase_client import (
    get_room_forecast,
    get_daily_operations,
    get_warehouse_inventory,
    get_financial_costs,
    get_revenue_accounts,
    get_financial_accounts,
    get_audit_log,
    insert_audit_log
)
from json_handlers import process_json_file
import json

# Page Configuration
st.set_page_config(
    page_title="COSMHOTEL BI",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .success { color: #00D96F; }
    .error { color: #FF4757; }
    .warning { color: #FFA502; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False


# ============================================================================
# LOGIN PAGE
# ============================================================================

if not check_password():
    login_page()
    st.stop()


# ============================================================================
# MAIN APPLICATION
# ============================================================================

# Sidebar
with st.sidebar:
    st.title("🏨 COSMHOTEL BI")
    show_user_info()
    
    st.divider()
    
    # Navigation
    page = st.radio(
        "📊 Navigation",
        ["Dashboard", "Forecasts", "Warehouse", "Payroll", "Revenue", "Accounts", "Admin", "Audit Log"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    if st.button("🔓 Logout", use_container_width=True):
        logout()


# ============================================================================
# DASHBOARD PAGE
# ============================================================================

if page == "Dashboard":
    st.title("📊 Dashboard Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        forecasts = get_room_forecast(st.session_state.hotel_name)
        st.metric("🔮 Room Forecasts", len(forecasts))
    
    with col2:
        warehouse = get_warehouse_inventory(st.session_state.hotel_name)
        total_value = sum(item.get("balance_value", 0) for item in warehouse if item.get("balance_value"))
        st.metric("📦 Warehouse Items", len(warehouse))
    
    with col3:
        costs = get_financial_costs(st.session_state.hotel_name)
        total_costs = sum(item.get("amount", 0) for item in costs if item.get("amount"))
        st.metric("💼 Cost Records", len(costs))
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Revenue Overview")
        revenue_data = get_revenue_accounts(st.session_state.hotel_name)
        if revenue_data:
            df_revenue = pd.DataFrame(revenue_data)
            fig = px.bar(df_revenue, x="month", y="gross", title="Monthly Revenue")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No revenue data available")
    
    with col2:
        st.subheader("📦 Warehouse Balance")
        if warehouse:
            df_warehouse = pd.DataFrame(warehouse)
            fig = px.pie(df_warehouse, values="balance_value", names="category", title="Inventory Distribution")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No warehouse data available")


# ============================================================================
# FORECASTS PAGE
# ============================================================================

elif page == "Forecasts":
    st.title("🔮 Room Forecasts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_month = st.selectbox("Select Month", range(1, 13), format_func=lambda x: GREEK_MONTHS[x])
    
    with col2:
        selected_year = st.number_input("Select Year", value=2026, min_value=2020, max_value=2030)
    
    forecasts = get_room_forecast(st.session_state.hotel_name, selected_month, selected_year)
    
    if forecasts:
        df_forecasts = pd.DataFrame(forecasts)
        st.dataframe(df_forecasts, use_container_width=True)
        
        st.metric("Total Records", len(df_forecasts))
    else:
        st.info("No forecast data available for selected period")


# ============================================================================
# WAREHOUSE PAGE
# ============================================================================

elif page == "Warehouse":
    st.title("📦 Warehouse Inventory")
    
    warehouse = get_warehouse_inventory(st.session_state.hotel_name)
    
    if warehouse:
        df_warehouse = pd.DataFrame(warehouse)
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_items = len(df_warehouse)
            st.metric("Total Items", total_items)
        
        with col2:
            total_balance = df_warehouse["balance_value"].sum()
            st.metric("Total Balance Value", f"€{total_balance:,.2f}")
        
        with col3:
            total_purchases = df_warehouse["purchases_value"].sum()
            st.metric("Total Purchases", f"€{total_purchases:,.2f}")
        
        st.divider()
        
        # Data table
        st.subheader("Inventory Details")
        st.dataframe(df_warehouse, use_container_width=True)
    else:
        st.info("No warehouse data available")


# ============================================================================
# PAYROLL PAGE
# ============================================================================

elif page == "Payroll":
    st.title("💼 Payroll & Costs")
    
    costs = get_financial_costs(st.session_state.hotel_name)
    
    if costs:
        df_costs = pd.DataFrame(costs)
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_records = len(df_costs)
            st.metric("Total Records", total_records)
        
        with col2:
            total_amount = df_costs["amount"].sum()
            st.metric("Total Amount", f"€{total_amount:,.2f}")
        
        with col3:
            unique_employees = df_costs["employee_name"].nunique()
            st.metric("Unique Employees", unique_employees)
        
        st.divider()
        
        # Cost breakdown
        st.subheader("Cost Breakdown by Type")
        cost_by_type = df_costs.groupby("cost_type")["amount"].sum()
        fig = px.bar(cost_by_type, title="Costs by Type")
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Data table
        st.subheader("Cost Details")
        st.dataframe(df_costs, use_container_width=True)
    else:
        st.info("No payroll data available")


# ============================================================================
# REVENUE PAGE
# ============================================================================

elif page == "Revenue":
    st.title("💰 Revenue Accounts")
    
    revenue = get_revenue_accounts(st.session_state.hotel_name)
    
    if revenue:
        df_revenue = pd.DataFrame(revenue)
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_gross = df_revenue["gross"].sum()
            st.metric("Total Gross Revenue", f"€{total_gross:,.2f}")
        
        with col2:
            total_net = df_revenue["net"].sum()
            st.metric("Total Net Revenue", f"€{total_net:,.2f}")
        
        with col3:
            total_vat = df_revenue["vat"].sum()
            st.metric("Total VAT", f"€{total_vat:,.2f}")
        
        st.divider()
        
        # Monthly trend
        st.subheader("Monthly Revenue Trend")
        revenue_by_month = df_revenue.groupby("month")["gross"].sum()
        fig = px.line(revenue_by_month, title="Revenue by Month", markers=True)
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Data table
        st.subheader("Revenue Details")
        st.dataframe(df_revenue, use_container_width=True)
    else:
        st.info("No revenue data available")


# ============================================================================
# ACCOUNTS PAGE
# ============================================================================

elif page == "Accounts":
    st.title("📋 Chart of Accounts")
    
    accounts = get_financial_accounts(st.session_state.hotel_name)
    
    if accounts:
        df_accounts = pd.DataFrame(accounts)
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_debits = df_accounts["debit_amount"].sum()
            st.metric("Total Debits", f"€{total_debits:,.2f}")
        
        with col2:
            total_credits = df_accounts["credit_amount"].sum()
            st.metric("Total Credits", f"€{total_credits:,.2f}")
        
        with col3:
            total_accounts = len(df_accounts)
            st.metric("Total Accounts", total_accounts)
        
        st.divider()
        
        # Data table
        st.subheader("Account Details")
        st.dataframe(df_accounts, use_container_width=True)
    else:
        st.info("No account data available")


# ============================================================================
# ADMIN PAGE
# ============================================================================

elif page == "Admin":
    st.title("⚙️ Admin Panel")
    
    if st.session_state.user_role != "admin":
        st.error("❌ Access denied. Admin only.")
    else:
        st.subheader("📁 Upload JSON Data")
        
        uploaded_file = st.file_uploader("Choose a JSON file", type="json")
        
        if uploaded_file is not None:
            try:
                file_content = uploaded_file.read()
                filename = uploaded_file.name
                
                with st.spinner("Processing file..."):
                    inserted, message = process_json_file(
                        file_content,
                        filename,
                        st.session_state.hotel_name
                    )
                
                # Log the action
                insert_audit_log(
                    hotel_name=st.session_state.hotel_name,
                    user_email=st.session_state.user_email,
                    action="File Upload",
                    file_name=filename,
                    records_count=inserted,
                    status="success" if inserted > 0 else "error",
                    error_message=message if inserted == 0 else None
                )
                
                if inserted > 0:
                    st.success(f"✅ {message}")
                else:
                    st.error(f"❌ {message}")
            
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
        
        st.divider()
        
        st.subheader("📊 Data Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            forecasts = get_room_forecast(st.session_state.hotel_name)
            st.metric("Forecasts", len(forecasts))
        
        with col2:
            warehouse = get_warehouse_inventory(st.session_state.hotel_name)
            st.metric("Warehouse", len(warehouse))
        
        with col3:
            costs = get_financial_costs(st.session_state.hotel_name)
            st.metric("Costs", len(costs))
        
        with col4:
            revenue = get_revenue_accounts(st.session_state.hotel_name)
            st.metric("Revenue", len(revenue))


# ============================================================================
# AUDIT LOG PAGE
# ============================================================================

elif page == "Audit Log":
    st.title("📂 Audit Log")
    
    audit = get_audit_log(st.session_state.hotel_name, limit=100)
    
    if audit:
        df_audit = pd.DataFrame(audit)
        
        st.subheader("File Upload History")
        st.dataframe(df_audit, use_container_width=True)
    else:
        st.info("No audit log entries available")


# Footer
st.divider()
st.caption(f"COSMHOTEL BI • Hotel: {st.session_state.hotel_name} • Role: {st.session_state.user_role.upper()}")
