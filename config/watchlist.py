"""
Curated Stock Lists - Best Performers for Swing Trading
"""

# India - Top performing NSE stocks for swing trading
INDIA_SWING_STOCKS = [
    "RELIANCE.NS",      # Reliance Industries - High liquidity, good swings
    "TCS.NS",           # Tata Consultancy Services - Tech leader
    "HDFCBANK.NS",      # HDFC Bank - Banking sector leader
    "INFY.NS",          # Infosys - IT sector
    "HINDUNILVR.NS",    # Hindustan Unilever - FMCG stable
    "ICICIBANK.NS",     # ICICI Bank - Private bank
    "KOTAKBANK.NS",     # Kotak Mahindra Bank
    "BHARTIARTL.NS",    # Bharti Airtel - Telecom
    "ITC.NS",           # ITC Limited - Diversified
    "SBIN.NS",          # State Bank of India
    "LT.NS",            # Larsen & Toubro - Infrastructure
    "ASIANPAINT.NS",    # Asian Paints - Paint leader
    "MARUTI.NS",        # Maruti Suzuki - Auto leader
    "TITAN.NS",         # Titan Company - Jewelry/watches
    "WIPRO.NS"          # Wipro - IT services
]

# Malaysia - Top KLSE stocks with good swing trading potential
MALAYSIA_SWING_STOCKS = [
    "1155.KL",          # Maybank - Malaysia's largest bank
    "5225.KL",          # PPB Group - Diversified conglomerate
    "3816.KL",          # MISC Berhad - Shipping
    "6012.KL",          # IOI Corporation - Palm oil
    "1023.KL",          # CIMB Group - Banking
    "4707.KL",          # Telekom Malaysia
    "1066.KL",          # RHB Bank
    "2445.KL",          # YTL Corporation
    "4863.KL",          # Sime Darby Property
    "1961.KL"           # Genting Malaysia
]

# USA - High-quality swing trading stocks across sectors
USA_SWING_STOCKS = [
    # Technology Leaders
    "AAPL",             # Apple - Consistent performer
    "MSFT",             # Microsoft - Cloud leader
    "GOOGL",            # Alphabet - Search/AI giant
    "NVDA",             # NVIDIA - AI/chip leader
    "AMZN",             # Amazon - E-commerce/cloud
    "TSLA",             # Tesla - EV leader (high volatility)
    "META",             # Meta - Social media
    
    # Financial Sector
    "JPM",              # JPMorgan Chase - Banking leader
    "BAC",              # Bank of America
    "V",                # Visa - Payments
    "MA",               # Mastercard - Payments
    
    # Healthcare
    "JNJ",              # Johnson & Johnson - Pharma giant
    "UNH",              # UnitedHealth - Healthcare
    
    # Consumer
    "KO",               # Coca-Cola - Stable dividend
    "PG",               # Procter & Gamble - Consumer goods
    "WMT",              # Walmart - Retail leader
    
    # Industrial
    "BA",               # Boeing - Aerospace
    "CAT",              # Caterpillar - Heavy machinery
    
    # Energy
    "XOM",              # ExxonMobil - Oil giant
    "CVX"               # Chevron - Energy
]

# Combined watchlist for dashboard
DEFAULT_WATCHLIST = {
    'india': INDIA_SWING_STOCKS,
    'malaysia': MALAYSIA_SWING_STOCKS,
    'usa': USA_SWING_STOCKS
}

# Trading configuration
TRADING_CONFIG = {
    'initial_capital': 10000,
    'max_positions': 8,
    'risk_per_trade': 0.02,  # 2% risk per trade
    'stop_loss_pct': 0.05,   # 5% stop loss
    'take_profit_pct': 0.10, # 10% take profit
    'min_confidence': 70,    # Minimum confidence for trades
    'position_sizing': 'equal_weight'  # or 'risk_based'
}
