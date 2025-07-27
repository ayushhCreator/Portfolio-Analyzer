"""
Enhanced Portfolio Analyzer with Scalable Architecture
Advanced portfolio analysis with dimension/fact model and comprehensive insights
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import yfinance as yf
import sys
import os

# Add the parent directory to the Python path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import our custom modules
from src.models.data_models import DataModels
from src.analytics.portfolio_analytics import PortfolioAnalytics
from src.analytics.portfolio_insights import PortfolioInsights

# Page configuration
st.set_page_config(
    page_title="📈 Enhanced Portfolio Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .positive-return {
        color: #28a745;
        font-weight: bold;
    }
    .negative-return {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for data persistence
@st.cache_resource
def initialize_data_models():
    """Initialize and populate data models"""
    dm = DataModels()
    dm.initialize_schemas()
    
    # Sample symbols for demonstration
    symbols = ['AAPL', 'TSLA', 'INFY']
    
    # Fetch and populate data
    with st.spinner("Fetching stock metadata..."):
        dm.fetch_stock_metadata(symbols)
        dm.log_refresh('dim_stock', len(dm.dim_stock), 'SUCCESS')
    
    with st.spinner("Fetching price data..."):
        dm.fetch_stock_prices(symbols, days=30)
        dm.log_refresh('stg_stock_price', len(dm.stg_stock_price), 'SUCCESS')
    
    # Create sample users and transactions
    dm.create_sample_users()
    dm.create_sample_transactions(symbols)
    dm.log_refresh('fact_portfolio_transactions', len(dm.fact_portfolio_transactions), 'SUCCESS')
    
    return dm

def main():
    st.markdown('<h1 class="main-header">📈 Enhanced Portfolio Analyzer</h1>', unsafe_allow_html=True)
    st.markdown("**Advanced Portfolio Analysis with Scalable Data Architecture**")
    
    # Initialize data models
    data_models = initialize_data_models()
    analytics = PortfolioAnalytics(data_models)
    insights_engine = PortfolioInsights(data_models, analytics)
    
    # Sidebar for navigation
    st.sidebar.title("🚀 Navigation")
    
    # Data architecture overview
    with st.sidebar.expander("📊 Data Architecture Overview", expanded=False):
        summary = data_models.get_data_summary()
        st.write("**Scalable Data Model:**")
        st.write(f"• Stock Metadata: {summary['dimension_stock_records']} records")
        st.write(f"• Price Data: {summary['staging_stock_price_records']} records")
        st.write(f"• Transactions: {summary['fact_transaction_records']} records")
        st.write(f"• Users: {summary['dimension_user_records']} records")
    
    # User selection
    users = data_models.dim_user['user_id'].tolist()
    selected_user = st.sidebar.selectbox(
        "👤 Select User Portfolio",
        options=users,
        format_func=lambda x: data_models.dim_user[data_models.dim_user['user_id']==x]['user_name'].iloc[0]
    )
    
    # Main navigation
    tab_options = [
        "🏠 Portfolio Overview",
        "📊 Performance Analytics", 
        "🎯 Diversification Analysis",
        "📈 Historical Performance",
        "� Portfolio Insights",
        "�🔍 Stock Research",
        "⚙️ Data Management"
    ]
    
    selected_tab = st.sidebar.radio("Select Analysis", tab_options)
    
    # Tab content
    if selected_tab == "🏠 Portfolio Overview":
        portfolio_overview_tab(analytics, selected_user, data_models)
    
    elif selected_tab == "📊 Performance Analytics":
        performance_analytics_tab(analytics, selected_user)
    
    elif selected_tab == "🎯 Diversification Analysis":
        diversification_analysis_tab(analytics, selected_user)
    
    elif selected_tab == "📈 Historical Performance":
        historical_performance_tab(analytics, selected_user)
    
    elif selected_tab == "� Portfolio Insights":
        portfolio_insights_tab(insights_engine, selected_user, data_models)
    
    elif selected_tab == "�🔍 Stock Research":
        stock_research_tab(data_models)
    
    elif selected_tab == "⚙️ Data Management":
        data_management_tab(data_models)

def portfolio_overview_tab(analytics, user_id, data_models):
    """Portfolio overview and current holdings"""
    st.header("🏠 Portfolio Overview")
    
    # Get user info
    user_info = data_models.dim_user[data_models.dim_user['user_id'] == user_id].iloc[0]
    st.subheader(f"Portfolio for: {user_info['user_name']}")
    
    # Current holdings
    holdings = analytics.get_current_holdings(user_id)
    
    if holdings.empty:
        st.warning("No current holdings found for this user.")
        return
    
    # Portfolio summary metrics
    performance_metrics = analytics.calculate_performance_metrics(user_id)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💰 Total Invested",
            f"${performance_metrics['total_invested']:,.2f}",
            f"Fees: ${performance_metrics['total_fees']:,.2f}"
        )
    
    with col2:
        st.metric(
            "📈 Current Value", 
            f"${performance_metrics['current_value']:,.2f}",
            f"{performance_metrics['total_return_pct']:+.2f}%"
        )
    
    with col3:
        pnl_color = "normal" if performance_metrics['total_unrealized_pnl'] >= 0 else "inverse"
        st.metric(
            "💵 Unrealized P&L",
            f"${performance_metrics['total_unrealized_pnl']:,.2f}",
            delta_color=pnl_color
        )
    
    with col4:
        st.metric(
            "📅 Days Invested",
            f"{performance_metrics['days_invested']} days",
            f"Holdings: {len(holdings)}"
        )
    
    st.divider()
    
    # Holdings table
    st.subheader("📋 Current Holdings")
    
    # Format holdings for display
    display_holdings = holdings.copy()
    display_holdings['unrealized_pnl_pct'] = display_holdings['unrealized_pnl_pct'].apply(
        lambda x: f"{x:+.2f}%" 
    )
    display_holdings['unrealized_pnl'] = display_holdings['unrealized_pnl'].apply(
        lambda x: f"${x:+,.2f}"
    )
    
    # Color code the P&L columns
    def color_pnl(val):
        if '+' in str(val):
            return 'color: green'
        elif '-' in str(val):
            return 'color: red'
        return 'color: black'
    
    styled_holdings = display_holdings.style.applymap(
        color_pnl, subset=['unrealized_pnl', 'unrealized_pnl_pct']
    )
    
    st.dataframe(styled_holdings, use_container_width=True)
    
    # Portfolio allocation pie chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🥧 Portfolio Allocation by Value")
        fig_allocation = px.pie(
            holdings,
            values='current_value',
            names='symbol',
            title="Portfolio Allocation"
        )
        st.plotly_chart(fig_allocation, use_container_width=True)
    
    with col2:
        st.subheader("📊 Sector Allocation")
        sector_allocation = holdings.groupby('sector')['current_value'].sum().reset_index()
        fig_sector = px.pie(
            sector_allocation,
            values='current_value', 
            names='sector',
            title="Sector Diversification"
        )
        st.plotly_chart(fig_sector, use_container_width=True)

def performance_analytics_tab(analytics, user_id):
    """Advanced performance analytics and XIRR calculations"""
    st.header("📊 Performance Analytics")
    
    # XIRR calculations
    xirr_results = analytics.calculate_portfolio_xirr(user_id)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Portfolio XIRR")
        portfolio_xirr = xirr_results['portfolio_xirr']
        
        if portfolio_xirr is not None:
            color = "green" if portfolio_xirr > 0 else "red"
            st.markdown(
                f'<h2 style="color: {color};">{portfolio_xirr:+.2f}%</h2>',
                unsafe_allow_html=True
            )
            st.write("**Extended Internal Rate of Return (Annualized)**")
        else:
            st.warning("Unable to calculate XIRR (insufficient data)")
    
    with col2:
        st.subheader("📈 Performance Summary")
        performance_metrics = analytics.calculate_performance_metrics(user_id)
        
        if performance_metrics.get('top_performer'):
            st.success(
                f"🏆 **Top Performer:** {performance_metrics['top_performer']['symbol']} "
                f"({performance_metrics['top_performer']['return_pct']:+.2f}%)"
            )
        
        if performance_metrics.get('bottom_performer'):
            st.error(
                f"📉 **Bottom Performer:** {performance_metrics['bottom_performer']['symbol']} "
                f"({performance_metrics['bottom_performer']['return_pct']:+.2f}%)"
            )
    
    st.divider()
    
    # Individual stock XIRR
    st.subheader("🔍 Individual Stock XIRR")
    
    individual_xirr = xirr_results['individual_xirr']
    
    if individual_xirr:
        xirr_df = pd.DataFrame([
            {'Symbol': symbol, 'XIRR (%)': xirr if xirr is not None else 'N/A'}
            for symbol, xirr in individual_xirr.items()
        ])
        
        # Create bar chart for XIRR
        valid_xirr = {k: v for k, v in individual_xirr.items() if v is not None}
        
        if valid_xirr:
            fig_xirr = go.Figure(data=[
                go.Bar(
                    x=list(valid_xirr.keys()),
                    y=list(valid_xirr.values()),
                    marker_color=['green' if x > 0 else 'red' for x in valid_xirr.values()]
                )
            ])
            fig_xirr.update_layout(
                title="Individual Stock XIRR Performance",
                xaxis_title="Stock Symbol",
                yaxis_title="XIRR (%)",
                showlegend=False
            )
            st.plotly_chart(fig_xirr, use_container_width=True)
        
        st.dataframe(xirr_df, use_container_width=True)
    else:
        st.info("No XIRR data available for individual stocks")

def diversification_analysis_tab(analytics, user_id):
    """Portfolio diversification analysis"""
    st.header("🎯 Diversification Analysis")
    
    diversification_metrics = analytics.calculate_diversification_metrics(user_id)
    
    if not diversification_metrics:
        st.warning("No diversification data available")
        return
    
    # Diversification score
    col1, col2, col3 = st.columns(3)
    
    with col1:
        score = diversification_metrics['diversification_score']
        score_color = {
            'Well Diversified': 'green',
            'Moderately Diversified': 'orange', 
            'Concentrated': 'red'
        }.get(score, 'blue')
        
        st.markdown(f'<h3 style="color: {score_color};">🎯 {score}</h3>', unsafe_allow_html=True)
    
    with col2:
        st.metric(
            "🏢 Sectors",
            diversification_metrics['sector_count'],
            "Different sectors"
        )
    
    with col3:
        st.metric(
            "🔍 Concentration Risk",
            f"{diversification_metrics['top_3_concentration']:.1f}%",
            "Top 3 holdings"
        )
    
    st.divider()
    
    # Detailed diversification charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏢 Sector Diversification")
        sector_data = diversification_metrics['sector_allocation']
        
        if sector_data:
            sector_df = pd.DataFrame([
                {'Sector': sector, 'Allocation (%)': allocation}
                for sector, allocation in sector_data.items()
            ])
            
            fig_sector = px.bar(
                sector_df,
                x='Sector',
                y='Allocation (%)',
                title="Portfolio Allocation by Sector"
            )
            st.plotly_chart(fig_sector, use_container_width=True)
    
    with col2:
        st.subheader("🏭 Industry Diversification")
        industry_data = diversification_metrics['industry_allocation']
        
        if industry_data:
            industry_df = pd.DataFrame([
                {'Industry': industry, 'Allocation (%)': allocation}
                for industry, allocation in industry_data.items()
            ])
            
            fig_industry = px.bar(
                industry_df,
                x='Industry',
                y='Allocation (%)',
                title="Portfolio Allocation by Industry"
            )
            st.plotly_chart(fig_industry, use_container_width=True)
    
    # Risk metrics
    st.subheader("⚠️ Risk Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        hhi = diversification_metrics['hhi_concentration']
        st.metric("📊 HHI Concentration Index", f"{hhi:.0f}")
        
        if hhi < 1500:
            st.success("Low concentration risk")
        elif hhi < 2500:
            st.warning("Moderate concentration risk")
        else:
            st.error("High concentration risk")
    
    with col2:
        top_3 = diversification_metrics['top_3_concentration']
        st.metric("🎯 Top 3 Holdings", f"{top_3:.1f}%")
        
        if top_3 < 50:
            st.success("Well diversified")
        elif top_3 < 75:
            st.warning("Moderately concentrated")
        else:
            st.error("Highly concentrated")

def historical_performance_tab(analytics, user_id):
    """Historical portfolio performance"""
    st.header("📈 Historical Performance")
    
    # Date range selector
    col1, col2 = st.columns(2)
    
    with col1:
        days_back = st.selectbox(
            "📅 Time Period",
            options=[7, 14, 30, 60, 90],
            index=2,
            format_func=lambda x: f"Last {x} days"
        )
    
    # Generate timeline
    timeline = analytics.generate_portfolio_timeline(user_id, days=days_back)
    
    if timeline.empty:
        st.warning("No historical data available for the selected period")
        return
    
    # Portfolio value chart
    fig_timeline = px.line(
        timeline,
        x='date',
        y='portfolio_value',
        title=f"Portfolio Value Over Last {days_back} Days"
    )
    fig_timeline.update_layout(
        xaxis_title="Date",
        yaxis_title="Portfolio Value ($)",
        hovermode='x'
    )
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Performance statistics
    if len(timeline) > 1:
        start_value = timeline.iloc[0]['portfolio_value']
        end_value = timeline.iloc[-1]['portfolio_value']
        total_return = ((end_value - start_value) / start_value) * 100
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📅 Start Value", f"${start_value:,.2f}")
        
        with col2:
            st.metric("📈 End Value", f"${end_value:,.2f}")
        
        with col3:
            color = "normal" if total_return >= 0 else "inverse"
            st.metric("📊 Period Return", f"{total_return:+.2f}%", delta_color=color)

def stock_research_tab(data_models):
    """Stock research and metadata exploration"""
    st.header("🔍 Stock Research")
    
    # Stock metadata table
    st.subheader("📊 Stock Universe")
    
    if not data_models.dim_stock.empty:
        research_df = data_models.dim_stock[[
            'symbol', 'company_name', 'sector', 'industry', 
            'exchange', 'country', 'currency'
        ]].copy()
        
        st.dataframe(research_df, use_container_width=True)
        
        # Stock details
        selected_symbol = st.selectbox(
            "🔎 Select Stock for Details",
            options=data_models.dim_stock['symbol'].tolist()
        )
        
        if selected_symbol:
            stock_details = data_models.dim_stock[
                data_models.dim_stock['symbol'] == selected_symbol
            ].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(f"📈 {stock_details['company_name']}")
                st.write(f"**Symbol:** {stock_details['symbol']}")
                st.write(f"**Sector:** {stock_details['sector']}")
                st.write(f"**Industry:** {stock_details['industry']}")
                st.write(f"**Exchange:** {stock_details['exchange']}")
                st.write(f"**Country:** {stock_details['country']}")
            
            with col2:
                # Recent price chart
                price_data = data_models.stg_stock_price[
                    data_models.stg_stock_price['symbol'] == selected_symbol
                ].sort_values('date')
                
                if not price_data.empty:
                    fig_price = px.line(
                        price_data,
                        x='date',
                        y='close',
                        title=f"{selected_symbol} Price History"
                    )
                    st.plotly_chart(fig_price, use_container_width=True)
    else:
        st.info("No stock metadata available")

def data_management_tab(data_models):
    """Data management and refresh operations"""
    st.header("⚙️ Data Management")
    
    # Data refresh status
    st.subheader("🔄 Data Refresh Status")
    
    if not data_models.meta_refresh_log.empty:
        refresh_log = data_models.meta_refresh_log.sort_values('refresh_date', ascending=False)
        st.dataframe(refresh_log, use_container_width=True)
    else:
        st.info("No refresh logs available")
    
    # Manual refresh options
    st.subheader("🔄 Manual Data Refresh")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Refresh Stock Metadata"):
            with st.spinner("Refreshing stock metadata..."):
                symbols = ['AAPL', 'TSLA', 'INFY']  # Could be made configurable
                data_models.fetch_stock_metadata(symbols)
                data_models.log_refresh('dim_stock', len(data_models.dim_stock), 'SUCCESS')
                st.success("Stock metadata refreshed!")
                st.experimental_rerun()
    
    with col2:
        if st.button("📈 Refresh Price Data"):
            with st.spinner("Refreshing price data..."):
                symbols = ['AAPL', 'TSLA', 'INFY']
                data_models.fetch_stock_prices(symbols, days=30)
                data_models.log_refresh('stg_stock_price', len(data_models.stg_stock_price), 'SUCCESS')
                st.success("Price data refreshed!")
                st.experimental_rerun()
    
    # Export functionality
    st.subheader("📥 Export Data")
    
    export_options = st.multiselect(
        "Select data to export:",
        options=['Stock Metadata', 'Price Data', 'Transactions', 'Users'],
        default=['Stock Metadata']
    )
    
    if st.button("📤 Export Selected Data"):
        export_data = {}
        
        if 'Stock Metadata' in export_options:
            export_data['stock_metadata.csv'] = data_models.dim_stock.to_csv(index=False)
        
        if 'Price Data' in export_options:
            export_data['price_data.csv'] = data_models.stg_stock_price.to_csv(index=False)
        
        if 'Transactions' in export_options:
            export_data['transactions.csv'] = data_models.fact_portfolio_transactions.to_csv(index=False)
        
        if 'Users' in export_options:
            export_data['users.csv'] = data_models.dim_user.to_csv(index=False)
        
        for filename, data in export_data.items():
            st.download_button(
                label=f"Download {filename}",
                data=data,
                file_name=filename,
                mime='text/csv'
            )

def portfolio_insights_tab(insights_engine, selected_user, data_models):
    """
    Advanced Portfolio Insights Tab with time-period analysis
    """
    st.header("💡 Portfolio Insights & Analysis")
    st.markdown("**Deep dive into your portfolio performance with market context**")
    
    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "📅 Start Date",
            value=datetime.now() - timedelta(days=90),
            max_value=datetime.now()
        )
    with col2:
        end_date = st.date_input(
            "📅 End Date", 
            value=datetime.now(),
            max_value=datetime.now()
        )
    
    if start_date >= end_date:
        st.error("Start date must be before end date")
        return
    
    if st.button("🔍 Generate Insights", type="primary"):
        with st.spinner("Analyzing portfolio performance and market events..."):
            try:
                insights = insights_engine.get_period_insights(
                    selected_user, 
                    start_date.strftime('%Y-%m-%d'), 
                    end_date.strftime('%Y-%m-%d')
                )
                
                if "error" in insights:
                    st.error(insights["error"])
                    return
                
                # Portfolio Overview
                st.subheader("📊 Portfolio Performance Overview")
                overview = insights["portfolio_overview"]
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric(
                        "Start Value", 
                        f"${overview['start_value']:,.2f}"
                    )
                with col2:
                    st.metric(
                        "End Value", 
                        f"${overview['end_value']:,.2f}"
                    )
                with col3:
                    st.metric(
                        "Total Return", 
                        f"${overview['absolute_return']:,.2f}",
                        f"{overview['percentage_return']:.2f}%"
                    )
                with col4:
                    st.metric(
                        "Annualized Return", 
                        f"{overview['annualized_return']:.2f}%"
                    )
                
                # Stock Performance Analysis
                st.subheader("📈 Individual Stock Performance")
                
                stock_performance = insights["stock_performance"]
                if stock_performance:
                    perf_data = []
                    for stock in stock_performance:
                        perf_data.append({
                            "Stock": stock.symbol,
                            "Company": stock.company_name,
                            "Price Change": f"{stock.price_change_pct:.2f}%",
                            "Portfolio Impact": f"${stock.portfolio_impact:.2f}",
                            "Performance": stock.performance_rating,
                            "Volume Change": f"{stock.volume_change_pct:.1f}%"
                        })
                    
                    df_performance = pd.DataFrame(perf_data)
                    st.dataframe(df_performance, use_container_width=True)
                    
                    # Top performer and worst performer
                    best_stock = max(stock_performance, key=lambda x: x.price_change_pct)
                    worst_stock = min(stock_performance, key=lambda x: x.price_change_pct)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.success(f"🏆 **Best Performer**: {best_stock.symbol} (+{best_stock.price_change_pct:.2f}%)")
                        if best_stock.key_events:
                            st.write("**Key Events:**")
                            for event in best_stock.key_events:
                                st.write(f"• {event}")
                    
                    with col2:
                        st.error(f"📉 **Worst Performer**: {worst_stock.symbol} ({worst_stock.price_change_pct:.2f}%)")
                        if worst_stock.key_events:
                            st.write("**Key Events:**")
                            for event in worst_stock.key_events:
                                st.write(f"• {event}")
                
                # Portfolio Impact Analysis
                st.subheader("🎯 Portfolio Impact Analysis")
                impact_analysis = insights["portfolio_impact_analysis"]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Top Contributors to Returns:**")
                    for contrib in impact_analysis["top_contributors"]:
                        st.write(f"• {contrib['symbol']}: +${contrib['impact']:.2f} ({contrib['contribution_pct']:.1f}%)")
                
                with col2:
                    st.write("**Top Detractors from Returns:**")
                    for detractor in impact_analysis["top_detractors"]:
                        st.write(f"• {detractor['symbol']}: ${detractor['impact']:.2f} ({detractor['contribution_pct']:.1f}%)")
                
                # Market Events
                st.subheader("📰 Market Events During Period")
                market_events = insights["market_events"]
                
                if market_events:
                    for event in market_events:
                        with st.expander(f"📅 {event['date']} - {event['event_type']} ({event['impact_level']} Impact)"):
                            st.write(event['description'])
                            st.write(f"**Affected Sectors**: {', '.join(event['affected_sectors'])}")
                else:
                    st.info("No significant market events recorded for this period")
                
                # Sector Analysis
                st.subheader("🏭 Sector Performance Analysis")
                sector_analysis = insights["sector_analysis"]
                
                if sector_analysis:
                    sector_data = []
                    for sector, data in sector_analysis.items():
                        sector_data.append({
                            "Sector": sector,
                            "Average Performance": f"{data['average_performance']:.2f}%",
                            "Total Impact": f"${data['total_impact']:.2f}",
                            "Stock Count": data['stock_count']
                        })
                    
                    df_sectors = pd.DataFrame(sector_data)
                    st.dataframe(df_sectors, use_container_width=True)
                
                # Risk Insights
                st.subheader("⚠️ Risk Analysis")
                risk_insights = insights["risk_insights"]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Portfolio Risk Level", risk_insights["risk_level"])
                with col2:
                    if risk_insights["highest_risk_stock"]:
                        st.metric(
                            "Highest Risk Stock", 
                            risk_insights["highest_risk_stock"]["symbol"],
                            f"{risk_insights['highest_risk_stock']['volatility']:.1f}% volatility"
                        )
                with col3:
                    st.metric("Diversification", f"{risk_insights['portfolio_diversification']} stocks")
                
                # Recommendations
                st.subheader("💰 AI-Generated Recommendations")
                recommendations = insights["recommendations"]
                
                if recommendations:
                    for i, rec in enumerate(recommendations, 1):
                        st.write(f"{i}. {rec}")
                else:
                    st.info("No specific recommendations at this time. Your portfolio appears well-balanced.")
                
                # Advanced Analytics Chart
                st.subheader("📊 Performance Visualization")
                
                # Create performance comparison chart
                symbols = [stock.symbol for stock in stock_performance]
                performance_pct = [stock.price_change_pct for stock in stock_performance]
                impact_values = [stock.portfolio_impact for stock in stock_performance]
                
                fig = make_subplots(
                    rows=1, cols=2,
                    subplot_titles=("Stock Performance %", "Portfolio Impact $"),
                    specs=[[{"secondary_y": False}, {"secondary_y": False}]]
                )
                
                # Performance chart
                colors = ['green' if p > 0 else 'red' for p in performance_pct]
                fig.add_trace(
                    go.Bar(x=symbols, y=performance_pct, name="Performance %", marker_color=colors),
                    row=1, col=1
                )
                
                # Impact chart
                colors_impact = ['green' if i > 0 else 'red' for i in impact_values]
                fig.add_trace(
                    go.Bar(x=symbols, y=impact_values, name="Impact $", marker_color=colors_impact),
                    row=1, col=2
                )
                
                fig.update_layout(
                    title="Stock Performance & Portfolio Impact Analysis",
                    showlegend=False,
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error generating insights: {str(e)}")
                st.info("This might be due to network connectivity or data availability issues.")

if __name__ == "__main__":
    main()
