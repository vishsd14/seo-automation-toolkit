import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import streamlit as st

# --- Auth using Streamlit Secrets ---
SERVICE_ACCOUNT_INFO = st.secrets["gcp_service_account"]
SCOPES = [
    "https://www.googleapis.com/auth/webmasters.readonly",
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
client = gspread.authorize(creds)
service = build("webmasters", "v3", credentials=creds)

# --- GSC Keyword + Page Data ---
def get_gsc_data(site_url, start_date="2025-01-01", end_date="2025-04-30"):
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

            bucket = (
                "Top 3 (High Performing)" if position <= 3 else
                "4-10 (Needs Optimization)" if position <= 10 else
                "11-20 (Potential Improvement)" if position <= 20 else
                "20+ (Needs Strong SEO)"
            )

            insights_data.append([
                keyword, page_url, clicks, impressions, ctr, position, bucket,
                "Yes" if impressions > 1000 and ctr < 2 else "No",
                "Yes" if 11 <= position <= 20 else "No"
            ])

        return raw_data, insights_data

    except Exception as e:
        st.error(f"❌ Error in get_gsc_data: {e}")
        return [], []

# --- Time Series Data ---
def get_time_series_data(site_url, start_date="2025-01-01", end_date="2025-03-31"):
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
        st.error(f"❌ Error in get_time_series_data: {e}")
        return pd.DataFrame(columns=["Date", "Clicks", "Impressions", "CTR", "Position"])
