#!/usr/bin/env python3
"""
Enhanced Daily Signals with Swing Trading Analysis
Integrates with dashboard to show real-time swing opportunities
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
from typing import Dict, List, Optional
import logging
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class EnhancedSwingAnalyzer:
    """Enhanced analyzer for dashboard integration"""
    
    def __init__(self):
        self.lookback_period = 50
        
    def calculate_support_resistance(self, df: pd.DataFrame) -> Dict:
        """Calculate dynamic support and resistance levels"""
        if len(df) < 20:
            return {'current_price': df['Close'].iloc[-1], 'nearest_resistance': None, 'nearest_support': None}
            
        current_price = df['Close'].iloc[-1]
        
        # Rolling highs and lows for pivot detection
        window = min(20, len(df) // 3)
        
        # Find pivot highs (resistance)
        highs = df['High'].rolling(window=5, center=True).max()
        resistance_candidates = []
        
        for i in range(5, len(df) - 5):
            if df['High'].iloc[i] == highs.iloc[i] and df['High'].iloc[i] > current_price:
                resistance_candidates.append(df['High'].iloc[i])
        
        # Find pivot lows (support)
        lows = df['Low'].rolling(window=5, center=True).min()
        support_candidates = []
        
        for i in range(5, len(df) - 5):
            if df['Low'].iloc[i] == lows.iloc[i] and df['Low'].iloc[i] < current_price:
                support_candidates.append(df['Low'].iloc[i])
        
        # Get nearest levels
        nearest_resistance = min(resistance_candidates) if resistance_candidates else None
        nearest_support = max(support_candidates) if support_candidates else None
        
        return {
            'current_price': current_price,
            'nearest_resistance': nearest_resistance,
            'nearest_support': nearest_support
        }
    
    def calculate_swing_signals(self, symbol: str, period: str = "3mo") -> Optional[Dict]:
        """Calculate comprehensive swing trading signals"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval="1d")
            
            if df.empty or len(df) < 30:
                return None
            
            # Basic technical indicators
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
            
            # Support/Resistance
            sr_levels = self.calculate_support_resistance(df)
            
            # Volume analysis
            volume_ma = volume.rolling(window=20).mean()
            volume_ratio = volume.iloc[-1] / volume_ma.iloc[-1] if volume_ma.iloc[-1] > 0 else 1
            
            # Current values
            current_price = close.iloc[-1]
            current_rsi = rsi.iloc[-1]
            current_sma_20 = sma_20.iloc[-1]
            current_sma_50 = sma_50.iloc[-1]
            current_macd = macd.iloc[-1]
            current_macd_signal = macd_signal.iloc[-1]
            
            # Swing trading score calculation
            score = 0
            signals = []
            entry_type = "WATCH"
            
            # Distance to support/resistance
            nearest_support = sr_levels['nearest_support']
            nearest_resistance = sr_levels['nearest_resistance']
            
            support_distance = None
            resistance_distance = None
            
            if nearest_support:
                support_distance = ((current_price - nearest_support) / current_price) * 100
                if support_distance <= 3:  # Within 3% of support
                    score += 30
                    signals.append(f"Near support ({support_distance:.1f}%)")
                    entry_type = "SUPPORT_BOUNCE"
            
            if nearest_resistance:
                resistance_distance = ((nearest_resistance - current_price) / current_price) * 100
                if resistance_distance <= 3:  # Within 3% of resistance
                    score += 25
                    signals.append(f"Near resistance ({resistance_distance:.1f}%)")
                    if entry_type != "SUPPORT_BOUNCE":
                        entry_type = "RESISTANCE_BREAK"
            
            # RSI signals
            if 30 <= current_rsi <= 40:
                score += 20
                signals.append(f"RSI oversold recovery ({current_rsi:.1f})")
            elif 60 <= current_rsi <= 70:
                score += 15
                signals.append(f"RSI strong momentum ({current_rsi:.1f})")
            elif current_rsi < 30:
                score += 10
                signals.append(f"RSI oversold ({current_rsi:.1f})")
            
            # Moving average alignment
            if current_sma_20 > current_sma_50:
                score += 15
                signals.append("Bullish MA alignment")
            
            # MACD momentum
            if current_macd > current_macd_signal:
                score += 10
                signals.append("MACD bullish")
            
            # Volume confirmation
            if volume_ratio > 1.2:
                score += 10
                signals.append(f"High volume ({volume_ratio:.1f}x)")
            
            # Price position relative to MAs
            if current_price > current_sma_20 > current_sma_50:
                score += 10
                signals.append("Above key MAs")
            
            # Determine recommendation
            if score >= 70:
                recommendation = "STRONG BUY"
            elif score >= 55:
                recommendation = "BUY"
            elif score >= 40:
                recommendation = "WATCH"
            elif score <= 25:
                recommendation = "AVOID"
            else:
                recommendation = "HOLD"
            
            # Risk/reward calculation
            risk_reward = "N/A"
            if nearest_support and nearest_resistance:
                risk = current_price - nearest_support
                reward = nearest_resistance - current_price
                if risk > 0:
                    risk_reward = f"{reward/risk:.1f}:1"
            
            # Price change
            price_change_pct = ((current_price - close.iloc[-2]) / close.iloc[-2]) * 100 if len(close) > 1 else 0
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'price_change_pct': price_change_pct,
                'swing_score': score,
                'recommendation': recommendation,
                'entry_type': entry_type,
                'signals': signals,
                'rsi': current_rsi,
                'volume_ratio': volume_ratio,
                'support_level': nearest_support,
                'resistance_level': nearest_resistance,
                'support_distance': support_distance,
                'resistance_distance': resistance_distance,
                'risk_reward': risk_reward,
                'sma_20': current_sma_20,
                'sma_50': current_sma_50,
                'macd': current_macd,
                'macd_signal': current_macd_signal,
                'trend': "BULLISH" if current_sma_20 > current_sma_50 else "BEARISH",
                
                # Enhanced data for detailed analysis
                'support_levels': self._get_multiple_support_levels(df, current_price),
                'resistance_levels': self._get_multiple_resistance_levels(df, current_price),
                'bollinger_bands': self._calculate_bollinger_bands(df['Close']),
                'stochastic': self._calculate_stochastic(df),
                'volume_trend': 'High' if volume_ratio > 1.5 else 'Normal' if volume_ratio > 0.8 else 'Low',
                'macd_signal_trend': 'Bullish' if current_macd > current_macd_signal else 'Bearish',
                'trend_strength': self._calculate_trend_strength(df['Close']),
                'volatility': self._calculate_volatility(df['Close']),
                'momentum': self._calculate_momentum_score(df['Close'])
            }
            
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            return None
    
    def _get_multiple_support_levels(self, data, current_price):
        """Calculate multiple support levels for detailed analysis"""
        try:
            lows = data['Low'].values
            support_levels = []
            
            # Find recent swing lows
            for i in range(10, len(lows) - 10):
                if lows[i] == min(lows[max(0, i-10):i+11]):
                    if lows[i] < current_price:
                        support_levels.append(round(lows[i], 2))
            
            # Add moving average supports
            if len(data) >= 20:
                sma_20 = data['Close'].rolling(window=20).mean().iloc[-1]
                if sma_20 < current_price:
                    support_levels.append(round(sma_20, 2))
            
            if len(data) >= 50:
                sma_50 = data['Close'].rolling(window=50).mean().iloc[-1]
                if sma_50 < current_price:
                    support_levels.append(round(sma_50, 2))
            
            # Remove duplicates and sort
            support_levels = sorted(list(set(support_levels)), reverse=True)
            return support_levels[:5]  # Return top 5
            
        except Exception:
            return [current_price * 0.95, current_price * 0.90]
    
    def _get_multiple_resistance_levels(self, data, current_price):
        """Calculate multiple resistance levels for detailed analysis"""
        try:
            highs = data['High'].values
            resistance_levels = []
            
            # Find recent swing highs
            for i in range(10, len(highs) - 10):
                if highs[i] == max(highs[max(0, i-10):i+11]):
                    if highs[i] > current_price:
                        resistance_levels.append(round(highs[i], 2))
            
            # Add moving average resistance if price is below
            if len(data) >= 20:
                sma_20 = data['Close'].rolling(window=20).mean().iloc[-1]
                if sma_20 > current_price:
                    resistance_levels.append(round(sma_20, 2))
            
            if len(data) >= 50:
                sma_50 = data['Close'].rolling(window=50).mean().iloc[-1]
                if sma_50 > current_price:
                    resistance_levels.append(round(sma_50, 2))
            
            # Remove duplicates and sort
            resistance_levels = sorted(list(set(resistance_levels)))
            return resistance_levels[:5]  # Return top 5
            
        except Exception:
            return [current_price * 1.05, current_price * 1.10]
    
    def _calculate_bollinger_bands(self, prices, period=20):
        """Calculate Bollinger Bands"""
        try:
            sma = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()
            
            upper_band = sma + (std * 2)
            lower_band = sma - (std * 2)
            
            return {
                'upper': round(upper_band.iloc[-1], 2),
                'middle': round(sma.iloc[-1], 2),
                'lower': round(lower_band.iloc[-1], 2)
            }
        except Exception:
            current = prices.iloc[-1]
            return {
                'upper': round(current * 1.02, 2),
                'middle': round(current, 2),
                'lower': round(current * 0.98, 2)
            }
    
    def _calculate_stochastic(self, data, k_period=14):
        """Calculate Stochastic Oscillator"""
        try:
            if len(data) < k_period:
                return 50
            
            low_min = data['Low'].rolling(window=k_period).min()
            high_max = data['High'].rolling(window=k_period).max()
            
            k_percent = 100 * ((data['Close'] - low_min) / (high_max - low_min))
            
            return round(k_percent.iloc[-1], 1) if not pd.isna(k_percent.iloc[-1]) else 50
        except Exception:
            return 50
    
    def _calculate_trend_strength(self, prices):
        """Calculate trend strength"""
        try:
            if len(prices) < 20:
                return "Neutral"
            
            recent_avg = prices.tail(5).mean()
            older_avg = prices.tail(20).head(5).mean()
            
            change_pct = ((recent_avg - older_avg) / older_avg) * 100
            
            if change_pct > 5:
                return "Strong Uptrend"
            elif change_pct > 2:
                return "Uptrend"
            elif change_pct < -5:
                return "Strong Downtrend"
            elif change_pct < -2:
                return "Downtrend"
            else:
                return "Sideways"
        except Exception:
            return "Neutral"
    
    def _calculate_volatility(self, prices, period=20):
        """Calculate price volatility"""
        try:
            returns = prices.pct_change().dropna()
            volatility = returns.tail(period).std() * (252 ** 0.5) * 100  # Annualized
            return round(volatility, 1)
        except Exception:
            return 20.0  # Default volatility
    
    def _calculate_momentum_score(self, prices):
        """Calculate momentum score"""
        try:
            if len(prices) < 10:
                return 0
            
            momentum = ((prices.iloc[-1] - prices.iloc[-10]) / prices.iloc[-10]) * 100
            return round(momentum, 2)
        except Exception:
            return 0
    
    def get_portfolio_position_analysis(self, portfolio_positions: List[Dict]) -> List[Dict]:
        """Analyze existing portfolio positions for hold/sell signals"""
        position_analysis = []
        
        for position in portfolio_positions:
            symbol = position['symbol']
            entry_price = position['avg_price']
            current_shares = position['shares']
            
            # Get current analysis
            analysis = self.calculate_swing_signals(symbol)
            
            if analysis:
                current_price = analysis['current_price']
                pnl_pct = ((current_price - entry_price) / entry_price) * 100
                
                # Position-specific signals
                position_signals = []
                action_score = 0
                
                # Profit/loss analysis
                if pnl_pct > 10:
                    action_score += 15
                    position_signals.append(f"Strong profit (+{pnl_pct:.1f}%)")
                elif pnl_pct > 5:
                    action_score += 10
                    position_signals.append(f"Good profit (+{pnl_pct:.1f}%)")
                elif pnl_pct < -5:
                    action_score -= 15
                    position_signals.append(f"Loss ({pnl_pct:.1f}%)")
                
                # Technical analysis for positions
                if analysis['resistance_level'] and current_price >= analysis['resistance_level'] * 0.98:
                    action_score += 20
                    position_signals.append("Near resistance - consider taking profit")
                
                if analysis['support_level'] and current_price <= analysis['support_level'] * 1.02:
                    action_score -= 20
                    position_signals.append("Near support - consider stop loss")
                
                if analysis['rsi'] > 70:
                    action_score += 10
                    position_signals.append("RSI overbought - profit taking zone")
                elif analysis['rsi'] < 30:
                    action_score -= 10
                    position_signals.append("RSI oversold - hold for recovery")
                
                # Determine action
                if action_score > 20:
                    action = "SELL"
                elif action_score > 10:
                    action = "PARTIAL_SELL"
                elif action_score < -15:
                    action = "STOP_LOSS"
                elif action_score < -5:
                    action = "WATCH_CLOSE"
                else:
                    action = "HOLD"
                
                position_analysis.append({
                    'symbol': symbol,
                    'entry_price': entry_price,
                    'current_price': current_price,
                    'shares': current_shares,
                    'pnl_pct': pnl_pct,
                    'action': action,
                    'action_score': action_score,
                    'signals': position_signals,
                    'swing_analysis': analysis
                })
        
        return position_analysis
    
    def scan_top_opportunities(self, symbols: List[str], market_name: str, limit: int = 5) -> List[Dict]:
        """Scan for top swing opportunities in a market"""
        opportunities = []
        
        for symbol in symbols:
            analysis = self.calculate_swing_signals(symbol)
            if analysis and analysis['swing_score'] >= 40:  # Minimum threshold
                opportunities.append(analysis)
        
        # Sort by swing score and return top N
        opportunities.sort(key=lambda x: x['swing_score'], reverse=True)
        return opportunities[:limit]

def get_market_watchlists() -> Dict[str, List[str]]:
    """Get optimized watchlists for daily scanning"""
    return {
        'usa': [
            # Tech
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'NFLX',
            # Finance
            'JPM', 'BAC', 'WFC', 'GS', 'V', 'MA',
            # Consumer
            'KO', 'PG', 'WMT', 'HD', 'NKE', 'DIS',
            # Healthcare
            'JNJ', 'PFE', 'UNH', 'ABBV',
            # Other
            'SPY', 'QQQ', 'XOM', 'CVX'
        ],
        'india': [
            # Large caps
            'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS',
            'ICICIBANK.NS', 'KOTAKBANK.NS', 'BHARTIARTL.NS', 'ITC.NS', 'SBIN.NS',
            # Swing favorites
            'BAJFINANCE.NS', 'ASIANPAINT.NS', 'MARUTI.NS', 'HCLTECH.NS', 'AXISBANK.NS',
            'TATAMOTORS.NS', 'WIPRO.NS', 'ONGC.NS', 'NTPC.NS', 'POWERGRID.NS',
            'TATASTEEL.NS', 'JSWSTEEL.NS', 'VEDL.NS', 'ADANIPORTS.NS', 'GRASIM.NS'
        ],
        'malaysia': [
            # Corrected symbols
            '1155.KL', '1023.KL', 'PBBANK.KL', '1066.KL', '1015.KL',
            '5347.KL', '3182.KL', 'IOICORP.KL', '4197.KL', '4715.KL',
            '3816.KL', '5225.KL', '6012.KL', '1818.KL', '2445.KL',
            '3034.KL', '7277.KL', '2291.KL', '6947.KL', '2739.KL'
        ]
    }

# For dashboard integration
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_daily_swing_signals(portfolio_manager=None) -> Dict:
    """Main function for dashboard integration with caching"""
    analyzer = EnhancedSwingAnalyzer()
    watchlists = get_market_watchlists()
    
    print("🔄 Analyzing swing opportunities...")
    
    # Get top opportunities for each market
    results = {
        'timestamp': datetime.now(),
        'markets': {},
        'portfolio_analysis': []
    }
    
    for market, symbols in watchlists.items():
        market_name = "🇺🇸 USA" if market == 'usa' else "🇮🇳 India" if market == 'india' else "🇲🇾 Malaysia"
        print(f"  Scanning {market_name}...")
        
        opportunities = analyzer.scan_top_opportunities(symbols, market_name, limit=5)
        results['markets'][market] = {
            'name': market_name,
            'opportunities': opportunities,
            'total_scanned': len(symbols),
            'opportunities_found': len(opportunities)
        }
    
    # Note: Portfolio analysis can't be cached due to dynamic nature
    print("✅ Analysis complete!")
    return results

def get_portfolio_analysis(portfolio_manager) -> List[Dict]:
    """Separate function for portfolio analysis (not cached)"""
    if not portfolio_manager:
        return []
    
    analyzer = EnhancedSwingAnalyzer()
    current_positions = portfolio_manager.get_current_positions()
    
    if current_positions:
        print("  Analyzing current positions...")
        return analyzer.get_portfolio_position_analysis(current_positions)
    
    return []
