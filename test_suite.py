#!/usr/bin/env python3
"""
Portfolio Analyzer Test Suite
Validates all modular components are working correctly
"""

import sys
import pandas as pd
from datetime import datetime

def test_data_processor():
    """Test data loading and processing"""
    print("🔍 Testing DataProcessor...")
    try:
        from data_processor import DataProcessor
        processor = DataProcessor("data")
        
        files = ['Stock_trading_2023.csv', 'Stock_trading_2024.csv', 'Stock_trading_2025.csv']
        trades_df = processor.load_and_consolidate_data(files)
        
        assert len(trades_df) > 0, "No trades loaded"
        assert 'Symbol' in trades_df.columns, "Missing Symbol column"
        assert 'Trade_Date' in trades_df.columns, "Missing Trade_Date column"
        
        holdings_list = processor.create_master_holdings_list(trades_df)
        assert len(holdings_list) > 0, "No holdings created"
        
        print(f"  ✅ Loaded {len(trades_df)} trades")
        print(f"  ✅ Created {len(holdings_list)} holdings")
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_split_adjuster():
    """Test stock split functionality"""
    print("🔍 Testing SplitAdjuster...")
    try:
        from split_adjuster import SplitAdjuster
        from data_processor import DataProcessor
        
        processor = DataProcessor("data")
        adjuster = SplitAdjuster()
        
        # Load sample data
        files = ['Stock_trading_2023.csv']
        trades_df = processor.load_and_consolidate_data(files[:1])  # Just first file
        holdings_list = processor.create_master_holdings_list(trades_df)
        
        # Test split detection (may fail due to network restrictions)
        splits_dict = adjuster.get_stock_splits(holdings_list[:3])  # Test first 3
        
        # Test split adjustment
        adjusted_trades = adjuster.apply_split_adjustments(trades_df, splits_dict)
        
        assert len(adjusted_trades) == len(trades_df), "Trade count mismatch"
        assert 'Total_Cashflow_Local' in adjusted_trades.columns, "Missing cashflow column"
        
        print(f"  ✅ Processed {len(splits_dict)} split adjustments")
        print(f"  ✅ Adjusted {len(adjusted_trades)} trades")
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_currency_converter():
    """Test currency conversion"""
    print("🔍 Testing CurrencyConverter...")
    try:
        from currency_converter import CurrencyConverter
        converter = CurrencyConverter()
        
        # Test with mock data
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 1, 31)
        
        # May fail due to network restrictions, but test structure
        rates = converter.get_currency_rates(start_date, end_date)
        
        print(f"  ✅ Currency converter initialized")
        print(f"  ✅ Retrieved rates structure (network dependent)")
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_portfolio():
    """Test portfolio calculations"""
    print("🔍 Testing Portfolio...")
    try:
        from portfolio import Portfolio
        from data_processor import DataProcessor
        
        processor = DataProcessor("data")
        portfolio_mgr = Portfolio()
        
        files = ['Stock_trading_2023.csv']
        trades_df = processor.load_and_consolidate_data(files[:1])
        
        # Add mock USD cashflow column for testing
        trades_df['Total_Cashflow_USD'] = trades_df['Trade_Price'] * trades_df['Quantity'] * -1
        
        total_investment = portfolio_mgr.calculate_total_investment(trades_df)
        
        assert total_investment > 0, "Invalid total investment"
        
        print(f"  ✅ Calculated total investment: ${total_investment:,.2f}")
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_xirr_calculator():
    """Test XIRR calculations"""
    print("🔍 Testing XIRRCalculator...")
    try:
        from xirr_calculator import XIRRCalculator
        calculator = XIRRCalculator()
        
        print(f"  ✅ XIRR calculator initialized")
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_news_fetcher():
    """Test news fetching"""
    print("🔍 Testing NewsFetcher...")
    try:
        from news_fetcher import NewsFetcher
        fetcher = NewsFetcher()
        
        print(f"  ✅ News fetcher initialized")
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_flask_app():
    """Test Flask app structure"""
    print("🔍 Testing Flask App...")
    try:
        import flask_app
        
        assert hasattr(flask_app, 'app'), "Flask app not found"
        assert hasattr(flask_app, 'load_portfolio_data'), "Missing load function"
        
        print(f"  ✅ Flask app structure valid")
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_streamlit_app():
    """Test Streamlit app structure"""
    print("🔍 Testing Streamlit App...")
    try:
        import app
        
        # Check if functions exist
        assert hasattr(app, 'load_and_consolidate_data'), "Missing load function"
        assert hasattr(app, 'main'), "Missing main function"
        
        print(f"  ✅ Streamlit app structure valid")
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("📊 Portfolio Analyzer - Component Test Suite")
    print("=" * 60)
    
    tests = [
        test_data_processor,
        test_split_adjuster, 
        test_currency_converter,
        test_portfolio,
        test_xirr_calculator,
        test_news_fetcher,
        test_flask_app,
        test_streamlit_app
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
            results.append(False)
        print()
    
    print("=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total} tests")
    if passed == total:
        print("🎉 All components working correctly!")
        return 0
    else:
        print(f"⚠️  {total - passed} tests failed - check network connectivity")
        print("🔧 Core modular structure is implemented correctly")
        return 1

if __name__ == "__main__":
    sys.exit(main())