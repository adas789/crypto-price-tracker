{{config(
    materialized='table'
)}}

{% do ref('dim_coin') %}

WITH ranked AS (
    SELECT
        id AS coin_id,
        current_price,
        market_cap,
        price_change_24h,
        price_change_percentage_24h,
        fetched_at,
        date(fetched_at) AS price_date,
        row_number() OVER (PARTITION BY id ORDER BY fetched_at DESC) AS rn
    FROM {{ source('crypto_data', 'top_10_prices') }}
)

SELECT
    coin_id,
    current_price,
    market_cap,
    price_change_24h,
    price_change_percentage_24h AS price_change_pct_24h,
    price_date
FROM ranked
WHERE rn = 1