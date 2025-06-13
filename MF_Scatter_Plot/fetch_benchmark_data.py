def benchmark_data():
    import pandas as pd
    import numpy as np
    from datetime import datetime
    from nsepython import index_history
    # output_filename = r"C:\Users\hanis\Downloads\MF_data_2024jan_now\all_funds_nav_data_hist.csv"

    symbol='^NSEI'
    # Fetch data for Nifty 50
    # nifty_50 = yf.download(symbol, start="1992-01-01", end="2025-02-02")
    today=datetime.today()

    nifty_data = index_history("NIFTY 50", "01-01-1992", today.strftime("%m-%d-%Y"))
    nifty_data['HistoricalDate']=pd.to_datetime(nifty_data['HistoricalDate'])

    nifty_data=nifty_data.reset_index()
    nifty_data['Date']=pd.to_datetime(nifty_data['HistoricalDate'].apply(lambda x:x.strftime("%d-%m-%Y")))
    nifty_data['scheme_category']='Benchmark Nifty 50'
    nifty_data['Fund']='Nifty 50'
    nifty_data['scheme_code']=100000
    nifty_data['scheme_type']='Benchmark'
    nifty_data['Category']='Benchmark'
    nifty_data['Sub_category']='Benchmark'
    nifty_data['Close']=nifty_data['CLOSE']
    nifty_df=nifty_data[['scheme_code','Fund','Date','Close','Category','Sub_category','scheme_category','scheme_type']]

    # Save all NAV data to a single CSV 
    print("Successfully fetched Nifty 50 data")
    # output_filename = r"C:\Users\hanis\source\repos\streamlit\streamlit\MF_Scatter_Plot\data\benchmark_data.csv"
    # nifty_df.to_csv(output_filename, index=False)
    return nifty_df