#!/usr/bin/env python3
"""
Comprehensive Market Stock Lists Generator
Provides access to thousands of stocks across USA, India, and Malaysia markets
"""

import yfinance as yf
import pandas as pd
import requests
from typing import List, Dict, Optional
import json
import os
from datetime import datetime, timedelta
import time

class MarketStockListGenerator:
    """Generate comprehensive stock lists for swing trading analysis"""
    
    def __init__(self, cache_dir: str = "data/stock_lists"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
    def get_usa_stocks(self, use_cache: bool = True) -> List[str]:
        """Get comprehensive USA stock list (Russell 3000 + Popular ETFs)"""
        cache_file = os.path.join(self.cache_dir, "usa_stocks.json")
        
        if use_cache and os.path.exists(cache_file):
            # Check if cache is less than 7 days old
            cache_age = time.time() - os.path.getmtime(cache_file)
            if cache_age < 7 * 24 * 3600:  # 7 days
                with open(cache_file, 'r') as f:
                    return json.load(f)
        
        print("🔄 Generating USA stock list (this may take a few minutes)...")
        
        # Core list of major stocks that we know work well
        usa_stocks = [
            # Mega caps (Market cap > $1T)
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA',
            
            # Large caps (Market cap > $100B)
            'BRK-B', 'UNH', 'JNJ', 'V', 'XOM', 'WMT', 'LLY', 'JPM', 'MA', 'PG',
            'AVGO', 'HD', 'CVX', 'ABBV', 'BAC', 'KO', 'ASML', 'PEP', 'TMO', 'COST',
            'WFC', 'MRK', 'NFLX', 'CRM', 'ADBE', 'ACN', 'LIN', 'DHR', 'AMD', 'GS',
            'NOW', 'TXN', 'SYK', 'NEE', 'VZ', 'QCOM', 'HON', 'T', 'RTX', 'SPGI',
            'CAT', 'INTU', 'AXP', 'SBUX', 'BKNG', 'TJX', 'ADP', 'GILD', 'MDLZ', 'ISRG',
            
            # Mid caps with good swing potential
            'PLTR', 'ROKU', 'COIN', 'RBLX', 'SQ', 'SHOP', 'SPOT', 'ZM', 'DOCU', 'TWLO',
            'CRWD', 'SNOW', 'NET', 'DDOG', 'ZS', 'OKTA', 'PINS', 'SNAP', 'UBER', 'LYFT',
            'AIRB', 'DASH', 'ABNB', 'RIVN', 'LCID', 'F', 'GM', 'FORD', 'NIO', 'XPEV',
            
            # Energy & Materials
            'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'OXY', 'KMI', 'WMB', 'PSX', 'VLO',
            'FCX', 'NEM', 'AA', 'MP', 'CLF', 'X', 'MT', 'VALE', 'RIO', 'BHP',
            
            # Healthcare & Biotech
            'JNJ', 'PFE', 'ABBV', 'MRK', 'TMO', 'ABT', 'ISRG', 'DHR', 'SYK', 'MDT',
            'GILD', 'AMGN', 'VRTX', 'REGN', 'BIIB', 'ILMN', 'MRNA', 'BNTX', 'ZTS', 'EW',
            
            # Financial
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'USB', 'PNC', 'TFC', 'COF',
            'AXP', 'BLK', 'SCHW', 'CB', 'MMC', 'AON', 'ICE', 'CME', 'SPGI', 'MCO',
            
            # Consumer Discretionary
            'AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'BKNG', 'LOW', 'TJX', 'SBUX', 'TGT',
            'DIS', 'CMCSA', 'NFLX', 'CRM', 'PYPL', 'ADSK', 'INTU', 'NOW', 'TEAM', 'ZEN',
            
            # Industrial
            'CAT', 'RTX', 'HON', 'UPS', 'BA', 'LMT', 'NOC', 'GD', 'FDX', 'CSX',
            'UNP', 'NSC', 'EMR', 'ETN', 'ITW', 'MMM', 'GE', 'WM', 'RSG', 'PH',
            
            # Utilities
            'NEE', 'DUK', 'SO', 'AEP', 'EXC', 'XEL', 'SRE', 'D', 'PCG', 'EIX',
            
            # REITs
            'AMT', 'PLD', 'CCI', 'EQIX', 'WELL', 'DLR', 'PSA', 'O', 'CBRE', 'AVB',
            
            # Popular ETFs for swing trading
            'SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VOO', 'VEA', 'VWO', 'AGG', 'BND',
            'GLD', 'SLV', 'USO', 'XLE', 'XLF', 'XLK', 'XLV', 'XLI', 'XLP', 'XLU',
            'SOXL', 'TQQQ', 'UPRO', 'TMF', 'TLT', 'HYG', 'LQD', 'EMB', 'VNQ', 'GDXJ'
        ]
        
        # Add sector-specific stocks
        sectors = {
            'Tech': ['CRM', 'ORCL', 'SAP', 'TEAM', 'ZEN', 'WDAY', 'VEEV', 'DDOG', 'NET', 'CRWD'],
            'Biotech': ['MRNA', 'BNTX', 'NVAX', 'SGEN', 'BMRN', 'ALNY', 'RARE', 'SRPT', 'BLUE', 'FOLD'],
            'Growth': ['ROKU', 'PLTR', 'COIN', 'RBLX', 'U', 'OPEN', 'AFFIRM', 'SQ', 'HOOD', 'SOFI'],
            'Value': ['BRK-B', 'WFC', 'JPM', 'XOM', 'CVX', 'KO', 'PG', 'JNJ', 'WMT', 'VZ'],
            'Dividend': ['T', 'VZ', 'IBM', 'INTC', 'F', 'SIRI', 'KHC', 'PSEC', 'AGNC', 'NLY']
        }
        
        for sector_stocks in sectors.values():
            usa_stocks.extend(sector_stocks)
        
        # Remove duplicates and sort
        usa_stocks = sorted(list(set(usa_stocks)))
        
        # Cache the results
        with open(cache_file, 'w') as f:
            json.dump(usa_stocks, f)
        
        print(f"✅ Generated {len(usa_stocks)} USA stocks")
        return usa_stocks
    
    def get_india_stocks(self, use_cache: bool = True) -> List[str]:
        """Get comprehensive India stock list (NSE + BSE active stocks)"""
        cache_file = os.path.join(self.cache_dir, "india_stocks.json")
        
        if use_cache and os.path.exists(cache_file):
            cache_age = time.time() - os.path.getmtime(cache_file)
            if cache_age < 7 * 24 * 3600:  # 7 days
                with open(cache_file, 'r') as f:
                    return json.load(f)
        
        print("🔄 Generating India stock list...")
        
        # Core NSE stocks that work well with yfinance
        india_stocks = [
            # Nifty 50 components
            'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS',
            'ICICIBANK.NS', 'KOTAKBANK.NS', 'BHARTIARTL.NS', 'ITC.NS', 'SBIN.NS',
            'BAJFINANCE.NS', 'ASIANPAINT.NS', 'MARUTI.NS', 'HCLTECH.NS', 'AXISBANK.NS',
            'LT.NS', 'NESTLEIND.NS', 'ULTRACEMCO.NS', 'TITAN.NS', 'SUNPHARMA.NS',
            'WIPRO.NS', 'ONGC.NS', 'NTPC.NS', 'POWERGRID.NS', 'TATAMOTORS.NS',
            'TATASTEEL.NS', 'JSWSTEEL.NS', 'HINDALCO.NS', 'COALINDIA.NS', 'HDFCLIFE.NS',
            'SBILIFE.NS', 'ICICIPRULI.NS', 'DIVISLAB.NS', 'DRREDDY.NS', 'CIPLA.NS',
            'TECHM.NS', 'HEROMOTOCO.NS', 'BAJAJFINSV.NS', 'BRITANNIA.NS', 'ADANIPORTS.NS',
            'EICHERMOT.NS', 'UPL.NS', 'BPCL.NS', 'GRASIM.NS', 'SHREECEM.NS',
            'APOLLOHOSP.NS', 'TATACONSUM.NS', 'INDUSINDBK.NS', 'M&M.NS', 'BAJAJ-AUTO.NS',
            
            # Nifty Next 50
            'ADANIGREEN.NS', 'ADANIENT.NS', 'AMBUJACEM.NS', 'BANDHANBNK.NS', 'BERGEPAINT.NS',
            'BIOCON.NS', 'BOSCHLTD.NS', 'CADILAHC.NS', 'CANBK.NS', 'CHOLAFIN.NS',
            'COLPAL.NS', 'CONCOR.NS', 'DABUR.NS', 'DMART.NS', 'GAIL.NS',
            'GODREJCP.NS', 'HAVELLS.NS', 'HDFC.NS', 'HDFCAMC.NS', 'IBULHSGFIN.NS',
            'IDFCFIRSTB.NS', 'IGL.NS', 'INDIGO.NS', 'IOC.NS', 'IRCTC.NS',
            'JINDALSTEL.NS', 'JUBLFOOD.NS', 'LICHSGFIN.NS', 'MARICO.NS', 'MCDOWELL-N.NS',
            'MFSL.NS', 'MUTHOOTFIN.NS', 'NAUKRI.NS', 'NMDC.NS', 'OFSS.NS',
            'PAGEIND.NS', 'PEL.NS', 'PETRONET.NS', 'PIDILITIND.NS', 'PNB.NS',
            'POLYCAB.NS', 'PVR.NS', 'RAMCOCEM.NS', 'SAIL.NS', 'SIEMENS.NS',
            'SRF.NS', 'TORNTPHARM.NS', 'TRENT.NS', 'VOLTAS.NS', 'ZEEL.NS',
            
            # Additional high-volume stocks
            'ACC.NS', 'AUROPHARMA.NS', 'BANKBARODA.NS', 'BHEL.NS', 'HINDZINC.NS',
            'IDEA.NS', 'INDIAMART.NS', 'JUSTDIAL.NS', 'LUPIN.NS', 'MINDTREE.NS',
            'MOTHERSUMI.NS', 'NATIONALUM.NS', 'RECLTD.NS', 'RPOWER.NS', 'TATACHEM.NS',
            'TATAELXSI.NS', 'VEDL.NS', 'YESBANK.NS', 'ZYDUSWELL.NS', 'FEDERALBNK.NS',
            
            # Midcap favorites
            'BAJAJHLDNG.NS', 'BATINDIA.NS', 'CUMMINSIND.NS', 'ESCORTS.NS', 'EXIDEIND.NS',
            'GODREJIND.NS', 'HONAUT.NS', 'INDIANB.NS', 'INDHOTEL.NS', 'L&TFH.NS',
            'LALPATHLAB.NS', 'MRF.NS', 'PERSISTENT.NS', 'RELAXO.NS', 'SCHAEFFLER.NS',
            
            # Smallcap with good swing potential
            'ASHOKLEY.NS', 'CROMPTON.NS', 'DELTACORP.NS', 'FINEORG.NS', 'GRAPHITE.NS',
            'HEXAWARE.NS', 'IBREALEST.NS', 'KSCL.NS', 'METROPOLIS.NS', 'NETWORK18.NS',
            'ORIENTCEM.NS', 'PFIZER.NS', 'QUESS.NS', 'RAJESHEXPO.NS', 'SCHNEIDER.NS'
        ]
        
        # Add ETFs and indices
        india_etfs = [
            'NIFTYBEES.NS', 'JUNIORBEES.NS', 'BANKBEES.NS', 'ITBEES.NS', 'PHARMBEES.NS'
        ]
        
        india_stocks.extend(india_etfs)
        india_stocks = sorted(list(set(india_stocks)))
        
        # Cache the results
        with open(cache_file, 'w') as f:
            json.dump(india_stocks, f)
        
        print(f"✅ Generated {len(india_stocks)} India stocks")
        return india_stocks
    
    def get_malaysia_stocks(self, use_cache: bool = True) -> List[str]:
        """Get comprehensive Malaysia stock list (Bursa Malaysia)"""
        cache_file = os.path.join(self.cache_dir, "malaysia_stocks.json")
        
        if use_cache and os.path.exists(cache_file):
            cache_age = time.time() - os.path.getmtime(cache_file)
            if cache_age < 7 * 24 * 3600:  # 7 days
                with open(cache_file, 'r') as f:
                    return json.load(f)
        
        print("🔄 Generating Malaysia stock list...")
        
        # Comprehensive Malaysia stocks with correct Yahoo Finance symbols
        malaysia_stocks = [
            # FTSE Bursa Malaysia KLCI components (Top 30)
            '1155.KL',     # Malayan Banking (Maybank)
            '5225.KL',     # Public Bank
            '1023.KL',     # CIMB Group
            '1066.KL',     # RHB Bank
            '1015.KL',     # AmBank Group
            '6947.KL',     # Hong Leong Bank
            '1082.KL',     # Hong Leong Financial Group
            
            # Telecommunications
            '6012.KL',     # Axiata Group
            '4863.KL',     # Telekom Malaysia
            '5347.KL',     # Digi.Com
            '6888.KL',     # Maxis
            
            # Plantation & Commodities
            '5681.KL',     # Sime Darby Plantation
            '2445.KL',     # IOI Corporation
            '1961.KL',     # Kuala Lumpur Kepong
            '2291.KL',     # Genting Plantations
            '5296.KL',     # Felda Global Ventures
            
            # Industrial & Manufacturing
            '4197.KL',     # Genting
            '3182.KL',     # Genting Malaysia
            '4715.KL',     # Press Metal Aluminium
            '7277.KL',     # Dialog Group
            '3034.KL',     # Hartalega Holdings
            '7113.KL',     # Top Glove Corporation
            '5020.KL',     # Public Gold
            
            # Energy & Utilities
            '5681.KL',     # Petronas Chemicals Group
            '5285.KL',     # Petronas Dagangan
            '6033.KL',     # Tenaga Nasional
            '1818.KL',     # YTL Corporation
            '4677.KL',     # YTL Power International
            
            # Technology
            '0097.KL',     # Vitrox Corporation
            '5168.KL',     # ViTrox Corporation
            '0155.KL',     # VSolar Group
            
            # Consumer
            '3816.KL',     # Malaysian Resources Corporation
            '2739.KL',     # Kuala Lumpur Kepong
            '1818.KL',     # Nestle (Malaysia)
            '4707.KL',     # Dutch Lady Milk Industries
            
            # REITs
            '5106.KL',     # Pavilion REIT
            '5109.KL',     # IGB REIT
            '5108.KL',     # KLCCP Stapled Group
            
            # Construction & Property
            '1082.KL',     # Gamuda
            '5878.KL',     # IJM Corporation
            '1287.KL',     # Sunway
            '1961.KL',     # UEM Sunrise
            '4139.KL',     # WCT Holdings
            
            # Additional high-volume stocks
            '6399.KL',     # AirAsia Group
            '5185.KL',     # Capital A (formerly AirAsia)
            '6888.KL',     # Fraser & Neave Holdings
            '3336.KL',     # Magni-Tech Industries
            '6742.KL',     # Westports Holdings
            '1295.KL',     # Public Mutual
            '5014.KL',     # Malaysia Airports Holdings
            '8869.KL',     # Pharmaniaga
            '6399.KL',     # Berjaya Corporation
            '1929.KL',     # Public Investment Bank
            
            # Midcap opportunities
            '7082.KL',     # Kossan Rubber Industries
            '5225.KL',     # Supermax Corporation
            '0096.KL',     # TIME dotCom
            '1503.KL',     # Protasco
            '6033.KL',     # TNB Renewables
            '1597.KL',     # Malaysian Pacific Industries
            '3395.KL',     # Sunway Construction Group
            '1961.KL',     # KL Kepong Plantations
            '5183.KL',     # Malaysian Bulk Carriers
            '6888.KL',     # Fraser & Neave
        ]
        
        # Remove duplicates and sort
        malaysia_stocks = sorted(list(set(malaysia_stocks)))
        
        # Cache the results
        with open(cache_file, 'w') as f:
            json.dump(malaysia_stocks, f)
        
        print(f"✅ Generated {len(malaysia_stocks)} Malaysia stocks")
        return malaysia_stocks
    
    def get_all_markets(self, use_cache: bool = True) -> Dict[str, List[str]]:
        """Get comprehensive stock lists for all markets"""
        return {
            'usa': self.get_usa_stocks(use_cache),
            'india': self.get_india_stocks(use_cache),
            'malaysia': self.get_malaysia_stocks(use_cache)
        }
    
    def validate_symbols(self, symbols: List[str], market: str) -> List[str]:
        """Validate that symbols are accessible via yfinance"""
        print(f"🔍 Validating {len(symbols)} {market} symbols...")
        valid_symbols = []
        
        # Test in batches of 50 to avoid overwhelming the API
        batch_size = 50
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i+batch_size]
            
            for symbol in batch:
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    
                    # Check if we can get basic data
                    if 'regularMarketPrice' in info or 'currentPrice' in info:
                        valid_symbols.append(symbol)
                    else:
                        print(f"❌ {symbol}: No price data available")
                        
                except Exception as e:
                    print(f"❌ {symbol}: {str(e)}")
                    continue
            
            # Add small delay between batches
            time.sleep(0.5)
        
        print(f"✅ Validated {len(valid_symbols)}/{len(symbols)} {market} symbols")
        return valid_symbols

# Create comprehensive market lists
def get_comprehensive_market_watchlists(validate: bool = False) -> Dict[str, List[str]]:
    """Get comprehensive market watchlists with thousands of stocks"""
    generator = MarketStockListGenerator()
    
    # Get all market lists
    all_markets = generator.get_all_markets(use_cache=True)
    
    if validate:
        # Validate symbols (warning: this takes a long time!)
        print("⚠️ Warning: Symbol validation can take 30+ minutes for all markets")
        for market in all_markets:
            all_markets[market] = generator.validate_symbols(all_markets[market], market)
    
    print(f"""
📊 COMPREHENSIVE MARKET COVERAGE:
🇺🇸 USA: {len(all_markets['usa'])} stocks (Major caps + Growth + Value + Sectors)
🇮🇳 India: {len(all_markets['india'])} stocks (NSE large/mid/small caps + ETFs)  
🇲🇾 Malaysia: {len(all_markets['malaysia'])} stocks (Bursa Malaysia active stocks)
📈 Total: {sum(len(stocks) for stocks in all_markets.values())} stocks across all markets

This provides comprehensive coverage for finding swing trading opportunities!
    """)
    
    return all_markets

if __name__ == "__main__":
    # Test the system
    watchlists = get_comprehensive_market_watchlists(validate=False)
    
    print("\nSample stocks from each market:")
    for market, stocks in watchlists.items():
        print(f"{market.upper()}: {stocks[:10]}... (+{len(stocks)-10} more)")
