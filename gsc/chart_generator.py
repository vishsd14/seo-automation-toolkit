import matplotlib.pyplot as plt
import pandas as pd
from utils.sheet_handler import update_google_sheet

def generate_and_export_charts(df, sheet_name):
    df["Date"] = pd.to_datetime(df["Date"])
    df.sort_values("Date", inplace=True)

    metrics = ["Clicks", "Impressions", "CTR"]
    for metric in metrics:
        plt.figure(figsize=(10, 4))
        plt.plot(df["Date"], df[metric], marker='o', label=metric)
        plt.xlabel("Date")
        plt.ylabel(metric)
        plt.title(f"{metric} Over Time")
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        filename = f"gsc_{metric.lower()}_chart.png"
        plt.savefig(filename)
        print(f"📊 Saved chart: {filename}")

    # Write to Sheet
    df["Date"] = df["Date"].dt.strftime('%Y-%m-%d')
    update_google_sheet(df.values.tolist(), sheet_name, list(df.columns))
