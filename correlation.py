import time
import pandas as pd
import numpy as np
from binance.client import Client

# Insert your API key and secret here
api_key = ""
api_secret = ""

# Create a client object for the Binance API
client = Client(api_key, api_secret)

# Get historical price data for ETH and BTC in the last 50 days
data = client.get_klines(
    symbol="AAVEUSDT",
    interval=Client.KLINE_INTERVAL_1DAY,
    limit=100
)

# Convert the historical data into a pandas DataFrame
df = pd.DataFrame(data, columns=[
    "open_time", "open", "high", "low", "close",
    "volume", "close_time", "quote_asset_volume", "num_trades",
    "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
])

print(pd.to_numeric(df["close"]).head())
print(pd.to_numeric(df["close"]).tail())
#print(type((eth_btc_df["close"].iloc[1])))

# Calculate the correlation between ETH and BTC prices
corr1 = pd.to_numeric(df["close"]).corr(pd.to_numeric(df["close"]), method="pearson")
corr2 = pd.to_numeric(df["close"]).corr(pd.to_numeric(df["close"]), method="kendall")
corr3 = pd.to_numeric(df["close"]).corr(pd.to_numeric(df["close"]), method="spearman")
corr4 = np.corrcoef(pd.to_numeric(df["close"]))

# Print the correlation values
print(corr1, corr2, corr3, corr4)

