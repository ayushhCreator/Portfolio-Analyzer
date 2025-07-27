#!/usr/bin/env python3
"""
Demo: Scalable Data Structure for Portfolio Analyzer
This script demonstrates the complete data architecture with sample data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_models import DataModels
import pandas as pd
from datetime import datetime

def main():
    print("📊 SCALABLE DATA STRUCTURE FOR PORTFOLIO ANALYZER")
    print("=" * 70)
    
    # Initialize data models
    dm = DataModels()
    dm.initialize_schemas()
    
    print("\n🏗️  TABLE SCHEMAS:")
    
    print("\n1. STG_STOCK_PRICE (Staging Table - Raw Stock Data):")
    for col in dm.stg_stock_price.columns:
        print(f"   📍 {col}")
    
    print("\n2. DIM_STOCK (Dimension Table - Stock Metadata):")
    for col in dm.dim_stock.columns:
        print(f"   📍 {col}")
    
    print("\n3. FACT_PORTFOLIO_TRANSACTIONS (Fact Table - Transaction Events):")
    for col in dm.fact_portfolio_transactions.columns:
        print(f"   📍 {col}")
    
    print("\n4. DIM_USER (Dimension Table - User Information):")
    for col in dm.dim_user.columns:
        print(f"   📍 {col}")
    
    print("\n5. META_REFRESH_LOG (Metadata Table - ETL Tracking):")
    for col in dm.meta_refresh_log.columns:
        print(f"   📍 {col}")
    
    # Sample data population
    symbols = ['AAPL', 'TSLA', 'INFY']
    print(f"\n🔄 POPULATING SAMPLE DATA FOR: {symbols}")
    
    try:
        # Fetch stock metadata
        dm.fetch_stock_metadata(symbols)
        print(f"\n📋 DIM_STOCK populated with {len(dm.dim_stock)} records:")
        
        for _, stock in dm.dim_stock.iterrows():
            print(f"   🏢 {stock['symbol']}: {stock['company_name']}")
            print(f"      Sector: {stock['sector']} | Industry: {stock['industry']}")
            print(f"      Country: {stock['country']} | Exchange: {stock['exchange']}")
            print(f"      Market Cap: ${stock['market_cap']:,}")
            print()
        
        # Fetch price data (last 7 days for demo)
        dm.fetch_stock_prices(symbols, days=7)
        print(f"📈 STG_STOCK_PRICE populated with {len(dm.stg_stock_price)} price records")
        
        # Create users
        dm.create_sample_users()
        print(f"👥 DIM_USER populated with {len(dm.dim_user)} users:")
        for _, user in dm.dim_user.iterrows():
            print(f"   👤 {user['user_name']} ({user['user_id']})")
        
        # Create sample transactions
        dm.create_sample_transactions(symbols)
        print(f"\n💰 FACT_PORTFOLIO_TRANSACTIONS populated with {len(dm.fact_portfolio_transactions)} transactions")
        
        # Log the refresh
        dm.log_refresh('demo_population', len(dm.fact_portfolio_transactions), 'SUCCESS')
        
        print("\n📊 DATA SUMMARY:")
        summary = dm.get_data_summary()
        for key, value in summary.items():
            print(f"   📈 {key}: {value}")
        
        print("\n✅ SCALABLE ARCHITECTURE SUCCESSFULLY DEMONSTRATED!")
        print("   • Staging tables for raw data ingestion")
        print("   • Dimension tables for master data")
        print("   • Fact tables for transactional data")
        print("   • Metadata tables for ETL tracking")
        print("   • Automatic data population from Yahoo Finance")
        
    except Exception as e:
        print(f"❌ Error during data population: {str(e)}")
        print("   This might be due to network connectivity or Yahoo Finance API limits")

if __name__ == "__main__":
    main()
