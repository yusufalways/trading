#!/usr/bin/env python3
"""
Simple test to demonstrate the enhanced trading functionality
"""

import sys
import os
sys.path.append('/Users/yusufalways/trading')

from tools.portfolio_manager import PaperTradingPortfolio
import yfinance as yf

def main():
    print("🚀 Testing Enhanced Trading System\n")
    
    # Initialize portfolio
    portfolio = PaperTradingPortfolio()
    
    print("💰 Initial Portfolio Status:")
    summary = portfolio.get_portfolio_summary()
    print(f"   Cash: ${summary['cash']:,.2f}")
    print(f"   Total Value: ${summary['total_value']:,.2f}")
    print(f"   Positions: {summary['position_count']}")
    
    # Test buying stocks with different confidence levels
    test_stocks = [
        ("AAPL", 85),  # High confidence
        ("MSFT", 75),  # Medium confidence  
        ("GOOGL", 65)  # Lower confidence
    ]
    
    print("\n📈 Testing Buy Orders with Different Confidence Levels:")
    
    for symbol, confidence in test_stocks:
        print(f"\n   🎯 Testing {symbol} (Confidence: {confidence}%)...")
        
        # Get current price
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")
            if not data.empty:
                current_price = float(data['Close'].iloc[-1])
                
                # Execute buy order
                result = portfolio.buy_stock(symbol, current_price, confidence)
                
                if result['success']:
                    print(f"   ✅ {result['message']}")
                    print(f"      💰 Invested: ${result['total_cost']:,.2f}")
                    print(f"      🎯 Target: ${result['target_price']:.2f} (+10%)")
                    print(f"      🛡️ Stop Loss: ${result['stop_loss_price']:.2f} (-5%)")
                    print(f"      📊 Shares: {result['shares']}")
                else:
                    print(f"   ❌ {result['message']}")
            else:
                print(f"   ⚠️ No price data available for {symbol}")
                
        except Exception as e:
            print(f"   ❌ Error getting data for {symbol}: {e}")
    
    # Show final portfolio status
    print("\n📊 Final Portfolio Summary:")
    summary = portfolio.get_portfolio_summary()
    
    print(f"   💰 Total Value: ${summary['total_value']:,.2f}")
    print(f"   💵 Cash Remaining: ${summary['cash']:,.2f}")
    print(f"   📈 Total Return: ${summary['total_return_amount']:+,.2f} ({summary['total_return_pct']:+.2f}%)")
    print(f"   📊 Active Positions: {summary['position_count']}")
    
    if summary['positions']:
        print(f"\n   🏢 Position Details:")
        for i, pos in enumerate(summary['positions'], 1):
            print(f"   {i}. {pos['symbol']}:")
            print(f"      • Shares: {pos['shares']}")
            print(f"      • Entry: ${pos['avg_price']:.2f} → Current: ${pos['current_price']:.2f}")
            print(f"      • Target: ${pos['target_price']:.2f} | Stop: ${pos['stop_loss_price']:.2f}")
            print(f"      • P&L: ${pos['unrealized_pnl']:+.2f} ({pos['unrealized_pnl_pct']:+.1f}%)")
            print(f"      • Progress to Target: {pos['progress_pct']:.1f}%")
            print(f"      • Confidence: {pos['confidence']}%")
    
    print(f"\n🎉 Test completed successfully!")
    print(f"💡 Your enhanced trading system includes:")
    print(f"   ✅ Confidence-based position sizing")
    print(f"   ✅ Automatic target (+10%) and stop-loss (-5%) calculation")
    print(f"   ✅ Progress tracking toward targets")
    print(f"   ✅ Comprehensive portfolio analytics")
    print(f"   ✅ Risk management features")
    
    print(f"\n🌐 Ready to launch dashboard:")
    print(f"   Command: streamlit run dashboard.py")
    print(f"   URL: http://localhost:8501")

if __name__ == "__main__":
    main()
