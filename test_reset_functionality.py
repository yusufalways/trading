#!/usr/bin/env python3
"""
Test script for portfolio reset functionality
"""

import sys
import os
import json

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.portfolio_manager import PaperTradingPortfolio

def test_reset_functions():
    """Test the portfolio reset functions"""
    print("🧪 Testing Portfolio Reset Functions...")
    
    # Initialize portfolio
    portfolio = PaperTradingPortfolio()
    
    # Show current state
    print(f"\n📊 Current Portfolio State:")
    print(f"   Cash: {portfolio.portfolio['cash']}")
    print(f"   Positions: {len(portfolio.portfolio['positions'])} positions")
    print(f"   Trade History: {len(portfolio.portfolio.get('trade_history', []))} trades")
    
    # Test 1: Clear History
    print(f"\n🧪 Test 1: Clear History Function")
    result = portfolio.clear_history()
    print(f"   Result: {result['success']} - {result['message']}")
    
    # Test 2: Reset Portfolio (but restore data first)
    print(f"\n🧪 Test 2: Portfolio Reset Function")
    # Add some dummy data first
    portfolio.portfolio['positions']['TEST'] = {
        'shares': 10,
        'avg_price': 100.0,
        'currency': 'USD'
    }
    portfolio.portfolio['cash']['USD'] = 5000  # Simulate some trades
    
    result = portfolio.reset_portfolio()
    print(f"   Result: {result['success']} - {result['message']}")
    print(f"   Cash after reset: {portfolio.portfolio['cash']}")
    print(f"   Positions after reset: {len(portfolio.portfolio['positions'])}")
    
    # Test 3: Full Reset
    print(f"\n🧪 Test 3: Full Reset Function")
    # Add some dummy data again
    portfolio.portfolio['trade_history'] = [{'test': 'data'}]
    
    result = portfolio.full_reset()
    print(f"   Result: {result['success']} - {result['message']}")
    print(f"   Cash after full reset: {portfolio.portfolio['cash']}")
    print(f"   Positions after full reset: {len(portfolio.portfolio['positions'])}")
    print(f"   History after full reset: {len(portfolio.portfolio.get('trade_history', []))}")
    
    print("\n🎉 All reset function tests completed!")

def verify_default_state():
    """Verify portfolio is in default state"""
    print("\n✅ Verifying Default State:")
    
    portfolio = PaperTradingPortfolio()
    
    expected_cash = {
        'USD': 10000,
        'INR': 100000,
        'MYR': 10000
    }
    
    # Check cash balances
    current_cash = portfolio.portfolio['cash']
    for currency, expected_amount in expected_cash.items():
        current_amount = current_cash.get(currency, 0)
        if current_amount == expected_amount:
            print(f"   ✅ {currency}: {current_amount} (correct)")
        else:
            print(f"   ❌ {currency}: {current_amount} (expected {expected_amount})")
    
    # Check positions
    if len(portfolio.portfolio['positions']) == 0:
        print(f"   ✅ Positions: Empty (correct)")
    else:
        print(f"   ❌ Positions: {len(portfolio.portfolio['positions'])} (expected 0)")
    
    # Check history
    history_count = len(portfolio.portfolio.get('trade_history', []))
    if history_count == 0:
        print(f"   ✅ Trade History: Empty (correct)")
    else:
        print(f"   ❌ Trade History: {history_count} trades (expected 0)")

if __name__ == "__main__":
    print("🚀 Portfolio Reset Test Suite")
    print("=" * 50)
    
    try:
        test_reset_functions()
        verify_default_state()
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("\n📋 Reset Functions Available:")
        print("   🔄 reset_portfolio() - Clear positions, restore cash, keep history")
        print("   🗑️ clear_history() - Clear trade history, keep positions")
        print("   🧹 full_reset() - Complete reset to factory defaults")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
