from engine.events import OrderEvent

class RiskManager:
    """
    Applies constraints to OrderEvents before they are sent to the ExecutionHandler.
    e.g. Stop-losses, concentration limits, max positions.
    """
    def __init__(self, max_position_pct=0.20):
        self.max_position_pct = max_position_pct
        
    def filter_order(self, event: OrderEvent, portfolio) -> OrderEvent:
        """
        Validates an order against risk constraints.
        Returns the OrderEvent if passed, or None if rejected.
        Can also modify the order quantity to fit within limits.
        """
        # Simplistic Risk check: does the new order exceed max concentration?
        if event.direction == 'BUY':
            if event.ticker in portfolio.holdings:
                current_value = portfolio.holdings[event.ticker]
            else:
                current_value = 0.0
                
            # Assume fill price is roughly current MTM price (we don't know exactly yet)
            # Since this is a simple check, we use a naive approximation or skip if we don't have prices
            # For a proper check, we'd need the current price passed in.
            pass
            
        return event # Pass through for now
