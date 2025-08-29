"""
Data Collector for Multi-Country Market Data
"""

import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta
from typing import List, Dict
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.market_config import INDIA_CONFIG, MALAYSIA_CONFIG, USA_CONFIG

class MarketDataCollector:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        
    def download_stock_data(self, symbols: List[str], country: str, period: str = "1y") -> Dict[str, pd.DataFrame]:
        """
        Download stock data for given symbols
        """
        data = {}
        country_dir = os.path.join(self.data_dir, country.lower())
        
        for symbol in symbols:
            try:
                print(f"Downloading {symbol} data...")
                ticker = yf.Ticker(symbol)
                df = ticker.history(period=period)
                
                if not df.empty:
                    # Save to CSV
                    filename = f"{symbol.replace('.', '_')}.csv"
                    filepath = os.path.join(country_dir, filename)
                    df.to_csv(filepath)
                    data[symbol] = df
                    print(f"✓ {symbol} data saved to {filepath}")
                else:
                    print(f"✗ No data found for {symbol}")
                    
            except Exception as e:
                print(f"✗ Error downloading {symbol}: {str(e)}")
                
        return data
    
    def download_index_data(self, country: str, period: str = "2y"):
        """
        Download major index data for a country
        """
        configs = {
            'india': INDIA_CONFIG,
            'malaysia': MALAYSIA_CONFIG,
            'usa': USA_CONFIG
        }
        
        if country.lower() not in configs:
            print(f"Country {country} not supported")
            return
            
        config = configs[country.lower()]
        indices = config['major_indices']
        
        print(f"\nDownloading {country.upper()} index data...")
        return self.download_stock_data(indices, country, period)
    
    def download_popular_stocks(self, country: str, period: str = "1y"):
        """
        Download popular stocks data for a country
        """
        configs = {
            'india': INDIA_CONFIG,
            'malaysia': MALAYSIA_CONFIG,
            'usa': USA_CONFIG
        }
        
        if country.lower() not in configs:
            print(f"Country {country} not supported")
            return
            
        config = configs[country.lower()]
        stocks = config['popular_stocks']
        
        print(f"\nDownloading {country.upper()} popular stocks...")
        return self.download_stock_data(stocks, country, period)
    
    def collect_all_data(self):
        """
        Collect data for all countries
        """
        countries = ['india', 'malaysia', 'usa']
        
        for country in countries:
            print(f"\n{'='*50}")
            print(f"Collecting data for {country.upper()}")
            print(f"{'='*50}")
            
            # Download indices
            self.download_index_data(country)
            
            # Download popular stocks
            self.download_popular_stocks(country)

if __name__ == "__main__":
    collector = MarketDataCollector()
    collector.collect_all_data()
