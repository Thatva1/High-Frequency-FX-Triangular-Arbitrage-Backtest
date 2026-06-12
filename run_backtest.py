import argparse
import yaml
import datetime
import pandas as pd
from data.fetcher import fetch_yfinance_data, fetch_fred_macro
from data.preprocessor import align_and_clean_data
from engine.portfolio import Portfolio
from engine.execution import ExecutionHandler
from engine.events import EventType, OrderEvent, OrderType, BasketOrderEvent
from strategies.momentum import MomentumStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.triangular_arb import TriangularArbStrategy
from portfolio.sizing import equal_weight
from analytics.tearsheet import generate_tearsheet
from analytics.visualizer import plot_equity_curve

def load_config(config_path="config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def run_backtest(strategy_name: str, config_path: str = "config.yaml"):
    config = load_config(config_path)
    
    start_date = config['backtest']['start_date']
    end_date = config['backtest']['end_date']
    initial_cap = config['backtest']['initial_capital']
    interval = config['backtest'].get('interval', '1d')
    spread_bps = config['execution'].get('spread_bps', 1.0)
    
    if strategy_name.lower() == 'triangular_arb':
        universe = config['universe'].get('triplet', [])
    else:
        equities = config['universe'].get('equities', [])
        etfs = config['universe'].get('etfs', [])
        fx = config['universe'].get('fx', [])
        universe = equities + etfs + fx
    
    print(f"Running {strategy_name} strategy from {start_date} to {end_date} on {len(universe)} assets with {interval} interval.")
    
    # 1. Fetch Data
    ohlcv_data = fetch_yfinance_data(universe, start_date, end_date, interval=interval)
    # Using SPY as a macro proxy if no FRED data
    macro_data = pd.DataFrame() 
    market_data = align_and_clean_data(ohlcv_data, macro_data, spread_bps=spread_bps)
    
    # Extract global dates
    all_dates = set()
    for df in market_data.values():
        all_dates.update(df.index)
    trading_days = sorted(list(all_dates))
    
    # 2. Initialize Engine Components
    portfolio = Portfolio(initial_capital=initial_cap)
    execution = ExecutionHandler(
        commission_fixed=config['execution']['commission_fixed'],
        commission_pct=config['execution']['commission_pct'],
        slippage_bps=config['execution']['slippage_bps']
    )
    
    # Pick Strategy
    if strategy_name.lower() == 'momentum':
        strategy = MomentumStrategy("MOM", lookback_months=12)
    elif strategy_name.lower() == 'mean_reversion':
        strategy = MeanReversionStrategy("MR", length=20, std_dev=2.0)
    elif strategy_name.lower() == 'triangular_arb':
        strategy = TriangularArbStrategy("TRI_ARB", tuple(universe), threshold_bps=1.0)
    else:
        print(f"Strategy {strategy_name} not implemented in CLI yet.")
        return
        
    print("Starting Event Loop...")
    
    # 3. Event Loop
    for current_date in trading_days:
        # Snapshot of prices for today
        current_prices = {}
        for ticker, df in market_data.items():
            if current_date in df.index:
                # Capture Bid/Ask and Close
                snap = {'Close': df.loc[current_date, 'Close']}
                if 'Ask' in df.columns and 'Bid' in df.columns:
                    snap['Ask'] = df.loc[current_date, 'Ask']
                    snap['Bid'] = df.loc[current_date, 'Bid']
                current_prices[ticker] = snap
        
        # Portfolio MTM Update - use Close price for valuation
        mtm_prices = {t: snap['Close'] for t, snap in current_prices.items()}
        portfolio.update_timeindex(current_date, mtm_prices)
        
        # Strategy Signal Generation
        signals = strategy.calculate_signals(market_data, current_date)
        
        if strategy_name.lower() == 'triangular_arb' and signals:
            # Triangular Arbitrage signals are a triplet that must execute as a basket
            # We hardcode a nominal order size for arb testing (e.g. 100,000 units)
            arb_orders = []
            for sig in signals:
                order = OrderEvent(sig.ticker, OrderType.MARKET, 100000, sig.signal_type)
                arb_orders.append(order)
                
            basket = BasketOrderEvent(orders=arb_orders)
            fills = execution.execute_basket(basket, current_date, current_prices)
            
            for fill in fills:
                portfolio.update_fill(fill)
        else:
            # Standard single-asset logic
            # Portfolio Sizing
            target_positions = equal_weight(signals, portfolio.total_equity, mtm_prices)
            
            # Generate Orders based on target vs current
            for ticker, target_shares in target_positions.items():
                current_shares = portfolio.positions.get(ticker, 0)
                diff = target_shares - current_shares
                
                if diff != 0:
                    direction = 'BUY' if diff > 0 else 'SELL'
                    order = OrderEvent(ticker, OrderType.MARKET, abs(diff), direction)
                    
                    # Execute order
                    fill = execution.execute_order(order, current_date, current_prices)
                    if fill:
                        portfolio.update_fill(fill)
                    
    print("Backtest Complete.")
    
    # 4. Analytics
    equity_curve = portfolio.generate_equity_curve()
    
    print("\n--- Summary ---")
    print(f"Final Equity: ${portfolio.total_equity:,.2f}")
    
    # Generate interactive HTML report
    # Only if we have variance, otherwise Quantstats will throw error
    if equity_curve['returns'].std() > 0:
        generate_tearsheet(equity_curve['returns'], title=f"{strategy_name.capitalize()} Tearsheet")
    else:
        print("No trades executed or flat returns, skipping tearsheet generation.")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Asset Algo Trading Backtester")
    parser.add_argument("--strategy", type=str, required=True, help="Strategy name (e.g., momentum, mean_reversion, triangular_arb)")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to config.yaml")
    args = parser.parse_args()
    
    run_backtest(args.strategy, args.config)
