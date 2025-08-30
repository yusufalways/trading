"""
User Management Utility for Trading Dashboard
Simple script to add/remove users
"""

from auth import SimpleAuth, add_user
import json

def show_users():
    """Display all users"""
    auth = SimpleAuth()
    try:
        with open(auth.credentials_file, 'r') as f:
            creds = json.load(f)
        
        print("\n📋 Current Users:")
        print("-" * 50)
        for email, info in creds["users"].items():
            print(f"📧 {email}")
            print(f"   Name: {info.get('name', 'Unknown')}")
            print(f"   Created: {info.get('created', 'Unknown')}")
            print()
    except FileNotFoundError:
        print("❌ No credentials file found. Run the dashboard first to create it.")

def add_new_user():
    """Add a new user"""
    print("\n➕ Add New User")
    print("-" * 30)
    
    email = input("📧 Email: ").strip()
    password = input("🔒 Password: ").strip()
    name = input("👤 Name: ").strip()
    
    if not email or not password:
        print("❌ Email and password are required!")
        return
    
    if not name:
        name = "User"
    
    if add_user(email, password, name):
        print(f"✅ User {email} added successfully!")
    else:
        print("❌ Failed to add user. Check if email already exists.")

def change_password():
    """Change user password"""
    auth = SimpleAuth()
    print("\n🔐 Change Password")
    print("-" * 30)
    
    email = input("📧 Email: ").strip()
    new_password = input("🔒 New Password: ").strip()
    
    try:
        with open(auth.credentials_file, 'r') as f:
            creds = json.load(f)
        
        if email not in creds["users"]:
            print("❌ User not found!")
            return
        
        creds["users"][email]["password_hash"] = auth.hash_password(new_password)
        
        with open(auth.credentials_file, 'w') as f:
            json.dump(creds, f, indent=2)
        
        print(f"✅ Password changed for {email}")
    except Exception as e:
        print(f"❌ Error changing password: {e}")

def main():
    """Main menu"""
    while True:
        print("\n🔐 Trading Dashboard User Management")
        print("=" * 40)
        print("1. 📋 Show all users")
        print("2. ➕ Add new user")
        print("3. 🔐 Change password")
        print("4. 🚪 Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            show_users()
        elif choice == "2":
            add_new_user()
        elif choice == "3":
            change_password()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
