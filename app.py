"""
COSMHOTEL GROUP BI Dashboard - Supabase Backend
Main Streamlit Application with Advanced Financial Analytics
Multi-property Group Reporting
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from auth import check_password, login_page, logout, show_user_info
from config import HOTELS, GREEK_MONTHS, HOTEL_PROPERTIES
from financial_dashboards import (
    show_pl_dashboard,
    show_budget_vs_actual,
    show_revenue_breakdown,
    show_cost_analysis,
    show_kpi_dashboard,
    show_multi_hotel_comparison
)
from group_dashboards import (
    render_group_overview,
    render_group_kpis,
    render_hotel_comparison,
    render_revenue_analysis,
    render_occupancy_trends,
)
from room_forecast_dashboard import show_room_forecast_dashboard, show_group_room_forecast
from inventory_dashboard import show_inventory_dashboard, show_group_inventory_analysis
from payroll_dashboard import show_payroll_dashboard, show_group_payroll_analysis
from accounts_dashboard import show_accounts_dashboard, show_group_accounts_analysis
from monthly_statements_dashboard import show_monthly_statements, show_group_monthly_statements
from budget_dashboard import show_budget_dashboard, show_group_budget_analysis
from upload_manager import render_upload_interface
from hotels_management import render_hotels_management

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
    st.session_state.user = None
    st.session_state.user_id = None
    st.session_state.user_email = None
    st.session_state.user_role = None
    st.session_state.hotel_name = "All Hotels"


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
    if st.session_state.user_role == "group_director":
        # Group-level navigation for directors
        page = st.radio(
            "📊 Navigation",
            [
                "Group Overview",
                "Group KPIs",
                "Hotel Comparison",
                "Revenue Analysis",
                "Occupancy Trends",
                "📅 Room Forecast",
                "📦 Inventory",
                "💼 Payroll",
                "Hotel Dashboard",
                "P&L Statement",
                "Budget Analysis",
                "📤 Upload Data",
                "Audit Log"
            ],
            label_visibility="collapsed"
        )
    elif st.session_state.user_role == "admin":
        # Admin navigation for file uploads
        page = st.radio(
            "📊 Navigation",
            [
                "Group Overview",
                "🏨 Hotels Management",
                "Group KPIs",
                "Hotel Comparison",
                "Revenue Analysis",
                "Occupancy Trends",
                "📅 Room Forecast",
                "📦 Inventory",
                "💼 Payroll",
                "📊 Accounts",
                "📈 Monthly Statements",
                "📉 Budget & Forecast",
                "P&L Statement",
                "Budget Analysis",
                "Revenue",
                "Costs",
                "KPI",
                "📤 Upload Data",
                "Audit Log"
            ],
            label_visibility="collapsed"
        )
    elif st.session_state.user_role:  # Any other authenticated user
        # Hotel-level navigation for others
        page = st.radio(
            "📊 Navigation",
            ["Dashboard", "P&L Statement", "Budget Analysis", "Revenue", "Costs", "KPI", "Audit Log"],
            label_visibility="collapsed"
        )
    else:
        page = None
    
    st.divider()
    
    if st.button("🔓 Logout", use_container_width=True):
        logout()


# ============================================================================
# PAGE ROUTING
# ============================================================================

# GROUP DIRECTOR PAGES
if st.session_state.authenticated and st.session_state.user_role == "group_director":
    
    if page == "Group Overview":
        render_group_overview()
    
    elif page == "Group KPIs":
        st.title("🎯 Group Key Performance Indicators")
        render_group_kpis()
    
    elif page == "Hotel Comparison":
        st.title("🏨 Hotel-by-Hotel Comparison")
        render_hotel_comparison()
    
    elif page == "Revenue Analysis":
        st.title("📈 Group Revenue Analysis")
        render_revenue_analysis()
    
    elif page == "Occupancy Trends":
        st.title("🛏️ Group Occupancy Trends")
        render_occupancy_trends()
    
    elif page == "📅 Room Forecast":
        show_group_room_forecast()
    
    elif page == "📦 Inventory":
        show_group_inventory_analysis()
    
    elif page == "💼 Payroll":
        show_group_payroll_analysis()
    
    elif page == "📊 Accounts":
        show_group_accounts_analysis()
    
    elif page == "📈 Monthly Statements":
        show_group_monthly_statements()
    
    elif page == "📉 Budget & Forecast":
        show_group_budget_analysis()
    
    elif page == "Hotel Dashboard":
        st.title("📊 Individual Hotel Dashboard")
        
        selected_hotel = st.selectbox(
            "Select Hotel",
            [h["name"] for h in HOTEL_PROPERTIES.values()]
        )
        
        if selected_hotel:
            show_kpi_dashboard(selected_hotel)
    
    elif page == "P&L Statement":
        st.title("💰 Profit & Loss Statement")
        
        selected_hotel = st.selectbox(
            "Select Hotel",
            [h["name"] for h in HOTEL_PROPERTIES.values()]
        )
        
        if selected_hotel:
            show_pl_dashboard(selected_hotel)
    
    elif page == "Budget Analysis":
        st.title("📋 Budget vs Actual")
        
        selected_hotel = st.selectbox(
            "Select Hotel",
            [h["name"] for h in HOTEL_PROPERTIES.values()]
        )
        
        if selected_hotel:
            show_budget_vs_actual(selected_hotel)
    
    elif page == "📤 Upload Data":
        st.title("📤 Upload Operational Data")
        
        if st.session_state.user_role not in ["admin", "group_director"]:
            st.error("❌ Unauthorized. Only admins and directors can upload data.")
        else:
            render_upload_interface()
    
    elif page == "Audit Log":
        st.title("📂 Audit Log - All Properties")
        
        from supabase_client import get_audit_log
        
        # Get audit logs for all hotels
        all_audits = []
        for hotel in HOTEL_PROPERTIES.values():
            audit = get_audit_log(hotel["name"], limit=50)
            if audit:
                all_audits.extend(audit)
        
        if all_audits:
            df_audit = pd.DataFrame(all_audits)
            st.subheader("File Upload History - All Properties")
            st.dataframe(df_audit, use_container_width=True)
        else:
            st.info("No audit log entries available")

# ADMIN AND OTHER ROLES
elif st.session_state.authenticated and st.session_state.user_role == "admin":
    # Admin has access to all pages
    if page == "Group Overview":
        render_group_overview()
    
    elif page == "Group KPIs":
        st.title("🎯 Group Key Performance Indicators")
        render_group_kpis()
    
    elif page == "🏨 Hotels Management":
        render_hotels_management()
    
    elif page == "Hotel Comparison":
        st.title("🏨 Hotel-by-Hotel Comparison")
        render_hotel_comparison()
    
    elif page == "Revenue Analysis":
        st.title("📈 Group Revenue Analysis")
        render_revenue_analysis()
    
    elif page == "Occupancy Trends":
        st.title("🛏️ Group Occupancy Trends")
        render_occupancy_trends()
    
    elif page == "📅 Room Forecast":
        show_group_room_forecast()
    
    elif page == "📦 Inventory":
        show_group_inventory_analysis()
    
    elif page == "💼 Payroll":
        show_group_payroll_analysis()
    
    elif page == "📊 Accounts":
        show_group_accounts_analysis()
    
    elif page == "📈 Monthly Statements":
        show_group_monthly_statements()
    
    elif page == "📉 Budget & Forecast":
        show_group_budget_analysis()
    
    elif page == "P&L Statement":
        st.title("💰 Profit & Loss Statement")
        
        selected_hotel = st.selectbox(
            "Select Hotel",
            [h["name"] for h in HOTEL_PROPERTIES.values()],
            key="admin_pl"
        )
        
        if selected_hotel:
            show_pl_dashboard(selected_hotel)
    
    elif page == "Budget Analysis":
        st.title("📋 Budget vs Actual")
        
        selected_hotel = st.selectbox(
            "Select Hotel",
            [h["name"] for h in HOTEL_PROPERTIES.values()],
            key="admin_budget"
        )
        
        if selected_hotel:
            show_budget_vs_actual(selected_hotel)
    
    elif page == "Revenue":
        st.title("💰 Revenue Analysis")
        
        selected_hotel = st.selectbox(
            "Select Hotel",
            [h["name"] for h in HOTEL_PROPERTIES.values()],
            key="admin_revenue"
        )
        
        if selected_hotel:
            show_revenue_breakdown(selected_hotel)
    
    elif page == "Costs":
        st.title("💼 Cost Analysis")
        
        selected_hotel = st.selectbox(
            "Select Hotel",
            [h["name"] for h in HOTEL_PROPERTIES.values()],
            key="admin_costs"
        )
        
        if selected_hotel:
            show_cost_analysis(selected_hotel)
    
    elif page == "KPI":
        st.title("🎯 Key Performance Indicators")
        
        selected_hotel = st.selectbox(
            "Select Hotel",
            [h["name"] for h in HOTEL_PROPERTIES.values()],
            key="admin_kpi"
        )
        
        if selected_hotel:
            show_kpi_dashboard(selected_hotel)
    
    elif page == "📤 Upload Data":
        st.title("📤 Upload Operational Data")
        render_upload_interface()
    
    elif page == "Audit Log":
        st.title("📂 Audit Log - All Properties")
        
        from supabase_client import get_audit_log
        
        all_audits = []
        for hotel in HOTEL_PROPERTIES.values():
            audit = get_audit_log(hotel["name"], limit=50)
            if audit:
                all_audits.extend(audit)
        
        if all_audits:
            df_audit = pd.DataFrame(all_audits)
            st.subheader("File Upload History - All Properties")
            st.dataframe(df_audit, use_container_width=True)
        else:
            st.info("No audit log entries available")

# HOTEL MANAGER AND OTHER ROLES
else:
    if page == "Dashboard":
        st.title("📊 Dashboard Overview")
        show_kpi_dashboard(st.session_state.hotel_name)

    elif page == "P&L Statement":
        st.title("💰 Profit & Loss Statement")
        
        if st.session_state.user_role not in ["admin", "accountant", "group_director", "hotel_manager"]:
            st.warning("⚠️ You don't have access to financial reports")
        else:
            show_pl_dashboard(st.session_state.hotel_name)

    elif page == "Budget Analysis":
        st.title("📋 Budget vs Actual")
        
        if st.session_state.user_role not in ["admin", "accountant", "group_director", "hotel_manager"]:
            st.warning("⚠️ You don't have access to financial reports")
        else:
            show_budget_vs_actual(st.session_state.hotel_name)

    elif page == "Revenue":
        st.title("💰 Revenue Analysis")
        show_revenue_breakdown(st.session_state.hotel_name)

    elif page == "Costs":
        st.title("💼 Cost Analysis")
        
        if st.session_state.user_role not in ["admin", "accountant", "group_director", "hotel_manager"]:
            st.warning("⚠️ You don't have access to cost data")
        else:
            show_cost_analysis(st.session_state.hotel_name)

    elif page == "KPI":
        st.title("🎯 Key Performance Indicators")
        show_kpi_dashboard(st.session_state.hotel_name)

    elif page == "Audit Log":
        st.title("📂 Audit Log")
        
        from supabase_client import get_audit_log
        audit = get_audit_log(st.session_state.hotel_name, limit=100)
        
        if audit:
            df_audit = pd.DataFrame(audit)
            st.subheader("File Upload History")
            st.dataframe(df_audit, use_container_width=True)
        else:
            st.info("No audit log entries available")


# Footer
st.divider()

if st.session_state.authenticated:
    if st.session_state.user_role == "group_director":
        st.caption(f"COSMHOTEL GROUP BI • Role: {st.session_state.user_role.upper()} • All Properties")
    else:
        st.caption(f"COSMHOTEL BI • Hotel: {st.session_state.hotel_name} • Role: {st.session_state.user_role.upper() if st.session_state.user_role else 'N/A'}")
