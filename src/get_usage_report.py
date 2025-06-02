# Import modules
import os
import requests
import json
import time
import gzip
import sys

# Build data to send with requests
ORG_ID = os.getenv('ORG_ID')
CIRCLECI_TOKEN = os.getenv('CIRCLECI_API_TOKEN')
START_DATE = os.getenv('START_DATE')
END_DATE = os.getenv('END_DATE')
FILENAME_PREFIX = os.getenv('FILENAME_PREFIX', 'usage_report')  # Default to 'usage_report' if not specified

if not all([ORG_ID, CIRCLECI_TOKEN, START_DATE, END_DATE]):
    print("Error: Missing required environment variables")
    print("Please ensure ORG_ID, CIRCLECI_API_TOKEN, START_DATE, and END_DATE are set")
    sys.exit(1)

post_data = {
    "start": f"{START_DATE}T00:00:01Z",
    "end": f"{END_DATE}T00:00:01Z",
    "shared_org_ids": []
}

# Request the usage report
try:
    response = requests.post(
        f"https://circleci.com/api/v2/organizations/{ORG_ID}/usage_export_job",
        headers={"Circle-Token": CIRCLECI_TOKEN, "Content-Type": "application/json"},
        data=json.dumps(post_data)
    )
    response.raise_for_status()  # Raise an exception for bad status codes
except requests.exceptions.RequestException as e:
    print(f"Error making API request: {str(e)}")
    sys.exit(1)

#print out the API response for the usage report request
print("Response Content:", response.json())  # This will parse the JSON response

# Once requested, the report can take some time to process, so a retry is built-in
if response.status_code == 201:
    print("Report requested successfully")
    data = response.json()
    USAGE_REPORT_ID = data.get("usage_export_job_id")
    print(f"Report ID is {USAGE_REPORT_ID}")
    
    # Check if the report is ready for downloading as it can take a while to process
    for i in range(5):
        print("Checking if report can be downloaded")
        try:
            report = requests.get(
                f"https://circleci.com/api/v2/organizations/{ORG_ID}/usage_export_job/{USAGE_REPORT_ID}",
                headers={"Circle-Token": CIRCLECI_TOKEN}
            ).json()
        except requests.exceptions.RequestException as e:
            print(f"Error checking report status: {str(e)}")
            sys.exit(1)

        report_status = report.get("state")

        # Download the report and save it
        if report_status == "completed":
            print("Report generated. Now Downloading...")
            download_urls = report.get("download_urls", [])

            if not os.path.exists("/tmp/reports"):
                os.makedirs("/tmp/reports")
            
            for idx, url in enumerate(download_urls):
                try:
                    r = requests.get(url)
                    r.raise_for_status()
                    with open(f"/tmp/{FILENAME_PREFIX}_{idx}.csv.gz", "wb") as f:
                        f.write(r.content)
                    
                    with gzip.open(f"/tmp/{FILENAME_PREFIX}_{idx}.csv.gz", "rb") as f_in:
                        with open(f"/tmp/reports/{FILENAME_PREFIX}_{idx}.csv", "wb") as f_out:
                            f_out.write(f_in.read())

                    print(f"File {idx} downloaded and extracted")
                except (requests.exceptions.RequestException, IOError) as e:
                    print(f"Error downloading or extracting file {idx}: {str(e)}")
                    continue

            print("All files downloaded and extracted to the /tmp/reports directory")
            break
        
        elif report_status == "processing":
            print("Report still processing. Retrying in 1 minute...")
            time.sleep(60)  # Wait for 60 seconds before retrying
        
        else:
            print(f"Report status: {report_status}. Error occurred.")
            break
    else:
        print("Report is still in processing state after 5 retries.")
        sys.exit(1)
else:
    # Exit if something else happens, like requests are being throttled
    print(f"Error: {response.status_code} - {response.text}")
    sys.exit(1)
