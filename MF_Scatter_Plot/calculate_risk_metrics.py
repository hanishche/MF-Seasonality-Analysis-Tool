from metrics import max_drawdown, recovery_time, calculate_beta_alpha_r2, omega_ratio, calmar_ratio, downside_capture_ratio, upside_capture_ratio
import numpy as np

def calculate_risk_metrics(df_final, timeline, risk_free_rate=0.06, freq='monthly', result_type='default'):
    if df_final is None or df_final.empty:
        return None
    df_final=df_final.reset_index(drop=True)
    df_final = df_final.sort_values(by='Date', ascending=True).reset_index(drop=True)

    first = df_final['Close'].iloc[0]
    last = df_final['Close'].iloc[-1]
    time_difference = (df_final['Date'].iloc[-1] - df_final['Date'].iloc[0]).days
    years = np.where(time_difference <= 365.25, 1, round(time_difference / 365.25, 1))
    cagr = ((last / first) ** (1 / years)) - 1
    cagr = cagr * 100

    max_dd, peak_date, trough_date = max_drawdown(df_final.set_index('Date')['Close'].dropna())
    recovery_time_value, recovery_date = recovery_time(df_final.set_index('Date')['Close'].dropna())

    df_final = df_final.dropna(subset=['Fund', 'Return'])
    if df_final.empty:
        return None 
    else:
        returns = df_final['Return']
        market_returns = df_final['Market Return']
        if freq == 'daily':
            annual_rate = 252
        elif freq == 'weekly':
            annual_rate = 52
        elif freq == 'monthly':
            annual_rate = 12
        else:
            raise ValueError("Frequency must be 'daily', 'weekly', or 'monthly'.")
        excess_returns = returns - risk_free_rate / annual_rate
        stdev = returns.std() * np.sqrt(annual_rate)
        sharpe_ratio = np.mean(excess_returns) * annual_rate / (np.std(excess_returns) * np.sqrt(annual_rate) if np.std(excess_returns) != 0 else np.nan)
        downside_returns = returns[returns < returns.mean()].std() * np.sqrt(12)
        sortino_ratio = np.mean(excess_returns) * annual_rate / (downside_returns if downside_returns != 0 else np.nan)
        beta_value, alpha, r_squared = calculate_beta_alpha_r2(returns, market_returns, annual_rate)
        treynor_ratio = np.mean(excess_returns) * annual_rate / (beta_value if beta_value != 0 else np.nan)
        omega = omega_ratio(returns)
        calmar = calmar_ratio(returns, df_final['Close'], freq)
        downside_capture = downside_capture_ratio(returns, market_returns)
        upside_capture = upside_capture_ratio(returns, market_returns)

        return {
            'Fund': df_final['Fund'].unique()[0],
            'Category_Name': df_final['scheme_category'].unique()[0],
            'Scheme_code': df_final['scheme_code'].unique()[0],
            'Category': df_final['Category'].unique()[0],
            'Fund_house': df_final['fund_house'].unique()[0],
            'timeline': timeline,
            'CAGR': cagr,
            'sharpe_ratio': round(sharpe_ratio, 2),
            'sortino_ratio': round(sortino_ratio, 2),
            'std': round(stdev * 100, 2),
            'treynor_ratio': round(treynor_ratio * 100, 2),
            'beta_value': round(beta_value * 100, 2),
            'alpha': alpha,
            'r_squared': r_squared,
            'omega': omega,
            'calmar': calmar,
            'downside_capture': round(downside_capture * 100, 0),
            'upside_capture': round(upside_capture * 100, 0),
            'Maximum_Drawdown': max_dd * 100,
            'Peak_Date': peak_date,
            'Trough_Date': trough_date,
            'Recovery_Time': recovery_time_value,
            'Recovery_Date': recovery_date,
            'result_type': result_type
        }
