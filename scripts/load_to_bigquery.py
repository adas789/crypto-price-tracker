import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
DATASET_NAME = os.getenv("DATASET_NAME")
TABLE_NAME = os.getenv("TABLE_NAME")
KEY_FILE_PATH = os.getenv("KEY_FILE_PATH")

# LOAD CSV
try:
    df = pd.read_csv("top_10_crypto.csv")

    if df.empty:
        raise ValueError("DataFrame is empty. Please check the CSV file.")

    # Authenticate using service account key
    credentials = service_account.Credentials.from_service_account_file(KEY_FILE_PATH)
    client = bigquery.Client(credentials=credentials, project=PROJECT_ID)

    # Full table reference
    table_ref = f"{PROJECT_ID}.{DATASET_NAME}.{TABLE_NAME}"

    # Load DataFrame to BigQuery
    job_config = bigquery.LoadJobConfig(
        autodetect=True, # Automatically detect schema
        write_disposition="WRITE_TRUNCATE" # Overwrite table data
    )

    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()  # Wait for the job to complete

    print(f"✅ Uploaded {len(df)} rows to {table_ref}")
    print("✅ Data successfully loaded into BigQuery")

except FileNotFoundError as e:
    print(f"❌ File not found: {e}")

except Exception as e:
    print(f"❌ An error occurred: {e}")