#!/usr/bin/env python3
"""
Convert portfolio to separate currency tracking system
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.portfolio_manager import PaperTradingPortfolio
from config.watchlist import TRADING_CONFIG

def convert_to_separate_currencies():
    """Convert portfolio to separate currency tracking"""
    print("🔄 Converting Portfolio to Separate Currency Tracking")
    print("=" * 60)
    
    # Load current portfolio data
    portfolio_file = "data/paper_portfolio.json"
    with open(portfolio_file, 'r') as f:
        portfolio_data = json.load(f)
    
    print("📊 Current Portfolio Data:")
    print(f"   Cash USD: ${portfolio_data['cash']['USD']:,.2f}")
    print(f"   Cash INR: ₹{portfolio_data['cash']['INR']:,.2f}")
    print(f"   Cash MYR: RM{portfolio_data['cash']['MYR']:,.2f}")
    
    # Convert existing positions to single currency format
    if portfolio_data['positions']:
        print(f"\\n🔧 Converting {len(portfolio_data['positions'])} positions:")
        
        for symbol, position in portfolio_data['positions'].items():
            currency = position.get('currency', 'USD')
            print(f"   {symbol} ({currency}):")
            
            # Use original prices for everything
            if 'avg_price_original' in position:
                position['avg_price'] = position['avg_price_original']
                print(f"     avg_price: {position['avg_price_original']:.4f} → {position['avg_price']:.4f}")
            
            if 'last_price_original' in position:
                position['last_price'] = position['last_price_original']
                print(f"     last_price: {position['last_price_original']:.4f} → {position['last_price']:.4f}")
            
            if 'target_price_original' in position:
                position['target_price'] = position['target_price_original']
                
            if 'stop_loss_price_original' in position:
                position['stop_loss_price'] = position['stop_loss_price_original']
                
            # Remove USD conversion fields
            for field in ['avg_price_original', 'last_price_original', 'target_price_original', 'stop_loss_price_original']:
                if field in position:
                    del position[field]
    
    # Clean up trade history
    if portfolio_data.get('trade_history'):
        print(f"\\n🔧 Converting {len(portfolio_data['trade_history'])} trade records:")
        
        for trade in portfolio_data['trade_history']:
            currency = trade.get('currency', 'USD')
            
            # Use original currency values
            if 'price_original' in trade:
                trade['price'] = trade['price_original']
                del trade['price_original']
            
            if 'total_original' in trade:
                trade['total'] = trade['total_original']
                
            if 'target_price_original' in trade:
                trade['target_price'] = trade['target_price_original']
                del trade['target_price_original']
                
            if 'stop_loss_price_original' in trade:
                trade['stop_loss_price'] = trade['stop_loss_price_original']
                del trade['stop_loss_price_original']
            
            # Remove USD conversion fields
            for field in ['total_usd', 'total_original']:
                if field in trade:
                    del trade[field]
    
    # Save the converted portfolio
    with open(portfolio_file, 'w') as f:
        json.dump(portfolio_data, f, indent=2)
    
    print("\\n✅ Portfolio converted to separate currency tracking!")
    
    # Test the new system
    print("\\n🧪 Testing New System:")
    portfolio = PaperTradingPortfolio(initial_capital=TRADING_CONFIG['initial_capital'])
    
    metrics = portfolio.get_performance_metrics()
    positions = portfolio.get_current_positions()
    
    print("\\n📊 Separate Currency Metrics:")
    for currency in ['USD', 'INR', 'MYR']:
        currency_data = metrics['currency_metrics'][currency]
        symbol = '$' if currency == 'USD' else '₹' if currency == 'INR' else 'RM'
        print(f"   {currency} Portfolio:")
        print(f"     Value: {symbol}{currency_data['current_value']:,.2f}")
        print(f"     Return: {symbol}{currency_data['total_return']:,.2f} ({currency_data['total_return_pct']:.2f}%)")
        print(f"     Positions: {currency_data['positions_count']}")
    
    print(f"\\n📈 Current Positions:")
    for pos in positions:
        currency = pos['currency']
        symbol = '$' if currency == 'USD' else '₹' if currency == 'INR' else 'RM'
        print(f"   {pos['symbol']} ({currency}): {pos['unrealized_pnl_pct']:.2f}% P&L")
        print(f"     Value: {symbol}{pos['current_value']:.2f}")

if __name__ == "__main__":
    convert_to_separate_currencies()
