#!/usr/bin/env python3
"""
Professional Technical Analysis Module
Addresses critical signal contradictions and implements proper indicator calculations
"""

import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Optional, Tuple
import talib
from datetime import datetime, timedelta

class ProfessionalTechnicalAnalysis:
    """
    Professional-grade technical analysis with proper indicator calculations
    Fixes contradictory signals and implements market-standard interpretations
    """
    
    def __init__(self):
        self.rsi_period = 14
        self.macd_fast = 12
        self.macd_slow = 26
        self.macd_signal = 9
        self.bb_period = 20
        self.bb_std = 2
        self.adx_period = 14
        
    def calculate_comprehensive_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators with proper interpretations"""
        
        # Trend Indicators
        df['SMA_20'] = talib.SMA(df['Close'], timeperiod=20)
        df['SMA_50'] = talib.SMA(df['Close'], timeperiod=50)
        df['EMA_12'] = talib.EMA(df['Close'], timeperiod=12)
        df['EMA_26'] = talib.EMA(df['Close'], timeperiod=26)
        
        # ADX for trend strength
        df['ADX'] = talib.ADX(df['High'], df['Low'], df['Close'], timeperiod=self.adx_period)
        df['+DI'] = talib.PLUS_DI(df['High'], df['Low'], df['Close'], timeperiod=self.adx_period)
        df['-DI'] = talib.MINUS_DI(df['High'], df['Low'], df['Close'], timeperiod=self.adx_period)
        
        # MACD
        df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = talib.MACD(
            df['Close'], fastperiod=self.macd_fast, slowperiod=self.macd_slow, signalperiod=self.macd_signal
        )
        
        # Momentum Oscillators
        df['RSI'] = talib.RSI(df['Close'], timeperiod=self.rsi_period)
        df['Stoch_K'], df['Stoch_D'] = talib.STOCH(df['High'], df['Low'], df['Close'])
        df['Williams_R'] = talib.WILLR(df['High'], df['Low'], df['Close'])
        df['Stoch_RSI_K'], df['Stoch_RSI_D'] = talib.STOCHRSI(df['Close'])
        
        # Bollinger Bands
        df['BB_Upper'], df['BB_Middle'], df['BB_Lower'] = talib.BBANDS(
            df['Close'], timeperiod=self.bb_period, nbdevup=self.bb_std, nbdevdn=self.bb_std
        )
        df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle']
        df['BB_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        
        # Volume Indicators
        df['OBV'] = talib.OBV(df['Close'], df['Volume'])
        df['AD'] = talib.AD(df['High'], df['Low'], df['Close'], df['Volume'])
        df['Volume_SMA'] = talib.SMA(df['Volume'], timeperiod=20)
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
        
        # Volatility
        df['ATR'] = talib.ATR(df['High'], df['Low'], df['Close'], timeperiod=14)
        df['True_Range'] = talib.TRANGE(df['High'], df['Low'], df['Close'])
        
        # VWAP calculation
        df['VWAP'] = (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum() / df['Volume'].cumsum()
        
        return df
    
    def interpret_rsi(self, rsi_value: float) -> Dict[str, str]:
        """Proper RSI interpretation based on market standards"""
        if rsi_value >= 70:
            return {
                'status': 'Overbought',
                'signal': 'SELL_WARNING',
                'color': '🔴',
                'description': 'RSI above 70 indicates overbought conditions'
            }
        elif rsi_value <= 30:
            return {
                'status': 'Oversold',
                'signal': 'BUY_OPPORTUNITY',
                'color': '🟢',
                'description': 'RSI below 30 indicates oversold conditions'
            }
        elif 30 < rsi_value < 40:
            return {
                'status': 'Oversold Zone',
                'signal': 'POTENTIAL_BUY',
                'color': '🟡',
                'description': 'RSI in oversold zone, potential bounce opportunity'
            }
        elif 60 < rsi_value < 70:
            return {
                'status': 'Overbought Zone',
                'signal': 'CAUTION',
                'color': '🟡',
                'description': 'RSI approaching overbought, watch for reversal'
            }
        else:
            return {
                'status': 'Neutral',
                'signal': 'NEUTRAL',
                'color': '⚪',
                'description': 'RSI in neutral range (40-60)'
            }
    
    def _interpret_rsi(self, rsi_value: float) -> Dict[str, str]:
        """Wrapper for interpret_rsi for test compatibility"""
        return self.interpret_rsi(rsi_value)
    
    def analyze_stock(self, symbol: str) -> Optional[Dict]:
        """Comprehensive stock analysis using professional technical analysis"""
        try:
            # Get data
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="6mo", interval="1d")
            
            if len(df) < 50:
                return None
            
            current_price = df['Close'].iloc[-1]
            
            # Calculate technical indicators
            df['RSI'] = talib.RSI(df['Close'].values, timeperiod=14)
            macd_line, signal_line, histogram = talib.MACD(df['Close'].values)
            df['MACD'] = macd_line
            df['MACD_Signal'] = signal_line
            df['MACD_Histogram'] = histogram
            
            # Get current values
            current_rsi = df['RSI'].iloc[-1]
            current_macd = df['MACD'].iloc[-1]
            current_signal = df['MACD_Signal'].iloc[-1]
            current_histogram = df['MACD_Histogram'].iloc[-1]
            
            # Interpret indicators
            rsi_analysis = self.interpret_rsi(current_rsi)
            macd_analysis = self.interpret_macd(current_macd, current_signal, current_histogram)
            
            # Calculate overall score
            score = 50  # Base score
            
            if rsi_analysis['signal'] == 'BUY_OPPORTUNITY':
                score += 25
            elif rsi_analysis['signal'] == 'POTENTIAL_BUY':
                score += 15
            elif rsi_analysis['signal'] == 'SELL_WARNING':
                score -= 25
            
            if macd_analysis['signal'] == 'BUY':
                score += 20
            elif macd_analysis['signal'] == 'SELL':
                score -= 20
            
            score = max(0, min(100, score))
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'rsi': {
                    'value': current_rsi,
                    'signal': rsi_analysis['status'],
                    'description': rsi_analysis['description']
                },
                'macd': {
                    'signal': macd_analysis['status'],
                    'description': macd_analysis['description']
                },
                'overall_score': score
            }
            
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            return None
    
    def interpret_macd(self, macd_line: float, signal_line: float, histogram: float) -> Dict[str, str]:
        """Proper MACD interpretation"""
        if macd_line > signal_line and histogram > 0:
            if histogram > np.roll(np.array([histogram]), 1)[0]:  # Rising histogram
                return {
                    'status': 'Bullish',
                    'signal': 'BUY',
                    'color': '🟢',
                    'description': 'MACD above signal line with rising momentum'
                }
            else:
                return {
                    'status': 'Bullish Weakening',
                    'signal': 'HOLD',
                    'color': '🟡',
                    'description': 'MACD above signal but momentum weakening'
                }
        elif macd_line < signal_line and histogram < 0:
            if histogram < np.roll(np.array([histogram]), 1)[0]:  # Falling histogram
                return {
                    'status': 'Bearish',
                    'signal': 'SELL',
                    'color': '🔴',
                    'description': 'MACD below signal line with falling momentum'
                }
            else:
                return {
                    'status': 'Bearish Weakening',
                    'signal': 'WAIT',
                    'color': '🟡',
                    'description': 'MACD below signal but momentum improving'
                }
        else:
            return {
                'status': 'Neutral',
                'signal': 'NEUTRAL',
                'color': '⚪',
                'description': 'MACD near signal line, no clear direction'
            }
    
    def interpret_trend_strength(self, adx: float, plus_di: float, minus_di: float) -> Dict[str, str]:
        """ADX-based trend strength interpretation"""
        if adx < 20:
            return {
                'strength': 'Weak/Sideways',
                'direction': 'Consolidation',
                'color': '⚪',
                'description': 'No clear trend, market in consolidation'
            }
        elif 20 <= adx < 40:
            direction = 'Uptrend' if plus_di > minus_di else 'Downtrend'
            return {
                'strength': 'Moderate',
                'direction': direction,
                'color': '🟡',
                'description': f'Moderate {direction.lower()} in progress'
            }
        else:  # adx >= 40
            direction = 'Strong Uptrend' if plus_di > minus_di else 'Strong Downtrend'
            color = '🟢' if plus_di > minus_di else '🔴'
            return {
                'strength': 'Strong',
                'direction': direction,
                'color': color,
                'description': f'{direction} with strong momentum'
            }
    
    def calculate_support_resistance(self, df: pd.DataFrame, lookback: int = 20) -> Dict[str, List[float]]:
        """Calculate dynamic support and resistance levels using pivot points"""
        
        # Pivot highs and lows
        highs = df['High'].rolling(window=lookback).max()
        lows = df['Low'].rolling(window=lookback).min()
        
        # Recent pivot points
        recent_highs = highs.tail(5).unique()
        recent_lows = lows.tail(5).unique()
        
        # Remove current price area to avoid noise
        current_price = df['Close'].iloc[-1]
        price_threshold = current_price * 0.02  # 2% threshold
        
        resistance_levels = [h for h in recent_highs if h > current_price + price_threshold]
        support_levels = [l for l in recent_lows if l < current_price - price_threshold]
        
        # Add Fibonacci levels if we have a clear swing
        if len(df) >= 50:
            swing_high = df['High'].tail(50).max()
            swing_low = df['Low'].tail(50).min()
            
            fib_levels = [
                swing_low + (swing_high - swing_low) * 0.236,
                swing_low + (swing_high - swing_low) * 0.382,
                swing_low + (swing_high - swing_low) * 0.618,
            ]
            
            # Add relevant fib levels
            for level in fib_levels:
                if level > current_price:
                    resistance_levels.append(level)
                else:
                    support_levels.append(level)
        
        return {
            'resistance': sorted(list(set(resistance_levels)))[:3],  # Top 3
            'support': sorted(list(set(support_levels)), reverse=True)[:3]  # Top 3
        }
    
    def comprehensive_stock_analysis(self, symbol: str, period: str = "6mo") -> Dict:
        """
        Comprehensive analysis addressing all identified issues
        """
        try:
            # Fetch data
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval="1d")
            
            if df.empty or len(df) < 50:
                return None
            
            # Calculate all indicators
            df = self.calculate_comprehensive_indicators(df)
            
            # Get latest values
            latest = df.iloc[-1]
            current_price = latest['Close']
            
            # Technical Analysis
            rsi_analysis = self.interpret_rsi(latest['RSI'])
            macd_analysis = self.interpret_macd(latest['MACD'], latest['MACD_Signal'], latest['MACD_Hist'])
            trend_analysis = self.interpret_trend_strength(latest['ADX'], latest['+DI'], latest['-DI'])
            
            # Support/Resistance
            levels = self.calculate_support_resistance(df)
            
            # Volume Analysis
            volume_trend = "High" if latest['Volume_Ratio'] > 1.5 else "Normal" if latest['Volume_Ratio'] > 0.8 else "Low"
            
            # Moving Average Analysis
            ma_20_status = "Above" if current_price > latest['SMA_20'] else "Below"
            ma_50_status = "Above" if current_price > latest['SMA_50'] else "Below"
            
            # Price position in Bollinger Bands
            bb_position = "Upper" if latest['BB_Position'] > 0.8 else "Lower" if latest['BB_Position'] < 0.2 else "Middle"
            
            # Calculate comprehensive score
            score = self.calculate_professional_score(df, latest, rsi_analysis, macd_analysis, trend_analysis)
            
            # Risk/Reward calculation
            nearest_resistance = min(levels['resistance']) if levels['resistance'] else current_price * 1.05
            nearest_support = max(levels['support']) if levels['support'] else current_price * 0.95
            
            risk_reward_ratio = (nearest_resistance - current_price) / (current_price - nearest_support) if nearest_support < current_price else 1.0
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'swing_score': score,
                'recommendation': self.get_recommendation(score, risk_reward_ratio),
                'entry_type': self.determine_entry_type(trend_analysis, rsi_analysis),
                'market_name': self.get_market_name(symbol),
                'risk_reward': f"{risk_reward_ratio:.1f}:1",
                
                # Technical Details
                'rsi_analysis': rsi_analysis,
                'macd_analysis': macd_analysis,
                'trend_analysis': trend_analysis,
                'volume_trend': volume_trend,
                'ma_20_status': ma_20_status,
                'ma_50_status': ma_50_status,
                'bb_position': bb_position,
                'support_levels': levels['support'],
                'resistance_levels': levels['resistance'],
                'atr': latest['ATR'],
                'volatility': (latest['ATR'] / current_price) * 100,
                
                # Raw indicator values for debugging
                'rsi_value': latest['RSI'],
                'macd_line': latest['MACD'],
                'macd_signal': latest['MACD_Signal'],
                'macd_histogram': latest['MACD_Hist'],
                'adx': latest['ADX'],
                'plus_di': latest['+DI'],
                'minus_di': latest['-DI'],
                
                'signals': [
                    f"RSI: {latest['RSI']:.1f} ({rsi_analysis['status']})",
                    f"MACD: {macd_analysis['status']}",
                    f"Trend: {trend_analysis['direction']} (ADX: {latest['ADX']:.1f})",
                    f"Volume: {volume_trend}"
                ]
            }
            
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            return None
    
    def calculate_professional_score(self, df: pd.DataFrame, latest: pd.Series, 
                                   rsi_analysis: Dict, macd_analysis: Dict, trend_analysis: Dict) -> int:
        """
        Professional scoring system addressing oversimplified current approach
        """
        score = 50  # Base score
        
        # Trend Analysis (25 points max)
        adx = latest['ADX']
        plus_di = latest['+DI']
        minus_di = latest['-DI']
        
        if adx > 25:  # Strong trend
            if plus_di > minus_di:  # Uptrend
                score += 20
            else:  # Downtrend
                score -= 15
        elif adx > 15:  # Moderate trend
            if plus_di > minus_di:
                score += 10
            else:
                score -= 5
        # Sideways market (adx < 15): no points added/subtracted
        
        # RSI Analysis (20 points max)
        rsi = latest['RSI']
        if 30 <= rsi <= 40:  # Oversold zone
            score += 15
        elif 40 < rsi < 60:  # Neutral zone
            score += 5
        elif 60 <= rsi <= 70:  # Overbought zone
            score -= 5
        elif rsi > 70:  # Overbought
            score -= 15
        elif rsi < 30:  # Severely oversold
            score += 10  # Could bounce but risky
        
        # MACD Analysis (20 points max)
        if macd_analysis['signal'] == 'BUY':
            score += 15
        elif macd_analysis['signal'] == 'HOLD':
            score += 5
        elif macd_analysis['signal'] == 'SELL':
            score -= 15
        elif macd_analysis['signal'] == 'WAIT':
            score -= 5
        
        # Volume Confirmation (15 points max)
        volume_ratio = latest['Volume_Ratio']
        if volume_ratio > 2.0:
            score += 15
        elif volume_ratio > 1.5:
            score += 10
        elif volume_ratio > 1.0:
            score += 5
        elif volume_ratio < 0.5:
            score -= 10
        
        # Moving Average Position (10 points max)
        current_price = latest['Close']
        sma_20 = latest['SMA_20']
        sma_50 = latest['SMA_50']
        
        if current_price > sma_20 > sma_50:
            score += 10
        elif current_price > sma_20:
            score += 5
        elif current_price < sma_20 < sma_50:
            score -= 10
        elif current_price < sma_20:
            score -= 5
        
        # Volatility adjustment (can reduce score)
        atr_percent = (latest['ATR'] / current_price) * 100
        if atr_percent > 5:  # High volatility
            score -= 10
        elif atr_percent > 3:
            score -= 5
        
        return max(0, min(100, score))
    
    def get_recommendation(self, score: int, risk_reward_ratio: float) -> str:
        """Enhanced recommendation logic"""
        if score >= 80 and risk_reward_ratio >= 2.0:
            return "STRONG BUY"
        elif score >= 70 and risk_reward_ratio >= 1.5:
            return "BUY"
        elif score >= 60:
            return "WEAK BUY"
        elif score >= 40:
            return "HOLD"
        else:
            return "AVOID"
    
    def determine_entry_type(self, trend_analysis: Dict, rsi_analysis: Dict) -> str:
        """Determine entry type based on technical setup"""
        if trend_analysis['strength'] == 'Strong' and rsi_analysis['signal'] == 'BUY_OPPORTUNITY':
            return "Trend Continuation"
        elif rsi_analysis['signal'] == 'BUY_OPPORTUNITY':
            return "Oversold Bounce"
        elif trend_analysis['strength'] == 'Strong':
            return "Momentum Play"
        else:
            return "Swing Entry"
    
    def get_market_name(self, symbol: str) -> str:
        """Get market name from symbol"""
        if symbol.endswith('.NS') or symbol.endswith('.BO'):
            return "🇮🇳 India"
        elif symbol.endswith('.KL'):
            return "🇲🇾 Malaysia"
        else:
            return "🇺🇸 USA"
