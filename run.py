#!/usr/bin/env python3
"""
Portfolio Analyzer Launcher
Simple script to launch either Flask or Streamlit interface
"""

import sys
import subprocess
import argparse

def run_flask():
    """Launch Flask web application"""
    print("🚀 Starting Flask Portfolio Analyzer...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop")
    subprocess.run([sys.executable, "flask_app.py"])

def run_streamlit():
    """Launch Streamlit dashboard"""
    print("🚀 Starting Streamlit Portfolio Analyzer...")
    print("📊 Dashboard will be available at: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])

def main():
    parser = argparse.ArgumentParser(description="Portfolio Analyzer Launcher")
    parser.add_argument(
        "interface", 
        choices=["flask", "streamlit", "f", "s"],
        help="Interface to launch: 'flask'/'f' for Flask web app, 'streamlit'/'s' for Streamlit dashboard"
    )
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("📊 Portfolio Analyzer")
    print("=" * 50)
    
    if args.interface in ["flask", "f"]:
        run_flask()
    elif args.interface in ["streamlit", "s"]:
        run_streamlit()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("📊 Portfolio Analyzer Launcher")
        print("\nUsage:")
        print("  python run.py flask      # Launch Flask web application")
        print("  python run.py streamlit  # Launch Streamlit dashboard")
        print("  python run.py f          # Short form for Flask")
        print("  python run.py s          # Short form for Streamlit")
        print("\nBoth interfaces provide full portfolio analysis capabilities:")
        print("  • Load and process CSV trading data")
        print("  • Multi-currency support with exchange rates")
        print("  • Stock split adjustments")
        print("  • Portfolio valuation and XIRR calculations")
        print("  • Interactive charts and news integration")
    else:
        main()