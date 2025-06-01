import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

# --- Auth Setup using Streamlit secrets ---
SERVICE_ACCOUNT_INFO = st.secrets["gcp_service_account"]
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
client = gspread.authorize(creds)

# --- Sheet Writer Function ---
def update_google_sheet(client, data, sheet_name, headers):
    try:
        spreadsheet = client.open_by_url(st.secrets["spreadsheet_url"])
        worksheet = spreadsheet.worksheet(sheet_name)
        worksheet.clear()
        worksheet.append_row(headers)
        for row in data:
            worksheet.append_row(row)
        print(f"✅ Data written to sheet: {sheet_name}")
    except Exception as e:
        print(f"❌ Error updating sheet {sheet_name}:", e)
