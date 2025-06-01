import streamlit as st
import yaml
import tempfile
from datetime import datetime
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import urllib.parse

from gsc.fetch_data_dynamic import get_time_series_data
#from gsc.serp_fetcher import get_serp_data
from gsc.chart_generator import generate_and_export_charts
from utils.sheet_handler import update_google_sheet

st.set_page_config(page_title="SEO Automation Toolkit", page_icon="🔍")

st.title("🔍 SEO Automation Toolkit")
st.markdown("Upload your YAML config and authenticate with Google to trigger full GSC + SERP automation.")

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
        redirect_uri="http://localhost:8501"
    )

    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline', include_granted_scopes='true')
    st.markdown(f"🔐 [Click here to log in with Google]({auth_url})")

    code = st.text_input("Paste the authorization code here:")
    if code:
        try:
            flow.fetch_token(code=code)
            creds = flow.credentials
            service = build("webmasters", "v3", credentials=creds)
            st.success("✅ Authorized successfully!")
            return service
        except Exception as e:
            st.error(f"❌ Authorization failed: {e}")

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
    start_date = config.get("start_date", "2025-01-01")
    end_date = config.get("end_date", "2025-04-30")
    sheets = config["sheet_names"]

    if st.button("🚀 Run SEO Automation"):
        service = authenticate_user()

        if service:
            with st.spinner("Running automation tasks..."):
                from gsc.fetch_data_dynamic import get_gsc_data_dynamic
                raw_data, insights_data = get_gsc_data_dynamic(service, site_url, start_date, end_date)
                from gsc.fetch_data import client  # Use default sheet client
                update_google_sheet(client, raw_data, sheets["raw_data"], ["Keyword", "Page URL", "Clicks", "Impressions"])
                update_google_sheet(client, insights_data, sheets["insights"], [
                    "Keyword", "Page URL", "Clicks", "Impressions", "CTR (%)",
                    "Position", "Ranking Bucket", "Optimization Opportunity", "Quick Win Potential"
                ])

                #serp_data = []
                #if raw_data:
                #    for keyword in [row[0] for row in raw_data[:10]]:
                #        serp_data.append(get_serp_data(keyword))
                #update_google_sheet(client, serp_data, sheets["serp"], [
                #    "Keyword", "Top Competitors", "People Also Ask", "Related Searches"
                #])

                ts_df = get_time_series_data(site_url, start_date, end_date)
                generate_and_export_charts(client, ts_df, sheets["charts"])

            st.success(f"✅ All tasks completed for {site_url} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.warning("🔐 Please authorize using Google first.")
else:
    st.info("Please upload a valid `.yaml` config file to begin.")
