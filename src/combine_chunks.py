import pandas as pd
import glob
import os
from datetime import datetime

# Create reports directory if it doesn't exist
os.makedirs("/tmp/reports", exist_ok=True)

# Get all CSV files in the reports directory
csv_files = glob.glob('/tmp/reports/*.csv')

if not csv_files:
    print("No CSV files found in /tmp/reports/")
    exit(1)

print(f"Found {len(csv_files)} CSV files to combine")

# Read and combine all CSV files
dfs = []
for file in csv_files:
    print(f"Reading {file}")
    try:
        df = pd.read_csv(file, low_memory=False, on_bad_lines='skip')
        dfs.append(df)
    except Exception as e:
        print(f"Error reading {file}: {str(e)}")
        continue

if not dfs:
    print("No data to combine")
    exit(1)

# Combine all dataframes
print("Combining data...")
combined_df = pd.concat(dfs, ignore_index=True)

# Remove duplicates if any
print("Removing duplicates...")
combined_df = combined_df.drop_duplicates()

# Sort by JOB_RUN_STARTED_AT if the column exists
if 'JOB_RUN_STARTED_AT' in combined_df.columns:
    print("Sorting by JOB_RUN_STARTED_AT...")
    combined_df['JOB_RUN_STARTED_AT'] = pd.to_datetime(combined_df['JOB_RUN_STARTED_AT'], errors='coerce')
    combined_df = combined_df.sort_values('JOB_RUN_STARTED_AT')

# Save the combined file
output_file = '/tmp/reports/usage_report_combined.csv'
print(f"Saving combined data to {output_file}")
combined_df.to_csv(output_file, index=False)

print(f"\nCombined {len(combined_df)} rows into {output_file}")
print(f"Original files had {sum(len(df) for df in dfs)} rows")
print(f"Removed {sum(len(df) for df in dfs) - len(combined_df)} duplicate rows") 