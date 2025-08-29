#!/usr/bin/env python3
"""
Working Trading Signals Demo
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

def simple_analysis(symbol):
    """Simple working stock analysis"""
    try:
        print(f"  📊 {symbol:<15}", end=" ")
        
        # Get data
        ticker = yf.Ticker(symbol)
        data = ticker.history(period='3mo')
        
        if len(data) < 20:
            print("❌ Insufficient data")
            return None
        
        # Calculate indicators
        data['SMA_20'] = data['Close'].rolling(20).mean()
        data['SMA_50'] = data['Close'].rolling(50).mean()
        data['RSI'] = calculate_rsi(data['Close'], 14)
        
        # Get latest values
        current_price = data['Close'].iloc[-1]
        sma_20 = data['SMA_20'].iloc[-1]
        sma_50 = data['SMA_50'].iloc[-1]
        rsi = data['RSI'].iloc[-1]
        
        # Simple signal logic
        signal = "HOLD"
        confidence = 50
        
        if pd.notna(sma_20) and pd.notna(sma_50):
            if sma_20 > sma_50 and current_price > sma_20:
                if rsi < 70:  # Not overbought
                    signal = "BUY"
                    confidence = 75
            elif sma_20 < sma_50 and current_price < sma_20:
                if rsi > 30:  # Not oversold
                    signal = "SELL"
                    confidence = 70
        
        # Display result
        emoji = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "🟡"
        print(f"{emoji} {signal:<6} ({confidence:>2}%) @ ${current_price:>8.2f}")
        
        return {
            'symbol': symbol,
            'price': current_price,
            'signal': signal,
            'confidence': confidence,
            'rsi': rsi
        }
        
    except Exception as e:
        print(f"❌ Error: {str(e)[:30]}...")
        return None

def calculate_rsi(prices, window=14):
    """Calculate RSI indicator"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def main():
    print("=" * 70)
    print(f"📈 SWING TRADING SIGNALS DEMO - {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 70)
    
    # Sample stocks for demo
    markets = {
        '🇺🇸 USA': ['AAPL', 'MSFT', 'NVDA'],
        '🇮🇳 INDIA': ['RELIANCE.NS', 'TCS.NS']
    }
    
    all_results = []
    
    for market_name, symbols in markets.items():
        print(f"\n{market_name} Market Analysis:")
        print("-" * 50)
        
        for symbol in symbols:
            result = simple_analysis(symbol)
            if result:
                all_results.append(result)
    
    # Generate summary
    if all_results:
        buy_signals = [r for r in all_results if r['signal'] == 'BUY']
        sell_signals = [r for r in all_results if r['signal'] == 'SELL']
        
        print(f"\n📊 TRADING SUMMARY:")
        print("-" * 30)
        print(f"💚 Buy Opportunities: {len(buy_signals)}")
        print(f"❤️  Sell Signals: {len(sell_signals)}")
        print(f"📈 Total Analyzed: {len(all_results)}")
        
        if buy_signals:
            top_buy = max(buy_signals, key=lambda x: x['confidence'])
            print(f"\n🎯 TOP BUY OPPORTUNITY:")
            print(f"   {top_buy['symbol']} @ ${top_buy['price']:.2f} ({top_buy['confidence']}% confidence)")
            print(f"   RSI: {top_buy['rsi']:.1f}")
        
        if sell_signals:
            top_sell = max(sell_signals, key=lambda x: x['confidence'])
            print(f"\n⚠️  TOP SELL SIGNAL:")
            print(f"   {top_sell['symbol']} @ ${top_sell['price']:.2f} ({top_sell['confidence']}% confidence)")
            print(f"   RSI: {top_sell['rsi']:.1f}")
    
    print(f"\n✅ Analysis Complete!")
    print("\n💡 Next Steps:")
    print("   • This demo shows basic signal generation")
    print("   • Full system will track paper trading portfolio")
    print("   • Daily automated reports with more indicators")
    print("   • Risk management and position sizing")
    print("   • Customizable watchlists for each market")
    
    return all_results

if __name__ == "__main__":
    main()
