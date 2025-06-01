import os
import gspread
import pandas as pd
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

# --- Scopes ---
SCOPES = [
    "https://www.googleapis.com/auth/webmasters.readonly",
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# --- OAuth Flow (User-Based Login) ---
def get_authenticated_services():
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials/client_secret_oauth.json', SCOPES
    )
    creds = flow.run_local_server(port=0)
    client = gspread.authorize(creds)
    service = build("webmasters", "v3", credentials=creds)
    return client, service

client, service = get_authenticated_services()

# --- GSC Query + Page Data ---
def get_gsc_data(site_url, start_date="2025-01-01", end_date="2025-04-30"):
    print("🔍 Fetching keyword data from:", site_url)
    request = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": ["query", "page"],
        "rowLimit": 1000
    }

    try:
        response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()
        raw_data, insights_data = [], []

        for row in response.get("rows", []):
            clicks = row.get("clicks", 0)
            impressions = row.get("impressions", 1)
            ctr = round((clicks / impressions) * 100, 2)
            position = row.get("position", 0)
            keyword = row["keys"][0]
            page_url = row["keys"][1] if len(row["keys"]) > 1 else "N/A"

            raw_data.append([keyword, page_url, clicks, impressions])

            if position <= 3:
                bucket = "Top 3 (High Performing)"
            elif 4 <= position <= 10:
                bucket = "4-10 (Needs Optimization)"
            elif 11 <= position <= 20:
                bucket = "11-20 (Potential Improvement)"
            else:
                bucket = "20+ (Needs Strong SEO)"

            insights_data.append([
                keyword, page_url, clicks, impressions, ctr, position, bucket,
                "Yes" if impressions > 1000 and ctr < 2 else "No",
                "Yes" if 11 <= position <= 20 else "No"
            ])

        return raw_data, insights_data

    except Exception as e:
        print("❌ Error in get_gsc_data:", e)
        return [], []

# --- Time Series CTR + Clicks ---
def get_time_series_data(site_url, start_date="2025-01-01", end_date="2025-03-31"):
    print("📈 Fetching time-series data for:", site_url)
    request = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": ["date"],
        "rowLimit": 1000
    }

    try:
        response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()
        data = []
        for row in response.get("rows", []):
            date = row["keys"][0]
            clicks = row.get("clicks", 0)
            impressions = row.get("impressions", 0)
            ctr = round((clicks / impressions) * 100, 2) if impressions else 0
            position = row.get("position", 0)
            data.append([date, clicks, impressions, ctr, position])

        return pd.DataFrame(data, columns=["Date", "Clicks", "Impressions", "CTR", "Position"])

    except Exception as e:
        print("❌ Error in get_time_series_data:", e)
        return pd.DataFrame(columns=["Date", "Clicks", "Impressions", "CTR", "Position"])
