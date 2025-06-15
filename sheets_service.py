# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
# import streamlit as st

# def connect_to_sheet():
#     creds_dict = st.secrets["gcp_service_account"]
#     scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
#     creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
#     client = gspread.authorize(creds)
#     sheet = client.open(creds_dict["sheet_name"]).sheet1
#     return sheet

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

def connect_to_sheet():
    creds_dict = dict(st.secrets["gcp_service_account"]) # Convert to regular dict
    # Decode the private key: convert "\\n" to actual line breaks
    if isinstance(creds_dict["private_key"], str):
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

# Set up the scope for Google Sheets and Drive access
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    # Create credentials object
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

# Authorize the client
    client = gspread.authorize(creds)

# Open the Google Sheet by name and return the first sheet
    sheet = client.open(creds_dict["sheet_name"]).sheet1
    return sheet
