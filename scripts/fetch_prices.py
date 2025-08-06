import requests
import pandas as pd
import datetime

# Define the CoinGecko API, URL and parameters
url = "https://api.coingecko.com/api/v3/coins/markets"
params = {
    "vs_currency": "usd", # get prices in USD
    "order": "market_cap_desc", # order by market cap descending
    "per_page": 10, # get top 10 coins
    "page": 1, # first page
    "sparkline": False # no sparkline data
}

# Make GET request to CoinGecko API
response = requests.get(url, params=params)
# Check for errors in the response
if response.status_code != 200:
    print(f"Error fetching data: {response.status_code}")
    exit()

# Parse the JSON response
data = response.json()


# Tranfsform the data into a DataFrame

# Create a list of cleaned data
rows = []

for coin in data:
    rows.append({
        "id": coin["id"],
        "symbol": coin["symbol"],
        "name": coin["name"],
        "current_price": coin["current_price"],
        "market_cap": coin["market_cap"],
        "price_change_24h": coin["price_change_24h"],
        "price_change_percentage_24h": coin["price_change_percentage_24h"],
        "last_updated": coin["last_updated"],
        "fetched_at": datetime.datetime.now().isoformat() # when it was fetched


    })

# Convert the list of rows into a DataFrame
df = pd.DataFrame(rows)

# Print to check the DataFrame
print(df.head())

# Save the DataFrame to a CSV file
df.to_csv("top_10_crypto.csv", index=False)
print("✅ Data saved to top_10_crypto.csv")