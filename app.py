import pandas as pd
import streamlit as st
import yfinance as yf
import numpy_financial as npf
import numpy as np
from datetime import datetime, timedelta
import warnings
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import re


warnings.filterwarnings('ignore')



# --- CONFIGURATION ---
BASE_CURRENCY = "USD"
FILES = ['Stock_trading_2023.csv', 'Stock_trading_2024.csv', 'Stock_trading_2025.csv']

# --- 1. DATA LOADING & CLEANING ---
@st.cache_data
def load_and_consolidate_data(files):
    """Step 1: Create a simple data structure to append and store the files."""
    all_trades = []
    for file in files:
        try:
            df = pd.read_csv(file, thousands=',', on_bad_lines='skip')
            if not df.empty:
                df['source_file'] = file
                all_trades.append(df)
        except FileNotFoundError:
            st.error(f"Error: The file {file} was not found.")
            continue
    
    if not all_trades:
        return pd.DataFrame()
        
    # Consolidate all data
    consolidated_df = pd.concat(all_trades, ignore_index=True)
    consolidated_df = consolidated_df[consolidated_df['Header'] == 'Data'].copy()
    consolidated_df['Date/Time'] = pd.to_datetime(consolidated_df['Date/Time'])
    
    # Clean numeric columns
    numeric_cols = ['Quantity', 'T. Price', 'C. Price', 'Proceeds', 'Comm/Fee', 'Basis', 'Realized P/L', 'MTM P/L']
    for col in numeric_cols:
        consolidated_df[col] = pd.to_numeric(consolidated_df[col], errors='coerce')
    
    # Clean and sort
    consolidated_df.dropna(subset=['Quantity', 'T. Price', 'Date/Time'], inplace=True)
    consolidated_df.sort_values('Date/Time', inplace=True)
    consolidated_df.rename(columns={'T. Price': 'Trade_Price', 'Date/Time': 'Trade_Date'}, inplace=True)
    
    return consolidated_df

# --- 2. MASTER HOLDINGS LIST ---
@st.cache_data
def create_master_holdings_list(_df):
    """Step 2: Create a master list of holdings"""
    if _df.empty:
        return []
    
    holdings = _df[['Symbol', 'Currency']].drop_duplicates()
    holdings_list = [(row['Symbol'], row['Currency']) for _, row in holdings.iterrows()]
    return holdings_list

# --- 3. STOCK SPLIT DETAILS ---
@st.cache_data
def get_stock_splits(holdings_list):
    """Step 3: Get stock split details for all holdings"""
    all_splits = {}
    
    for symbol, currency in holdings_list:
        yf_symbol = f"{symbol}.SI" if currency == 'SGD' else symbol
        try:
            ticker = yf.Ticker(yf_symbol)
            splits = ticker.splits
            if not splits.empty:
                # Convert to DataFrame for easier handling
                split_df = splits.reset_index()
                split_df.columns = ['Split_Date', 'Split_Ratio']
                split_df['Split_Date'] = pd.to_datetime(split_df['Split_Date']).dt.tz_localize(None)
                split_df = split_df.sort_values('Split_Date')
                all_splits[symbol] = split_df
        except Exception:
            continue
    
    return all_splits

# --- 4. SPLIT ADJUSTMENT ---
@st.cache_data
def apply_split_adjustments(_trades_df, _splits_dict):
    """Step 4: Transform input files to reflect split adjusted price and quantity"""
    df = _trades_df.copy()
    
    for symbol, splits_df in _splits_dict.items():
        symbol_mask = df['Symbol'] == symbol
        symbol_trades = df[symbol_mask].copy()
        
        if symbol_trades.empty:
            continue
        
        # Apply splits iteratively based on split date
        for _, split_row in splits_df.iterrows():
            split_date = split_row['Split_Date']
            split_ratio = split_row['Split_Ratio']
            
            # Find trades before this split date
            pre_split_mask = (df['Symbol'] == symbol) & (df['Trade_Date'] < split_date)
            
            if pre_split_mask.any():
                # If split is 1:2 (ratio = 2), quantity doubles, price halves
                df.loc[pre_split_mask, 'Quantity'] *= split_ratio
                df.loc[pre_split_mask, 'Trade_Price'] /= split_ratio
    
    # Recalculate adjusted cashflow
    df['Adjusted_Cashflow_Local'] = df['Quantity'] * df['Trade_Price'] * -1
    df['Comm_Fee'] = df['Comm/Fee'].fillna(0)
    df['Total_Cashflow_Local'] = df['Adjusted_Cashflow_Local'] - df['Comm_Fee']
    
    return df

# --- 5. CURRENCY EXCHANGE RATES ---
@st.cache_data
def get_currency_rates(start_date, end_date):
    """Step 5: Get historical daily currency pairing for each date (USD, INR, SGD)"""
    try:
        # Download currency rates
        currency_pairs = ['SGDUSD=X', 'INRUSD=X']  # USD is base
        
        rates = yf.download(currency_pairs, start=start_date, end=end_date, progress=False)['Close']
        
        # Handle single currency case
        if len(currency_pairs) == 1:
            rates = rates.to_frame(currency_pairs[0])
        
        # Create full date range and forward fill
        full_dates = pd.date_range(start=start_date, end=end_date, freq='D')
        rates = rates.reindex(full_dates)
        rates = rates.fillna(method='ffill').fillna(method='bfill')
        
        # Add USD rate (always 1)
        rates['USDUSD=X'] = 1.0
        
        return rates
        
    except Exception as e:
        st.warning(f"Unable to fetch live currency data: {str(e)[:100]}...")
        st.info("Using approximate currency rates.")
        
        # Create fallback currency rates
        full_dates = pd.date_range(start=start_date, end=end_date, freq='D')
        rates = pd.DataFrame(index=full_dates)
        
        # Use approximate exchange rates
        rates['SGDUSD=X'] = 0.74  # Approximate SGD to USD rate
        rates['INRUSD=X'] = 0.012  # Approximate INR to USD rate 
        rates['USDUSD=X'] = 1.0
        
        return rates

# --- 6. CURRENCY CONVERSION ---
def convert_to_usd(_trades_df, _currency_rates):
    """Step 6: Compute transaction price in each currency (convert to USD)"""
    df = _trades_df.copy()
    
    # Map currency rates to trade dates
    df['Trade_Date_Key'] = df['Trade_Date'].dt.floor('D')
    
    def get_usd_rate(row):
        date_key = row['Trade_Date_Key']
        currency = row['Currency']
        
        if currency == 'USD':
            return 1.0
        elif currency == 'SGD':
            return _currency_rates.loc[date_key, 'SGDUSD=X'] if date_key in _currency_rates.index else 0.74
        elif currency == 'INR':
            return _currency_rates.loc[date_key, 'INRUSD=X'] if date_key in _currency_rates.index else 0.012
        else:
            return 1.0  # Default to USD
    
    df['USD_Exchange_Rate'] = df.apply(get_usd_rate, axis=1)
    df['Trade_Price_USD'] = df['Trade_Price'] * df['USD_Exchange_Rate']
    df['Total_Cashflow_USD'] = df['Total_Cashflow_Local'] * df['USD_Exchange_Rate']
    
    return df

# --- 7. HISTORICAL PRICES ---
@st.cache_data
def get_split_adjusted_prices(holdings_list, splits_dict, start_date, end_date):
    """Step 7: Get split adjusted historical prices/NAVs through yahoo finance"""
    
    # Create symbol mapping
    yf_symbols = []
    symbol_map = {}
    
    for symbol, currency in holdings_list:
        yf_symbol = f"{symbol}.SI" if currency == 'SGD' else symbol
        yf_symbols.append(yf_symbol)
        symbol_map[yf_symbol] = symbol
    
    # Add currency rates
    yf_symbols.extend(['SGDUSD=X', 'INRUSD=X'])
    
    # Download prices with better error handling
    try:
        prices = yf.download(yf_symbols, start=start_date, end=end_date, progress=False, auto_adjust=False)['Close']
        
        if len(yf_symbols) == 1:
            prices = prices.to_frame(yf_symbols[0])
            
    except Exception as e:
        st.warning(f"Unable to fetch live price data from Yahoo Finance: {str(e)[:100]}...")
        st.info("Using fallback price data. Some calculations may be limited.")
        
        # Create fallback prices using trade prices as estimates
        full_dates = pd.date_range(start=start_date, end=end_date, freq='D')
        prices = pd.DataFrame(index=full_dates)
        
        # Add default currency rates
        prices['SGDUSD=X'] = 0.74  # Approximate SGD to USD rate
        prices['INRUSD=X'] = 0.012  # Approximate INR to USD rate
        
        # For each symbol, try to get at least some historical data or use trade prices
        for symbol, currency in holdings_list:
            yf_symbol = f"{symbol}.SI" if currency == 'SGD' else symbol
            try:
                # Try to get at least some recent data
                recent_data = yf.download(yf_symbol, period="5d", progress=False)
                if not recent_data.empty:
                    last_price = recent_data['Close'].iloc[-1]
                    prices[symbol] = last_price
                else:
                    # Use a default price if no data available
                    prices[symbol] = 100.0  # Default fallback price
            except:
                # Use default price if all else fails
                prices[symbol] = 100.0  # Default fallback price
        
        return prices
    
    # Create full date range
    full_dates = pd.date_range(start=start_date, end=end_date, freq='D')
    prices = prices.reindex(full_dates)
    
    # Apply manual split adjustments to prices (reverse chronological order)
    for yf_symbol, orig_symbol in symbol_map.items():
        if orig_symbol in splits_dict:
            splits_df = splits_dict[orig_symbol]
            
            for _, split_row in splits_df.sort_values('Split_Date', ascending=False).iterrows():
                split_date = split_row['Split_Date']
                split_ratio = split_row['Split_Ratio']
                
                # Adjust prices before split date
                pre_split_mask = prices.index < split_date
                if pre_split_mask.any() and yf_symbol in prices.columns:
                    prices.loc[pre_split_mask, yf_symbol] /= split_ratio
    
    # Forward fill missing values (weekends, holidays)
    prices = prices.replace(0, pd.NA)
    prices = prices.fillna(method='ffill').fillna(method='bfill')
    
    # Rename columns back to original symbols
    prices.rename(columns=symbol_map, inplace=True)
    
    return prices

# --- 8. DAILY PORTFOLIO VALUE ---
@st.cache_data
def compute_daily_portfolio_value(_trades_df, _prices_df, holdings_list):
    """Step 8: Compute daily portfolio value across currencies"""
    
    # Calculate cumulative quantities for each symbol
    daily_quantities = _trades_df.pivot_table(
        index='Trade_Date', 
        columns='Symbol', 
        values='Quantity', 
        aggfunc='sum'
    ).fillna(0).cumsum()
    
    # Extend to full date range
    full_dates = _prices_df.index
    daily_quantities = daily_quantities.reindex(full_dates, method='ffill').fillna(0)
    
    # Calculate daily values in USD
    portfolio_values = pd.DataFrame(index=full_dates)
    
    for symbol, currency in holdings_list:
        if symbol in _prices_df.columns and symbol in daily_quantities.columns:
            prices_usd = _prices_df[symbol].copy()
            
            # Convert SGD and INR prices to USD
            if currency == 'SGD':
                prices_usd = prices_usd * _prices_df['SGDUSD=X']
            elif currency == 'INR':
                prices_usd = prices_usd * _prices_df['INRUSD=X']
            
            portfolio_values[symbol] = daily_quantities[symbol] * prices_usd
    
    # Calculate total portfolio value
    portfolio_values['Total_Portfolio_Value_USD'] = portfolio_values.sum(axis=1)
    
    return portfolio_values, daily_quantities

# --- 9. XIRR CALCULATION (CORRECTED) ---
@st.cache_data
def calculate_xirr_by_holding(_trades_df, _portfolio_values):
    """Compute XIRR for each holding: buy = negative, sell = positive, add current value if holding exists."""
    xirr_results = {}
    last_date = _portfolio_values.index[-1]

    for symbol in _trades_df['Symbol'].unique():
        symbol_trades = _trades_df[_trades_df['Symbol'] == symbol].copy()
        if symbol_trades.empty:
            xirr_results[symbol] = None
            continue

        # Chronological order
        symbol_trades.sort_values(by='Trade_Date', inplace=True)

        # Prepare cashflows
        cashflows = symbol_trades['Total_Cashflow_USD'].tolist()
        dates = symbol_trades['Trade_Date'].tolist()

        # Current holding value
        current_quantity = symbol_trades['Quantity'].sum()
        current_value = _portfolio_values[symbol].iloc[-1] if symbol in _portfolio_values.columns else 0

        # If still holding shares, add current market value as last positive cashflow
        # If position is closed (all sold), do not add
        if abs(current_quantity) > 1e-6:
            cashflows.append(current_value)
            dates.append(last_date)

        # XIRR requires at least one positive and one negative cashflow
        if len(cashflows) >= 2 and any(cf > 0 for cf in cashflows) and any(cf < 0 for cf in cashflows):
            try:
                # Use .date() for each date for npf.xirr
                date_objects = [d.date() for d in dates]
                xirr_value = npf.xirr(cashflows, date_objects)
                # Filter out extreme values
                if pd.notna(xirr_value) and abs(xirr_value) < 10:
                    xirr_results[symbol] = xirr_value
                else:
                    xirr_results[symbol] = None
            except Exception as e:
                xirr_results[symbol] = None
        else:
            xirr_results[symbol] = None

    return xirr_results


# --- NEWS FUNCTION ---
@st.cache_data(ttl=3600)
def get_news_google_rss(symbol, currency):
    """Get news using Google News RSS (no API key needed, no feedparser required)"""
    try:
        # Get company name for better search
        yf_symbol = f"{symbol}.SI" if currency == 'SGD' else symbol
        try:
            ticker = yf.Ticker(yf_symbol)
            info = ticker.info
            company_name = info.get('longName', '') or info.get('shortName', '') or symbol
        except:
            company_name = symbol

        # Google News RSS URL
        search_query = urllib.parse.quote(f"{symbol} {company_name} stock")
        rss_url = f"https://news.google.com/rss/search?q={search_query}&hl=en-US&gl=US&ceid=US:en"

        # Fetch RSS feed
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        req = urllib.request.Request(rss_url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()

        # Parse XML
        root = ET.fromstring(xml_data)
        
        formatted_news = []
        items = root.findall('.//item')[:5]  # Get first 5 items
        
        if not items:
            return [f"No Google News found for {symbol}"]

        for item in items:
            title_elem = item.find('title')
            link_elem = item.find('link')
            pub_date_elem = item.find('pubDate')
            
            title = title_elem.text if title_elem is not None else 'No title'
            link = link_elem.text if link_elem is not None else '#'
            pub_date = pub_date_elem.text if pub_date_elem is not None else ''
            
            # Clean up title (remove source attribution if present)
            title = re.sub(r' - [^-]*$', '', title)
            
            # Format date
            if pub_date:
                try:
                    # Parse RFC 2822 date format
                    date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
                    date_str = date_obj.strftime('%m/%d')
                    title = f"{title} ({date_str})"
                except:
                    try:
                        # Alternative date format
                        date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                        date_str = date_obj.strftime('%m/%d')
                        title = f"{title} ({date_str})"
                    except:
                        pass  # Skip date formatting if parsing fails
            
            formatted_news.append(f"• [{title}]({link})")

        return formatted_news if formatted_news else [f"No news found for {symbol}"]

    except urllib.error.URLError as e:
        return [f"Network error fetching Google News: {str(e)}"]
    except ET.ParseError as e:
        return [f"Error parsing Google News RSS: {str(e)}"]
    except Exception as e:
        return [f"An error occurred fetching Google News: {str(e)}"]


# --- CORRECTED TOTAL INVESTMENT CALCULATION ---
def calculate_total_investment(trades_df):
    """
    Calculate total investment by summing all purchase cashflows (outflows).
    This represents the total capital deployed in the portfolio.
    """
    # Buy transactions are those with a negative cashflow in USD.
    buy_cashflows = trades_df[trades_df['Total_Cashflow_USD'] < 0]['Total_Cashflow_USD'].sum()
    
    # The sum will be negative, so we take the absolute value for the total investment amount.
    return abs(buy_cashflows)


# --- VALIDATION FUNCTION ---
def validate_xirr_calculation(_trades_df, _portfolio_values):
    """Simple validation to check if cashflows make sense"""
    print("\n=== XIRR Validation ===")
    
    # Check first few symbols
    test_symbols = ['NET', 'MSFT', 'AAPL', 'NVDA']
    
    for symbol in test_symbols:
        if symbol not in _trades_df['Symbol'].unique():
            continue
            
        symbol_trades = _trades_df[_trades_df['Symbol'] == symbol].copy()
        print(f"\n{symbol}:")
        print(f"  Number of trades: {len(symbol_trades)}")
        print(f"  Total quantity: {symbol_trades['Quantity'].sum()}")
        print(f"  Cashflow range: ${symbol_trades['Total_Cashflow_USD'].min():.2f} to ${symbol_trades['Total_Cashflow_USD'].max():.2f}")
        
        # Check if Total_Cashflow_USD has the right signs
        buys = symbol_trades[symbol_trades['Quantity'] > 0]
        sells = symbol_trades[symbol_trades['Quantity'] < 0]
        
        print(f"  Buy trades cashflow (should be negative): {buys['Total_Cashflow_USD'].tolist()}")
        print(f"  Sell trades cashflow (should be positive): {sells['Total_Cashflow_USD'].tolist()}")


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
    
    current_holdings = []
    total_value = 0
    
    for symbol, currency in holdings_list:
        current_qty = daily_quantities[symbol].iloc[-1] if symbol in daily_quantities.columns else 0
        
        if symbol in historical_prices.columns:
            current_price_local = historical_prices[symbol].iloc[-1]
            
            # Convert to USD
            if currency == 'SGD':
                current_price_usd = current_price_local * historical_prices['SGDUSD=X'].iloc[-1]
            elif currency == 'INR':
                current_price_usd = current_price_local * historical_prices['INRUSD=X'].iloc[-1]
            else:
                current_price_usd = current_price_local
                
            current_value = current_qty * current_price_usd
            total_value += current_value
            
            if abs(current_qty) > 0.001: # Only display if holding quantity is meaningful
                current_holdings.append({
                    'Symbol': symbol,
                    'Current Quantity': current_qty,
                    'Current Price (USD)': current_price_usd if pd.notna(current_price_usd) else 0.0,
                    'Current Value (USD)': current_value if pd.notna(current_value) else 0.0
                })
        else:
            # Handle case where price data is not available
            if abs(current_qty) > 0.001:
                current_holdings.append({
                    'Symbol': symbol,
                    'Current Quantity': current_qty,
                    'Current Price (USD)': 0.0,  # Price not available
                    'Current Value (USD)': 0.0   # Value not available
                })
    
    # Sort by value and display
    if current_holdings:
        holdings_df = pd.DataFrame(current_holdings)
        holdings_df = holdings_df.sort_values('Current Value (USD)', ascending=False)
        
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
        
        # Add note if prices are unavailable
        if total_value == 0 and len(current_holdings) > 0:
            st.info("💡 Current prices may be unavailable due to network restrictions. Portfolio calculations use last available data.")
    else:
        st.info("No current holdings found.")
    
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
    tab1, tab2, tab3, tab4 = st.tabs(["📊 XIRR Analysis", "📰 News", "🗂️ Data Tables", "📤 Export Data"])
    
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
                
    with tab4:
        st.subheader("Export Portfolio Data")
        st.write("Download your portfolio analysis data in various formats:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📁 Export Holdings Summary"):
                if current_holdings:
                    holdings_df = pd.DataFrame(current_holdings)
                    csv = holdings_df.to_csv(index=False)
                    st.download_button(
                        label="Download Holdings CSV",
                        data=csv,
                        file_name=f"portfolio_holdings_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                
        with col2:
            if st.button("📈 Export Portfolio Values"):
                csv = portfolio_values.to_csv()
                st.download_button(
                    label="Download Portfolio Values CSV",
                    data=csv,
                    file_name=f"portfolio_values_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
                
        with col3:
            if st.button("💰 Export XIRR Analysis"):
                if xirr_results:
                    xirr_df = pd.DataFrame([
                        {'Symbol': symbol, 'XIRR': xirr if xirr is not None else None}
                        for symbol, xirr in xirr_results.items()
                    ])
                    csv = xirr_df.to_csv(index=False)
                    st.download_button(
                        label="Download XIRR CSV",
                        data=csv,
                        file_name=f"portfolio_xirr_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )

if __name__ == "__main__":
    main()
