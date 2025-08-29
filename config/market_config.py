"""
Market Configuration for Different Countries
"""

# India Market Configuration
INDIA_CONFIG = {
    "timezone": "Asia/Kolkata",
    "market_hours": {
        "start": "09:15",
        "end": "15:30"
    },
    "exchanges": ["NSE", "BSE"],
    "major_indices": [
        "^NSEI",  # Nifty 50
        "^NSEBANK",  # Bank Nifty
        "^BSESN"  # Sensex
    ],
    "currency": "INR",
    "data_sources": ["yfinance", "nsepy"],
    "popular_stocks": [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS",
        "ICICIBANK.NS", "KOTAKBANK.NS", "BHARTIARTL.NS", "ITC.NS", "SBIN.NS"
    ]
}

# Malaysia Market Configuration
MALAYSIA_CONFIG = {
    "timezone": "Asia/Kuala_Lumpur",
    "market_hours": {
        "start": "09:00",
        "end": "17:00"
    },
    "exchanges": ["KLSE"],
    "major_indices": [
        "^KLSE"  # FTSE Bursa Malaysia KLCI
    ],
    "currency": "MYR",
    "data_sources": ["yfinance"],
    "popular_stocks": [
        "1155.KL",  # Maybank
        "5225.KL",  # PPB Group
        "3816.KL",  # MISC
        "6012.KL",  # IOI Corporation
        "1023.KL"   # CIMB Group
    ]
}

# USA Market Configuration
USA_CONFIG = {
    "timezone": "America/New_York",
    "market_hours": {
        "start": "09:30",
        "end": "16:00"
    },
    "exchanges": ["NYSE", "NASDAQ"],
    "major_indices": [
        "^GSPC",  # S&P 500
        "^DJI",   # Dow Jones
        "^IXIC"   # NASDAQ
    ],
    "currency": "USD",
    "data_sources": ["yfinance", "alpha_vantage"],
    "popular_stocks": [
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
        "META", "NVDA", "JPM", "JNJ", "V"
    ]
}

# Common settings
COMMON_CONFIG = {
    "timeframes": ["1d", "1wk", "1mo"],
    "swing_trade_period": "5-20 days",
    "technical_indicators": [
        "SMA", "EMA", "RSI", "MACD", "Bollinger Bands",
        "Stochastic", "Williams %R", "ADX"
    ]
}
