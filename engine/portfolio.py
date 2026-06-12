import pandas as pd
from engine.events import FillEvent, OrderEvent
import datetime

class Portfolio:
    """
    Tracks positions, cash, and PnL.
    Subscribes to FillEvents from the ExecutionHandler to update its state.
    """
    def __init__(self, initial_capital: float = 1000000.0):
        self.initial_capital = initial_capital
        self.current_cash = initial_capital
        
        # Position tracking: dict[ticker, int]
        self.positions = {}
        
        # Ledger for recording state over time
        # dict[datetime, dict]
        self.history = {}
        
        # Current holdings dict (symbol -> value)
        self.holdings = {}
        self.total_equity = initial_capital
        
    def update_timeindex(self, current_date: datetime.datetime, market_data_snap: dict):
        """
        Called on every MarketEvent to revalue the portfolio using the latest prices.
        """
        self.holdings = {k: 0.0 for k in self.positions.keys()}
        
        for ticker, pos in self.positions.items():
            # MTM: current price * position size
            if ticker in market_data_snap:
                price = market_data_snap[ticker]
                self.holdings[ticker] = pos * price
                
        self.total_equity = self.current_cash + sum(self.holdings.values())
        
        # Append to history
        state = {
            'cash': self.current_cash,
            'equity': self.total_equity,
            **self.holdings
        }
        self.history[current_date] = state

    def update_fill(self, event: FillEvent):
        """
        Updates the portfolio current positions and cash from a FillEvent.
        """
        if event.direction == 'BUY':
            fill_dir = 1
        else:
            fill_dir = -1
            
        # Update position
        if event.ticker not in self.positions:
            self.positions[event.ticker] = 0
            
        self.positions[event.ticker] += fill_dir * event.quantity
        
        # Update cash
        # Cost = Quantity * Fill Price
        fill_cost = event.quantity * event.fill_cost
        
        # Cash goes down when we buy, up when we sell
        self.current_cash -= (fill_dir * fill_cost)
        
        # Deduct commissions and slippage
        self.current_cash -= (event.commission + event.slippage)
        
    def generate_equity_curve(self) -> pd.DataFrame:
        """
        Returns a DataFrame of the portfolio history over time.
        """
        df = pd.DataFrame.from_dict(self.history, orient='index')
        df.index.name = 'Date'
        df['returns'] = df['equity'].pct_change()
        return df
