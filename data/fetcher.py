import yfinance as yf
import pandas_datareader.data as web
import pandas as pd
from typing import List, Optional
import datetime

from data.cache import load_from_cache, save_to_cache

def fetch_yfinance_data(tickers: List[str], start_date: str, end_date: str, interval: str = "1d", use_cache: bool = True) -> dict[str, pd.DataFrame]:
    """
    Fetches OHLCV data for a list of tickers from Yahoo Finance.
    Returns a dictionary mapping ticker -> DataFrame.
    Interval can be '1m', '5m', '15m', '1d', etc.
    """
    results = {}
    
    for ticker in tickers:
        df = None
        if use_cache:
            df = load_from_cache(f"{ticker}_{interval}", "ohlcv")
            
        if df is None or df.empty:
            print(f"Fetching {ticker} ({interval}) from Yahoo Finance...")
            try:
                # auto_adjust=True gets dividend/split adjusted prices
                ticker_obj = yf.Ticker(ticker)
                
                # Handling 1m interval requires period instead of start/end usually for yf, 
                # but start/end works if it's within the last 7 days.
                # If start_date/end_date are not specified properly for intraday, it might fail.
                df = ticker_obj.history(start=start_date, end=end_date, interval=interval, auto_adjust=True)
                
                if not df.empty:
                    df.index = pd.to_datetime(df.index).tz_localize(None) # Remove tz for consistency
                    if use_cache:
                        save_to_cache(f"{ticker}_{interval}", df, "ohlcv")
            except Exception as e:
                print(f"Error fetching {ticker}: {e}")
                
        if df is not None and not df.empty:
            # Slice to requested date range if cache returned a larger set
            df = df.loc[start_date:end_date]
            results[ticker] = df
            
    return results


def fetch_fred_macro(series_ids: List[str], start_date: str, end_date: str, use_cache: bool = True) -> pd.DataFrame:
    """
    Fetches macroeconomic series from FRED.
    Common IDs: 'VIXCLS' (VIX), 'FEDFUNDS' (Fed Funds Rate), 'CPIAUCSL' (CPI)
    Returns a combined DataFrame.
    """
    dfs = []
    
    for series in series_ids:
        df = None
        if use_cache:
            df = load_from_cache(series, "fred")
            
        if df is None or df.empty or str(df.index[0].date()) > start_date or str(df.index[-1].date()) < end_date:
            print(f"Fetching {series} from FRED...")
            try:
                # Convert start/end to datetime for pandas-datareader
                start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
                end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")
                
                df = web.DataReader(series, "fred", start_dt, end_dt)
                if not df.empty:
                    df.index = pd.to_datetime(df.index)
                    if use_cache:
                        save_to_cache(series, df, "fred")
            except Exception as e:
                print(f"Error fetching {series}: {e}")
                
        if df is not None and not df.empty:
            dfs.append(df)
            
    if dfs:
        # Outer join all macro series
        combined = pd.concat(dfs, axis=1)
        return combined.loc[start_date:end_date]
    
    return pd.DataFrame()
