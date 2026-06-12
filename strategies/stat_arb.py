import pandas as pd
import datetime
from typing import List, Dict
import statsmodels.tsa.stattools as ts
from strategies.base import BaseStrategy
from engine.events import SignalEvent

class StatArbStrategy(BaseStrategy):
    """
    Statistical Arbitrage using Cointegration.
    For simplicity, this skeleton will test pairs provided in a list.
    Real implementation uses Johansen test, here we'll use Engle-Granger (ts.coint) for a 2-asset pair.
    """
    def __init__(self, strategy_id: str, pairs: List[tuple], zscore_threshold=2.0, lookback=252):
        super().__init__(strategy_id)
        self.pairs = pairs # e.g. [('GOOGL', 'MSFT'), ('XOM', 'CVX')]
        self.zscore_threshold = zscore_threshold
        self.lookback = lookback
        
    def calculate_signals(self, market_data: Dict[str, pd.DataFrame], current_date: datetime.datetime) -> List[SignalEvent]:
        signals = []
        
        for asset1, asset2 in self.pairs:
            if asset1 not in market_data or asset2 not in market_data:
                continue
                
            df1 = market_data[asset1].loc[:current_date]
            df2 = market_data[asset2].loc[:current_date]
            
            if len(df1) < self.lookback or len(df2) < self.lookback:
                continue
                
            p1 = df1['Close'].iloc[-self.lookback:]
            p2 = df2['Close'].iloc[-self.lookback:]
            
            # Align them
            df_pair = pd.concat([p1, p2], axis=1).dropna()
            if len(df_pair) < self.lookback * 0.9:
                continue
                
            y = df_pair.iloc[:, 0]
            x = df_pair.iloc[:, 1]
            
            # Very simplistic z-score of the spread
            spread = y - x
            mean_spread = spread.mean()
            std_spread = spread.std()
            zscore = (spread.iloc[-1] - mean_spread) / std_spread
            
            # Signal Logic
            if zscore > self.zscore_threshold:
                # Spread is too high, short asset 1, long asset 2
                signals.append(SignalEvent(self.strategy_id, asset1, current_date, 'SHORT', 1.0))
                signals.append(SignalEvent(self.strategy_id, asset2, current_date, 'LONG', 1.0))
            elif zscore < -self.zscore_threshold:
                # Spread is too low, long asset 1, short asset 2
                signals.append(SignalEvent(self.strategy_id, asset1, current_date, 'LONG', 1.0))
                signals.append(SignalEvent(self.strategy_id, asset2, current_date, 'SHORT', 1.0))
            elif abs(zscore) < 0.5: # Mean reversion completed
                signals.append(SignalEvent(self.strategy_id, asset1, current_date, 'EXIT', 1.0))
                signals.append(SignalEvent(self.strategy_id, asset2, current_date, 'EXIT', 1.0))
                
        return signals
