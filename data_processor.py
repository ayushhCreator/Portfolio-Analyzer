"""
Data processing module for Portfolio Analyzer
Handles CSV parsing and data management
"""

import pandas as pd
import warnings
from typing import List, Tuple

warnings.filterwarnings('ignore')

class DataProcessor:
    """Handles loading and processing of trading data from CSV files"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        
    def load_and_consolidate_data(self, files: List[str]) -> pd.DataFrame:
        """Load and consolidate data from multiple CSV files"""
        all_trades = []
        
        for file in files:
            try:
                file_path = f"{self.data_dir}/{file}" if self.data_dir else file
                df = pd.read_csv(file_path, thousands=',', on_bad_lines='skip')
                if not df.empty:
                    df['source_file'] = file
                    all_trades.append(df)
            except FileNotFoundError:
                print(f"Error: The file {file} was not found.")
                continue
        
        if not all_trades:
            return pd.DataFrame()
            
        # Consolidate all data
        consolidated_df = pd.concat(all_trades, ignore_index=True)
        consolidated_df = consolidated_df[consolidated_df['Header'] == 'Data'].copy()
        consolidated_df['Date/Time'] = pd.to_datetime(consolidated_df['Date/Time'])
        
        # Clean numeric columns
        numeric_cols = ['Quantity', 'T. Price', 'C. Price', 'Proceeds', 'Comm/Fee', 'Basis', 'Realized P/L', 'MTM P/L']
        for col in numeric_cols:
            consolidated_df[col] = pd.to_numeric(consolidated_df[col], errors='coerce')
        
        # Clean and sort
        consolidated_df.dropna(subset=['Quantity', 'T. Price', 'Date/Time'], inplace=True)
        consolidated_df.sort_values('Date/Time', inplace=True)
        consolidated_df.rename(columns={'T. Price': 'Trade_Price', 'Date/Time': 'Trade_Date'}, inplace=True)
        
        return consolidated_df
    
    def create_master_holdings_list(self, df: pd.DataFrame) -> List[Tuple[str, str]]:
        """Create a master list of holdings from trade data"""
        if df.empty:
            return []
        
        holdings = df[['Symbol', 'Currency']].drop_duplicates()
        holdings_list = [(row['Symbol'], row['Currency']) for _, row in holdings.iterrows()]
        return holdings_list