from dataclasses import dataclass
from enum import Enum
import datetime

class EventType(Enum):
    MARKET = 'MARKET'
    SIGNAL = 'SIGNAL'
    ORDER = 'ORDER'
    BASKET_ORDER = 'BASKET_ORDER'
    FILL = 'FILL'

class OrderType(Enum):
    MARKET = 'MARKET'
    LIMIT = 'LIMIT'
    STOP = 'STOP'
    TRAILING_STOP = 'TRAILING_STOP'

@dataclass
class Event:
    """Base Event Class"""
    pass

@dataclass
class MarketEvent(Event):
    """
    Handles the event of receiving a new market update with corresponding bars.
    """
    type: EventType = EventType.MARKET

@dataclass
class SignalEvent(Event):
    """
    Handles the event of sending a Signal from a Strategy object.
    """
    strategy_id: str
    ticker: str
    datetime: datetime.datetime
    signal_type: str # 'LONG', 'SHORT', 'EXIT'
    strength: float # 0.0 to 1.0 confidence
    type: EventType = EventType.SIGNAL

@dataclass
class OrderEvent(Event):
    """
    Handles the event of sending an Order to an execution system.
    """
    ticker: str
    order_type: OrderType
    quantity: int
    direction: str # 'BUY' or 'SELL'
    limit_price: float = None
    stop_price: float = None
    type: EventType = EventType.ORDER
    
    def print_order(self):
        print(f"Order: {self.direction} {self.quantity} {self.ticker} @ {self.order_type.value}")

@dataclass
class FillEvent(Event):
    """
    Encapsulates the notion of a Filled Order, as returned
    from a brokerage or execution engine.
    """
    timeindex: datetime.datetime
    ticker: str
    exchange: str
    quantity: int
    direction: str # 'BUY' or 'SELL'
    fill_cost: float
    commission: float = 0.0
    slippage: float = 0.0
    type: EventType = EventType.FILL

@dataclass
class BasketOrderEvent(Event):
    """
    Handles a basket of OrderEvents that must be executed together.
    Used for strategies like Triangular Arbitrage.
    """
    orders: list[OrderEvent]
    type: EventType = EventType.BASKET_ORDER
