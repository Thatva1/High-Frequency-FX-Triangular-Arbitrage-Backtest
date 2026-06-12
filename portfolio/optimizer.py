import pandas as pd
import numpy as np
from pypfopt import expected_returns, risk_models
from pypfopt.efficient_frontier import EfficientFrontier

def maximize_sharpe_ratio(prices_df: pd.DataFrame, current_prices: dict, capital: float) -> dict:
    """
    Uses PyPortfolioOpt to calculate the max Sharpe portfolio weights.
    prices_df: DataFrame of historical prices where columns are tickers.
    Returns target shares for each ticker.
    """
    if prices_df.empty or len(prices_df.columns) < 2:
        return {}
        
    mu = expected_returns.mean_historical_return(prices_df)
    S = risk_models.sample_cov(prices_df)
    
    ef = EfficientFrontier(mu, S)
    raw_weights = ef.max_sharpe()
    cleaned_weights = ef.clean_weights()
    
    target_positions = {}
    for ticker, weight in cleaned_weights.items():
        if ticker in current_prices:
            allocation = capital * weight
            price = current_prices[ticker]
            shares = int(allocation / price)
            target_positions[ticker] = shares
            
    return target_positions
