import pytest
import pandas as pd
from data.cache import load_from_cache, save_to_cache
from data.preprocessor import align_and_clean_data
import os

def test_cache_save_and_load(tmp_path):
    # Override CACHE_DIR for tests
    import data.cache
    data.cache.CACHE_DIR = str(tmp_path)
    
    # Create sample data
    dates = pd.date_range('2023-01-01', periods=3)
    df = pd.DataFrame({'Close': [100, 101, 102]}, index=dates)
    
    # Save
    save_to_cache('TEST', df, 'ohlcv')
    
    # Load
    loaded_df = load_from_cache('TEST', 'ohlcv')
    
    assert loaded_df is not None
    assert len(loaded_df) == 3
    assert (loaded_df['Close'] == df['Close']).all()

def test_preprocessor():
    # Simulate some gaps and macro data
    dates = pd.date_range('2023-01-01', periods=5)
    ohlcv = pd.DataFrame({'Close': [10, None, 12, 13, 14]}, index=dates)
    
    # Initial NaN that should be dropped
    ohlcv.iloc[0] = pd.NA
    
    macro = pd.DataFrame({'VIX': [20, 21, 19, 18, 17]}, index=dates)
    
    ohlcv_data = {'AAPL': ohlcv}
    
    cleaned = align_and_clean_data(ohlcv_data, macro)
    df = cleaned['AAPL']
    
    # First row dropped
    assert len(df) == 4
    # Missing value ffilled
    assert df.loc['2023-01-03', 'Close'] == 12
    # Macro data merged
    assert 'VIX' in df.columns
    assert df.loc['2023-01-04', 'VIX'] == 18
