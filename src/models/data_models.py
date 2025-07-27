"""
Scalable Data Models for Portfolio Analyzer
This module defines the data architecture with staging, dimension, and fact tables
"""

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import uuid
from typing import Dict, List, Tuple, Optional
import streamlit as st

class DataModels:
    """
    Scalable data architecture with staging, dimension, and fact tables
    """
    
    def __init__(self):
        self.stg_stock_price = pd.DataFrame()
        self.dim_stock = pd.DataFrame()
        self.fact_portfolio_transactions = pd.DataFrame()
        self.dim_user = pd.DataFrame()
        self.meta_refresh_log = pd.DataFrame()
    
    def initialize_schemas(self):
        """Initialize empty DataFrames with proper schemas"""
        
        # Staging Table - Raw stock price data
        self.stg_stock_price = pd.DataFrame(columns=[
            'symbol', 'date', 'open', 'close', 'high', 'low', 'volume', 
            'adj_close', 'created_at'
        ])
        
        # Dimension Table - Stock metadata
        self.dim_stock = pd.DataFrame(columns=[
            'symbol', 'company_name', 'industry', 'sector', 'exchange', 
            'country', 'currency', 'market_cap', 'website', 'description',
            'created_at', 'updated_at'
        ])
        
        # Fact Table - Portfolio transactions
        self.fact_portfolio_transactions = pd.DataFrame(columns=[
            'transaction_id', 'user_id', 'symbol', 'transaction_type', 
            'quantity', 'price', 'total_amount', 'fees', 'date', 
            'created_at'
        ])
        
        # Dimension Table - User information
        self.dim_user = pd.DataFrame(columns=[
            'user_id', 'user_name', 'email', 'created_at'
        ])
        
        # Metadata Table - Data refresh tracking
        self.meta_refresh_log = pd.DataFrame(columns=[
            'table_name', 'refresh_date', 'records_processed', 'status'
        ])
    
    def fetch_stock_metadata(self, symbols: List[str]) -> pd.DataFrame:
        """
        Fetch stock metadata from Yahoo Finance and populate dim_stock
        """
        metadata_list = []
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                metadata = {
                    'symbol': symbol,
                    'company_name': info.get('longName', 'N/A'),
                    'industry': info.get('industry', 'N/A'),
                    'sector': info.get('sector', 'N/A'),
                    'exchange': info.get('exchange', 'N/A'),
                    'country': info.get('country', 'N/A'),
                    'currency': info.get('currency', 'USD'),
                    'market_cap': info.get('marketCap', 0),
                    'website': info.get('website', 'N/A'),
                    'description': info.get('longBusinessSummary', 'N/A')[:500],  # Truncate
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                }
                metadata_list.append(metadata)
                
            except Exception as e:
                st.warning(f"Failed to fetch metadata for {symbol}: {str(e)}")
                # Add minimal record
                metadata_list.append({
                    'symbol': symbol,
                    'company_name': symbol,
                    'industry': 'Unknown',
                    'sector': 'Unknown',
                    'exchange': 'Unknown',
                    'country': 'Unknown',
                    'currency': 'USD',
                    'market_cap': 0,
                    'website': 'N/A',
                    'description': 'N/A',
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                })
        
        self.dim_stock = pd.DataFrame(metadata_list)
        return self.dim_stock
    
    def fetch_stock_prices(self, symbols: List[str], days: int = 30) -> pd.DataFrame:
        """
        Fetch stock price data and populate stg_stock_price
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        price_data_list = []
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(start=start_date, end=end_date)
                
                for date, row in hist.iterrows():
                    price_data = {
                        'symbol': symbol,
                        'date': date.date(),
                        'open': round(row['Open'], 4),
                        'close': round(row['Close'], 4),
                        'high': round(row['High'], 4),
                        'low': round(row['Low'], 4),
                        'volume': int(row['Volume']),
                        'adj_close': round(row['Close'], 4),  # Simplified for now
                        'created_at': datetime.now()
                    }
                    price_data_list.append(price_data)
                    
            except Exception as e:
                st.warning(f"Failed to fetch price data for {symbol}: {str(e)}")
        
        self.stg_stock_price = pd.DataFrame(price_data_list)
        return self.stg_stock_price
    
    def create_sample_users(self) -> pd.DataFrame:
        """
        Create sample users for demonstration
        """
        users = [
            {
                'user_id': 'user_001',
                'user_name': 'John Investor',
                'email': 'john@example.com',
                'created_at': datetime.now()
            },
            {
                'user_id': 'user_002', 
                'user_name': 'Sarah Trader',
                'email': 'sarah@example.com',
                'created_at': datetime.now()
            },
             {
                'user_id': 'user_003',
                'user_name': 'Ayush Investor',
                'email': 'ayush@example.com',
                'created_at': datetime.now()
            }
        ]
        
        self.dim_user = pd.DataFrame(users)
        return self.dim_user
    
    def create_sample_transactions(self, symbols: List[str]) -> pd.DataFrame:
        """
        Create sample portfolio transactions for demonstration
        """
        transactions = []
        
        # Sample transactions for user_001
        user_001_transactions = [
            {'user_id': 'user_001', 'symbol': 'AAPL', 'transaction_type': 'Buy', 'quantity': 100, 'price': 150.0, 'date': '2024-01-15'},
            {'user_id': 'user_001', 'symbol': 'AAPL', 'transaction_type': 'Buy', 'quantity': 50, 'price': 155.0, 'date': '2024-02-10'},
            {'user_id': 'user_001', 'symbol': 'TSLA', 'transaction_type': 'Buy', 'quantity': 30, 'price': 200.0, 'date': '2024-01-20'},
            {'user_id': 'user_001', 'symbol': 'TSLA', 'transaction_type': 'Sell', 'quantity': 10, 'price': 220.0, 'date': '2024-03-01'},
            {'user_id': 'user_001', 'symbol': 'INFY', 'transaction_type': 'Buy', 'quantity': 200, 'price': 18.5, 'date': '2024-02-05'},
        ]
        
        # Sample transactions for user_002
        user_002_transactions = [
            {'user_id': 'user_002', 'symbol': 'AAPL', 'transaction_type': 'Buy', 'quantity': 75, 'price': 145.0, 'date': '2024-01-10'},
            {'user_id': 'user_002', 'symbol': 'TSLA', 'transaction_type': 'Buy', 'quantity': 40, 'price': 195.0, 'date': '2024-01-25'},
            {'user_id': 'user_002', 'symbol': 'INFY', 'transaction_type': 'Buy', 'quantity': 300, 'price': 17.8, 'date': '2024-02-15'},
            {'user_id': 'user_002', 'symbol': 'AAPL', 'transaction_type': 'Sell', 'quantity': 25, 'price': 160.0, 'date': '2024-03-10'},
        ]
        

        user_003_transactions = [
            {'user_id': 'user_003', 'symbol': 'AAPL', 'transaction_type': 'Buy', 'quantity': 10, 'price': 200.0, 'date': '2025-01-10'},
            {'user_id': 'user_003', 'symbol': 'TSLA', 'transaction_type': 'Buy', 'quantity': 5, 'price': 240.0, 'date': '2025-01-25'},
            {'user_id': 'user_003', 'symbol': 'INFY', 'transaction_type': 'Buy', 'quantity': 10, 'price': 17.8, 'date': '2025-02-15'},
            {'user_id': 'user_003', 'symbol': 'AAPL', 'transaction_type': 'Sell', 'quantity': 5, 'price': 210.0, 'date': '2025-03-10'},
    ]

        all_transactions = user_001_transactions + user_002_transactions + user_003_transactions

        for i, txn in enumerate(all_transactions):
            transaction = {
                'transaction_id': f'txn_{i+1:03d}',
                'user_id': txn['user_id'],
                'symbol': txn['symbol'],
                'transaction_type': txn['transaction_type'],
                'quantity': txn['quantity'],
                'price': txn['price'],
                'total_amount': txn['quantity'] * txn['price'],
                'fees': round(txn['quantity'] * txn['price'] * 0.001, 2),  # 0.1% fee
                'date': datetime.strptime(txn['date'], '%Y-%m-%d').date(),
                'created_at': datetime.now()
            }
            transactions.append(transaction)
        
        self.fact_portfolio_transactions = pd.DataFrame(transactions)
        return self.fact_portfolio_transactions
    
    def log_refresh(self, table_name: str, records_processed: int, status: str):
        """
        Log data refresh operations
        """
        log_entry = {
            'table_name': table_name,
            'refresh_date': datetime.now(),
            'records_processed': records_processed,
            'status': status
        }
        
        new_log = pd.DataFrame([log_entry])
        self.meta_refresh_log = pd.concat([self.meta_refresh_log, new_log], ignore_index=True)
    
    def get_data_summary(self) -> Dict:
        """
        Get summary of all data tables
        """
        return {
            'staging_stock_price_records': len(self.stg_stock_price),
            'dimension_stock_records': len(self.dim_stock),
            'fact_transaction_records': len(self.fact_portfolio_transactions),
            'dimension_user_records': len(self.dim_user),
            'last_refresh': self.meta_refresh_log['refresh_date'].max() if not self.meta_refresh_log.empty else None
        }
