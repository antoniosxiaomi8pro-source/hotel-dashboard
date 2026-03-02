"""
Initialize Demo Users in Supabase
Run this once to populate the database with demo users
"""
import hashlib
from supabase_client import supabase_admin

def hash_password(password: str) -> str:
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

# Demo users to create
demo_users = [
    {
        "email": "admin@cosmhotel.gr",
        "password": "admin123",
        "full_name": "Administrator",
        "hotel_name": "Porto Greco",
        "role": "admin"
    },
    {
        "email": "manager@cosmhotel.gr",
        "password": "manager123",
        "full_name": "Manager",
        "hotel_name": "Porto Greco",
        "role": "manager"
    },
    {
        "email": "viewer@cosmhotel.gr",
        "password": "viewer123",
        "full_name": "Viewer",
        "hotel_name": "Porto Greco",
        "role": "viewer"
    }
]

print("🔄 Initializing demo users...")

# First delete existing users
try:
    supabase_admin.table("users").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    print("✅ Cleared existing users")
except Exception as e:
    print(f"⚠️ Could not clear users (might be first run): {e}")

# Insert new users
for user in demo_users:
    try:
        response = supabase_admin.table("users").insert({
            "email": user["email"],
            "password_hash": hash_password(user["password"]),
            "full_name": user["full_name"],
            "hotel_name": user["hotel_name"],
            "role": user["role"],
            "is_active": True
        }).execute()
        
        print(f"✅ Created user: {user['email']}")
    except Exception as e:
        print(f"❌ Error creating {user['email']}: {e}")

print("\n✅ Demo users initialization complete!")
print("\nYou can now login with:")
for user in demo_users:
    print(f"  - {user['email']} / {user['password']}")
