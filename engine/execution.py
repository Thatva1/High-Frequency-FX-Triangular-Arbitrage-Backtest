import datetime
from engine.events import OrderEvent, FillEvent, BasketOrderEvent

class ExecutionHandler:
    """
    Simulates the execution of OrderEvents against a given set of market data.
    Generates FillEvents that are fed back into the event queue.
    """
    def __init__(self, commission_fixed=1.0, commission_pct=0.0005, slippage_bps=5.0):
        self.commission_fixed = commission_fixed
        self.commission_pct = commission_pct
        self.slippage_bps = slippage_bps
        
    def execute_order(self, event: OrderEvent, current_date: datetime.datetime, market_data_snap: dict) -> FillEvent:
        """
        Takes an OrderEvent and executes it, returning a FillEvent.
        Applies simplistic slippage and commission logic.
        """
        if event.ticker not in market_data_snap:
            print(f"Warning: Cannot execute {event.ticker}, no price data for {current_date}")
            return None
            
        # Use Bid/Ask if available, else fallback to Close
        if 'Ask' in market_data_snap and 'Bid' in market_data_snap:
            # We pay the Ask when we BUY, we receive the Bid when we SELL
            if event.direction == 'BUY':
                fill_price = market_data_snap[event.ticker]['Ask']
            else:
                fill_price = market_data_snap[event.ticker]['Bid']
        else:
            # Fallback for daily data / missing spread
            fill_price = market_data_snap[event.ticker]
            if isinstance(fill_price, pd.Series):
                fill_price = fill_price['Close']
        
        # Apply additional simulated slippage
        slippage_amount = fill_price * (self.slippage_bps / 10000.0)
        if event.direction == 'BUY':
            fill_price += slippage_amount
        else:
            fill_price -= slippage_amount
            
        # Calculate Commission
        notional_value = event.quantity * fill_price
        commission = self.commission_fixed + (notional_value * self.commission_pct)
        
        fill_event = FillEvent(
            timeindex=current_date,
            ticker=event.ticker,
            exchange="SIM",
            quantity=event.quantity,
            direction=event.direction,
            fill_cost=fill_price,
            commission=commission,
            slippage=slippage_amount * event.quantity
        )
        return fill_event
        
    def execute_basket(self, basket_event: BasketOrderEvent, current_date: datetime.datetime, market_data_snap: dict) -> list[FillEvent]:
        """
        Executes a basket of orders together.
        Implements strict 'Fill-or-Kill' logic: if any single order in the basket cannot be executed, 
        the entire basket is rejected and returns an empty list.
        """
        fills = []
        for order in basket_event.orders:
            # Pass only the specific asset's dictionary slice down to execute_order
            asset_snap = {order.ticker: market_data_snap.get(order.ticker, {})}
            
            fill = self.execute_order(order, current_date, asset_snap)
            if not fill:
                print(f"Basket execution failed on {order.ticker}. Rolling back.")
                return [] # Basket fails completely
            fills.append(fill)
            
        return fills
