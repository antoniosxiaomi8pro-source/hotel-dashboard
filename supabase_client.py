"""
Supabase Client Module
Handles all database operations with Supabase
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime
import hashlib

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Initialize clients
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


# ============================================================================
# AUTHENTICATION
# ============================================================================

def hash_password(password: str) -> str:
    """Simple hash for demo (in production use proper bcrypt)"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hash: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(password) == hash


def get_user(email: str) -> dict | None:
    """Get user by email"""
    try:
        response = supabase.table("users").select("*").eq("email", email).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None


def authenticate_user(email: str, password: str) -> dict | None:
    """Authenticate user with email and password"""
    user = get_user(email)
    if user and verify_password(password, user["password_hash"]):
        return user
    return None


def create_user(email: str, password: str, full_name: str, hotel_name: str, role: str = "viewer") -> dict | None:
    """Create new user (admin only)"""
    try:
        response = supabase_admin.table("users").insert({
            "email": email,
            "password_hash": hash_password(password),
            "full_name": full_name,
            "hotel_name": hotel_name,
            "role": role,
            "is_active": True
        }).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error creating user: {e}")
        return None


# ============================================================================
# ROOM FORECAST
# ============================================================================

def insert_room_forecast(hotel_name: str, room_type: str, forecast_date: str, 
                        forecast_value: int, month: int = None, year: int = None, 
                        source_file: str = None) -> bool:
    """Insert room forecast record"""
    try:
        supabase_admin.table("room_forecast").insert({
            "hotel_name": hotel_name,
            "room_type": room_type,
            "forecast_date": forecast_date,
            "forecast_value": forecast_value,
            "month": month,
            "year": year,
            "source_file": source_file
        }).execute()
        return True
    except Exception as e:
        print(f"Error inserting forecast: {e}")
        return False


def get_room_forecast(hotel_name: str, month: int = None, year: int = None) -> list:
    """Get room forecasts for a hotel"""
    try:
        query = supabase.table("room_forecast").select("*").eq("hotel_name", hotel_name)
        
        if month:
            query = query.eq("month", month)
        if year:
            query = query.eq("year", year)
        
        response = query.execute()
        return response.data
    except Exception as e:
        print(f"Error getting forecast: {e}")
        return []


# ============================================================================
# DAILY OPERATIONS
# ============================================================================

def insert_daily_operation(hotel_name: str, operation_date: str, occupancy_rate: float = None,
                          revenue: float = None, guests_count: int = None, rooms_sold: int = None,
                          manager_notes: str = None, source_file: str = None) -> bool:
    """Insert daily operation record"""
    try:
        supabase_admin.table("daily_operations").insert({
            "hotel_name": hotel_name,
            "operation_date": operation_date,
            "occupancy_rate": occupancy_rate,
            "revenue": revenue,
            "guests_count": guests_count,
            "rooms_sold": rooms_sold,
            "manager_notes": manager_notes,
            "source_file": source_file
        }).execute()
        return True
    except Exception as e:
        print(f"Error inserting operation: {e}")
        return False


def get_daily_operations(hotel_name: str) -> list:
    """Get daily operations for a hotel"""
    try:
        response = supabase.table("daily_operations").select("*").eq("hotel_name", hotel_name).execute()
        return response.data
    except Exception as e:
        print(f"Error getting operations: {e}")
        return []


# ============================================================================
# WAREHOUSE INVENTORY
# ============================================================================

def insert_warehouse_item(hotel_name: str, warehouse: str, category: str, 
                         balance_value: float = None, purchases_value: float = None,
                         outflow_value: float = None, source_file: str = None) -> bool:
    """Insert warehouse inventory item"""
    try:
        supabase_admin.table("warehouse_inventory").insert({
            "hotel_name": hotel_name,
            "warehouse": warehouse,
            "category": category,
            "balance_value": balance_value,
            "purchases_value": purchases_value,
            "outflow_value": outflow_value,
            "source_file": source_file
        }).execute()
        return True
    except Exception as e:
        print(f"Error inserting warehouse item: {e}")
        return False


def get_warehouse_inventory(hotel_name: str) -> list:
    """Get warehouse inventory for a hotel"""
    try:
        response = supabase.table("warehouse_inventory").select("*").eq("hotel_name", hotel_name).execute()
        return response.data
    except Exception as e:
        print(f"Error getting inventory: {e}")
        return []


# ============================================================================
# FINANCIAL COSTS
# ============================================================================

def insert_financial_cost(hotel_name: str, cost_type: str, description: str = None,
                         amount: float = None, employee_name: str = None,
                         period: str = None, year: int = None, source_file: str = None) -> bool:
    """Insert financial cost record"""
    try:
        supabase_admin.table("financial_costs").insert({
            "hotel_name": hotel_name,
            "cost_type": cost_type,
            "description": description,
            "amount": amount,
            "employee_name": employee_name,
            "period": period,
            "year": year,
            "source_file": source_file
        }).execute()
        return True
    except Exception as e:
        print(f"Error inserting cost: {e}")
        return False


def get_financial_costs(hotel_name: str) -> list:
    """Get financial costs for a hotel"""
    try:
        response = supabase.table("financial_costs").select("*").eq("hotel_name", hotel_name).execute()
        return response.data
    except Exception as e:
        print(f"Error getting costs: {e}")
        return []


# ============================================================================
# REVENUE ACCOUNTS
# ============================================================================

def insert_revenue_account(hotel_name: str, account_name: str, month: int, year: int,
                          gross: float = None, net: float = None, vat: float = None,
                          tax: float = None, source_file: str = None) -> bool:
    """Insert revenue account record"""
    try:
        supabase_admin.table("revenue_accounts").insert({
            "hotel_name": hotel_name,
            "account_name": account_name,
            "month": month,
            "year": year,
            "gross": gross,
            "net": net,
            "vat": vat,
            "tax": tax,
            "source_file": source_file
        }).execute()
        return True
    except Exception as e:
        print(f"Error inserting revenue: {e}")
        return False


def get_revenue_accounts(hotel_name: str) -> list:
    """Get revenue accounts for a hotel"""
    try:
        response = supabase.table("revenue_accounts").select("*").eq("hotel_name", hotel_name).execute()
        return response.data
    except Exception as e:
        print(f"Error getting revenue: {e}")
        return []


# ============================================================================
# FINANCIAL ACCOUNTS
# ============================================================================

def insert_financial_account(hotel_name: str, account_code: str, description: str,
                            debit_amount: float = None, credit_amount: float = None,
                            account_type: str = None, source_file: str = None) -> bool:
    """Insert financial account record"""
    try:
        supabase_admin.table("financial_accounts").insert({
            "hotel_name": hotel_name,
            "account_code": account_code,
            "description": description,
            "debit_amount": debit_amount,
            "credit_amount": credit_amount,
            "account_type": account_type,
            "source_file": source_file
        }).execute()
        return True
    except Exception as e:
        print(f"Error inserting account: {e}")
        return False


def get_financial_accounts(hotel_name: str) -> list:
    """Get financial accounts for a hotel"""
    try:
        response = supabase.table("financial_accounts").select("*").eq("hotel_name", hotel_name).execute()
        return response.data
    except Exception as e:
        print(f"Error getting accounts: {e}")
        return []


# ============================================================================
# AUDIT LOG
# ============================================================================

def insert_audit_log(hotel_name: str, user_email: str, action: str, file_name: str = None,
                    records_count: int = None, status: str = "success", 
                    error_message: str = None) -> bool:
    """Insert audit log entry"""
    try:
        supabase_admin.table("audit_log").insert({
            "hotel_name": hotel_name,
            "user_email": user_email,
            "action": action,
            "file_name": file_name,
            "records_count": records_count,
            "status": status,
            "error_message": error_message
        }).execute()
        return True
    except Exception as e:
        print(f"Error inserting audit log: {e}")
        return False


def get_audit_log(hotel_name: str, limit: int = 100) -> list:
    """Get audit log for a hotel"""
    try:
        response = supabase.table("audit_log").select("*").eq("hotel_name", hotel_name).order("created_at", desc=True).limit(limit).execute()
        return response.data
    except Exception as e:
        print(f"Error getting audit log: {e}")
        return []
