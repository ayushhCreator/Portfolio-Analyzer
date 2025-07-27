#!/usr/bin/env python3
"""
Debug cashflow logic to understand the problem
"""

import pandas as pd
from app import *

def debug_cashflow_logic():
    print("🔍 Debugging Cashflow Logic\n")
    
    # Load data
    trades_df = load_and_consolidate_data(['Stock_trading_2023.csv', 'Stock_trading_2024.csv', 'Stock_trading_2025.csv'])
    holdings_list = create_master_holdings_list(trades_df)
    splits_dict = get_stock_splits(holdings_list)
    adjusted_trades = apply_split_adjustments(trades_df, splits_dict)
    
    start_date = adjusted_trades['Trade_Date'].min().date()
    end_date = pd.Timestamp.now().date()
    currency_rates = get_currency_rates(start_date, end_date)
    usd_trades = convert_to_usd(adjusted_trades, currency_rates)
    
    # Check cashflow logic for a specific symbol
    symbol = 'AAPL'  # Let's debug AAPL
    aapl_trades = usd_trades[usd_trades['Symbol'] == symbol].copy()
    
    if not aapl_trades.empty:
        print(f"=== {symbol} Cashflow Analysis ===")
        print("Raw trade data:")
        print(aapl_trades[['Trade_Date', 'Quantity', 'Trade_Price_USD', 'Total_Cashflow_USD']].to_string())
        print()
        
        # Check current cashflow signs
        buys = aapl_trades[aapl_trades['Quantity'] > 0]  # Buy transactions
        sells = aapl_trades[aapl_trades['Quantity'] < 0]  # Sell transactions
        
        print("Buy transactions (should be negative cashflows):")
        if not buys.empty:
            print(buys[['Trade_Date', 'Quantity', 'Total_Cashflow_USD']].to_string())
        print()
        
        print("Sell transactions (should be positive cashflows):")
        if not sells.empty:
            print(sells[['Trade_Date', 'Quantity', 'Total_Cashflow_USD']].to_string())
        print()
        
        # Current quantity held
        current_qty = aapl_trades['Quantity'].sum()
        print(f"Current quantity held: {current_qty}")
        
        # Total investment (should be sum of negative cashflows made positive)
        total_investment_current = abs(aapl_trades[aapl_trades['Total_Cashflow_USD'] < 0]['Total_Cashflow_USD'].sum())
        print(f"Total investment (current logic): ${total_investment_current:,.2f}")
        
        # CORRECTED total investment should be sum of all buy amounts
        total_investment_correct = abs(buys['Total_Cashflow_USD'].sum())
        print(f"Total investment (corrected): ${total_investment_correct:,.2f}")
        
    else:
        print(f"No {symbol} trades found. Let's try NET instead.")
        symbol = 'NET'
        debug_symbol_cashflow(usd_trades, symbol)

def debug_symbol_cashflow(usd_trades, symbol):
    """Debug cashflow for any symbol"""
    symbol_trades = usd_trades[usd_trades['Symbol'] == symbol].copy()
    
    if symbol_trades.empty:
        print(f"No {symbol} trades found")
        return
        
    print(f"=== {symbol} Cashflow Analysis ===")
    print("All trades:")
    print(symbol_trades[['Trade_Date', 'Quantity', 'Trade_Price_USD', 'Total_Cashflow_USD']].to_string())
    print()
    
    # Current logic analysis
    buys = symbol_trades[symbol_trades['Quantity'] > 0]
    sells = symbol_trades[symbol_trades['Quantity'] < 0]
    
    print(f"Buy transactions: {len(buys)}")
    print(f"Sell transactions: {len(sells)}")
    print(f"Total quantity: {symbol_trades['Quantity'].sum()}")
    print(f"Total cashflow: ${symbol_trades['Total_Cashflow_USD'].sum():,.2f}")

if __name__ == "__main__":
    debug_cashflow_logic()
