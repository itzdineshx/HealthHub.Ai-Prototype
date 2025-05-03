import streamlit as st
from utils.db import get_appointments, get_user, update_appointment_status
import datetime

st.set_page_config(page_title="Doctor Panel", layout="wide")
st.title("🩺 Doctor Dashboard")

# Mock current doctor ID (in real app, get from authentication)
doctor_id = 1
doctor = get_user(doctor_id)

if not doctor:
    st.error("Doctor not found!")
    st.info("Please make sure you've added sample data through the Admin Panel first.")
    st.stop()

st.markdown(f"### Welcome, Dr. {doctor['name']}")

# Appointment Management
st.subheader("📆 Your Appointments")

# Get appointments for this doctor
appointments = get_appointments(user_id=doctor_id)

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
    tabs = st.tabs(["Pending", "Confirmed", "Completed", "Cancelled"])
    
    for tab, status in zip(tabs, ["pending", "confirmed", "completed", "cancelled"]):
        with tab:
            status_apts = status_dict.get(status, [])
            if not status_apts:
                st.info(f"No {status} appointments.")
            else:
                for apt in status_apts:
                    cols = st.columns([3, 1])
                    date_obj = apt["date"]
                    with cols[0]:
                        st.markdown(f"**Patient:** {apt.get('requested_by', 'Anonymous')}")
                        st.markdown(f"**Date:** {date_obj.strftime('%Y-%m-%d %H:%M')}")
                        st.markdown(f"**Type:** {apt.get('type', '')}")
                    with cols[1]:
                        if status == "pending":
                            if st.button("Confirm", key=f"confirm_{apt['id']}"):
                                # Update appointment status
                                if update_appointment_status(apt['id'], "confirmed"):
                                    st.success("Appointment confirmed!")
                                    st.rerun()
                                else:
                                    st.error("Failed to update appointment status")
                        
                        if status in ["pending", "confirmed"]:
                            if st.button("Cancel", key=f"cancel_{apt['id']}"):
                                # Update appointment status
                                if update_appointment_status(apt['id'], "cancelled"):
                                    st.error("Appointment cancelled")
                                    st.rerun()
                                else:
                                    st.error("Failed to update appointment status")
                        
                        if status == "confirmed":
                            if st.button("Complete", key=f"complete_{apt['id']}"):
                                # Update appointment status
                                if update_appointment_status(apt['id'], "completed"):
                                    st.success("Appointment completed!")
                                    st.rerun()
                                else:
                                    st.error("Failed to update appointment status")
                    
                    st.markdown("---")
