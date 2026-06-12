import pytest
import pandas as pd
import datetime
from strategies.triangular_arb import TriangularArbStrategy
from engine.events import EventType

def test_triangular_arb_signals():
    strategy = TriangularArbStrategy("TRI_ARB", ("EURUSD=X", "USDJPY=X", "EURJPY=X"), threshold_bps=1.0)
    
    current_date = datetime.datetime(2024, 5, 15, 10, 0)
    
    # Scenario: No arbitrage
    market_data = {
        "EURUSD=X": pd.DataFrame({'Bid': [1.1000], 'Ask': [1.1001]}, index=[current_date]),
        "USDJPY=X": pd.DataFrame({'Bid': [150.00], 'Ask': [150.01]}, index=[current_date]),
        "EURJPY=X": pd.DataFrame({'Bid': [165.00], 'Ask': [165.015]}, index=[current_date])
    }
    
    # Implied Ask = 1.1001 * 150.01 = 165.026
    # Direct Bid = 165.00 (Bid is NOT > Implied Ask)
    
    # Implied Bid = 1.1000 * 150.00 = 165.00
    # Direct Ask = 165.015 (Implied Bid is NOT > Direct Ask)
    
    signals = strategy.calculate_signals(market_data, current_date)
    assert len(signals) == 0
    
    # Scenario: Arbitrage - Direct Ask is too cheap!
    market_data_arb = {
        "EURUSD=X": pd.DataFrame({'Bid': [1.1000], 'Ask': [1.1001]}, index=[current_date]),
        "USDJPY=X": pd.DataFrame({'Bid': [150.00], 'Ask': [150.01]}, index=[current_date]),
        "EURJPY=X": pd.DataFrame({'Bid': [164.00], 'Ask': [164.50]}, index=[current_date])
    }
    # Implied Bid = 165.00
    # Direct Ask = 164.50 (Implied Bid is > Direct Ask) -> Sell Implied (Sell EU, Sell UJ), Buy Direct (Buy EJ)
    
    signals = strategy.calculate_signals(market_data_arb, current_date)
    assert len(signals) == 3
    
    # Check directions
    assert signals[0].ticker == "EURUSD=X" and signals[0].signal_type == "SHORT"
    assert signals[1].ticker == "USDJPY=X" and signals[1].signal_type == "SHORT"
    assert signals[2].ticker == "EURJPY=X" and signals[2].signal_type == "LONG"
