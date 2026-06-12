import pandas as pd
import numpy as np

def equal_weight(signals: list, capital: float, current_prices: dict) -> dict:
    """
    Given a list of SignalEvents, allocates capital equally among all active signals.
    Returns a dict of target quantities {ticker: target_shares}
    """
    if not signals:
        return {}
        
    allocation_per_asset = capital / len(signals)
    target_positions = {}
    
    for sig in signals:
        if sig.ticker in current_prices:
            price = current_prices[sig.ticker]
            # Naive floor division for shares
            shares = int(allocation_per_asset / price)
            if sig.signal_type == 'SHORT':
                shares = -shares
            elif sig.signal_type == 'EXIT':
                shares = 0
                
            target_positions[sig.ticker] = shares
            
    return target_positions

def inverse_volatility_weight(signals: list, capital: float, current_prices: dict, market_data: dict, lookback=60) -> dict:
    """
    Allocates capital inversely proportional to trailing volatility.
    """
    if not signals:
        return {}
        
    vols = {}
    for sig in signals:
        if sig.ticker in market_data:
            df = market_data[sig.ticker]
            if len(df) > lookback:
                # Calculate daily return std dev
                vols[sig.ticker] = df['Close'].pct_change().tail(lookback).std()
                
    if not vols:
        return equal_weight(signals, capital, current_prices)
        
    inv_vols = {k: 1.0 / v for k, v in vols.items() if v > 0}
    total_inv_vol = sum(inv_vols.values())
    
    target_positions = {}
    for sig in signals:
        if sig.ticker in current_prices and sig.ticker in inv_vols:
            weight = inv_vols[sig.ticker] / total_inv_vol
            allocation = capital * weight
            price = current_prices[sig.ticker]
            
            shares = int(allocation / price)
            if sig.signal_type == 'SHORT':
                shares = -shares
            elif sig.signal_type == 'EXIT':
                shares = 0
                
            target_positions[sig.ticker] = shares
            
    return target_positions
