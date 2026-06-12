import pandas as pd
import pandas_ta as ta
import datetime
from typing import List, Dict
from strategies.base import BaseStrategy
from engine.events import SignalEvent

class MeanReversionStrategy(BaseStrategy):
    """
    Mean Reversion strategy using Bollinger Band z-score.
    Long when price dips below lower band, Exit when it crosses SMA.
    Short when price spikes above upper band, Exit when it crosses SMA.
    """
    def __init__(self, strategy_id: str, length: int = 20, std_dev: float = 2.0):
        super().__init__(strategy_id)
        self.length = length
        self.std_dev = std_dev
        
    def calculate_signals(self, market_data: Dict[str, pd.DataFrame], current_date: datetime.datetime) -> List[SignalEvent]:
        signals = []
        
        for ticker, df in market_data.items():
            if current_date not in df.index:
                continue
                
            historical = df.loc[:current_date]
            if len(historical) < self.length:
                continue
                
            # Calculate Bollinger Bands using pandas-ta
            # pandas-ta returns BBL_20_2.0, BBM_20_2.0, BBU_20_2.0, BBB_20_2.0, BBP_20_2.0
            bbands = ta.bbands(historical['Close'], length=self.length, std=self.std_dev)
            
            if bbands is None or bbands.empty:
                continue
                
            lower_band_col = f"BBL_{self.length}_{self.std_dev}"
            upper_band_col = f"BBU_{self.length}_{self.std_dev}"
            sma_col = f"BBM_{self.length}_{self.std_dev}"
            
            current_price = historical['Close'].iloc[-1]
            lower_band = bbands[lower_band_col].iloc[-1]
            upper_band = bbands[upper_band_col].iloc[-1]
            sma = bbands[sma_col].iloc[-1]
            
            prev_price = historical['Close'].iloc[-2]
            prev_lower = bbands[lower_band_col].iloc[-2]
            prev_upper = bbands[upper_band_col].iloc[-2]
            
            # Entry logic
            if current_price < lower_band and prev_price >= prev_lower:
                signals.append(SignalEvent(self.strategy_id, ticker, current_date, 'LONG', 1.0))
            elif current_price > upper_band and prev_price <= prev_upper:
                signals.append(SignalEvent(self.strategy_id, ticker, current_date, 'SHORT', 1.0))
            
            # Exit logic (crossing SMA)
            # If we hold a long position, and price crosses above SMA, exit
            # If we hold a short position, and price crosses below SMA, exit
            # For simplicity in this method, we send an EXIT signal if price crosses SMA from either direction
            if (prev_price < sma and current_price >= sma) or (prev_price > sma and current_price <= sma):
                signals.append(SignalEvent(self.strategy_id, ticker, current_date, 'EXIT', 1.0))
                
        return signals
