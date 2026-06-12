# Multi-Asset Algo Trading Backtester

A robust, event-driven multi-asset trading backtester built from scratch. Features an independent data ingestion/caching layer, an abstract strategy generation layer, a custom event-driven execution engine, a portfolio sizing layer, and an interactive analytics suite powered by QuantStats and Streamlit.

## Architecture

1. **Data Layer**: Fetches OHLCV from `yfinance` and macro data from FRED via `pandas-datareader`. Uses `pyarrow` for fast parquet caching.
2. **Strategy Layer**: Implements `BaseStrategy` with subclasses for Momentum, Mean Reversion (Bollinger), Carry, Trend Following (EMA+Donchian), and Stat-Arb.
3. **Execution Engine**: Custom event-driven loop (`MarketEvent`, `SignalEvent`, `OrderEvent`, `FillEvent`) with realistic slippage and commission modeling.
4. **Portfolio Layer**: Tracks positions, cash, and PnL, integrating PyPortfolioOpt for sizing optimizations.
5. **Analytics**: Generates HTML tear sheets via QuantStats and interactive Streamlit dashboards.

## Setup

1. Create a virtual environment and install requirements:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Run tests:
```bash
PYTHONPATH=. pytest tests/
```

## Usage

### Run Backtest CLI
Execute a backtest using a specific strategy (e.g., `momentum` or `mean_reversion`):
```bash
PYTHONPATH=. python run_backtest.py --strategy momentum
```
This generates an interactive `tearsheet.html` in the root directory.

### Streamlit Dashboard
Launch the web UI:
```bash
PYTHONPATH=. streamlit run app.py
```
