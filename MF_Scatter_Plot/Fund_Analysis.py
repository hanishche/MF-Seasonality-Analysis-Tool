from calculate_risk_metrics import calculate_risk_metrics
from frequency import frequency

def Fund_Analysis(df_fund, Fund, Benchmark_fund, risk_free_rate=0.06, result_type='default'):
    import pandas as pd
    from dateutil.relativedelta import relativedelta
    import numpy as np

    df_fund = df_fund.copy()
    df_fund['Date'] = pd.to_datetime(df_fund['Date'], errors='coerce')
    if len(df_fund) <= 10:
        return None, None

    df_market = Benchmark_fund
    df_market['Date'] = pd.to_datetime(df_market['Date'], errors='coerce')

    if df_fund.empty or df_market.empty:        
        return None, None

    max_date = df_fund['Date'].max()
    if result_type == 'default':
        max_date = max_date if max_date == max_date + pd.offsets.MonthEnd(0) else max_date + pd.offsets.MonthEnd(-1)

    date_ranges = {
        '1W': (max_date - relativedelta(weeks=1), max_date),
        '3W': (max_date - relativedelta(weeks=3), max_date),
        '1M': (max_date - relativedelta(months=1), max_date),
        '3M': (max_date - relativedelta(months=3), max_date),
        '6M': (max_date - relativedelta(months=6), max_date),
        '1Y': (max_date - relativedelta(years=1), max_date),
        '2Y': (max_date - relativedelta(years=2), max_date),
        '3Y': (max_date - relativedelta(years=3), max_date),
        '5Y': (max_date - relativedelta(years=5), max_date),
        '7Y': (max_date - relativedelta(years=7), max_date),
        '10Y': (max_date - relativedelta(years=10), max_date),
        '15Y': (max_date - relativedelta(years=15), max_date),
        'All': None,
        '2025_TD': ('2025-01-01', max_date),
        '2024': ('2024-01-01', '2024-12-31'),
        '2023': ('2023-01-01', '2023-12-31'),
        '2022': ('2022-01-01', '2022-12-31'),
        '2021': ('2021-01-01', '2021-12-31'),
        '2020': ('2020-01-01', '2020-12-31'),
        '2019': ('2019-01-01', '2019-12-31'),
        '2018': ('2018-01-01', '2018-12-31'),
    }

    results = []
    for timeline, date_range in date_ranges.items():
        if isinstance(date_range, tuple):
            start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
            filtered_data = df_fund[(df_fund['Date'] >= start_date) & (df_fund['Date'] <= end_date)]
            filtered_market_data = df_market[(df_market['Date'] >= start_date) & (df_market['Date'] <= end_date)]
            duration_years = (end_date - start_date).days
            tenure = (filtered_data['Date'].max() - filtered_data['Date'].min()).days
            if (duration_years * 0.95 > tenure):
                continue
        else:
            filtered_data = df_fund
            filtered_market_data = df_market

        if filtered_data.empty or filtered_market_data.empty:
            continue

        if timeline in ['1W', '3W', '1M']:
            freq_str = 'daily'
        elif timeline in ['3M', '6M', '1Y', '2Y', '2025_TD', '2024', '2023', '2022', '2021', '2020', '2019', '2018']:
            freq_str = 'weekly'
        else:
            freq_str = 'monthly'

        df_frequency, df_market_frequency = frequency(filtered_data, filtered_market_data, freq_str)
        df_frequency['Return'] = df_frequency['Close'].pct_change()
        df_market_frequency['Market Return'] = df_market_frequency['Close'].pct_change()
        df_final = pd.merge(df_frequency, df_market_frequency[['Market Return', 'Date']], on='Date', how='inner').reset_index(drop=True)
        if df_final.empty:
            continue

        metrics = calculate_risk_metrics(df_final, timeline, risk_free_rate, freq_str, result_type)
        if metrics is not None:
            results.append(metrics)

    results_df = pd.DataFrame(results) if results else None
    return results_df, None

