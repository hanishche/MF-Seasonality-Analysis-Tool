import requests
import pandas as pd
from tqdm import tqdm
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import time
from mftool import Mftool

# --- Step 1: Fetch and filter scheme master ---
url = "https://api.mfapi.in/mf"
response = requests.get(url)
response.raise_for_status()
data = response.json()
df = pd.DataFrame(data)

scheme_codes = df['schemeCode'].tolist()
today = datetime.today().date()
threshold_date = today - timedelta(days=5)

def check_active(i, retries=3):
    url = f"https://api.mfapi.in/mf/{i}/latest"
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            if data.get('data') and pd.to_datetime(data['data'][0]['date'], dayfirst=True).date() >= threshold_date:
                return i
        except Exception as e:
            if attempt == retries - 1:
                print(f"Failed for {i} after {retries} attempts: {e}")
            time.sleep(1)
    return None

# --- Step 2: Check for active funds in parallel (low concurrency) ---
active_list = []
inactive_list = []
with ThreadPoolExecutor(max_workers=6) as executor:
    results = list(tqdm(executor.map(check_active, scheme_codes), total=len(scheme_codes), desc="Checking active status"))
for i, code in enumerate(scheme_codes):
    if results[i]:
        active_list.append(results[i])
    else:
        inactive_list.append(code)

print(f"Active schemes found: {len(active_list)}")

# --- Step 3: Fetch NAV history for only active funds, in parallel (low concurrency) ---
def fetch_nav(i, retries=3):
    url = f"https://api.mfapi.in/mf/{i}"
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            nav_data = data.get('data', [])
            scheme_meta = df[df['schemeCode'] == i].iloc[0].to_dict()
            for entry in nav_data:
                for k, v in scheme_meta.items():
                    entry[k] = v
            return nav_data
        except Exception as e:
            if attempt == retries - 1:
                print(f"Failed to fetch NAV for {i} after {retries} attempts: {e}")
            time.sleep(1)
    return []

all_nav_data = []
with ThreadPoolExecutor(max_workers=6) as executor:
    nav_results = list(tqdm(executor.map(fetch_nav, active_list), total=len(active_list), desc="Fetching NAV history"))
    for nav_data in nav_results:
        all_nav_data.extend(nav_data)

# --- Step 4: Save to DataFrame and CSV ---
all_nav_df = pd.DataFrame(all_nav_data)
if not all_nav_df.empty and 'date' in all_nav_df.columns:
    all_nav_df['date'] = pd.to_datetime(all_nav_df['date'], format='%d-%m-%Y', errors='coerce')


mf = Mftool()

# Ensure columns exist
for col in ['fund_house', 'scheme_type', 'scheme_category', 'scheme_start_date', 'scheme_start_nav']:
    if col not in all_nav_df.columns:
        all_nav_df[col] = None

def fetch_and_update(i):
    try:
        details = mf.get_scheme_details(i)
        mask = all_nav_df['schemeCode'] == i
        all_nav_df.loc[mask, 'fund_house'] = details.get('fund_house')
        all_nav_df.loc[mask, 'scheme_type'] = details.get('scheme_type')
        all_nav_df.loc[mask, 'scheme_category'] = details.get('scheme_category')
        start_date = details.get('scheme_start_date', {}).get('date')
        start_nav = details.get('scheme_start_date', {}).get('nav')
        all_nav_df.loc[mask, 'scheme_start_date'] = start_date
        all_nav_df.loc[mask, 'scheme_start_nav'] = start_nav
    except Exception as e:
        print(f"Failed for {i}: {e}")

unique_codes = all_nav_df['schemeCode'].unique()
with ThreadPoolExecutor(max_workers=8) as executor:
    list(tqdm(executor.map(fetch_and_update, unique_codes), total=len(unique_codes), desc="Fetching scheme details"))


all_nav_df.to_csv(r'C:\Users\hanis\source\repos\streamlit\streamlit\MF_Scatter_Plot\data\API_active_funds_nav_history.csv', index=False)