"""
Authentication Module for Streamlit
"""
import streamlit as st
from supabase_client import authenticate_user, get_user, hash_password


def check_password():
    """Check if user is authenticated"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.user_id = None
        st.session_state.user_email = None
        st.session_state.user_role = None
        st.session_state.hotel_name = "All Hotels"
    
    return st.session_state.authenticated


def login_page():
    """Display login page"""
    col1, col2, col3 = st.columns(3)
    
    with col2:
        st.title("🏨 COSMHOTEL GROUP")
        st.write("Hotel Management Dashboard")
        st.divider()
        
        email = st.text_input("📧 Email", placeholder="admin@cosmhotel.gr")
        password = st.text_input("🔐 Password", type="password", placeholder="password")
        
        if st.button("🔓 Login", use_container_width=True):
            if email and password:
                # Authenticate against Supabase users table
                try:
                    user = authenticate_user(email, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        st.session_state.user_id = user.get("id")
                        st.session_state.user_email = user.get("email")
                        st.session_state.user_role = user.get("role")
                        st.session_state.hotel_name = user.get("hotel_name", "All Hotels")
                        st.rerun()
                    else:
                        st.error("❌ Invalid email or password")
                except Exception as e:
                    st.error(f"❌ Authentication error: {str(e)}")
            else:
                st.warning("⚠️ Please enter email and password")
        
        st.divider()
        st.info("ℹ️ Users are managed through the Supabase admin panel. Contact your administrator to create user accounts.")


def logout():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.rerun()


def require_role(*roles):
    """Decorator to require specific role"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if st.session_state.user_role not in roles:
                st.error(f"❌ Access denied. Required role: {', '.join(roles)}")
                return
            return func(*args, **kwargs)
        return wrapper
    return decorator


def show_user_info():
    """Display current user info"""
    if st.session_state.authenticated:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("👤 User", st.session_state.user["full_name"])
        
        with col2:
            st.metric("🏨 Hotel", st.session_state.hotel_name)
        
        with col3:
            role_label = st.session_state.user_role.upper()
            st.metric("🔐 Role", role_label)
