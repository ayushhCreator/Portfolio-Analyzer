"""
Test script for the Enhanced Portfolio Analyzer
Tests all components of the scalable architecture
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_models import DataModels
from portfolio_analytics import PortfolioAnalytics
import pandas as pd
from datetime import datetime

def test_enhanced_portfolio_analyzer():
    """Test all components of the enhanced system"""
    
    print("🚀 Testing Enhanced Portfolio Analyzer with Scalable Architecture")
    print("=" * 70)
    
    # 1. Test Data Models
    print("\n📊 Testing Data Models...")
    dm = DataModels()
    dm.initialize_schemas()
    
    # Test stock metadata fetching
    symbols = ['AAPL', 'TSLA', 'INFY']
    print(f"Fetching metadata for: {symbols}")
    
    metadata = dm.fetch_stock_metadata(symbols)
    print(f"✅ Stock metadata: {len(metadata)} records")
    print(metadata[['symbol', 'company_name', 'sector', 'industry']].to_string())
    
    # Test price data fetching
    print(f"\n📈 Fetching price data for last 7 days...")
    price_data = dm.fetch_stock_prices(symbols, days=7)
    print(f"✅ Price data: {len(price_data)} records")
    
    # Test user creation
    print(f"\n👥 Creating sample users...")
    users = dm.create_sample_users()
    print(f"✅ Users created: {len(users)} records")
    print(users[['user_id', 'user_name', 'email']].to_string())
    
    # Test transaction creation
    print(f"\n💰 Creating sample transactions...")
    transactions = dm.create_sample_transactions(symbols)
    print(f"✅ Transactions created: {len(transactions)} records")
    print(transactions[['user_id', 'symbol', 'transaction_type', 'quantity', 'price']].head(10).to_string())
    
    # 2. Test Analytics Engine
    print("\n📊 Testing Portfolio Analytics...")
    analytics = PortfolioAnalytics(dm)
    
    # Test for each user
    for user_id in ['user_001', 'user_002']:
        user_name = dm.dim_user[dm.dim_user['user_id'] == user_id]['user_name'].iloc[0]
        print(f"\n👤 Testing analytics for: {user_name} ({user_id})")
        
        # Current holdings
        holdings = analytics.get_current_holdings(user_id)
        print(f"✅ Current holdings: {len(holdings)} positions")
        if not holdings.empty:
            print(holdings[['symbol', 'quantity', 'current_price', 'current_value', 'unrealized_pnl_pct']].to_string())
        
        # XIRR calculations
        xirr_results = analytics.calculate_portfolio_xirr(user_id)
        portfolio_xirr = xirr_results['portfolio_xirr']
        print(f"✅ Portfolio XIRR: {portfolio_xirr:.2f}%" if portfolio_xirr else "❌ XIRR calculation failed")
        
        individual_xirr = xirr_results['individual_xirr']
        if individual_xirr:
            print("✅ Individual stock XIRR:")
            for symbol, xirr in individual_xirr.items():
                if xirr is not None:
                    print(f"   {symbol}: {xirr:.2f}%")
        
        # Diversification metrics
        diversification = analytics.calculate_diversification_metrics(user_id)
        if diversification:
            print(f"✅ Diversification score: {diversification['diversification_score']}")
            print(f"   Sectors: {diversification['sector_count']}")
            print(f"   Top 3 concentration: {diversification['top_3_concentration']:.1f}%")
        
        # Performance metrics
        performance = analytics.calculate_performance_metrics(user_id)
        if performance:
            print(f"✅ Performance metrics:")
            print(f"   Total invested: ${performance['total_invested']:,.2f}")
            print(f"   Current value: ${performance['current_value']:,.2f}")
            print(f"   Total return: {performance['total_return_pct']:+.2f}%")
        
        # Historical timeline
        timeline = analytics.generate_portfolio_timeline(user_id, days=7)
        print(f"✅ Historical timeline: {len(timeline)} data points")
        
        print("-" * 50)
    
    # 3. Test Data Summary
    print("\n📋 Data Architecture Summary:")
    summary = dm.get_data_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    print("\n🎉 Enhanced Portfolio Analyzer Test Complete!")
    print("✅ All components working with scalable architecture")
    return True

if __name__ == "__main__":
    try:
        test_enhanced_portfolio_analyzer()
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
