import streamlit as st
from utils.db import get_users, add_user, get_appointments, delete_appointment, delete_user
import datetime

st.set_page_config(page_title="Admin Panel", layout="wide")
st.title("⚙️ Admin Dashboard")

# Admin Authentication would normally go here
st.sidebar.markdown("### Admin Controls")

# Create tabs for different admin functions
tabs = st.tabs(["Users", "Appointments", "Analytics"])

# --- Users Management Tab ---
with tabs[0]:
    st.header("👥 User Management")
    
    # Add new doctor/trainer form
    with st.expander("Add New Professional"):
        with st.form("add_professional"):
            name = st.text_input("Name")
            role = st.selectbox("Role", ["doctor", "trainer"])
            
            if role == "doctor":
                specialty = st.selectbox("Specialty", 
                    ["General", "Cardiologist", "Endocrinologist", "Dermatologist", "Pediatrician", "Neurologist"])
            else:
                specialty = st.selectbox("Specialty", 
                    ["Strength Coach", "Yoga Instructor", "Pilates Instructor", "CrossFit Coach", "Cardio Trainer"])
            
            bio = st.text_area("Bio")
            photo_url = st.text_input("Photo URL")
            rating = st.slider("Initial Rating", 1.0, 5.0, 4.5, 0.1)
            location = st.text_input("Location")
            
            if st.form_submit_button("Add Professional"):
                if not name:
                    st.error("Name is required")
                else:
                    user_data = {
                        "name": name,
                        "role": role,
                        "specialty": specialty,
                        "bio": bio,
                        "photo_url": photo_url,
                        "rating": rating,
                        "location": location,
                        "distance_km": 1.2,  # Mock distance
                        "created_at": datetime.datetime.utcnow()
                    }
                    
                    user_id = add_user(user_data)
                    st.success(f"Added new {role} with ID: {user_id}")
    
    # View existing professionals
    st.subheader("View Professionals")
    
    role_filter = st.radio("Filter by role", ["All", "Doctor", "Trainer"], horizontal=True)
    
    # Get users based on filter
    if role_filter == "All":
        users = get_users()
    else:
        users = get_users(role=role_filter.lower())
    
    if not users:
        st.info("No professionals found.")
    else:
        # Display users in a table
        for user in users:
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col1:
                if user.get("photo_url"):
                    st.image(user["photo_url"], width=100)
                else:
                    st.image("https://via.placeholder.com/100", width=100)
            
            with col2:
                st.markdown(f"### {user['name']}")
                st.markdown(f"**Role:** {user['role'].title()}")
                st.markdown(f"**Specialty:** {user.get('specialty', '–')}")
                st.markdown(f"**Location:** {user.get('location', '–')}")
                st.markdown(f"**Rating:** {user.get('rating', 4.5)}")
                st.markdown(f"**Added:** {user.get('created_at', '–')}")
            
            with col3:
                st.write("Actions")
                if st.button("Delete", key=f"delete_user_{user['id']}"):
                    if delete_user(user['id']):
                        st.success(f"Deleted {user['name']}")
                        st.rerun()
                    else:
                        st.error("Failed to delete user")
            
            st.markdown("---")

# --- Appointments Tab ---
with tabs[1]:
    st.header("📆 Appointment Management")
    
    # Get all appointments
    appointments = get_appointments()
    
    if not appointments:
        st.info("No appointments found.")
    else:
        # Group by status
        status_dict = {}
        for apt in appointments:
            status = apt.get("status", "pending")
            if status not in status_dict:
                status_dict[status] = []
            status_dict[status].append(apt)
        
        # Create tabs for different statuses
        status_tabs = st.tabs(["All", "Pending", "Confirmed", "Completed", "Cancelled"])
        
        # Display all appointments
        with status_tabs[0]:
            st.metric("Total Appointments", len(appointments))
            for apt in appointments:
                cols = st.columns([3, 1])
                date_obj = apt["date"]
                with cols[0]:
                    st.markdown(f"**Professional:** {apt.get('user_name', 'Unknown')}")
                    st.markdown(f"**Patient:** {apt.get('requested_by', 'Anonymous')}")
                    st.markdown(f"**Date:** {date_obj.strftime('%Y-%m-%d %H:%M')}")
                    st.markdown(f"**Type:** {apt.get('type', '')}")
                    st.markdown(f"**Status:** {apt.get('status', 'pending')}")
                with cols[1]:
                    st.write("Admin Actions")
                    if st.button("Delete", key=f"delete_{apt['id']}"):
                        if delete_appointment(apt['id']):
                            st.success("Appointment deleted")
                            st.rerun()
                        else:
                            st.error("Failed to delete appointment")
                
                st.markdown("---")
        
        # Display by status
        for i, status in enumerate(["pending", "confirmed", "completed", "cancelled"], 1):
            with status_tabs[i]:
                status_apts = status_dict.get(status, [])
                st.metric(f"{status.title()} Appointments", len(status_apts))
                
                if not status_apts:
                    st.info(f"No {status} appointments.")
                else:
                    for apt in status_apts:
                        cols = st.columns([3, 1])
                        date_obj = apt["date"]
                        with cols[0]:
                            st.markdown(f"**Professional:** {apt.get('user_name', 'Unknown')}")
                            st.markdown(f"**Patient:** {apt.get('requested_by', 'Anonymous')}")
                            st.markdown(f"**Date:** {date_obj.strftime('%Y-%m-%d %H:%M')}")
                            st.markdown(f"**Type:** {apt.get('type', '')}")
                        with cols[1]:
                            st.write("Admin Actions")
                            if st.button("Delete", key=f"delete_status_{apt['id']}"):
                                if delete_appointment(apt['id']):
                                    st.success("Appointment deleted")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete appointment")
                        
                        st.markdown("---")

# --- Analytics Tab ---
with tabs[2]:
    st.header("📊 Analytics Dashboard")
    
    st.markdown("### Summary Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Get counts by role
        doctors = len([u for u in get_users() if u.get("role") == "doctor"])
        trainers = len([u for u in get_users() if u.get("role") == "trainer"])
        
        st.metric("Total Doctors", doctors)
        st.metric("Total Trainers", trainers)
    
    with col2:
        # Count appointments by status
        pending = len([a for a in appointments if a.get("status") == "pending"])
        confirmed = len([a for a in appointments if a.get("status") == "confirmed"])
        
        st.metric("Pending Appointments", pending)
        st.metric("Confirmed Appointments", confirmed)
    
    with col3:
        # Mock metrics - in real app would come from actual data
        st.metric("Active Users", 142)
        st.metric("New Users (Last 7 Days)", 23)
    
    st.markdown("### Data Visualization")
    st.info("Data visualizations with matplotlib/plotly would go here in the final app.")
