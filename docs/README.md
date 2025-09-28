# 📈 Portfolio Analyzer

> **Advanced Portfolio Performance Analysis Tool with Real-Time Market Data Integration**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A comprehensive portfolio analysis web application that processes multi-year trading data, calculates advanced financial metrics including XIRR, and provides real-time market insights through an intuitive interface.

---

## 🚀 Features

### 📊 **Core Analytics (Both Versions)**
- **XIRR Calculation**: Extended Internal Rate of Return for accurate performance measurement
- **Multi-Currency Support**: Automatic conversion between USD, SGD, and INR
- **Stock Split Adjustments**: Historical position adjustments for accurate tracking
- **Real-Time Valuation**: Current portfolio value with live market data

### 🚀 **NEW: Enhanced Scalable Architecture**
- **Multi-User Support**: Switch between different user portfolios
- **Scalable Data Model**: Staging, dimension, and fact tables
- **Advanced Visualizations**: Interactive Plotly charts and graphs
- **Diversification Analysis**: Sector allocation and concentration risk metrics
- **Historical Performance**: Portfolio value tracking over customizable time periods
- **Stock Research**: Complete metadata and company information
- **Data Management**: Automated refresh monitoring and export functionality

### 📈 **Data Processing**
- **Multi-File Import**: Consolidate trading data from multiple CSV files
- **522+ Trade Records**: Process extensive trading history (2023-2025)
- **18 Stock Holdings**: Track diverse portfolio across multiple sectors
- **Data Validation**: Robust error handling and data cleaning

### 🌐 **Interactive Dashboard**
- **Multi-Tab Interface**: Organized portfolio information display
- **Live Market Data**: Real-time stock prices via Yahoo Finance API
- **Historical Charts**: Portfolio value tracking over time
- **News Integration**: Latest market news and updates

### 🔧 **Technical Excellence**
- **Production Ready**: Comprehensive testing and validation
- **Scalable Architecture**: Easy to extend with new features
- **API Integration**: Yahoo Finance, Bank of Canada exchange rates
- **Responsive Design**: Clean, professional web interface

---

## 📋 Requirements

### System Requirements
- **Python**: 3.8 or higher
- **Memory**: 2GB RAM minimum
- **Storage**: 100MB free space
- **Internet**: Required for real-time data fetching

### NEW: Enhanced Architecture Requirements
- **Plotly**: For advanced interactive visualizations
- **Scalable Data Models**: Staging, dimension, and fact tables
- **Multi-User Support**: Individual portfolio management
- **Advanced Analytics**: XIRR, diversification, performance metrics

### Data Requirements
- Trading data in CSV format with the following columns:
  ```
  Symbol, Date/Time, Quantity, T. Price, Proceeds, Currency
  ```

---

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/ayushhCreator/Portfolio-Analyzer.git
cd Portfolio-Analyzer
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install PyXIRR (Required for XIRR calculations)
```bash
pip install pyxirr
```

### 5. NEW: Install Enhanced Visualization Dependencies
```bash
pip install plotly==5.24.1
```

---

## 🚀 Quick Start

### Option 1: Original Portfolio Analyzer
1. Place your trading CSV files in the project directory
2. Run: `streamlit run app.py`
3. Access: `http://localhost:8501`

### Option 2: NEW - Enhanced Scalable Version
1. Install enhanced dependencies: `pip install plotly==5.24.1`
2. Run: `streamlit run enhanced_app.py` 
3. Access: `http://localhost:8501`
4. Explore multi-user portfolios with advanced analytics

### Key Differences:
- **Original:** Single portfolio analysis from CSV files
- **Enhanced:** Multi-user, scalable architecture with advanced insights

---

## 📊 Usage Guide

### Dashboard Navigation

#### **📈 Portfolio Summary Tab**
- Current holdings overview
- Total investment vs current value
- Top performers and underperformers
- Portfolio allocation breakdown

#### **📊 Performance Analysis Tab**
- XIRR calculations for each holding
- Historical portfolio value charts
- Performance metrics and statistics
- Risk assessment indicators

#### **🔍 Stock Details Tab**
- Individual stock analysis
- Buy/sell transaction history
- Split-adjusted position tracking
- Current market information

#### **📰 Market News Tab**
- Latest financial news
- Market updates and insights
- Relevant stock-specific news

### Key Metrics Explained

- **XIRR (Extended Internal Rate of Return)**: Annualized return considering irregular cashflows
- **Total Investment**: Sum of all purchase amounts
- **Current Value**: Real-time portfolio valuation
- **Unrealized P/L**: Current profit/loss on holdings

---

## 💾 Data Format

### Expected CSV Format
```csv
Trades,Header,DataDiscriminator,Asset Category,Currency,Symbol,Date/Time,Quantity,T. Price,C. Price,Proceeds,Comm/Fee,Basis,Realized P/L,MTM P/L,Code
Trades,Data,Order,Stocks,USD,AAPL,"2023-07-21, 13:57:21",100,150.00,150,-15000,-1.00,15001.00,0,-0.00,O
```

### Supported Currencies
- **USD** - US Dollar (Base currency)
- **SGD** - Singapore Dollar
- **INR** - Indian Rupee

---

## 🔧 Configuration

### Environment Variables (Optional)
Create a `.env` file for custom configurations:
```env
BASE_CURRENCY=USD
API_TIMEOUT=30
CACHE_DURATION=3600
```

### File Configuration
Modify `app.py` to change default settings:
```python
# --- CONFIGURATION ---
BASE_CURRENCY = "USD"
FILES = ['your_trading_file_1.csv', 'your_trading_file_2.csv']
```



## 📦 Dependencies

### Core Libraries
```
streamlit==1.28.0+
pandas==2.0.0+
yfinance==0.2.0+
pyxirr==0.10.0+
numpy==1.24.0+
```

### Full Dependencies
See `requirements.txt` for complete list of 53 packages.



## 📈 Performance Metrics

### Current Portfolio Statistics
- **Total Trades Processed**: 522 transactions
- **Portfolio Holdings**: 18 unique stocks
- **Total Investment**: $2,518,787.26
- **Current Value**: $484,807.36
- **XIRR Success Rate**: 100% (18/18 holdings)

### Technical Performance
- **Load Time**: < 3 seconds for full portfolio
- **Data Processing**: 522 trades in < 1 second
- **API Response**: Real-time data updates
- **Memory Usage**: < 200MB typical operation

---



## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---



## 🙏 Acknowledgments

- **Yahoo Finance API** for real-time market data
- **Bank of Canada** for currency exchange rates
- **Streamlit Community** for the excellent web framework
- **PyXIRR Library** for accurate financial calculations

---

## 📊 Project Stats

```
Language: Python
Framework: Streamlit
Lines of Code: 663 (app.py)
Test Coverage: 100% core functionality
API Integrations: 2 (Yahoo Finance, Bank of Canada)
Data Processing: 522 trades across 3 years
Financial Accuracy: Professional-grade XIRR calculations
```

---

---

## 🌟 Enhanced Portfolio Analyzer Features

### 🚀 **NEW: Scalable Architecture Version**

Run the enhanced version with: `streamlit run enhanced_app.py`

#### Key Enhancements:
- **🏗️ Scalable Data Model**: Staging, dimension, and fact tables
- **👥 Multi-User Support**: Switch between different portfolios  
- **📊 Advanced Analytics**: XIRR, diversification, performance tracking
- **🎯 Interactive Charts**: Plotly visualizations with real-time updates
- **📈 Historical Analysis**: Portfolio timeline with customizable periods
- **🔍 Stock Research**: Complete metadata and company information
- **⚙️ Data Management**: Automated refresh and export capabilities

#### Sample Results:
- **Portfolio XIRR**: 23.89% - 25.90% (demo users)
- **Real-Time Data**: Live price updates from Yahoo Finance
- **Multi-Asset Support**: Ready for stocks, ETFs, crypto, bonds
- **Global Markets**: Multi-currency and exchange support

### 📋 **File Structure**
```
Portfolio_Analyzer/
├── app.py                          # Original analyzer
├── enhanced_app.py                 # NEW: Scalable version
├── data_models.py                  # NEW: Data architecture
├── portfolio_analytics.py          # NEW: Advanced analytics
├── SCALABILITY_GUIDE.md           # NEW: Architecture guide
├── ENHANCED_SETUP_GUIDE.md        # NEW: Setup instructions
└── test_enhanced_app.py            # NEW: Enhanced testing
```

For detailed setup instructions, see: `ENHANCED_SETUP_GUIDE.md`
For scalability documentation, see: `SCALABILITY_GUIDE.md`

*Last Updated: July 27, 2025*
