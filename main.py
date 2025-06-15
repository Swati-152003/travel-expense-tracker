import streamlit as st
import pandas as pd
from expense_logic import (
    add_expense, get_expenses, calculate_summary,
    get_group_member_summary, calculate_group_balances, get_expense_stats
)
from auth import (
    login_page, logout, create_group, invite_to_group,
    accept_group_invite, get_user_groups, get_user_pending_invites
)
import datetime
import plotly.express as px
import plotly.graph_objects as go

# Set page config with custom theme
st.set_page_config(
    page_title="Travel Expense Tracker",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
        border-radius: 10px;
        background-image: url('https://img.freepik.com/free-vector/travel-time-typography-design_1308-99359.jpg');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    .login-container {
        background-image: url('https://img.freepik.com/free-photo/travel-concept-with-landmarks_23-2149153256.jpg');
        background-size: cover;
        background-position: center;
        padding: 3rem;
        border-radius: 15px;
        margin: 2rem auto;
        max-width: 500px;
    }
    .login-box {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .stForm {
        background-color: rgba(255, 255, 255, 0.9);
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .st-emotion-cache-1y4p8pa {
        padding: 2rem;
        border-radius: 10px;
        background-color: rgba(255, 255, 255, 0.9);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .analytics-section {
        margin-top: 2rem;
        margin-bottom: 2rem;
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metrics-container {
        display: flex;
        justify-content: center;
        gap: 20px;
        padding: 20px;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        cursor: pointer;
        border: 2px solid #E6E6FA;
        width: 100%;
        max-width: 280px;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 15px;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
        border-color: #008080;
    }
    .metric-header {
        background-color: #f0f8ff;
        padding: 10px 15px;
        border-radius: 10px;
        width: 100%;
        text-align: center;
        border: 1px solid #e0e0e0;
    }
    .metric-icon {
        width: 35px;
        height: 35px;
        padding: 6px;
        background-color: #ffffff;
        border-radius: 50%;
        border: 1px solid #e0e0e0;
        transition: transform 0.3s ease;
    }
    .metric-card:hover .metric-icon {
        transform: scale(1.1);
    }
    .metric-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 10px;
        width: 100%;
    }
    .metric-title {
        font-size: 1.1rem;
        color: #008080;
        font-weight: 700;
        margin: 0;
    }
    .metric-subtitle {
        font-size: 0.8rem;
        color: #666;
        text-transform: uppercase;
        margin: 0;
    }
    .metric-value-container {
        background-color: #f8f9fa;
        padding: 12px;
        border-radius: 10px;
        width: 100%;
        text-align: center;
        border: 1px solid #e0e0e0;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #008080;
        margin: 0;
        word-break: break-word;
    }
    h1, h2, h3 {
        font-weight: 700 !important;
    }
    .stButton>button {
        background-color: #B22222 !important;  /* Brick/Cherry red color */
        color: white;
        border-radius: 6px;
        padding: 0.5rem 2rem;
        font-weight: 700;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(178, 34, 34, 0.3);
    }
    .stButton>button:hover {
        background-color: #8B0000 !important;  /* Darker cherry red for hover */
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(178, 34, 34, 0.4);
    }
    .expense-form-label {
        color: #800000 !important;
        font-weight: 700 !important;
    }
    .expense-form {
        background-color: #36454F !important;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #36454F;
        color: white !important;
    }
    .stDataFrame {
        font-weight: 700 !important;
    }
    .user-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem;
        background-color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .group-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }
    .balance-positive {
        color: #059669;
        font-weight: bold;
    }
    .balance-negative {
        color: #dc2626;
        font-weight: bold;
    }
    .welcome-text {
        position: absolute;
        top: 0;
        right: 20px;
        font-size: 1.2rem;
        font-weight: bold;
        color: #006994;
        background: rgba(0, 105, 148, 0.1);
        padding: 1rem;
        border-radius: 12px;
        z-index: 1000;
        margin-top: 10px;
    }
    .expander-header {
        color: #000080;  /* Navy Blue */
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }
    .title-text {
        text-align: center;
        font-size: 2.2rem;
        font-weight: bold;
        color: #1B3B6F;
        margin: 1.5rem auto;
        padding: 1.2rem;
        background-color: #E6D5AC;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        max-width: 70%;
    }
    .expense-form-container {
        max-width: 40%;
        margin: 0 auto;
        padding: 1.5rem;
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metrics-container {
        background: white;
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    .transaction-table {
        background: white;
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        
        margin: 1rem 0;
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
        border: 5px solid #36454F;  /* Thicker charcoal border */
    }
    .metric-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0, 105, 148, 0.15);
    }
    .metric-title {
        color: #36454F;  /* Charcoal */
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    .metric-value {
        color: #36454F;  /* Charcoal */
        font-size: 1.8rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .metric-subtitle {
        color: #36454F;  /* Charcoal */
        font-size: 0.8rem;
    }
    .expense-details {
        margin-top: 1rem;
        padding: 1rem;
        background: rgba(0, 105, 148, 0.05);
        border-radius: 8px;
    }
    .expense-detail-item {
        display: block;
        padding: 0.5rem 0;
        border-bottom: 1px solid rgba(0, 105, 148, 0.1);
        margin-bottom: 0.5rem;
    }
    .expense-detail-item:last-child {
        border-bottom: none;
    }
    .expense-detail-label {
        color: #006994;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    .expense-table {
        margin-top: 2rem;
        padding: 1rem;
        background: white;
        border-radius: 16px;
        box-shadow: 0 4px 6px rgba(0, 105, 148, 0.1);
        border: 3px solid #006994;
    }
    .expense-table th {
        background-color: #006994;
        color: white;
        padding: 0.75rem;
        text-align: left;
    }
    .expense-table td {
        padding: 0.75rem;
        border-bottom: 1px solid rgba(0, 105, 148, 0.1);
        color: #614051;  /* Eggplant color */
        font-weight: 700;  /* Make text bold */
    }
    .expense-table tr:hover {
        background-color: rgba(0, 105, 148, 0.05);
    }
    .distribution-graph {
        margin-top: 2rem;
        padding: 1rem;
        background: white;
        border-radius: 16px;
        box-shadow: 0 4px 6px rgba(0, 105, 148, 0.1);
        border: 3px solid #006994;
    }
    /* Custom styling for search highlight */
    .stDataFrame [data-testid="stDataFrame"] {
        --highlight-color: #4682B4 !important;  /* Steel Blue */
    }
    </style>
""", unsafe_allow_html=True)

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

        # Add logout button at the bottom of sidebar
        st.divider()
        if st.button("🚪 Logout", key="logout", use_container_width=True):
            logout()
            st.rerun()

    # Main content area
    col1, col2, col3 = st.columns([2,1,1])

    # Welcome message with username at top right (before title)
    st.markdown(f"""<div class="welcome-text">Welcome, {username} 😊</div>""", unsafe_allow_html=True)

    # Main title with plane icon
    st.markdown("""
        <div class="title-text">✈️ Travel Expense Tracker</div>
    """, unsafe_allow_html=True)

    # Add new expense section
    st.markdown("""
        <div class="section-container">
            <h3 class="section-title">📝 Add New Expense</h3>
        </div>
    """, unsafe_allow_html=True)

    # Main content based on current view
    if st.session_state.current_view == "personal":
        # Personal expense tracking interface
        with st.form("expense_form", clear_on_submit=True):
            date_input = st.date_input(
                "**Date**",
                value=datetime.date.today(),
                max_value=datetime.date.today(),
                format="DD/MM/YYYY"
            )
            amount = st.number_input("**Amount (₹)**", min_value=0.0, step=1.0, format="%.2f")
            category = st.selectbox("**Category**", ["Food", "Transport", "Accommodation", "Activities", "Shopping", "Other"])
            location = st.text_input("**Location**", placeholder="Enter location...")
            description = st.text_area("**Description**", placeholder="Enter expense details...")
            submit_button = st.form_submit_button("💾 Save Expense")
            
            if submit_button:
                if not description or not location:
                    st.error("Please enter a description and location")
                else:
                    new_expense = {
                        "Date": date_input.strftime("%Y-%m-%d"),
                        "Amount": amount,
                        "Category": category,
                        "Location": location,
                        "Description": description,
                        "Username": username
                    }
                    add_expense(new_expense)
                    st.success("✅ Expense saved successfully!")
                    st.balloons()
                    st.rerun()

        # Analytics section
        expenses = get_expenses(username)
        if not expenses.empty:
            # Convert Date column to datetime
            expenses['Date'] = pd.to_datetime(expenses['Date'])
            
            # Calculate metrics
            total_spent = expenses['Amount'].sum()
            current_month = datetime.date.today().month
            current_year = datetime.date.today().year
            last_month = current_month - 1 if current_month > 1 else 12
            last_month_year = current_year if current_month > 1 else current_year - 1
            
            this_month_expenses = expenses[(expenses['Date'].dt.month == current_month) & 
                                        (expenses['Date'].dt.year == current_year)]
            last_month_expenses = expenses[(expenses['Date'].dt.month == last_month) & 
                                        (expenses['Date'].dt.year == last_month_year)]
            top_category = expenses['Category'].mode()[0]
            top_category_amount = expenses[expenses['Category'] == top_category]['Amount'].sum()
            
            # Create four columns for metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown(f"""
                    <div class="metric-box">
                        <div class="metric-title">💰 TOTAL SPENT</div>
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
                                    <span class="expense-detail-label">Date:</span> {expense['Date'].strftime('%Y-%m-%d')}
                                </div>
                                <div class="expense-detail-item">
                                    <span class="expense-detail-label">Amount:</span> ₹{expense['Amount']:.2f}
                                </div>
                                <div class="expense-detail-item">
                                    <span class="expense-detail-label">Category:</span> {expense['Category']}
                                </div>
                                <div class="expense-detail-item">
                                    <span class="expense-detail-label">Location:</span> {expense.get('Location', '')}
                                </div>
                                <div class="expense-detail-item">
                                    <span class="expense-detail-label">Description:</span> {expense['Description']}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                    <div class="metric-box">
                        <div class="metric-title">📅 THIS MONTH</div>
                        <div class="metric-value">₹{this_month_expenses['Amount'].sum():.2f}</div>
                        <div class="metric-subtitle">Expenses</div>
                    </div>
                """, unsafe_allow_html=True)
                with st.expander("📊 View Details", expanded=False):
                    st.write("### This Month's Expenses")
                    for _, expense in this_month_expenses.iterrows():
                        st.markdown(f"""
                            <div class="expense-details">
                                <div class="expense-detail-item">
                                    <span class="expense-detail-label">Date:</span> {expense['Date'].strftime('%Y-%m-%d')}
                                </div>
                                <div class="expense-detail-item">
                                    <span class="expense-detail-label">Amount:</span> ₹{expense['Amount']:.2f}
                                </div>
                                <div class="expense-detail-item">
                                    <span class="expense-detail-label">Category:</span> {expense['Category']}
                                </div>
                                <div class="expense-detail-item">
                                    <span class="expense-detail-label">Location:</span> {expense.get('Location', '')}
                                </div>
                                <div class="expense-detail-item">
                                    <span class="expense-detail-label">Description:</span> {expense['Description']}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                    <div class="metric-box">
                        <div class="metric-title">📅 LAST MONTH</div>
                        <div class="metric-value">₹{last_month_expenses['Amount'].sum():.2f}</div>
                        <div class="metric-subtitle">Expenses</div>
                    </div>
                """, unsafe_allow_html=True)
                with st.expander("📊 View Details", expanded=False):
                    st.write("### Last Month's Expenses")
                    for _, expense in last_month_expenses.iterrows():
                        st.markdown(f"""
                            <div class="expense-details">
                                <div class="expense-detail-item">
                                    <span class="expense-detail-label">Date:</span> {expense['Date'].strftime('%Y-%m-%d')}
                                </div>
                                <div class="expense-detail-item">
                                    <span class="expense-detail-label">Amount:</span> ₹{expense['Amount']:.2f}
                                </div>
                                <div class="expense-detail-item">
                                    <span class="expense-detail-label">Category:</span> {expense['Category']}
                                </div>
                                <div class="expense-detail-item">
                                    <span class="expense-detail-label">Location:</span> {expense.get('Location', '')}
                                </div>
                                <div class="expense-detail-item">
                                    <span class="expense-detail-label">Description:</span> {expense['Description']}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

            with col4:
                st.markdown(f"""
                    <div class="metric-box">
                        <div class="metric-title">🏆 TOP CATEGORY</div>
                        <div class="metric-value">{top_category}</div>
                        <div class="metric-subtitle">₹{top_category_amount:.2f}</div>
                    </div>
                """, unsafe_allow_html=True)
                with st.expander("📊 View Details", expanded=False):
                    st.write("### Top Category Expenses")
                    top_category_expenses = expenses[expenses['Category'] == top_category]
                    for _, expense in top_category_expenses.iterrows():
                        st.markdown(f"""
                            <div class="expense-details">
                                <div class="expense-detail-item">
                                    <span class="expense-detail-label">Date:</span> {expense['Date'].strftime('%Y-%m-%d')}
                                </div>
                                <div class="expense-detail-item">
                                    <span class="expense-detail-label">Amount:</span> ₹{expense['Amount']:.2f}
                                </div>
                                <div class="expense-detail-item">
                                    <span class="expense-detail-label">Category:</span> {expense['Category']}
                                </div>
                                <div class="expense-detail-item">
                                    <span class="expense-detail-label">Location:</span> {expense.get('Location', '')}
                                </div>
                                <div class="expense-detail-item">
                                    <span class="expense-detail-label">Description:</span> {expense['Description']}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

            # Single distribution graph for all expenses
            st.markdown('<div class="distribution-graph">', unsafe_allow_html=True)
            fig = px.pie(expenses, values='Amount', names='Category', 
                        title='Overall Expense Distribution',
                        color_discrete_sequence=['#800020', '#355E3B', '#1C39BB', '#CD7F32', '#808080', '#FF0000', '#006B54', '#8E4585', '#9400D3', '#9932CC'])  # Added more violet colors
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Expense Table in expander
            with st.expander("📋 View Expenses", expanded=False):
                st.markdown('<div class="expense-table">', unsafe_allow_html=True)
                # Display the table without serial numbers and search
                st.dataframe(
                    expenses[['Date', 'Amount', 'Category', 'Description']],
                    hide_index=True,
                    use_container_width=True,
                    height=400
                )
                st.markdown('</div>', unsafe_allow_html=True)

    else:  # Group expense view
        if st.session_state.current_group:
            group_info = None
            for group in get_user_groups(username):
                if group["id"] == st.session_state.current_group:
                    group_info = group
                    break
            
            if group_info:
                # Group header
                st.markdown(f"### 👥 {group_info['name']}")
                st.markdown(f"_{group_info['description']}_")
                
                # Tabs for different group features (Add Expense first, then Overview)
                tab2, tab1 = st.tabs([
                    "💰 Add Expense",
                    "📊 Overview"
                ])
                
                with tab2:
                    # Add group expense form
                    st.markdown("### 📝 Add Group Expense")
                    with st.form("group_expense_form", clear_on_submit=True):
                        spender = st.text_input("Name of Spender", help="Enter the name of the person who spent")
                        date = st.date_input("Date", datetime.date.today(), max_value=datetime.date.today(), help="Select the date of your expense (up to today)")
                        category = st.selectbox("Category", ["Food", "Travel", "Accommodation", "Shopping", "Entertainment", "Other"], help="Select the category of your expense")
                        amount = st.number_input("Amount (₹)", min_value=0.0, step=0.5, help="Enter the amount spent")
                        location = st.text_input("Location", placeholder="Enter the location", help="Where did you spend this amount?")
                        description = st.text_area("Description", placeholder="Add any additional notes...", help="Optional: Add more details about the expense")
                        submitted = st.form_submit_button("💰 Add Group Expense")
                        if submitted:
                            if amount > 0 and location and spender:
                                add_expense({
                                    "Date": date.strftime("%Y-%m-%d"),
                                    "Category": category,
                                    "Amount": amount,
                                    "Location": location,
                                    "Description": description,
                                    "Username": spender,
                                    "group_id": st.session_state.current_group
                                })
                                st.success("✅ Group expense added successfully!")
                                st.balloons()
                            else:
                                st.error("❌ Please fill all required fields.")
                
                with tab1:
                    # Group expense statistics
                    stats = get_expense_stats(group_id=st.session_state.current_group)
                    # Display metrics with thick border, icon, and expander for details
                    metric_cols = st.columns(4)
                    icons = ["💰", "📅", "📅", "🏆"]
                    titles = ["Group Total", "This Month", "Last Month", "Top Category"]
                    values = [stats['total_spent'], stats['this_month_total'], stats['last_month_total'], stats['top_category']]
                    for i, col in enumerate(metric_cols):
                        with col:
                            col.markdown(f"""
                                <div style='border: 5px solid #2a3439; border-radius: 16px; padding: 1.2rem; text-align: center; margin-bottom: 1rem;'>
                                    <div style='font-size: 2rem;'>{icons[i]}</div>
                                    <div style='font-size: 1.1rem; font-weight: 700; margin-bottom: 0.5rem;'>{titles[i]}</div>
                                    <div style='font-size: 1.5rem; font-weight: bold; color: #355E3B;'>{values[i] if i < 3 else values[i]}</div>
                                </div>
                            """, unsafe_allow_html=True)
                            with st.expander(f"View Details for {titles[i]}"):
                                if i == 0:
                                    st.write("All group expenses:")
                                    df = get_expenses(group_id=st.session_state.current_group)
                                    st.dataframe(df, hide_index=True)
                                elif i == 1:
                                    st.write("This month's group expenses:")
                                    df = get_expenses(group_id=st.session_state.current_group)
                                    this_month = datetime.date.today().month
                                    this_year = datetime.date.today().year
                                    st.dataframe(df[(df['Date'].dt.month == this_month) & (df['Date'].dt.year == this_year)], hide_index=True)
                                elif i == 2:
                                    st.write("Last month's group expenses:")
                                    df = get_expenses(group_id=st.session_state.current_group)
                                    last_month = datetime.date.today().month - 1 if datetime.date.today().month > 1 else 12
                                    last_month_year = datetime.date.today().year if datetime.date.today().month > 1 else datetime.date.today().year - 1
                                    st.dataframe(df[(df['Date'].dt.month == last_month) & (df['Date'].dt.year == last_month_year)], hide_index=True)
                                elif i == 3:
                                    st.write("Top category group expenses:")
                                    df = get_expenses(group_id=st.session_state.current_group)
                                    st.dataframe(df[df['Category'] == stats['top_category']], hide_index=True)
                    # Member contribution chart with ocean green color
                    member_summary = get_group_member_summary(st.session_state.current_group)
                    if not member_summary.empty:
                        # Reset index and rename the index column to 'Username'
                        member_summary = member_summary.reset_index().rename(columns={'index': 'Username'})
                        fig_members = px.bar(
                            member_summary,
                            x='Username',
                            y='Total Spent',
                            title="Member Contributions",
                            template="plotly_white",
                            color_discrete_sequence=["#48BF91"]  # Ocean green
                        )
                        fig_members.update_layout(
                            xaxis_title="Members",
                            yaxis_title="Amount Spent (₹)"
                        )
                        st.plotly_chart(fig_members, use_container_width=True)
                    else:
                        st.info("No expenses recorded in this group yet.")
            
            else:
                st.error("Group not found!")
        else:
            st.info("👈 Select a group from the sidebar or create a new one to get started!")

    # Add some space at the bottom
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)

