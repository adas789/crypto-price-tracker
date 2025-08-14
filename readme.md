
# Crypto Price Tracker

An end-to-end data engineering project that demonstrates a modern data pipeline:

- **Extracts** top 10 cryptocurrency prices from the CoinGecko API (hourly)
- **Loads** raw data into Google BigQuery
- **Transforms** data into dimension and fact tables using DBT
- **Ensures data quality** with DBT tests
- (Optional) Visualizes trends in Power BI

## 🚀 Project Structure

- `dags/` — Airflow DAGs for orchestrating the pipeline
- `scripts/` — Python scripts for extraction/loading (if needed)
- `crypto_dbt/` — DBT project for modeling and testing
- `docker-compose.airflow.yml` — Docker Compose for local Airflow + Postgres
- `secrets/` — Service account key for BigQuery (not committed)

## 🔧 Tech Stack

- Python 3.10
- Apache Airflow (Docker)
- Google BigQuery
- DBT (BigQuery adapter)
- CoinGecko API


## 🏗️ How It Works

1. **Airflow DAG** runs hourly, fetching the top 10 coins by market cap from CoinGecko and loading them into BigQuery.
2. **Data Validation**: After extraction, a validation task checks that all expected coins are present, prices are positive, and timestamps are valid. The pipeline fails fast if data is missing or malformed.
3. **DBT** transforms raw data into clean dimension (`dim_coin`) and fact (`fact_prices`) tables, deduplicating and testing for data quality.
4. (Optional) Data can be visualized in Power BI or other BI tools.

## ⚡ Quickstart

1. **Clone the repo:**
   ```sh
   git clone https://github.com/adas789/crypto-price-tracker.git
   cd crypto-price-tracker
   ```
2. **Set up Google Cloud:**
   - Create a BigQuery dataset and table (see `sql/create_tables.sql` for schema)
   - Download a service account key and place it in `secrets/crypto-tracker-creds.json`
3. **Start Airflow (Docker):**
   ```sh
   docker compose -f docker-compose.airflow.yml up -d
   ```
4. **Run DBT models/tests:**
   ```sh
   cd crypto_dbt
   dbt run
   dbt test
   ```


## 🧑‍💻 Data Engineering Best Practices

- Modular, idempotent DAGs
- Data validation step in the pipeline
- Parameterized configs and secrets
- Data quality tests (DBT)
- Deduplication in models
- Clear documentation and code comments

## 📁 Example DBT Tests (see `crypto_dbt/models/schema.yml`)
```yaml
  - name: dim_coin
    columns:
      - name: coin_id
        tests: [not_null, unique]
```

## 📊 Example Query
```sql
SELECT * FROM `crypto_data.fact_prices` WHERE price_date = CURRENT_DATE()
```

## 📌 Coming Soon
- Power BI dashboard
- Deployment guide
- Freemium model for crypto traders