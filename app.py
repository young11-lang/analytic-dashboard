import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Performance Analytics Hub", layout="wide")

st.title("📊 High-Performance Analytics Dashboard")
st.write("Real-time performance tracking and advanced analytics engine.")

# 2. Sidebar Controls & File Uploader
st.sidebar.header("Filter & Controls")
uploaded_file = st.sidebar.file_uploader("Upload Custom CSV Data", type=["csv"])

starting_balance = st.sidebar.number_input("Starting Capital ($)", value=1000, step=100)
risk_per_trade = st.sidebar.slider("Risk Per Trade (%)", min_value=0.5, max_value=5.0, value=1.0, step=0.5)

# 3. Data Loading Logic (Custom File or Fallback Mock Data)
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("Custom dataset loaded successfully!")
else:
    # Fallback Mock Analytics Data
    np.random.seed(42)
    days = 30
    dates = pd.date_range(end=pd.Timestamp.today(), periods=days)
    daily_returns = np.random.normal(loc=15, scale=40, size=days)
    cumulative_profit = np.cumsum(daily_returns) + starting_balance

    df = pd.DataFrame({
        "Date": dates,
        "Daily PnL ($)": daily_returns,
        "Account Equity ($)": cumulative_profit
    })

# Ensure Account Equity calculates automatically if only PnL is provided
if "Account Equity ($)" not in df.columns and "Daily PnL ($)" in df.columns:
    df["Account Equity ($)"] = starting_balance + df["Daily PnL ($)"].cumsum()

# 4. Advanced Metrics Calculations
df["Cumulative Max"] = df["Account Equity ($)"].cummax()
df["Drawdown ($)"] = df["Account Equity ($)"] - df["Cumulative Max"]
df["Drawdown (%)"] = (df["Drawdown ($)"] / df["Cumulative Max"]) * 100

max_drawdown = df["Drawdown (%)"].min()
gross_profits = df.loc[df["Daily PnL ($)"] > 0, "Daily PnL ($)"].sum()
gross_losses = abs(df.loc[df["Daily PnL ($)"] < 0, "Daily PnL ($)"].sum())
profit_factor = (gross_profits / gross_losses) if gross_losses != 0 else np.nan

# 5. Dashboard Tabs Layout
tab1, tab2 = st.tabs(["📈 Overview & Charts", "⚙️ Advanced Risk & Performance"])

with tab1:
    # Top KPI Cards Layout
    col1, col2, col3, col4 = st.columns(4)

    total_profit = df["Daily PnL ($)"].sum()
    win_rate = (df["Daily PnL ($)"] > 0).mean() * 100
    final_balance = df["Account Equity ($)"].iloc[-1]
    risk_amount = final_balance * (risk_per_trade / 100)

    col1.metric("Current Equity", f"${final_balance:,.2f}")
    col2.metric("Total Net PnL", f"${total_profit:,.2f}", delta=f"{((total_profit/starting_balance)*100):.1f}%")
    col3.metric("Win Rate", f"{win_rate:.1f}%")
    col4.metric(f"Risk Per Position ({risk_per_trade}%)", f"${risk_amount:,.2f}")

    st.markdown("---")

    # Interactive Equity Growth Chart
    st.subheader("📈 Performance Trajectory")
    fig = px.line(
        df, 
        x="Date", 
        y="Account Equity ($)", 
        title="Cumulative Equity Curve",
        line_shape="spline"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Detailed Data Log Table
    st.subheader("📋 Session Performance Log")
    st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)

with tab2:
    st.subheader("Deep-Dive Risk Metrics")
    
    adv_col1, adv_col2, adv_col3 = st.columns(3)
    adv_col1.metric("Max Drawdown (%)", f"{max_drawdown:.2f}%")
    adv_col2.metric("Profit Factor", f"{profit_factor:.2f}" if not np.isnan(profit_factor) else "N/A")
    adv_col3.metric("Gross Win / Loss Ratio", f"${gross_profits:,.2f} / ${gross_losses:,.2f}")

    st.markdown("---")
    
    st.subheader("📉 Drawdown Over Time")
    fig_dd = px.area(
        df, 
        x="Date", 
        y="Drawdown (%)", 
        title="Underwater Equity Drawdown Chart",
        color_discrete_sequence=["red"]
    )
    st.plotly_chart(fig_dd, use_container_width=True)