import pandas as pd
import numpy as np
from numba import njit, prange
from typing import Union, List

def process_data(df):
    # 데이터프레임 뒤집기 및 인덱스 재설정
    df = df[::-1].reset_index(drop=True)
    
    # 'Date' 열을 인덱스로 설정
    df.set_index('Date', inplace=True)
    
    # 'Change %' 열을 수치로 변환하여 'Change' 열로 추가
    df['Change'] = df['Change %'].str.rstrip('%').astype(float) / 100
    
    # 필요한 열들을 숫자로 변환
    numeric_cols = ['Price', 'Open', 'High', 'Low']
    for col in numeric_cols:
        try:
            df[col] = df[col].str.replace(',', '').astype(float)
        except (KeyError, AttributeError):
            pass
    
    # 'Vol.' 열 삭제
    try:
        df.drop('Vol.', axis=1, inplace=True)
    except KeyError:
        pass
    
    return df

def get_historical_var(df, window_size, percentile):
    df['VaR'] = df['Change'].rolling(window=window_size).quantile(percentile, interpolation='lower')
    # df.dropna(subset=['VaR'], inplace=True) 
        # NaN 드랍하기
    return df

def calculate_daily_rf(df, days):
    df['rf'] = (1 + df['rf']/100) ** (1 / days) - 1
    df = df.set_index('Date')
    return df

# @njit(cache=True)
# def get_rolling_kelly(
#     df, 
#     # returns: Union[pd.DataFrame, pd.Series],
#     window: int = 400,
#     r: float = 0.02,
#     days: int = 250,
# ) -> pd.DataFrame:
# #     r = (1 + r) ** (1 / days) - 1
#     returns = df['Change']
#     mean = returns.rolling(window).mean().dropna()
#     print(mean)
#     return_exces = mean - r

#     var = returns.rolling(window).var().dropna()
#     kelly = return_exces / var

#     return kelly

def get_rolling_kelly(
    df, 
    window: int = 400,
) -> pd.DataFrame:
    mean = df['Change'].rolling(window).mean().dropna()
    return_exces = mean -  df['rf']

    var = df['Change'].rolling(window).var().dropna()
    kelly = return_exces / var
    kelly = kelly.dropna()

    return kelly

def get_cumulative_returns(df, rebalancing):
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
            portfolio[i] = cash[i-1] + equity[i-1]
            # portfolio[i] = equity[i-1] * (1 + row['Change']) + cash[i-1] * (1 + row['rf'])
            if i % rebalancing == 0:
                equity[i] = portfolio[i] * row['kelly_ratio']
                cash[i] = portfolio[i] * (1 - row['kelly_ratio'])
            else:
                equity[i] = equity[i-1] * (1 + row['Change'])
                cash[i] = cash[i-1] * (1 + row['rf'])
    df.loc[:, 'portfolio'] = portfolio
    df.loc[:, 'equity'] = equity
    df.loc[:, 'cash'] = cash

    return df

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
                portfolio[i] = equity[i-1] * (1 + row['Change']) + cash[i-1] * (1 + row['rf'])
                if portfolio[i] < 0:
                    equity[i] = equity[i-1] * (1 + row['Change']) + row['kelly_ratio']
                    cash[i] = cash[i-1] * (1 + row['rf']) - row['kelly_ratio']
                    # equity[i] = equity[i-1] * (1 + row['Change'])
                    # cash[i] = cash[i-1] * (1 + row['rf'])
                else:
                    equity[i] = portfolio[i] * row['kelly_ratio'] 
                    cash[i] = portfolio[i] * (1 - row['kelly_ratio'])                   
            elif row['sell_signal']:
                portfolio[i] = equity[i-1] * (1 + row['Change']) + cash[i-1] * (1 + row['rf'])
                equity[i] = 0
                cash[i] = portfolio[i]
            else:
                equity[i] = equity[i-1] * (1 + row['Change'])
                cash[i] = cash[i-1] * (1 + row['rf'])
    df.loc[:, 'portfolio'] = portfolio
    df.loc[:, 'equity'] = equity
    df.loc[:, 'cash'] = cash

    return df