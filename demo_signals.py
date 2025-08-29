#!/usr/bin/env python3
"""
Simple Trading Signals Demo
"""

import yfinance as yf
import pandas as pd
from datetime import datetime

def analyze_stock(symbol):
    """Simple stock analysis with moving averages"""
    try:
        print(f"  Fetching {symbol}...", end=" ")
        data = yf.download(symbol, period='3mo', progress=False)
        if len(data) < 20:
            return None
            
        # Calculate simple moving averages
        data['SMA_20'] = data['Close'].rolling(20).mean()
        data['SMA_50'] = data['Close'].rolling(50).mean()
        
        latest = data.iloc[-1]
        
        # Generate simple signal
        sma_20_gt_50 = latest['SMA_20'] > latest['SMA_50']
        price_gt_sma20 = latest['Close'] > latest['SMA_20']
        
        if sma_20_gt_50 and price_gt_sma20:
            signal = 'BUY'
            confidence = 75
        elif not sma_20_gt_50 and latest['Close'] < latest['SMA_20']:
            signal = 'SELL' 
            confidence = 70
        else:
            signal = 'HOLD'
            confidence = 50
            
        print("✓")
        return {
            'symbol': symbol,
            'price': latest['Close'],
            'signal': signal,
            'confidence': confidence
        }
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def main():
    print("=" * 60)
    print(f"📈 TRADING SIGNALS DEMO - {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 60)
    
    # Test stocks from different markets
    markets = {
        '🇺🇸 USA Market': ['AAPL', 'MSFT', 'GOOGL'],
        '🇮🇳 India Market': ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS']
    }
    
    all_signals = []
    
    for market_name, symbols in markets.items():
        print(f"\n{market_name}:")
        print("-" * 40)
        
        for symbol in symbols:
            result = analyze_stock(symbol)
            if result:
                all_signals.append(result)
                
                # Format output
                emoji = "🟢" if result['signal'] == 'BUY' else "🔴" if result['signal'] == 'SELL' else "🟡"
                print(f"  {emoji} {result['symbol']:<15} {result['signal']:<6} ({result['confidence']:>2}%) @ ${result['price']:>8.2f}")
    
    # Summary
    buy_signals = [s for s in all_signals if s['signal'] == 'BUY']
    sell_signals = [s for s in all_signals if s['signal'] == 'SELL']
    
    print(f"\n📊 SUMMARY:")
    print(f"  💚 Buy opportunities: {len(buy_signals)}")
    print(f"  ❤️  Sell signals: {len(sell_signals)}")
    print(f"  📈 Total analyzed: {len(all_signals)}")
    
    if buy_signals:
        top_buy = max(buy_signals, key=lambda x: x['confidence'])
        print(f"\n🎯 TOP BUY: {top_buy['symbol']} ({top_buy['confidence']}% confidence)")
    
    print(f"\n✅ Demo complete!")
    print("💡 This is a simplified example. The full system will include:")
    print("   • More sophisticated technical indicators")
    print("   • Risk management calculations")
    print("   • Paper trading portfolio tracking")
    print("   • Daily automated reports")

if __name__ == "__main__":
    main()
