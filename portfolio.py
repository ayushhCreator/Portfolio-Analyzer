"""
Portfolio calculations module for Portfolio Analyzer
Handles portfolio holdings, valuations and performance metrics
"""

import pandas as pd
import numpy_financial as npf
from typing import Dict, List, Tuple

class Portfolio:
    """Handles portfolio calculations and holdings management"""
    
    def compute_daily_portfolio_value(self, trades_df: pd.DataFrame, 
                                    prices_df: pd.DataFrame, 
                                    holdings_list: List[Tuple[str, str]]) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Compute daily portfolio value across currencies"""
        
        # Calculate cumulative quantities for each symbol
        daily_quantities = trades_df.pivot_table(
            index='Trade_Date', 
            columns='Symbol', 
            values='Quantity', 
            aggfunc='sum'
        ).fillna(0).cumsum()
        
        # Extend to full date range
        full_dates = prices_df.index
        daily_quantities = daily_quantities.reindex(full_dates, method='ffill').fillna(0)
        
        # Calculate daily values in USD
        portfolio_values = pd.DataFrame(index=full_dates)
        
        for symbol, currency in holdings_list:
            if symbol in prices_df.columns and symbol in daily_quantities.columns:
                prices_usd = prices_df[symbol].copy()
                
                # Convert SGD and INR prices to USD
                if currency == 'SGD':
                    prices_usd = prices_usd * prices_df['SGDUSD=X']
                elif currency == 'INR':
                    prices_usd = prices_usd * prices_df['INRUSD=X']
                
                portfolio_values[symbol] = daily_quantities[symbol] * prices_usd
        
        # Calculate total portfolio value
        portfolio_values['Total_Portfolio_Value_USD'] = portfolio_values.sum(axis=1)
        
        return portfolio_values, daily_quantities
    
    def calculate_total_investment(self, trades_df: pd.DataFrame) -> float:
        """
        Calculate total investment by summing all purchase cashflows (outflows).
        This represents the total capital deployed in the portfolio.
        """
        # Buy transactions are those with a negative cashflow in USD.
        buy_cashflows = trades_df[trades_df['Total_Cashflow_USD'] < 0]['Total_Cashflow_USD'].sum()
        
        # The sum will be negative, so we take the absolute value for the total investment amount.
        return abs(buy_cashflows)
    
    def get_current_holdings(self, daily_quantities: pd.DataFrame, 
                           historical_prices: pd.DataFrame, 
                           holdings_list: List[Tuple[str, str]]) -> List[Dict]:
        """Get current portfolio holdings with valuations"""
        current_holdings = []
        
        for symbol, currency in holdings_list:
            current_qty = daily_quantities[symbol].iloc[-1] if symbol in daily_quantities.columns else 0
            
            if symbol in historical_prices.columns:
                current_price_local = historical_prices[symbol].iloc[-1]
                
                # Convert to USD
                if currency == 'SGD':
                    current_price_usd = current_price_local * historical_prices['SGDUSD=X'].iloc[-1]
                elif currency == 'INR':
                    current_price_usd = current_price_local * historical_prices['INRUSD=X'].iloc[-1]
                else:
                    current_price_usd = current_price_local
                    
                current_value = current_qty * current_price_usd
                
                if abs(current_qty) > 0.001: # Only include meaningful holdings
                    current_holdings.append({
                        'Symbol': symbol,
                        'Current Quantity': current_qty,
                        'Current Price (USD)': current_price_usd,
                        'Current Value (USD)': current_value
                    })
        
        return sorted(current_holdings, key=lambda x: x['Current Value (USD)'], reverse=True)