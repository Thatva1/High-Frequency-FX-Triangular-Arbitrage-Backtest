import pandas as pd
from typing import Dict, Optional

def align_and_clean_data(ohlcv_data: Dict[str, pd.DataFrame], macro_data: pd.DataFrame, spread_bps: float = 1.0) -> Dict[str, pd.DataFrame]:
    """
    Takes raw dictionaries of dataframes and cleans them.
    1. Forward-fill missing values (prices gap).
    2. Drops rows where the asset hasn't started trading.
    3. Merges macro data onto each asset's dataframe for strategy access.
    4. Synthesizes Bid and Ask columns from the Close price using spread_bps.
    """
    cleaned_data = {}
    
    for ticker, df in ohlcv_data.items():
        if df is None or df.empty:
            continue
            
        # 1. Forward-fill missing values for non-trading days/gaps
        # Actually, for OHLCV, we shouldn't create synthetic trading days for equities,
        # but we should forward-fill NaNs within existing index dates.
        df = df.ffill()
        
        # 2. Merge macro data
        if not macro_data.empty:
            # We want to use the latest available macro data on any given trading day
            # Reindex macro data to match the asset's trading calendar
            aligned_macro = macro_data.reindex(df.index, method='ffill')
            df = df.join(aligned_macro)
            
        # 3. Drop initial NaNs where the asset hadn't IPO'd
        df = df.dropna(subset=['Close'])
        
        # 4. Synthesize Bid/Ask
        # Example: if spread_bps is 1.0 (1 basis point), then half spread is 0.5 bps
        # Ask = Close * (1 + 0.5 bps)
        # Bid = Close * (1 - 0.5 bps)
        half_spread_pct = (spread_bps / 10000.0) / 2.0
        df['Ask'] = df['Close'] * (1 + half_spread_pct)
        df['Bid'] = df['Close'] * (1 - half_spread_pct)
        
        cleaned_data[ticker] = df
        
    return cleaned_data
