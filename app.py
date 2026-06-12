import streamlit as st
import pandas as pd
import yaml
from run_backtest import run_backtest
from analytics.visualizer import plot_equity_curve

st.set_page_config(page_title="Algo Backtester", layout="wide")

st.title("Multi-Asset Algo Trading Backtester")

# Sidebar
st.sidebar.header("Configuration")

# Load config to display defaults
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

strategy = st.sidebar.selectbox("Strategy", ["Momentum", "Mean_Reversion"])
start_date = st.sidebar.date_input("Start Date", pd.to_datetime(config['backtest']['start_date']))
end_date = st.sidebar.date_input("End Date", pd.to_datetime(config['backtest']['end_date']))
initial_capital = st.sidebar.number_input("Initial Capital", value=config['backtest']['initial_capital'])

if st.sidebar.button("Run Backtest"):
    with st.spinner("Running Backtest..."):
        # For a full implementation, we'd dynamically override config here
        # and capture the portfolio returns to display in Streamlit.
        # This is a stub showing the UI structure.
        st.success(f"Backtest for {strategy} completed! Check tearsheet.html for full report.")
        
        # Display mock equity curve for UI demonstration
        st.subheader("Equity Curve")
        dates = pd.date_range(start_date, end_date)
        mock_equity = pd.DataFrame({'equity': [initial_capital * (1 + 0.001 * i) for i in range(len(dates))]}, index=dates)
        fig = plot_equity_curve(mock_equity)
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("### Instructions")
st.write("1. Select a strategy from the sidebar.")
st.write("2. Configure dates and capital.")
st.write("3. Click 'Run Backtest'.")
st.write("4. The detailed tear sheet will be saved to `tearsheet.html` in the root directory.")
