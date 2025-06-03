import streamlit as st
import yaml
import tempfile
from datetime import datetime
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from gsc.fetch_data_dynamic import get_gsc_data_dynamic, get_time_series_data
from gsc.chart_generator import generate_and_export_charts
from utils.sheet_handler import update_google_sheet
from gsc.fetch_data import client  # For Google Sheets access

st.set_page_config(page_title="SEO Automation Toolkit", page_icon="🔍")

st.title("🔍 SEO Automation Toolkit")
st.markdown("Upload your YAML config and authenticate with Google to trigger the automation.")

# --- Google OAuth Handler ---
def authenticate_user():
    client_config = {
        "web": {
            "client_id": st.secrets["google_oauth"]["client_id"],
            "client_secret": st.secrets["google_oauth"]["client_secret"],
            "auth_uri": st.secrets["google_oauth"]["auth_uri"],
            "token_uri": st.secrets["google_oauth"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["google_oauth"]["auth_provider_x509_cert_url"],
            "redirect_uris": st.secrets["google_oauth"]["redirect_uris"]
        }
    }

    flow = Flow.from_client_config(
        client_config,
        scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
        redirect_uri=st.secrets["google_oauth"]["redirect_uris"][0]
    )

    # If 'code' is in query params, user returned from Google
    query_params = st.query_params
    if "code" in query_params:
        code = query_params["code"]
        try:
            flow.fetch_token(code=code)
            creds = flow.credentials
            service = build("webmasters", "v3", credentials=creds)
            st.success("✅ Authorized successfully!")
            return service
        except Exception as e:
            st.error(f"❌ Authorization failed: {e}")
            return None
    else:
        # Start OAuth flow
        auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline', include_granted_scopes='true')
        st.markdown(f"🔐 [Click here to log in with Google]({auth_url})")
        st.stop()  # Wait for user to return after auth

    return None

# --- Upload Config File ---
yaml_file = st.file_uploader("📂 Upload Config (.yaml)", type=["yaml", "yml"])

if yaml_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as tmp:
        tmp.write(yaml_file.read())
        config_path = tmp.name

    st.success("✅ Config uploaded. Ready to run!")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    site_url = config["site_url"]
    spreadsheet_id = config["spreadsheet_id"]
    start_date = config.get("start_date", "2025-01-01")
    end_date = config.get("end_date", "2025-04-30")
    sheets = config["sheet_names"]

    # Authenticate only once at the top level
    service = authenticate_user()

    if st.button("🚀 Run SEO Automation"):
        if service:
            with st.spinner("Running automation tasks..."):
                raw_data, insights_data = get_gsc_data_dynamic(service, site_url, start_date, end_date)

                update_google_sheet(client, raw_data, spreadsheet_id, sheets["raw_data"],
                                    ["Keyword", "Page URL", "Clicks", "Impressions"])
                update_google_sheet(client, insights_data, spreadsheet_id, sheets["insights"], [
                    "Keyword", "Page URL", "Clicks", "Impressions", "CTR (%)",
                    "Position", "Ranking Bucket", "Optimization Opportunity", "Quick Win Potential"
                ])

                ts_df = get_time_series_data(site_url, start_date, end_date)
                generate_and_export_charts(client, ts_df, spreadsheet_id, sheets["charts"])

            st.success(f"✅ All tasks completed for {site_url} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.warning("🔐 Google authentication is required to proceed.")
else:
    st.info("Please upload a valid `.yaml` config file to begin.")
