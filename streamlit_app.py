"""
Streamlit Cloud deployment entry point for Enhanced Portfolio Analyzer
"""
import sys
import os

# Add the current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import and run the enhanced app
from src.ui.enhanced_app import main

if __name__ == "__main__":
    main()
