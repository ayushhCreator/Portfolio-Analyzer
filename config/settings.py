# Portfolio Analyzer Configuration
# Copy this file to config.py and modify as needed

# Application Settings
APP_NAME = "Portfolio Analyzer"
APP_VERSION = "2.0.0"
DEBUG = False

# Data Settings
DEFAULT_SYMBOLS = ["AAPL", "TSLA", "INFY"]
CACHE_DURATION = 3600  # seconds

# Fee Settings
TRANSACTION_FEE_RATE = 0.001  # 0.1%

# API Settings
YAHOO_FINANCE_TIMEOUT = 30  # seconds

# Database Settings (for future use)
DATABASE_URL = "sqlite:///data/portfolio.db"

# Streamlit Settings
STREAMLIT_CONFIG = {
    "page_title": "📈 Portfolio Analyzer",
    "page_icon": "📈",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Risk Analysis Settings
RISK_THRESHOLDS = {
    "low": 20,      # volatility < 20%
    "medium": 40,   # volatility 20-40%
    "high": 40      # volatility > 40%
}
