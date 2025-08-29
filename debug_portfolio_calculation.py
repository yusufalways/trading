#!/usr/bin/env python3
"""
Debug script to reproduce the 4.19% return calculation error
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.portfolio_manager import PaperTradingPortfolio
from config.watchlist import TRADING_CONFIG

def debug_portfolio_calculation():
    """Debug the portfolio value calculation issue"""
    print("🔍 Debugging Portfolio Value Calculation Error")
    print("=" * 60)
    
    # Start with fresh portfolio
    portfolio = PaperTradingPortfolio(initial_capital=TRADING_CONFIG['initial_capital'])
    
    # Reset to clean state first
    portfolio.reset_portfolio()
    
    print("1️⃣ Initial State:")
    initial_value = portfolio.get_portfolio_value()
    initial_metrics = portfolio.get_performance_metrics()
    print(f"   Portfolio Value: ${initial_value:,.2f}")
    print(f"   Return: {initial_metrics['total_return_pct']:.2f}%")
    
    # Get exchange rates
    rates = portfolio.currency_converter.exchange_rates
    print(f"   Exchange Rates - INR: {rates['INR']:.2f}, MYR: {rates['MYR']:.2f}")
    
    # Simulate buying 3816.KL at RM7.42
    print("\n2️⃣ Simulating Buy: 3816.KL, 100 shares @ RM7.42")
    
    symbol = "3816.KL"
    price_myr = 7.42
    shares = 100
    
    # Before trade calculations
    print("   Before Trade:")
    cash_before = portfolio.portfolio['cash'].copy()
    print(f"     Cash MYR: RM{cash_before['MYR']:,.2f}")
    print(f"     Portfolio Value: ${portfolio.get_portfolio_value():,.2f}")
    
    # Manual calculation of what should happen
    price_usd = portfolio.currency_converter.convert_to_usd(price_myr, 'MYR')
    cost_myr = shares * price_myr
    cost_usd = shares * price_usd
    
    print(f"   Price Conversion: RM{price_myr} = ${price_usd:.4f}")
    print(f"   Cost: RM{cost_myr} = ${cost_usd:.2f}")
    
    # Expected after-trade state
    expected_cash_myr = cash_before['MYR'] - cost_myr
    expected_portfolio_value = (
        cash_before['USD'] + 
        portfolio.currency_converter.convert_to_usd(cash_before['INR'], 'INR') +
        portfolio.currency_converter.convert_to_usd(expected_cash_myr, 'MYR') +
        cost_usd  # Position value
    )
    
    print(f"   Expected Cash MYR after: RM{expected_cash_myr:,.2f}")
    print(f"   Expected Portfolio Value after: ${expected_portfolio_value:,.2f}")
    
    # Execute the trade
    print("\n3️⃣ Executing Trade...")
    result = portfolio.buy_stock(symbol, price_myr, 85, shares=shares)
    print(f"   Result: {result['message']}")
    
    # Check actual after-trade state
    print("\n4️⃣ Actual After-Trade State:")
    cash_after = portfolio.portfolio['cash']
    actual_portfolio_value = portfolio.get_portfolio_value()
    metrics_after = portfolio.get_performance_metrics()
    
    print(f"   Cash MYR: RM{cash_after['MYR']:,.2f} (Expected: RM{expected_cash_myr:,.2f})")
    print(f"   Portfolio Value: ${actual_portfolio_value:,.2f} (Expected: ${expected_portfolio_value:,.2f})")
    print(f"   Return: {metrics_after['total_return_pct']:.2f}%")
    
    # Check trade history
    trade_history = portfolio.portfolio['trade_history']
    if trade_history:
        last_trade = trade_history[-1]
        print(f"   Trade Record Portfolio Value: ${last_trade['portfolio_value_after']:,.2f}")
    
    # Manual verification of portfolio value calculation
    print("\n5️⃣ Manual Portfolio Value Verification:")
    manual_cash_usd = 0
    for currency, amount in cash_after.items():
        usd_equiv = portfolio.currency_converter.convert_to_usd(amount, currency)
        manual_cash_usd += usd_equiv
        print(f"     {currency}: {amount:,.2f} = ${usd_equiv:.2f}")
    
    positions_value_usd = 0
    for symbol, pos in portfolio.portfolio['positions'].items():
        pos_value = pos['shares'] * pos['last_price']
        positions_value_usd += pos_value
        print(f"     Position {symbol}: {pos['shares']} @ ${pos['last_price']:.4f} = ${pos_value:.2f}")
    
    manual_total = manual_cash_usd + positions_value_usd
    print(f"   Manual Total: ${manual_total:,.2f}")
    print(f"   get_portfolio_value(): ${actual_portfolio_value:,.2f}")
    print(f"   Difference: ${abs(manual_total - actual_portfolio_value):,.2f}")
    
    # Check initial capital calculation
    print("\n6️⃣ Initial Capital Verification:")
    initial_cap = portfolio.portfolio['initial_capital']
    manual_initial_usd = sum(
        portfolio.currency_converter.convert_to_usd(amount, currency)
        for currency, amount in initial_cap.items()
    )
    print(f"   Manual Initial Capital: ${manual_initial_usd:,.2f}")
    print(f"   Should be: $13,510.83 (10k + 1,141.16 + 2,369.67)")
    
    return_should_be = ((manual_total - manual_initial_usd) / manual_initial_usd) * 100
    print(f"   Return should be: {return_should_be:.2f}%")

if __name__ == "__main__":
    debug_portfolio_calculation()
