import warnings
from pandas.errors import SettingWithCopyWarning
from concurrent.futures import ProcessPoolExecutor, as_completed
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import pandas as pd
from Fund_Analysis import Fund_Analysis
# from fetch_benchmark_data import benchmark_data
# from fetch_data import fetch_active_funds_nav_history


warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.simplefilter(action='ignore', category=SettingWithCopyWarning)


# df_funds=fetch_active_funds_nav_history()
# df_benchmark=benchmark_data()
# df_funds=pd.read_csv(r"C:\Users\hanis\source\repos\streamlit\streamlit\MF_Scatter_Plot\data\active_funds_nav_history.csv")
# df_benchmark=pd.read_csv(r"C:\Users\hanis\source\repos\streamlit\streamlit\MF_Scatter_Plot\data\benchmark_data.csv")
# print("Successfully fetched data")
# df_funds['Date']=pd.to_datetime(df_funds['Date'], dayfirst=True, errors='coerce')

# df_benchmark['fund_house']='Benchmark Nifty 50'
# df_benchmark['Date']=pd.to_datetime(df_benchmark['Date'], dayfirst=True, errors='coerce')

# df=pd.concat([df_funds,df_benchmark]).reset_index(drop=True)
# df['Close']=df['Close'].astype(float)
# print("Successfully concatenated data & exproting to CSV")
# df.to_csv(r'C:\Users\hanis\source\repos\streamlit\streamlit\MF_Scatter_Plot\data\final.csv', index=False)

# df=pd.read_csv(r'C:\Users\hanis\source\repos\streamlit\streamlit\MF_Scatter_Plot\data\final.csv')


# Fund_list=df['Fund'].unique()
# final_data=pd.DataFrame()
# df_final=pd.DataFrame()
# benchmark_data=df[df['Fund']=='Nifty 50']
# # Fund_list=['Nippon India BSE Sensex Next 30 Index Fund- Direct Plan- Growth Option']
# # # Fund_list=['Motilal Oswal Midcap Fund-Direct Plan-Growth Option']
# # # Fund_list='ICICI Prudential Bluechip Fund - Direct Plan - Growth'

# # # Fund_list=["Nippon India Credit Risk Fund - Segregated Portfolio 2 - Institutional Growth Plan"]        

# for i in ['default','Till_date']:
#     final_data = pd.DataFrame() 
#     for Fund in tqdm(Fund_list,position=0):        
#         tqdm.write(f"Processing: {Fund}")
#         final_data1,final_raw=Fund_Analysis(df[df['Fund']==Fund],Fund,benchmark_data,0.06,i)
#         final_data=pd.concat([final_data,final_data1])        
#     df_final=pd.concat([df_final,final_data])

# df_final=df_final.reset_index(drop=True)
# df_final.to_csv(r'C:\Users\hanis\source\repos\streamlit\streamlit\MF_Scatter_Plot\data\final_data.csv', index=False)
# print(df_final)


# Load the data
df = pd.read_csv(r'C:\Users\hanis\source\repos\streamlit\streamlit\MF_Scatter_Plot\data\final.csv')
# Get unique funds
Fund_list = df['Fund'].unique()
benchmark_data = df[df['Fund'] == 'Nifty 50']
# Function to process each fund
def process_fund(Fund, benchmark_data, i):
    final_data1, final_raw = Fund_Analysis(df[df['Fund'] == Fund], Fund, benchmark_data, 0.06, i)
    return final_data1
# Initialize final DataFrame
df_final = pd.DataFrame()
# Use ThreadPoolExecutor for parallel processing
for i in ['default', 'Till_date']:
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_fund, Fund, benchmark_data, i): Fund for Fund in Fund_list}
        
        # Use tqdm to create a progress bar
        with tqdm(total=len(futures), position=0, desc="Processing Funds") as pbar:
            for future in as_completed(futures):
                final_data1 = future.result()
                df_final = pd.concat([df_final, final_data1])
                pbar.update(1)  # Update the progress bar for each completed future
# Reset index and save to CSV
df_final = df_final.reset_index(drop=True)
df_final.to_csv(r'C:\Users\hanis\source\repos\streamlit\streamlit\MF_Scatter_Plot\data\final_data.csv', index=False)
print(df_final)