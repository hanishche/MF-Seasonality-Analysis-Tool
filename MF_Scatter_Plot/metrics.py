import pandas as pd
import numpy as np
from scipy.stats import linregress

# Function to calculate Omega Ratio
def omega_ratio(returns, threshold=0):
    if returns is None or len(returns) == 0 or returns.dropna().empty:
        return np.nan
    excess_returns = returns - threshold
    numerator = excess_returns[excess_returns > 0].sum()
    denominator = -excess_returns[excess_returns < 0].sum()
    return numerator / (denominator if denominator != 0 else np.nan)

# Function to calculate Max Drawdown and Drawdown Dates
def max_drawdown(nav):
    if nav is None or nav.empty or nav.isna().all():
        return np.nan, pd.NaT, pd.NaT
    nav = nav.dropna()
    if nav.empty:
        return np.nan, pd.NaT, pd.NaT
    peak = nav.cummax()
    drawdown = (peak - nav) / peak
    max_dd = drawdown.max()
    if pd.isna(max_dd):
        return np.nan, pd.NaT, pd.NaT
    max_dd_index = drawdown.idxmax()
    try:
        peak_before_drawdown = peak.loc[max_dd_index]
        peak_date = peak[peak == peak_before_drawdown].index[0]
        trough_date = max_dd_index
    except Exception:
        peak_date = pd.NaT
        trough_date = pd.NaT
    return max_dd, peak_date, trough_date

# Function to calculate Recovery Time and Recovery Date
def recovery_time(nav):
    if nav is None or nav.empty or nav.isna().all():
        return None, None
    nav = nav.dropna()
    if nav.empty:
        return None, None
    peak = nav.cummax()
    drawdown = (peak - nav) / peak
    max_dd_index = drawdown.idxmax()
    try:
        peak_before_drawdown = peak.loc[max_dd_index]
        recovery_indices = nav[nav.index >= max_dd_index][nav >= peak_before_drawdown]
        if recovery_indices.empty:
            return None, None
        recovery_index = recovery_indices.index[0]
        recovery_time_days = (recovery_index - max_dd_index).days
        return recovery_time_days, recovery_index
    except Exception:
        return None, None

# Function to calculate Calmar Ratio
def calmar_ratio(returns, nav, frequency='monthly'):
    if returns is None or len(returns) == 0 or returns.dropna().empty:
        return np.nan
    if frequency == 'daily':
        annualized_return = returns.mean() * 252
    elif frequency == 'weekly':
        annualized_return = returns.mean() * 52
    elif frequency == 'monthly':
        annualized_return = returns.mean() * 12
    else:
        raise ValueError("Frequency must be 'daily', 'weekly', or 'monthly'.")
    max_dd = max_drawdown(nav)[0]  # Only need the drawdown value
    return annualized_return / (max_dd if max_dd not in [0, np.nan] else np.nan)

# Function to calculate Beta, Alpha, and R-squared
def calculate_beta_alpha_r2(returns, market_returns, annual_rate):
    if returns is None or market_returns is None or len(market_returns) != len(returns) or len(returns) == 0:
        return np.nan, np.nan, np.nan
    if returns.dropna().empty or market_returns.dropna().empty:
        return np.nan, np.nan, np.nan
    try:
        beta_value, alpha, r_value, _, _ = linregress(market_returns, returns)
        r_squared = r_value ** 2
        return beta_value, alpha * annual_rate * 100, r_squared
    except Exception:
        return np.nan, np.nan, np.nan

# Function to calculate Downside Capture Ratio
def downside_capture_ratio(returns, market_returns):
    if returns is None or market_returns is None or len(returns) == 0 or len(market_returns) == 0:
        return np.nan
    downside_market = market_returns[market_returns < 0]
    downside_fund = returns[market_returns < 0]
    if downside_market.mean() == 0 or downside_market.dropna().empty:
        return np.nan
    return downside_fund.mean() / downside_market.mean()

# Function to calculate Upside Capture Ratio
def upside_capture_ratio(returns, market_returns):
    if returns is None or market_returns is None or len(returns) == 0 or len(market_returns) == 0:
        return np.nan
    up_market = market_returns[market_returns > 0]
    up_fund = returns[market_returns > 0]
    if up_market.mean() == 0 or up_market.dropna().empty:
        return np.nan
    return up_fund.mean() / up_market.mean()