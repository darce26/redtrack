import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import calendar
from db import (
    authenticate_user,
    register_user,
    add_date,
    get_dates,
    update_password,
    delete_record,
    delete_date,
    edit_date
)

# Set page configuration - THIS MUST BE THE FIRST ST COMMAND
st.set_page_config(page_title="RedTrack", page_icon="🗓️", layout="wide")

# Custom CSS for dark sidebar
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background-color: #161b22;  /* Lighter than main background */
        border-right: 1px solid #30363d;
    }
    
    [data-testid="stSidebar"] .stButton button {
        background-color: #21262d;  /* Slightly lighter than sidebar background */
        color: #ffffff;
        border: none;
        border-radius: 5px;
        padding: 10px 15px;
        margin: 5px 0;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    [data-testid="stSidebar"] .stButton button:hover {
        background-color: #2d333b;  /* Lighter shade for hover */
        transform: translateX(3px);
    }
    
    [data-testid="stSidebar"] h1 {
        color: #ffffff;
        font-size: 1.5rem;
        padding: 1rem 0;
        margin: 0;
        text-align: center;
    }
    
    [data-testid="stSidebar"] hr {
        border-color: #30363d;
        margin: 15px 0;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #ffffff;
    }

    /* Make the sidebar scrollbar match the theme */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        scrollbar-color: #30363d #161b22;
    }
    
    /* Webkit browsers custom scrollbar */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"]::-webkit-scrollbar {
        width: 7px;
    }
    
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"]::-webkit-scrollbar-track {
        background: #161b22;
    }
    
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"]::-webkit-scrollbar-thumb {
        background-color: #30363d;
        border-radius: 20px;
        border: 3px solid #161b22;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "user" not in st.session_state:
    st.session_state.user = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "Track"

def login_page():
    st.markdown('<h3 class="main-header"> Login</h3>', unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if authenticate_user(username, password):
            st.session_state.user = username
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid username or password")

def register_page():
    st.markdown('<h3 class="main-header"> Register</h3>', unsafe_allow_html=True)
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    if st.button("Register"):
        if not new_username or not new_password:
            st.error("Please fill in all fields!")
            return
            
        if new_password != confirm_password:
            st.error("Passwords do not match!")
            return
        
        if register_user(new_username, new_password):
            st.success("Registration successful! Please login.")
        else:
            st.error("Username already exists!")

def track_date():
    st.markdown('<h1 class="main-header">Track - Date Entry</h1>', unsafe_allow_html=True)
    st.text("Enter date to track")
    # Add CSS for the current date box
    st.markdown("""
    <style>
    .current-date-box {
        background-color: #1e2530;
        border: 2px solid #30363d;
        border-radius: 5px;
        padding:5px;
        margin: 5px 0;
        text-align: center;
    }
    .current-date-label {
        color: #7c8490;
        font-size: 1.1rem;
        margin-bottom: 5px;
    }
    .current-date {
        color: white;
        font-size: 2rem;
        font-weight: bold;
        margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="date-card">', unsafe_allow_html=True)
        current_date = datetime.now().date()
        
        # Current date in box with larger text
        st.markdown(f"""
        <div class="current-date-box">
            <div class="current-date-label">Current Date</div>
            <div class="current-date">{current_date.strftime('%d/%m/%Y')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        selected_date = st.date_input("Select Date", format="DD/MM/YYYY")
        
        if st.button("Submit Date", key="submit_date"):
            add_date(st.session_state.user, selected_date.strftime("%d/%m/%Y"))
            st.success("Date tracked successfully!")
        st.markdown('</div>', unsafe_allow_html=True)

def view_dates():
    st.markdown('<div class="title-container"><h1>View</h1><p>View and manage your tracked dates</p></div>', unsafe_allow_html=True)
    dates = get_dates(st.session_state.user)
    
    if not dates:
        st.warning("No dates tracked yet.")
        return
    
    # Convert dates to datetime objects and sort them
    tracked_dates = [datetime.strptime(d, "%d/%m/%Y").date() for d in dates]
    tracked_dates.sort()

    # Create a calendar view
    st.subheader("Calendar View")
    
    # Get the current month and year
    if 'calendar_date' not in st.session_state:
        st.session_state.calendar_date = datetime.now()
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("Previous Month"):
            st.session_state.calendar_date -= timedelta(days=31)
            st.rerun()
    with col3:
        if st.button("Next Month"):
            st.session_state.calendar_date += timedelta(days=31)
            st.rerun()
    
    current_month = st.session_state.calendar_date.month
    current_year = st.session_state.calendar_date.year
    
    # Create calendar
    cal = calendar.monthcalendar(current_year, current_month)
    month_name = calendar.month_name[current_month]
    
    st.markdown(f"### {month_name} {current_year}")
    
    # Create calendar grid
    header = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    # Style for dates with entries
    highlight_style = """
    <style>
    .highlight {
        background-color: #ff4b4b;
        color: white;
        padding: 5px;
        border-radius: 5px;
    }
    .calendar-cell {
        width: 40px;
        height: 40px;
        text-align: center;
        padding: 5px;
    }
    </style>
    """
    st.markdown(highlight_style, unsafe_allow_html=True)
    
    # Create the calendar table
    table_html = "<table style='width: 100%; text-align: center;'><tr>"
    for day in header:
        table_html += f"<th class='calendar-cell'>{day}</th>"
    table_html += "</tr>"
    
    for week in cal:
        table_html += "<tr>"
        for day in week:
            if day == 0:
                table_html += "<td class='calendar-cell'></td>"
            else:
                date = datetime(current_year, current_month, day).date()
                if date in tracked_dates:
                    table_html += f"<td class='calendar-cell'><span class='highlight'>{day}</span></td>"
                else:
                    table_html += f"<td class='calendar-cell'>{day}</td>"
        table_html += "</tr>"
    table_html += "</table>"
    
    st.markdown(table_html, unsafe_allow_html=True)
    
    # List view of dates
    st.subheader("List View")
    for date in tracked_dates:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(date.strftime("%B %d, %Y"))
        with col2:
            if st.button("Delete", key=f"delete_{date}"):
                # Get the dates list again to find the index
                dates = get_dates(st.session_state.user)
                date_str = date.strftime("%d/%m/%Y")
                if date_str in dates:
                    delete_date(st.session_state.user, date_str)
                    st.success(f"Date {date.strftime('%B %d, %Y')} deleted successfully!")
                    st.rerun()
                else:
                    st.error("Date not found")

def count_dates():
    st.markdown('<div class="title-container"><h1>Count</h1><p>View the difference between your tracked dates</p></div>', unsafe_allow_html=True)
    dates = get_dates(st.session_state.user)
    
    if len(dates) < 2:
        st.warning("You need at least 2 date entries to see the count.")
        return
    
    # Convert and sort dates
    tracked_dates = [datetime.strptime(d, "%d/%m/%Y").date() for d in dates]
    tracked_dates.sort()
    
    # Create data for the table
    table_data = []
    for i in range(1, len(tracked_dates)):
        initial_date = tracked_dates[i-1]
        recent_date = tracked_dates[i]
        days_difference = (recent_date - initial_date).days
        table_data.append({
            "S.No": f"{i}",  # Convert to string to avoid index column
            "Initial Date": initial_date.strftime("%d/%m/%Y"),
            "Recent Date": recent_date.strftime("%d/%m/%Y"),
            "Days Count": days_difference
        })
    
    # Convert to DataFrame and set index to S.No
    df = pd.DataFrame(table_data)
    df.set_index('S.No', inplace=True)  # Use S.No as index
    st.table(df)

def settings():
    st.markdown('<div class="title-container"><h1>Settings</h1><p>Manage your account settings</p></div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="settings-section">', unsafe_allow_html=True)
        st.subheader("Change Password")
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        if st.button("Update Password"):
            if authenticate_user(st.session_state.user, current_password):
                if new_password == confirm_password:
                    update_password(st.session_state.user, new_password)
                    st.success("Password updated successfully!")
                else:
                    st.error("New passwords do not match!")
            else:
                st.error("Current password is incorrect!")
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    if not st.session_state.user:
        # Login/Register page layout
        col1, col2, col3 = st.columns([3,4,3])
        
        # Left column - Title
        with col2:
            st.title("Red Track")
        
        # Right column - Login/Register
        with col3:
            auth_mode = st.radio("", ["Login", "Register"], horizontal=True, key="auth_mode")
            if auth_mode == "Login":
                login_page()
            else:
                register_page()
    
    else:
        # Dashboard layout after login
        # Sidebar for navigation
        with st.sidebar:
            st.title(f"Welcome {st.session_state.user}")
            st.markdown("---")
            
            # Navigation buttons
            if st.button("Track", key="nav_track", use_container_width=True):
                st.session_state.current_page = "Track"
                st.rerun()
            
            if st.button("View", key="nav_view", use_container_width=True):
                st.session_state.current_page = "View"
                st.rerun()
            
            if st.button("Count", key="nav_count", use_container_width=True):
                st.session_state.current_page = "Count"
                st.rerun()
            
            if st.button("Settings", key="nav_settings", use_container_width=True):
                st.session_state.current_page = "Settings"
                st.rerun()
            
            st.markdown("---")
            if st.button("Logout", use_container_width=True):
                st.session_state.user = None
                st.session_state.current_page = "Track"
                st.rerun()
        
        # Main content area
        if st.session_state.current_page == "Track":
            col1, col2, col3 = st.columns([2,3,1])
            with col2:
                st.title("Red Track")
                st.text("")
                st.text("")
            track_date()
        elif st.session_state.current_page == "View":
            col1, col2, col3 = st.columns([2, 3, 1])
            with col2:
                st.title("Red Track")
                st.text("")
                st.text("")
            view_dates()
        elif st.session_state.current_page == "Count":
            col1, col2, col3 = st.columns([2, 3, 1])
            with col2:
                st.title("Red Track")
                st.text("")
                st.text("")
            count_dates()
        elif st.session_state.current_page == "Settings":
            col1, col2, col3 = st.columns([2, 3, 1])
            with col2:
                st.title("Red Track")
                st.text("")
                st.text("")
            settings()

if __name__ == "__main__":
    main() 