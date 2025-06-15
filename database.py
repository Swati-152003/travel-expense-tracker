import json
import os
from datetime import datetime, date
import pandas as pd

# File paths
USERS_FILE = "users.json"
EXPENSES_FILE = "expenses.json"
GROUPS_FILE = "groups.json"

def load_json_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return {}

def save_json_file(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# User management
def create_user(username, password):
    users = load_json_file(USERS_FILE)
    if username in users:
        return False
    users[username] = {"password": password}
    save_json_file(USERS_FILE, users)
    return True

def verify_user(username, password):
    users = load_json_file(USERS_FILE)
    return username in users and users[username]["password"] == password

# Expense management
def add_expense(expense):
    expenses = load_json_file(EXPENSES_FILE)
    if "expenses" not in expenses:
        expenses["expenses"] = []
    expenses["expenses"].append(expense)
    save_json_file(EXPENSES_FILE, expenses)

def load_expenses(username=None, group_id=None):
    expenses = load_json_file(EXPENSES_FILE)
    if "expenses" not in expenses:
        return pd.DataFrame()
    
    df = pd.DataFrame(expenses["expenses"])
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        if username:
            df = df[df["username"] == username]
        if group_id:
            df = df[df["group_id"] == group_id]
    return df

# Group management
def create_group(name, creator, description=""):
    groups = load_json_file(GROUPS_FILE)
    group_id = str(len(groups) + 1)
    groups[group_id] = {
        "name": name,
        "creator": creator,
        "description": description,
        "members": [creator],
        "invites": []
    }
    save_json_file(GROUPS_FILE, groups)
    return group_id

def get_user_groups(username):
    groups = load_json_file(GROUPS_FILE)
    return [
        {"id": group_id, **group_data}
        for group_id, group_data in groups.items()
        if username in group_data["members"]
    ]

def get_user_pending_invites(username):
    groups = load_json_file(GROUPS_FILE)
    invites = []
    for group_id, group_data in groups.items():
        if username in group_data.get("invites", []):
            invites.append({
                "group_id": group_id,
                "group_name": group_data["name"],
                "creator": group_data["creator"],
                "description": group_data["description"]
            })
    return invites

def accept_group_invite(group_id, username):
    groups = load_json_file(GROUPS_FILE)
    if group_id in groups and username in groups[group_id].get("invites", []):
        groups[group_id]["members"].append(username)
        groups[group_id]["invites"].remove(username)
        save_json_file(GROUPS_FILE, groups)
        return True
    return False

def add_group_expense(group_id, expense):
    expenses = load_json_file(EXPENSES_FILE)
    if "expenses" not in expenses:
        expenses["expenses"] = []
    expense["group_id"] = group_id
    expenses["expenses"].append(expense)
    save_json_file(EXPENSES_FILE, expenses)

def get_group_expenses(group_id):
    return load_expenses(group_id=group_id)

def get_group_members(group_id):
    groups = load_json_file(GROUPS_FILE)
    if group_id in groups:
        return groups[group_id]["members"]
    return []

def get_group_balance(group_id):
    expenses = get_group_expenses(group_id)
    if expenses.empty:
        return pd.DataFrame()
    
    total = expenses["amount"].sum()
    members = get_group_members(group_id)
    fair_share = total / len(members)
    
    balances = []
    for member in members:
        member_expenses = expenses[expenses["username"] == member]["amount"].sum()
        net_balance = member_expenses - fair_share
        balances.append({
            "Username": member,
            "Total Spent": member_expenses,
            "Fair Share": fair_share,
            "Net Balance": net_balance
        })
    
    return pd.DataFrame(balances) 