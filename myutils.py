import pandas as pd
import numpy as np
from numba import njit, prange
from typing import Union, List

@njit(cache=True)
def get_expanding_kelly(
    returns: Union[pd.DataFrame, pd.Series],
    window: int = 400,
    r: float = 0.02,
    days: int = 250,
) -> pd.DataFrame:
    r_adjusted = (1 + r) ** (1 / days) - 1
    mean = returns.expanding(window).mean().dropna()
    return_exces = mean - r_adjusted

    var = returns.expanding(window).var().dropna()
    kelly = return_exces / var

    return kelly

def get_rolling_kelly(
    returns: Union[pd.DataFrame, pd.Series],
    window: int = 400,
    r: float = 0.02,
    days: int = 250,
) -> pd.DataFrame:
    r_adjusted = (1 + r) ** (1 / days) - 1
    mean = returns.rolling(window).mean().dropna()
    return_exces = mean - r_adjusted

    var = returns.rolling(window).var().dropna()
    kelly = return_exces / var

    return kelly