import pandas as pd
import streamlit as st
import warnings
from datetime import datetime

from data_processor import DataProcessor
from split_adjuster import SplitAdjuster
from currency_converter import CurrencyConverter
from price_fetcher import PriceFetcher
from portfolio import Portfolio
from xirr_calculator import XIRRCalculator
from news_fetcher import NewsFetcher

warnings.filterwarnings('ignore')

# --- CONFIGURATION ---
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

# --- 1. DATA LOADING & CLEANING ---
@st.cache_data
def load_and_consolidate_data(files):
    """Step 1: Create a simple data structure to append and store the files."""
    return data_processor.load_and_consolidate_data(files)

# --- 2. MASTER HOLDINGS LIST ---
@st.cache_data
def create_master_holdings_list(_df):
    """Step 2: Create a master list of holdings"""
    return data_processor.create_master_holdings_list(_df)

# --- 3. STOCK SPLIT DETAILS ---
@st.cache_data
def get_stock_splits(holdings_list):
    """Step 3: Get stock split details for all holdings"""
    return split_adjuster.get_stock_splits(holdings_list)

# --- 4. SPLIT ADJUSTMENT ---
@st.cache_data
def apply_split_adjustments(_trades_df, _splits_dict):
    """Step 4: Transform input files to reflect split adjusted price and quantity"""
    return split_adjuster.apply_split_adjustments(_trades_df, _splits_dict)

# --- 5. CURRENCY EXCHANGE RATES ---
@st.cache_data
def get_currency_rates(start_date, end_date):
    """Step 5: Get historical daily currency pairing for each date (USD, INR, SGD)"""
    return currency_converter.get_currency_rates(start_date, end_date)

# --- 6. CURRENCY CONVERSION ---
def convert_to_usd(_trades_df, _currency_rates):
    """Step 6: Compute transaction price in each currency (convert to USD)"""
    return currency_converter.convert_to_usd(_trades_df, _currency_rates)

# --- 7. HISTORICAL PRICES ---
@st.cache_data
def get_split_adjusted_prices(holdings_list, splits_dict, start_date, end_date):
    """Step 7: Get split adjusted historical prices/NAVs through yahoo finance"""
    return price_fetcher.get_split_adjusted_prices(holdings_list, splits_dict, start_date, end_date)

# --- 8. DAILY PORTFOLIO VALUE ---
@st.cache_data
def compute_daily_portfolio_value(_trades_df, _prices_df, holdings_list):
    """Step 8: Compute daily portfolio value across currencies"""
    return portfolio_manager.compute_daily_portfolio_value(_trades_df, _prices_df, holdings_list)

# --- 9. XIRR CALCULATION (CORRECTED) ---
@st.cache_data
def calculate_xirr_by_holding(_trades_df, _portfolio_values):
    """Compute XIRR for each holding: buy = negative, sell = positive, add current value if holding exists."""
    return xirr_calculator.calculate_xirr_by_holding(_trades_df, _portfolio_values)

# --- NEWS FUNCTION ---
@st.cache_data(ttl=3600)
def get_news_google_rss(symbol, currency):
    """Get news using Google News RSS (no API key needed, no feedparser required)"""
    return news_fetcher.get_news_google_rss(symbol, currency)

# --- CORRECTED TOTAL INVESTMENT CALCULATION ---
def calculate_total_investment(trades_df):
    """
    Calculate total investment by summing all purchase cashflows (outflows).
    This represents the total capital deployed in the portfolio.
    """
    return portfolio_manager.calculate_total_investment(trades_df)

# --- VALIDATION FUNCTION ---
def validate_xirr_calculation(_trades_df, _portfolio_values):
    """Simple validation to check if cashflows make sense"""
    xirr_calculator.validate_xirr_calculation(_trades_df, _portfolio_values)


# --- 10. MAIN UI ---
def main():
    """Step 10: Represent through a simple UI"""
    st.set_page_config(page_title="Portfolio Analyzer", layout="wide")
    st.title("📊 Portfolio Performance Analyzer")
    
    # Load and process data
    with st.spinner("Loading and processing data..."):
        # Step 1: Load data
        trades_df = load_and_consolidate_data(FILES)
        
        if trades_df.empty:
            st.error("No valid trade data found!")
            return
        
        # Step 2: Create master holdings
        holdings_list = create_master_holdings_list(trades_df)
        
        # Step 3: Get splits
        splits_dict = get_stock_splits(holdings_list)
        
        # Step 4: Apply split adjustments
        adjusted_trades = apply_split_adjustments(trades_df, splits_dict)
        
        # Date range
        start_date = adjusted_trades['Trade_Date'].min().date()
        end_date = datetime.now().date()
        
        # Step 5: Get currency rates
        currency_rates = get_currency_rates(start_date, end_date)
        
        # Step 6: Convert to USD
        usd_trades = convert_to_usd(adjusted_trades, currency_rates)

       
        # Step 7: Get historical prices
        historical_prices = get_split_adjusted_prices(holdings_list, splits_dict, start_date, end_date)
        
        # Step 8: Calculate portfolio values
        portfolio_values, daily_quantities = compute_daily_portfolio_value(usd_trades, historical_prices, holdings_list)
        
        # ADD THIS LINE FOR DEBUGGING:
        validate_xirr_calculation(usd_trades, portfolio_values)

        # Step 9: Calculate XIRR
        xirr_results = calculate_xirr_by_holding(usd_trades, portfolio_values)
    
    # Current Holdings Table
    st.header("📋 Current Holdings Summary")
    
    current_holdings = portfolio_manager.get_current_holdings(daily_quantities, historical_prices, holdings_list)
    total_value = sum(holding['Current Value (USD)'] for holding in current_holdings)
    
    # Sort by value and display
    if current_holdings:
        holdings_df = pd.DataFrame(current_holdings)
        
        # Add total row
        total_row = pd.DataFrame({
            'Symbol': ['TOTAL'],
            'Current Quantity': ['-'],
            'Current Price (USD)': ['-'],
            'Current Value (USD)': [total_value]
        })
        
        display_df = pd.concat([holdings_df, total_row], ignore_index=True)
        
        # Format and display
        st.dataframe(
            display_df.style.format({
                'Current Quantity': lambda x: f"{x:,.4f}" if isinstance(x, (int, float)) else x,
                'Current Price (USD)': lambda x: f"${x:,.2f}" if isinstance(x, (int, float)) else x,
                'Current Value (USD)': "${:,.2f}"
            }),
            use_container_width=True
        )
    
    # Portfolio Overview
    st.header("📈 Portfolio Performance")

    col1, col2, col3 = st.columns(3)

    current_value = portfolio_values['Total_Portfolio_Value_USD'].iloc[-1]
    # CORRECTED: Use the new function for a clearer "Total Invested" metric
    total_invested = calculate_total_investment(usd_trades)
    
    # To calculate total return, we need to account for sales
    total_sales = usd_trades[usd_trades['Total_Cashflow_USD'] > 0]['Total_Cashflow_USD'].sum()
    
    # Total P/L = Current Value + Cash from Sales - Total Investment
    total_pnl = current_value + total_sales - total_invested
    total_return_pct = (total_pnl / total_invested * 100) if total_invested > 0 else 0

    col1.metric("Current Value", f"${current_value:,.2f}")
    col2.metric("Total Invested", f"${total_invested:,.2f}")
    col3.metric("Total Return %", f"{total_return_pct:.2f}%", help="Return is calculated as (Current Value + Total Sales - Total Invested) / Total Invested.")
    
    # Portfolio Value Chart
    st.subheader("Portfolio Value Over Time")
    st.line_chart(portfolio_values['Total_Portfolio_Value_USD'])
    
    # Tabs for detailed views
    tab1, tab2, tab3 = st.tabs(["📊 XIRR Analysis", "📰 News", "🗂️ Data Tables"])
    
    with tab1:
        st.subheader("XIRR by Holding (Annualized Return)")
        if xirr_results:
            xirr_df = pd.DataFrame([
                {'Symbol': symbol, 'XIRR': f"{xirr*100:.2f}%" if xirr is not None else "N/A"}
                for symbol, xirr in xirr_results.items()
            ])
            st.dataframe(xirr_df.sort_values(by='Symbol'), use_container_width=True)
        else:
            st.info("Could not calculate XIRR for any holdings.")
    
    with tab2:
        st.subheader("Latest News")
        if holdings_list:
            selected_symbol = st.selectbox("Select symbol for news:", [symbol for symbol, _ in holdings_list])
            if selected_symbol:
                selected_currency = next(currency for symbol, currency in holdings_list if symbol == selected_symbol)
                
                with st.spinner(f"Fetching news for {selected_symbol}..."):
                    news = get_news_google_rss(selected_symbol, selected_currency)
                
                if news:
                    for item in news:
                        st.markdown(item, unsafe_allow_html=True)
                else:
                    st.info(f"No news found for {selected_symbol}")
        else:
            st.info("No holdings to select.")
 
    with tab3:
        st.subheader("Detailed Data")
        
        with st.expander("Processed & USD Converted Trades"):
            st.dataframe(usd_trades)
        
        with st.expander("Daily Portfolio Values (USD)"):
            st.dataframe(portfolio_values)
        
        with st.expander("Stock Splits Applied"):
            if splits_dict:
                split_summary = []
                for symbol, splits_df in splits_dict.items():
                    for _, row in splits_df.iterrows():
                        split_summary.append({
                            'Symbol': symbol,
                            'Split Date': row['Split_Date'].date(),
                            'Split Ratio': row['Split_Ratio']
                        })
                st.dataframe(pd.DataFrame(split_summary))
            else:
                st.info("No stock splits detected")

if __name__ == "__main__":
    main()
