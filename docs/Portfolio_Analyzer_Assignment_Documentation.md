# Portfolio Analyzer Assignment - Complete Documentation

## Project Overview

**Project Name:** Advanced Portfolio Performance Analyzer  
**Developer:** Ayush Raj  
**Technology Stack:** Python, Streamlit, Pandas, YFinance, PyXIRR  
**Repository:** [Portfolio-Analyzer](https://github.com/ayushhCreator/Portfolio-Analyzer)  
**Assignment Type:** Financial Data Analysis & Web Application Development

---

## Assignment Objectives

The goal was to create a comprehensive portfolio analysis tool that can:

1. **Process Multi-Year Trading Data** - Load and consolidate stock trading records from multiple CSV files
2. **Handle Multi-Currency Transactions** - Convert all trades to a base currency (USD) using real-time exchange rates
3. **Account for Stock Splits** - Automatically adjust historical positions for stock splits and dividends
4. **Calculate Advanced Financial Metrics** - Compute XIRR (Extended Internal Rate of Return) for each holding
5. **Provide Interactive Visualization** - Create a user-friendly web interface with charts and analytics
6. **Real-Time Market Data Integration** - Fetch current stock prices and market news
7. **Portfolio Valuation Tracking** - Track portfolio value changes over time

---

## Technical Architecture

### Core Components

#### 1. **Data Processing Engine**
- **Input:** Three CSV files containing trading data (2023, 2024, 2025)
- **Volume:** 522 individual trades across 18 different stock symbols
- **Currencies:** USD, SGD, INR with automatic conversion
- **Data Cleaning:** Handles malformed records and missing data

#### 2. **Financial Calculations Module**
- **XIRR Calculation:** Uses PyXIRR library for accurate annualized returns
- **Currency Conversion:** Real-time exchange rates from Bank of Canada
- **Stock Split Adjustments:** Automatic historical position adjustments
- **Portfolio Valuation:** Daily portfolio value calculations

#### 3. **Web Interface (Streamlit)**
- **Multi-Tab Layout:** Organized information display
- **Interactive Charts:** Portfolio performance visualization
- **Real-Time Updates:** Current market data integration
- **Responsive Design:** Clean, professional interface

### Technology Stack Details

```python
# Core Libraries Used
import pandas as pd          # Data manipulation and analysis
import streamlit as st       # Web application framework
import yfinance as yf        # Yahoo Finance API for stock data
import numpy as np           # Numerical computations
from pyxirr import xirr     # XIRR calculations (financial metrics)
```

---

## Key Features Implemented

### 📊 **Feature 1: Multi-File Data Consolidation**
- **Challenge:** Process trading data spread across multiple CSV files
- **Solution:** Created automated data loading system that consolidates all files
- **Result:** Successfully loaded 522 trades from 3 separate files

### 💱 **Feature 2: Multi-Currency Support**
- **Challenge:** Trades in USD, SGD, and INR currencies
- **Solution:** Implemented real-time currency conversion using Bank of Canada API
- **Result:** All trades normalized to USD for accurate analysis

### 📈 **Feature 3: Stock Split Adjustments**
- **Challenge:** Historical stock splits affect position calculations
- **Solution:** Integrated Yahoo Finance API to detect and apply split adjustments
- **Result:** Accurate historical position tracking for all holdings

### 🧮 **Feature 4: XIRR Calculation (Major Technical Challenge)**
- **Challenge:** Calculate Extended Internal Rate of Return for irregular cashflows
- **Initial Problem:** Original implementation using numpy_financial was returning 0% returns
- **Root Cause Analysis:** 
  - Incorrect cashflow signs (buy vs sell transactions)
  - Library compatibility issues
  - Date format inconsistencies
- **Solution Implemented:**
  ```python
  # Corrected cashflow logic
  # Buy transactions: negative cashflow (money going out)
  # Sell transactions: positive cashflow (money coming in)
  
  # Replaced numpy_financial with pyxirr for reliability
  from pyxirr import xirr as pyxirr_calc
  
  # Proper date handling and type conversion
  date_objects = [d.date() for d in dates]
  float_cashflows = [float(cf) for cf in cashflows]
  ```
- **Result:** Achieved realistic XIRR calculations (NET: 45.35%, NVDA: 98.16%, SPY: 23.36%)

### 📱 **Feature 5: Interactive Web Interface**
- **Portfolio Summary Tab:** Current holdings and performance metrics
- **Historical Performance Tab:** Time-series portfolio value charts
- **Individual Stock Analysis Tab:** Detailed per-stock metrics
- **Market News Tab:** Real-time financial news integration

### 💰 **Feature 6: Portfolio Valuation Engine**
- **Real-time Pricing:** Integration with Yahoo Finance for current market prices
- **Historical Tracking:** 785 days of portfolio value history
- **Total Investment Calculation:** Accurate summation of all purchase amounts
- **Current Value:** $484,807.36 portfolio value vs $2,518,787.26 total invested

---

## Data Structure & Processing

### Input Data Format
```csv
Trades,Header,DataDiscriminator,Asset Category,Currency,Symbol,Date/Time,Quantity,T. Price,C. Price,Proceeds,Comm/Fee,Basis,Realized P/L,MTM P/L,Code
Trades,Data,Order,Stocks,USD,AMZN,"2023-07-21, 13:57:21",50,130.478,130,-6523.9,-1.078,6524.978,0,-23.9,O
```

### Holdings Summary
The portfolio contains **18 unique stock symbols**:
- **Technology:** AMZN, GOOG, MSFT, NVDA, NET, PLTR, TSLA, SOFI
- **Financial:** JPM, BAC, WFC, BRK.B
- **ETFs:** SPY, QQQ
- **Others:** GPRO, AAL, GME, AAPL

### Financial Metrics Achieved
- **Total Trades Processed:** 522 transactions
- **Total Investment:** $2,518,787.26
- **Current Portfolio Value:** $484,807.36
- **XIRR Success Rate:** 18/18 holdings (100%)
- **Currency Conversion Days:** 785 days of exchange rates

---

## Technical Challenges & Solutions

### Challenge 1: XIRR Calculation Accuracy
**Problem:** Initial XIRR calculations were returning 0% for all holdings
**Investigation Process:**
1. Created debug scripts to analyze cashflow patterns
2. Tested different financial libraries (numpy_financial vs pyxirr)
3. Analyzed date formatting and data type issues

**Solution:**
- Implemented proper cashflow sign conventions
- Migrated to PyXIRR library for better accuracy
- Added robust error handling and data validation

### Challenge 2: Multi-Currency Data Processing
**Problem:** Trades in different currencies needed normalization
**Solution:**
- Integrated Bank of Canada XML API for real-time exchange rates
- Implemented caching to optimize API calls
- Added fallback mechanisms for missing exchange rate data

### Challenge 3: Stock Split Adjustments
**Problem:** Historical stock splits distort position calculations
**Solution:**
- Used Yahoo Finance API to fetch stock split history
- Implemented automatic position adjustment algorithms
- Added validation to ensure split accuracy

---

## Testing & Validation

### Comprehensive Testing Suite
Created multiple test scripts to validate functionality:

1. **test_functionality.py** - End-to-end system testing
2. **test_xirr.py** - Specific XIRR calculation validation
3. **debug_cashflow.py** - Cashflow pattern analysis
4. **debug_xirr.py** - XIRR debugging and verification

### Test Results
✅ **Data Loading:** 522 trades successfully loaded  
✅ **Holdings Generation:** 18 holdings created  
✅ **Stock Splits:** Applied to 11 stocks  
✅ **Currency Conversion:** 785 days of rates retrieved  
✅ **XIRR Calculations:** 18/18 holdings successful  
✅ **Portfolio Valuation:** Real-time pricing working  
✅ **Web Interface:** All tabs functional  

---

## Development Process & Version Control

### Git Repository Management
- **Repository:** GitHub - ayushhCreator/Portfolio-Analyzer
- **Branch:** master
- **Commits:** Detailed commit messages documenting each feature
- **Key Commit:** "Fix XIRR calculation and total investment logic"

### Code Organization
```
Portfolio_Analyzer/
├── app.py                 # Main application (663 lines)
├── requirements.txt       # Python dependencies (53 packages)
├── Stock_trading_2023.csv # Trading data (33 records)
├── Stock_trading_2024.csv # Trading data (largest file)
├── Stock_trading_2025.csv # Trading data (current year)
├── test_functionality.py # Comprehensive testing
├── test_xirr.py          # XIRR-specific tests
└── debug_*.py            # Debugging utilities
```

---

## Key Learnings & Skills Demonstrated

### Technical Skills
1. **Python Programming:** Advanced pandas operations, API integrations
2. **Financial Mathematics:** XIRR calculations, portfolio theory
3. **Web Development:** Streamlit framework, responsive design
4. **Data Engineering:** ETL processes, data validation
5. **API Integration:** Yahoo Finance, Bank of Canada APIs
6. **Version Control:** Git workflow, collaborative development

### Problem-Solving Approach
1. **Root Cause Analysis:** Systematic debugging of financial calculations
2. **Research & Learning:** Evaluated multiple financial libraries
3. **Testing Strategy:** Created comprehensive validation suite
4. **Documentation:** Detailed code comments and commit messages

### Financial Domain Knowledge
1. **Portfolio Management:** Understanding of investment metrics
2. **Currency Markets:** Multi-currency transaction handling
3. **Stock Market Mechanics:** Split adjustments, dividend handling
4. **Performance Metrics:** XIRR, total returns, portfolio valuation

---

## Results & Impact

### Quantitative Results
- **Portfolio Value:** Successfully tracking $484K+ in current holdings
- **Historical Data:** Processing 3+ years of trading history
- **Accuracy:** 100% success rate in XIRR calculations
- **Performance:** Real-time data updates and responsive interface

### Qualitative Achievements
- **Professional Web Application:** Clean, intuitive user interface
- **Robust Error Handling:** Graceful handling of data anomalies
- **Scalable Architecture:** Easy to extend with new features
- **Production Ready:** Comprehensive testing and validation

---

## Future Enhancement Opportunities

### Technical Improvements
1. **Database Integration:** Move from CSV files to proper database
2. **Advanced Charting:** More sophisticated financial visualizations
3. **Risk Metrics:** Add VaR, Sharpe ratio, beta calculations
4. **Automated Reporting:** PDF export functionality

### Feature Expansions
1. **Options Trading:** Support for derivatives and complex instruments
2. **Tax Optimization:** Capital gains/loss analysis
3. **Benchmark Comparison:** Performance vs market indices
4. **Portfolio Optimization:** Modern portfolio theory integration

---

## Conclusion

This Portfolio Analyzer assignment demonstrates a comprehensive understanding of:

- **Software Engineering:** Clean code, testing, version control
- **Financial Technology:** Real-world fintech application development
- **Data Science:** Large-scale data processing and analysis
- **Web Development:** User-friendly interface design
- **Problem Solving:** Complex technical challenge resolution

The project successfully evolved from a basic data processing tool to a sophisticated portfolio management system, showcasing both technical depth and practical financial application.

**Final Status:** ✅ All objectives completed with production-ready implementation.

---

*Document Generated: July 24, 2025*  
*Project Repository: https://github.com/ayushhCreator/Portfolio-Analyzer 
