from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import json
from google.cloud import bigquery
import logging
from airflow.operators.bash import BashOperator

#--------------- CONFIGURATION ---------------#
PROJECT_ID = "crypto-price-tracker-468210"
DATASET = "crypto_data"
TABLE = "top_10_prices"

# Default arguments for the DAG
default_args = {
    'owner': 'adas',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Task 1: Extract prices from CoinGecko API
def extract_prices(**kwargs):
    logging.info("Starting extraction of crypto prices from CoinGecko API")
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 10,
        'page': 1,
        'sparkline': 'false',
        'price_change_percentage': '24h'
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    logging.info(f"Fetched {len(data)} records from CoinGecko API")
    kwargs['ti'].xcom_push(key='crypto_data', value=data)

# Task 2: Validate the fetched data
def validate_data(**kwargs):
    logging.info("Starting data validation")
    ti = kwargs['ti']
    data = ti.xcom_pull(key='crypto_data', task_ids='extract_prices')

    if not data or len(data) < 2:
        logging.error("Validation failed: Insufficient data fetched from CoinGecko API.")
        raise ValueError("Insufficient data fetched from CoinGecko API.")
    
        # Ensure the main coins are present
    expected = {"bitcoin", "ethereum"}
    seen = {c.get("id") for c in data}
    if not expected.issubset(seen):
        logging.error(f"Validation failed: missing expected coins. Seen: {seen}")
        raise ValueError(f"Validation failed: missing expected coins. Seen: {seen}")

    for coin in data:
        cid = coin.get("id")
        price = coin.get("current_price")
        last_updated = coin.get("last_updated")
        if price is None or price <= 0:
            logging.error(f"Validation failed: Invalid price for coin {cid}: {price}")
            raise ValueError(f"Invalid price for coin {cid}: {price}")
        if not last_updated:
            logging.error(f"Validation failed: Missing last updated timestamp for coin {cid}")
            raise ValueError(f"Missing last updated timestamp for coin {cid}")
    logging.info("Data validation passed successfully")
        

        
        # -------- Additional validation can be added here as needed --------

# Task 3: Load data to BigQuery
def load_to_bigquery(**kwargs):
    logging.info("Starting data load to BigQuery")
    # Pull the data from XCom and insert into BigQuery
    data = kwargs['ti'].xcom_pull(key='crypto_data', task_ids='extract_prices')

    # Initialize BigQuery client
    client = bigquery.Client(project=PROJECT_ID)

    # Build the full table ID
    table_id = f"{PROJECT_ID}.{DATASET}.{TABLE}"

    # Format the data as a list of rows to insert, matching the BigQuery schema
    rows = []
    fetched_at = datetime.utcnow().isoformat()
    for coin in data:
        rows.append({
            "id": coin.get("id"),
            "symbol": coin.get("symbol"),
            "name": coin.get("name"),
            "current_price": coin.get("current_price"),
            "market_cap": coin.get("market_cap"),
            "price_change_24h": coin.get("price_change_24h"),
            "price_change_percentage_24h": coin.get("price_change_percentage_24h"),
            "last_updated": coin.get("last_updated"),
            "fetched_at": fetched_at
        })

    # Insert rows into BigQuery
    logging.info(f"Inserting {len(rows)} rows into BigQuery table {table_id}")
    errors = client.insert_rows_json(table_id, rows)
    if errors:
        logging.error(f"Failed to insert rows: {errors}")
        raise Exception(f"Failed to insert rows: {errors}")
    logging.info(f"Successfully inserted {len(rows)} rows into BigQuery table {table_id}")
    
#---------------- DAG DEFINITION ---------------#

with DAG(
    dag_id='crypto_price_tracker_dag', # Unique identifier for the DAG
    default_args=default_args,
    description='A DAG to track cryptocurrency prices and load them into BigQuery',
    schedule_interval='@hourly',  # Run hourly
    start_date=datetime(2025, 8, 8),
    catchup=False,  # Do not backfill
    tags=['crypto', 'bigquery'],
) as dag:
    
    # Extract data from CoinGecko API
    extract = PythonOperator(
        task_id='extract_prices',
        python_callable=extract_prices,
    )

    # Validate the extracted data
    validate = PythonOperator(
        task_id='validate_data',
        python_callable=validate_data,
    )

    # Load data into BigQuery
    load = PythonOperator(
        task_id='load_to_bigquery',
        python_callable=load_to_bigquery,
    )

    # Create a BashOperator to run the dbt commands
    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='cd /opt/airflow/crypto_dbt && dbt run',
    )

    #Create a BashOperator to run the dbt tests
    dbt_tests = BashOperator(
        task_id='dbt_tests',
        bash_command='cd /opt/airflow/crypto_dbt && dbt test',
    )

    # Set task dependencies
    extract >> validate >> load >> dbt_run >> dbt_tests
