import streamlit as st
import yaml
import tempfile
from datetime import datetime

from gsc.fetch_data import get_gsc_data, get_time_series_data, client
from gsc.serp_fetcher import get_serp_data
from gsc.chart_generator import generate_and_export_charts
from utils.sheet_handler import update_google_sheet

st.set_page_config(page_title="SEO Automation Toolkit", page_icon="🔍")

st.title("🔍 SEO Automation Toolkit")
st.markdown("Upload your YAML config and trigger the full GSC + SERP automation.")

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
        with st.spinner("Running automation tasks..."):

            # Step 1: Fetch GSC Data
            raw_data, insights_data = get_gsc_data(site_url, start_date, end_date)
            update_google_sheet(client, raw_data, sheets["raw_data"], ["Keyword", "Page URL", "Clicks", "Impressions"])
            update_google_sheet(client, insights_data, sheets["insights"], [
                "Keyword", "Page URL", "Clicks", "Impressions", "CTR (%)",
                "Position", "Ranking Bucket", "Optimization Opportunity", "Quick Win Potential"
            ])

            # Step 2: Fetch SERP Data
            serp_data = []
            if raw_data:
                for keyword in [row[0] for row in raw_data[:10]]:
                    serp_data.append(get_serp_data(keyword))
            update_google_sheet(client, serp_data, sheets["serp"], [
                "Keyword", "Top Competitors", "People Also Ask", "Related Searches"
            ])

            # Step 3: Chart Data
            ts_df = get_time_series_data(site_url, start_date, end_date)
            generate_and_export_charts(client, ts_df, sheets["charts"])

        st.success(f"✅ All tasks completed for {site_url} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
else:
    st.info("Please upload a valid `.yaml` config file to begin.")
