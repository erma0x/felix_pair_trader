import time
import datetime
import numpy as np
import pandas as pd
import yfinance as yf

def calculate_spread(asset1, asset2):
    """
    Calculates the spread between two assets.

    Arguments:
    - asset1: Symbol of the first asset.
    - asset2: Symbol of the second asset.

    Returns:
    - spread: Series representing the spread between the two assets.
    """
    spread = asset1 - asset2
    return spread

def calculate_statistics(spread, window):
    """
    Calculates the historical mean and standard deviation of the spread.

    Arguments:
    - spread: Series representing the spread between two assets.
    - window: Number of days for calculating the historical statistics.

    Returns:
    - spread_mean: Series representing the historical mean of the spread.
    - spread_std: Series representing the historical standard deviation of the spread.
    """
    spread_mean = spread.rolling(window).mean()
    spread_std = spread.rolling(window).std()
    return spread_mean, spread_std

def pair_trading_strategy(asset1, asset2, threshold, window, exit_days, take_profit, stop_loss):
    """
    Executes a pair trading strategy on two assets.

    Arguments:
    - asset1: Symbol of the first asset.
    - asset2: Symbol of the second asset.
    - threshold: Number of standard deviations for the trading signal.
    - window: Number of days for calculating the historical statistics.
    - exit_days: Number of days for the trade exit based on time (None if not used).
    - take_profit: Take profit target as a percentage (None if not used).
    - stop_loss: Stop loss level as a percentage (None if not used).

    Returns:
    - spread: Series representing the spread between the two assets.
    - spread_mean: Series representing the historical mean of the spread.
    - spread_std: Series representing the historical standard deviation of the spread.
    - trade_entry_date: Date of trade entry.
    - trade_exit_date: Date of trade exit.
    - entry_price_asset1: Entry price of asset1.
    - entry_price_asset2: Entry price of asset2.
    - exit_price_asset1: Exit price of asset1.
    - exit_price_asset2: Exit price of asset2.
    """
    data = yf.download([asset1, asset2], start="yyyy-mm-dd", end="yyyy-mm-dd")
    asset1_prices = data['Adj Close'][asset1]
    asset2_prices = data['Adj Close'][asset2]

    spread = calculate_spread(asset1_prices, asset2_prices)
    spread_mean, spread_std = calculate_statistics(spread, window)

    trade_active = False
    entry_price_asset1 = 0
    entry_price_asset2 = 0
    trade_entry_date = None
    exit_price_asset1 = 0
    exit_price_asset2 = 0
    trade_exit_date = None

    for i in range(window, len(spread)):
        current_spread = spread[i]
        current_mean = spread_mean[i]
        current_std = spread_std[i]

        if not trade_active and current_spread > (current_mean + threshold * current_std):
            entry_price_asset1 = asset1_prices[i]
            entry_price_asset2 = asset2_prices[i]
            trade_entry_date = spread.index[i]
            trade_active = True
        elif not trade_active and current_spread < (current_mean - threshold * current_std):
            entry_price_asset1 = asset1_prices[i]
            entry_price_asset2 = asset2_prices[i]
            trade_entry_date = spread.index[i]
            trade_active = True

        if trade_active:
            if exit_days is not None and (spread.index[i] - trade_entry_date).days >= exit_days:
                exit_price_asset1 = asset1_prices[i]
                exit_price_asset2 = asset2_prices[i]
                trade_exit_date = spread.index[i]
                trade_active = False
            elif take_profit is not None and (entry_price_asset1 * (1 + take_profit)) <= asset1_prices[i]:
                exit_price_asset1 = asset1_prices[i]
                exit_price_asset2 = asset2_prices[i]
                trade_exit_date = spread.index[i]
                trade_active = False
            elif stop_loss is not None and (entry_price_asset1 * (1 - stop_loss)) >= asset1_prices[i]:
                exit_price_asset1 = asset1_prices[i]
                exit_price_asset2 = asset2_prices[i]
                trade_exit_date = spread.index[i]
                trade_active = False

        spread_mean[i+1], spread_std[i+1] = calculate_statistics(spread[i-window+1:i+1], window)

    return spread, spread_mean, spread_std, trade_entry_date, trade_exit_date, entry_price_asset1, entry_price_asset2, exit_price_asset1, exit_price_asset2

asset1 = "ES"  # E-mini S&P 500
asset2 = "NQ"  # E-mini NASDAQ 100
threshold = 2  # Number of standard deviations for the trading signal
window = 20  # Number of days for calculating the historical statistics
exit_days = 10  # Number of days for the trade exit based on time (None if not used)
take_profit = 0.05  # Take profit target as a percentage (None if not used)
stop_loss = 0.03  # Stoploss level as a percentage (None if not used)

spread, spread_mean, spread_std, entry_date, exit_date, entry_price_asset1, entry_price_asset2, exit_price_asset1, exit_price_asset2 = pair_trading_strategy(asset1, asset2, threshold, window, exit_days, take_profit, stop_loss)

data = pd.DataFrame({'Spread': spread, 'Mean': spread_mean, 'Std': spread_std})
print(data)

if entry_date is not None:
    print("Trade entry:", entry_date)
    print("Entry price", asset1 + ":", entry_price_asset1)
    print("Entry price", asset2 + ":", entry_price_asset2)

if exit_date is not None:
    print("Trade exit:", exit_date)
    print("Exit price", asset1 + ":", exit_price_asset1)
    print("Exit price", asset2 + ":", exit_price_asset2)

