# Portfolio Performance Analyzer

A comprehensive portfolio analysis application that processes stock trading data from CSV files and computes portfolio returns, values, and performance metrics.

![Portfolio Analyzer UI](https://github.com/user-attachments/assets/dc094c20-cdb7-43f1-ad15-9ade72fd0798)

## Features

### Core Functionality
- **📊 Data Processing**: Loads and consolidates multiple CSV trading files
- **🏢 Multi-Currency Support**: Handles USD, SGD, and INR currencies with automatic conversion
- **📈 Stock Split Handling**: Automatically adjusts prices and quantities for stock splits
- **💰 Portfolio Valuation**: Calculates daily portfolio values and performance metrics
- **🎯 XIRR Analysis**: Computes Extended Internal Rate of Return for each holding
- **📰 News Integration**: Fetches latest news for portfolio holdings
- **📤 Data Export**: Export portfolio data in CSV format

### Technical Features
- **Real-time Price Data**: Integration with Yahoo Finance for historical and current prices
- **Robust Error Handling**: Graceful fallbacks when external APIs are unavailable
- **Caching**: Efficient data caching to improve performance
- **Interactive UI**: Modern Streamlit interface with multiple views and tabs

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ayushhCreator/Portfolio-Analyzer.git
cd Portfolio-Analyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Usage

### Data Format
The application expects CSV files with the following structure:
- `Symbol`: Stock symbol (e.g., AAPL, NVDA)
- `Date/Time`: Transaction date and time
- `Quantity`: Number of shares bought/sold
- `T. Price`: Transaction price per share
- `Currency`: Currency of the transaction (USD, SGD, INR)
- `Comm/Fee`: Commission and fees

### Sample Data Files
The repository includes sample data files:
- `Stock_trading_2023.csv`
- `Stock_trading_2024.csv`
- `Stock_trading_2025.csv`

### Key Metrics

#### Portfolio Performance
- **Current Value**: Total current market value of all holdings
- **Total Invested**: Total capital deployed (purchase cashflows)
- **Total Return %**: Overall portfolio return percentage

#### Holdings Analysis
- **Current Quantity**: Number of shares currently held
- **Current Price (USD)**: Latest price converted to USD
- **Current Value (USD)**: Market value of holding in USD

#### XIRR Analysis
Extended Internal Rate of Return calculated for each holding, representing annualized returns accounting for the timing of cashflows.

## Architecture

### Data Processing Pipeline

1. **Data Loading (`load_and_consolidate_data`)**
   - Reads multiple CSV files
   - Consolidates data with source tracking
   - Cleans and validates numeric columns

2. **Holdings Management (`create_master_holdings_list`)**
   - Creates unique list of all holdings
   - Tracks currency for each symbol

3. **Split Adjustments (`get_stock_splits`, `apply_split_adjustments`)**
   - Fetches split data from Yahoo Finance
   - Applies split adjustments chronologically
   - Adjusts both prices and quantities

4. **Currency Conversion (`get_currency_rates`, `convert_to_usd`)**
   - Downloads historical exchange rates
   - Converts all transactions to USD base
   - Handles missing data with forward/backward fill

5. **Price Data (`get_split_adjusted_prices`)**
   - Downloads historical price data
   - Applies split adjustments to price history
   - Handles multiple currencies and symbols

6. **Portfolio Calculation (`compute_daily_portfolio_value`)**
   - Calculates daily portfolio values
   - Tracks quantity changes over time
   - Aggregates across all holdings

7. **XIRR Calculation (`calculate_xirr_by_holding`)**
   - Computes annualized returns per holding
   - Accounts for cashflow timing
   - Handles open and closed positions

### Error Handling

The application includes robust error handling for:
- **Network Issues**: Fallback to approximate exchange rates and default prices
- **Missing Data**: Forward/backward fill for price gaps
- **Invalid Data**: Data cleaning and validation
- **API Limitations**: Graceful degradation when external services are unavailable

## Testing

Run the test suite to validate core functionality:

```bash
python test_portfolio.py
```

The test suite covers:
- Data loading and consolidation
- Holdings list generation
- Split adjustment calculations
- Currency conversion logic
- Portfolio value calculations

## Data Export

The application provides multiple export options:

1. **Holdings Summary**: Current portfolio holdings with values
2. **Portfolio Values**: Historical daily portfolio values
3. **XIRR Analysis**: Annualized returns by holding

All exports are available in CSV format for further analysis in Excel or other tools.

## Configuration

### Supported Currencies
- USD (US Dollar) - Base currency
- SGD (Singapore Dollar)
- INR (Indian Rupee)

### Supported Data Sources
- Yahoo Finance (primary)
- Fallback to approximate rates when unavailable

## Limitations

- Requires internet connection for real-time price data
- Limited to Yahoo Finance supported symbols
- Currency conversion uses approximate rates as fallback
- Historical data availability depends on Yahoo Finance

## Contributing

1. Fork the repository
2. Create a feature branch
3. Run tests to ensure functionality
4. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues or questions:
1. Check the existing issues in the repository
2. Run the test suite to validate your environment
3. Create a new issue with detailed information about the problem

---

**Note**: This application is for educational and personal use. Always verify financial calculations independently before making investment decisions.