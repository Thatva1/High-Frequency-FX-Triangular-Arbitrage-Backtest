import pandas as pd
import datetime
from typing import List, Dict
from strategies.base import BaseStrategy
from engine.events import SignalEvent

class CarryStrategy(BaseStrategy):
    """
    FX Carry Strategy based on Interest Rate Differential.
    For simplicity in this implementation:
    Go long FX pairs where the domestic rate > US Fed Funds rate.
    Short FX pairs where domestic rate < US Fed Funds rate.
    Requires macro data like 'FEDFUNDS' and corresponding foreign rates in the merged dataframe.
    """
    def __init__(self, strategy_id: str, domestic_rate_col='FEDFUNDS'):
        super().__init__(strategy_id)
        self.domestic_rate_col = domestic_rate_col
        
    def calculate_signals(self, market_data: Dict[str, pd.DataFrame], current_date: datetime.datetime) -> List[SignalEvent]:
        signals = []
        
        # In a full implementation, we'd map each FX pair to its corresponding foreign interest rate column
        # For this skeleton, if we detect FX pairs, we can do a simplistic carry proxy
        # based on rolling yield or predefined columns if available.
        
        for ticker, df in market_data.items():
            if current_date not in df.index:
                continue
                
            historical = df.loc[:current_date]
            if len(historical) < 2:
                continue
                
            if self.domestic_rate_col not in historical.columns:
                continue
                
            # If we don't have the explicit foreign rate, a naive proxy for carry is looking at 
            # the rolling yield or forward premium. Here we just show the structure of the signal.
            # E.g. we might have 'EUR_RATE' or 'JPY_RATE' merged from FRED.
            # Assuming we map TICKER -> RATE_COL
            rate_map = {
                'EURUSD=X': 'ECB_RATE',
                'USDJPY=X': 'BOJ_RATE',
                'GBPUSD=X': 'BOE_RATE'
            }
            
            foreign_rate_col = rate_map.get(ticker)
            
            if foreign_rate_col and foreign_rate_col in historical.columns:
                dom_rate = historical[self.domestic_rate_col].iloc[-1]
                for_rate = historical[foreign_rate_col].iloc[-1]
                
                # Base currency is first in pair (e.g. EUR in EURUSD)
                # If EUR rate > USD rate, go LONG EURUSD
                # Note: USDJPY has USD as base, so if USD rate > JPY rate, go LONG USDJPY
                is_usd_base = ticker.startswith("USD")
                
                if is_usd_base:
                    differential = dom_rate - for_rate
                else:
                    differential = for_rate - dom_rate
                    
                if differential > 0.0:
                    signals.append(SignalEvent(self.strategy_id, ticker, current_date, 'LONG', abs(differential)))
                elif differential < 0.0:
                    signals.append(SignalEvent(self.strategy_id, ticker, current_date, 'SHORT', abs(differential)))
                    
        return signals
