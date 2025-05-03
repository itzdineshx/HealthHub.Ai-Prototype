"""
Database Test Script
Run this script to verify database functionality and create test data
"""
import os
import sys
from datetime import datetime, timedelta
import random

print("Testing database setup...")

# Import database utilities
try:
    from utils.db import (
        get_users, add_user, get_user, update_user, delete_user,
        add_appointment, get_appointments, update_appointment_status,
        delete_appointment, add_health_record, get_health_records
    )
    print("✅ Successfully imported database utilities")
except ImportError as e:
    print(f"❌ Error importing database utilities: {e}")
    sys.exit(1)

# Test database operations
try:
    # Get existing users
    existing_users = get_users()
    print(f"✅ Found {len(existing_users)} existing users")
    
    # Add a test user if none exist
    if not existing_users:
        user_data = {
            "name": "Test User",
            "role": "doctor",
            "specialty": "General",
            "bio": "Test doctor for database validation",
            "photo_url": "https://xsgames.co/randomusers/assets/avatars/male/5.jpg",
            "rating": 4.5,
            "location": "Test City",
            "distance_km": 1.0,
            "created_at": datetime.utcnow()
        }
        
        user_id = add_user(user_data)
        print(f"✅ Added test user with ID: {user_id}")
        
        # Verify user was added
        user = get_user(user_id)
        if user and user["name"] == "Test User":
            print(f"✅ Successfully retrieved user: {user['name']}")
        else:
            print("❌ Failed to retrieve added user")
            
        # Add test appointment
        tomorrow = datetime.now() + timedelta(days=1)
        appointment_data = {
            "user_id": user_id,
            "user_name": "Test User",
            "type": "doctor",
            "specialty": "General",
            "requested_by": "test_patient",
            "date": tomorrow.replace(hour=10, minute=0, second=0, microsecond=0),
            "status": "pending",
            "notes": "Test appointment",
            "created_at": datetime.utcnow()
        }
        
        appointment_id = add_appointment(appointment_data)
        print(f"✅ Added test appointment with ID: {appointment_id}")
        
        # Verify appointment was added
        appointments = get_appointments(user_id=user_id)
        if appointments and len(appointments) > 0:
            print(f"✅ Successfully retrieved {len(appointments)} appointments")
            
            # Test update status
            update_result = update_appointment_status(appointment_id, "confirmed")
            if update_result:
                print("✅ Successfully updated appointment status")
            else:
                print("❌ Failed to update appointment status")
                
        else:
            print("❌ Failed to retrieve added appointment")
            
        # Test health record
        record_data = {
            "user_id": "test_patient",
            "filename": "test_record.pdf",
            "file_hash": "0x" + "".join(random.choices("0123456789abcdef", k=64)),
            "tx_hash": "0x" + "".join(random.choices("0123456789abcdef", k=64)),
            "block_number": 12345678,
            "timestamp": datetime.utcnow()
        }
        
        record_id = add_health_record(record_data)
        print(f"✅ Added test health record with ID: {record_id}")
        
        # Verify health record was added
        records = get_health_records("test_patient")
        if records and len(records) > 0:
            print(f"✅ Successfully retrieved {len(records)} health records")
        else:
            print("❌ Failed to retrieve added health record")
            
    print("\n✅ All database tests completed successfully!")
    print("Database is properly configured and working.")
    
except Exception as e:
    print(f"❌ Error during database testing: {e}")
    sys.exit(1) 