#!/usr/bin/env python3
"""
Demo: Portfolio Insights Testing
Test the advanced insights functionality with sample data
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.models.data_models import DataModels
from src.analytics.portfolio_analytics import PortfolioAnalytics
from src.analytics.portfolio_insights import PortfolioInsights
from datetime import datetime, timedelta
import json

def main():
    print("💡 PORTFOLIO INSIGHTS ENGINE DEMO")
    print("=" * 60)
    
    # Initialize components
    data_models = DataModels()
    data_models.initialize_schemas()
    
    # Create sample data
    symbols = ['AAPL', 'TSLA', 'INFY']
    data_models.create_sample_users()
    data_models.fetch_stock_metadata(symbols)  # Fetch real metadata first
    data_models.create_sample_transactions(symbols)
    
    print(f"✅ Initialized with {len(data_models.dim_user)} users and {len(data_models.fact_portfolio_transactions)} transactions")
    
    # Initialize analytics and insights
    analytics = PortfolioAnalytics(data_models)
    insights_engine = PortfolioInsights(data_models, analytics)
    
    # Test insights for a specific user and period
    user_id = 'user_003'  # Ayush Investor
    start_date = '2024-01-01'
    end_date = '2024-03-31'
    
    print(f"\n🔍 GENERATING INSIGHTS FOR USER: {user_id}")
    print(f"📅 Period: {start_date} to {end_date}")
    print("-" * 60)
    
    try:
        # Get insights
        insights = insights_engine.get_period_insights(user_id, start_date, end_date)
        
        if "error" in insights:
            print(f"❌ Error: {insights['error']}")
            return
        
        # Display portfolio overview
        overview = insights["portfolio_overview"]
        print("\n📊 PORTFOLIO OVERVIEW:")
        print(f"   Start Value: ${overview['start_value']:,.2f}")
        print(f"   End Value: ${overview['end_value']:,.2f}")
        print(f"   Total Return: ${overview['absolute_return']:,.2f} ({overview['percentage_return']:.2f}%)")
        print(f"   Annualized Return: {overview['annualized_return']:.2f}%")
        print(f"   Period: {overview['period_days']} days")
        
        # Display stock performance
        print("\n📈 STOCK PERFORMANCE:")
        for stock in insights["stock_performance"]:
            print(f"   {stock.symbol} ({stock.company_name}):")
            print(f"      Price Change: {stock.price_change_pct:.2f}%")
            print(f"      Portfolio Impact: ${stock.portfolio_impact:.2f}")
            print(f"      Performance Rating: {stock.performance_rating}")
            if stock.key_events:
                print(f"      Key Events: {', '.join(stock.key_events)}")
            print()
        
        # Display portfolio impact
        print("🎯 PORTFOLIO IMPACT ANALYSIS:")
        impact = insights["portfolio_impact_analysis"]
        print(f"   Total Portfolio Impact: ${impact['total_portfolio_impact']:,.2f}")
        
        print("\n   📈 Top Contributors:")
        for contrib in impact["top_contributors"][:3]:
            print(f"      {contrib['symbol']}: +${contrib['impact']:.2f} ({contrib['contribution_pct']:.1f}%)")
        
        print("\n   📉 Top Detractors:")
        for detractor in impact["top_detractors"][:3]:
            print(f"      {detractor['symbol']}: ${detractor['impact']:.2f} ({detractor['contribution_pct']:.1f}%)")
        
        # Display market events
        print("\n📰 MARKET EVENTS:")
        events = insights["market_events"]
        if events:
            for event in events:
                print(f"   📅 {event['date']}: {event['description']}")
                print(f"      Impact Level: {event['impact_level']} | Sectors: {', '.join(event['affected_sectors'])}")
        else:
            print("   No significant market events recorded for this period")
        
        # Display sector analysis
        print("\n🏭 SECTOR PERFORMANCE:")
        for sector, data in insights["sector_analysis"].items():
            print(f"   {sector}:")
            print(f"      Average Performance: {data['average_performance']:.2f}%")
            print(f"      Total Impact: ${data['total_impact']:.2f}")
            print(f"      Stock Count: {data['stock_count']}")
        
        # Display risk insights
        print("\n⚠️ RISK ANALYSIS:")
        risk = insights["risk_insights"]
        print(f"   Portfolio Risk Level: {risk['risk_level']}")
        print(f"   Diversification: {risk['portfolio_diversification']} stocks")
        if risk["highest_risk_stock"]:
            print(f"   Highest Risk Stock: {risk['highest_risk_stock']['symbol']} ({risk['highest_risk_stock']['volatility']:.1f}% volatility)")
        if risk["lowest_risk_stock"]:
            print(f"   Lowest Risk Stock: {risk['lowest_risk_stock']['symbol']} ({risk['lowest_risk_stock']['volatility']:.1f}% volatility)")
        
        # Display recommendations
        print("\n💰 AI-GENERATED RECOMMENDATIONS:")
        recommendations = insights["recommendations"]
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        else:
            print("   No specific recommendations. Portfolio appears well-balanced.")
        
        print("\n✅ INSIGHTS GENERATION COMPLETED SUCCESSFULLY!")
        print("\n🚀 FEATURES DEMONSTRATED:")
        print("   • Time-period specific analysis")
        print("   • Individual stock performance tracking")
        print("   • Portfolio impact analysis")
        print("   • Market events correlation")
        print("   • Sector performance breakdown")
        print("   • Risk assessment")
        print("   • AI-powered recommendations")
        print("   • Visual performance comparisons")
        
    except Exception as e:
        print(f"❌ Error during insights generation: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
