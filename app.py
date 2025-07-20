import pandas as pd
import streamlit as st
import yfinance as yf
import numpy_financial as npf
from datetime import datetime
import requests

# --- CONFIGURATION ---
BASE_CURRENCY = "USD"
FILES = ['Stock_trading_2023.csv', 'Stock_trading_2024.csv', 'Stock_trading_2025.csv']
NEWS_API_KEY = "148950622340442b94d1387dea89c798" 

# --- DATA LOADING & CLEANING ---
@st.cache_data
def load_data(files):
    all_trades = []
    for file in files:
        try:
            df = pd.read_csv(file, thousands=',', on_bad_lines='skip')
            all_trades.append(df)
        except FileNotFoundError:
            st.error(f"Error: The file {file} was not found.")
            return pd.DataFrame()
    master_df = pd.concat(all_trades, ignore_index=True)
    master_df.dropna(how='all', inplace=True)
    master_df = master_df[master_df['Header'] == 'Data']
    master_df['Date/Time'] = pd.to_datetime(master_df['Date/Time'])
    numeric_cols = ['Quantity', 'T. Price', 'C. Price', 'Proceeds', 'Comm/Fee', 'Basis', 'Realized P/L', 'MTM P/L']
    for col in numeric_cols:
        master_df[col] = pd.to_numeric(master_df[col], errors='coerce')
    master_df.dropna(subset=['Quantity', 'T. Price', 'Date/Time'], inplace=True)
    master_df.sort_values(by='Date/Time', inplace=True)
    master_df.rename(columns={'T. Price': 'Trade Price', 'Date/Time': 'Date'}, inplace=True)
    return master_df

# --- CORE FUNCTIONS ---
def get_holdings(df):
    unique_holdings = df[['Symbol', 'Currency']].drop_duplicates().values.tolist()
    return unique_holdings

@st.cache_data
def adjust_for_splits(_df, holdings_list):
    return _df.copy() # Pass-through function

@st.cache_data
def get_historical_prices(holdings_list_of_pairs, start_date, end_date):
    yfinance_tickers = []
    rename_map = {}
    for symbol, currency in holdings_list_of_pairs:
        yfinance_symbol = symbol
        if currency == 'SGD':
            yfinance_symbol = f"{symbol}.SI"
        yfinance_tickers.append(yfinance_symbol)
        rename_map[yfinance_symbol] = symbol
    yfinance_tickers.append('SGDUSD=X')
    prices = yf.download(yfinance_tickers, start=start_date, end=end_date, progress=False, auto_adjust=False)['Adj Close']
    prices.ffill(inplace=True)
    prices.bfill(inplace=True)
    prices.rename(columns=rename_map, inplace=True)
    return prices

@st.cache_data
def calculate_daily_values(_trades_df, _prices_df):
    df = _trades_df.copy()
    
    usd_map = _prices_df['SGDUSD=X']
    df['Exchange Rate'] = df['Date'].dt.floor('D').map(usd_map)
    
    # --- THIS IS THE FIX ---
    # The inplace operations must be on separate lines because they return None.
    df['Exchange Rate'].bfill(inplace=True)
    df['Exchange Rate'].ffill(inplace=True)
    
    df['Trade Price (USD)'] = df.apply(
        lambda row: row['Trade Price'] * row['Exchange Rate'] if row['Currency'] == 'SGD' else row['Trade Price'],
        axis=1
    )
    df['Adjusted Cashflow (USD)'] = (df['Quantity'] * df['Trade Price (USD)'] * -1) - df['Comm/Fee'].fillna(0)

    if df['Adjusted Cashflow (USD)'].isnull().any():
        st.error("Error: NaN values created during cashflow calculation.")
        st.dataframe(df[df['Adjusted Cashflow (USD)'].isnull()])
        st.stop()

    daily_qty = df.pivot_table(index='Date', columns='Symbol', values='Quantity', aggfunc='sum').cumsum()
    daily_qty = daily_qty.reindex(_prices_df.index, method='ffill').fillna(0)
    
    original_symbols = [s for s, c in get_holdings(df)]
    aligned_prices, aligned_qty = _prices_df[original_symbols].align(daily_qty, join='left', axis=1, fill_value=0)
    daily_value = aligned_prices * aligned_qty
    daily_value['Total Portfolio Value'] = daily_value.sum(axis=1)
    
    return daily_value, df

@st.cache_data
def calculate_xirr(_trades_df, _prices_df):
    xirr_results = {}
    last_date = _prices_df.index[-1]
    holdings_list = get_holdings(_trades_df)
    
    for symbol, currency in holdings_list:
        asset_trades = _trades_df[_trades_df['Symbol'] == symbol].copy()
        current_quantity = asset_trades['Quantity'].sum()
        
        last_price = _prices_df[symbol].iloc[-1]
        
        if abs(current_quantity) > 0.001 and pd.notna(last_price):
            closing_value = current_quantity * last_price
            closing_trade = pd.DataFrame({'Date': [last_date], 'Adjusted Cashflow (USD)': [closing_value]})
            cash_flows = pd.concat([asset_trades[['Date', 'Adjusted Cashflow (USD)']], closing_trade], ignore_index=True)
        else:
            cash_flows = asset_trades[['Date', 'Adjusted Cashflow (USD)']].copy()

        cash_flows = cash_flows.dropna(subset=['Adjusted Cashflow (USD)'])
        cash_flows = cash_flows[cash_flows['Adjusted Cashflow (USD)'].abs() > 0.01]
        
        if len(cash_flows['Date'].unique()) > 1:
            try:
                xirr_value = npf.xirr(cash_flows['Adjusted Cashflow (USD)'].values, cash_flows['Date'].dt.date.values)
                xirr_results[symbol] = xirr_value if abs(xirr_value) < 10 else None
            except Exception:
                xirr_results[symbol] = None
        else:
            xirr_results[symbol] = None
    return xirr_results

@st.cache_data(ttl=3600)
def get_news(yfinance_ticker_obj):
    try:
        symbol = yfinance_ticker_obj.ticker
        long_name = yfinance_ticker_obj.info.get('longName', symbol)
        query = f'"{long_name}" OR "{symbol}"'
        
        if not NEWS_API_KEY or "YOUR_NEWS_API_KEY_HERE" in NEWS_API_KEY:
            return ["Please add a valid NewsAPI.org key to fetch news."]
        
        url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}&pageSize=5&sortBy=relevancy&language=en"
        
        r = requests.get(url)
        r.raise_for_status()
        
        data = r.json()
        articles = [f"- [{article['title']}]({article['url']}) ({article['source']['name']})" for article in data['articles']]
        
        return articles if articles else ["No recent news found."]
    except Exception as e:
        return [f"Could not fetch news. The API may be unavailable or the key may be invalid. (Error: {e})"]

# --- MAIN APP LOGIC ---
st.set_page_config(layout="wide")
st.title("Personal Portfolio Performance Analyzer")

trades_df = load_data(FILES)

if not trades_df.empty:
    holdings = get_holdings(trades_df)
    adjusted_trades_df = adjust_for_splits(trades_df, holdings)
    start_date = adjusted_trades_df['Date'].min().date()
    end_date = datetime.today().date()
    historical_prices = get_historical_prices(holdings, start_date, end_date)
    daily_portfolio_value, final_trades_df = calculate_daily_values(adjusted_trades_df, historical_prices)
    
    if not daily_portfolio_value.empty:
        xirr_values = calculate_xirr(final_trades_df, historical_prices)
        tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📈 Holdings Analysis", "🗃️ Data Explorer"])

        with tab1:
            st.header("Portfolio Overview")
            current_value = daily_portfolio_value['Total Portfolio Value'].iloc[-1]
            total_investment = final_trades_df[final_trades_df['Adjusted Cashflow (USD)'] < 0]['Adjusted Cashflow (USD)'].sum() * -1
            total_return_pct = ((current_value - total_investment) / total_investment) * 100 if total_investment > 0 else 0
            col1, col2, col3 = st.columns(3)
            col1.metric("Current Portfolio Value (USD)", f"${current_value:,.2f}")
            col2.metric("Total Investment (USD)", f"${total_investment:,.2f}")
            col3.metric("Total Return", f"{total_return_pct:.2f}%")
            
            st.header("Current Holdings")
            current_qty = final_trades_df.groupby('Symbol')['Quantity'].sum()
            current_holdings_df = pd.DataFrame(current_qty).reset_index()
            current_holdings_df = current_holdings_df[current_holdings_df['Quantity'] > 0.001]
            latest_prices = historical_prices.iloc[-1]
            current_holdings_df['Current Price'] = current_holdings_df['Symbol'].map(latest_prices)
            current_holdings_df['Current Value'] = current_holdings_df['Quantity'] * current_holdings_df['Current Price']
            total_row = pd.DataFrame({'Symbol': ['**TOTAL**'], 'Quantity': ['-'], 'Current Price': ['-'], 'Current Value': [current_holdings_df['Current Value'].sum()]})
            display_holdings_df = pd.concat([current_holdings_df, total_row], ignore_index=True)
            st.dataframe(display_holdings_df.style.format({'Current Price': '${:,.2f}', 'Current Value': '${:,.2f}'}), use_container_width=True)
            
            st.header("Daily Portfolio Value History (USD)")
            st.line_chart(daily_portfolio_value['Total Portfolio Value'])

        with tab2:
            st.header("Holdings Breakdown")
            col1, col2 = st.columns([0.6, 0.4])
            with col1:
                st.subheader("Performance per Holding (XIRR)")
                xirr_df = pd.DataFrame(list(xirr_values.items()), columns=['Symbol', 'XIRR'])
                xirr_df['XIRR'] = xirr_df['XIRR'].apply(lambda x: f"{x*100:.2f}%" if pd.notna(x) else "N/A")
                st.dataframe(xirr_df, use_container_width=True)
            with col2:
                st.subheader("Latest News")
                stock_symbols_only = [s for s, c in holdings]
                selected_stock = st.selectbox("Select a stock for news:", stock_symbols_only)
                if selected_stock:
                    selected_currency = [c for s, c in holdings if s == selected_stock][0]
                    yfinance_symbol = selected_stock + ".SI" if selected_currency == 'SGD' else selected_stock
                    ticker_obj = yf.Ticker(yfinance_symbol)
                    news_items = get_news(ticker_obj)
                    for item in news_items:
                        st.markdown(item)
        
        with tab3:
            st.header("Detailed Data Tables")
            with st.expander("Final Calculated Trades"):
                st.dataframe(final_trades_df)
            with st.expander("Daily Portfolio Value Breakdown"):
                st.dataframe(daily_portfolio_value)