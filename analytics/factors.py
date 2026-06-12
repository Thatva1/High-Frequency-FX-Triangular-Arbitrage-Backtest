import pandas as pd
import statsmodels.api as sm

def fama_french_ols(strategy_returns: pd.Series, ff_factors: pd.DataFrame) -> dict:
    """
    Runs an OLS regression of the strategy returns against Fama-French factors.
    ff_factors should contain Mkt-RF, SMB, HML, RMW, CMA, and RF columns.
    Returns the alpha and betas.
    """
    if strategy_returns.empty or ff_factors.empty:
        return {}
        
    # Align dates
    aligned = pd.concat([strategy_returns, ff_factors], axis=1).dropna()
    if aligned.empty:
        return {}
        
    y = aligned.iloc[:, 0] - aligned['RF'] # Excess returns
    X = aligned[['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA']]
    X = sm.add_constant(X)
    
    model = sm.OLS(y, X).fit()
    
    results = {
        'Alpha (Annualized)': model.params['const'] * 252,
        'Market Beta': model.params['Mkt-RF'],
        'SMB Beta': model.params['SMB'],
        'HML Beta': model.params['HML'],
        'RMW Beta': model.params['RMW'],
        'CMA Beta': model.params['CMA'],
        'R-squared': model.rsquared
    }
    
    return {k: round(v, 4) for k, v in results.items()}
