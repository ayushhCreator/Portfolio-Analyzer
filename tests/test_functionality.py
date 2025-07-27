#!/usr/bin/env python3
"""
Test script to verify all Portfolio Analyzer functionality
"""

import pandas as pd
import sys
import os
from datetime import datetime

# Import all functions from app.py
from app import (
    load_and_consolidate_data,
    create_master_holdings_list,
    get_stock_splits,
    apply_split_adjustments,
    get_currency_rates,
    convert_to_usd,
    get_split_adjusted_prices,
    compute_daily_portfolio_value,
    calculate_xirr_by_holding,
    calculate_total_investment,
    get_news_google_rss
)

def test_portfolio_analyzer():
    """Test all functionality step by step"""
    print("🔍 Testing Portfolio Analyzer Functionality\n")
    
    # Files to test
    files = ['Stock_trading_2023.csv', 'Stock_trading_2024.csv', 'Stock_trading_2025.csv']
    
    try:
        # Step 1: Load and consolidate data
        print("1️⃣ Testing data loading...")
        trades_df = load_and_consolidate_data(files)
        if trades_df.empty:
            print("❌ No data loaded - check if CSV files exist")
            return False
        print(f"✅ Loaded {len(trades_df)} trades from {len(files)} files")
        print(f"   Date range: {trades_df['Trade_Date'].min()} to {trades_df['Trade_Date'].max()}")
        print(f"   Unique symbols: {trades_df['Symbol'].nunique()}")
        
        # Step 2: Create master holdings list
        print("\n2️⃣ Testing master holdings list...")
        holdings_list = create_master_holdings_list(trades_df)
        print(f"✅ Created holdings list with {len(holdings_list)} unique holdings")
        for symbol, currency in holdings_list[:5]:  # Show first 5
            print(f"   {symbol} ({currency})")
        
        # Step 3: Get stock splits
        print("\n3️⃣ Testing stock splits retrieval...")
        splits_dict = get_stock_splits(holdings_list)
        print(f"✅ Retrieved splits for {len(splits_dict)} stocks")
        for symbol, splits_df in list(splits_dict.items())[:3]:  # Show first 3
            print(f"   {symbol}: {len(splits_df)} splits")
        
        # Step 4: Apply split adjustments
        print("\n4️⃣ Testing split adjustments...")
        adjusted_trades = apply_split_adjustments(trades_df, splits_dict)
        print(f"✅ Applied split adjustments to {len(adjusted_trades)} trades")
        
        # Step 5: Get currency rates
        print("\n5️⃣ Testing currency rates...")
        start_date = adjusted_trades['Trade_Date'].min().date()
        end_date = datetime.now().date()
        currency_rates = get_currency_rates(start_date, end_date)
        if not currency_rates.empty:
            print(f"✅ Retrieved currency rates for {len(currency_rates)} days")
            print(f"   Latest SGD/USD: {currency_rates['SGDUSD=X'].iloc[-1]:.4f}")
            print(f"   Latest INR/USD: {currency_rates['INRUSD=X'].iloc[-1]:.4f}")
        else:
            print("❌ Failed to retrieve currency rates")
            return False
        
        # Step 6: Convert to USD
        print("\n6️⃣ Testing USD conversion...")
        usd_trades = convert_to_usd(adjusted_trades, currency_rates)
        print(f"✅ Converted {len(usd_trades)} trades to USD")
        total_usd_cashflow = usd_trades['Total_Cashflow_USD'].sum()
        print(f"   Total USD cashflow: ${total_usd_cashflow:,.2f}")
        
        # Step 7: Get historical prices
        print("\n7️⃣ Testing historical prices...")
        historical_prices = get_split_adjusted_prices(holdings_list, splits_dict, start_date, end_date)
        if not historical_prices.empty:
            print(f"✅ Retrieved historical prices for {len(historical_prices.columns)} symbols")
            print(f"   Price data from {historical_prices.index[0]} to {historical_prices.index[-1]}")
        else:
            print("❌ Failed to retrieve historical prices")
            return False
        
        # Step 8: Compute daily portfolio value
        print("\n8️⃣ Testing portfolio value computation...")
        portfolio_values, daily_quantities = compute_daily_portfolio_value(usd_trades, historical_prices, holdings_list)
        if not portfolio_values.empty:
            current_value = portfolio_values['Total_Portfolio_Value_USD'].iloc[-1]
            print(f"✅ Computed portfolio values for {len(portfolio_values)} days")
            print(f"   Current portfolio value: ${current_value:,.2f}")
        else:
            print("❌ Failed to compute portfolio values")
            return False
        
        # Step 9: Calculate XIRR
        print("\n9️⃣ Testing XIRR calculation...")
        xirr_results = calculate_xirr_by_holding(usd_trades, portfolio_values)
        valid_xirr = {k: v for k, v in xirr_results.items() if v is not None}
        print(f"✅ Calculated XIRR for {len(valid_xirr)} out of {len(xirr_results)} holdings")
        for symbol, xirr in list(valid_xirr.items())[:3]:  # Show first 3
            print(f"   {symbol}: {xirr*100:.2f}%")
        
        # Step 10: Test total investment calculation
        print("\n🔟 Testing total investment calculation...")
        total_invested = calculate_total_investment(usd_trades)
        print(f"✅ Total invested: ${total_invested:,.2f}")
        
        # Bonus: Test news functionality
        print("\n🎁 Testing news functionality...")
        if holdings_list:
            test_symbol, test_currency = holdings_list[0]
            news = get_news_google_rss(test_symbol, test_currency)
            print(f"✅ Retrieved {len(news)} news items for {test_symbol}")
            if news and len(news) > 0:
                print(f"   Latest: {news[0][:100]}...")
        
        print("\n🎉 All functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_portfolio_analyzer()
    sys.exit(0 if success else 1)
