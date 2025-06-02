###
# This script shows an example of how data from the usage report can be manipulated to create graphs
###

# Import modules
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import subprocess

# Find the merged files
input_file = '/tmp/reports/usage_report_combined.csv'

# Read the merged CSV data into a pandas dataframe
print(f"Reading {input_file}")

try:
    df = pd.read_csv(input_file, low_memory=False, on_bad_lines='skip')
except Exception as e:
    print(f"Error reading CSV file: {str(e)}")
    exit(1)

# Group the data by 'PROJECT_NAME' and 'VCS_URL', and calculate the sum of 'TOTAL_CREDITS' for each group
grouped_df = df.groupby(['PROJECT_NAME', 'VCS_URL'])['TOTAL_CREDITS'].sum()

# Sort the grouped dataframe by 'TOTAL_CREDITS' in descending order
sorted_df = grouped_df.sort_values(ascending=False)

# Save the sorted dataframe into a CSV file
sorted_file_path = '/tmp/reports/sorted_credits.csv'
sorted_df.to_csv(sorted_file_path, header=True)

# Print message after saving the sorted DataFrame
print(f"Sorted data saved to {sorted_file_path}")

# Filter out rows with 0 total credits
print("To reduce graph noise, removing all projects that have 0 credits spent")
grouped_df = grouped_df[grouped_df != 0]

# Create a bar plot to show total credits per project
plt.figure(figsize=(15, 10))
grouped_df.plot(kind='bar')
plt.ylabel('Total Credits')
plt.xlabel('Project')
plt.title('Total Credits per Project')

# Save the plot as an artifact
plt.savefig('/tmp/reports/total_credits_per_project.png', bbox_inches='tight')

# Print the total credits per project
print(grouped_df)

# Print message after saving the plot
print("Plot saved as 'total_credits_per_project.png' in the reports directory")

# Group by JOB_RUN_STARTED_AT and sum TOTAL_CREDITS
print("Grouping data by date...")
df['JOB_RUN_STARTED_AT'] = pd.to_datetime(df['JOB_RUN_STARTED_AT'], errors='coerce')
df = df.groupby('JOB_RUN_STARTED_AT')['TOTAL_CREDITS'].sum().reset_index()

# Sort by date
print("Sorting data...")
df = df.sort_values('JOB_RUN_STARTED_AT')

# Create the plot
print("Creating plot...")
plt.figure(figsize=(12, 6))
sns.barplot(x='JOB_RUN_STARTED_AT', y='TOTAL_CREDITS', data=df)

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Add labels and title
plt.xlabel('Date')
plt.ylabel('Total Credits')
plt.title('CircleCI Credit Usage Over Time')

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Save the plot
output_file = '/tmp/reports/credit_usage.png'
print(f"Saving plot to {output_file}")
plt.savefig(output_file)
plt.close()

print("Plot saved successfully!")

# Open the plot in Preview
print("Opening plot in Preview...")
subprocess.run(['open', output_file])