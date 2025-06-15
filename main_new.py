import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px
import plotly.graph_objects as go
from database import (
    create_user, verify_user, add_expense, load_expenses,
    create_group, get_user_groups, get_user_pending_invites,
    accept_group_invite, add_group_expense, get_group_expenses,
    get_group_members, get_group_balance
)

# Set page configuration
st.set_page_config(
    page_title="Travel Expense Tracker",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background: linear-gradient(45deg, #6f42c1, #8e44ad);
        color: white;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(45deg, #8e44ad, #6f42c1);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(111, 66, 193, 0.2);
    }
    .login-container {
        background: rgba(255, 255, 255, 0.95);
        padding: 2.5rem;
        border-radius: 16px;
        box-shadow: 0 8px 16px rgba(111, 66, 193, 0.1);
        transition: all 0.3s ease;
        border: 1px solid rgba(111, 66, 193, 0.1);
    }
    .login-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 20px rgba(111, 66, 193, 0.15);
    }
    .login-title {
        color: #6f42c1;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
        border: 2px solid #e9ecef;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    .stTextInput>div>div>input:focus {
        border-color: #6f42c1;
        box-shadow: 0 0 0 2px rgba(111, 66, 193, 0.2);
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .title-text {
        background: linear-gradient(45deg, #6f42c1, #8e44ad);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 3rem;
        animation: fadeIn 1s ease-out;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .metric-box {
        background-color: white;
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 105, 148, 0.1);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .metric-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0, 105, 148, 0.15);
    }
    .metric-title {
        color: #006994;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    .metric-value {
        color: #006994;
        font-size: 1.8rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .metric-subtitle {
        color: #006994;
        font-size: 0.8rem;
    }
    .group-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(111, 66, 193, 0.1);
        transition: all 0.3s ease;
    }
    .group-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(111, 66, 193, 0.15);
    }
    .logout-button {
        position: fixed;
        bottom: 20px;
        left: 20px;
        z-index: 1000;
    }
    .logout-button button {
        background: #006994;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .logout-button button:hover {
        background: #005177;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 105, 148, 0.2);
    }
    .signup-title {
        color: #6f42c1;
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
    }
    .section-title {
        color: #006994;  /* Ocean blue color */
        font-weight: 700;
        display: inline-block;
        margin-right: 2rem;
        font-size: 1.5rem;
        padding: 0.5rem 1rem;
        background: rgba(0, 105, 148, 0.1);  /* Light ocean blue background */
        border-radius: 8px;
    }
    .section-container {
        display: flex;
        align-items: center;
        margin-bottom: 2rem;
        gap: 2rem;
        justify-content: flex-start;  /* Align items to the start */
    }
    .welcome-message {
        color: #006994;
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 2rem;
        padding: 1rem;
        background: rgba(0, 105, 148, 0.1);
        border-radius: 12px;
        display: inline-block;
        position: absolute;
        top: 20px;
        right: 20px;
    }
    .expense-details {
        margin-top: 1rem;
        padding: 1rem;
        background: rgba(0, 105, 148, 0.05);
        border-radius: 8px;
    }
    .expense-detail-item {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid rgba(0, 105, 148, 0.1);
    }
    .expense-detail-item:last-child {
        border-bottom: none;
    }
    </style>
""", unsafe_allow_html=True)

def login_page():
    st.markdown("""
        <div style='display: flex; justify-content: center; align-items: center; height: 180px;'>
            <div style='width: 300px; height: 300px; display: flex; justify-content: center; align-items: center; background: #fff; border-radius: 16px; border: 2px solid #e9ecef;'>
                <h1 style='font-weight: 800; font-size: 2rem; margin: 0;'>✈️ Travel Expense Tracker</h1>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Add an attractive travel-related image below the heading
    st.image(
        "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=600&q=80",
        width=300,
        caption="",
        use_column_width=False
    )
    
    # Create two columns for login and signup
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="login-title">🔐 Login</div>', unsafe_allow_html=True)
        with st.form("login_form"):
            login_username = st.text_input("Username", key="login_username")
            login_password = st.text_input("Password", type="password", key="login_password")
            login_submitted = st.form_submit_button("Login")
            
            if login_submitted:
                if verify_user(login_username, login_password):
                    return True, login_username
                else:
                    st.error("Invalid username or password")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="login-title">📝 Sign Up</div>', unsafe_allow_html=True)
        with st.form("signup_form"):
            signup_username = st.text_input("Username", key="signup_username")
            signup_password = st.text_input("Password", type="password", key="signup_password")
            signup_submitted = st.form_submit_button("Sign Up")
            
            if signup_submitted:
                if create_user(signup_username, signup_password):
                    return True, signup_username
                else:
                    st.error("Username already exists")
        st.markdown('</div>', unsafe_allow_html=True)
    
    return False, None

# Handle authentication
is_logged_in, username = login_page()

if is_logged_in:
    # Initialize session state for tracking current view
    if "current_view" not in st.session_state:
        st.session_state.current_view = "personal"
    if "current_group" not in st.session_state:
        st.session_state.current_group = None

    # Sidebar for navigation
    with st.sidebar:
        st.title("📱 Navigation")
        
        # View selection
        view = st.radio(
            "Select View",
            ["Personal Expenses", "Group Expenses"],
            key="view_selection"
        )
        st.session_state.current_view = "personal" if view == "Personal Expenses" else "group"
        
        st.divider()
        
        # Group management section
        if st.session_state.current_view == "group":
            st.subheader("👥 Group Management")
            
            # Create new group
            with st.expander("➕ Create New Group"):
                with st.form("create_group_form"):
                    group_name = st.text_input("Group Name")
                    group_description = st.text_area("Description")
                    create_group_submitted = st.form_submit_button("Create Group")
                    
                    if create_group_submitted and group_name:
                        group_id = create_group(group_name, username, group_description)
                        st.success(f"Group '{group_name}' created successfully!")
                        st.rerun()
            
            # List user's groups
            st.subheader("🏢 Your Groups")
            user_groups = get_user_groups(username)
            
            if user_groups:
                selected_group = st.selectbox(
                    "Select Group",
                    options=[group["name"] for group in user_groups],
                    key="group_selector"
                )
                
                # Find selected group's ID
                for group in user_groups:
                    if group["name"] == selected_group:
                        st.session_state.current_group = group["id"]
                        break
            else:
                st.info("You haven't joined any groups yet.")
            
            # Show pending invites
            pending_invites = get_user_pending_invites(username)
            if pending_invites:
                st.subheader("📨 Pending Invites")
                for invite in pending_invites:
                    with st.container():
                        st.markdown(f"""
                            <div class="group-card">
                                <h4>{invite['group_name']}</h4>
                                <p>Created by: {invite['creator']}</p>
                                <p>{invite['description']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button("Accept Invite", key=f"accept_{invite['group_id']}"):
                            if accept_group_invite(invite['group_id'], username):
                                st.success(f"Joined group '{invite['group_name']}'!")
                                st.rerun()

    # Main content area
    st.markdown("""
        <div class="title-text">Travel Expense Tracker</div>
    """, unsafe_allow_html=True)

    # Welcome message with username
    st.markdown(f"""<div class="welcome-message">Welcome, {username} 😊</div>""", unsafe_allow_html=True)
    
    # Add new expense section and analytics in the same line
    st.markdown("""
        <div class="section-container">
            <h3 class="section-title">📝 Add New Expense</h3>
            <h3 class="section-title">📊 Personal Expense Analytics</h3>
        </div>
    """, unsafe_allow_html=True)

    # Main content based on current view
    if st.session_state.current_view == "personal":
        # Personal expense tracking interface
        with st.form("expense_form", clear_on_submit=True):
            date_input = st.date_input("**Date**", 
                                   value=date.today(),
                                   format="DD/MM/YYYY")
            amount = st.number_input("**Amount (₹)**", 
                                   min_value=0.0, 
                                   step=1.0,
                                   format="%.2f")
            category = st.selectbox("**Category**", 
                                  ["Food", "Transport", "Accommodation", "Activities", "Shopping", "Other"])
            description = st.text_area("**Description**", 
                                     placeholder="Enter expense details...")
            submit_button = st.form_submit_button("💾 Save Expense")
            
            if submit_button:
                if not description:
                    st.error("Please enter a description")
                else:
                    new_expense = {
                        "date": date_input.strftime("%Y-%m-%d"),
                        "amount": amount,
                        "category": category,
                        "description": description,
                        "username": username
                    }
                    add_expense(new_expense)
                    st.success("✅ Expense saved successfully!")
                    st.rerun()

        # Analytics section
        st.markdown("### 📊 Personal Expense Analytics")
        # Load and display expenses
        expenses = load_expenses()
        if not expenses.empty:
            # Create four columns for metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                    <div class="metric-box">
                        <div class="metric-title">TOTAL SPENT</div>
                        <div class="metric-value">₹{total_spent:.2f}</div>
                        <div class="metric-subtitle">All Time</div>
                    </div>
                """, unsafe_allow_html=True)
                with st.expander("📊 View Details", expanded=False):
                    st.write("### Total Expenses Details")
                    for _, expense in expenses.iterrows():
                        st.markdown(f"""
                            <div class="expense-details">
                                <div class="expense-detail-item">
                                    <span>Date: {expense['date']}</span>
                                    <span>Amount: ₹{expense['amount']:.2f}</span>
                                </div>
                                <div class="expense-detail-item">
                                    <span>Category: {expense['category']}</span>
                                    <span>Description: {expense['description']}</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    # Single distribution graph for all expenses in a search bar-like box
                    st.markdown("""
                        <div style='background: #f5f6fa; border-radius: 24px; padding: 1.5rem 2rem; margin: 2rem 0; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1.5px solid #e9ecef;'>
                            <h3 style='margin-top: 0; color: #006994; font-weight: 700;'>Overall Expense Distribution</h3>
                    """, unsafe_allow_html=True)
                    fig = px.pie(expenses, values='Amount', names='Category', 
                                title='',
                                color_discrete_sequence=['#800020', '#355E3B', '#1C39BB', '#CD7F32', '#808080', '#FF0000', '#006B54', '#8E4585', '#9400D3', '#9932CC'])
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                    <div class="metric-box">
                        <div class="metric-title">THIS MONTH</div>
                        <div class="metric-value">₹{this_month_total:.2f}</div>
                        <div class="metric-subtitle">Expenses</div>
                    </div>
                """, unsafe_allow_html=True)
                with st.expander("📊 View Details", expanded=False):
                    st.write("### This Month's Expenses")
                    this_month_expenses = expenses[expenses['date'].str.startswith(date.today().strftime("%Y-%m"))]
                    for _, expense in this_month_expenses.iterrows():
                        st.markdown(f"""
                            <div class="expense-details">
                                <div class="expense-detail-item">
                                    <span>Date: {expense['date']}</span>
                                    <span>Amount: ₹{expense['amount']:.2f}</span>
                                </div>
                                <div class="expense-detail-item">
                                    <span>Category: {expense['category']}</span>
                                    <span>Description: {expense['description']}</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    # Distribution graph
                    fig = px.pie(this_month_expenses, values='amount', names='category', 
                               title='This Month\'s Expense Distribution')
                    st.plotly_chart(fig)

            with col3:
                st.markdown(f"""
                    <div class="metric-box">
                        <div class="metric-title">LAST MONTH</div>
                        <div class="metric-value">₹{last_month_total:.2f}</div>
                        <div class="metric-subtitle">Expenses</div>
                    </div>
                """, unsafe_allow_html=True)
                with st.expander("📊 View Details", expanded=False):
                    st.write("### Last Month's Expenses")
                    last_month_expenses = expenses[expenses['date'].str.startswith((date.today().replace(day=1) - pd.DateOffset(months=1)).strftime("%Y-%m"))]
                    for _, expense in last_month_expenses.iterrows():
                        st.markdown(f"""
                            <div class="expense-details">
                                <div class="expense-detail-item">
                                    <span>Date: {expense['date']}</span>
                                    <span>Amount: ₹{expense['amount']:.2f}</span>
                                </div>
                                <div class="expense-detail-item">
                                    <span>Category: {expense['category']}</span>
                                    <span>Description: {expense['description']}</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    # Distribution graph
                    fig = px.pie(last_month_expenses, values='amount', names='category', 
                               title='Last Month\'s Expense Distribution')
                    st.plotly_chart(fig)

            with col4:
                st.markdown(f"""
                    <div class="metric-box">
                        <div class="metric-title">TOP CATEGORY</div>
                        <div class="metric-value">{top_category}</div>
                        <div class="metric-subtitle">Most Frequent</div>
                    </div>
                """, unsafe_allow_html=True)
                with st.expander("📊 View Details", expanded=False):
                    st.write("### Top Category Expenses")
                    top_category_expenses = expenses[expenses['category'] == top_category]
                    for _, expense in top_category_expenses.iterrows():
                        st.markdown(f"""
                            <div class="expense-details">
                                <div class="expense-detail-item">
                                    <span>Date: {expense['date']}</span>
                                    <span>Amount: ₹{expense['amount']:.2f}</span>
                                </div>
                                <div class="expense-detail-item">
                                    <span>Category: {expense['category']}</span>
                                    <span>Description: {expense['description']}</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    # Distribution graph
                    fig = px.pie(top_category_expenses, values='amount', names='date', 
                               title=f'Expense Distribution for {top_category}')
                    st.plotly_chart(fig)

    # Add some space at the bottom
    st.markdown("<br><br><br><br>", unsafe_allow_html=True) 