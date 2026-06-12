import pandas as pd
import quantstats as qs
import numpy as np

def calculate_basic_metrics(returns: pd.Series) -> dict:
    """
    Calculates core performance metrics from a daily return series.
    """
    if returns.empty:
        return {}
        
    metrics = {
        'CAGR': qs.stats.cagr(returns),
        'Sharpe': qs.stats.sharpe(returns),
        'Sortino': qs.stats.sortino(returns),
        'Max Drawdown': qs.stats.max_drawdown(returns),
        'Calmar': qs.stats.calmar(returns),
        'Omega': qs.stats.omega(returns),
        'Volatility': qs.stats.volatility(returns)
    }
    
    return {k: round(v, 4) for k, v in metrics.items() if v is not None}
