# High-Frequency FX Triangular Arbitrage Backtester

A robust, event-driven backtesting engine tailored specifically for High-Frequency Trading (HFT) and FX Triangular Arbitrage. 

This engine is capable of ingesting minute/tick-level data, synthesizing order book spreads (Bid/Ask), and processing simultaneous "Fill-or-Kill" basket orders to accurately simulate high-frequency arbitrage strategies.

## Features

- **Event-Driven Architecture**: Fully modular components responding to `MarketEvent`, `SignalEvent`, `OrderEvent`, `BasketOrderEvent`, and `FillEvent`.
- **HFT Data Pipeline**: Ingests intraday 1-minute data and synthesizes Bid/Ask spreads directly onto the dataframes for accurate cross-rate arbitrage calculations.
- **Strict "Fill-or-Kill" Basket Execution**: If one leg of an arbitrage trade fails to fill due to simulated slippage or missing data, the entire basket is rejected to prevent unhedged directional exposure.
- **Triangular Arbitrage Logic**: Evaluates triplet FX pairs (e.g., `EUR/USD`, `USD/JPY`, `EUR/JPY`) in real-time. Identifies when the implied synthetic cross rate diverges from the direct quote beyond a user-defined threshold, locking in risk-free profit (accounting for spreads and commissions).
- **Analytics & Visualization**: Generates interactive HTML tearsheets via `QuantStats` and features a full Streamlit dashboard for parameter tweaking and visual inspection of PnL.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Thatva1/High-Frequency-FX-Triangular-Arbitrage-Backtest.git
cd "High-Frequency FX Triangular Arbitrage Backtest"
```

2. Create a virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Run the unit tests to verify the engine:
```bash
PYTHONPATH=. python3 -m pytest tests/
```

## Usage

### 1. Configure the Triplet
Modify `config.yaml` to specify the FX triplet you wish to trade, along with the date range, initial capital, and simulated execution costs (commissions & slippage).

```yaml
backtest:
  start_date: "2024-05-15"
  end_date: "2024-05-20"
  interval: "1m"

universe:
  triplet:
    - EURUSD=X
    - USDJPY=X
    - EURJPY=X
```

### 2. Run the CLI Backtester
Execute the backtest specifically using the `triangular_arb` strategy via the command line:

```bash
PYTHONPATH=. python run_backtest.py --strategy triangular_arb
```
This will run the event loop and output an interactive `tearsheet.html` containing performance metrics.

### 3. Launch the Interactive Dashboard
If you prefer a UI to review the equity curve and drawdowns:

```bash
PYTHONPATH=. streamlit run app.py
```
This will launch a local Streamlit web application.

## Project Structure
- `data/`: Ingestion (`yfinance`) and preprocessing layer (synthesizing Bid/Ask).
- `engine/`: The core event loop, including `events.py`, `portfolio.py`, and `execution.py` (which handles the Fill-or-Kill basket logic).
- `strategies/`: Houses the quantitative logic, primarily `triangular_arb.py`.
- `analytics/`: Tear sheet generation and Streamlit plotting modules.
- `tests/`: Unit tests utilizing `pytest`.
