#!/usr/bin/env python3
"""
Unified Swing Trading Analysis System
Combines all analysis methods into one coherent scoring and recommendation system
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
from typing import Dict, List, Optional, Tuple
warnings.filterwarnings('ignore')

# Import all analysis modules
try:
    from .advanced_technical_analysis import AdvancedTechnicalAnalysis
    from .market_context_analyzer import MarketContextAnalyzer
    ADVANCED_AVAILABLE = True
except ImportError:
    ADVANCED_AVAILABLE = False

class UnifiedSwingAnalyzer:
    """
    Unified analyzer that combines all technical, advanced, and market analysis
    into one coherent scoring system for reliable swing trading signals
    """
    
    def __init__(self):
        self.minimum_score = 70  # Only show high-quality opportunities
        self.risk_reward_minimum = 1.5  # Minimum R/R ratio
        
    def comprehensive_analysis(self, symbol: str, period: str = "3mo") -> Optional[Dict]:
        """
        Unified comprehensive analysis combining all methods
        Returns a single coherent score and recommendation
        """
        try:
            # Get basic market data
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval="1d")
            
            if df.empty or len(df) < 30:
                return None
            
            current_price = df['Close'].iloc[-1]
            
            # Initialize scoring components
            analysis_result = {
                'symbol': symbol,
                'current_price': current_price,
                'analysis_timestamp': datetime.now().strftime('%H:%M:%S'),
                'market_name': self._get_market_name(symbol),
                
                # Scoring breakdown
                'technical_score': 0,      # Max 40 points
                'advanced_score': 0,       # Max 30 points  
                'market_context_score': 0, # Max 20 points
                'risk_management_score': 0,# Max 10 points
                'total_score': 0,          # Max 100 points
                
                # Analysis details
                'technical_analysis': {},
                'advanced_analysis': {},
                'market_context': {},
                'risk_analysis': {},
                
                # Final recommendation
                'recommendation': 'AVOID',
                'confidence': 'Low',
                'entry_rationale': [],
                'risk_factors': [],
                'opportunity_type': 'NONE'
            }
            
            # 1. Technical Analysis (40 points max)
            technical_result = self._analyze_technical_indicators(df)
            analysis_result['technical_score'] = technical_result['score']
            analysis_result['technical_analysis'] = technical_result['details']
            
            # 2. Advanced Analysis (30 points max) - only if available
            if ADVANCED_AVAILABLE:
                advanced_result = self._analyze_advanced_features(symbol, current_price)
                analysis_result['advanced_score'] = advanced_result['score']
                analysis_result['advanced_analysis'] = advanced_result['details']
            
            # 3. Market Context Analysis (20 points max)
            if ADVANCED_AVAILABLE:
                context_result = self._analyze_market_context(symbol)
                analysis_result['market_context_score'] = context_result['score']
                analysis_result['market_context'] = context_result['details']
            
            # 4. Risk Management Analysis (10 points max)
            risk_result = self._analyze_risk_management(df, analysis_result['technical_analysis'])
            analysis_result['risk_management_score'] = risk_result['score']
            analysis_result['risk_analysis'] = risk_result['details']
            
            # Calculate total score
            analysis_result['total_score'] = (
                analysis_result['technical_score'] + 
                analysis_result['advanced_score'] + 
                analysis_result['market_context_score'] + 
                analysis_result['risk_management_score']
            )
            
            # Generate unified recommendation
            final_result = self._generate_unified_recommendation(analysis_result)
            
            return final_result
            
        except Exception as e:
            print(f"Error in unified analysis for {symbol}: {e}")
            return None
    
    def _analyze_technical_indicators(self, df: pd.DataFrame) -> Dict:
        """Technical analysis scoring (40 points max)"""
        score = 0
        details = {}
        
        close = df['Close']
        high = df['High']
        low = df['Low']
        volume = df['Volume']
        current_price = close.iloc[-1]
        
        # RSI Analysis (10 points max)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        if 30 <= current_rsi <= 45:  # Oversold recovery
            score += 10
            details['rsi_signal'] = f"Strong oversold recovery ({current_rsi:.1f})"
        elif 45 <= current_rsi <= 60:  # Healthy momentum
            score += 7
            details['rsi_signal'] = f"Healthy momentum ({current_rsi:.1f})"
        elif 60 <= current_rsi <= 70:  # Strong momentum
            score += 5
            details['rsi_signal'] = f"Strong momentum ({current_rsi:.1f})"
        else:
            details['rsi_signal'] = f"RSI neutral/unfavorable ({current_rsi:.1f})"
        
        details['rsi'] = current_rsi
        
        # Moving Average Analysis (10 points max)
        sma_20 = close.rolling(window=20).mean()
        sma_50 = close.rolling(window=50).mean()
        current_sma_20 = sma_20.iloc[-1]
        current_sma_50 = sma_50.iloc[-1]
        
        if current_price > current_sma_20 > current_sma_50:  # Strong uptrend
            score += 10
            details['ma_signal'] = "Strong uptrend (Price > MA20 > MA50)"
        elif current_sma_20 > current_sma_50:  # Bullish alignment
            score += 6
            details['ma_signal'] = "Bullish MA alignment"
        elif current_price > current_sma_20:  # Above short-term MA
            score += 3
            details['ma_signal'] = "Above short-term MA"
        else:
            details['ma_signal'] = "Below moving averages"
        
        details['sma_20'] = current_sma_20
        details['sma_50'] = current_sma_50
        
        # Support/Resistance Analysis (15 points max)
        support_resistance = self._calculate_support_resistance(df, current_price)
        nearest_support = support_resistance['nearest_support']
        nearest_resistance = support_resistance['nearest_resistance']
        
        support_distance = None
        resistance_distance = None
        
        if nearest_support:
            support_distance = ((current_price - nearest_support) / current_price) * 100
            if support_distance <= 2:  # Very close to support
                score += 15
                details['support_signal'] = f"Excellent support bounce setup ({support_distance:.1f}%)"
            elif support_distance <= 4:  # Close to support
                score += 10
                details['support_signal'] = f"Good support level ({support_distance:.1f}%)"
            elif support_distance <= 8:  # Reasonable support
                score += 5
                details['support_signal'] = f"Moderate support level ({support_distance:.1f}%)"
        
        details['support_level'] = nearest_support
        details['resistance_level'] = nearest_resistance
        details['support_distance'] = support_distance
        details['resistance_distance'] = resistance_distance
        
        # Volume Confirmation (5 points max)
        volume_ma = volume.rolling(window=20).mean()
        volume_ratio = volume.iloc[-1] / volume_ma.iloc[-1] if volume_ma.iloc[-1] > 0 else 1
        
        if volume_ratio > 1.5:
            score += 5
            details['volume_signal'] = f"Strong volume confirmation ({volume_ratio:.1f}x)"
        elif volume_ratio > 1.2:
            score += 3
            details['volume_signal'] = f"Good volume ({volume_ratio:.1f}x)"
        else:
            details['volume_signal'] = f"Normal volume ({volume_ratio:.1f}x)"
        
        details['volume_ratio'] = volume_ratio
        
        return {'score': min(score, 40), 'details': details}
    
    def _analyze_advanced_features(self, symbol: str, current_price: float) -> Dict:
        """Advanced technical analysis (30 points max)"""
        score = 0
        details = {}
        
        try:
            advanced_analyzer = AdvancedTechnicalAnalysis(symbol)
            advanced_analysis = advanced_analyzer.comprehensive_entry_analysis(current_price)
            
            # Setup Quality (15 points max)
            setup_quality = advanced_analysis.get('setup_quality_score', 0)
            quality_score = min(setup_quality * 0.15, 15)  # Convert to 15-point scale
            score += quality_score
            details['setup_quality'] = setup_quality
            
            if setup_quality >= 70:
                details['setup_signal'] = f"Excellent setup quality ({setup_quality}/100)"
            elif setup_quality >= 50:
                details['setup_signal'] = f"Good setup quality ({setup_quality}/100)"
            else:
                details['setup_signal'] = f"Poor setup quality ({setup_quality}/100)"
            
            # Timeframe Confluence (10 points max)
            confluence = advanced_analysis.get('timeframe_confluence', {})
            confluence_score = confluence.get('confluence_score', 0)
            
            if confluence_score >= 80:
                score += 10
                details['confluence_signal'] = f"Strong multi-timeframe alignment ({confluence_score}%)"
            elif confluence_score >= 60:
                score += 7
                details['confluence_signal'] = f"Good timeframe alignment ({confluence_score}%)"
            elif confluence_score >= 40:
                score += 4
                details['confluence_signal'] = f"Moderate alignment ({confluence_score}%)"
            else:
                details['confluence_signal'] = f"Poor timeframe alignment ({confluence_score}%)"
            
            # Pattern Recognition (5 points max)
            patterns = advanced_analysis.get('pattern_analysis', {})
            if patterns.get('double_bottom', False):
                score += 5
                details['pattern_signal'] = "Double bottom pattern detected"
            elif patterns.get('support_retest', False):
                score += 3
                details['pattern_signal'] = "Support retest pattern"
            else:
                details['pattern_signal'] = "No significant patterns"
            
            details['advanced_data'] = advanced_analysis
            
        except Exception as e:
            details['error'] = f"Advanced analysis failed: {e}"
            details['setup_signal'] = "Advanced analysis unavailable"
        
        return {'score': min(score, 30), 'details': details}
    
    def _analyze_market_context(self, symbol: str) -> Dict:
        """Market context analysis (20 points max)"""
        score = 0
        details = {}
        
        try:
            market_analyzer = MarketContextAnalyzer()
            market_context = market_analyzer.comprehensive_market_analysis(symbol)
            
            # Market sentiment (10 points max)
            sentiment = market_context.get('overall_sentiment', 'Neutral')
            if sentiment == 'Bullish':
                score += 10
                details['sentiment_signal'] = "Bullish market sentiment"
            elif sentiment == 'Neutral':
                score += 5
                details['sentiment_signal'] = "Neutral market sentiment"
            else:
                details['sentiment_signal'] = "Bearish market sentiment"
            
            # Sector performance (10 points max)
            sector_data = market_context.get('sector_analysis', {})
            relative_strength = sector_data.get('relative_strength', 0)
            
            if relative_strength > 2:
                score += 10
                details['sector_signal'] = f"Strong sector outperformance (+{relative_strength:.1f}%)"
            elif relative_strength > 0:
                score += 6
                details['sector_signal'] = f"Sector outperforming (+{relative_strength:.1f}%)"
            elif relative_strength > -2:
                score += 3
                details['sector_signal'] = f"Sector performing in-line ({relative_strength:.1f}%)"
            else:
                details['sector_signal'] = f"Sector underperforming ({relative_strength:.1f}%)"
            
            details['market_data'] = market_context
            
        except Exception as e:
            details['error'] = f"Market context analysis failed: {e}"
            details['sentiment_signal'] = "Market context unavailable"
            details['sector_signal'] = "Sector analysis unavailable"
        
        return {'score': min(score, 20), 'details': details}
    
    def _analyze_risk_management(self, df: pd.DataFrame, technical_details: Dict) -> Dict:
        """Risk management analysis (10 points max)"""
        score = 0
        details = {}
        
        current_price = df['Close'].iloc[-1]
        
        # Risk/Reward calculation
        support_level = technical_details.get('support_level')
        resistance_level = technical_details.get('resistance_level')
        
        if support_level and resistance_level:
            risk = current_price - support_level
            reward = resistance_level - current_price
            
            if risk > 0:
                rr_ratio = reward / risk
                details['risk_reward_ratio'] = rr_ratio
                
                if rr_ratio >= 3.0:
                    score += 10
                    details['rr_signal'] = f"Excellent R/R ratio ({rr_ratio:.1f}:1)"
                elif rr_ratio >= 2.0:
                    score += 8
                    details['rr_signal'] = f"Good R/R ratio ({rr_ratio:.1f}:1)"
                elif rr_ratio >= 1.5:
                    score += 5
                    details['rr_signal'] = f"Acceptable R/R ratio ({rr_ratio:.1f}:1)"
                else:
                    score = 0  # Poor R/R kills the setup
                    details['rr_signal'] = f"Poor R/R ratio ({rr_ratio:.1f}:1) - SETUP REJECTED"
            else:
                details['rr_signal'] = "Cannot calculate R/R - insufficient data"
        else:
            details['rr_signal'] = "Support/resistance levels unclear"
        
        # Volatility check
        returns = df['Close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252) * 100  # Annualized volatility
        details['volatility'] = volatility
        
        if volatility > 50:
            score = max(0, score - 3)  # Penalize high volatility
            details['volatility_signal'] = f"High volatility ({volatility:.1f}%) - increased risk"
        elif volatility < 15:
            details['volatility_signal'] = f"Low volatility ({volatility:.1f}%) - stable"
        else:
            details['volatility_signal'] = f"Normal volatility ({volatility:.1f}%)"
        
        return {'score': min(score, 10), 'details': details}
    
    def _generate_unified_recommendation(self, analysis: Dict) -> Dict:
        """Generate final unified recommendation based on all analysis"""
        
        total_score = analysis['total_score']
        technical_score = analysis['technical_score']
        risk_score = analysis['risk_management_score']
        
        # Critical filters - must pass these to be recommended
        critical_failures = []
        
        # 1. Minimum technical score (at least 20/40)
        if technical_score < 20:
            critical_failures.append("Poor technical setup")
        
        # 2. Risk management must be acceptable (at least 5/10)
        if risk_score < 5:
            critical_failures.append("Poor risk/reward profile")
        
        # 3. Minimum total score
        if total_score < self.minimum_score:
            critical_failures.append(f"Score below threshold ({total_score}/{self.minimum_score})")
        
        # Generate recommendation
        if critical_failures:
            analysis['recommendation'] = 'AVOID'
            analysis['confidence'] = 'High'
            analysis['entry_rationale'] = ['Setup fails critical requirements']
            analysis['risk_factors'] = critical_failures
            analysis['opportunity_type'] = 'POOR_QUALITY'
        else:
            # High-quality setup
            if total_score >= 85:
                analysis['recommendation'] = 'STRONG BUY'
                analysis['confidence'] = 'High'
                analysis['opportunity_type'] = 'PREMIUM'
            elif total_score >= 75:
                analysis['recommendation'] = 'BUY'
                analysis['confidence'] = 'High'
                analysis['opportunity_type'] = 'QUALITY'
            else:  # 70-74 range
                analysis['recommendation'] = 'BUY'
                analysis['confidence'] = 'Medium'
                analysis['opportunity_type'] = 'STANDARD'
            
            # Build entry rationale
            rationale = []
            if analysis['technical_score'] >= 30:
                rationale.append("Strong technical setup")
            if analysis['advanced_score'] >= 20:
                rationale.append("Advanced patterns confirm")
            if analysis['market_context_score'] >= 15:
                rationale.append("Favorable market context")
            if analysis['risk_management_score'] >= 8:
                rationale.append("Excellent risk/reward")
            
            analysis['entry_rationale'] = rationale
            
            # Identify remaining risk factors
            risk_factors = []
            if analysis['technical_score'] < 30:
                risk_factors.append("Moderate technical setup")
            if analysis['advanced_score'] < 15:
                risk_factors.append("Limited pattern confirmation")
            if analysis['market_context_score'] < 10:
                risk_factors.append("Neutral market conditions")
            
            analysis['risk_factors'] = risk_factors
        
        # Add price change
        analysis['price_change_pct'] = 0  # Will be calculated if historical data available
        
        # Add formatted display data
        analysis['swing_score'] = total_score
        analysis['signals'] = analysis['entry_rationale'] + analysis['risk_factors']
        
        return analysis
    
    def _calculate_support_resistance(self, df: pd.DataFrame, current_price: float) -> Dict:
        """Calculate support and resistance levels"""
        if len(df) < 20:
            return {'nearest_support': None, 'nearest_resistance': None}
        
        # Find pivot points
        highs = df['High']
        lows = df['Low']
        
        # Rolling window for pivot detection
        window = min(10, len(df) // 4)
        
        resistance_levels = []
        support_levels = []
        
        # Find resistance levels (pivot highs above current price)
        for i in range(window, len(df) - window):
            if (highs.iloc[i] == highs.iloc[i-window:i+window+1].max() and 
                highs.iloc[i] > current_price):
                resistance_levels.append(highs.iloc[i])
        
        # Find support levels (pivot lows below current price)
        for i in range(window, len(df) - window):
            if (lows.iloc[i] == lows.iloc[i-window:i+window+1].min() and 
                lows.iloc[i] < current_price):
                support_levels.append(lows.iloc[i])
        
        # Find nearest levels
        nearest_support = max(support_levels) if support_levels else None
        nearest_resistance = min(resistance_levels) if resistance_levels else None
        
        return {
            'nearest_support': nearest_support,
            'nearest_resistance': nearest_resistance,
            'all_support': support_levels,
            'all_resistance': resistance_levels
        }
    
    def _get_market_name(self, symbol: str) -> str:
        """Determine market name from symbol"""
        if '.NS' in symbol:
            return "🇮🇳 India"
        elif '.KL' in symbol:
            return "🇲🇾 Malaysia"
        else:
            return "🇺🇸 USA"
    
    def scan_market_opportunities(self, symbols: List[str], market_name: str, limit: int = 5) -> List[Dict]:
        """Scan for high-quality opportunities using unified analysis"""
        opportunities = []
        
        print(f"Scanning {len(symbols)} stocks in {market_name}...")
        
        for i, symbol in enumerate(symbols):
            print(f"  Analyzing {symbol} ({i+1}/{len(symbols)})")
            
            analysis = self.comprehensive_analysis(symbol)
            if analysis and analysis['recommendation'] in ['BUY', 'STRONG BUY']:
                opportunities.append(analysis)
        
        # Sort by total score
        opportunities.sort(key=lambda x: x['total_score'], reverse=True)
        
        print(f"Found {len(opportunities)} quality opportunities in {market_name}")
        return opportunities[:limit]

# For backward compatibility with dashboard
class EnhancedSwingAnalyzer:
    """Wrapper class for backward compatibility"""
    
    def __init__(self):
        self.unified_analyzer = UnifiedSwingAnalyzer()
    
    def calculate_swing_signals(self, symbol: str, period: str = "3mo") -> Optional[Dict]:
        """Calculate swing signals using unified analysis"""
        result = self.unified_analyzer.comprehensive_analysis(symbol, period)
        
        if not result:
            return None
        
        # Convert to dashboard-compatible format
        converted = {
            'symbol': result['symbol'],
            'current_price': result['current_price'],
            'swing_score': result['total_score'],
            'recommendation': result['recommendation'],
            'entry_type': result['opportunity_type'],
            'signals': result['signals'],
            'market_name': result['market_name'],
            
            # Technical details
            'rsi': result['technical_analysis'].get('rsi', 0),
            'volume_ratio': result['technical_analysis'].get('volume_ratio', 1),
            'support_level': result['technical_analysis'].get('support_level'),
            'resistance_level': result['technical_analysis'].get('resistance_level'),
            'support_distance': result['technical_analysis'].get('support_distance'),
            'resistance_distance': result['technical_analysis'].get('resistance_distance'),
            'risk_reward': f"{result['risk_analysis'].get('risk_reward_ratio', 0):.1f}:1",
            'risk_reward_ratio': result['risk_analysis'].get('risk_reward_ratio', 0),
            
            # Moving averages
            'sma_20': result['technical_analysis'].get('sma_20'),
            'sma_50': result['technical_analysis'].get('sma_50'),
            'trend': "BULLISH" if result['technical_analysis'].get('sma_20', 0) > result['technical_analysis'].get('sma_50', 0) else "BEARISH",
            
            # Additional data for dashboard compatibility
            'price_change_pct': result.get('price_change_pct', 0),
            'macd': 0,
            'macd_signal': 0,
            'volume_trend': 'High' if result['technical_analysis'].get('volume_ratio', 1) > 1.5 else 'Normal',
            'macd_signal_trend': 'Neutral',
            
            # Enhanced data
            'advanced_analysis': {
                'advanced_available': ADVANCED_AVAILABLE,
                'unified_analysis': result
            }
        }
        
        return converted
    
    def scan_top_opportunities(self, symbols: List[str], market_name: str, limit: int = 5) -> List[Dict]:
        """Scan using unified analyzer"""
        unified_results = self.unified_analyzer.scan_market_opportunities(symbols, market_name, limit)
        
        # Convert to dashboard format
        converted_results = []
        for result in unified_results:
            converted = self.calculate_swing_signals(result['symbol'])
            if converted:
                converted_results.append(converted)
        
        return converted_results
