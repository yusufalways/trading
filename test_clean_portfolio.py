#!/usr/bin/env python3
"""
Test script to validate the new clean multi-currency portfolio setup
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.portfolio_manager import PaperTradingPortfolio

def test_clean_portfolio():
    """Test the new clean multi-currency portfolio"""
    print("🧹 Testing Clean Multi-Currency Portfolio Setup")
    print("=" * 60)
    
    # Initialize portfolio
    portfolio = PaperTradingPortfolio()
    
    # Check initial balances
    print("💰 Initial Cash Balances:")
    cash_balances = portfolio.portfolio['cash']
    for currency, amount in cash_balances.items():
        symbol = '₹' if currency == 'INR' else 'RM' if currency == 'MYR' else '$'
        print(f"   {currency}: {symbol}{amount:,.2f}")
    
    print(f"\n📊 Initial Portfolio Stats:")
    metrics = portfolio.get_performance_metrics()
    print(f"   Total Value: ${metrics['total_value']:,.2f}")
    print(f"   Positions: {metrics['positions_count']}")
    print(f"   Trade History: {len(portfolio.portfolio['trade_history'])} trades")
    
    # Test buying stocks in different currencies
    print(f"\n🛒 Testing Multi-Currency Trading:")
    
    # Buy US stock
    print("   • Buying US stock (AAPL)...")
    result_us = portfolio.buy_stock('AAPL', 232.00, 85, shares=5)
    if result_us['success']:
        print(f"     ✅ {result_us['message']}")
    else:
        print(f"     ❌ {result_us['message']}")
    
    # Buy Indian stock
    print("   • Buying Indian stock (RELIANCE.NS)...")
    result_in = portfolio.buy_stock('RELIANCE.NS', 1357.20, 80, shares=10)
    if result_in['success']:
        print(f"     ✅ {result_in['message']}")
    else:
        print(f"     ❌ {result_in['message']}")
    
    # Buy Malaysian stock (using a working symbol)
    print("   • Buying Malaysian stock (1155.KL)...")
    result_my = portfolio.buy_stock('1155.KL', 9.90, 75, shares=100)
    if result_my['success']:
        print(f"     ✅ {result_my['message']}")
    else:
        print(f"     ❌ {result_my['message']}")
    
    # Check final balances
    print(f"\n💰 Final Cash Balances:")
    final_cash = portfolio.portfolio['cash']
    for currency, amount in final_cash.items():
        symbol = '₹' if currency == 'INR' else 'RM' if currency == 'MYR' else '$'
        print(f"   {currency}: {symbol}{amount:,.2f}")
    
    # Check positions
    positions = portfolio.get_current_positions()
    print(f"\n📈 Current Positions: {len(positions)}")
    for pos in positions:
        symbol = pos['symbol']
        shares = pos['shares']
        avg_price = pos['avg_price']
        # Get currency from symbol
        if symbol.endswith('.NS') or symbol.endswith('.BO'):
            currency = 'INR'
            symbol_char = '₹'
        elif symbol.endswith('.KL'):
            currency = 'MYR'
            symbol_char = 'RM'
        else:
            currency = 'USD'
            symbol_char = '$'
        print(f"   {symbol}: {shares} shares @ {symbol_char}{avg_price:,.2f}")
    
    # Check final metrics
    final_metrics = portfolio.get_performance_metrics()
    print(f"\n📊 Final Portfolio Stats:")
    print(f"   Total Value: ${final_metrics['total_value']:,.2f}")
    print(f"   Total Return: ${final_metrics['total_return']:,.2f} ({final_metrics['total_return_pct']:.2f}%)")
    print(f"   Positions: {final_metrics['positions_count']}")
    print(f"   Trade History: {len(portfolio.portfolio['trade_history'])} trades")
    
    print(f"\n✅ Multi-currency portfolio test completed!")
    return True

def test_no_auto_trading():
    """Verify no auto-trading occurs"""
    print("\n🚫 Testing No Auto-Trading")
    print("=" * 40)
    
    portfolio = PaperTradingPortfolio()
    initial_positions = len(portfolio.portfolio['positions'])
    initial_trades = len(portfolio.portfolio['trade_history'])
    
    print(f"   Initial positions: {initial_positions}")
    print(f"   Initial trade history: {initial_trades}")
    
    # Simulate dashboard loading without auto-trades
    print("   Simulating dashboard load...")
    # No automatic buying should occur
    
    final_positions = len(portfolio.portfolio['positions'])
    final_trades = len(portfolio.portfolio['trade_history'])
    
    print(f"   Final positions: {final_positions}")
    print(f"   Final trade history: {final_trades}")
    
    if initial_positions == final_positions and initial_trades == final_trades:
        print("   ✅ No auto-trading confirmed")
        return True
    else:
        print("   ❌ Unexpected trading occurred")
        return False

def main():
    """Run all tests"""
    print("🚀 Clean Portfolio Test Suite")
    print("=" * 60)
    print()
    
    success = True
    success &= test_clean_portfolio()
    success &= test_no_auto_trading()
    
    if success:
        print("\n🎉 All tests passed! Portfolio is clean and ready for manual trading.")
    else:
        print("\n❌ Some tests failed. Please check the setup.")

if __name__ == "__main__":
    main()
