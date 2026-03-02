"""
Debug Authentication Script
"""
import hashlib
from supabase_client import get_user

# Test hashes
test_password = "admin123"
test_hash = hashlib.sha256(test_password.encode()).hexdigest()

print(f"Password: {test_password}")
print(f"Expected hash: {test_hash}")

# Try to get user from Supabase
user = get_user("admin@cosmhotel.gr")

if user:
    print(f"\n✅ User found!")
    print(f"Email: {user['email']}")
    print(f"Stored hash: {user['password_hash']}")
    print(f"Hashes match: {user['password_hash'] == test_hash}")
else:
    print("\n❌ User not found in database")
