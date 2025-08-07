{{config(
    materialized='table'
)}}

SELECT DISTINCT
    id as coin_id,
    name,
    symbol
FROM {{source('crypto_data', 'top_10_prices')}}