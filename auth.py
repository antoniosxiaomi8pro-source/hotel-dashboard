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
                # Test credentials (hardcoded for demo)
                test_users = {
                    "admin@cosmhotel.gr": "admin123",
                    "admin2@cosmhotel.gr": "admin234",
                    "director@cosmhotel.gr": "director123",
                    "manager.porto@cosmhotel.gr": "manager123",
                    "manager.theros@cosmhotel.gr": "manager123",
                    "manager.apollon@cosmhotel.gr": "manager123",
                    "manager.axelcrete@cosmhotel.gr": "manager123",
                    "manager.axelmykonos@cosmhotel.gr": "manager123",
                    "manager.kingscorpio@cosmhotel.gr": "manager123",
                    "accountant@cosmhotel.gr": "accountant123",
                    "viewer@cosmhotel.gr": "viewer123",
                }
                
                if email in test_users and test_users[email] == password:
                    # Determine role based on email
                    if "admin" in email:
                        role = "admin"
                        hotel = "Porto Greco Beach & Village" if email == "admin@cosmhotel.gr" else "Theros Resort"
                    elif "director" in email:
                        role = "group_director"
                        hotel = "All Hotels"
                    elif "accountant" in email:
                        role = "accountant"
                        hotel = "All Hotels (Finance)"
                    elif "viewer" in email:
                        role = "viewer"
                        hotel = "Porto Greco Beach & Village"
                    else:
                        role = "hotel_manager"
                        # Extract hotel from email
                        if "porto" in email:
                            hotel = "Porto Greco Beach & Village"
                        elif "theros" in email:
                            hotel = "Theros Resort"
                        elif "apollon" in email:
                            hotel = "Apollon Hotel"
                        elif "axelcrete" in email:
                            hotel = "Axel Crete Villaggio"
                        elif "axelmykonos" in email:
                            hotel = "Axel Beach Mykonos"
                        elif "kingscorpio" in email:
                            hotel = "KingScorpio Restaurant"
                        else:
                            hotel = "Porto Greco Beach & Village"
                    
                    user = {
                        "id": "demo-user",
                        "email": email,
                        "full_name": email.split("@")[0].replace(".", " ").title(),
                        "hotel_name": hotel,
                        "role": role
                    }
                    
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.session_state.user_id = user["id"]
                    st.session_state.user_email = user["email"]
                    st.session_state.user_role = user["role"]
                    st.session_state.hotel_name = user["hotel_name"]
                    st.rerun()
                else:
                    st.error("❌ Invalid email or password")
            else:
                st.warning("⚠️ Please enter email and password")
        
        st.divider()
        st.write("**Demo Credentials:**")
        
        with st.expander("👤 Admin Users (Upload Files)"):
            st.write("- `admin@cosmhotel.gr` / `admin123`")
            st.write("- `admin2@cosmhotel.gr` / `admin234`")
        
        with st.expander("👨‍💼 Group Director (All Hotels)"):
            st.write("- `director@cosmhotel.gr` / `director123`")
        
        with st.expander("🏨 Hotel Managers (Own Hotel)"):
            st.write("- `manager.porto@cosmhotel.gr` / `manager123`")
            st.write("- `manager.theros@cosmhotel.gr` / `manager123`")
            st.write("- `manager.apollon@cosmhotel.gr` / `manager123`")
            st.write("- `manager.axelcrete@cosmhotel.gr` / `manager123`")
            st.write("- `manager.axelmykonos@cosmhotel.gr` / `manager123`")
            st.write("- `manager.kingscorpio@cosmhotel.gr` / `manager123`")
        
        with st.expander("💰 Accountant (Finance Only)"):
            st.write("- `accountant@cosmhotel.gr` / `accountant123`")
        
        with st.expander("👁️ Viewer (Read-Only)"):
            st.write("- `viewer@cosmhotel.gr` / `viewer123`")


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
