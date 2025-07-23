"""
Currency conversion module for Portfolio Analyzer
Handles multi-currency support and exchange rate conversion
"""

import pandas as pd
import yfinance as yf
from datetime import datetime
from typing import Dict

class CurrencyConverter:
    """Handles currency exchange rates and conversion"""
    
    def get_currency_rates(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Get historical daily currency rates (USD, INR, SGD)"""
        try:
            # Download currency rates
            currency_pairs = ['SGDUSD=X', 'INRUSD=X']  # USD is base
            
            rates = yf.download(currency_pairs, start=start_date, end=end_date, progress=False)['Close']
            
            # Handle single currency case
            if len(currency_pairs) == 1:
                rates = rates.to_frame(currency_pairs[0])
            
            # Create full date range and forward fill
            full_dates = pd.date_range(start=start_date, end=end_date, freq='D')
            rates = rates.reindex(full_dates)
            rates = rates.fillna(method='ffill').fillna(method='bfill')
            
            # Add USD rate (always 1)
            rates['USDUSD=X'] = 1.0
            
            return rates
            
        except Exception as e:
            print(f"Error downloading currency rates: {e}")
            return pd.DataFrame()
    
    def convert_to_usd(self, trades_df: pd.DataFrame, currency_rates: pd.DataFrame) -> pd.DataFrame:
        """Convert transaction prices to USD"""
        df = trades_df.copy()
        
        # Map currency rates to trade dates
        df['Trade_Date_Key'] = df['Trade_Date'].dt.floor('D')
        
        def get_usd_rate(row):
            date_key = row['Trade_Date_Key']
            currency = row['Currency']
            
            if currency == 'USD':
                return 1.0
            elif currency == 'SGD':
                return currency_rates.loc[date_key, 'SGDUSD=X'] if date_key in currency_rates.index else 0.74
            elif currency == 'INR':
                return currency_rates.loc[date_key, 'INRUSD=X'] if date_key in currency_rates.index else 0.012
            else:
                return 1.0  # Default to USD
        
        df['USD_Exchange_Rate'] = df.apply(get_usd_rate, axis=1)
        df['Trade_Price_USD'] = df['Trade_Price'] * df['USD_Exchange_Rate']
        df['Total_Cashflow_USD'] = df['Total_Cashflow_Local'] * df['USD_Exchange_Rate']
        
        return df