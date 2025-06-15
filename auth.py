import streamlit as st
import json
import os
import re
from hashlib import sha256
from typing import Dict, List, Optional
from datetime import datetime

# File to store user credentials and groups
USERS_DB_FILE = "users.json"
GROUPS_DB_FILE = "groups.json"

def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength
    Returns: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    
    return True, ""

def init_db():
    """Initialize database files if they don't exist"""
    if not os.path.exists(USERS_DB_FILE):
        # Create initial user
        initial_users = {
            "swa u gou": {
                "password": hash_password("swa123"),
                "created_at": datetime.now().isoformat()
            }
        }
        with open(USERS_DB_FILE, "w") as f:
            json.dump(initial_users, f)
    else:
        # Ensure existing users have groups field
        try:
            with open(USERS_DB_FILE, "r") as f:
                users = json.load(f)
            updated = False
            for username in users:
                if "groups" not in users[username]:
                    users[username]["groups"] = []
                    updated = True
            if updated:
                with open(USERS_DB_FILE, "w") as f:
                    json.dump(users, f)
        except Exception as e:
            st.error(f"Error updating users file: {str(e)}")

    # Initialize groups file
    if not os.path.exists(GROUPS_DB_FILE):
        with open(GROUPS_DB_FILE, "w") as f:
            json.dump({}, f)

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return sha256(password.encode()).hexdigest()

def load_users() -> Dict:
    """Load users from the JSON file"""
    try:
        with open(USERS_DB_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading users: {str(e)}")
        return {}

def save_users(users: Dict):
    """Save users to the JSON file"""
    try:
        with open(USERS_DB_FILE, "w") as f:
            json.dump(users, f)
    except Exception as e:
        st.error(f"Error saving users: {str(e)}")

def load_groups() -> Dict:
    """Load groups from the JSON file"""
    try:
        with open(GROUPS_DB_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading groups: {str(e)}")
        return {}

def save_groups(groups: Dict):
    """Save groups to the JSON file"""
    try:
        with open(GROUPS_DB_FILE, "w") as f:
            json.dump(groups, f)
    except Exception as e:
        st.error(f"Error saving groups: {str(e)}")

def create_user(username: str, password: str, confirm_password: str) -> tuple[bool, str]:
    """
    Create a new user
    Returns: (success, message)
    """
    # Check if passwords match
    if password != confirm_password:
        return False, "Passwords do not match"
    
    # Validate password strength
    is_valid, error_message = validate_password(password)
    if not is_valid:
        return False, error_message
    
    users = load_users()
    if username in users:
        return False, "Username already exists"
    
    users[username] = {
        "password": hash_password(password),
        "created_at": datetime.now().isoformat(),
        "groups": []  # List of group IDs the user belongs to
    }
    save_users(users)
    return True, "User created successfully"

def authenticate_user(username: str, password: str) -> bool:
    """Authenticate user credentials"""
    users = load_users()
    if username not in users:
        return False
    
    return users[username]["password"] == hash_password(password)

def create_group(name: str, creator_username: str, description: str = "") -> str:
    """Create a new expense group"""
    try:
        groups = load_groups()
        users = load_users()
        
        # Generate a unique group ID
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        group_id = f"group_{timestamp}_{len(groups)}"
        
        # Create the group
        groups[group_id] = {
            "name": name,
            "description": description,
            "creator": creator_username,
            "members": [creator_username],
            "created_at": datetime.now().isoformat(),
            "invites_pending": []
        }
        
        # Add group to user's groups
        if creator_username in users:
            if "groups" not in users[creator_username]:
                users[creator_username]["groups"] = []
            users[creator_username]["groups"].append(group_id)
            
            save_groups(groups)
            save_users(users)
            return group_id
        else:
            st.error("Creator user not found")
            return ""
    except Exception as e:
        st.error(f"Error creating group: {str(e)}")
        return ""

def invite_to_group(group_id: str, username: str, inviter_username: str) -> bool:
    """Invite a user to a group"""
    try:
        groups = load_groups()
        users = load_users()
        
        if (group_id not in groups or 
            username not in users or 
            inviter_username not in groups[group_id]["members"]):
            return False
        
        if username not in groups[group_id]["invites_pending"] and username not in groups[group_id]["members"]:
            groups[group_id]["invites_pending"].append(username)
            save_groups(groups)
            return True
        return False
    except Exception as e:
        st.error(f"Error inviting to group: {str(e)}")
        return False

def accept_group_invite(group_id: str, username: str) -> bool:
    """Accept a group invitation"""
    try:
        groups = load_groups()
        users = load_users()
        
        if (group_id not in groups or 
            username not in groups[group_id]["invites_pending"]):
            return False
        
        # Add user to group
        groups[group_id]["members"].append(username)
        groups[group_id]["invites_pending"].remove(username)
        
        # Add group to user's groups
        if "groups" not in users[username]:
            users[username]["groups"] = []
        users[username]["groups"].append(group_id)
        
        save_groups(groups)
        save_users(users)
        return True
    except Exception as e:
        st.error(f"Error accepting invite: {str(e)}")
        return False

def get_user_groups(username: str) -> List[Dict]:
    """Get all groups a user belongs to"""
    try:
        users = load_users()
        groups = load_groups()
        
        if username not in users:
            return []
        
        if "groups" not in users[username]:
            users[username]["groups"] = []
            save_users(users)
            return []
        
        user_groups = []
        for group_id in users[username]["groups"]:
            if group_id in groups:
                group_info = groups[group_id].copy()
                group_info["id"] = group_id
                user_groups.append(group_info)
        
        return user_groups
    except Exception as e:
        st.error(f"Error getting user groups: {str(e)}")
        return []

def get_user_pending_invites(username: str) -> List[Dict]:
    """Get all pending group invites for a user"""
    try:
        groups = load_groups()
        
        pending_invites = []
        for group_id, group_info in groups.items():
            if username in group_info.get("invites_pending", []):
                invite_info = {
                    "group_id": group_id,
                    "group_name": group_info["name"],
                    "creator": group_info["creator"],
                    "description": group_info.get("description", "")
                }
                pending_invites.append(invite_info)
        
        return pending_invites
    except Exception as e:
        st.error(f"Error getting pending invites: {str(e)}")
        return []

def login_page():
    """Display and handle login page"""
    # Initialize session state variables if they don't exist
    if "show_signup" not in st.session_state:
        st.session_state.show_signup = False
    if "user_logged_in" not in st.session_state:
        st.session_state.user_logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = None

    if not st.session_state.user_logged_in:
        # Custom CSS for vibrant, modern look (no container)
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@500;700&display=swap');
            html, body, .main {
                height: 100%;
                font-family: 'Quicksand', sans-serif;
                background: linear-gradient(135deg, #f8ffae 0%, #43cea2 100%);
            }
            .tracker-heading {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.7rem;
                margin-bottom: 1.5rem;
                margin-top: 2.5rem;
            }
            .tracker-icon {
                width: 38px;
                height: 38px;
                object-fit: cover;
                border-radius: 8px;
                box-shadow: 0 2px 8px 0 rgba(67,206,162,0.15);
                background: #fff;
            }
            .tracker-title {
                font-size: 2rem;
                font-weight: 800;
                color: #333333;
                letter-spacing: 1px;
                margin: 0;
            }
            .stTextInput > div > input {
                border-radius: 10px;
                background: #f0f9f7;
                border: 1.5px solid #43cea2;
                font-size: 1.1rem;
                padding: 0.5rem 0.75rem;
            }
            .stTextInput > div > input:focus {
                border: 2px solid #185a9d;
                background: #e6f7ff;
            }
            .stTextArea textarea {
                border-radius: 10px;
                background: #f0f9f7;
                border: 1.5px solid #43cea2;
                font-size: 1.1rem;
            }
            .stTextArea textarea:focus {
                border: 2px solid #185a9d;
                background: #e6f7ff;
            }
            .st-bb, .st-bc {
                border-radius: 10px !important;
            }
            .button-row {
                display: flex;
                justify-content: center;
                gap: 0.7rem;
                margin-bottom: 0.5rem;
            }
            .button-row .stButton > button {
                width: 100%;
                min-width: 80px;
                max-width: 120px;
                font-size: 0.95rem;
                padding: 0.25rem 0.5rem;
                margin-bottom: 0;
            }
            div[data-testid=\"stButton\"] > button {
                width: 40%;
                min-width: 80px;
                max-width: 120px;
                background: linear-gradient(90deg, #43cea2 0%, #185a9d 100%);
                color: white;
                border: none;
                padding: 0.25rem 0.5rem;
                border-radius: 10px;
                font-weight: 700;
                font-size: 0.95rem;
                margin-bottom: 0.5rem;
                box-shadow: 0 2px 8px 0 rgba(67,206,162,0.10);
                transition: background 0.3s, transform 0.2s;
                display: block;
                margin-left: auto;
                margin-right: auto;
            }
            div[data-testid=\"stButton\"] > button:hover {
                background: linear-gradient(90deg, #185a9d 0%, #43cea2 100%);
                color: #fff;
                transform: translateY(-2px) scale(1.03);
            }
            div[data-testid=\"stButton\"] > button[data-testid=\"baseButton-secondary\"] {
                background: linear-gradient(90deg, #f7971e 0%, #ffd200 100%);
                color: #222;
            }
            div[data-testid=\"stButton\"] > button[data-testid=\"baseButton-secondary\"]:hover {
                background: linear-gradient(90deg, #ffd200 0%, #f7971e 100%);
                color: #222;
            }
            .stSubheader, .stMarkdown h2, .stMarkdown h3 {
                color: #185a9d;
                font-weight: 700;
            }
            </style>
        """, unsafe_allow_html=True)

        # Heading with icon and title
        st.markdown(f'''
            <div class="tracker-heading">
                <img src="https://img.icons8.com/color/96/000000/bus.png" alt="Travel Icon" class="tracker-icon" width="38" height="38">
                <span class="tracker-title">Travel Expense Tracker</span>
            </div>
        ''', unsafe_allow_html=True)
        
        if not st.session_state.show_signup:
            # Login form
            st.subheader("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            # Button row for Login and Sign Up
            st.markdown('<div class="button-row">', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                login_clicked = st.button("Login", type="primary", key="login_btn")
            with col2:
                signup_clicked = st.button("Sign Up", type="secondary", key="signup_btn")
            st.markdown('</div>', unsafe_allow_html=True)
            if login_clicked:
                if authenticate_user(username, password):
                    st.session_state.user_logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            if signup_clicked:
                st.session_state.show_signup = True
                st.rerun()
        
        else:
            # Signup form
            st.subheader("Sign Up")
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            # Password requirements display
            st.markdown("""
                **Password Requirements:**
                - At least 8 characters long
                - At least one uppercase letter
                - At least one lowercase letter
                - At least one number
                - At least one special character
            """)
            # Button row for Create Account and Back to Login
            st.markdown('<div class="button-row">', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                create_clicked = st.button("Create Account", type="primary", key="create_btn")
            with col2:
                back_clicked = st.button("Back to Login", type="secondary", key="back_btn")
            st.markdown('</div>', unsafe_allow_html=True)
            if create_clicked:
                success, message = create_user(new_username, new_password, confirm_password)
                if success:
                    st.success(message)
                    st.session_state.show_signup = False
                    st.rerun()
                else:
                    st.error(message)
            if back_clicked:
                st.session_state.show_signup = False
                st.rerun()
    
    return st.session_state.user_logged_in, st.session_state.username

def logout():
    """Log out the current user"""
    st.session_state.user_logged_in = False
    st.session_state.username = None
    st.rerun()

# Initialize database when the module is imported
init_db() 