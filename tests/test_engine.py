import pytest
import datetime
from engine.events import OrderEvent, OrderType, FillEvent
from engine.portfolio import Portfolio
from engine.execution import ExecutionHandler

def test_portfolio_update_fill():
    port = Portfolio(initial_capital=100000.0)
    
    # Simulate buying 10 shares of AAPL at 150
    fill = FillEvent(
        timeindex=datetime.datetime(2023, 1, 1),
        ticker='AAPL',
        exchange='SIM',
        quantity=10,
        direction='BUY',
        fill_cost=150.0,
        commission=1.0,
        slippage=0.5
    )
    
    port.update_fill(fill)
    
    assert port.positions['AAPL'] == 10
    # Cash = 100000 - (10 * 150) - 1.0 - 0.5 = 100000 - 1500 - 1.5 = 98498.5
    assert port.current_cash == 98498.5
    
    # Simulate selling 5 shares at 200
    fill_sell = FillEvent(
        timeindex=datetime.datetime(2023, 1, 2),
        ticker='AAPL',
        exchange='SIM',
        quantity=5,
        direction='SELL',
        fill_cost=200.0,
        commission=1.0,
        slippage=0.5
    )
    
    port.update_fill(fill_sell)
    assert port.positions['AAPL'] == 5
    # Cash = 98498.5 + (5 * 200) - 1.5 = 98498.5 + 1000 - 1.5 = 99497.0
    assert port.current_cash == 99497.0

def test_execution_handler():
    handler = ExecutionHandler(commission_fixed=1.0, commission_pct=0.0, slippage_bps=0.0)
    
    order = OrderEvent(
        ticker='AAPL',
        order_type=OrderType.MARKET,
        quantity=10,
        direction='BUY'
    )
    
    current_date = datetime.datetime(2023, 1, 1)
    market_data_snap = {'AAPL': 150.0}
    
    fill = handler.execute_order(order, current_date, market_data_snap)
    
    assert fill is not None
    assert fill.ticker == 'AAPL'
    assert fill.quantity == 10
    assert fill.direction == 'BUY'
    assert fill.fill_cost == 150.0
    assert fill.commission == 1.0
