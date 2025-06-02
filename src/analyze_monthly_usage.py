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

# Resample by month, label months by their start date
monthly_usage = df['TOTAL_CREDITS'].resample('MS').sum()

# Calculate month-over-month growth
growth_rates = monthly_usage.pct_change() * 100

# Plot
plt.figure(figsize=(14, 7))
sns.set_style("whitegrid")

# Create the bar plot
bars = plt.bar(monthly_usage.index.strftime('%Y-%m'), monthly_usage.values, color='skyblue')

# Add value labels on top of each bar with growth rates
for i, (date, usage) in enumerate(monthly_usage.items()):
    if i == 0:  # First month has no growth rate
        label = f'{usage:,.0f}'
    else:
        growth = growth_rates[date]
        label = f'{usage:,.0f}\n({growth:+.1f}%)'
    plt.text(i, usage, label, ha='center', va='bottom')

plt.title('CircleCI Monthly Credit Usage')
plt.xlabel('Month')
plt.ylabel('Total Credits')

# Format y-axis to show actual numbers instead of scientific notation
plt.gca().yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

plt.tight_layout()
output_file = '/tmp/reports/monthly_credit_usage.png'
plt.savefig(output_file)
plt.close()

# Print summary
print("\nMonthly Credit Usage:")
for date, usage in monthly_usage.items():
    print(f"{date.strftime('%Y-%m')}: {usage:,.2f} credits")

# Calculate month-over-month growth
print("\nMonth-over-Month Growth:")
for date, rate in growth_rates.items():
    if not pd.isna(rate):  # Skip the first month which has no previous month to compare to
        print(f"{date.strftime('%Y-%m')}: {rate:+.1f}%")

print(f"\nPlot saved to {output_file}")

# Open the plot in Preview
subprocess.run(['open', output_file]) 