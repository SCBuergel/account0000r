import requests
import csv

def get_asset_ids(tickers):
    response = requests.get("https://api.coingecko.com/api/v3/coins/list?include_platform=false")
    data = response.json()
    ids = {}
    for item in data:
        if item['symbol'].upper() in tickers:
            ids[item['symbol'].upper()] = item['id']
    return ids

def get_prices(ids, year):
    end_date = f"01-01-{year+1}"
    vs_currency = "usd"
    prices = {}
    for id in ids:
        response = requests.get(f"https://api.coingecko.com/api/v3/coins/{id}/history",
                                params={"date": end_date, "localization": False, "vs_currency": vs_currency})
        data = response.json()
        print(f"RESPONSE: {data}")
        prices[data['symbol'].upper()] = data['market_data']['current_price'][vs_currency]
    return prices

def export_prices(prices, filename):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Asset', 'Price'])
        for asset, price in prices.items():
            writer.writerow([asset, price])


# Define the list of cryptocurrencies to get the end-of-year prices for
assets = ['BTC', 'ETH', 'MKR']

# Define the end year
end_year = 2021

# Load the end-of-year prices for the assets
prices = get_prices(assets, end_year)

# Export the end-of-year prices as a CSV file
export_prices(prices, 'crypto_prices.csv')

