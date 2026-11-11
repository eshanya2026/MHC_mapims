"""
Setup script to create secure admin user
Run this once to set up admin account with hashed password
"""

import sys
import getpass
from pymongo import MongoClient
from security_config import SecurityConfig
from dotenv import load_dotenv
import os

load_dotenv()

def setup_admin():
    """Create or update admin user with secure password"""
    # Get MongoDB connection
    mongodb_uri = os.environ.get('MONGODB_URI')
    if not mongodb_uri:
        print("ERROR: MONGODB_URI environment variable not set")
        print("Please set MONGODB_URI in your .env file")
        sys.exit(1)
    
    try:
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        db = client['mapims_health']
        admin_collection = db['admin_users']
        
        # Test connection
        client.server_info()
        print("✓ Connected to MongoDB")
        
        # Get admin credentials
        print("\n=== MAPIMS Admin Account Setup ===")
        username = input("Enter admin username (default: admin): ").strip() or "admin"
        
        # Check if user exists
        existing_user = admin_collection.find_one({'username': username})
        if existing_user:
            print(f"\nUser '{username}' already exists.")
            update = input("Do you want to update the password? (y/n): ").strip().lower()
            if update != 'y':
                print("Cancelled.")
                sys.exit(0)
        
        # Get password
        while True:
            password = getpass.getpass("Enter admin password (min 12 chars): ")
            
            # Validate password strength
            errors = SecurityConfig.validate_password_strength(password)
            if errors:
                print("\nPassword validation errors:")
                for error in errors:
                    print(f"  - {error}")
                print()
                continue
            
            confirm_password = getpass.getpass("Confirm password: ")
            if password != confirm_password:
                print("Passwords do not match. Please try again.\n")
                continue
            
            break
        
        # Hash password
        password_hash = SecurityConfig.hash_password(password)
        
        # Create or update admin user
        from datetime import datetime
        admin_user = {
            'username': username,
            'password_hash': password_hash,
            'created_at': str(datetime.now()),
            'last_updated': str(datetime.now()),
            'role': 'admin',
            'active': True
        }
        
        if existing_user:
            admin_collection.update_one(
                {'username': username},
                {'$set': admin_user}
            )
            print(f"\n✓ Admin user '{username}' password updated successfully")
        else:
            admin_collection.insert_one(admin_user)
            print(f"\n✓ Admin user '{username}' created successfully")
        
        print("\nAdmin account setup complete!")
        print(f"Username: {username}")
        print("\nIMPORTANT: Keep your password secure and never share it.")
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        sys.exit(1)
    finally:
        if 'client' in locals():
            client.close()

if __name__ == '__main__':
    from datetime import datetime
    setup_admin()

