import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Risk vs Returns Scatter Plot", layout="wide")  # <-- MUST BE FIRST
# Sidebar controls
st.sidebar.title("Filters")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv(r'C:\Users\hanis\source\repos\streamlit\streamlit\MF_Scatter_Plot\data\final_data.csv')
    return df

df_final = load_data()

# Info button for Result Type
with st.sidebar.expander("ℹ️ About Result Type", expanded=False):
    st.markdown(
        """
        **Result Type:**
        - **Till Date:** Considers data up to the latest available date in the dataset (e.g., today or most recent NAV).
        - **Default:** Considers data only up to the last completed month.
        """
    )


result_type = st.sidebar.selectbox(
    "Select Result Type",
    options=["Till_date", "default"],
    format_func=lambda x: "Till Date" if x == "Till_date" else "Default"
)

df_filtered_result = df_final[df_final['result_type'] == result_type]

categories = ['Portfolio', 'All'] + sorted(df_filtered_result['Category_Name'].unique())
selected_categories = st.sidebar.multiselect(
    "Select Category",
    options=categories,
    default=['Equity Scheme - Large Cap Fund']
)

# Funds for highlighting
selected_funds_list = [
    'JM Flexicap Fund (Direct) - Growth Option',
    'Motilal Oswal Midcap Fund-Direct Plan-Growth Option',
    'ICICI Prudential Pharma Healthcare and Diagnostics (P.H.D) Fund - Cumulative Option',
    'HDFC Focused 30 Fund - Growth Option - Direct Plan',
    'LIC MF Infrastructure Fund-Direct Plan-Growth',
    'Invesco India Smallcap Fund - Direct Plan - Growth',
    'Franklin India Opportunities Fund - Direct - Growth',
    'quant Small Cap Fund - Growth Option - Direct Plan',
    'Aditya Birla Sun Life PSU Equity Fund-Direct Plan-Growth',
    'Mirae Asset ELSS Tax Saver Fund - Direct Plan - Growth',
    'Parag Parikh Flexi Cap Fund - Direct Plan - Growth'
]

# Filter funds for dropdown based on selected categories
if "All" in selected_categories:
    fund_options = sorted(df_filtered_result["Fund"].unique())
elif "Portfolio" in selected_categories:
    fund_options = sorted(set(df_filtered_result[df_filtered_result["Category_Name"].isin(selected_categories)]["Fund"].unique()) | set(selected_funds_list))
else:
    fund_options = sorted(df_filtered_result[df_filtered_result["Category_Name"].isin(selected_categories)]["Fund"].unique())

highlight_funds = st.sidebar.multiselect(
    "Highlight Specific Funds (Yellow)",
    options=fund_options,
    default=[]
)

timelines = ['1W', '1M', '3M', '6M', '1Y', '2Y', '3Y', '5Y', '7Y', '10Y', '15Y', 'All', '2025_TD', '2024', '2023', '2022', '2021']
selected_timeline = st.sidebar.selectbox("Select Timeline", timelines, index=timelines.index("3Y"))

# Data filtering logic
df_filtered = df_filtered_result[df_filtered_result['timeline'] == selected_timeline]

if "All" in selected_categories:
    selected_categories = df_filtered['Category_Name'].unique().tolist() + ['Portfolio']
    highlight_funds = selected_funds_list
elif "Portfolio" in selected_categories and len(selected_categories) == 1:
    highlight_funds = selected_funds_list
    df_filtered = df_filtered[df_filtered["Fund"].isin(highlight_funds + ['Nifty 50'])]
elif "Portfolio" in selected_categories and len(selected_categories) > 1:
    highlight_funds = selected_funds_list
    df_filtered1 = df_filtered[df_filtered["Fund"].isin(highlight_funds + ['Nifty 50'])]
    df_filtered2 = df_filtered[df_filtered["Category_Name"].isin(selected_categories)]
    df_filtered = pd.concat([df_filtered1, df_filtered2], ignore_index=True)
else:
    df_filtered = df_filtered[df_filtered["Category_Name"].isin(selected_categories)]
    nifty_50_data = df_filtered_result[(df_filtered_result['timeline'] == selected_timeline) & (df_filtered_result['Fund'] == 'Nifty 50')]
    df_filtered = pd.concat([df_filtered, nifty_50_data], ignore_index=True)

returns_col = "CAGR"
risk_col = "std"

# Calculate averages
avg_returns = df_filtered[returns_col].mean()
avg_risk = df_filtered[risk_col].mean()

# Category-wise averages and top funds
if 'All' in selected_categories:
    df_filtered[f"{returns_col}_Category_Avg"] = avg_returns
    df_filtered[f"{risk_col}_Category_Avg"] = avg_risk
    df_top_funds = df_filtered[
        (df_filtered[risk_col] < avg_risk) &
        (df_filtered[returns_col] > avg_returns)
    ]
    df_top_funds["Risk_Adjusted_Score"] = df_top_funds[returns_col] / df_top_funds[risk_col]
    df_top_funds = df_top_funds.nlargest(3, "Risk_Adjusted_Score")
else:
    category_avg = df_filtered.groupby("Category_Name")[[returns_col, risk_col]].mean().reset_index()
    df_filtered = df_filtered.merge(category_avg, on="Category_Name", suffixes=("", "_Category_Avg"))
    df_top_funds = df_filtered[
        (df_filtered[risk_col] < df_filtered[f"{risk_col}_Category_Avg"]) &
        (df_filtered[returns_col] > df_filtered[f"{returns_col}_Category_Avg"])
    ]
    df_top_funds["Risk_Adjusted_Score"] = df_top_funds[returns_col] / df_top_funds[risk_col]
    df_top_funds = df_top_funds.nlargest(3, "Risk_Adjusted_Score")

# Highlighted, portfolio, and default funds
df_highlighted = df_filtered[df_filtered["Fund"].isin(highlight_funds)]
df_portfolio = df_filtered[df_filtered["Fund"].isin(selected_funds_list)]
df_highlighted_top_funds = df_highlighted[df_highlighted["Fund"].isin(df_top_funds["Fund"])]
df_portfolio_top_funds = df_portfolio[df_portfolio["Fund"].isin(df_top_funds["Fund"])]
df_default = df_filtered[~df_filtered["Fund"].isin(highlight_funds + selected_funds_list + df_top_funds["Fund"].tolist())]

# Scatter plot
fig = go.Figure()

# Default (Blue)
fig.add_trace(go.Scatter(
    x=df_default[risk_col], y=df_default[returns_col],
    mode="markers",
    marker=dict(size=10, color="blue", opacity=0.7, line=dict(width=1, color='white')),
    hovertext=df_default["Fund"],
    hovertemplate="<b>%{hovertext}</b><br>Returns: %{y:.2f}%<br>Risk: %{x:.3f}",
    name="Other Funds"
))

# Highlighted (Yellow)
fig.add_trace(go.Scatter(
    x=df_highlighted[risk_col], y=df_highlighted[returns_col],
    mode="markers",
    marker=dict(size=12, color="yellow", opacity=0.9, line=dict(width=2, color='black')),
    hovertext=df_highlighted["Fund"],
    hovertemplate="<b>%{hovertext}</b><br>Returns: %{y:.2f}%<br>Risk: %{x:.3f}",
    name="Selected Funds"
))

# Portfolio (White)
fig.add_trace(go.Scatter(
    x=df_portfolio[risk_col], y=df_portfolio[returns_col],
    mode="markers",
    marker=dict(size=12, color="white", opacity=0.9, line=dict(width=2, color='black')),
    hovertext=df_portfolio["Fund"],
    hovertemplate="<b>%{hovertext}</b><br>Returns: %{y:.2f}%<br>Risk: %{x:.3f}",
    name="Portfolio Funds"
))

# Top Funds (Purple)
fig.add_trace(go.Scatter(
    x=df_top_funds[risk_col], y=df_top_funds[returns_col],
    mode="markers",
    marker=dict(size=14, color="purple", opacity=0.9, line=dict(width=2, color='black')),
    hovertext=df_top_funds["Fund"],
    hovertemplate="<b>%{hovertext}</b><br>Returns: %{y:.2f}%<br>Risk: %{x:.3f}",
    name="Top Ranked Funds"
))

# Highlighted Top Funds (Orange Diamond)
fig.add_trace(go.Scatter(
    x=df_highlighted_top_funds[risk_col], y=df_highlighted_top_funds[returns_col],
    mode="markers",
    marker=dict(size=14, symbol='diamond', color="orange", opacity=0.9, line=dict(width=2, color='black')),
    hovertext=df_highlighted_top_funds["Fund"],
    hovertemplate="<b>%{hovertext}</b><br>Returns: %{y:.2f}%<br>Risk: %{x:.3f}",
    name="Selected & Top Fund"
))

# Portfolio Top Funds (Green Diamond)
fig.add_trace(go.Scatter(
    x=df_portfolio_top_funds[risk_col], y=df_portfolio_top_funds[returns_col],
    mode="markers",
    marker=dict(size=14, symbol='diamond', color="green", opacity=0.9, line=dict(width=2, color='black')),
    hovertext=df_portfolio_top_funds["Fund"],
    hovertemplate="<b>%{hovertext}</b><br>Returns: %{y:.2f}%<br>Risk: %{x:.3f}",
    name="Portfolio & Top Fund"
))

# Nifty 50 (Star)
nifty_50_data = df_filtered[df_filtered['Fund'] == 'Nifty 50']
fig.add_trace(go.Scatter(
    x=nifty_50_data[risk_col], y=nifty_50_data[returns_col],
    mode="markers",
    marker=dict(size=15, symbol='star', color="purple", opacity=1, line=dict(width=2, color='white')),
    hovertext=nifty_50_data["Fund"],
    hovertemplate="<b>%{hovertext}</b><br>Returns: %{y:.2f}%<br>Risk: %{x:.3f}",
    name='Nifty 50'
))

# Average point (Green Circle)
fig.add_trace(go.Scatter(
    x=[avg_risk], y=[avg_returns],
    mode="markers",
    marker=dict(size=14, color="green", opacity=1, line=dict(width=2, color='white')),
    hovertext=["Average"],
    hovertemplate="<b>Average</b><br>Returns: %{y:.2f}%<br>Risk: %{x:.3f}",
    name='Category Avg'
))

fig.update_layout(
    title=f"Risk vs Returns ({selected_timeline})",
    xaxis_title="Risk (STD)",
    yaxis_title="Returns (%)",
    template="plotly_dark",
    margin=dict(l=50, r=50, b=50, t=50),
    showlegend=True,
    height=650,
    width=1100
)

st.title("Risk vs Returns Scatter Plot")
st.plotly_chart(fig, use_container_width=True)

# Fund details table
st.subheader("Fund Details")
st.dataframe(df_filtered.reset_index(drop=True), use_container_width=True)