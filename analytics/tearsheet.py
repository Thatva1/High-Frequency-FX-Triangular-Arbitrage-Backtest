import pandas as pd
import quantstats as qs

def generate_tearsheet(returns: pd.Series, benchmark: pd.Series = None, title="Strategy Tearsheet", output_path="tearsheet.html"):
    """
    Generates a full interactive HTML tearsheet using QuantStats.
    """
    if returns.empty:
        print("Empty returns series, skipping tearsheet.")
        return
        
    qs.reports.html(returns, benchmark=benchmark, title=title, output=output_path)
    print(f"Tearsheet generated at {output_path}")
