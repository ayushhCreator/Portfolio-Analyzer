#!/usr/bin/env python3
"""
Simple XIRR test to debug date issues
"""

import pandas as pd
from pyxirr import xirr as calculate_xirr
from datetime import datetime, date

def test_simple_xirr():
    # Simple test case
    cashflows = [-1000.0, -1000.0, 3000.0]  # Invest $1000 twice, get back $3000
    dates = [
        date(2023, 1, 1),
        date(2023, 6, 1), 
        date(2024, 1, 1)
    ]
    
    print("Testing simple XIRR calculation...")
    print(f"Cashflows: {cashflows}")
    print(f"Dates: {dates}")
    print(f"Date types: {[type(d).__name__ for d in dates]}")
    
    try:
        result = calculate_xirr(cashflows, dates)
        print(f"✅ XIRR result: {result*100:.2f}%")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test with pandas timestamp
    pd_dates = [pd.Timestamp(d) for d in dates]
    print(f"\nTesting with pandas timestamps...")
    print(f"PD Date types: {[type(d).__name__ for d in pd_dates]}")
    
    try:
        result = calculate_xirr(cashflows, pd_dates)
        print(f"✅ XIRR result with pandas: {result*100:.2f}%")
    except Exception as e:
        print(f"❌ Error with pandas: {e}")
        
    # Test converting pandas to date
    converted_dates = [d.date() if hasattr(d, 'date') else d for d in pd_dates]
    print(f"\nTesting with converted dates...")
    print(f"Converted Date types: {[type(d).__name__ for d in converted_dates]}")
    
    try:
        result = calculate_xirr(cashflows, converted_dates)
        print(f"✅ XIRR result with converted: {result*100:.2f}%")
    except Exception as e:
        print(f"❌ Error with converted: {e}")

if __name__ == "__main__":
    test_simple_xirr()
