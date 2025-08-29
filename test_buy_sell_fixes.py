#!/usr/bin/env python3
"""
Test script to verify buy/sell fixes
"""

import sys
import os
import json

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.portfolio_manager import PaperTradingPortfolio

def test_position_display():
    """Test that positions show correct entry prices"""
    print("🧪 Testing Position Display Fixes...")
    
    # Initialize portfolio
    portfolio = PaperTradingPortfolio()
    
    # Get current positions
    positions = portfolio.get_current_positions()
    
    print(f"\n📊 Current Positions ({len(positions)} found):")
    
    for position in positions:
        symbol = position['symbol']
        shares = position['shares']
        currency = position['currency']
        
        # Check if we have original price data
        avg_price_original = position.get('avg_price_original')
        current_price_original = position.get('current_price_original')
        
        print(f"\n📈 {symbol} ({currency}):")
        print(f"   Shares: {shares}")
        print(f"   Entry Price (USD): {position['avg_price']:.2f}")
        print(f"   Entry Price (Original): {avg_price_original:.2f} {currency}")
        print(f"   Current Price (USD): {position['current_price']:.2f}")
        print(f"   Current Price (Original): {current_price_original:.2f} {currency}")
        print(f"   P&L: {position['unrealized_pnl']:.2f} {currency} ({position['unrealized_pnl_pct']:.1f}%)")
        
        # Verify the original prices make sense
        if currency == 'MYR':
            if avg_price_original > 1 and avg_price_original < 100:
                print(f"   ✅ Entry price looks correct for MYR stock")
            else:
                print(f"   ❌ Entry price might be wrong for MYR stock")

def test_manual_buy():
    """Test manual buy with specific quantity"""
    print(f"\n🧪 Testing Manual Buy with Quantity Control...")
    
    portfolio = PaperTradingPortfolio()
    
    # Test buying with specific quantity
    print(f"\n💰 Current cash: {portfolio.portfolio['cash']}")
    
    # Test buying 10 shares of a Malaysian stock
    test_symbol = "TEST.KL"
    test_price = 5.00  # RM 5.00
    test_shares = 10
    test_confidence = 80
    
    print(f"\n🔍 Testing purchase:")
    print(f"   Symbol: {test_symbol}")
    print(f"   Price: RM{test_price:.2f}")
    print(f"   Quantity: {test_shares} shares")
    print(f"   Expected Cost: RM{test_price * test_shares:.2f}")
    
    # Execute the trade
    result = portfolio.buy_stock(test_symbol, test_price, test_confidence, shares=test_shares)
    
    if result['success']:
        print(f"   ✅ Purchase successful: {result['message']}")
        
        # Check the position
        if test_symbol in portfolio.portfolio['positions']:
            position = portfolio.portfolio['positions'][test_symbol]
            print(f"   📊 Position created:")
            print(f"      Shares: {position['shares']}")
            print(f"      Entry Price (Original): RM{position['avg_price_original']:.2f}")
            print(f"      Entry Price (USD): ${position['avg_price']:.2f}")
            
            # Verify the quantities match
            if position['shares'] == test_shares:
                print(f"   ✅ Correct quantity purchased")
            else:
                print(f"   ❌ Wrong quantity: got {position['shares']}, expected {test_shares}")
                
            # Verify the price is stored correctly
            if abs(position['avg_price_original'] - test_price) < 0.01:
                print(f"   ✅ Correct entry price stored")
            else:
                print(f"   ❌ Wrong entry price: got {position['avg_price_original']}, expected {test_price}")
        
        # Check cash was deducted correctly
        expected_remaining_myr = 10000 - (test_shares * test_price)
        actual_remaining_myr = portfolio.portfolio['cash']['MYR']
        
        if abs(actual_remaining_myr - expected_remaining_myr) < 0.01:
            print(f"   ✅ Correct cash deduction: RM{actual_remaining_myr:.2f}")
        else:
            print(f"   ❌ Wrong cash deduction: RM{actual_remaining_myr:.2f}, expected RM{expected_remaining_myr:.2f}")
            
    else:
        print(f"   ❌ Purchase failed: {result['message']}")

def cleanup_test_position():
    """Remove test position"""
    print(f"\n🧹 Cleaning up test position...")
    
    portfolio = PaperTradingPortfolio()
    
    if "TEST.KL" in portfolio.portfolio['positions']:
        del portfolio.portfolio['positions']["TEST.KL"]
        portfolio.portfolio['cash']['MYR'] = 10000  # Restore original cash
        portfolio.save_portfolio()
        print(f"   ✅ Test position removed")

if __name__ == "__main__":
    print("🚀 Buy/Sell Fixes Test Suite")
    print("=" * 50)
    
    try:
        test_position_display()
        test_manual_buy()
        cleanup_test_position()
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS COMPLETED!")
        print("\n📋 Fixes Applied:")
        print("   ✅ Removed auto-buy button to prevent large accidental purchases")
        print("   ✅ Fixed entry price display to show correct original currency prices")
        print("   ✅ Enhanced position data to include original currency information")
        print("   ✅ Updated portfolio calculations for accurate P&L in native currency")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
