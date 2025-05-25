import pandas as pd

# --- GSC Query + Page Data (OAuth version) ---
def get_gsc_data_dynamic(service, site_url, start_date="2025-01-01", end_date="2025-04-30"):
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
        print("❌ Error in get_gsc_data_dynamic:", e)
        return [], []
