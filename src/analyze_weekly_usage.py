import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import matplotlib.ticker as ticker
import subprocess

# Use the combined CSV file
input_file = '/tmp/reports/usage_report_combined.csv'

# Date range for analysis
start_date = pd.to_datetime('2024-07-01')  # July 1st, 2024
end_date = pd.to_datetime('2025-05-31')    # May 31st, 2025

# Read the data
print(f"Reading {input_file}")
df = pd.read_csv(input_file, low_memory=False, on_bad_lines='skip')

# Handle nulls in date columns
for col in ['JOB_RUN_STARTED_AT', 'JOB_RUN_STOPPED_AT']:
    if col in df.columns:
        df[col] = df[col].replace(['\\N', 'NULL', 'null', ''], np.nan)
        df[col] = pd.to_datetime(df[col], errors='coerce')

# Filter to the specified date range
mask = (df['JOB_RUN_STARTED_AT'] >= start_date) & (df['JOB_RUN_STARTED_AT'] <= end_date)
df = df[mask]

# Convert TOTAL_CREDITS to numeric
if 'TOTAL_CREDITS' in df.columns:
    df['TOTAL_CREDITS'] = pd.to_numeric(df['TOTAL_CREDITS'], errors='coerce')
else:
    raise ValueError('TOTAL_CREDITS column not found in input file')

# Set index to JOB_RUN_STARTED_AT
if not df.empty:
    df = df.set_index('JOB_RUN_STARTED_AT')
else:
    raise ValueError('No data in the specified date range.')

# Resample by week (Mon-Sun), label weeks by the Monday
weekly_usage = df['TOTAL_CREDITS'].resample('W-MON', label='left', closed='left').sum()

# Calculate trend line
x = np.arange(len(weekly_usage))
z = np.polyfit(x, weekly_usage.values, 1)
p = np.poly1d(z)
trend = p(x)

# Plot
plt.figure(figsize=(14, 7))
sns.set_style("whitegrid")
sns.lineplot(x=weekly_usage.index, y=weekly_usage.values, marker='o', label='Weekly Credits')
plt.plot(weekly_usage.index, trend, 'r--', label='Trend Line')

plt.title('CircleCI Weekly Credit Usage')
plt.xlabel('Week Starting (Monday)')
plt.ylabel('Total Credits')

# Format y-axis to show actual numbers instead of scientific notation
plt.gca().yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

plt.legend()
plt.tight_layout()
output_file = '/tmp/reports/weekly_credit_usage_2024_2025.png'
plt.savefig(output_file)
plt.close()

# Print summary
print("\nWeekly Credit Usage:")
for date, usage in weekly_usage.items():
    print(f"{date.strftime('%Y-%m-%d')}: {usage:,.2f} credits")

# Calculate and print trend information
slope = z[0]
intercept = z[1]
print(f"\nTrend Analysis:")
print(f"Slope: {slope:,.2f} credits per week")
print(f"Intercept: {intercept:,.2f} credits")
print(f"Trend line equation: y = {slope:,.2f}x + {intercept:,.2f}")

print(f"\nPlot saved to {output_file}")

# Open the plot in Preview
subprocess.run(['open', output_file]) 