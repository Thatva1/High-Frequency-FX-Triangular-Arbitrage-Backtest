import pandas as pd
import pandas_ta as ta
import datetime
from typing import List, Dict
from strategies.base import BaseStrategy
from engine.events import SignalEvent

class MomentumStrategy(BaseStrategy):
    """
    12-1 Cross-sectional Momentum + Time-Series Filter.
    Ranks the universe based on 12-month return (excluding most recent month).
    Buys top N assets if their 12-month return is > 0 (Time-Series filter).
    """
    def __init__(self, strategy_id: str, lookback_months=12, skip_months=1, top_n=3):
        super().__init__(strategy_id)
        self.lookback_months = lookback_months
        self.skip_months = skip_months
        self.top_n = top_n
        
    def calculate_signals(self, market_data: Dict[str, pd.DataFrame], current_date: datetime.datetime) -> List[SignalEvent]:
        signals = []
        scores = {}
        
        # Calculate momentum score for each asset
        for ticker, df in market_data.items():
            if current_date not in df.index:
                continue
                
            # We need at least 252 days of data roughly for a year
            if len(df.loc[:current_date]) < 252:
                continue
                
            historical = df.loc[:current_date]
            
            # Simple approximation of 12-1 momentum:
            # Return from 252 days ago to 21 days ago
            try:
                price_12m_ago = historical['Close'].iloc[-252]
                price_1m_ago = historical['Close'].iloc[-21]
                current_price = historical['Close'].iloc[-1]
                
                # Cross-sectional score: 11-month return
                mom_score = (price_1m_ago - price_12m_ago) / price_12m_ago
                
                # Time-series filter: Absolute 12-month return must be positive
                ts_mom = (current_price - price_12m_ago) / price_12m_ago
                
                if ts_mom > 0:
                    scores[ticker] = mom_score
            except IndexError:
                continue
                
        # Rank scores and generate LONG signals for top N
        if not scores:
            return signals
            
        ranked_tickers = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)
        top_tickers = ranked_tickers[:self.top_n]
        
        for ticker in top_tickers:
            signals.append(SignalEvent(
                strategy_id=self.strategy_id,
                ticker=ticker,
                datetime=current_date,
                signal_type='LONG',
                strength=1.0 # Simple equal conviction for top N
            ))
            
        # Optional: Generate EXIT signals for things no longer in top N?
        # That logic is usually handled by the Portfolio/Rebalance engine combining signals
        
        return signals
