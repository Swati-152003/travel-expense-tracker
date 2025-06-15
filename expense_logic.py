import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import streamlit as st

# File to store expenses
EXPENSES_FILE = "expenses.json"

def init_expenses_file():
    """Initialize expenses file if it doesn't exist"""
    try:
        if not os.path.exists(EXPENSES_FILE):
            with open(EXPENSES_FILE, "w") as f:
                json.dump([], f)
    except Exception as e:
        st.error(f"Error initializing expenses file: {str(e)}")

def load_expenses():
    """Load expenses from JSON file"""
    try:
        with open(EXPENSES_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    except Exception as e:
        st.error(f"Error loading expenses: {str(e)}")
        return []

def save_expenses(expenses):
    """Save expenses to JSON file"""
    try:
        with open(EXPENSES_FILE, "w") as f:
            json.dump(expenses, f)
    except Exception as e:
        st.error(f"Error saving expenses: {str(e)}")

def add_expense(expense_data: Dict) -> bool:
    """Add a new expense"""
    try:
        expenses = load_expenses()
        # Add timestamp to expense
        expense_data["timestamp"] = datetime.now().isoformat()
        
        # Ensure group_id is None for personal expenses
        if "group_id" not in expense_data:
            expense_data["group_id"] = None
            
        expenses.append(expense_data)
        save_expenses(expenses)
        return True
    except Exception as e:
        st.error(f"Error adding expense: {str(e)}")
        return False

def get_expenses(username: str = None, group_id: str = None) -> pd.DataFrame:
    """Get expenses as a pandas DataFrame
    
    Args:
        username: If provided, get personal expenses for this user
        group_id: If provided, get expenses for this group
    """
    try:
        expenses = load_expenses()
        if not expenses:
            return pd.DataFrame()
        
        df = pd.DataFrame(expenses)
        if df.empty:
            return df
            
        # Convert date strings to datetime
        df["Date"] = pd.to_datetime(df["Date"])
        
        # Handle group_id field
        if "group_id" not in df.columns:
            df["group_id"] = None
        
        if username and group_id:
            # Get expenses that are either personal or from the specified group
            mask = ((df["Username"] == username) & df["group_id"].isna()) | (df["group_id"] == group_id)
            df = df[mask]
        elif username:
            # Get only personal expenses
            df = df[(df["Username"] == username) & df["group_id"].isna()]
        elif group_id:
            # Get only group expenses
            df = df[df["group_id"] == group_id]
        
        return df
    except Exception as e:
        st.error(f"Error getting expenses: {str(e)}")
        return pd.DataFrame()

def calculate_summary(df: pd.DataFrame) -> Tuple[float, pd.DataFrame]:
    """Calculate summary statistics from expenses"""
    try:
        if df.empty:
            return 0, pd.DataFrame()
        
        total = df["Amount"].sum()
        summary = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
        summary_df = pd.DataFrame({
            "Total Amount": summary,
            "Percentage": (summary / total * 100).round(2)
        })
        return total, summary_df
    except Exception as e:
        st.error(f"Error calculating summary: {str(e)}")
        return 0, pd.DataFrame()

def get_group_member_summary(group_id: str) -> pd.DataFrame:
    """Calculate how much each member has spent in the group"""
    try:
        df = get_expenses(group_id=group_id)
        if df.empty:
            return pd.DataFrame()
        
        member_summary = df.groupby("Username")["Amount"].agg([
            ("Total Spent", "sum"),
            ("Number of Expenses", "count"),
            ("Average Expense", "mean")
        ]).round(2)
        
        # Calculate percentage of total
        total_spent = member_summary["Total Spent"].sum()
        if total_spent > 0:
            member_summary["Percentage of Total"] = (member_summary["Total Spent"] / total_spent * 100).round(2)
        else:
            member_summary["Percentage of Total"] = 0
        
        return member_summary
    except Exception as e:
        st.error(f"Error calculating member summary: {str(e)}")
        return pd.DataFrame()

def calculate_group_balances(group_id: str) -> pd.DataFrame:
    """Calculate who owes what to whom in the group"""
    try:
        df = get_expenses(group_id=group_id)
        if df.empty:
            return pd.DataFrame()
        
        member_summary = get_group_member_summary(group_id)
        total_spent = member_summary["Total Spent"].sum()
        num_members = len(member_summary)
        
        if num_members == 0:
            return pd.DataFrame()
        
        # Calculate how much each person should have paid
        fair_share = total_spent / num_members
        
        # Calculate how much each person owes or is owed
        balances = pd.DataFrame({
            "Username": member_summary.index,
            "Total Spent": member_summary["Total Spent"],
            "Fair Share": fair_share,
            "Net Balance": member_summary["Total Spent"] - fair_share
        })
        
        return balances
    except Exception as e:
        st.error(f"Error calculating group balances: {str(e)}")
        return pd.DataFrame()

def get_expense_stats(username: str = None, group_id: str = None) -> Dict:
    """Get statistics about expenses"""
    try:
        df = get_expenses(username, group_id)
        if df.empty:
            return {
                "total_spent": 0,
                "avg_expense": 0,
                "num_transactions": 0,
                "top_category": "N/A",
                "this_month_total": 0,
                "last_month_total": 0
            }
        
        # Get current month's start and end dates
        today = pd.Timestamp.now()
        this_month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month_start = (this_month_start + pd.DateOffset(months=1))
        last_month_start = (this_month_start - pd.DateOffset(months=1))
        
        stats = {
            "total_spent": df["Amount"].sum(),
            "avg_expense": df["Amount"].mean(),
            "num_transactions": len(df),
            "top_category": df.groupby("Category")["Amount"].sum().idxmax() if not df.empty else "N/A",
            "this_month_total": df[(df["Date"] >= this_month_start) & (df["Date"] < next_month_start)]["Amount"].sum(),
            "last_month_total": df[(df["Date"] >= last_month_start) & (df["Date"] < this_month_start)]["Amount"].sum()
        }
        
        return stats
    except Exception as e:
        st.error(f"Error calculating expense stats: {str(e)}")
        return {
            "total_spent": 0,
            "avg_expense": 0,
            "num_transactions": 0,
            "top_category": "N/A",
            "this_month_total": 0,
            "last_month_total": 0
        }

def remove_expenses_by_indices(indices: List[int]) -> bool:
    """Remove expenses at specified indices"""
    try:
        expenses = load_expenses()
        if not expenses:
            return False
        
        # Sort indices in descending order to avoid index shifting
        indices = sorted(indices, reverse=True)
        
        # Remove expenses at specified indices
        for index in indices:
            if 0 <= index < len(expenses):
                expenses.pop(index)
        
        save_expenses(expenses)
        return True
    except Exception as e:
        st.error(f"Error removing expenses: {str(e)}")
        return False

# Initialize expenses file when module is imported
init_expenses_file()
