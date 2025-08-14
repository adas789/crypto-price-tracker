
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
3. **Configure DBT profile and credentials:**
   - Ensure `profiles.yml` is in the project root (already included in this repo)
   - The service account key should be at `secrets/crypto-tracker-creds.json`
   - Docker Compose mounts these automatically to the correct locations in the Airflow containers:
     - `./profiles.yml:/home/airflow/.dbt/profiles.yml:ro`
     - `./secrets/crypto-tracker-creds.json:/opt/airflow/secrets/crypto-tracker-creds.json:ro`

4. **Start Airflow (Docker):**
   ```sh
   docker compose up -d
   ```

5. **Run DBT models/tests manually (optional):**
   ```sh
   docker compose exec airflow-webserver bash
   dbt run
   dbt test
   ```


## 🧑‍💻 Data Engineering Best Practices
## 🛠️ Troubleshooting

- If DBT cannot find your profile or credentials, ensure the `profiles.yml` and keyfile are mounted as shown above and the keyfile path in `profiles.yml` is `/opt/airflow/secrets/crypto-tracker-creds.json`.
- If you change `profiles.yml` or the keyfile, restart the containers: `docker compose down && docker compose up -d`.

## ✅ Airflow + DBT Automation

- The Airflow DAG automatically triggers DBT runs after loading data to BigQuery.
- All configuration is containerized for reproducibility and portability.

- Modular, idempotent DAGs
- Data validation step in the pipeline
- Parameterized configs and secrets
- Data quality tests (DBT)
- Deduplication in models
- Clear documentation and code comments
- Comprehensive logging for all pipeline steps: Each Airflow task logs key events, record counts, validation results, and errors for full traceability and easier debugging.

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
- Freemium model for crypto lovers