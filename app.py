"""
COSMHOTEL GROUP BI Dashboard - Supabase Backend
Main Streamlit Application with Advanced Financial Analytics
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from auth import check_password, login_page, logout, show_user_info
from config import HOTELS, GREEK_MONTHS
from financial_dashboards import (
    show_pl_dashboard,
    show_budget_vs_actual,
    show_revenue_breakdown,
    show_cost_analysis,
    show_kpi_dashboard,
    show_multi_hotel_comparison
)

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
        ["Dashboard", "P&L Statement", "Budget Analysis", "Revenue", "Costs", "KPI", "Audit Log"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    if st.button("🔓 Logout", use_container_width=True):
        logout()


if page == "Dashboard":
    st.title("📊 Dashboard Overview")
    
    # Show multi-hotel for Group Director
    if st.session_state.user_role == "group_director":
        show_multi_hotel_comparison(HOTELS)
    else:
        st.write(f"**Current Hotel:** {st.session_state.hotel_name}")
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
st.caption(f"COSMHOTEL BI • Hotel: {st.session_state.hotel_name} • Role: {st.session_state.user_role.upper()}")
