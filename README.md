# Portfolio Analyzer

A comprehensive portfolio analysis system that processes stock trading data from CSV files and computes portfolio returns with advanced analytics.

## Features

### 🎯 Core Functionality
- **Data Processing**: Load and consolidate trading data from multiple CSV files
- **Multi-Currency Support**: Handle USD, SGD, and INR with automatic exchange rate conversion
- **Stock Split Adjustments**: Automatic detection and adjustment for stock splits
- **Portfolio Valuation**: Real-time portfolio value calculation across currencies
- **XIRR Calculations**: Extended Internal Rate of Return for each holding
- **News Integration**: Latest news fetching via Google RSS

### 🌐 Dual Web Interfaces
- **Flask Web App**: Modern responsive interface with Bootstrap
- **Streamlit Dashboard**: Interactive analytics dashboard

### 📊 Current Portfolio Stats
- **522 trades** processed across **18 symbols**
- **Total Investment**: $2,511,325.42 
- **Active Holdings**: 16 positions
- **Currencies**: USD, SGD support with automatic conversion

## 🏗️ Architecture

### Modular Design
```
portfolio-analyzer/
├── app.py                 # Streamlit application (refactored)
├── flask_app.py          # Flask web application
├── data_processor.py     # CSV parsing and data management
├── portfolio.py          # Portfolio calculations and holdings
├── split_adjuster.py     # Stock split handling
├── currency_converter.py # Multi-currency support
├── price_fetcher.py      # Historical price data fetching
├── xirr_calculator.py    # XIRR computations
├── news_fetcher.py       # News API integration
├── templates/            # Flask HTML templates
│   ├── index.html        # Main dashboard
│   ├── data_tables.html  # Data exploration
│   └── error.html        # Error handling
├── static/               # CSS and JavaScript
│   ├── css/style.css     # Custom styling
│   └── js/app.js         # Interactive features
├── data/                 # CSV data files
│   ├── Stock_trading_2023.csv
│   ├── Stock_trading_2024.csv
│   └── Stock_trading_2025.csv
└── requirements.txt      # Python dependencies
```

## 🚀 Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Run Flask Web App
```bash
python flask_app.py
```
Visit http://localhost:5000

### Run Streamlit Dashboard  
```bash
streamlit run app.py
```
Visit http://localhost:8501

## 📈 Data Flow

1. **Load CSV Files** → Parse trading data with proper data types
2. **Extract Holdings** → Create master list of unique symbols
3. **Fetch Split Data** → Get stock split information from Yahoo Finance
4. **Apply Adjustments** → Adjust historical prices and quantities
5. **Currency Conversion** → Convert all values to USD using exchange rates
6. **Portfolio Calculation** → Compute daily portfolio values
7. **XIRR Analysis** → Calculate returns for each holding
8. **Web Dashboard** → Display results in interactive interface

## 🔧 Key Components

### DataProcessor
- CSV file loading and consolidation
- Data cleaning and validation
- Holdings list generation

### SplitAdjuster  
- Yahoo Finance split data fetching
- Iterative split adjustments
- Price and quantity recalculation

### CurrencyConverter
- Multi-currency exchange rate fetching
- USD conversion for all transactions
- Historical rate management

### Portfolio
- Daily portfolio value computation
- Current holdings analysis
- Investment total calculations

### XIRRCalculator
- Extended Internal Rate of Return
- Cashflow analysis per holding
- Performance validation

## 📊 Web Interface Features

### Flask Dashboard
- **Responsive Design**: Bootstrap-based modern UI
- **Interactive Charts**: Portfolio value over time
- **Holdings Table**: Current positions with valuations
- **XIRR Analysis**: Performance metrics by symbol
- **News Feed**: Latest news for selected holdings
- **Data Tables**: Raw data exploration

### Streamlit Dashboard
- **Real-time Updates**: Cached data processing
- **Interactive Widgets**: Symbol selection and filtering
- **Visualizations**: Charts and graphs
- **Data Export**: Download processed data

## 🛠️ Technical Stack

- **Backend**: Python with Pandas for data processing
- **APIs**: Yahoo Finance for stock data and splits
- **Web Frameworks**: Flask + Bootstrap, Streamlit
- **Visualization**: Chart.js, Plotly
- **Data**: CSV files with trade history

## 📝 Usage Examples

### Load and Analyze Data
```python
from data_processor import DataProcessor
from portfolio import Portfolio

# Initialize components
data_processor = DataProcessor("data")
portfolio_manager = Portfolio()

# Load trading data
files = ['Stock_trading_2023.csv', 'Stock_trading_2024.csv', 'Stock_trading_2025.csv']
trades_df = data_processor.load_and_consolidate_data(files)

# Get holdings
holdings_list = data_processor.create_master_holdings_list(trades_df)
print(f"Portfolio contains {len(holdings_list)} unique symbols")
```

### Calculate Portfolio Metrics
```python
# Calculate total investment
total_invested = portfolio_manager.calculate_total_investment(trades_df)
print(f"Total Investment: ${total_invested:,.2f}")

# Get current holdings
current_holdings = portfolio_manager.get_current_holdings(
    daily_quantities, historical_prices, holdings_list
)
```

## 🔄 Data Format

Expected CSV format:
```csv
Trades,Header,DataDiscriminator,Asset Category,Currency,Symbol,Date/Time,Quantity,T. Price,C. Price,Proceeds,Comm/Fee,Basis,Realized P/L,MTM P/L,Code
Trades,Data,Order,Stocks,USD,AAPL,"2023-07-21, 13:57:21",50,130.478,130,-6523.9,-1.078,6524.978,0,-23.9,O
```

## 🔧 Configuration

### Environment Variables
- `BASE_CURRENCY`: Default currency (default: USD)
- `DATA_DIR`: Directory containing CSV files (default: data)

### Customization
- Modify `FILES` list in applications to add more CSV files
- Update currency pairs in `CurrencyConverter` for additional currencies
- Extend `NewsFetcher` for different news sources

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following the modular architecture
4. Test both Flask and Streamlit interfaces
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.