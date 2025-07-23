#!/usr/bin/env python3
"""
Simple test suite for Portfolio Analyzer core functionality.
Tests the main data processing functions independently of external APIs.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add current directory to path to import app modules
sys.path.append(os.path.dirname(__file__))

def test_data_loading():
    """Test that CSV files can be loaded and consolidated."""
    print("Testing data loading...")
    
    try:
        from app import load_and_consolidate_data, FILES
        
        # Test data loading
        trades_df = load_and_consolidate_data(FILES)
        
        assert not trades_df.empty, "No trade data loaded"
        assert 'Symbol' in trades_df.columns, "Symbol column missing"
        assert 'Trade_Date' in trades_df.columns, "Trade_Date column missing"
        assert 'Quantity' in trades_df.columns, "Quantity column missing"
        assert 'Trade_Price' in trades_df.columns, "Trade_Price column missing"
        
        print(f"✅ Data loading test passed - Loaded {len(trades_df)} trades")
        return True
        
    except Exception as e:
        print(f"❌ Data loading test failed: {e}")
        return False

def test_holdings_list():
    """Test master holdings list creation."""
    print("Testing holdings list creation...")
    
    try:
        from app import load_and_consolidate_data, create_master_holdings_list, FILES
        
        trades_df = load_and_consolidate_data(FILES)
        holdings_list = create_master_holdings_list(trades_df)
        
        assert len(holdings_list) > 0, "No holdings found"
        assert all(len(holding) == 2 for holding in holdings_list), "Invalid holding format"
        
        symbols = [holding[0] for holding in holdings_list]
        assert len(set(symbols)) == len(symbols), "Duplicate symbols in holdings list"
        
        print(f"✅ Holdings list test passed - Found {len(holdings_list)} unique holdings")
        return True
        
    except Exception as e:
        print(f"❌ Holdings list test failed: {e}")
        return False

def test_split_adjustments():
    """Test split adjustment logic with mock data."""
    print("Testing split adjustments...")
    
    try:
        from app import apply_split_adjustments
        
        # Create mock trade data
        test_trades = pd.DataFrame({
            'Symbol': ['TEST', 'TEST', 'TEST'],
            'Trade_Date': [
                datetime(2023, 1, 1),
                datetime(2023, 6, 1),  # Before split
                datetime(2023, 12, 1)  # After split
            ],
            'Quantity': [100, 50, 25],
            'Trade_Price': [10.0, 20.0, 40.0],
            'Comm/Fee': [1.0, 1.0, 1.0]
        })
        
        # Mock split data (2:1 split on July 1, 2023)
        mock_splits = {
            'TEST': pd.DataFrame({
                'Split_Date': [datetime(2023, 7, 1)],
                'Split_Ratio': [2.0]  # 2:1 split
            })
        }
        
        adjusted_trades = apply_split_adjustments(test_trades, mock_splits)
        
        # Check that pre-split trades were adjusted
        pre_split_trades = adjusted_trades[adjusted_trades['Trade_Date'] < datetime(2023, 7, 1)]
        post_split_trades = adjusted_trades[adjusted_trades['Trade_Date'] >= datetime(2023, 7, 1)]
        
        # Pre-split quantities should be doubled, prices halved
        assert pre_split_trades.iloc[0]['Quantity'] == 200, "Split adjustment failed for quantity"
        assert pre_split_trades.iloc[0]['Trade_Price'] == 5.0, "Split adjustment failed for price"
        
        # Post-split trades should remain unchanged
        assert post_split_trades.iloc[0]['Quantity'] == 25, "Post-split trade incorrectly adjusted"
        
        print("✅ Split adjustments test passed")
        return True
        
    except Exception as e:
        print(f"❌ Split adjustments test failed: {e}")
        return False

def test_currency_conversion():
    """Test currency conversion logic."""
    print("Testing currency conversion...")
    
    try:
        from app import convert_to_usd
        
        # Create mock trade data with different currencies
        test_trades = pd.DataFrame({
            'Symbol': ['USD_STOCK', 'SGD_STOCK', 'INR_STOCK'],
            'Currency': ['USD', 'SGD', 'INR'],
            'Trade_Date': [datetime(2023, 1, 1)] * 3,
            'Trade_Price': [100.0, 100.0, 100.0],
            'Total_Cashflow_Local': [-1000.0, -1000.0, -1000.0]
        })
        test_trades['Trade_Date_Key'] = test_trades['Trade_Date'].dt.floor('D')
        
        # Mock currency rates
        mock_rates = pd.DataFrame({
            'SGDUSD=X': [0.75],  # SGD to USD
            'INRUSD=X': [0.012], # INR to USD
            'USDUSD=X': [1.0]    # USD to USD
        }, index=[datetime(2023, 1, 1)])
        
        converted_trades = convert_to_usd(test_trades, mock_rates)
        
        # Check conversions
        usd_trade = converted_trades[converted_trades['Currency'] == 'USD'].iloc[0]
        sgd_trade = converted_trades[converted_trades['Currency'] == 'SGD'].iloc[0]
        inr_trade = converted_trades[converted_trades['Currency'] == 'INR'].iloc[0]
        
        assert usd_trade['Trade_Price_USD'] == 100.0, "USD conversion failed"
        assert sgd_trade['Trade_Price_USD'] == 75.0, "SGD conversion failed"
        assert inr_trade['Trade_Price_USD'] == 1.2, "INR conversion failed"
        
        print("✅ Currency conversion test passed")
        return True
        
    except Exception as e:
        print(f"❌ Currency conversion test failed: {e}")
        return False

def test_portfolio_calculation():
    """Test portfolio value calculation logic."""
    print("Testing portfolio value calculation...")
    
    try:
        from app import compute_daily_portfolio_value
        
        # Create mock trade data
        test_trades = pd.DataFrame({
            'Trade_Date': [datetime(2023, 1, 1), datetime(2023, 1, 2)],
            'Symbol': ['STOCK_A', 'STOCK_A'],
            'Quantity': [100, 50]
        })
        
        # Create mock price data
        price_dates = pd.date_range(start='2023-01-01', end='2023-01-03', freq='D')
        test_prices = pd.DataFrame({
            'STOCK_A': [10.0, 11.0, 12.0],
            'SGDUSD=X': [0.75, 0.75, 0.75],
            'INRUSD=X': [0.012, 0.012, 0.012]
        }, index=price_dates)
        
        holdings_list = [('STOCK_A', 'USD')]
        
        portfolio_values, daily_quantities = compute_daily_portfolio_value(
            test_trades, test_prices, holdings_list
        )
        
        # Check calculations
        assert len(portfolio_values) == 3, "Wrong number of portfolio value dates"
        assert 'Total_Portfolio_Value_USD' in portfolio_values.columns, "Total portfolio value missing"
        
        # Day 1: 100 shares @ $10 = $1000
        # Day 2: 150 shares @ $11 = $1650  
        # Day 3: 150 shares @ $12 = $1800
        expected_values = [1000.0, 1650.0, 1800.0]
        actual_values = portfolio_values['Total_Portfolio_Value_USD'].tolist()
        
        for i, (expected, actual) in enumerate(zip(expected_values, actual_values)):
            assert abs(actual - expected) < 1e-6, f"Portfolio value mismatch on day {i+1}: expected {expected}, got {actual}"
        
        print("✅ Portfolio calculation test passed")
        return True
        
    except Exception as e:
        print(f"❌ Portfolio calculation test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and return overall pass/fail status."""
    print("=" * 50)
    print("Running Portfolio Analyzer Test Suite")
    print("=" * 50)
    
    tests = [
        test_data_loading,
        test_holdings_list,
        test_split_adjustments,
        test_currency_conversion,
        test_portfolio_calculation
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        if test_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Portfolio Analyzer core functionality is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    # Suppress warnings during testing
    import warnings
    warnings.filterwarnings('ignore')
    
    success = run_all_tests()
    sys.exit(0 if success else 1)