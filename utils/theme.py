import streamlit as st

def apply_theme(page_title="HealthHub.AI", set_page=False):
    """Apply consistent theme to all pages
    
    Args:
        page_title: The title to display on the page
        set_page: Whether to also set page config (should only be True if 
                  called directly from a page, not when imported)
    """
    # Only set page config if requested and it hasn't been set before
    if set_page and 'page_config_set' not in st.session_state:
        st.set_page_config(
            page_title=page_title,
            page_icon="🏥",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        st.session_state.page_config_set = True
    
    # Apply custom styling
    st.markdown("""
    <style>
        /* Color Variables */
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
        
        /* Base styles */
        .stApp {
            background-color: var(--background-color);
            color: var(--text-color);
        }
        
        /* Header styling */
        .page-header {
            background: linear-gradient(90deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            color: white;
        }
        
        /* Cards styling */
        .card {
            background-color: var(--card-color);
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
            border-top: 4px solid var(--primary-color);
        }
        
        /* Custom button styling */
        .stButton>button {
            background-color: var(--primary-color);
            color: white;
            border-radius: 20px;
            padding: 0.5rem 1rem;
            border: none;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            background-color: var(--highlight-color);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        
        /* Form elements styling */
        .stTextInput>div>div>input, .stNumberInput>div>div>input {
            border-radius: 20px;
            border: 1px solid #e0e0e0;
            padding: 0.5rem 1rem;
        }
        
        .stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 0.2rem rgba(74, 111, 165, 0.25);
        }
        
        /* Select box styling */
        .stSelectbox>div>div>div {
            border-radius: 20px;
            border: 1px solid #e0e0e0;
        }
        
        /* Metrics styling */
        .metric-card {
            background-color: var(--card-color);
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: var(--primary-color);
        }
        
        .metric-label {
            font-size: 1rem;
            color: var(--muted-color);
        }
        
        /* Status badges */
        .badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        
        .badge-primary {
            background-color: var(--primary-color);
            color: white;
        }
        
        .badge-success {
            background-color: var(--success-color);
            color: white;
        }
        
        .badge-danger {
            background-color: var(--danger-color);
            color: white;
        }
        
        /* Tables styling */
        .styled-table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .styled-table thead tr {
            background-color: var(--primary-color);
            color: white;
            text-align: left;
        }
        
        .styled-table th,
        .styled-table td {
            padding: 12px 15px;
        }
        
        .styled-table tbody tr {
            border-bottom: 1px solid #dddddd;
        }
        
        .styled-table tbody tr:nth-of-type(even) {
            background-color: rgba(255, 255, 255, 0.05);
        }
        
        .styled-table tbody tr:last-of-type {
            border-bottom: 2px solid var(--primary-color);
        }
        
        /* Page transitions */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .fade-in {
            animation: fadeIn 0.5s ease-in-out;
        }
        
        /* Custom progress bar */
        .progress-container {
            width: 100%;
            height: 10px;
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 5px;
            margin: 10px 0;
            overflow: hidden;
        }
        
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, var(--primary-color) 0%, var(--highlight-color) 100%);
            border-radius: 5px;
            transition: width 0.5s ease;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Set page title with consistent format
    st.markdown(f"<h1 class='page-header'>{page_title}</h1>", unsafe_allow_html=True)

def card(title, content, icon=None):
    """Create a styled card with title and content"""
    icon_html = f"<span style='font-size: 1.5rem; margin-right: 0.5rem;'>{icon}</span>" if icon else ""
    
    st.markdown(f"""
    <div class="card fade-in">
        <h3>{icon_html}{title}</h3>
        <div>{content}</div>
    </div>
    """, unsafe_allow_html=True)

def metric_card(label, value, description=None, delta=None, delta_suffix=None):
    """Create a styled metric card"""
    delta_html = ""
    if delta is not None:
        color = "green" if delta >= 0 else "red"
        arrow = "↑" if delta >= 0 else "↓"
        delta_html = f"""
        <div style="color: {color}; font-size: 1rem;">
            {arrow} {abs(delta)}{delta_suffix if delta_suffix else ''}
        </div>
        """
    
    description_html = f"<div style='color: var(--muted-color); font-size: 0.9rem;'>{description}</div>" if description else ""
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
        {description_html}
    </div>
    """, unsafe_allow_html=True)

def badge(text, badge_type="primary"):
    """Create a styled badge"""
    return f'<span class="badge badge-{badge_type}">{text}</span>'

def progress_bar(value, max_value=100):
    """Create a styled progress bar"""
    percentage = int((value / max_value) * 100)
    return f"""
    <div class="progress-container">
        <div class="progress-bar" style="width: {percentage}%"></div>
    </div>
    """

def styled_table(data, columns):
    """Create a styled table from data"""
    header_row = "".join([f"<th>{col}</th>" for col in columns])
    
    rows = ""
    for item in data:
        row = "<tr>"
        for col in columns:
            row += f"<td>{item.get(col, '')}</td>"
        row += "</tr>"
        rows += row
    
    table_html = f"""
    <table class="styled-table">
        <thead>
            <tr>
                {header_row}
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    """
    
    return table_html 