"""
Enhanced Portfolio Analyzer - Streamlit Cloud Deployment Version
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

# Streamlit Cloud-friendly path setup
if os.path.exists('/mount/src'):
    # Running on Streamlit Cloud
    sys.path.append('/mount/src/portfolio-analyzer')
else:
    # Running locally
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(current_dir, '..', '..'))

# Import our custom modules
try:
    from src.models.data_models import DataModels
    from src.analytics.portfolio_analytics import PortfolioAnalytics
    from src.analytics.portfolio_insights import PortfolioInsights
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please ensure all required files are in the correct directory structure.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="📈 Enhanced Portfolio Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import the main function from enhanced_app
try:
    from src.ui.enhanced_app import (
        initialize_data_models,
        portfolio_overview_tab,
        performance_analytics_tab,
        diversification_analysis_tab,
        historical_performance_tab,
        transaction_details_tab,
        portfolio_insights_tab,
        stock_research_tab,
        data_management_tab
    )
except ImportError:
    st.error("Could not import required modules. Please check the file structure.")
    st.stop()

def main():
    """Main application entry point"""
    try:
        # Custom CSS
        st.markdown("""
        <style>
        .main-header {
            font-size: 3rem;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-container {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
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
            st.write(f"• Portfolio Transactions: {summary['fact_transactions_records']} records")
            st.write(f"• Users: {summary['dimension_user_records']} users")
        
        # User selection
        st.sidebar.subheader("👤 Select User Portfolio")
        selected_user = st.sidebar.selectbox(
            "Choose Portfolio:",
            options=data_models.dim_user['user_id'].unique(),
            format_func=lambda x: data_models.dim_user[data_models.dim_user['user_id']==x]['user_name'].iloc[0]
        )
        
        # Main navigation
        tab_options = [
            "🏠 Portfolio Overview",
            "📊 Performance Analytics", 
            "🎯 Diversification Analysis",
            "📈 Historical Performance",
            "💰 Transaction Details",
            "🔍 Portfolio Insights",
            "🔍 Stock Research",
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
        
        elif selected_tab == "💰 Transaction Details":
            transaction_details_tab(analytics, selected_user, data_models)
        
        elif selected_tab == "🔍 Portfolio Insights":
            portfolio_insights_tab(insights_engine, selected_user, data_models)
        
        elif selected_tab == "🔍 Stock Research":
            stock_research_tab(analytics, selected_user)
        
        elif selected_tab == "⚙️ Data Management":
            data_management_tab(data_models)
            
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.error("Please check that all required dependencies are installed and files are in the correct locations.")

if __name__ == "__main__":
    main()
