#!/usr/bin/env python3
"""
Test script to validate dashboard functionality and price accuracy
"""

import yfinance as yf
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.portfolio_manager import PaperTradingPortfolio
from config.watchlist import DEFAULT_WATCHLIST

def test_price_accuracy():
    """Test that our prices match market reality"""
    print("🔍 Testing Price Accuracy")
    print("=" * 50)
    
    test_symbols = {
        'RELIANCE.NS': {'expected_range': (1300, 1400), 'currency': 'INR'},
        'TCS.NS': {'expected_range': (3000, 3200), 'currency': 'INR'},
        'AAPL': {'expected_range': (200, 250), 'currency': 'USD'},
    }
    
    for symbol, expectations in test_symbols.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='1d')
            info = ticker.info
            
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                currency = info.get('currency', 'Unknown')
                min_price, max_price = expectations['expected_range']
                
                print(f"✅ {symbol}:")
                print(f"   Price: {price:.2f} {currency}")
                print(f"   Expected Range: {min_price}-{max_price} {expectations['currency']}")
                print(f"   Within Range: {'✅' if min_price <= price <= max_price else '❌'}")
                print(f"   Currency Match: {'✅' if currency == expectations['currency'] else '❌'}")
                print()
        except Exception as e:
            print(f"❌ {symbol}: Error - {e}\n")

def test_portfolio_functionality():
    """Test portfolio operations"""
    print("🔍 Testing Portfolio Functionality")
    print("=" * 50)
    
    try:
        # Initialize portfolio
        portfolio = PaperTradingPortfolio()
        initial_cash = portfolio.portfolio['cash']
        print(f"✅ Portfolio initialized with ${initial_cash:,.2f}")
        
        # Test buying a stock
        test_symbol = 'AAPL'
        test_price = 232.00
        test_confidence = 85
        
        result = portfolio.buy_stock(test_symbol, test_price, test_confidence, shares=1)
        if result['success']:
            print(f"✅ Successfully bought 1 share of {test_symbol}")
            print(f"   Message: {result['message']}")
        else:
            print(f"❌ Failed to buy stock: {result['message']}")
        
        # Test portfolio metrics
        metrics = portfolio.get_performance_metrics()
        print(f"✅ Performance metrics calculated successfully")
        print(f"   Total Value: ${metrics['total_value']:,.2f}")
        print(f"   Cash: ${metrics['cash']:,.2f}")
        print(f"   Win Rate: {metrics['win_rate']:.1f}%")
        
        # Test current positions
        positions = portfolio.get_current_positions()
        print(f"✅ Current positions: {len(positions)} positions")
        
        print()
        
    except Exception as e:
        print(f"❌ Portfolio test failed: {e}\n")

def test_currency_conversion():
    """Test currency conversion functionality"""
    print("🔍 Testing Currency Conversion")
    print("=" * 50)
    
    try:
        portfolio = PaperTradingPortfolio()
        converter = portfolio.currency_converter
        
        # Test currency detection
        test_symbols = {
            'RELIANCE.NS': 'INR',
            'GENTING.KL': 'MYR',
            'AAPL': 'USD'
        }
        
        for symbol, expected_currency in test_symbols.items():
            detected = converter.get_symbol_currency(symbol)
            print(f"{'✅' if detected == expected_currency else '❌'} {symbol}: {detected} (expected {expected_currency})")
        
        # Test conversion
        usd_amount = 100
        inr_amount = converter.convert_to_currency(usd_amount, 'USD', 'INR')
        myr_amount = converter.convert_to_currency(usd_amount, 'USD', 'MYR')
        
        print(f"\n💱 Currency Conversion Test:")
        print(f"   $100 USD = ₹{inr_amount:,.2f} INR")
        print(f"   $100 USD = RM{myr_amount:,.2f} MYR")
        print()
        
    except Exception as e:
        print(f"❌ Currency conversion test failed: {e}\n")

def test_watchlist_symbols():
    """Test that watchlist symbols are valid"""
    print("🔍 Testing Watchlist Symbols")
    print("=" * 50)
    
    symbol_count = 0
    valid_count = 0
    
    for market, symbols in DEFAULT_WATCHLIST.items():
        print(f"\n📊 {market.upper()} Market:")
        for symbol in symbols[:3]:  # Test first 3 symbols per market
            symbol_count += 1
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period='1d')
                if not hist.empty:
                    price = hist['Close'].iloc[-1]
                    print(f"   ✅ {symbol}: ${price:.2f}")
                    valid_count += 1
                else:
                    print(f"   ❌ {symbol}: No data available")
            except Exception as e:
                print(f"   ❌ {symbol}: Error - {str(e)[:50]}...")
    
    print(f"\n📈 Watchlist Summary: {valid_count}/{symbol_count} symbols valid ({valid_count/symbol_count*100:.1f}%)")
    print()

def main():
    """Run all tests"""
    print("🚀 Dashboard Functionality Test Suite")
    print("=" * 60)
    print()
    
    test_price_accuracy()
    test_portfolio_functionality()
    test_currency_conversion()
    test_watchlist_symbols()
    
    print("✅ Test suite completed!")

if __name__ == "__main__":
    main()
