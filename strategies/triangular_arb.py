import pandas as pd
import datetime
from typing import List, Dict
from strategies.base import BaseStrategy
from engine.events import SignalEvent

class TriangularArbStrategy(BaseStrategy):
    """
    High-Frequency Triangular Arbitrage Strategy.
    Expects triplets of the form (Base/Quote1, Quote1/Quote2, Base/Quote2).
    E.g. ('EURUSD=X', 'USDJPY=X', 'EURJPY=X')
    
    Looks for discrepancies where Bid(Base/Quote2) > Ask(Base/Quote1) * Ask(Quote1/Quote2)
    or Bid(Base/Quote1) * Bid(Quote1/Quote2) > Ask(Base/Quote2).
    """
    def __init__(self, strategy_id: str, triplet: tuple, threshold_bps: float = 1.0):
        super().__init__(strategy_id)
        self.pair1, self.pair2, self.pair3 = triplet
        self.threshold_bps = threshold_bps
        
    def calculate_signals(self, market_data: Dict[str, pd.DataFrame], current_date: datetime.datetime) -> List[SignalEvent]:
        # Return empty list unless all 3 pairs have data at current tick
        if any(p not in market_data for p in (self.pair1, self.pair2, self.pair3)):
            return []
            
        df1 = market_data[self.pair1]
        df2 = market_data[self.pair2]
        df3 = market_data[self.pair3]
        
        if current_date not in df1.index or current_date not in df2.index or current_date not in df3.index:
            return []
            
        # Extract Bid/Ask
        try:
            bid1, ask1 = df1.loc[current_date, ['Bid', 'Ask']]
            bid2, ask2 = df2.loc[current_date, ['Bid', 'Ask']]
            bid3, ask3 = df3.loc[current_date, ['Bid', 'Ask']]
        except KeyError:
            # Fallback to Close if no Bid/Ask synthesized
            p1 = df1.loc[current_date, 'Close']
            p2 = df2.loc[current_date, 'Close']
            p3 = df3.loc[current_date, 'Close']
            bid1 = ask1 = p1
            bid2 = ask2 = p2
            bid3 = ask3 = p3
            
        signals = []
        
        # Scenario 1: Implied Cross Ask is cheaper than Direct Bid
        # Implied Cross Ask = Ask(EUR/USD) * Ask(USD/JPY)
        # Direct Bid = Bid(EUR/JPY)
        # Arb: Buy EUR/USD, Buy USD/JPY, Sell EUR/JPY
        implied_ask = ask1 * ask2
        if bid3 > implied_ask * (1 + self.threshold_bps / 10000.0):
            # We use 'BASKET' as a special signal strength to indicate these must execute together
            signals.append(SignalEvent(self.strategy_id, self.pair1, current_date, 'LONG', 1.0))
            signals.append(SignalEvent(self.strategy_id, self.pair2, current_date, 'LONG', 1.0))
            signals.append(SignalEvent(self.strategy_id, self.pair3, current_date, 'SHORT', 1.0))
            return signals # Return immediately, only 1 arb direction at a time
            
        # Scenario 2: Implied Cross Bid is richer than Direct Ask
        # Implied Cross Bid = Bid(EUR/USD) * Bid(USD/JPY)
        # Direct Ask = Ask(EUR/JPY)
        # Arb: Sell EUR/USD, Sell USD/JPY, Buy EUR/JPY
        implied_bid = bid1 * bid2
        if implied_bid > ask3 * (1 + self.threshold_bps / 10000.0):
            signals.append(SignalEvent(self.strategy_id, self.pair1, current_date, 'SHORT', 1.0))
            signals.append(SignalEvent(self.strategy_id, self.pair2, current_date, 'SHORT', 1.0))
            signals.append(SignalEvent(self.strategy_id, self.pair3, current_date, 'LONG', 1.0))
            
        return signals
