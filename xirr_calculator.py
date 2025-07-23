"""
XIRR calculation module for Portfolio Analyzer
Computes Extended Internal Rate of Return for holdings
"""

import pandas as pd
import numpy_financial as npf
from typing import Dict

class XIRRCalculator:
    """Handles XIRR calculations for portfolio holdings"""
    
    def calculate_xirr_by_holding(self, trades_df: pd.DataFrame, portfolio_values: pd.DataFrame) -> Dict[str, float]:
        """Compute XIRR for each holding: buy = negative, sell = positive, add current value if holding exists."""
        xirr_results = {}
        last_date = portfolio_values.index[-1]

        for symbol in trades_df['Symbol'].unique():
            symbol_trades = trades_df[trades_df['Symbol'] == symbol].copy()
            if symbol_trades.empty:
                xirr_results[symbol] = None
                continue

            # Chronological order
            symbol_trades.sort_values(by='Trade_Date', inplace=True)

            # Prepare cashflows
            cashflows = symbol_trades['Total_Cashflow_USD'].tolist()
            dates = symbol_trades['Trade_Date'].tolist()

            # Current holding value
            current_quantity = symbol_trades['Quantity'].sum()
            current_value = portfolio_values[symbol].iloc[-1] if symbol in portfolio_values.columns else 0

            # If still holding shares, add current market value as last positive cashflow
            # If position is closed (all sold), do not add
            if abs(current_quantity) > 1e-6:
                cashflows.append(current_value)
                dates.append(last_date)

            # XIRR requires at least one positive and one negative cashflow
            if len(cashflows) >= 2 and any(cf > 0 for cf in cashflows) and any(cf < 0 for cf in cashflows):
                try:
                    # Use .date() for each date for npf.xirr
                    date_objects = [d.date() for d in dates]
                    xirr_value = npf.xirr(cashflows, date_objects)
                    # Filter out extreme values
                    if pd.notna(xirr_value) and abs(xirr_value) < 10:
                        xirr_results[symbol] = xirr_value
                    else:
                        xirr_results[symbol] = None
                except Exception as e:
                    xirr_results[symbol] = None
            else:
                xirr_results[symbol] = None

        return xirr_results
    
    def validate_xirr_calculation(self, trades_df: pd.DataFrame, portfolio_values: pd.DataFrame):
        """Simple validation to check if cashflows make sense"""
        print("\n=== XIRR Validation ===")
        
        # Check first few symbols
        test_symbols = ['NET', 'MSFT', 'AAPL', 'NVDA']
        
        for symbol in test_symbols:
            if symbol not in trades_df['Symbol'].unique():
                continue
                
            symbol_trades = trades_df[trades_df['Symbol'] == symbol].copy()
            print(f"\n{symbol}:")
            print(f"  Number of trades: {len(symbol_trades)}")
            print(f"  Total quantity: {symbol_trades['Quantity'].sum()}")
            print(f"  Cashflow range: ${symbol_trades['Total_Cashflow_USD'].min():.2f} to ${symbol_trades['Total_Cashflow_USD'].max():.2f}")
            
            # Check if Total_Cashflow_USD has the right signs
            buys = symbol_trades[symbol_trades['Quantity'] > 0]
            sells = symbol_trades[symbol_trades['Quantity'] < 0]
            
            print(f"  Buy trades cashflow (should be negative): {buys['Total_Cashflow_USD'].tolist()}")
            print(f"  Sell trades cashflow (should be positive): {sells['Total_Cashflow_USD'].tolist()}")