import os
import sqlite3
import json
import datetime
from pathlib import Path

# Ensure the data directory exists
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# Database path
DB_PATH = data_dir / "healthhub.db"

def get_db_connection():
    """Get a connection to the SQLite database"""
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

# Initialize the database
def init_db():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    
    # Create users table (for doctors and trainers)
    conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        specialty TEXT,
        bio TEXT,
        photo_url TEXT,
        rating REAL DEFAULT 4.5,
        location TEXT,
        distance_km REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create appointments table
    conn.execute('''
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        user_name TEXT NOT NULL,
        type TEXT NOT NULL,
        specialty TEXT,
        requested_by TEXT NOT NULL,
        date TIMESTAMP NOT NULL,
        status TEXT DEFAULT 'pending',
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create health_records table
    conn.execute('''
    CREATE TABLE IF NOT EXISTS health_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        filename TEXT NOT NULL,
        file_hash TEXT NOT NULL,
        tx_hash TEXT NOT NULL,
        block_number INTEGER NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()
    
# User operations
def add_user(user_data):
    """Add a new user (doctor or trainer)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    columns = ', '.join(user_data.keys())
    placeholders = ', '.join(['?' for _ in user_data])
    values = list(user_data.values())
    
    query = f"INSERT INTO users ({columns}) VALUES ({placeholders})"
    cursor.execute(query, values)
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return user_id

def get_users(role=None, specialty=None):
    """Get users with optional filters"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM users"
    params = []
    
    if role or specialty:
        query += " WHERE"
        
        if role:
            query += " role = ?"
            params.append(role)
            
        if specialty and specialty != "Any":
            if role:
                query += " AND"
            query += " specialty = ?"
            params.append(specialty)
    
    cursor.execute(query, params)
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return users

def get_user(user_id):
    """Get a user by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    user = dict(row) if row else None
    conn.close()
    
    return user

def update_user(user_id, update_data):
    """Update a user's information"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    set_clause = ', '.join([f"{key} = ?" for key in update_data.keys()])
    values = list(update_data.values())
    values.append(user_id)  # For the WHERE clause
    
    query = f"UPDATE users SET {set_clause} WHERE id = ?"
    cursor.execute(query, values)
    
    conn.commit()
    conn.close()
    
    return cursor.rowcount > 0

def delete_user(user_id):
    """Delete a user by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    success = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    return success

# Appointment operations
def add_appointment(appointment_data):
    """Add a new appointment"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    columns = ', '.join(appointment_data.keys())
    placeholders = ', '.join(['?' for _ in appointment_data])
    values = list(appointment_data.values())
    
    query = f"INSERT INTO appointments ({columns}) VALUES ({placeholders})"
    cursor.execute(query, values)
    
    appointment_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return appointment_id

def get_appointments(user_id=None, status=None):
    """Get appointments with optional filters"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM appointments"
    params = []
    
    if user_id or status:
        query += " WHERE"
        
        if user_id:
            query += " user_id = ?"
            params.append(user_id)
            
        if status:
            if user_id:
                query += " AND"
            query += " status = ?"
            params.append(status)
    
    cursor.execute(query, params)
    appointments = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return appointments

def update_appointment_status(appointment_id, new_status):
    """Update the status of an appointment"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE appointments SET status = ? WHERE id = ?", 
        (new_status, appointment_id)
    )
    
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return success

def delete_appointment(appointment_id):
    """Delete an appointment by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
    success = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    return success

# Health records operations
def add_health_record(record_data):
    """Add a new health record"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    columns = ', '.join(record_data.keys())
    placeholders = ', '.join(['?' for _ in record_data])
    values = list(record_data.values())
    
    query = f"INSERT INTO health_records ({columns}) VALUES ({placeholders})"
    cursor.execute(query, values)
    
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return record_id

def get_health_records(user_id):
    """Get health records for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM health_records 
        WHERE user_id = ? 
        ORDER BY timestamp DESC
    """, (user_id,))
    
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return records

def delete_health_record(record_id):
    """Delete a health record by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM health_records WHERE id = ?", (record_id,))
    success = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    return success

# Add some seed data for testing if none exists
def add_seed_data():
    """Add some initial data if the database is empty"""
    # Check if any users exist
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    
    if count == 0:
        # Add sample doctors
        doctors = [
            {
                "name": "John Smith",
                "role": "doctor",
                "specialty": "Cardiologist",
                "bio": "Experienced cardiologist with 15 years of practice.",
                "photo_url": "https://xsgames.co/randomusers/assets/avatars/male/1.jpg",
                "rating": 4.8,
                "location": "New York",
                "distance_km": 1.5,
                "created_at": datetime.datetime.utcnow()
            },
            {
                "name": "Emily Johnson",
                "role": "doctor",
                "specialty": "Pediatrician",
                "bio": "Caring pediatrician specializing in early childhood development.",
                "photo_url": "https://xsgames.co/randomusers/assets/avatars/female/1.jpg",
                "rating": 4.9,
                "location": "Boston",
                "distance_km": 2.3,
                "created_at": datetime.datetime.utcnow()
            }
        ]
        
        # Add sample trainers
        trainers = [
            {
                "name": "Mike Williams",
                "role": "trainer",
                "specialty": "Strength Coach",
                "bio": "Certified strength coach with expertise in powerlifting.",
                "photo_url": "https://xsgames.co/randomusers/assets/avatars/male/2.jpg",
                "rating": 4.7,
                "location": "Chicago",
                "distance_km": 0.8,
                "created_at": datetime.datetime.utcnow()
            },
            {
                "name": "Sarah Davis",
                "role": "trainer",
                "specialty": "Yoga Instructor",
                "bio": "200-hour certified yoga instructor specializing in vinyasa flow.",
                "photo_url": "https://xsgames.co/randomusers/assets/avatars/female/2.jpg",
                "rating": 4.6,
                "location": "Los Angeles",
                "distance_km": 1.2,
                "created_at": datetime.datetime.utcnow()
            }
        ]
        
        # Add all sample users
        for user in doctors + trainers:
            add_user(user)

# Initialize the database when this module is imported
init_db()
# Add seed data
add_seed_data() 