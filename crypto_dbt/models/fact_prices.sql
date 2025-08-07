{{config(
    materialized='table'
)}}

{% do ref('dim_coin') %}

SELECT
    id AS coin_id,
    current_price,
    market_cap,
    price_change_24h,
    price_change_percentage_24h AS price_change_pct_24h,
    DATE(fetched_at) AS price_date
FROM {{source('crypto_data', 'top_10_prices')}}