import pandas as pd
import plotly.graph_objects as go

def plot_equity_curve(portfolio_df: pd.DataFrame, benchmark_returns: pd.Series = None) -> go.Figure:
    """
    Creates an interactive Plotly chart of the equity curve and benchmark.
    """
    fig = go.Figure()
    
    # Portfolio
    fig.add_trace(go.Scatter(
        x=portfolio_df.index,
        y=portfolio_df['equity'],
        mode='lines',
        name='Strategy Equity',
        line=dict(color='blue')
    ))
    
    # Add benchmark if provided
    if benchmark_returns is not None and not benchmark_returns.empty:
        # Rebase benchmark to initial capital
        initial_capital = portfolio_df['equity'].iloc[0]
        cum_bmark = (1 + benchmark_returns).cumprod() * initial_capital
        
        fig.add_trace(go.Scatter(
            x=cum_bmark.index,
            y=cum_bmark,
            mode='lines',
            name='Benchmark',
            line=dict(color='gray', dash='dash')
        ))
        
    fig.update_layout(
        title='Portfolio Equity Curve',
        xaxis_title='Date',
        yaxis_title='Equity ($)',
        template='plotly_white'
    )
    
    return fig
