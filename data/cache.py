import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

CACHE_DIR = ".cache"

def _get_file_path(ticker: str, data_type: str) -> str:
    """Returns the parquet file path for a ticker and data type."""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    return os.path.join(CACHE_DIR, f"{ticker}_{data_type}.parquet")

def load_from_cache(ticker: str, data_type: str = "ohlcv") -> pd.DataFrame:
    """
    Loads data from parquet cache.
    Returns None if cache does not exist.
    """
    path = _get_file_path(ticker, data_type)
    if os.path.exists(path):
        return pd.read_parquet(path)
    return None

def save_to_cache(ticker: str, df: pd.DataFrame, data_type: str = "ohlcv") -> None:
    """
    Saves dataframe to parquet cache.
    """
    if df is None or df.empty:
        return
        
    path = _get_file_path(ticker, data_type)
    # Convert index to column if it's named 'Date' or 'Datetime' 
    # to avoid warnings during parquet serialization, though pyarrow handles indexes well
    df.to_parquet(path, engine="pyarrow", compression="snappy")
