"""
Stock split adjustment module for Portfolio Analyzer
Handles fetching and applying stock split adjustments
"""

import pandas as pd
import yfinance as yf
from typing import Dict, List, Tuple

class SplitAdjuster:
    """Handles stock split data fetching and adjustments"""
    
    def get_stock_splits(self, holdings_list: List[Tuple[str, str]]) -> Dict[str, pd.DataFrame]:
        """Get stock split details for all holdings"""
        all_splits = {}
        
        for symbol, currency in holdings_list:
            yf_symbol = f"{symbol}.SI" if currency == 'SGD' else symbol
            try:
                ticker = yf.Ticker(yf_symbol)
                splits = ticker.splits
                if not splits.empty:
                    # Convert to DataFrame for easier handling
                    split_df = splits.reset_index()
                    split_df.columns = ['Split_Date', 'Split_Ratio']
                    split_df['Split_Date'] = pd.to_datetime(split_df['Split_Date']).dt.tz_localize(None)
                    split_df = split_df.sort_values('Split_Date')
                    all_splits[symbol] = split_df
            except Exception:
                continue
        
        return all_splits
    
    def apply_split_adjustments(self, trades_df: pd.DataFrame, splits_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Apply split adjustments to trading data"""
        df = trades_df.copy()
        
        for symbol, splits_df in splits_dict.items():
            symbol_mask = df['Symbol'] == symbol
            symbol_trades = df[symbol_mask].copy()
            
            if symbol_trades.empty:
                continue
            
            # Apply splits iteratively based on split date
            for _, split_row in splits_df.iterrows():
                split_date = split_row['Split_Date']
                split_ratio = split_row['Split_Ratio']
                
                # Find trades before this split date
                pre_split_mask = (df['Symbol'] == symbol) & (df['Trade_Date'] < split_date)
                
                if pre_split_mask.any():
                    # If split is 1:2 (ratio = 2), quantity doubles, price halves
                    df.loc[pre_split_mask, 'Quantity'] *= split_ratio
                    df.loc[pre_split_mask, 'Trade_Price'] /= split_ratio
        
        # Recalculate adjusted cashflow
        df['Adjusted_Cashflow_Local'] = df['Quantity'] * df['Trade_Price'] * -1
        df['Comm_Fee'] = df['Comm/Fee'].fillna(0)
        df['Total_Cashflow_Local'] = df['Adjusted_Cashflow_Local'] - df['Comm_Fee']
        
        return df