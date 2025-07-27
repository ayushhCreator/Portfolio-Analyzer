"""
Advanced Portfolio Insights Engine
Provides detailed portfolio analysis, stock impact analysis, and market events correlation
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class MarketEvent:
    date: datetime
    event_type: str
    description: str
    impact_level: str  # High, Medium, Low
    affected_sectors: List[str]

@dataclass
class StockInsight:
    symbol: str
    company_name: str
    price_change_pct: float
    price_change_abs: float
    volume_change_pct: float
    portfolio_impact: float
    key_events: List[str]
    performance_rating: str

class PortfolioInsights:
    """
    Advanced insights engine for portfolio analysis
    """
    
    def __init__(self, data_models, portfolio_analytics):
        self.data_models = data_models
        self.portfolio_analytics = portfolio_analytics
        self.market_events = self._load_market_events()
    
    def get_period_insights(self, user_id: str, start_date: str, end_date: str) -> Dict:
        """
        Generate comprehensive insights for a specific time period
        """
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Get user's portfolio holdings
        holdings = self.portfolio_analytics.get_current_holdings(user_id)
        if holdings.empty:
            return {"error": "No holdings found for user"}
        
        insights = {
            "period": {"start": start_date, "end": end_date},
            "portfolio_overview": self._get_portfolio_overview(user_id, start_dt, end_dt),
            "stock_performance": self._analyze_stock_performance(holdings, start_dt, end_dt),
            "portfolio_impact_analysis": self._analyze_portfolio_impact(user_id, holdings, start_dt, end_dt),
            "market_events": self._get_relevant_market_events(start_dt, end_dt),
            "sector_analysis": self._analyze_sector_performance(holdings, start_dt, end_dt),
            "risk_insights": self._generate_risk_insights(holdings, start_dt, end_dt),
            "recommendations": self._generate_recommendations(user_id, holdings, start_dt, end_dt)
        }
        
        return insights
    
    def _get_portfolio_overview(self, user_id: str, start_dt: datetime, end_dt: datetime) -> Dict:
        """
        Get overall portfolio performance overview
        """
        holdings = self.portfolio_analytics.get_current_holdings(user_id)
        
        # Calculate portfolio value at start and end of period
        portfolio_start_value = 0
        portfolio_end_value = 0
        total_dividends = 0
        
        for _, holding in holdings.iterrows():
            symbol = holding['symbol']
            quantity = holding['quantity']
            
            # Get historical prices
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(start=start_dt, end=end_dt + timedelta(days=1))
                
                if not hist.empty:
                    start_price = hist.iloc[0]['Close'] if len(hist) > 0 else holding['current_price']
                    end_price = hist.iloc[-1]['Close'] if len(hist) > 0 else holding['current_price']
                    
                    portfolio_start_value += quantity * start_price
                    portfolio_end_value += quantity * end_price
                    
                    # Calculate dividends (simplified)
                    try:
                        dividends = ticker.dividends
                        if not dividends.empty:
                            # Convert timezone-aware dates to timezone-naive for comparison
                            dividends_index = dividends.index
                            if hasattr(dividends_index, 'tz') and dividends_index.tz is not None:
                                dividends_index = dividends_index.tz_convert(None)
                            
                            period_dividends = dividends[(dividends_index >= start_dt) & (dividends_index <= end_dt)]
                            total_dividends += (period_dividends * quantity).sum()
                    except:
                        # Skip dividend calculation if there are issues
                        pass
                        
            except Exception as e:
                print(f"Error fetching data for {symbol}: {e}")
                portfolio_start_value += quantity * holding['current_price']
                portfolio_end_value += quantity * holding['current_price']
        
        total_return = portfolio_end_value + total_dividends - portfolio_start_value
        total_return_pct = (total_return / portfolio_start_value * 100) if portfolio_start_value > 0 else 0
        
        return {
            "start_value": round(portfolio_start_value, 2),
            "end_value": round(portfolio_end_value, 2),
            "total_dividends": round(total_dividends, 2),
            "absolute_return": round(total_return, 2),
            "percentage_return": round(total_return_pct, 2),
            "period_days": (end_dt - start_dt).days,
            "annualized_return": round((total_return_pct * 365) / (end_dt - start_dt).days, 2) if (end_dt - start_dt).days > 0 else 0
        }
    
    def _analyze_stock_performance(self, holdings: pd.DataFrame, start_dt: datetime, end_dt: datetime) -> List[StockInsight]:
        """
        Analyze individual stock performance and impact
        """
        stock_insights = []
        
        for _, holding in holdings.iterrows():
            symbol = holding['symbol']
            company_name = holding['company_name']
            quantity = holding['quantity']
            
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(start=start_dt, end=end_dt + timedelta(days=1))
                
                if not hist.empty:
                    start_price = hist.iloc[0]['Close']
                    end_price = hist.iloc[-1]['Close']
                    start_volume = hist.iloc[0]['Volume']
                    avg_volume = hist['Volume'].mean()
                    
                    price_change_abs = end_price - start_price
                    price_change_pct = (price_change_abs / start_price) * 100
                    volume_change_pct = ((avg_volume - start_volume) / start_volume) * 100 if start_volume > 0 else 0
                    portfolio_impact = quantity * price_change_abs
                    
                    # Performance rating
                    if price_change_pct > 10:
                        performance_rating = "Excellent"
                    elif price_change_pct > 5:
                        performance_rating = "Good"
                    elif price_change_pct > 0:
                        performance_rating = "Positive"
                    elif price_change_pct > -5:
                        performance_rating = "Slight Decline"
                    else:
                        performance_rating = "Poor"
                    
                    # Get key events (simplified - in real implementation, would integrate with news APIs)
                    key_events = self._get_stock_events(symbol, start_dt, end_dt, price_change_pct)
                    
                    insight = StockInsight(
                        symbol=symbol,
                        company_name=company_name,
                        price_change_pct=round(price_change_pct, 2),
                        price_change_abs=round(price_change_abs, 2),
                        volume_change_pct=round(volume_change_pct, 2),
                        portfolio_impact=round(portfolio_impact, 2),
                        key_events=key_events,
                        performance_rating=performance_rating
                    )
                    
                    stock_insights.append(insight)
                    
            except Exception as e:
                print(f"Error analyzing {symbol}: {e}")
        
        # Sort by portfolio impact (absolute value)
        stock_insights.sort(key=lambda x: abs(x.portfolio_impact), reverse=True)
        return stock_insights
    
    def _analyze_portfolio_impact(self, user_id: str, holdings: pd.DataFrame, start_dt: datetime, end_dt: datetime) -> Dict:
        """
        Analyze which stocks had the most impact on portfolio performance
        """
        stock_impacts = []
        total_impact = 0
        
        for _, holding in holdings.iterrows():
            symbol = holding['symbol']
            quantity = holding['quantity']
            
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(start=start_dt, end=end_dt + timedelta(days=1))
                
                if not hist.empty:
                    start_price = hist.iloc[0]['Close']
                    end_price = hist.iloc[-1]['Close']
                    price_change = end_price - start_price
                    impact = quantity * price_change
                    total_impact += impact
                    
                    stock_impacts.append({
                        "symbol": symbol,
                        "company_name": holding['company_name'],
                        "impact": round(impact, 2),
                        "contribution_pct": 0  # Will calculate after total
                    })
                    
            except Exception as e:
                print(f"Error calculating impact for {symbol}: {e}")
        
        # Calculate contribution percentages
        for stock in stock_impacts:
            if total_impact != 0:
                stock["contribution_pct"] = round((stock["impact"] / total_impact) * 100, 2)
        
        # Sort by absolute impact
        stock_impacts.sort(key=lambda x: abs(x["impact"]), reverse=True)
        
        # Get top contributors and detractors
        positive_impacts = [s for s in stock_impacts if s["impact"] > 0]
        negative_impacts = [s for s in stock_impacts if s["impact"] < 0]
        
        return {
            "total_portfolio_impact": round(total_impact, 2),
            "top_contributors": positive_impacts[:3],
            "top_detractors": negative_impacts[:3],
            "all_impacts": stock_impacts
        }
    
    def _get_relevant_market_events(self, start_dt: datetime, end_dt: datetime) -> List[Dict]:
        """
        Get market events that occurred during the period
        """
        relevant_events = []
        
        for event in self.market_events:
            if start_dt <= event.date <= end_dt:
                relevant_events.append({
                    "date": event.date.strftime('%Y-%m-%d'),
                    "event_type": event.event_type,
                    "description": event.description,
                    "impact_level": event.impact_level,
                    "affected_sectors": event.affected_sectors
                })
        
        return relevant_events
    
    def _analyze_sector_performance(self, holdings: pd.DataFrame, start_dt: datetime, end_dt: datetime) -> Dict:
        """
        Analyze performance by sector
        """
        sector_performance = {}
        
        for _, holding in holdings.iterrows():
            sector = holding['sector']
            symbol = holding['symbol']
            quantity = holding['quantity']
            
            if sector not in sector_performance:
                sector_performance[sector] = {
                    "stocks": [],
                    "total_impact": 0,
                    "stock_count": 0
                }
            
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(start=start_dt, end=end_dt + timedelta(days=1))
                
                if not hist.empty:
                    start_price = hist.iloc[0]['Close']
                    end_price = hist.iloc[-1]['Close']
                    price_change_pct = ((end_price - start_price) / start_price) * 100
                    impact = quantity * (end_price - start_price)
                    
                    sector_performance[sector]["stocks"].append({
                        "symbol": symbol,
                        "performance": round(price_change_pct, 2),
                        "impact": round(impact, 2)
                    })
                    sector_performance[sector]["total_impact"] += impact
                    sector_performance[sector]["stock_count"] += 1
                    
            except Exception as e:
                print(f"Error analyzing sector performance for {symbol}: {e}")
        
        # Calculate average performance per sector
        for sector in sector_performance:
            if sector_performance[sector]["stock_count"] > 0:
                avg_performance = sum([s["performance"] for s in sector_performance[sector]["stocks"]]) / sector_performance[sector]["stock_count"]
                sector_performance[sector]["average_performance"] = round(avg_performance, 2)
                sector_performance[sector]["total_impact"] = round(sector_performance[sector]["total_impact"], 2)
        
        return sector_performance
    
    def _generate_risk_insights(self, holdings: pd.DataFrame, start_dt: datetime, end_dt: datetime) -> Dict:
        """
        Generate risk-related insights
        """
        volatilities = []
        correlations = {}
        
        for _, holding in holdings.iterrows():
            symbol = holding['symbol']
            
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(start=start_dt, end=end_dt + timedelta(days=1))
                
                if len(hist) > 1:
                    returns = hist['Close'].pct_change().dropna()
                    volatility = returns.std() * np.sqrt(252)  # Annualized volatility
                    volatilities.append({
                        "symbol": symbol,
                        "volatility": round(volatility * 100, 2)
                    })
                    
            except Exception as e:
                print(f"Error calculating risk metrics for {symbol}: {e}")
        
        # Sort by volatility
        volatilities.sort(key=lambda x: x["volatility"], reverse=True)
        
        return {
            "stock_volatilities": volatilities,
            "highest_risk_stock": volatilities[0] if volatilities else None,
            "lowest_risk_stock": volatilities[-1] if volatilities else None,
            "portfolio_diversification": len(holdings),
            "risk_level": self._assess_portfolio_risk(volatilities)
        }
    
    def _generate_recommendations(self, user_id: str, holdings: pd.DataFrame, start_dt: datetime, end_dt: datetime) -> List[str]:
        """
        Generate actionable recommendations based on analysis
        """
        recommendations = []
        
        # Analyze performance
        poor_performers = []
        excellent_performers = []
        
        for _, holding in holdings.iterrows():
            symbol = holding['symbol']
            
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(start=start_dt, end=end_dt + timedelta(days=1))
                
                if not hist.empty:
                    start_price = hist.iloc[0]['Close']
                    end_price = hist.iloc[-1]['Close']
                    performance = ((end_price - start_price) / start_price) * 100
                    
                    if performance < -10:
                        poor_performers.append(symbol)
                    elif performance > 15:
                        excellent_performers.append(symbol)
                        
            except Exception as e:
                print(f"Error in recommendations for {symbol}: {e}")
        
        # Generate recommendations
        if poor_performers:
            recommendations.append(f"Consider reviewing underperforming stocks: {', '.join(poor_performers)}")
        
        if excellent_performers:
            recommendations.append(f"Consider taking profits or rebalancing from strong performers: {', '.join(excellent_performers)}")
        
        # Diversification recommendations
        if len(holdings) < 5:
            recommendations.append("Consider diversifying your portfolio with more stocks across different sectors")
        
        # Sector concentration
        sector_counts = holdings['sector'].value_counts()
        if len(sector_counts) > 0 and sector_counts.iloc[0] > len(holdings) * 0.6:
            recommendations.append(f"Your portfolio is heavily concentrated in {sector_counts.index[0]}. Consider diversifying across sectors")
        
        return recommendations
    
    def _get_stock_events(self, symbol: str, start_dt: datetime, end_dt: datetime, price_change_pct: float) -> List[str]:
        """
        Get key events for a stock during the period (simplified implementation)
        """
        events = []
        
        # Earnings season check (simplified)
        if start_dt.month in [1, 4, 7, 10]:  # Typical earnings months
            events.append("Earnings season - potential earnings announcement impact")
        
        # Significant price movement analysis
        if abs(price_change_pct) > 15:
            if price_change_pct > 0:
                events.append("Significant positive price movement - possible positive news or market sentiment")
            else:
                events.append("Significant negative price movement - possible negative news or market concerns")
        
        # Market event correlation
        for event in self.market_events:
            if start_dt <= event.date <= end_dt:
                if event.impact_level == "High":
                    events.append(f"Market event: {event.description}")
        
        return events
    
    def _load_market_events(self) -> List[MarketEvent]:
        """
        Load historical market events (simplified - in real implementation, would use financial data APIs)
        """
        events = [
            MarketEvent(
                date=datetime(2024, 1, 15),
                event_type="Fed Decision",
                description="Federal Reserve keeps interest rates unchanged",
                impact_level="Medium",
                affected_sectors=["Financial", "Technology"]
            ),
            MarketEvent(
                date=datetime(2024, 2, 10),
                event_type="Inflation Data",
                description="Lower than expected inflation data released",
                impact_level="High",
                affected_sectors=["All"]
            ),
            MarketEvent(
                date=datetime(2024, 3, 1),
                event_type="Geopolitical",
                description="Geopolitical tensions affecting global markets",
                impact_level="High",
                affected_sectors=["Energy", "Defense", "Technology"]
            ),
            MarketEvent(
                date=datetime(2024, 6, 15),
                event_type="Tech Earnings",
                description="Strong tech sector earnings beat expectations",
                impact_level="Medium",
                affected_sectors=["Technology"]
            ),
            MarketEvent(
                date=datetime(2025, 1, 10),
                event_type="AI Revolution",
                description="Major AI breakthrough announcements affecting tech stocks",
                impact_level="High",
                affected_sectors=["Technology", "Healthcare"]
            )
        ]
        
        return events
    
    def _assess_portfolio_risk(self, volatilities: List[Dict]) -> str:
        """
        Assess overall portfolio risk level
        """
        if not volatilities:
            return "Unknown"
        
        avg_volatility = sum([v["volatility"] for v in volatilities]) / len(volatilities)
        
        if avg_volatility > 40:
            return "High Risk"
        elif avg_volatility > 25:
            return "Medium Risk"
        else:
            return "Low Risk"
