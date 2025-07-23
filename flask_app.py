"""
Flask web application for Portfolio Analyzer
Main web interface for the portfolio analysis system
"""

from flask import Flask, render_template, jsonify, request
import pandas as pd
from datetime import datetime
import json

from data_processor import DataProcessor
from split_adjuster import SplitAdjuster
from currency_converter import CurrencyConverter
from price_fetcher import PriceFetcher
from portfolio import Portfolio
from xirr_calculator import XIRRCalculator
from news_fetcher import NewsFetcher

app = Flask(__name__)

# Configuration
BASE_CURRENCY = "USD"
FILES = ['Stock_trading_2023.csv', 'Stock_trading_2024.csv', 'Stock_trading_2025.csv']

# Initialize components
data_processor = DataProcessor("data")
split_adjuster = SplitAdjuster()
currency_converter = CurrencyConverter()
price_fetcher = PriceFetcher()
portfolio_manager = Portfolio()
xirr_calculator = XIRRCalculator()
news_fetcher = NewsFetcher()

# Global variables to store processed data
processed_data = {}

def load_portfolio_data():
    """Load and process all portfolio data"""
    global processed_data
    
    # Step 1: Load data
    trades_df = data_processor.load_and_consolidate_data(FILES)
    
    if trades_df.empty:
        return False
    
    # Step 2: Create master holdings
    holdings_list = data_processor.create_master_holdings_list(trades_df)
    
    # Step 3: Get splits
    splits_dict = split_adjuster.get_stock_splits(holdings_list)
    
    # Step 4: Apply split adjustments
    adjusted_trades = split_adjuster.apply_split_adjustments(trades_df, splits_dict)
    
    # Date range
    start_date = adjusted_trades['Trade_Date'].min().date()
    end_date = datetime.now().date()
    
    # Step 5: Get currency rates
    currency_rates = currency_converter.get_currency_rates(start_date, end_date)
    
    # Step 6: Convert to USD
    usd_trades = currency_converter.convert_to_usd(adjusted_trades, currency_rates)
    
    # Step 7: Get historical prices
    historical_prices = price_fetcher.get_split_adjusted_prices(holdings_list, splits_dict, start_date, end_date)
    
    # Step 8: Calculate portfolio values
    portfolio_values, daily_quantities = portfolio_manager.compute_daily_portfolio_value(usd_trades, historical_prices, holdings_list)
    
    # Step 9: Calculate XIRR
    xirr_results = xirr_calculator.calculate_xirr_by_holding(usd_trades, portfolio_values)
    
    # Store processed data
    processed_data = {
        'trades_df': usd_trades,
        'holdings_list': holdings_list,
        'splits_dict': splits_dict,
        'historical_prices': historical_prices,
        'portfolio_values': portfolio_values,
        'daily_quantities': daily_quantities,
        'xirr_results': xirr_results
    }
    
    return True

@app.route('/')
def index():
    """Main dashboard page"""
    if not processed_data:
        if not load_portfolio_data():
            return render_template('error.html', message="Failed to load portfolio data")
    
    # Get current holdings
    current_holdings = portfolio_manager.get_current_holdings(
        processed_data['daily_quantities'], 
        processed_data['historical_prices'], 
        processed_data['holdings_list']
    )
    
    # Calculate summary metrics
    current_value = processed_data['portfolio_values']['Total_Portfolio_Value_USD'].iloc[-1]
    total_invested = portfolio_manager.calculate_total_investment(processed_data['trades_df'])
    
    # Total sales
    total_sales = processed_data['trades_df'][processed_data['trades_df']['Total_Cashflow_USD'] > 0]['Total_Cashflow_USD'].sum()
    
    # Total P/L and return percentage
    total_pnl = current_value + total_sales - total_invested
    total_return_pct = (total_pnl / total_invested * 100) if total_invested > 0 else 0
    
    summary = {
        'current_value': current_value,
        'total_invested': total_invested,
        'total_pnl': total_pnl,
        'total_return_pct': total_return_pct,
        'num_holdings': len(current_holdings)
    }
    
    return render_template('index.html', holdings=current_holdings, summary=summary)

@app.route('/api/portfolio-chart')
def portfolio_chart():
    """API endpoint for portfolio value chart data"""
    if not processed_data:
        return jsonify({'error': 'No data available'})
    
    portfolio_values = processed_data['portfolio_values']['Total_Portfolio_Value_USD']
    
    chart_data = {
        'dates': [date.strftime('%Y-%m-%d') for date in portfolio_values.index],
        'values': portfolio_values.tolist()
    }
    
    return jsonify(chart_data)

@app.route('/api/xirr')
def xirr_data():
    """API endpoint for XIRR data"""
    if not processed_data:
        return jsonify({'error': 'No data available'})
    
    xirr_list = []
    for symbol, xirr in processed_data['xirr_results'].items():
        xirr_list.append({
            'symbol': symbol,
            'xirr': f"{xirr*100:.2f}%" if xirr is not None else "N/A",
            'xirr_value': xirr if xirr is not None else 0
        })
    
    return jsonify(sorted(xirr_list, key=lambda x: x['symbol']))

@app.route('/api/news/<symbol>')
def get_news(symbol):
    """API endpoint for getting news for a specific symbol"""
    if not processed_data:
        return jsonify({'error': 'No data available'})
    
    # Find currency for the symbol
    currency = 'USD'  # default
    for sym, curr in processed_data['holdings_list']:
        if sym == symbol:
            currency = curr
            break
    
    news = news_fetcher.get_news_google_rss(symbol, currency)
    return jsonify({'news': news})

@app.route('/data-tables')
def data_tables():
    """Data tables page"""
    if not processed_data:
        return render_template('error.html', message="No data available")
    
    # Prepare data for display
    trades_sample = processed_data['trades_df'].head(50).to_dict('records')
    
    splits_data = []
    for symbol, splits_df in processed_data['splits_dict'].items():
        for _, row in splits_df.iterrows():
            splits_data.append({
                'Symbol': symbol,
                'Split Date': row['Split_Date'].date(),
                'Split Ratio': row['Split_Ratio']
            })
    
    return render_template('data_tables.html', trades=trades_sample, splits=splits_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)