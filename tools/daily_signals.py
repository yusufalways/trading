#!/usr/bin/env python3
"""
Daily Trading Signal Generator
Run this script daily to get buy/sell recommendations
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.market_config import INDIA_CONFIG, MALAYSIA_CONFIG, USA_CONFIG
from tools.technical_analysis import TechnicalAnalyzer, SwingTradingSignals

class DailySignalGenerator:
    def __init__(self):
        self.analyzer = TechnicalAnalyzer()
        self.today = datetime.now().strftime('%Y-%m-%d')
        
    def get_stock_data(self, symbol, period="6mo"):
        """Get recent stock data for analysis"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            if data.empty:
                return None
            return data
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None
    
    def analyze_stock(self, symbol, data):
        """Analyze a single stock and generate signals"""
        if data is None or len(data) < 50:
            return None
            
        # Calculate technical indicators
        data['SMA_20'] = self.analyzer.sma(data['Close'], 20)
        data['SMA_50'] = self.analyzer.sma(data['Close'], 50)
        data['RSI'] = self.analyzer.rsi(data['Close'])
        
        # MACD
        macd_data = self.analyzer.macd(data['Close'])
        data['MACD'] = macd_data['macd']
        data['MACD_Signal'] = macd_data['signal']
        
        # Bollinger Bands
        bb_data = self.analyzer.bollinger_bands(data['Close'])
        data['BB_Upper'] = bb_data['upper']
        data['BB_Lower'] = bb_data['lower']
        
        # Get latest values
        latest = data.iloc[-1]
        prev = data.iloc[-2]
        
        # Calculate signals
        signals = self.calculate_signals(latest, prev)
        
        return {
            'symbol': symbol,
            'price': latest['Close'],
            'signals': signals,
            'confidence': self.calculate_confidence(signals),
            'recommendation': self.get_recommendation(signals)
        }
    
    def calculate_signals(self, latest, prev):
        """Calculate individual trading signals"""
        signals = {}
        
        # SMA Crossover
        signals['sma_bullish'] = latest['SMA_20'] > latest['SMA_50']
        signals['sma_cross_up'] = (latest['SMA_20'] > latest['SMA_50'] and 
                                   prev['SMA_20'] <= prev['SMA_50'])
        signals['sma_cross_down'] = (latest['SMA_20'] < latest['SMA_50'] and 
                                     prev['SMA_20'] >= prev['SMA_50'])
        
        # RSI
        signals['rsi_oversold'] = latest['RSI'] < 30
        signals['rsi_overbought'] = latest['RSI'] > 70
        signals['rsi_bullish'] = 30 < latest['RSI'] < 70
        
        # MACD
        signals['macd_bullish'] = latest['MACD'] > latest['MACD_Signal']
        signals['macd_cross_up'] = (latest['MACD'] > latest['MACD_Signal'] and 
                                    prev['MACD'] <= prev['MACD_Signal'])
        signals['macd_cross_down'] = (latest['MACD'] < latest['MACD_Signal'] and 
                                      prev['MACD'] >= prev['MACD_Signal'])
        
        # Bollinger Bands
        signals['bb_oversold'] = latest['Close'] < latest['BB_Lower']
        signals['bb_overbought'] = latest['Close'] > latest['BB_Upper']
        
        # Price trend
        signals['price_up'] = latest['Close'] > prev['Close']
        signals['above_sma20'] = latest['Close'] > latest['SMA_20']
        
        return signals
    
    def calculate_confidence(self, signals):
        """Calculate confidence score 0-100%"""
        score = 0
        
        # Trend signals (25 points)
        if signals['sma_bullish']: score += 15
        if signals['sma_cross_up']: score += 25
        if signals['sma_cross_down']: score -= 25
        
        # Momentum signals (25 points)
        if signals['macd_bullish']: score += 15
        if signals['macd_cross_up']: score += 25
        if signals['macd_cross_down']: score -= 25
        
        # Oscillator signals (25 points)
        if signals['rsi_oversold']: score += 20
        if signals['rsi_overbought']: score -= 20
        if signals['rsi_bullish']: score += 10
        
        # Mean reversion signals (25 points)
        if signals['bb_oversold']: score += 20
        if signals['bb_overbought']: score -= 20
        
        # Normalize to 0-100
        score = max(0, min(100, score + 50))
        return int(score)
    
    def get_recommendation(self, signals):
        """Get buy/sell/hold recommendation"""
        confidence = self.calculate_confidence(signals)
        
        if confidence >= 75:
            if (signals['sma_cross_up'] or signals['macd_cross_up'] or 
                (signals['sma_bullish'] and signals['rsi_oversold'])):
                return 'STRONG BUY'
            elif (signals['sma_cross_down'] or signals['macd_cross_down'] or 
                  (not signals['sma_bullish'] and signals['rsi_overbought'])):
                return 'STRONG SELL'
        elif confidence >= 60:
            if signals['sma_bullish'] and signals['macd_bullish']:
                return 'BUY'
            elif not signals['sma_bullish'] and not signals['macd_bullish']:
                return 'SELL'
        
        return 'HOLD'
    
    def analyze_market(self, country_config, country_name):
        """Analyze all stocks in a market"""
        print(f"\n🌍 {country_name.upper()} MARKET ANALYSIS")
        print("=" * 50)
        
        results = []
        stocks = country_config['popular_stocks'][:5]  # Analyze top 5 for demo
        
        for symbol in stocks:
            print(f"Analyzing {symbol}...", end=" ")
            data = self.get_stock_data(symbol)
            analysis = self.analyze_stock(symbol, data)
            
            if analysis:
                results.append(analysis)
                print(f"✓ {analysis['recommendation']} ({analysis['confidence']}%)")
            else:
                print("✗ Failed")
        
        # Sort by confidence
        results.sort(key=lambda x: x['confidence'], reverse=True)
        
        print(f"\n📊 TOP RECOMMENDATIONS:")
        for result in results[:3]:  # Show top 3
            rec = result['recommendation']
            conf = result['confidence']
            price = result['price']
            
            if rec in ['STRONG BUY', 'BUY']:
                emoji = "🟢"
            elif rec in ['STRONG SELL', 'SELL']:
                emoji = "🔴"
            else:
                emoji = "🟡"
                
            print(f"{emoji} {result['symbol']:<12} {rec:<12} {conf:>3}% @ ${price:.2f}")
        
        return results
    
    def generate_daily_report(self):
        """Generate comprehensive daily trading report"""
        print("=" * 60)
        print(f"📈 DAILY TRADING SIGNALS - {self.today}")
        print("=" * 60)
        
        all_results = []
        
        # Analyze each market
        markets = [
            (INDIA_CONFIG, "India"),
            (MALAYSIA_CONFIG, "Malaysia"), 
            (USA_CONFIG, "USA")
        ]
        
        for config, name in markets:
            results = self.analyze_market(config, name)
            all_results.extend(results)
        
        # Overall summary
        buy_signals = [r for r in all_results if 'BUY' in r['recommendation']]
        sell_signals = [r for r in all_results if 'SELL' in r['recommendation']]
        
        print(f"\n📋 DAILY SUMMARY")
        print("=" * 30)
        print(f"💚 Buy Opportunities: {len(buy_signals)}")
        print(f"❤️ Sell Signals: {len(sell_signals)}")
        print(f"📊 Total Analyzed: {len(all_results)}")
        
        if buy_signals:
            print(f"\n🎯 TOP BUY OPPORTUNITY:")
            top_buy = max(buy_signals, key=lambda x: x['confidence'])
            print(f"   {top_buy['symbol']} - {top_buy['recommendation']} ({top_buy['confidence']}%)")
        
        return all_results

def main():
    """Run daily signal generation"""
    generator = DailySignalGenerator()
    results = generator.generate_daily_report()
    
    print(f"\n✅ Analysis complete! Found {len(results)} signals.")
    print("💡 This is a demo with sample stocks. Customize your watchlist in config/market_config.py")

if __name__ == "__main__":
    main()
