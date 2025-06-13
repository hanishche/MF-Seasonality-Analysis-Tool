from mftool import Mftool
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import pandas as pd

mf = Mftool()
scheme_codes = list(mf.get_scheme_codes().keys())[1:]

# Fetches all mutual fund scheme details in parallel using ThreadPoolExecutor and organizes them into a DataFrame.
# Extracts and cleans category information, flags IDCW (dividend) schemes, and filters for direct, open-ended equity and other schemes (excluding IDCW).
# For each filtered scheme, fetches historical NAV data in parallel, keeping only those with recent NAVs.
# Merges NAV data with scheme details, standardizes column names, and parses dates.
# Saves the final cleaned and merged DataFrame to a CSV file for further analysis.

def fetch_scheme_detail(scheme_code):
    details = mf.get_scheme_details(scheme_code)
    scheme_name = details.get('scheme_name', '').lower()
    plan_type = (
        "Growth" if "growth" in scheme_name else
        "Dividend Reinvestment" if "div reinvestment" in scheme_name or "dividend reinvestment" in scheme_name else
        "Dividend" if "dividend" in scheme_name else "Unknown"
    )
    plan_class = (
        "Direct" if "direct" in scheme_name else
        "Regular" if "regular" in scheme_name else "Unknown"
    )
    scheme_detail = {
        'scheme_code': scheme_code,
        'scheme_name': details.get('scheme_name'),
        'plan_type': plan_type,
        'plan_class': plan_class,
        'start_date': details.get('scheme_start_date', {}).get('date'),
        'start_nav': details.get('scheme_start_date', {}).get('nav'),
        **{k: v for k, v in details.items() if k not in ['scheme_start_date', 'scheme_name']}
    }
    return scheme_detail

max_workers = 16

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    scheme_details_list = list(tqdm(executor.map(fetch_scheme_detail, scheme_codes), total=len(scheme_codes), desc="Fetching scheme details"))

df = pd.DataFrame(scheme_details_list)
df[['Category', 'Sub_category']] = df['scheme_category'].str.extract(r'^\s*([^-\n]+?)\s*-\s*([^\n]+)\s*$')
df['Category'] = df['Category'].fillna(df['scheme_category'])
df['Sub_category'] = df['Sub_category'].fillna(df['scheme_category'])

# Vectorized IDCW detection
idcw_keywords = [
    'idcw', 'income distribution cum capital withdrawal', 'dividend payout', 'dividend reinvestment',
    'dividend option', 'payout option', 'div payout', 'payout & reinvestment', 'dividend', 'bonus', 'idwc'
]
idcw_pattern = '|'.join([kw.replace(" ", "") for kw in idcw_keywords])
df['IDCW'] = df['scheme_name'].fillna("").str.replace(" ", "").str.lower().str.contains(idcw_pattern).astype(int)

# Efficient filtering
mask = (
    (df['plan_class'] != 'Regular') &
    (df['scheme_type'] == 'Open Ended Schemes') &
    (df['Category'].isin(['Equity Scheme', 'Other Scheme'])) &
    (df['IDCW'] == 0)
)
final_df = df[mask].reset_index(drop=True)

today = datetime.today().date()
threshold_date = today - timedelta(days=5)

def fetch_nav(scheme_code):
    try:
        df_nav = mf.get_scheme_historical_nav(scheme_code, as_Dataframe=True)
        if df_nav is not None and not df_nav.empty:
            df_nav = df_nav.reset_index()
            latest_nav_date = pd.to_datetime(df_nav['date'].iloc[0], dayfirst=True).date()
            if latest_nav_date >= threshold_date:
                df_nav['scheme_code'] = scheme_code
                return df_nav
        return None
    except Exception as e:
        tqdm.write(f"Error fetching NAV for scheme code {scheme_code}: {e}")
        return None

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    nav_results = list(tqdm(executor.map(fetch_nav, final_df['scheme_code']), total=len(final_df), desc="Fetching NAV data"))

# Filter out None and concatenate
nav_dfs = [df_nav for df_nav in nav_results if df_nav is not None]
combined_nav_df = pd.concat(nav_dfs, ignore_index=True)

print(f"Combined NAV DataFrame shape: {combined_nav_df.shape}")

df_fetched = combined_nav_df.merge(final_df, on='scheme_code', how='inner')
df_fetched['date'] = pd.to_datetime(df_fetched['date'], dayfirst=True, errors='coerce')
df_fetched = df_fetched.rename(columns={'date': 'Date', 'nav': 'Close', 'scheme_name': 'Fund'})
df_fetched.to_csv(r'C:\Users\hanis\source\repos\streamlit\streamlit\MF_Scatter_Plot\data\active_funds_nav_history.csv', index=False)