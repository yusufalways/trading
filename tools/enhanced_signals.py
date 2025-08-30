#!/usr/bin/env python3
"""
Enhanced Daily Signals with Swing Trading Analysis
Uses unified analysis system for consistent and reliable results
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

# Import unified analysis system
try:
    from .unified_swing_analyzer import UnifiedSwingAnalyzer
    UNIFIED_ANALYSIS_AVAILABLE = True
except ImportError:
    print("Unified analysis not available - using basic analysis")
    UNIFIED_ANALYSIS_AVAILABLE = False

# Import legacy modules for compatibility
try:
    from .advanced_technical_analysis import AdvancedTechnicalAnalysis
    from .market_context_analyzer import MarketContextAnalyzer, EnhancedEntryChecklist
    ADVANCED_ANALYSIS_AVAILABLE = True
except ImportError:
    print("Advanced analysis modules not available - using basic analysis")
    ADVANCED_ANALYSIS_AVAILABLE = False

class EnhancedSwingAnalyzer:
    """Enhanced analyzer using unified analysis system"""
    
    def __init__(self):
        self.lookback_period = 50
        if UNIFIED_ANALYSIS_AVAILABLE:
            self.unified_analyzer = UnifiedSwingAnalyzer()
            print("✅ Using unified analysis system for consistent results")
        else:
            print("⚠️ Unified analysis not available - using legacy system")
    
    def calculate_swing_signals(self, symbol: str, period: str = "3mo") -> Optional[Dict]:
        """Calculate comprehensive swing trading signals using unified analysis"""
        
        # Use unified analyzer if available
        if UNIFIED_ANALYSIS_AVAILABLE:
            return self._unified_analysis(symbol, period)
        else:
            return self._legacy_analysis(symbol, period)
    
    def _unified_analysis(self, symbol: str, period: str = "3mo") -> Optional[Dict]:
        """Use unified analysis system for consistent results"""
        try:
            result = self.unified_analyzer.comprehensive_analysis(symbol, period)
            
            if not result:
                return None
            
            # Convert to dashboard-compatible format
            return self._convert_unified_to_dashboard_format(result)
            
        except Exception as e:
            print(f"Unified analysis failed for {symbol}: {e}")
            return self._legacy_analysis(symbol, period)
    
    def _convert_unified_to_dashboard_format(self, unified_result: Dict) -> Dict:
        """Convert unified analysis result to dashboard-compatible format"""
        
        # Extract data from unified result
        tech_analysis = unified_result.get('technical_analysis', {})
        risk_analysis = unified_result.get('risk_analysis', {})
        
        converted = {
            'symbol': unified_result['symbol'],
            'current_price': unified_result['current_price'],
            'swing_score': unified_result['total_score'],
            'recommendation': unified_result['recommendation'],
            'entry_type': unified_result['opportunity_type'],
            'signals': unified_result['entry_rationale'] + unified_result['risk_factors'],
            'market_name': unified_result['market_name'],
            
            # Technical details
            'rsi': tech_analysis.get('rsi', 0),
            'volume_ratio': tech_analysis.get('volume_ratio', 1),
            'support_level': tech_analysis.get('support_level'),
            'resistance_level': tech_analysis.get('resistance_level'),
            'support_distance': tech_analysis.get('support_distance'),
            'resistance_distance': tech_analysis.get('resistance_distance'),
            'risk_reward': f"{risk_analysis.get('risk_reward_ratio', 0):.1f}:1",
            'risk_reward_ratio': risk_analysis.get('risk_reward_ratio', 0),
            
            # Moving averages
            'sma_20': tech_analysis.get('sma_20'),
            'sma_50': tech_analysis.get('sma_50'),
            'trend': "BULLISH" if tech_analysis.get('sma_20', 0) > tech_analysis.get('sma_50', 0) else "BEARISH",
            
            # Additional dashboard compatibility
            'price_change_pct': unified_result.get('price_change_pct', 0),
            'macd': 0,  # Not used in unified system
            'macd_signal': 0,  # Not used in unified system
            'volume_trend': 'High' if tech_analysis.get('volume_ratio', 1) > 1.5 else 'Normal',
            'macd_signal_trend': 'Neutral',
            'trend_strength': 0,
            'volatility': risk_analysis.get('volatility', 20),
            'momentum': 0,
            
            # Enhanced dashboard data
            'support_levels': self._extract_support_levels(tech_analysis),
            'resistance_levels': self._extract_resistance_levels(tech_analysis),
            'bollinger_bands': {'upper': 0, 'middle': 0, 'lower': 0},
            'stochastic': {'k': 0, 'd': 0},
            
            # Advanced analysis data (unified system)
            'advanced_analysis': {
                'advanced_available': True,
                'unified_analysis': unified_result,
                'setup_quality_score': unified_result.get('advanced_score', 0) * 100/30,  # Convert to 100-point scale
                'confidence_level': unified_result['confidence'],
                'recommendation_rationale': unified_result['entry_rationale']
            }
        }
        
        return converted
    
    def _extract_support_levels(self, tech_analysis: Dict) -> Dict:
        """Extract support levels for dashboard display"""
        support_level = tech_analysis.get('support_level')
        if not support_level:
            return {'strong': [], 'medium': [], 'weak': []}
        
        return {
            'strong': [support_level],
            'medium': [support_level * 0.98],  # Approximate additional level
            'weak': [support_level * 0.96]
        }
    
    def _extract_resistance_levels(self, tech_analysis: Dict) -> Dict:
        """Extract resistance levels for dashboard display"""
        resistance_level = tech_analysis.get('resistance_level')
        if not resistance_level:
            return {'strong': [], 'medium': [], 'weak': []}
        
        return {
            'strong': [resistance_level],
            'medium': [resistance_level * 1.02],  # Approximate additional level
            'weak': [resistance_level * 1.04]
        }
    
    def _legacy_analysis(self, symbol: str, period: str = "3mo") -> Optional[Dict]:
        """Legacy analysis system (fallback)"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval="1d")
            
            if df.empty or len(df) < 30:
                return None
            
            # Simplified legacy analysis
            current_price = df['Close'].iloc[-1]
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'swing_score': 50,  # Neutral score
                'recommendation': 'WATCH',
                'entry_type': 'BASIC',
                'signals': ['Legacy analysis - unified system unavailable'],
                'market_name': self._get_market_name(symbol),
                'rsi': 50,
                'volume_ratio': 1,
                'support_level': None,
                'resistance_level': None,
                'risk_reward': 'N/A',
                'risk_reward_ratio': 0,
                'trend': 'NEUTRAL'
            }
        except Exception as e:
            print(f"Legacy analysis failed for {symbol}: {e}")
            return None
    
    def _get_market_name(self, symbol: str) -> str:
        """Determine market name from symbol"""
        if '.NS' in symbol:
            return "🇮🇳 India"
        elif '.KL' in symbol:
            return "🇲🇾 Malaysia"
        else:
            return "🇺🇸 USA"
        
    def calculate_support_resistance(self, df: pd.DataFrame) -> Dict:
        """Calculate comprehensive swing trading signals with advanced analysis"""
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
            
            # Initialize enhanced analysis
            advanced_score = 0
            enhanced_signals = []
            
            # Try to get advanced analysis if available
            if ADVANCED_ANALYSIS_AVAILABLE:
                try:
                    advanced_analyzer = AdvancedTechnicalAnalysis(symbol)
                    advanced_analysis = advanced_analyzer.comprehensive_entry_analysis(current_price)
                    
                    # Extract advanced features
                    setup_quality = advanced_analysis.get('setup_quality_score', 0)
                    confluence = advanced_analysis.get('timeframe_confluence', {})
                    volume_analysis = advanced_analysis.get('volume_analysis', {})
                    patterns = advanced_analysis.get('pattern_analysis', {})
                    market_structure = advanced_analysis.get('market_structure', {})
                    divergences = advanced_analysis.get('momentum_divergences', {})
                    
                    # Add advanced scoring
                    advanced_score += min(setup_quality * 0.4, 40)  # Up to 40 points from setup quality
                    
                    # Confluence scoring
                    confluence_score = confluence.get('confluence_score', 0)
                    if confluence_score >= 80:
                        advanced_score += 20
                        enhanced_signals.append(f"Strong multi-timeframe confluence ({confluence_score}%)")
                    elif confluence_score >= 60:
                        advanced_score += 15
                        enhanced_signals.append(f"Good timeframe alignment ({confluence_score}%)")
                    elif confluence_score >= 40:
                        advanced_score += 10
                        enhanced_signals.append(f"Moderate timeframe alignment ({confluence_score}%)")
                    
                    # Volume profile analysis
                    volume_trend = volume_analysis.get('volume_trend', 'Normal')
                    if volume_trend == 'Above Average':
                        advanced_score += 15
                        enhanced_signals.append("Above average volume confirmation")
                    elif volume_trend == 'Normal':
                        advanced_score += 8
                    
                    # Pattern recognition
                    if patterns.get('double_bottom', False):
                        advanced_score += 20
                        enhanced_signals.append("Double bottom pattern detected")
                    
                    # Market structure
                    trend_structure = market_structure.get('trend_structure', '')
                    if 'Uptrend' in trend_structure:
                        advanced_score += 15
                        enhanced_signals.append("Strong uptrend structure (HH/HL)")
                    elif 'Sideways' in trend_structure:
                        advanced_score += 5
                        enhanced_signals.append("Consolidation pattern")
                    
                    # Divergence analysis
                    rsi_divergence = divergences.get('rsi_divergence', '')
                    if 'Bullish' in rsi_divergence:
                        advanced_score += 15
                        enhanced_signals.append("Bullish RSI divergence detected")
                    
                    # Store advanced analysis for detailed view
                    advanced_data = {
                        'setup_quality_score': setup_quality,
                        'confluence_data': confluence,
                        'volume_profile': volume_analysis,
                        'pattern_analysis': patterns,
                        'market_structure': market_structure,
                        'divergences': divergences,
                        'advanced_available': True
                    }
                    
                except Exception as e:
                    print(f"Advanced analysis failed for {symbol}: {e}")
                    advanced_data = {'advanced_available': False}
            else:
                advanced_data = {'advanced_available': False}
            
            # Basic swing trading score calculation
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
                    entry_type = "Support Bounce"
            
            if nearest_resistance:
                resistance_distance = ((nearest_resistance - current_price) / current_price) * 100
                if resistance_distance <= 3:  # Within 3% of resistance
                    score += 25
                    signals.append(f"Near resistance ({resistance_distance:.1f}%)")
                    if entry_type != "Support Bounce":
                        entry_type = "Resistance Break"
            
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
            
            # Add pullback entry detection
            if current_price < current_sma_20 and current_sma_20 > current_sma_50:
                if support_distance and support_distance <= 5:
                    score += 15
                    signals.append("Pullback to support in uptrend")
                    entry_type = "Pullback Entry"
            
            # Combine basic and advanced scores
            total_score = min(score + advanced_score, 100)  # Cap at 100
            
            # Combine signals
            all_signals = signals + enhanced_signals
            
            # Enhanced recommendation based on total score
            if total_score >= 80:
                recommendation = "STRONG BUY"
            elif total_score >= 65:
                recommendation = "BUY"  
            elif total_score >= 45:
                recommendation = "WATCH"
            elif total_score <= 25:
                recommendation = "AVOID"
            else:
                recommendation = "HOLD"
            
            # Risk/reward calculation with enhanced logic
            risk_reward = "N/A"
            risk_reward_ratio = 0
            if nearest_support and nearest_resistance:
                risk = current_price - nearest_support
                reward = nearest_resistance - current_price
                if risk > 0:
                    risk_reward_ratio = reward / risk
                    risk_reward = f"{risk_reward_ratio:.1f}:1"
                    
                    # Penalize poor R/R ratios
                    if risk_reward_ratio < 1.5:
                        total_score = max(0, total_score - 20)
                        all_signals.append(f"Poor R/R ratio ({risk_reward})")
                    elif risk_reward_ratio >= 2.0:
                        total_score = min(100, total_score + 10)
                        all_signals.append(f"Excellent R/R ratio ({risk_reward})")
            
            # Determine market name for currency symbol
            if '.NS' in symbol:
                market_name = "🇮🇳 India"
            elif '.KL' in symbol:
                market_name = "🇲🇾 Malaysia"
            else:
                market_name = "🇺🇸 USA"
            
            # Price change
            price_change_pct = ((current_price - close.iloc[-2]) / close.iloc[-2]) * 100 if len(close) > 1 else 0
            
            result = {
                'symbol': symbol,
                'current_price': current_price,
                'price_change_pct': price_change_pct,
                'swing_score': total_score,  # Now includes advanced analysis
                'recommendation': recommendation,
                'entry_type': entry_type,
                'signals': all_signals,
                'rsi': current_rsi,
                'volume_ratio': volume_ratio,
                'support_level': nearest_support,
                'resistance_level': nearest_resistance,
                'support_distance': support_distance,
                'resistance_distance': resistance_distance,
                'risk_reward': risk_reward,
                'risk_reward_ratio': risk_reward_ratio,
                'sma_20': current_sma_20,
                'sma_50': current_sma_50,
                'macd': current_macd,
                'macd_signal': current_macd_signal,
                'trend': "BULLISH" if current_sma_20 > current_sma_50 else "BEARISH",
                'market_name': market_name,
                
                # Enhanced data for detailed analysis
                'support_levels': self._get_multiple_support_levels(df, current_price),
                'resistance_levels': self._get_multiple_resistance_levels(df, current_price),
                'bollinger_bands': self._calculate_bollinger_bands(df['Close']),
                'stochastic': self._calculate_stochastic(df),
                'volume_trend': 'High' if volume_ratio > 1.5 else 'Normal' if volume_ratio > 0.8 else 'Low',
                'macd_signal_trend': 'Bullish' if current_macd > current_macd_signal else 'Bearish',
                'trend_strength': self._calculate_trend_strength(df['Close']),
                'volatility': self._calculate_volatility(df['Close']),
                'momentum': self._calculate_momentum_score(df['Close']),
                
                # Advanced analysis data
                'advanced_analysis': advanced_data
            }
            
            return result
            
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            return None
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
        """Scan for top swing opportunities using unified analysis"""
        if UNIFIED_ANALYSIS_AVAILABLE:
            print(f"🔍 Scanning {len(symbols)} stocks in {market_name} using unified analysis...")
            
            # Use unified analyzer for better results
            unified_results = self.unified_analyzer.scan_market_opportunities(symbols, market_name, limit)
            
            # Convert to dashboard format
            dashboard_results = []
            for result in unified_results:
                converted = self._convert_unified_to_dashboard_format(result)
                if converted:
                    dashboard_results.append(converted)
            
            print(f"✅ Found {len(dashboard_results)} high-quality opportunities in {market_name}")
            return dashboard_results
        else:
            # Fallback to basic scanning
            print(f"⚠️ Using basic scanning for {market_name} (unified analysis unavailable)")
            opportunities = []
            
            for symbol in symbols:
                analysis = self.calculate_swing_signals(symbol)
                if analysis and analysis['swing_score'] >= 70:
                    opportunities.append(analysis)
            
            opportunities.sort(key=lambda x: x['swing_score'], reverse=True)
            return opportunities[:limit]

def get_market_watchlists() -> Dict[str, List[str]]:
    """Get optimized watchlists for daily scanning - SMALL LIST for quick testing"""
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

def get_comprehensive_market_watchlists() -> Dict[str, List[str]]:
    """Get COMPREHENSIVE market watchlists with thousands of stocks for serious swing trading"""
    try:
        from .market_stock_lists import get_comprehensive_market_watchlists
        return get_comprehensive_market_watchlists(validate=False)
    except ImportError:
        print("⚠️ Comprehensive stock lists not available - using basic lists")
        return get_market_watchlists()

# For dashboard integration
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_daily_swing_signals(portfolio_manager=None) -> Dict:
    """Main function for dashboard integration with caching - BASIC SCAN (~73 stocks)"""
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

def get_ultra_fast_swing_signals(progress_callback=None, top_n: int = 15) -> Dict:
    """ULTRA-FAST market scan using optimized batch downloads (Streamlit Cloud compatible)"""
    
    print("⚡ ULTRA-FAST MARKET SCAN STARTING...")
    print("🎯 Using optimized batch downloads (Streamlit Cloud mode)")
    
    import time
    import warnings
    warnings.filterwarnings('ignore')
    
    def batch_download_data_simple(symbols: List[str], period: str = "1mo", batch_size: int = 20) -> Dict[str, pd.DataFrame]:
        """Simplified batch download for Streamlit Cloud compatibility"""
        all_data = {}
        
        # Split symbols into smaller batches for cloud compatibility
        for i in range(0, len(symbols), batch_size):
            batch_symbols = symbols[i:i + batch_size]
            
            try:
                # Use batch download
                batch_str = " ".join(batch_symbols)
                if progress_callback:
                    progress_callback(f"Downloading batch {i//batch_size + 1} ({len(batch_symbols)} stocks)", 
                                    i / len(symbols) * 0.3)  # First 30% for downloads
                
                data = yf.download(
                    batch_str, 
                    period=period, 
                    group_by='ticker',
                    threads=False,  # Disable threading for cloud compatibility
                    progress=False
                )
                
                # Extract individual DataFrames
                if len(batch_symbols) == 1:
                    # Single symbol case
                    if not data.empty:
                        all_data[batch_symbols[0]] = data
                else:
                    # Multiple symbols case
                    for symbol in batch_symbols:
                        try:
                            if hasattr(data.columns, 'levels') and symbol in data.columns.levels[0]:
                                symbol_data = data[symbol].dropna()
                                if not symbol_data.empty:
                                    all_data[symbol] = symbol_data
                        except (KeyError, AttributeError, IndexError):
                            # Symbol not found in batch
                            continue
                
                # Small delay between batches
                time.sleep(0.1)
                
            except Exception as e:
                print(f"❌ Batch download failed: {e}")
                # Fallback to individual downloads for this batch
                for symbol in batch_symbols:
                    try:
                        ticker = yf.Ticker(symbol)
                        symbol_data = ticker.history(period=period)
                        if not symbol_data.empty:
                            all_data[symbol] = symbol_data
                        time.sleep(0.05)  # Rate limiting
                    except Exception:
                        continue
        
        return all_data
    
    def calculate_quick_score(data: pd.DataFrame, symbol: str) -> Optional[Dict]:
        """Calculate a quick swing score without heavy analysis"""
        try:
            if data.empty or len(data) < 20:
                return None
            
            current_price = data['Close'].iloc[-1]
            
            # Quick technical indicators
            sma_20 = data['Close'].rolling(20).mean().iloc[-1]
            sma_50 = data['Close'].rolling(50).mean().iloc[-1] if len(data) >= 50 else sma_20
            
            # RSI calculation (simplified)
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
            
            # Volume analysis
            avg_volume = data['Volume'].rolling(20).mean().iloc[-1]
            current_volume = data['Volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            # Price momentum
            price_change_5d = (current_price / data['Close'].iloc[-6] - 1) * 100 if len(data) >= 6 else 0
            
            # Quick scoring algorithm
            score = 50  # Base score
            
            # Trend score
            if current_price > sma_20 > sma_50:
                score += 15  # Strong uptrend
            elif current_price > sma_20:
                score += 10  # Mild uptrend
            elif current_price < sma_20 < sma_50:
                score -= 15  # Strong downtrend
            
            # RSI score
            if 30 <= current_rsi <= 40:
                score += 15  # Oversold but recovering
            elif 40 <= current_rsi <= 60:
                score += 10  # Healthy range
            elif current_rsi > 80:
                score -= 10  # Overbought
            elif current_rsi < 20:
                score -= 5   # Extremely oversold
            
            # Volume score
            if volume_ratio > 2:
                score += 10  # High volume breakout
            elif volume_ratio > 1.5:
                score += 5   # Above average volume
            elif volume_ratio < 0.5:
                score -= 5   # Low volume concern
            
            # Momentum score
            if 2 <= price_change_5d <= 8:
                score += 10  # Good momentum
            elif price_change_5d > 15:
                score -= 5   # Too much too fast
            elif price_change_5d < -10:
                score -= 10  # Negative momentum
            
            # Determine recommendation
            if score >= 75:
                recommendation = "STRONG BUY"
                entry_type = "Breakout"
            elif score >= 65:
                recommendation = "BUY"
                entry_type = "Swing Entry"
            elif score >= 55:
                recommendation = "WEAK BUY"
                entry_type = "Watch List"
            elif score <= 35:
                recommendation = "AVOID"
                entry_type = "Bearish"
            else:
                recommendation = "HOLD"
                entry_type = "Neutral"
            
            market_name = "🇮🇳 India" if symbol.endswith('.NS') or symbol.endswith('.BO') else "🇲🇾 Malaysia" if symbol.endswith('.KL') else "🇺🇸 USA"
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'swing_score': max(0, min(100, score)),  # Clamp between 0-100
                'recommendation': recommendation,
                'entry_type': entry_type,
                'rsi': current_rsi,
                'volume_ratio': volume_ratio,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'price_change_5d': price_change_5d,
                'signals': [
                    f"RSI: {current_rsi:.1f}",
                    f"Volume: {volume_ratio:.1f}x avg",
                    f"5d change: {price_change_5d:.1f}%"
                ],
                'market_name': market_name
            }
            
        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {e}")
            return None
    
    
    def simple_analysis(symbol_data_pairs: List[Tuple[str, pd.DataFrame]], 
                       progress_callback=None) -> List[Dict]:
        """Analyze multiple symbols sequentially (Streamlit Cloud compatible)"""
        results = []
        total_pairs = len(symbol_data_pairs)
        
        for i, (symbol, data) in enumerate(symbol_data_pairs):
            try:
                result = calculate_quick_score(data, symbol)
                if result:
                    results.append(result)
                
                # Update progress
                if progress_callback and i % 5 == 0:
                    progress = (i + 1) / total_pairs
                    progress_callback(f"Analyzing: {symbol} ({i+1}/{total_pairs})", progress)
                    
            except Exception as e:
                print(f"❌ Analysis failed for {symbol}: {e}")
        
        return results
    
    # Get comprehensive stock lists
    try:
        watchlists = get_comprehensive_market_watchlists()
    except:
        watchlists = get_market_watchlists()
        print("⚠️ Using basic stock lists")
    
    total_stocks = sum(len(symbols) for symbols in watchlists.values())
    start_time = time.time()
    
    results = {
        'timestamp': datetime.now(),
        'scan_type': 'ULTRA_FAST',
        'markets': {},
        'total_stocks_scanned': total_stocks,
        'scan_duration': None
    }
    
    scanned_count = 0
    
    for market, symbols in watchlists.items():
        market_name = "🇺🇸 USA" if market == 'usa' else "🇮🇳 India" if market == 'india' else "🇲🇾 Malaysia"
        
        print(f"⚡ Fast scanning {market_name} - {len(symbols)} symbols")
        market_start = time.time()
        
        # Update progress callback for market start
        if progress_callback:
            overall_progress = scanned_count / total_stocks
            progress_callback(f"Starting {market_name} scan ({len(symbols)} stocks)", overall_progress)
        
        # Step 1: Batch download all data
        all_data = batch_download_data_simple(symbols, period="1mo", batch_size=20)
        download_time = time.time() - market_start
        
        print(f"📦 Downloaded {len(all_data)}/{len(symbols)} symbols in {download_time:.1f}s")
        
        # Step 2: Simple analysis
        if progress_callback:
            progress_callback(f"Analyzing {market_name} symbols...", (scanned_count + 0.3 * len(symbols)) / total_stocks)
        
        symbol_data_pairs = list(all_data.items())
        analysis_start = time.time()
        
        market_results = simple_analysis(
            symbol_data_pairs, 
            progress_callback=lambda msg, prog: progress_callback(
                f"{market_name}: {msg}", 
                (scanned_count + 0.3 * len(symbols) + prog * 0.7 * len(symbols)) / total_stocks
            ) if progress_callback else None
        )
        
        analysis_time = time.time() - analysis_start
        
        # Step 3: Sort and filter results
        market_results.sort(key=lambda x: x.get('swing_score', 0), reverse=True)
        top_opportunities = market_results[:top_n]
        
        total_time = time.time() - market_start
        scanned_count += len(symbols)
        
        results['markets'][market] = {
            'name': market_name,
            'opportunities': top_opportunities,
            'total_scanned': len(symbols),
            'total_downloaded': len(all_data),
            'opportunities_found': len(market_results),
            'top_displayed': len(top_opportunities),
            'download_time': download_time,
            'analysis_time': analysis_time,
            'total_time': total_time,
            'avg_time_per_stock': total_time / len(symbols) if symbols else 0
        }
        
        print(f"✅ {market_name}: {len(market_results)} opportunities in {total_time:.1f}s")
    
    total_duration = time.time() - start_time
    results['scan_duration'] = total_duration
    
    # Summary
    total_opportunities = sum(len(market['opportunities']) for market in results['markets'].values())
    
    print(f"""
⚡ ULTRA-FAST SCAN COMPLETE!
⏱️ Total time: {total_duration:.1f} seconds ({total_duration/60:.1f} minutes)
📊 Stocks scanned: {total_stocks}
🎯 Opportunities found: {total_opportunities}
⚡ Speed: {total_stocks/total_duration:.1f} stocks per second
🚀 Performance: {total_duration/60:.1f} minutes for {total_stocks} stocks!
    """)
    
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
