def frequency(filtered_data,filtered_market_data,frequency):
    
    if frequency == 'daily':
        df_frequency = filtered_data.set_index('Date').resample('D').last().reset_index()
        df_market_frequency = filtered_market_data.set_index('Date').resample('D').last().reset_index()

    elif frequency == 'weekly':
        df_frequency = filtered_data.set_index('Date').resample('W').last().reset_index()
        df_market_frequency = filtered_market_data.set_index('Date').resample('W').last().reset_index()

    elif frequency == 'monthly':
        df_frequency = filtered_data.set_index('Date').resample('M').last().reset_index()
        df_market_frequency = filtered_market_data.set_index('Date').resample('M').last().reset_index()
    else:
        raise ValueError("Frequency must be 'daily', 'weekly', or 'monthly'.")
    return df_frequency,df_market_frequency