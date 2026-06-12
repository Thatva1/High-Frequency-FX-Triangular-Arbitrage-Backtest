from abc import ABC, abstractmethod
import pandas as pd
import datetime
from typing import List, Dict
from engine.events import SignalEvent

class BaseStrategy(ABC):
    """
    Abstract interface for all strategies.
    Strategies process market data and generate SignalEvents.
    """
    def __init__(self, strategy_id: str):
        self.strategy_id = strategy_id
        
    @abstractmethod
    def calculate_signals(self, market_data: Dict[str, pd.DataFrame], current_date: datetime.datetime) -> List[SignalEvent]:
        """
        Receives a dictionary of OHLCV dataframes (with macro merged) up to current_date.
        Returns a list of SignalEvents.
        """
        pass
