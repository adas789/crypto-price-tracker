{{config(
    materialized='table'
)}}

WITH ranked AS (
    SELECT
        id AS coin_id,
        name,
        symbol,
        fetched_at,
        row_number() OVER (PARTITION BY id ORDER BY fetched_at DESC) AS rn
    FROM {{source('crypto_data', 'top_10_prices')}}
)

SELECT DISTINCT
    coin_id,
    name,
    symbol,
    fetched_at
FROM ranked
WHERE rn = 1