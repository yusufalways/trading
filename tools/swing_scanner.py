#!/usr/bin/env python3
"""
Advanced Swing Trading Scanner for Support/Resistance Levels
Identifies stocks near key technical levels for swing trade entries

Data Sources:
1. Yahoo Finance (yfinance) - Free, reliable price data
2. Screener.in (India) - Support/resistance levels via web scraping
3. TradingView (via unofficial API) - Technical analysis data
4. Finviz (US stocks) - Screener for technical patterns
"""

import yfinance as yf
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import json
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class SwingTradingScanner:
    """Advanced scanner for swing trading opportunities"""
    
    def __init__(self):
        self.lookback_period = 50  # Days for support/resistance calculation
        
    def calculate_support_resistance(self, df: pd.DataFrame, window: int = 20) -> Dict:
        """Calculate dynamic support and resistance levels"""
        high = df['High'].rolling(window=window).max()
        low = df['Low'].rolling(window=window).min()
        
        # Current price
        current_price = df['Close'].iloc[-1]
        
        # Recent highs and lows for S/R levels
        recent_highs = df['High'].tail(self.lookback_period)
        recent_lows = df['Low'].tail(self.lookback_period)
        
        # Find significant peaks and troughs
        resistance_levels = []
        support_levels = []
        
        # Simple peak detection
        for i in range(2, len(recent_highs) - 2):
            if (recent_highs.iloc[i] > recent_highs.iloc[i-1] and 
                recent_highs.iloc[i] > recent_highs.iloc[i+1] and
                recent_highs.iloc[i] > recent_highs.iloc[i-2] and 
                recent_highs.iloc[i] > recent_highs.iloc[i+2]):
                resistance_levels.append(recent_highs.iloc[i])
        
        for i in range(2, len(recent_lows) - 2):
            if (recent_lows.iloc[i] < recent_lows.iloc[i-1] and 
                recent_lows.iloc[i] < recent_lows.iloc[i+1] and
                recent_lows.iloc[i] < recent_lows.iloc[i-2] and 
                recent_lows.iloc[i] < recent_lows.iloc[i+2]):
                support_levels.append(recent_lows.iloc[i])
        
        # Get the most relevant levels (closest to current price)
        resistance_levels = sorted(set(resistance_levels))
        support_levels = sorted(set(support_levels))
        
        # Filter to most relevant levels
        nearest_resistance = None
        nearest_support = None
        
        for level in resistance_levels:
            if level > current_price:
                nearest_resistance = level
                break
        
        for level in reversed(support_levels):
            if level < current_price:
                nearest_support = level
                break
        
        return {
            'current_price': current_price,
            'nearest_resistance': nearest_resistance,
            'nearest_support': nearest_support,
            'all_resistance': resistance_levels[-3:] if len(resistance_levels) >= 3 else resistance_levels,
            'all_support': support_levels[-3:] if len(support_levels) >= 3 else support_levels
        }
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate key technical indicators for swing trading"""
        close = df['Close']
        high = df['High']
        low = df['Low']
        volume = df['Volume']
        
        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Moving Averages
        sma_20 = close.rolling(window=20).mean()
        sma_50 = close.rolling(window=50).mean()
        ema_20 = close.ewm(span=20).mean()
        
        # MACD
        ema_12 = close.ewm(span=12).mean()
        ema_26 = close.ewm(span=26).mean()
        macd = ema_12 - ema_26
        macd_signal = macd.ewm(span=9).mean()
        
        # Bollinger Bands
        bb_middle = sma_20
        bb_std = close.rolling(window=20).std()
        bb_upper = bb_middle + (bb_std * 2)
        bb_lower = bb_middle - (bb_std * 2)
        
        # Volume analysis
        volume_ma = volume.rolling(window=20).mean()
        volume_ratio = volume.iloc[-1] / volume_ma.iloc[-1] if volume_ma.iloc[-1] > 0 else 1
        
        return {
            'rsi': rsi.iloc[-1],
            'sma_20': sma_20.iloc[-1],
            'sma_50': sma_50.iloc[-1],
            'ema_20': ema_20.iloc[-1],
            'macd': macd.iloc[-1],
            'macd_signal': macd_signal.iloc[-1],
            'bb_upper': bb_upper.iloc[-1],
            'bb_lower': bb_lower.iloc[-1],
            'bb_middle': bb_middle.iloc[-1],
            'volume_ratio': volume_ratio,
            'current_price': close.iloc[-1]
        }
    
    def identify_swing_setup(self, symbol: str) -> Optional[Dict]:
        """Identify if a stock has a good swing trading setup"""
        try:
            # Download data
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="3mo", interval="1d")
            
            if df.empty or len(df) < 50:
                return None
            
            # Calculate support/resistance and technical indicators
            sr_levels = self.calculate_support_resistance(df)
            tech_indicators = self.calculate_technical_indicators(df)
            
            current_price = sr_levels['current_price']
            nearest_resistance = sr_levels['nearest_resistance']
            nearest_support = sr_levels['nearest_support']
            
            # Swing trading criteria
            setup_score = 0
            setup_reasons = []
            entry_type = None
            
            # Distance to support/resistance (key swing criterion)
            if nearest_support:
                support_distance = ((current_price - nearest_support) / current_price) * 100
                if support_distance <= 3:  # Within 3% of support
                    setup_score += 30
                    setup_reasons.append(f"Near support: {support_distance:.1f}% away")
                    entry_type = "SUPPORT_BOUNCE"
            
            if nearest_resistance:
                resistance_distance = ((nearest_resistance - current_price) / current_price) * 100
                if resistance_distance <= 3:  # Within 3% of resistance
                    setup_score += 25
                    setup_reasons.append(f"Near resistance: {resistance_distance:.1f}% away")
                    if entry_type != "SUPPORT_BOUNCE":
                        entry_type = "RESISTANCE_BREAK"
            
            # RSI conditions for swing trading
            rsi = tech_indicators['rsi']
            if 30 <= rsi <= 40:  # Oversold but recovering
                setup_score += 20
                setup_reasons.append(f"RSI oversold recovery: {rsi:.1f}")
            elif 60 <= rsi <= 70:  # Strong but not overbought
                setup_score += 15
                setup_reasons.append(f"RSI strong momentum: {rsi:.1f}")
            
            # Moving average alignment
            sma_20 = tech_indicators['sma_20']
            sma_50 = tech_indicators['sma_50']
            if sma_20 > sma_50:  # Uptrend
                setup_score += 15
                setup_reasons.append("SMA bullish alignment")
            
            # MACD momentum
            macd = tech_indicators['macd']
            macd_signal = tech_indicators['macd_signal']
            if macd > macd_signal and macd > 0:
                setup_score += 10
                setup_reasons.append("MACD bullish momentum")
            
            # Volume confirmation
            volume_ratio = tech_indicators['volume_ratio']
            if volume_ratio > 1.2:  # Above average volume
                setup_score += 10
                setup_reasons.append(f"High volume: {volume_ratio:.1f}x avg")
            
            # Bollinger Bands position
            bb_upper = tech_indicators['bb_upper']
            bb_lower = tech_indicators['bb_lower']
            if current_price <= bb_lower * 1.02:  # Near lower band
                setup_score += 15
                setup_reasons.append("Near Bollinger lower band")
            
            # Only return if it's a good setup
            if setup_score >= 40:  # Minimum threshold for swing trade
                return {
                    'symbol': symbol,
                    'current_price': current_price,
                    'setup_score': setup_score,
                    'entry_type': entry_type,
                    'reasons': setup_reasons,
                    'nearest_support': nearest_support,
                    'nearest_resistance': nearest_resistance,
                    'rsi': rsi,
                    'volume_ratio': volume_ratio,
                    'recommendation': self._get_recommendation(setup_score, entry_type),
                    'risk_reward': self._calculate_risk_reward(current_price, nearest_support, nearest_resistance)
                }
            
            return None
            
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            return None
    
    def _get_recommendation(self, score: int, entry_type: str) -> str:
        """Get trading recommendation based on setup score"""
        if score >= 70:
            return "STRONG BUY"
        elif score >= 55:
            return "BUY"
        elif score >= 40:
            return "WATCH"
        else:
            return "AVOID"
    
    def _calculate_risk_reward(self, price: float, support: Optional[float], resistance: Optional[float]) -> str:
        """Calculate risk-reward ratio"""
        if not support or not resistance:
            return "N/A"
        
        risk = price - support
        reward = resistance - price
        
        if risk > 0:
            ratio = reward / risk
            return f"{ratio:.1f}:1"
        
        return "N/A"
    
    def scan_market(self, symbols: List[str], market_name: str = "") -> List[Dict]:
        """Scan a list of symbols for swing trading opportunities"""
        print(f"🔍 Scanning {market_name} market for swing trade opportunities...")
        opportunities = []
        
        for i, symbol in enumerate(symbols):
            print(f"  Analyzing {symbol} ({i+1}/{len(symbols)})...", end=" ")
            
            setup = self.identify_swing_setup(symbol)
            if setup:
                opportunities.append(setup)
                print(f"✅ Found setup: {setup['recommendation']}")
            else:
                print("❌")
        
        # Sort by setup score
        opportunities.sort(key=lambda x: x['setup_score'], reverse=True)
        return opportunities

def get_expanded_watchlists() -> Dict[str, List[str]]:
    """Get expanded watchlists for better swing trading coverage"""
    
    # US Market - S&P 500 top stocks + popular swing trading stocks
    us_stocks = [
        # Tech giants
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'NFLX',
        # Financial
        'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C',
        # Healthcare
        'JNJ', 'PFE', 'UNH', 'ABBV', 'BMY', 'MRK',
        # Consumer
        'KO', 'PG', 'WMT', 'HD', 'NKE', 'SBUX',
        # Energy & Materials
        'XOM', 'CVX', 'COP', 'FCX', 'NEM',
        # Popular swing trading stocks
        'SPY', 'QQQ', 'IWM', 'AMD', 'BABA', 'DIS', 'V', 'MA'
    ]
    
    # Indian Market - Nifty 50 + popular swing stocks
    indian_stocks = [
        # Nifty heavyweights
        'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS',
        'ICICIBANK.NS', 'KOTAKBANK.NS', 'BHARTIARTL.NS', 'ITC.NS', 'SBIN.NS',
        'BAJFINANCE.NS', 'ASIANPAINT.NS', 'MARUTI.NS', 'HCLTECH.NS', 'AXISBANK.NS',
        # Swing trading favorites
        'TATAMOTORS.NS', 'WIPRO.NS', 'ONGC.NS', 'NTPC.NS', 'POWERGRID.NS',
        'TATASTEEL.NS', 'JSWSTEEL.NS', 'VEDL.NS', 'ADANIPORTS.NS', 'GRASIM.NS',
        'TECHM.NS', 'LTIM.NS', 'CIPLA.NS', 'DRREDDY.NS', 'SUNPHARMA.NS'
    ]
    
    # Malaysian Market - Top 30 + active stocks (corrected symbols)
    malaysian_stocks = [
        # Blue chips with correct symbols
        '1155.KL',   # Maybank
        '1023.KL',   # CIMB Group
        'PBBANK.KL', # Public Bank (alternative format)
        '1066.KL',   # RHB Bank
        '1015.KL',   # AMMB Holdings
        '5347.KL',   # Tenaga Nasional
        '3182.KL',   # Genting Berhad
        'IOICORP.KL', # IOI Corporation (alternative format)
        '4197.KL',   # Sime Darby Plantation
        '4715.KL',   # YTL Corporation
        # Active swing stocks
        '3816.KL', '1066.KL', '5225.KL', '6012.KL', '3888.KL',
        '4197.KL', '5347.KL', '1818.KL', '2445.KL', '3034.KL',
        '7277.KL', '8621.KL', '2291.KL', '6947.KL', '2739.KL'
    ]
    
    return {
        'usa': us_stocks[:30],  # Limit for performance
        'india': indian_stocks[:25],
        'malaysia': malaysian_stocks[:20]
    }

def main():
    """Main function to run swing trading scanner"""
    print("🎯 Advanced Swing Trading Scanner")
    print("=" * 50)
    print("Scanning for stocks near support/resistance levels...")
    print()
    
    scanner = SwingTradingScanner()
    watchlists = get_expanded_watchlists()
    
    all_opportunities = []
    
    # Scan each market
    for market, symbols in watchlists.items():
        market_name = f"🇺🇸 US" if market == 'usa' else f"🇮🇳 India" if market == 'india' else f"🇲🇾 Malaysia"
        opportunities = scanner.scan_market(symbols, market_name)
        
        if opportunities:
            print(f"\n📈 {market_name} Swing Trade Opportunities:")
            print("-" * 40)
            
            for opp in opportunities[:5]:  # Top 5 per market
                symbol = opp['symbol']
                price = opp['current_price']
                score = opp['setup_score']
                recommendation = opp['recommendation']
                entry_type = opp['entry_type']
                risk_reward = opp['risk_reward']
                
                # Format price based on market
                if '.NS' in symbol:
                    price_str = f"₹{price:.2f}"
                elif '.KL' in symbol:
                    price_str = f"RM{price:.2f}"
                else:
                    price_str = f"${price:.2f}"
                
                print(f"  🎯 {symbol:<12} | {price_str:<10} | Score: {score:<3} | {recommendation:<10} | R:R {risk_reward}")
                print(f"      💡 {entry_type}: {', '.join(opp['reasons'][:2])}")
                print()
            
            all_opportunities.extend(opportunities)
        else:
            print(f"\n❌ No swing opportunities found in {market_name} market")
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"   Total opportunities found: {len(all_opportunities)}")
    print(f"   Strong setups (70+ score): {len([o for o in all_opportunities if o['setup_score'] >= 70])}")
    print(f"   Good setups (55+ score): {len([o for o in all_opportunities if o['setup_score'] >= 55])}")
    
    # Top 3 overall
    if all_opportunities:
        print(f"\n🏆 Top 3 Overall Swing Opportunities:")
        print("-" * 40)
        
        for i, opp in enumerate(all_opportunities[:3], 1):
            symbol = opp['symbol']
            price = opp['current_price']
            
            if '.NS' in symbol:
                price_str = f"₹{price:.2f}"
                market_flag = "🇮🇳"
            elif '.KL' in symbol:
                price_str = f"RM{price:.2f}"
                market_flag = "🇲🇾"
            else:
                price_str = f"${price:.2f}"
                market_flag = "🇺🇸"
            
            print(f"  {i}. {market_flag} {symbol} - {price_str} (Score: {opp['setup_score']})")
            print(f"     🎯 {opp['recommendation']} | {opp['entry_type']} | R:R {opp['risk_reward']}")
            print(f"     💡 {', '.join(opp['reasons'][:3])}")
            print()
    
    print("✅ Swing trading scan complete!")
    print("\n💡 Best Data Sources for Daily Monitoring:")
    print("   🔸 TradingView.com - Best charts & screeners")
    print("   🔸 Finviz.com - US stock screener")
    print("   🔸 Screener.in - Indian stock analysis")
    print("   🔸 Yahoo Finance - Free data API")
    print("   🔸 This scanner - Daily automated scans")

if __name__ == "__main__":
    main()
