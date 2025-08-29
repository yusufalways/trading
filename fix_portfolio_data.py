#!/usr/bin/env python3
"""
Fix corrupted portfolio data where last_price is in original currency instead of USD
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.portfolio_manager import PaperTradingPortfolio
from config.watchlist import TRADING_CONFIG

def fix_portfolio_data():
    """Fix the portfolio data corruption"""
    print("🔧 Fixing Portfolio Data Corruption...")
    print("=" * 50)
    
    # Load the raw portfolio data
    portfolio_file = "data/paper_portfolio.json"
    with open(portfolio_file, 'r') as f:
        portfolio_data = json.load(f)
    
    print("📊 Current Portfolio Data Issues:")
    
    # Check positions for currency mismatches
    fixed_positions = {}
    for symbol, position in portfolio_data['positions'].items():
        print(f"\n🔍 Checking {symbol}:")
        print(f"   Currency: {position.get('currency', 'USD')}")
        print(f"   avg_price: {position['avg_price']:.4f}")
        print(f"   last_price: {position['last_price']:.4f}")
        print(f"   avg_price_original: {position.get('avg_price_original', 'N/A')}")
        print(f"   last_price_original: {position.get('last_price_original', 'N/A')}")
        
        # Check if last_price looks like it's in original currency
        currency = position.get('currency', 'USD')
        last_price = position['last_price']
        avg_price = position['avg_price']
        
        if currency == 'MYR' and last_price > 4.0:  # Likely MYR price, not USD
            print(f"   ❌ ISSUE: last_price ({last_price:.4f}) appears to be in MYR, not USD")
            
            # Fix it by converting to USD
            portfolio = PaperTradingPortfolio(initial_capital=TRADING_CONFIG['initial_capital'])
            last_price_usd = portfolio.currency_converter.convert_to_usd(last_price, currency)
            
            print(f"   🔧 FIXING: Converting RM{last_price:.4f} → ${last_price_usd:.4f}")
            
            # Create corrected position
            fixed_position = position.copy()
            fixed_position['last_price'] = last_price_usd
            fixed_position['last_price_original'] = last_price  # Store original for display
            
            fixed_positions[symbol] = fixed_position
            
        elif currency == 'USD' and last_price < 10 and 'avg_price_original' in position:
            # USD stock should have higher prices typically
            print(f"   ✅ OK: USD position looks correct")
            fixed_positions[symbol] = position
            
        else:
            print(f"   ✅ OK: Position data looks correct")
            fixed_positions[symbol] = position
    
    # Update the portfolio data
    if fixed_positions:
        print(f"\n🔧 Applying fixes to {len(fixed_positions)} positions...")
        portfolio_data['positions'] = fixed_positions
        
        # Write back to file
        with open(portfolio_file, 'w') as f:
            json.dump(portfolio_data, f, indent=2)
        
        print("✅ Portfolio data fixed!")
        
        # Verify the fix
        print("\n🔍 Verification:")
        portfolio = PaperTradingPortfolio(initial_capital=TRADING_CONFIG['initial_capital'])
        metrics = portfolio.get_performance_metrics()
        
        print(f"   Portfolio Value: ${metrics['total_value']:,.2f}")
        print(f"   Return: {metrics['total_return_pct']:.2f}%")
        
        if abs(metrics['total_return_pct']) < 0.01:  # Should be near 0% for same-price buy
            print("   ✅ Return calculation now correct!")
        else:
            print(f"   ❌ Return still incorrect: {metrics['total_return_pct']:.2f}%")
            
    else:
        print("\n✅ No fixes needed - portfolio data is correct")

if __name__ == "__main__":
    fix_portfolio_data()
