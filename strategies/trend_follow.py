import pandas as pd
import pandas_ta as ta
import datetime
from typing import List, Dict
from strategies.base import BaseStrategy
from engine.events import SignalEvent

class TrendFollowingStrategy(BaseStrategy):
    """
    Trend Following using Dual EMA Crossover + Donchian Channel filter.
    Goes LONG when fast EMA > slow EMA and price is near the upper Donchian Channel.
    """
    def __init__(self, strategy_id: str, fast_ema=50, slow_ema=200, donchian_len=20):
        super().__init__(strategy_id)
        self.fast_ema = fast_ema
        self.slow_ema = slow_ema
        self.donchian_len = donchian_len
        
    def calculate_signals(self, market_data: Dict[str, pd.DataFrame], current_date: datetime.datetime) -> List[SignalEvent]:
        signals = []
        
        for ticker, df in market_data.items():
            if current_date not in df.index:
                continue
                
            historical = df.loc[:current_date]
            if len(historical) < self.slow_ema:
                continue
                
            # Calculate EMAs
            fast = ta.ema(historical['Close'], length=self.fast_ema)
            slow = ta.ema(historical['Close'], length=self.slow_ema)
            
            # Calculate Donchian Channel
            # pandas-ta returns DCL_20_20, DCM_20_20, DCU_20_20
            donchian = ta.donchian(high=historical['High'], low=historical['Low'], lower_length=self.donchian_len, upper_length=self.donchian_len)
            
            if fast is None or slow is None or donchian is None:
                continue
                
            curr_fast = fast.iloc[-1]
            curr_slow = slow.iloc[-1]
            prev_fast = fast.iloc[-2]
            prev_slow = slow.iloc[-2]
            
            curr_price = historical['Close'].iloc[-1]
            dcu_col = f"DCU_{self.donchian_len}_{self.donchian_len}"
            dcl_col = f"DCL_{self.donchian_len}_{self.donchian_len}"
            
            upper_channel = donchian[dcu_col].iloc[-1]
            lower_channel = donchian[dcl_col].iloc[-1]
            
            # Trend condition: Fast crosses Slow
            if curr_fast > curr_slow and prev_fast <= prev_slow:
                # Donchian Filter: Price must be in the upper half of the channel
                mid_channel = (upper_channel + lower_channel) / 2
                if curr_price > mid_channel:
                    signals.append(SignalEvent(self.strategy_id, ticker, current_date, 'LONG', 1.0))
                    
            elif curr_fast < curr_slow and prev_fast >= prev_slow:
                # Short or exit condition
                mid_channel = (upper_channel + lower_channel) / 2
                if curr_price < mid_channel:
                    signals.append(SignalEvent(self.strategy_id, ticker, current_date, 'SHORT', 1.0))
                    
        return signals
