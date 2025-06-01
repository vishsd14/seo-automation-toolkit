# python3 main.py --config config/luxury.yaml
# python3 main.py --init-project clientxyz
# python3 main.py --project luxuryhandicrafts

import os
import yaml
import argparse
from dotenv import load_dotenv
from datetime import datetime

from gsc.fetch_data import get_gsc_data, get_time_series_data, client
from gsc.chart_generator import generate_and_export_charts
from utils.sheet_handler import update_google_sheet

# --- Load environment variables ---
load_dotenv()

# --- CLI Args ---
parser = argparse.ArgumentParser(description="Run SEO Automation Toolkit")
parser.add_argument("--config", help="Path to YAML config file (overrides project)", default=None)
parser.add_argument("--project", help="Project name (loads config from config/{project}.yaml)", default=None)
args = parser.parse_args()

# --- Load Config ---
if args.config:
    config_path = args.config
elif args.project:
    config_path = f"config/{args.project}.yaml"
else:
    config_path = "config/sample_config.yaml"

print(f"📄 Loading config: {config_path}")
with open(config_path, "r") as file:
    config = yaml.safe_load(file)

# --- Main Execution ---
def main():
    print("🚀 Starting SEO Automation Tool")

    site_url = config["site_url"]
    start_date = config.get("start_date", "2025-01-01")
    end_date = config.get("end_date", "2025-04-30")
    spreadsheet_id = config["spreadsheet_id"]
    sheet_config = config["sheet_names"]

    # Step 1: GSC Data
    raw_data, insights_data = get_gsc_data(site_url, start_date, end_date)
    update_google_sheet(client, raw_data, spreadsheet_id, sheet_config["raw_data"], ["Keyword", "Page URL", "Clicks", "Impressions"])
    update_google_sheet(client, insights_data, spreadsheet_id, sheet_config["insights"], [
        "Keyword", "Page URL", "Clicks", "Impressions", "CTR (%)",
        "Position", "Ranking Bucket", "Optimization Opportunity", "Quick Win Potential"
    ])

    # Step 2: Charts
    ts_df = get_time_series_data(site_url, start_date, end_date)
    generate_and_export_charts(client, ts_df, spreadsheet_id, sheet_config["charts"])

    print(f"✅ All tasks completed for {site_url} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
