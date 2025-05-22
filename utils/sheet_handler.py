import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

# Setup credentials once
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

# --- Update a specific sheet ---
def update_google_sheet(data, sheet_name, headers):
    try:
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)
        print(f"📄 Updating existing sheet: {sheet_name}")
    except gspread.exceptions.WorksheetNotFound:
        print(f"📄 Creating new sheet: {sheet_name}")
        sheet = client.open_by_key(SPREADSHEET_ID).add_worksheet(title=sheet_name, rows="1000", cols="20")

    sheet.clear()
    sheet.append_row(headers)

    if data:
        sheet.append_rows(data)
        print(f"✅ Wrote {len(data)} rows to sheet: {sheet_name}")
    else:
        print(f"⚠️ No data to write to sheet: {sheet_name}")
