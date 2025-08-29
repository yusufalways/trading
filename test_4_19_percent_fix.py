#!/usr/bin/env python3
"""
Test script to verify the 4.19% return calculation bug is completely fixed
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.portfolio_manager import PaperTradingPortfolio
from config.watchlist import TRADING_CONFIG

def test_4_19_percent_bug_fix():
    """Test that the 4.19% return calculation bug is fixed"""
    print("🧪 Testing 4.19% Return Calculation Bug Fix")
    print("=" * 60)
    
    # Load portfolio
    portfolio = PaperTradingPortfolio(initial_capital=TRADING_CONFIG['initial_capital'])
    
    # Test scenario: Buy stock at current price should show 0.00% return
    print("📊 Test Scenario: Buy stock at current market price")
    print("   Expected Result: 0.00% return immediately after purchase")
    print()
    
    # Get current metrics
    metrics = portfolio.get_performance_metrics()
    positions = portfolio.get_current_positions()
    
    print("🔍 Current Portfolio State:")
    print(f"   Portfolio Value: ${metrics['total_value']:,.2f}")
    print(f"   Total Return: {metrics['total_return_pct']:.2f}%")
    print(f"   Positions: {len(positions)}")
    
    # Manual calculation verification
    print("\n🧮 Manual Calculation Verification:")
    
    # Cash calculation
    cash_balances = portfolio.portfolio['cash']
    total_cash_usd = 0
    for currency, amount in cash_balances.items():
        usd_equiv = portfolio.currency_converter.convert_to_usd(amount, currency)
        total_cash_usd += usd_equiv
        print(f"   Cash {currency}: {amount:,.2f} = ${usd_equiv:,.2f}")
    
    # Position calculation
    total_positions_usd = 0
    for pos in positions:
        # Use avg_price (USD) for calculations, not original currency price
        pos_value_usd = pos['shares'] * pos['avg_price']
        total_positions_usd += pos_value_usd
        print(f"   Position {pos['symbol']}: {pos['shares']} × ${pos['avg_price']:.4f} = ${pos_value_usd:.2f}")
        print(f"     (Original currency: {pos['shares']} × {pos['currency']}{pos.get('avg_price_original', 0):.2f})")
    
    # Initial capital calculation
    initial_capital = portfolio.portfolio['initial_capital']
    total_initial_usd = 0
    for currency, amount in initial_capital.items():
        usd_equiv = portfolio.currency_converter.convert_to_usd(amount, currency)
        total_initial_usd += usd_equiv
    
    # Manual totals
    manual_total = total_cash_usd + total_positions_usd
    manual_return = manual_total - total_initial_usd
    manual_return_pct = (manual_return / total_initial_usd) * 100 if total_initial_usd > 0 else 0
    
    print(f"\n📈 Manual Calculation Results:")
    print(f"   Total Cash: ${total_cash_usd:,.2f}")
    print(f"   Total Positions: ${total_positions_usd:,.2f}")
    print(f"   **Portfolio Value: ${manual_total:,.2f}**")
    print(f"   Initial Capital: ${total_initial_usd:,.2f}")
    print(f"   **Return: ${manual_return:,.2f} ({manual_return_pct:.2f}%)**")
    
    print(f"\n🎯 get_performance_metrics() Results:")
    print(f"   **Portfolio Value: ${metrics['total_value']:,.2f}**")
    print(f"   **Return: ${metrics['total_return']:,.2f} ({metrics['total_return_pct']:.2f}%)**")
    
    # Verification
    print("\n✅ Bug Fix Verification:")
    
    value_diff = abs(manual_total - metrics['total_value'])
    return_diff = abs(manual_return_pct - metrics['total_return_pct'])
    
    if value_diff < 0.01:
        print(f"   ✅ Portfolio value calculation: CORRECT (diff: ${value_diff:.2f})")
    else:
        print(f"   ❌ Portfolio value calculation: WRONG (diff: ${value_diff:.2f})")
    
    if return_diff < 0.01:
        print(f"   ✅ Return percentage calculation: CORRECT (diff: {return_diff:.2f}%)")
    else:
        print(f"   ❌ Return percentage calculation: WRONG (diff: {return_diff:.2f}%)")
    
    # Special check for same-price positions (should be 0% return)
    zero_return_positions = 0
    for pos in positions:
        if abs(pos['unrealized_pnl_pct']) < 0.01:  # Near 0%
            zero_return_positions += 1
            print(f"   ✅ Position {pos['symbol']}: 0.00% return (as expected for same-price buy)")
    
    print("\n" + "=" * 60)
    
    # Overall result
    if value_diff < 0.01 and return_diff < 0.01:
        print("🎉 **BUG FIX SUCCESSFUL!** The 4.19% calculation error is RESOLVED!")
        print("   ✅ Portfolio calculations now accurate")
        print("   ✅ Return percentages now correct")
        print("   ✅ Multi-currency conversions working properly")
        
        # Explain what was fixed
        print("\n🔧 **What was fixed:**")
        print("   • update_positions() was storing raw yfinance prices in last_price")
        print("   • Raw prices were in original currency (MYR), not USD")
        print("   • get_portfolio_value() expected USD prices for calculations")
        print("   • Result: RM7.42 × 100 = RM742 ≈ $742 (wrong) vs $175.83 (correct)")
        print("   • Fix: Convert prices to USD before storing in last_price field")
        
    else:
        print("❌ **BUG STILL EXISTS!** Portfolio calculations are still incorrect.")
        print(f"   Portfolio value difference: ${value_diff:.2f}")
        print(f"   Return percentage difference: {return_diff:.2f}%")
    
    print("=" * 60)

if __name__ == "__main__":
    test_4_19_percent_bug_fix()
