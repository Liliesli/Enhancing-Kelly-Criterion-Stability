import pandas as pd
import numpy as np

def process_data(df):
    df = df[::-1].reset_index(drop=True)
    df.set_index('Date', inplace=True)
    df['Change'] = df['Change %'].str.rstrip('%').astype(float) / 100
    numeric_cols = ['Price', 'Open', 'High', 'Low']
    for col in numeric_cols:
        df[col] = df[col].str.replace(',', '').astype(float)
    df.drop('Vol.', axis=1, inplace=True)
    return df

def calculate_trix(close_prices, n):
    ema1 = close_prices.ewm(span=n, min_periods=n).mean()
    ema2 = ema1.ewm(span=n, min_periods=n).mean()
    ema3 = ema2.ewm(span=n, min_periods=n).mean()
    
    trix = (ema3 - ema3.shift(1)) / ema3.shift(1) * 100
    return trix

def get_historical_var(df, window_size, percentile):
    df['VaR'] = df['Change'].rolling(window=window_size).quantile(percentile, interpolation='lower')
    return df

def calculate_daily_rf(df, days):
    df['rf'] = (1 + df['rf']/100) ** (1 / days) - 1
    df = df.set_index('Date')
    return df

def get_rolling_kelly(df, window: int = 400):
    mean = df['Change'].rolling(window).mean().dropna()
    return_exces = mean -  df['rf']

    var = df['Change'].rolling(window).var().dropna()
    kelly = return_exces / var
    kelly = kelly.dropna()

    return kelly

def get_cumulative_trix_returns(df):
    portfolio = np.zeros(len(df))
    equity = np.zeros(len(df))
    cash = np.zeros(len(df))

    for i, _row in enumerate(df.iterrows()):
        row = _row[1]
        if i == 0:
            portfolio[0] = 1
            cash[0] = 1-row['kelly_ratio']
            equity[0] = row['kelly_ratio']
        else:
            portfolio[i] = equity[i-1] * (1 + row['Change']) + cash[i-1] * (1 + row['rf'])
            if row['buy_signal']:
                if portfolio[i] < 0:
                    equity[i] = equity[i-1] * (1 + row['Change']) + row['kelly_ratio']
                    cash[i] = cash[i-1] * (1 + row['rf']) - row['kelly_ratio']
                else:
                    equity[i] = portfolio[i] * row['kelly_ratio'] 
                    cash[i] = portfolio[i] * (1 - row['kelly_ratio'])                   
            elif row['sell_signal']:
                equity[i] = 0
                cash[i] = portfolio[i]
            else:
                equity[i] = equity[i-1] * (1 + row['Change'])
                cash[i] = cash[i-1] * (1 + row['rf'])
    df.loc[:, 'portfolio'] = portfolio
    df.loc[:, 'equity'] = equity
    df.loc[:, 'cash'] = cash

    return df