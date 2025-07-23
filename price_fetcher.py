"""
Price fetching module for Portfolio Analyzer
Handles historical price data from financial APIs
"""

import pandas as pd
import yfinance as yf
from datetime import datetime
from typing import Dict, List, Tuple

class PriceFetcher:
    """Handles fetching historical price data from financial APIs"""
    
    def get_split_adjusted_prices(self, holdings_list: List[Tuple[str, str]], 
                                splits_dict: Dict[str, pd.DataFrame], 
                                start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Get split adjusted historical prices/NAVs through Yahoo Finance"""
        
        # Create symbol mapping
        yf_symbols = []
        symbol_map = {}
        
        for symbol, currency in holdings_list:
            yf_symbol = f"{symbol}.SI" if currency == 'SGD' else symbol
            yf_symbols.append(yf_symbol)
            symbol_map[yf_symbol] = symbol
        
        # Add currency rates
        yf_symbols.extend(['SGDUSD=X', 'INRUSD=X'])
        
        # Download prices
        try:
            prices = yf.download(yf_symbols, start=start_date, end=end_date, progress=False, auto_adjust=False)['Close']
            
            if len(yf_symbols) == 1:
                prices = prices.to_frame(yf_symbols[0])
                
        except Exception as e:
            print(f"Error downloading prices: {e}")
            return pd.DataFrame()
        
        # Create full date range
        full_dates = pd.date_range(start=start_date, end=end_date, freq='D')
        prices = prices.reindex(full_dates)
        
        # Apply manual split adjustments to prices (reverse chronological order)
        for yf_symbol, orig_symbol in symbol_map.items():
            if orig_symbol in splits_dict:
                splits_df = splits_dict[orig_symbol]
                
                for _, split_row in splits_df.sort_values('Split_Date', ascending=False).iterrows():
                    split_date = split_row['Split_Date']
                    split_ratio = split_row['Split_Ratio']
                    
                    # Adjust prices before split date
                    pre_split_mask = prices.index < split_date
                    if pre_split_mask.any() and yf_symbol in prices.columns:
                        prices.loc[pre_split_mask, yf_symbol] /= split_ratio
        
        # Forward fill missing values (weekends, holidays)
        prices = prices.replace(0, pd.NA)
        prices = prices.fillna(method='ffill').fillna(method='bfill')
        
        # Rename columns back to original symbols
        prices.rename(columns=symbol_map, inplace=True)
        
        return prices