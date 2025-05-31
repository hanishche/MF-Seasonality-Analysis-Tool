import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from mftool import Mftool
from matplotlib.backends.backend_pdf import PdfPages
import io

# --- Data and Helper Functions ---

@st.cache_data(show_spinner=False)
def get_scheme_codes():
    mf = Mftool()
    codes = mf.get_scheme_codes()
    # Remove the first entry (which is a header)
    codes = {int(k): v for k, v in codes.items() if k.isdigit()}
    df = pd.DataFrame(list(codes.items()), columns=["Scheme Code", "Scheme Name"])
    return df

def fetch_data(scheme_code):
    mf = Mftool()
    df = mf.get_scheme_historical_nav(scheme_code, as_Dataframe=True)
    df = df.reset_index()
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
    df['nav'] = df['nav'].astype(float)
    df = df.sort_values('date')
    df.set_index('date', inplace=True)
    monthly_nav = df['nav'].resample('M').last()
    monthly_returns = monthly_nav.pct_change().dropna() * 100
    monthly_returns_df = monthly_returns.to_frame(name='Monthly Return')
    monthly_returns_df.reset_index(inplace=True)
    return monthly_returns_df

def seasonality1(monthly_returns_df, Name, ax=None):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_returns_df['Year'] = monthly_returns_df['date'].dt.year
    monthly_returns_df['Month'] = monthly_returns_df['date'].dt.strftime('%b')
    monthly_returns_df['Month_num'] = monthly_returns_df['date'].dt.month
    pivot_df = monthly_returns_df.pivot(index='Year', columns='Month', values='Monthly Return')
    pivot_df = pivot_df[months]
    avg_row = pd.DataFrame(pivot_df.mean(numeric_only=True), columns=['Average Monthly Performance']).T
    pivot_df = pd.concat([avg_row, pivot_df], axis=0)
    pivot_df = pivot_df.reindex(pivot_df.index.tolist() + ['neg_count'])
    neg_counts = (pivot_df.iloc[1:] < 0).sum()
    pivot_df.loc['neg_count'] = neg_counts
    if ax is None:
        ax = plt.gca()
    sns.heatmap(
        pivot_df,
        annot=True,
        fmt='.2f',
        center=0,
        cmap="RdYlGn",
        linewidths=0.5,
        linecolor='gray',
        cbar=True,
        vmin=-20, vmax=20,
        ax=ax
    )
    ax.set_title(f'Seasonality Analysis: {Name}', fontsize=16)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

def seasonality2(monthly_returns_df, Name, ax=None):
    monthly_returns_df['Month'] = monthly_returns_df['date'].dt.strftime('%B')
    avg_monthly_returns = monthly_returns_df.groupby('Month')['Monthly Return'].mean()
    months_order = ['January', 'February', 'March', 'April', 'May', 'June',
                    'July', 'August', 'September', 'October', 'November', 'December']
    avg_monthly_returns = avg_monthly_returns.reindex(months_order)
    if ax is None:
        ax = plt.gca()
    sns.barplot(x=avg_monthly_returns.index, y=avg_monthly_returns.values, palette='viridis', ax=ax)
    ax.set_title(f'Avg Monthly Returns {Name}')
    ax.set_ylabel('Average Return (%)')
    ax.set_xlabel('Month')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

# --- Streamlit UI ---

st.title("Mutual Fund Seasonality Visualizer")

# 1. Scheme search and selection
scheme_df = get_scheme_codes()
scheme_names = scheme_df['Scheme Name'].tolist()
selected_names = st.multiselect(
    "Search and select one or more mutual fund schemes:",
    options=scheme_names,
    default=[]
)
selected_codes = scheme_df[scheme_df['Scheme Name'].isin(selected_names)]['Scheme Code'].tolist()

if selected_codes:
    # 2. Visualizations
    pdf_buffer = io.BytesIO()
    with PdfPages(pdf_buffer) as pdf:
        for code, name in zip(selected_codes, selected_names):
            st.subheader(f"Visualizations for: {name}")

            # --- Heatmap ---
            st.write("#### Seasonality Heatmap")
            fig1, ax1 = plt.subplots(figsize=(12, 6))
            try:
                df = fetch_data(code)
                seasonality1(df, name, ax=ax1)
                st.pyplot(fig1)
                pdf.savefig(fig1)
            except Exception as e:
                st.warning(f"Could not plot heatmap for {name}: {e}")
            plt.close(fig1)

            # --- Barplot ---
            st.write("#### Average Monthly Returns")
            fig2, ax2 = plt.subplots(figsize=(10, 5))
            try:
                seasonality2(df, name, ax=ax2)
                st.pyplot(fig2)
                pdf.savefig(fig2)
            except Exception as e:
                st.warning(f"Could not plot barplot for {name}: {e}")
            plt.close(fig2)

    pdf_buffer.seek(0)
    st.download_button(
        label="Download all charts as PDF",
        data=pdf_buffer,
        file_name="seasonality_charts.pdf",
        mime="application/pdf"
    )
else:
    st.info("Search and select one or more schemes above to see visualizations.")

st.markdown("---")
st.caption("Powered by mftool, pandas, seaborn, matplotlib, and Streamlit.")
