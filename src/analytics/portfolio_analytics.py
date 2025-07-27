"""
Portfolio Analytics Engine
Advanced portfolio calculations and insights generation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import yfinance as yf

# XIRR calculation
try:
    from pyxirr import xirr as pyxirr_calc
    XIRR_AVAILABLE = True
except ImportError:
    try:
        import numpy_financial as npf
        XIRR_AVAILABLE = False
    except ImportError:
        XIRR_AVAILABLE = False

class PortfolioAnalytics:
    """
    Advanced portfolio analytics engine with scalable insights generation
    """
    
    def __init__(self, data_models):
        self.data_models = data_models
        self.current_prices = {}
    
    def get_current_holdings(self, user_id: str) -> pd.DataFrame:
        """
        Calculate current holdings for a user based on all transactions
        """
        user_transactions = self.data_models.fact_portfolio_transactions[
            self.data_models.fact_portfolio_transactions['user_id'] == user_id
        ].copy()
        
        if user_transactions.empty:
            return pd.DataFrame()
        
        # Calculate net positions
        holdings = []
        for symbol in user_transactions['symbol'].unique():
            symbol_txns = user_transactions[user_transactions['symbol'] == symbol]
            
            total_bought = symbol_txns[symbol_txns['transaction_type'] == 'Buy']['quantity'].sum()
            total_sold = symbol_txns[symbol_txns['transaction_type'] == 'Sell']['quantity'].sum()
            
            net_quantity = total_bought - total_sold
            
            if net_quantity > 0:  # Only include if still holding
                # Calculate average cost
                buy_txns = symbol_txns[symbol_txns['transaction_type'] == 'Buy']
                avg_cost = (buy_txns['quantity'] * buy_txns['price']).sum() / buy_txns['quantity'].sum()
                
                # Get current price
                current_price = self._get_current_price(symbol)
                current_value = net_quantity * current_price
                
                # Get stock metadata
                stock_info = self.data_models.dim_stock[
                    self.data_models.dim_stock['symbol'] == symbol
                ]
                
                holding = {
                    'symbol': symbol,
                    'company_name': stock_info['company_name'].iloc[0] if not stock_info.empty else symbol,
                    'sector': stock_info['sector'].iloc[0] if not stock_info.empty else 'Unknown',
                    'industry': stock_info['industry'].iloc[0] if not stock_info.empty else 'Unknown',
                    'quantity': net_quantity,
                    'avg_cost': round(avg_cost, 2),
                    'current_price': current_price,
                    'current_value': round(current_value, 2),
                    'total_cost': round(net_quantity * avg_cost, 2),
                    'unrealized_pnl': round(current_value - (net_quantity * avg_cost), 2),
                    'unrealized_pnl_pct': round(((current_price - avg_cost) / avg_cost) * 100, 2)
                }
                holdings.append(holding)
        
        return pd.DataFrame(holdings)
    
    def calculate_portfolio_xirr(self, user_id: str) -> Dict:
        """
        Calculate XIRR for the entire portfolio and individual holdings
        """
        user_transactions = self.data_models.fact_portfolio_transactions[
            self.data_models.fact_portfolio_transactions['user_id'] == user_id
        ].copy()
        
        if user_transactions.empty:
            return {'portfolio_xirr': None, 'individual_xirr': {}}
        
        # Portfolio-level XIRR
        portfolio_cashflows = []
        portfolio_dates = []
        
        for _, txn in user_transactions.iterrows():
            if txn['transaction_type'] == 'Buy':
                cashflow = -txn['total_amount'] - txn['fees']  # Money out
            else:  # Sell
                cashflow = txn['total_amount'] - txn['fees']   # Money in
            
            portfolio_cashflows.append(cashflow)
            portfolio_dates.append(txn['date'])
        
        # Add current portfolio value as final positive cashflow
        current_holdings = self.get_current_holdings(user_id)
        if not current_holdings.empty:
            current_portfolio_value = current_holdings['current_value'].sum()
            portfolio_cashflows.append(current_portfolio_value)
            portfolio_dates.append(datetime.now().date())
        
        # Calculate portfolio XIRR
        portfolio_xirr = self._calculate_xirr(portfolio_cashflows, portfolio_dates)
        
        # Individual stock XIRR
        individual_xirr = {}
        for symbol in user_transactions['symbol'].unique():
            symbol_txns = user_transactions[user_transactions['symbol'] == symbol]
            
            cashflows = []
            dates = []
            
            for _, txn in symbol_txns.iterrows():
                if txn['transaction_type'] == 'Buy':
                    cashflow = -txn['total_amount'] - txn['fees']
                else:
                    cashflow = txn['total_amount'] - txn['fees']
                
                cashflows.append(cashflow)
                dates.append(txn['date'])
            
            # Add current value for holdings still owned
            current_holding = current_holdings[current_holdings['symbol'] == symbol]
            if not current_holding.empty:
                cashflows.append(current_holding['current_value'].iloc[0])
                dates.append(datetime.now().date())
            
            individual_xirr[symbol] = self._calculate_xirr(cashflows, dates)
        
        return {
            'portfolio_xirr': portfolio_xirr,
            'individual_xirr': individual_xirr
        }
    
    def calculate_diversification_metrics(self, user_id: str) -> Dict:
        """
        Calculate portfolio diversification metrics
        """
        holdings = self.get_current_holdings(user_id)
        
        if holdings.empty:
            return {}
        
        total_value = holdings['current_value'].sum()
        
        # Sector diversification
        sector_allocation = holdings.groupby('sector')['current_value'].sum() / total_value * 100
        sector_count = len(sector_allocation)
        
        # Industry diversification  
        industry_allocation = holdings.groupby('industry')['current_value'].sum() / total_value * 100
        industry_count = len(industry_allocation)
        
        # Concentration risk (top 3 holdings)
        top_3_concentration = holdings.nlargest(3, 'current_value')['current_value'].sum() / total_value * 100
        
        # Herfindahl-Hirschman Index for concentration
        weights = holdings['current_value'] / total_value
        hhi = (weights ** 2).sum() * 10000  # Scale to 0-10000
        
        return {
            'sector_allocation': sector_allocation.to_dict(),
            'sector_count': sector_count,
            'industry_allocation': industry_allocation.to_dict(), 
            'industry_count': industry_count,
            'top_3_concentration': round(top_3_concentration, 2),
            'hhi_concentration': round(hhi, 0),
            'diversification_score': self._calculate_diversification_score(sector_count, hhi)
        }
    
    def calculate_performance_metrics(self, user_id: str) -> Dict:
        """
        Calculate comprehensive performance metrics
        """
        holdings = self.get_current_holdings(user_id)
        user_transactions = self.data_models.fact_portfolio_transactions[
            self.data_models.fact_portfolio_transactions['user_id'] == user_id
        ]
        
        if holdings.empty:
            return {}
        
        # Basic metrics
        buy_transactions = user_transactions[user_transactions['transaction_type'] == 'Buy']
        total_invested = buy_transactions['total_amount'].sum() + buy_transactions['fees'].sum()
        total_fees = user_transactions['fees'].sum()
        current_value = holdings['current_value'].sum()
        total_unrealized_pnl = holdings['unrealized_pnl'].sum()
        
        # Performance ratios
        total_return_pct = (current_value - total_invested) / total_invested * 100
        
        # Top/bottom performers
        top_performer = holdings.loc[holdings['unrealized_pnl_pct'].idxmax()] if not holdings.empty else None
        bottom_performer = holdings.loc[holdings['unrealized_pnl_pct'].idxmin()] if not holdings.empty else None
        
        # Portfolio timeline
        first_transaction = user_transactions['date'].min()
        days_invested = (datetime.now().date() - first_transaction).days
        
        return {
            'total_invested': round(total_invested, 2),
            'total_fees': round(total_fees, 2),
            'current_value': round(current_value, 2),
            'total_unrealized_pnl': round(total_unrealized_pnl, 2),
            'total_return_pct': round(total_return_pct, 2),
            'days_invested': days_invested,
            'top_performer': {
                'symbol': top_performer['symbol'],
                'return_pct': top_performer['unrealized_pnl_pct'],
                'pnl': top_performer['unrealized_pnl']
            } if top_performer is not None else None,
            'bottom_performer': {
                'symbol': bottom_performer['symbol'], 
                'return_pct': bottom_performer['unrealized_pnl_pct'],
                'pnl': bottom_performer['unrealized_pnl']
            } if bottom_performer is not None else None
        }
    
    def generate_portfolio_timeline(self, user_id: str, days: int = 30) -> pd.DataFrame:
        """
        Generate portfolio value over time
        """
        user_transactions = self.data_models.fact_portfolio_transactions[
            self.data_models.fact_portfolio_transactions['user_id'] == user_id
        ].copy()
        
        if user_transactions.empty:
            return pd.DataFrame()
        
        # Get date range
        start_date = max(
            user_transactions['date'].min(),
            datetime.now().date() - timedelta(days=days)
        )
        end_date = datetime.now().date()
        
        # Get price history for all user's symbols
        symbols = user_transactions['symbol'].unique()
        price_history = self.data_models.stg_stock_price[
            (self.data_models.stg_stock_price['symbol'].isin(symbols)) &
            (self.data_models.stg_stock_price['date'] >= start_date) &
            (self.data_models.stg_stock_price['date'] <= end_date)
        ]
        
        timeline = []
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        for date in date_range:
            date_only = date.date()
            
            # Calculate holdings as of this date
            holdings_as_of_date = self._calculate_holdings_as_of_date(user_transactions, date_only)
            
            portfolio_value = 0
            for symbol, quantity in holdings_as_of_date.items():
                if quantity > 0:
                    # Get price for this date (or closest available)
                    symbol_prices = price_history[
                        (price_history['symbol'] == symbol) &
                        (price_history['date'] <= date_only)
                    ].sort_values('date')
                    
                    if not symbol_prices.empty:
                        price = symbol_prices.iloc[-1]['close']
                        portfolio_value += quantity * price
            
            timeline.append({
                'date': date_only,
                'portfolio_value': round(portfolio_value, 2)
            })
        
        return pd.DataFrame(timeline)
    
    def _get_current_price(self, symbol: str) -> float:
        """
        Get current price for a symbol (with caching)
        """
        if symbol in self.current_prices:
            return self.current_prices[symbol]
        
        try:
            # First try to get from staging data (most recent)
            recent_price = self.data_models.stg_stock_price[
                self.data_models.stg_stock_price['symbol'] == symbol
            ].sort_values('date')
            
            if not recent_price.empty:
                price = recent_price.iloc[-1]['close']
            else:
                # Fallback to live fetch
                ticker = yf.Ticker(symbol)
                price = ticker.history(period='1d')['Close'].iloc[-1]
            
            self.current_prices[symbol] = round(price, 2)
            return self.current_prices[symbol]
            
        except Exception:
            return 0.0
    
    def _calculate_xirr(self, cashflows: List[float], dates: List) -> Optional[float]:
        """
        Calculate XIRR with fallback options
        """
        try:
            if len(cashflows) < 2:
                return None
            
            # Check if we have both positive and negative cashflows
            if not (any(cf > 0 for cf in cashflows) and any(cf < 0 for cf in cashflows)):
                return None
            
            if XIRR_AVAILABLE:
                # Convert dates to datetime objects if needed
                date_objects = []
                for d in dates:
                    if hasattr(d, 'date'):
                        date_objects.append(d.date())
                    elif isinstance(d, pd.Timestamp):
                        date_objects.append(d.date())
                    else:
                        date_objects.append(d)
                
                result = pyxirr_calc(amounts=cashflows, dates=date_objects)
                return round(result * 100, 2) if result is not None else None
            else:
                # Simple IRR approximation
                return None
                
        except Exception:
            return None
    
    def _calculate_diversification_score(self, sector_count: int, hhi: float) -> str:
        """
        Calculate qualitative diversification score
        """
        if sector_count >= 5 and hhi < 2500:
            return "Well Diversified"
        elif sector_count >= 3 and hhi < 4000:
            return "Moderately Diversified"
        else:
            return "Concentrated"
    
    def _calculate_holdings_as_of_date(self, transactions: pd.DataFrame, as_of_date) -> Dict[str, float]:
        """
        Calculate holdings as of a specific date
        """
        relevant_txns = transactions[transactions['date'] <= as_of_date]
        
        holdings = {}
        for symbol in relevant_txns['symbol'].unique():
            symbol_txns = relevant_txns[relevant_txns['symbol'] == symbol]
            
            bought = symbol_txns[symbol_txns['transaction_type'] == 'Buy']['quantity'].sum()
            sold = symbol_txns[symbol_txns['transaction_type'] == 'Sell']['quantity'].sum()
            
            holdings[symbol] = bought - sold
        
        return holdings
