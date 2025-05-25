import streamlit as st
import yaml
import tempfile
import os
from datetime import datetime

from gsc.fetch_data import get_gsc_data, get_time_series_data, client
from gsc.serp_fetcher import get_serp_data
from gsc.chart_generator import generate_and_export_charts
from utils.sheet_handler import update_google_sheet

st.set_page_config(page_title="SEO Automation Toolkit", page_icon="🔍")
st.title("🔍 SEO Automation Toolkit")
st.write("Upload your YAML config file and trigger GSC + SERP automation.")

# Upload YAML config
yaml_file = st.file_uploader("📂 Upload Config (.yaml)", type=["yaml", "yml"])

if yaml_file:
    st.success("✅ Config uploaded successfully.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as tmp:
        tmp.write(yaml_file.read())
        config_path = tmp.name

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    site_url = config["site_url"]
    start_date = config.get("start_date", "2025-01-01")
    end_date = config.get("end_date", "2025-04-30")
    sheets = config["sheet_names"]

    if st.button("🚀 Run Automation"):
        with st.spinner("Running GSC + SERP automation..."):
            raw_data, insights_data = get_gsc_data(site_url, start_date, end_date)
            update_google_sheet(client, raw_data, sheets["raw_data"], ["Keyword", "Page URL", "Clicks", "Impressions"])
            update_google_sheet(client, insights_data, sheets["insights"], ["Keyword", "Page URL", "Clicks", "Impressions", "CTR (%)", "Position", "Ranking Bucket", "Optimization Opportunity", "Quick Win Potential"])

            serp_data = []
            if raw_data:
                for keyword in [row[0] for row in raw_data[:10]]:
                    serp_data.append(get_serp_data(keyword))
            update_google_sheet(client, serp_data, sheets["serp"], ["Keyword", "Top Competitors", "People Also Ask", "Related Searches"])

            ts_df = get_time_series_data(site_url, start_date, end_date)
            generate_and_export_charts(client, ts_df, sheets["charts"])

        st.success("✅ Automation complete!")
        os.remove(config_path)
else:
    st.info("Upload a `.yaml` config file to get started.")
