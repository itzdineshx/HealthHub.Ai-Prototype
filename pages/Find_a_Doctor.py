# pages/6_Find_a_Doctor.py
import streamlit as st
from utils.db import get_users, add_appointment
from datetime import datetime, timedelta
from utils.theme import apply_theme, card, badge, styled_table

st.set_page_config(page_title="Find a Professional", layout="wide")

# Apply consistent theme
apply_theme("Find a Healthcare Professional")

# Introduction
with st.container():
    st.markdown("""
    <div class="fade-in">
    Find and book appointments with qualified healthcare professionals. Choose from our network of doctors and trainers specializing in various fields.
    </div>
    """, unsafe_allow_html=True)

# Create two columns for filters and search
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    # Professional type selection with styled buttons
    st.markdown("### I'm looking for:")
    prof_type = st.radio("Select professional type", ["Doctor", "Trainer"], horizontal=True, label_visibility="collapsed")

with col2:
    # Specialty selection
    if prof_type == "Doctor":
        specialties = ["Any", "General", "Cardiologist", "Endocrinologist", "Dermatologist", "Pediatrician", "Neurologist"]
    else:
        specialties = ["Any", "Strength Coach", "Yoga Instructor", "Pilates Instructor", "CrossFit Coach", "Cardio Trainer"]
    
    st.markdown("### Specialty:")
    specialty = st.selectbox("Select specialty", specialties, label_visibility="collapsed")

with col3:
    # Location input
    st.markdown("### Location:")
    location = st.text_input("Enter location", placeholder="City or ZIP code", label_visibility="collapsed")

# Search button in its own container with styling
st.markdown("""
<style>
    .search-button {
        background-color: var(--primary-color);
        color: white;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        text-align: center;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        border: none;
        font-size: 1rem;
        width: 100%;
        margin-top: 1rem;
    }
    .search-button:hover {
        background-color: var(--highlight-color);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
</style>
""", unsafe_allow_html=True)

search_clicked = st.button("Search", key="search_button")

# Display results
if search_clicked:
    # Get users based on filters
    results = get_users(
        role=prof_type.lower(),
        specialty=specialty if specialty != "Any" else None
    )

    # No results message
    if not results:
        st.markdown("""
        <div class="card fade-in" style="text-align: center; padding: 2rem;">
            <span style="font-size: 3rem;">🔍</span>
            <h3>No matching professionals found</h3>
            <p>Try adjusting your filters or check back later as we add more professionals.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if not get_users():
            st.info("Please make sure you've added professionals through the Admin Panel first.")
    else:
        st.markdown(f"<h3>Found {len(results)} {prof_type.lower()}{'s' if len(results) > 1 else ''}</h3>", unsafe_allow_html=True)
        
        # Advanced card display for professionals
        for user in results:
            with st.container():
                st.markdown("""
                <div class="card fade-in" style="margin-bottom: 2rem;">
                    <div style="display: flex; flex-wrap: wrap;">
                """, unsafe_allow_html=True)
                
                cols = st.columns([1, 3, 2])
                
                # Profile column
                with cols[0]:
                    if user.get("photo_url"):
                        st.image(user["photo_url"], width=150)
                    else:
                        st.image("https://via.placeholder.com/150x150?text=No+Image", width=150)
                    
                    # Rating display with stars
                    rating = user.get("rating", 4.5)
                    full_stars = int(rating)
                    half_star = rating - full_stars >= 0.5
                    
                    stars_html = "⭐" * full_stars
                    if half_star:
                        stars_html += "★"
                    
                    st.markdown(f"""
                    <div style="text-align: center; margin-top: 0.5rem;">
                        <div>{stars_html} ({rating:.1f})</div>
                        <div style="color: var(--muted-color); font-size: 0.8rem;">Rated by patients</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Info column
                with cols[1]:
                    title = "Dr. " if prof_type == "Doctor" else ""
                    st.markdown(f"""
                    <h2 style="margin-top: 0;">{title}{user['name']}</h2>
                    <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <span class="badge badge-primary">{user.get('specialty','–')}</span>
                        <span class="badge badge-success">{user.get('location','–')}</span>
                        <span class="badge badge-primary">{user.get('distance_km', 1.2):.1f} km away</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Bio with better formatting
                    bio = user.get("bio","No bio available.")
                    st.markdown(f"""
                    <div style="margin-top: 1rem;">
                        <h4>About</h4>
                        <p>{bio}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Availability calendar preview
                    st.markdown("""
                    <div style="margin-top: 1rem;">
                        <h4>Availability</h4>
                        <div style="display: flex; gap: 0.5rem;">
                            <div style="padding: 8px; background-color: var(--success-color); color: white; border-radius: 5px; text-align: center;">
                                <div style="font-weight: bold;">Today</div>
                                <div style="font-size: 0.8rem;">4 slots</div>
                            </div>
                            <div style="padding: 8px; background-color: var(--success-color); color: white; border-radius: 5px; text-align: center;">
                                <div style="font-weight: bold;">Tomorrow</div>
                                <div style="font-size: 0.8rem;">6 slots</div>
                            </div>
                            <div style="padding: 8px; background-color: var(--muted-color); color: white; border-radius: 5px; text-align: center;">
                                <div style="font-weight: bold;">Wed</div>
                                <div style="font-size: 0.8rem;">Booked</div>
                            </div>
                            <div style="padding: 8px; background-color: var(--success-color); color: white; border-radius: 5px; text-align: center;">
                                <div style="font-weight: bold;">Thu</div>
                                <div style="font-size: 0.8rem;">2 slots</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Booking column
                with cols[2]:
                    st.markdown("""
                    <div style="background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px;">
                        <h3 style="margin-top: 0;">Book an Appointment</h3>
                    """, unsafe_allow_html=True)
                    
                    # Booking form with improved UI
                    with st.form(f"booking_form_{user['id']}"):
                        # Set min date to today and max date to 60 days from now
                        min_date = datetime.now().date()
                        max_date = min_date + timedelta(days=60)
                        
                        date = st.date_input(
                            "Select Date", 
                            key=f"date_{user['id']}", 
                            min_value=min_date,
                            max_value=max_date
                        )
                        
                        # Business hours with more visual time slots
                        st.markdown("#### Select Time")
                        time_slots = [
                            "9:00 AM", "10:00 AM", "11:00 AM", 
                            "1:00 PM", "2:00 PM", "3:00 PM", "4:00 PM"
                        ]
                        
                        # Convert time slot strings to hours
                        slot_to_hour = {
                            "9:00 AM": 9, "10:00 AM": 10, "11:00 AM": 11,
                            "1:00 PM": 13, "2:00 PM": 14, "3:00 PM": 15, "4:00 PM": 16
                        }
                        
                        selected_slot = st.radio(
                            "Select time slot",
                            time_slots,
                            horizontal=True,
                            key=f"slot_{user['id']}",
                            label_visibility="collapsed"
                        )
                        
                        # Get hour from selected slot
                        hour = slot_to_hour[selected_slot]
                        
                        # Optional notes with placeholder text
                        notes = st.text_area(
                            "Additional notes", 
                            key=f"notes_{user['id']}", 
                            placeholder="Any specific concerns or information the professional should know...",
                            label_visibility="collapsed"
                        )
                        
                        # Create time from selected hour
                        time_obj = datetime.now().replace(hour=hour, minute=0, second=0, microsecond=0).time()
                        
                        # Submit button with clear purpose
                        submitted = st.form_submit_button(f"Book {'Appointment' if prof_type=='Doctor' else 'Session'}")
                        
                        if submitted:
                            # Check if selected date and time is in the past
                            selected_datetime = datetime.combine(date, time_obj)
                            now = datetime.now()
                            
                            if selected_datetime < now:
                                st.error("Cannot book appointments in the past")
                            else:
                                # Create appointment
                                req = {
                                    "user_id": user["id"],
                                    "user_name": user["name"],
                                    "type": prof_type.lower(),
                                    "specialty": user.get("specialty",""),
                                    "requested_by": st.session_state.get("username", "current_user"),
                                    "date": selected_datetime,
                                    "status": "pending",
                                    "notes": notes,
                                    "created_at": datetime.utcnow()
                                }
                                
                                # Add appointment to the database
                                appointment_id = add_appointment(req)
                                
                                # Success message with next steps
                                st.success(f"""
                                Successfully booked for {date.strftime('%A, %B %d')} at {time_obj.strftime('%I:%M %p')}!
                                A confirmation will be sent to your contact information.
                                """)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("</div></div>", unsafe_allow_html=True)
else:
    # Show featured professionals when no search has been performed
    featured_users = get_users()
    
    if featured_users:
        st.markdown("""
        <div class="card fade-in">
            <h3>⭐ Featured Professionals</h3>
            <p>Our highly-rated healthcare providers</p>
        """, unsafe_allow_html=True)
        
        # Featured professionals grid
        featured_cols = st.columns(3)
        
        for i, user in enumerate(featured_users[:3]):  # Show max 3 featured users
            with featured_cols[i % 3]:
                title = "Dr. " if user.get("role") == "doctor" else ""
                specialty = user.get("specialty", "Specialist")
                rating = user.get("rating", 4.5)
                
                st.markdown(f"""
                <div style="text-align: center; padding: 1rem; background-color: white; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                    <img src="{user.get('photo_url', 'https://via.placeholder.com/100x100')}" style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover;">
                    <h4>{title}{user.get('name', 'Healthcare Professional')}</h4>
                    <div style="color: var(--primary-color); font-weight: bold;">{specialty}</div>
                    <div>⭐ {rating}/5.0</div>
                    <button onclick="document.getElementById('search_button').click();" style="margin-top: 10px; background-color: var(--primary-color); color: white; border: none; padding: 5px 10px; border-radius: 20px; cursor: pointer;">View Profile</button>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # How it works section
    st.markdown("""
    <div class="card fade-in" style="margin-top: 2rem;">
        <h3>How It Works</h3>
        <div style="display: flex; flex-wrap: wrap; gap: 1rem; margin-top: 1rem;">
            <div style="flex: 1; text-align: center; padding: 1rem;">
                <div style="font-size: 2rem; color: var(--primary-color); margin-bottom: 0.5rem;">🔍</div>
                <h4>1. Search</h4>
                <p>Find the right specialist using our filters</p>
            </div>
            <div style="flex: 1; text-align: center; padding: 1rem;">
                <div style="font-size: 2rem; color: var(--primary-color); margin-bottom: 0.5rem;">📅</div>
                <h4>2. Book</h4>
                <p>Select a convenient date and time</p>
            </div>
            <div style="flex: 1; text-align: center; padding: 1rem;">
                <div style="font-size: 2rem; color: var(--primary-color); margin-bottom: 0.5rem;">👨‍⚕️</div>
                <h4>3. Connect</h4>
                <p>Meet with your healthcare professional</p>
            </div>
            <div style="flex: 1; text-align: center; padding: 1rem;">
                <div style="font-size: 2rem; color: var(--primary-color); margin-bottom: 0.5rem;">📝</div>
                <h4>4. Follow Up</h4>
                <p>Manage appointments and receive care plans</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer information
st.markdown("""
<div style="margin-top: 3rem; text-align: center; color: var(--muted-color); font-size: 0.9rem;">
    <p>Need immediate assistance? Contact our support team at support@healthhub.ai</p>
    <p>Emergency? Please call 911 or your local emergency number</p>
</div>
""", unsafe_allow_html=True)
