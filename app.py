# pages/1_Home.py
import streamlit as st
import os
from streamlit_option_menu import option_menu
from datetime import datetime
from pathlib import Path
import base64
import time
import importlib
import sys

# Ensure required directories exist
Path("data").mkdir(exist_ok=True)

# Initialize session state variables if they don't exist
if 'user_id' not in st.session_state:
    st.session_state.user_id = "current_user"  # Default anonymous user
if 'username' not in st.session_state:
    st.session_state.username = "Guest"
if 'role' not in st.session_state:
    st.session_state.role = "user"  # Options: user, doctor, trainer, admin
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
# Always use dark theme
st.session_state.theme = "dark"

# Page config
st.set_page_config(
    page_title="HealthHub.AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to load and encode images for background
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Use a placeholder image URL if the local file doesn't exist
def get_img_with_fallback(local_path, placeholder_url="https://images.unsplash.com/photo-1505751172876-fa1923c5c528?ixlib=rb-4.0.3"):
    try:
        return get_base64_of_bin_file(local_path)
    except:
        return placeholder_url

# Add custom CSS with theme support
def get_theme_css():
    # Always return dark theme CSS
    return """
    :root {
        --primary-color: #7A9E9F;
        --secondary-color: #4F6367;
        --background-color: #2A2D34;
        --card-color: #3E4049;
        --text-color: #EEF5DB;
        --highlight-color: #82B3AC;
        --danger-color: #B8336A;
        --success-color: #7FB069;
        --muted-color: #9DA3B3;
    }
    """

# Apply the custom CSS
st.markdown(f"""
<style>
    {get_theme_css()}
    
    /* Base styles */
    .stApp {{
        background-color: var(--background-color);
        color: var(--text-color);
    }}
    
    /* Header styling */
    .main-header {{
        background: linear-gradient(90deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }}
    
    /* Title styling */
    .main-title {{
        color: white;
        text-align: center;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin-bottom: 0.5rem;
    }}
    
    /* Special color */
    .highlight {{
        color: #F9EBB2;
        font-weight: 800;
    }}
    
    /* Subtitle styling */
    .subtitle {{
        color: rgba(255, 255, 255, 0.9);
        text-align: center;
        font-size: 1.2rem;
        font-family: 'Roboto', sans-serif;
        font-weight: 400;
    }}
    
    /* Feature cards */
    .feature-card {{
        background-color: var(--card-color);
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        height: 100%;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border-top: 4px solid var(--primary-color);
    }}
    
    .feature-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
    }}
    
    /* Feature icons */
    .feature-icon {{
        font-size: 2.5rem;
        margin-bottom: 1rem;
        color: var(--primary-color);
    }}
    
    /* Custom sidebar styling */
    .sidebar .sidebar-content {{
        background-color: var(--secondary-color);
    }}
    
    /* Custom button styles */
    .stButton>button {{
        background-color: var(--primary-color);
        color: white;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        border: none;
        transition: all 0.3s ease;
    }}
    
    .stButton>button:hover {{
        background-color: var(--highlight-color);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }}
    
    /* Card styling for different sections */
    .section-card {{
        background-color: var(--card-color);
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
    }}
    
    /* Footer styling */
    .footer {{
        text-align: center;
        color: var(--muted-color);
        font-size: 0.9rem;
        margin-top: 3rem;
        padding: 1rem;
        border-top: 1px solid rgba(0, 0, 0, 0.1);
    }}
    
    /* Success/info/warning/error message colors */
    .success-text {{ color: var(--success-color); }}
    .danger-text {{ color: var(--danger-color); }}
    
    /* Badge styling */
    .badge {{
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-right: 0.5rem;
    }}
    
    .badge-primary {{
        background-color: var(--primary-color);
        color: white;
    }}
    
    .badge-success {{
        background-color: var(--success-color);
        color: white;
    }}
    
    .badge-danger {{
        background-color: var(--danger-color);
        color: white;
    }}
    
    /* Navigation highlight */
    .nav-highlight {{
        border-left: 4px solid var(--highlight-color);
        background-color: rgba(0, 0, 0, 0.05);
    }}
    
    /* Custom progress bar */
    .progress-container {{
        width: 100%;
        height: 20px;
        background-color: #e0e0e0;
        border-radius: 10px;
        margin: 10px 0;
        overflow: hidden;
    }}
    
    .progress-bar {{
        height: 100%;
        background: linear-gradient(90deg, var(--primary-color) 0%, var(--highlight-color) 100%);
        border-radius: 10px;
        transition: width 0.5s ease;
    }}
    
    /* Animation for page transitions */
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    
    .fade-in {{
        animation: fadeIn 0.5s ease-in-out;
    }}
    
    /* Profile section styling */
    .profile-header {{
        display: flex;
        align-items: center;
        padding: 1rem;
        background-color: var(--card-color);
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }}
    
    .profile-avatar {{
        width: 50px;
        height: 50px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 1rem;
    }}
    
    .profile-info {{
        display: flex;
        flex-direction: column;
    }}
    
    .profile-name {{
        font-weight: bold;
        color: var(--text-color);
    }}
    
    .profile-role {{
        color: var(--muted-color);
        font-size: 0.8rem;
    }}
</style>
""", unsafe_allow_html=True)

# Simple authentication
def login_form():
    with st.container():
        st.markdown('<div class="section-card fade-in">', unsafe_allow_html=True)
        st.subheader("Login to HealthHub.AI")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.button("Login"):
                # Demo authentication logic (replace with actual auth in production)
                if username == "admin" and password == "admin":
                    st.session_state.username = "Admin User"
                    st.session_state.role = "admin"
                    st.session_state.authenticated = True
                    st.success("Login successful! Redirecting...")
                    time.sleep(1)
                    st.rerun()
                elif username == "doctor" and password == "doctor":
                    st.session_state.username = "Dr. Johnson"
                    st.session_state.role = "doctor"
                    st.session_state.user_id = 1  # Demo doctor ID
                    st.session_state.authenticated = True
                    st.success("Login successful! Redirecting...")
                    time.sleep(1)
                    st.rerun()
                elif username and password:  # Any user/pass combo works for demo
                    st.session_state.username = username
                    st.session_state.role = "user"
                    st.session_state.authenticated = True
                    st.success("Login successful! Redirecting...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Please enter username and password")
        
        with col2:
            st.markdown("""
            ### Demo Accounts
            - **Admin**: admin/admin
            - **Doctor**: doctor/doctor
            - **User**: any username/password
            
            Don't have an account? Just enter any username and password to try out the app!
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-card fade-in">', unsafe_allow_html=True)
        st.markdown("""
        ### About HealthHub.AI
        
        HealthHub.AI is a comprehensive platform that combines multiple health and wellness features:
        
        - **Disease Prediction**: Assess your risk for various conditions
        - **Doctor Network**: Connect with healthcare professionals
        - **Health Records**: Securely store and manage your medical data
        - **AI Training**: Get personalized workout guidance
        """)
        st.markdown('</div>', unsafe_allow_html=True)

# Sidebar with user profile and navigation
def build_sidebar():
    with st.sidebar:
        # User profile section in sidebar
        if st.session_state.authenticated:
            st.markdown(f"""
            <div class="profile-header">
                <img src="https://xsgames.co/randomusers/avatar.php?g=pixel&key={st.session_state.username}" class="profile-avatar">
                <div class="profile-info">
                    <div class="profile-name">{st.session_state.username}</div>
                    <div class="profile-role">{st.session_state.role.capitalize()}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### Navigation")
        
        # Different menu options based on user role
        if st.session_state.role == "admin":
            options = [
                "Dashboard", 
                "Disease Risk Predictor", 
                "Find a Doctor",
                "Health Records", 
                "Prescription OCR",
                "Admin Panel"
            ]
            icons = [
                "house-fill", 
                "activity", 
                "people-fill",
                "file-earmark-medical-fill", 
                "file-text-fill",
                "gear-fill"
            ]
        elif st.session_state.role == "doctor":
            options = [
                "Dashboard", 
                "Doctor Panel", 
                "Find a Doctor",
                "Health Records",
                "Prescription OCR"
            ]
            icons = [
                "house-fill", 
                "clipboard2-pulse-fill", 
                "people-fill",
                "file-earmark-medical-fill",
                "file-text-fill"
            ]
        else:
            options = [
                "Dashboard", 
                "Disease Risk Predictor", 
                "Find a Doctor",
                "Health Records", 
                "Prescription OCR",
                "AI Personal Trainer",
                "Diet Planner"
            ]
            icons = [
                "house-fill", 
                "activity", 
                "people-fill",
                "file-earmark-medical-fill", 
                "file-text-fill",
                "trophy-fill",
                "egg-fill"
            ]
        
        selected = option_menu(
            menu_title=None,
            options=options,
            icons=icons,
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "var(--primary-color)", "font-size": "1rem"},
                "nav-link": {
                    "font-size": "1rem",
                    "text-align": "left",
                    "margin": "0px",
                    "padding": "10px",
                    "--hover-color": "rgba(0, 0, 0, 0.05)",
                },
                "nav-link-selected": {"background-color": "var(--primary-color)"},
            }
        )
        
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.username = "Guest"
            st.session_state.role = "user"
            st.rerun()
                
        return selected

# Helper function to load page modules
def load_page(page_name):
    try:
        # Add the current directory to sys.path if needed
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # Import the module
        if page_name == "Disease_Risk_Predictor.py":
            import pages.Disease_Risk_Predictor as module
        elif page_name == "Find_a_Doctor.py":
            import pages.Find_a_Doctor as module
        elif page_name == "Health_Records.py":
            import pages.Health_Records as module
        elif page_name == "Admin_panel.py":
            import pages.Admin_panel as module
        elif page_name == "Doctor_panel.py":
            import pages.Doctor_panel as module
        elif page_name == "AI_Personal_Trainer.py":
            import pages.AI_Personal_Trainer as module
        elif page_name == "Diet_Planner.py":
            import pages.Diet_Planner as module
        elif page_name == "Prescription_OCR.py":
            import pages.Prescription_OCR as module
        else:
            st.error(f"Page {page_name} not found")
            return False
        
        # Reload the module to get fresh content
        importlib.reload(module)
        return True
    except Exception as e:
        st.error(f"Error loading page {page_name}: {str(e)}")
        return False

# Main content based on selection
def main():
    # If not authenticated, show login form
    if not st.session_state.authenticated:
        login_form()
        return
    
    # Get selected menu item from sidebar
    selected = build_sidebar()
    
    # Display main content based on selection
    if selected == "Dashboard":
        show_dashboard()
    elif selected == "Disease Risk Predictor":
        if not load_page("Disease_Risk_Predictor.py"):
            st.error("Could not load Disease Risk Predictor page")
    elif selected == "Find a Doctor":
        if not load_page("Find_a_Doctor.py"):
            st.error("Could not load Find a Doctor page")
    elif selected == "Health Records":
        if not load_page("Health_Records.py"):
            st.error("Could not load Health Records page")
    elif selected == "Admin Panel":
        if not load_page("Admin_panel.py"):
            st.error("Could not load Admin Panel page")
    elif selected == "Doctor Panel":
        if not load_page("Doctor_panel.py"):
            st.error("Could not load Doctor Panel page")
    elif selected == "AI Personal Trainer":
        if not load_page("AI_Personal_Trainer.py"):
            st.error("Could not load AI Personal Trainer page")
    elif selected == "Diet Planner":
        if not load_page("Diet_Planner.py"):
            st.error("Could not load Diet Planner page")
    elif selected == "Prescription OCR":
        if not load_page("Prescription_OCR.py"):
            st.warning("Creating Prescription OCR page...")
            create_prescription_ocr_page()

def create_prescription_ocr_page():
    """Temporarily display the Prescription OCR page until the module is created"""
    st.markdown('<div class="section-card fade-in">', unsafe_allow_html=True)
    st.title("📄 Prescription OCR")
    st.markdown("This feature will be available soon. We're working on creating it.")
    st.markdown("</div>", unsafe_allow_html=True)

def show_dashboard():
    # --- HERO SECTION ---
    st.markdown("""
    <div class="main-header fade-in">
      <h1 class="main-title">
        Welcome to <span class="highlight">HealthHub.AI</span>
      </h1>
      <p class="subtitle">
        Your unified AI‑driven health & fitness platform — predict, train, plan, and secure your health journey
      </p>
    </div>
    """, unsafe_allow_html=True)

    # User-specific greeting
    st.markdown(f"""
    <div class="section-card fade-in">
        <h3>Hello, {st.session_state.username}! 👋</h3>
        <p>Welcome to your health dashboard. Here's a summary of your health journey.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats overview
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="feature-card fade-in">
            <div class="feature-icon">📊</div>
            <h3>Health Score</h3>
            <h2 class="success-text">86 / 100</h2>
            <div class="progress-container">
                <div class="progress-bar" style="width: 86%"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card fade-in">
            <div class="feature-icon">💪</div>
            <h3>Activity</h3>
            <h2>7,568 steps</h2>
            <p>2.4 miles today</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="feature-card fade-in">
            <div class="feature-icon">🔔</div>
            <h3>Reminders</h3>
            <p><span class="badge badge-primary">2</span> Upcoming appointments</p>
            <p><span class="badge badge-success">1</span> Medication reminder</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="feature-card fade-in">
            <div class="feature-icon">🏆</div>
            <h3>Goals</h3>
            <p>Walk 10,000 steps</p>
            <div class="progress-container">
                <div class="progress-bar" style="width: 75%"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --- FEATURE HIGHLIGHTS ---
    st.markdown('<div class="section-card fade-in">', unsafe_allow_html=True)
    st.subheader("🚀 What You Can Do")
    
    cols = st.columns(4)
    features = [
        ("🏥 Risk Predictor", "Get explainable risk scores for 10+ diseases based on your symptoms and metrics."),
        ("💪 AI Trainer", "Real‑time pose correction & rep counting with visual feedback."),
        ("🥗 Diet Planner", "Personalized 7‑day meal plans based on your preferences and health goals."),
        ("🔐 Health Records", "Securely store and manage your health documents with blockchain verification."),
    ]
    
    for i, (title, desc) in enumerate(features):
        with cols[i]:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">{title[0]}</div>
                <h3>{title[2:]}</h3>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Recent Activity
    st.markdown('<div class="section-card fade-in">', unsafe_allow_html=True)
    st.subheader("Recent Activity")
    
    activity_col1, activity_col2 = st.columns([2, 1])
    
    with activity_col1:
        activities = [
            {"type": "appointment", "date": "2023-06-10", "description": "Appointment with Dr. Smith", "status": "completed"},
            {"type": "record", "date": "2023-06-08", "description": "Uploaded blood test results", "status": "verified"},
            {"type": "prediction", "date": "2023-06-05", "description": "Diabetes risk assessment", "status": "low risk"},
            {"type": "workout", "date": "2023-06-03", "description": "30 min strength training", "status": "completed"}
        ]
        
        for activity in activities:
            status_badge = ""
            if activity["status"] == "completed" or activity["status"] == "verified":
                status_badge = f'<span class="badge badge-success">{activity["status"]}</span>'
            elif activity["status"] == "low risk":
                status_badge = f'<span class="badge badge-success">{activity["status"]}</span>'
            else:
                status_badge = f'<span class="badge badge-primary">{activity["status"]}</span>'
                
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px; padding: 10px; background-color: var(--card-color); border-radius: 5px;">
                <div>
                    <strong>{activity["description"]}</strong>
                    <div style="color: var(--muted-color); font-size: 0.8rem;">{activity["date"]}</div>
                </div>
                <div>
                    {status_badge}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with activity_col2:
        st.markdown("### Upcoming")
        
        st.markdown("""
        <div style="padding: 15px; background-color: var(--primary-color); color: white; border-radius: 10px; margin-bottom: 10px;">
            <div style="font-size: 0.8rem;">Tomorrow, 10:00 AM</div>
            <div style="font-weight: bold;">Appointment with Dr. Johnson</div>
            <div style="font-size: 0.9rem;">Cardiology Check-up</div>
        </div>
        
        <div style="padding: 15px; background-color: var(--card-color); border-radius: 10px; border-left: 4px solid var(--primary-color);">
            <div style="font-size: 0.8rem;">In 3 days</div>
            <div style="font-weight: bold;">Lab Results Expected</div>
            <div style="font-size: 0.9rem;">Annual blood work</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # --- FOOTER ---
    st.markdown("""
    <div class="footer">
      © 2025 HealthHub.AI •  
      <a href="https://github.com/YourRepo/HealthHub.Ai" target="_blank">GitHub</a> •  
      <a href="mailto:contact@healthhub.ai">Contact</a>
    </div>
    """, unsafe_allow_html=True)

# Run the main function
if __name__ == "__main__":
    main()
