#!/usr/bin/env python3
"""
Test script to verify XIRR calculation with manual validation
"""

import pandas as pd
from pyxirr import xirr as pyxirr_calc
def calculate_xirr(amounts, dates):
    return pyxirr_calc(amounts=amounts, dates=dates)
from datetime import datetime, date
from app import *
import warnings
warnings.filterwarnings('ignore')

def test_xirr_calculation():
    print("🔍 Testing XIRR Calculation with Manual Validation\n")
    
    # Load and process data
    trades_df = load_and_consolidate_data(['Stock_trading_2023.csv', 'Stock_trading_2024.csv', 'Stock_trading_2025.csv'])
    holdings_list = create_master_holdings_list(trades_df)
    splits_dict = get_stock_splits(holdings_list)
    adjusted_trades = apply_split_adjustments(trades_df, splits_dict)
    
    start_date = adjusted_trades['Trade_Date'].min().date()
    end_date = datetime.now().date()
    currency_rates = get_currency_rates(start_date, end_date)
    usd_trades = convert_to_usd(adjusted_trades, currency_rates)
    historical_prices = get_split_adjusted_prices(holdings_list, splits_dict, start_date, end_date)
    portfolio_values, daily_quantities = compute_daily_portfolio_value(usd_trades, historical_prices, holdings_list)
    
    # Test XIRR for specific symbols
    test_symbols = ['NET', 'AAPL', 'MSFT', 'NVDA']
    
    for symbol in test_symbols:
        if symbol not in usd_trades['Symbol'].unique():
            print(f"❌ {symbol} not found in trades")
            continue
            
        print(f"=== {symbol} XIRR Analysis ===")
        
        # Get symbol trades
        symbol_trades = usd_trades[usd_trades['Symbol'] == symbol].copy()
        symbol_trades.sort_values('Trade_Date', inplace=True)
        
        # Show cashflow pattern
        print("Cashflow pattern:")
        for _, trade in symbol_trades.iterrows():
            sign = "📈" if trade['Total_Cashflow_USD'] > 0 else "📉"
            print(f"  {trade['Trade_Date'].date()}: {sign} ${trade['Total_Cashflow_USD']:,.2f} (Qty: {trade['Quantity']:,.0f})")
        
        # Current holding value
        current_quantity = symbol_trades['Quantity'].sum()
        current_value = portfolio_values[symbol].iloc[-1] if symbol in portfolio_values.columns else 0
        last_date = portfolio_values.index[-1]
        
        print(f"Current holding: {current_quantity:,.2f} shares worth ${current_value:,.2f}")
        
        # Manual XIRR calculation
        cashflows = symbol_trades['Total_Cashflow_USD'].tolist()
        dates = [d.date() if hasattr(d, 'date') else d for d in symbol_trades['Trade_Date'].tolist()]
        
        if abs(current_quantity) > 0.001 and current_value > 0:
            cashflows.append(current_value)
            dates.append(last_date.date())
            print(f"Adding final cashflow: 📈 ${current_value:,.2f} on {last_date.date()}")
        
        # Calculate XIRR
        if len(cashflows) >= 2 and any(cf > 0 for cf in cashflows) and any(cf < 0 for cf in cashflows):
            try:
                # Convert dates to proper format for pyxirr
                date_objects = []
                for d in dates:
                    if hasattr(d, 'date'):
                        date_objects.append(d.date())
                    elif isinstance(d, pd.Timestamp):
                        date_objects.append(d.date())
                    else:
                        date_objects.append(d)
                
                # Ensure cashflows are floats
                float_cashflows = [float(cf) for cf in cashflows]
                xirr_value = calculate_xirr(float_cashflows, date_objects)
                if pd.notna(xirr_value) and abs(xirr_value) < 10:
                    print(f"✅ XIRR: {xirr_value*100:.2f}% annually")
                    
                    # Show validation info
                    total_invested = abs(sum([cf for cf in cashflows if cf < 0]))
                    total_received = sum([cf for cf in cashflows if cf > 0])
                    print(f"   Total invested: ${total_invested:,.2f}")
                    print(f"   Total value (sales + current): ${total_received:,.2f}")
                    print(f"   Simple return: {((total_received - total_invested) / total_invested * 100):.2f}%")
                else:
                    print(f"❌ XIRR calculation resulted in extreme value: {xirr_value}")
            except Exception as e:
                print(f"❌ XIRR calculation failed: {str(e)}")
        else:
            print("❌ Insufficient cashflow data for XIRR calculation")
            print(f"   Cashflows: {len(cashflows)}, Positive: {sum(1 for cf in cashflows if cf > 0)}, Negative: {sum(1 for cf in cashflows if cf < 0)}")
        
        print()
    
    # Test overall XIRR calculation
    print("=== Overall XIRR Test ===")
    xirr_results = calculate_xirr_by_holding(usd_trades, portfolio_values)
    valid_xirr = {k: v for k, v in xirr_results.items() if v is not None}
    print(f"✅ Successfully calculated XIRR for {len(valid_xirr)} out of {len(xirr_results)} holdings")
    
    for symbol, xirr in valid_xirr.items():
        print(f"  {symbol}: {xirr*100:.2f}%")
    
    # Test total investment
    print(f"\n=== Total Investment Test ===")
    total_invested = calculate_total_investment(usd_trades)
    print(f"✅ Total invested: ${total_invested:,.2f}")
    
    # Validation: manual calculation
    manual_total = abs(usd_trades[usd_trades['Total_Cashflow_USD'] < 0]['Total_Cashflow_USD'].sum())
    print(f"   Manual verification: ${manual_total:,.2f}")
    print(f"   Match: {'✅' if abs(total_invested - manual_total) < 0.01 else '❌'}")

if __name__ == "__main__":
    test_xirr_calculation()
