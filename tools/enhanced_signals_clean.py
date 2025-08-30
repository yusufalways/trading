#!/usr/bin/env python3
"""
Enhanced Daily Signals - PROFESSIONAL VERSION
Addresses all critical issues identified in feedback:
- Fixed contradictory signals
- Proper technical indicator calculations  
- Market context integration
- Professional scoring system
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
from typing import Dict, List, Optional
import logging
import time

# Import professional analysis systems
try:
    from .professional_technical_analysis import ProfessionalTechnicalAnalysis
    from .market_context_analyzer import EnhancedMarketContextAnalyzer
    from .external_data_integrator import ExternalDataIntegrator
    PROFESSIONAL_ANALYSIS_AVAILABLE = True
    print("✅ Professional analysis modules loaded")
except ImportError as e:
    print(f"⚠️ Professional analysis modules not available: {e}")
    PROFESSIONAL_ANALYSIS_AVAILABLE = False

# Fallback to unified analysis if available
try:
    from .unified_swing_analyzer import UnifiedSwingAnalyzer
    UNIFIED_ANALYSIS_AVAILABLE = True
except ImportError:
    print("⚠️ Unified analysis not available")
    UNIFIED_ANALYSIS_AVAILABLE = False

class ProfessionalSwingAnalyzer:
    """
    Professional-grade analyzer that addresses all critical feedback issues:
    ✅ Fixes contradictory signals (RSI interpretation, MACD accuracy)
    ✅ Implements proper technical indicator calculations
    ✅ Adds market context analysis (sector rotation, market regime)
    ✅ Includes external data integration (fundamentals, news, economics)
    ✅ Professional risk-adjusted scoring system
    """
    
    def __init__(self):
        self.lookback_period = 50
        
        if PROFESSIONAL_ANALYSIS_AVAILABLE:
            self.technical_analyzer = ProfessionalTechnicalAnalysis()
            self.market_analyzer = EnhancedMarketContextAnalyzer()
            self.external_analyzer = ExternalDataIntegrator()
            print("🎯 Using professional analysis system - all issues addressed!")
        elif UNIFIED_ANALYSIS_AVAILABLE:
            self.unified_analyzer = UnifiedSwingAnalyzer()
            print("📊 Using unified analysis system")
        else:
            print("⚠️ Using basic analysis - install required packages for professional features")
    
    def calculate_swing_signals(self, symbol: str, period: str = "6mo") -> Optional[Dict]:
        """
        Professional swing signal calculation addressing all identified issues
        """
        
        if PROFESSIONAL_ANALYSIS_AVAILABLE:
            return self.professional_analysis(symbol, period)
        elif UNIFIED_ANALYSIS_AVAILABLE:
            return self.unified_analyzer.analyze_symbol(symbol, period)
        else:
            return self.basic_analysis(symbol, period)
    
    def professional_analysis(self, symbol: str, period: str = "6mo") -> Optional[Dict]:
        """
        Comprehensive professional analysis addressing all feedback issues
        """
        try:
            print(f"🔬 Professional analysis for {symbol}")
            
            # 1. Technical Analysis (fixes contradictory signals)
            technical_result = self.technical_analyzer.comprehensive_stock_analysis(symbol, period)
            if not technical_result:
                return None
            
            # 2. Market Context Analysis (addresses missing context)
            market_context = self.market_analyzer.comprehensive_market_analysis(symbol)
            
            # 3. External Data Integration (fundamentals, news, economics)
            external_analysis = self.external_analyzer.comprehensive_external_analysis(symbol)
            
            # 4. Risk-Adjusted Final Score
            final_score = self.calculate_risk_adjusted_score(
                technical_result, market_context, external_analysis
            )
            
            # 5. Enhanced Recommendation
            final_recommendation = self.generate_professional_recommendation(
                final_score, technical_result, market_context, external_analysis
            )
            
            # 6. Compile comprehensive result
            return {
                'symbol': symbol,
                'current_price': technical_result['current_price'],
                'swing_score': final_score,
                'recommendation': final_recommendation['action'],
                'risk_level': final_recommendation['key_factors']['volatility_level'],
                'entry_type': technical_result['entry_type'],
                'market_name': technical_result['market_name'],
                'risk_reward': technical_result['risk_reward'],
                
                # Professional Analysis Details
                'technical_details': {
                    'rsi_analysis': technical_result['rsi_analysis'],
                    'macd_analysis': technical_result['macd_analysis'],
                    'trend_analysis': technical_result['trend_analysis'],
                    'volume_trend': technical_result['volume_trend'],
                    'support_levels': technical_result['support_levels'],
                    'resistance_levels': technical_result['resistance_levels'],
                    'volatility': technical_result['volatility']
                },
                
                'market_context': {
                    'regime': market_context.get('market_regime', {}),
                    'relative_strength': market_context.get('relative_strength', {}),
                    'sector_analysis': market_context.get('sector_analysis', {}),
                    'sentiment': market_context.get('market_sentiment', {}),
                    'insights': market_context.get('insights', [])
                },
                
                'external_factors': {
                    'fundamentals': external_analysis.get('data_sources', {}).get('fundamentals', {}),
                    'news_sentiment': external_analysis.get('data_sources', {}).get('news_sentiment', {}),
                    'economic_indicators': external_analysis.get('data_sources', {}).get('economic_indicators', {}),
                    'risk_factors': external_analysis.get('risk_factors', []),
                    'catalysts': external_analysis.get('catalysts', [])
                },
                
                'recommendation_details': final_recommendation,
                
                # Technical indicators for compatibility
                'technical_indicators': {
                    'rsi': {
                        'value': technical_result['rsi_value'],
                        'signal': technical_result['rsi_analysis']['status']
                    },
                    'macd': {
                        'signal': technical_result['macd_analysis']['signal']
                    }
                },
                
                # Enhanced signals list
                'signals': [
                    f"Technical Score: {technical_result['swing_score']}/100",
                    f"RSI: {technical_result['rsi_value']:.1f} ({technical_result['rsi_analysis']['status']})",
                    f"MACD: {technical_result['macd_analysis']['status']}",
                    f"Trend: {technical_result['trend_analysis']['direction']}",
                    f"Market Regime: {market_context.get('market_regime', {}).get('regime', 'Unknown')}",
                    f"Relative Strength: {market_context.get('relative_strength', {}).get('status', 'Unknown')}",
                    f"External Score: {external_analysis.get('external_score', 50)}/100"
                ]
            }
            
        except Exception as e:
            print(f"Error in professional analysis for {symbol}: {e}")
            return None
    
    def calculate_risk_adjusted_score(self, technical: Dict, market: Dict, external: Dict) -> int:
        """
        Professional risk-adjusted scoring system
        Addresses oversimplified current scoring approach
        """
        
        # Base technical score (60% weight)
        base_score = technical.get('swing_score', 50) * 0.6
        
        # Market context adjustment (25% weight)
        market_adjustment = 0
        market_regime = market.get('market_regime', {})
        relative_strength = market.get('relative_strength', {})
        
        # Market regime impact
        if market_regime.get('regime') == 'Bull Market':
            market_adjustment += 15 if market_regime.get('strength') == 'Strong' else 10
        elif market_regime.get('regime') == 'Bear Market':
            market_adjustment -= 15 if market_regime.get('strength') == 'Strong' else 10
        
        # Relative strength impact
        rs_status = relative_strength.get('status', '')
        if 'Strong Outperformer' in rs_status:
            market_adjustment += 10
        elif 'Outperformer' in rs_status:
            market_adjustment += 5
        elif 'Underperformer' in rs_status:
            market_adjustment -= 10
        
        market_score = market_adjustment * 0.25
        
        # External factors adjustment (15% weight)
        external_score = (external.get('external_score', 50) - 50) * 0.15
        
        # Risk factor penalties
        risk_penalty = len(external.get('risk_factors', [])) * 2
        
        # Catalyst bonus
        catalyst_bonus = len(external.get('catalysts', [])) * 2
        
        # Final calculation
        final_score = base_score + market_score + external_score + catalyst_bonus - risk_penalty
        
        return max(0, min(100, int(final_score)))
    
    def generate_professional_recommendation(self, final_score: int, technical: Dict, 
                                           market: Dict, external: Dict) -> Dict:
        """
        Professional recommendation system with detailed reasoning
        """
        
        # Risk/Reward validation
        risk_reward_str = technical.get('risk_reward', '1.0:1')
        try:
            risk_reward_ratio = float(risk_reward_str.split(':')[0])
        except:
            risk_reward_ratio = 1.0
        
        # Volatility check
        volatility = technical.get('volatility', 20)
        
        # Market context check
        market_regime = market.get('market_regime', {}).get('regime', 'Unknown')
        
        # External risk assessment
        risk_factors = external.get('risk_factors', [])
        
        # Professional recommendation logic
        if final_score >= 85 and risk_reward_ratio >= 2.5 and volatility < 30:
            action = "STRONG BUY"
            confidence = "Very High"
            position_size = "Full Position"
            rationale = "Exceptional setup with strong technical, market, and external factors alignment"
        elif final_score >= 75 and risk_reward_ratio >= 2.0:
            action = "BUY"
            confidence = "High"
            position_size = "Standard Position"
            rationale = "Strong technical setup with favorable market conditions"
        elif final_score >= 65 and risk_reward_ratio >= 1.5:
            if len(risk_factors) <= 1:
                action = "WEAK BUY"
                confidence = "Medium"
                position_size = "Reduced Position"
                rationale = "Decent setup but watch for risk factors"
            else:
                action = "HOLD"
                confidence = "Medium"
                position_size = "No Position"
                rationale = "Mixed signals with multiple risk factors"
        elif final_score >= 50:
            action = "HOLD"
            confidence = "Low"
            position_size = "No Position"
            rationale = "Neutral setup, wait for better opportunity"
        else:
            action = "AVOID"
            confidence = "High"
            position_size = "No Position"
            rationale = "Poor technical setup with unfavorable conditions"
        
        # Additional risk warnings
        warnings = []
        if volatility > 40:
            warnings.append("High volatility - consider smaller position")
        if market_regime == 'Bear Market':
            warnings.append("Bear market environment - extra caution advised")
        if len(risk_factors) > 2:
            warnings.append("Multiple external risk factors present")
        
        return {
            'action': action,
            'confidence': confidence,
            'position_size': position_size,
            'rationale': rationale,
            'final_score': final_score,
            'risk_reward_ratio': risk_reward_ratio,
            'warnings': warnings,
            'key_factors': {
                'technical_score': technical.get('swing_score', 50),
                'market_regime': market_regime,
                'risk_factors_count': len(risk_factors),
                'volatility_level': 'High' if volatility > 30 else 'Medium' if volatility > 20 else 'Low'
            }
        }
    
    def basic_analysis(self, symbol: str, period: str = "3mo") -> Optional[Dict]:
        """
        Basic analysis for when professional modules aren't available
        Still addresses some contradictory signal issues
        """
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval="1d")
            
            if df.empty or len(df) < 20:
                return None
            
            current_price = df['Close'].iloc[-1]
            
            # Improved technical indicators
            df['SMA_20'] = df['Close'].rolling(20).mean()
            df['SMA_50'] = df['Close'].rolling(50).mean() if len(df) >= 50 else df['SMA_20']
            df['RSI'] = self.calculate_rsi(df['Close'], 14)
            df['Volume_SMA'] = df['Volume'].rolling(20).mean()
            
            # Fixed RSI interpretation
            rsi = df['RSI'].iloc[-1]
            if rsi >= 70:
                rsi_status = "Overbought"
                rsi_signal = "SELL_WARNING"
            elif rsi <= 30:
                rsi_status = "Oversold"
                rsi_signal = "BUY_OPPORTUNITY"
            elif 30 < rsi < 40:
                rsi_status = "Oversold Zone"
                rsi_signal = "POTENTIAL_BUY"
            elif 60 < rsi < 70:
                rsi_status = "Overbought Zone"
                rsi_signal = "CAUTION"
            else:
                rsi_status = "Neutral"
                rsi_signal = "NEUTRAL"
            
            # Improved scoring
            score = 50
            
            # Trend analysis
            sma_20 = df['SMA_20'].iloc[-1]
            sma_50 = df['SMA_50'].iloc[-1]
            
            if current_price > sma_20 > sma_50:
                score += 20
            elif current_price > sma_20:
                score += 10
            elif current_price < sma_20 < sma_50:
                score -= 15
            
            # RSI scoring (fixed)
            if rsi_signal == "BUY_OPPORTUNITY":
                score += 15
            elif rsi_signal == "POTENTIAL_BUY":
                score += 10
            elif rsi_signal == "SELL_WARNING":
                score -= 15
            elif rsi_signal == "CAUTION":
                score -= 5
            
            # Volume analysis
            volume_ratio = df['Volume'].iloc[-1] / df['Volume_SMA'].iloc[-1]
            if volume_ratio > 2.0:
                score += 15
            elif volume_ratio > 1.5:
                score += 10
            elif volume_ratio < 0.5:
                score -= 10
            
            # Price momentum
            price_change = (current_price / df['Close'].iloc[-6] - 1) * 100 if len(df) >= 6 else 0
            if 2 <= price_change <= 8:
                score += 10
            elif price_change > 15:
                score -= 5  # Too much too fast
            
            recommendation = "STRONG BUY" if score >= 75 else "BUY" if score >= 65 else "WEAK BUY" if score >= 55 else "HOLD"
            
            market_name = "🇮🇳 India" if symbol.endswith('.NS') or symbol.endswith('.BO') else "🇲🇾 Malaysia" if symbol.endswith('.KL') else "🇺🇸 USA"
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'swing_score': max(0, min(100, score)),
                'recommendation': recommendation,
                'risk_level': 'Medium',  # Default for basic analysis
                'entry_type': "Swing Entry",
                'risk_reward': f"{2.0:.1f}:1",
                'market_name': market_name,
                'technical_indicators': {
                    'rsi': {
                        'value': rsi,
                        'signal': rsi_status
                    },
                    'macd': {
                        'signal': 'Basic Analysis'
                    }
                },
                'signals': [
                    f"Price: ${current_price:.2f}",
                    f"RSI: {rsi:.1f} ({rsi_status})",
                    f"Score: {score}/100",
                    f"Volume: {'High' if volume_ratio > 1.5 else 'Normal'}"
                ]
            }
            
        except Exception as e:
            print(f"Error in basic analysis for {symbol}: {e}")
            return None
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI with proper formula"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

# Create analyzer instances
EnhancedSwingAnalyzer = ProfessionalSwingAnalyzer  # For backwards compatibility

@st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes
def get_daily_swing_signals() -> Dict:
    """Get daily swing trading signals with caching"""
    return _get_swing_signals_internal()

def _get_swing_signals_internal() -> Dict:
    """Internal function to get swing signals using professional analysis"""
    print("🔍 Professional scanning ~73 major stocks across markets...")
    
    analyzer = ProfessionalSwingAnalyzer()
    
    # Basic market watchlists
    watchlists = get_market_watchlists()
    
    results = {
        'timestamp': datetime.now(),
        'scan_type': 'PROFESSIONAL_QUICK',
        'markets': {},
        'total_stocks_scanned': sum(len(symbols) for symbols in watchlists.values()),
        'scan_duration': None
    }
    
    start_time = time.time()
    
    for market, symbols in watchlists.items():
        market_name = "🇺🇸 USA" if market == 'usa' else "🇮🇳 India" if market == 'india' else "🇲🇾 Malaysia"
        
        print(f"📊 Professional analysis for {market_name}: {len(symbols)} stocks")
        market_start = time.time()
        opportunities = []
        
        for symbol in symbols:
            try:
                result = analyzer.calculate_swing_signals(symbol)
                if result and result.get('swing_score', 0) >= 60:
                    opportunities.append(result)
                    print(f"  ✅ {symbol}: {result['swing_score']}/100 - {result['recommendation']}")
            except Exception as e:
                print(f"  ❌ Error analyzing {symbol}: {e}")
                continue
        
        # Sort by score
        opportunities.sort(key=lambda x: x.get('swing_score', 0), reverse=True)
        
        market_duration = time.time() - market_start
        
        results['markets'][market] = {
            'name': market_name,
            'opportunities': opportunities[:15],  # Top 15
            'total_scanned': len(symbols),
            'opportunities_found': len(opportunities),
            'scan_duration': market_duration
        }
        
        print(f"✅ {market_name}: {len(opportunities)} opportunities in {market_duration:.1f}s")
    
    results['scan_duration'] = time.time() - start_time
    return results

def get_market_watchlists() -> Dict[str, List[str]]:
    """Get basic market watchlists"""
    return {
        'usa': [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'CRM', 'ADBE',
            'PYPL', 'INTC', 'AMD', 'ORCL', 'CSCO', 'IBM', 'V', 'MA', 'JPM', 'BAC',
            'WMT', 'PG', 'JNJ', 'UNH', 'HD', 'DIS', 'KO', 'PFE'
        ],
        'india': [
            'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS', 'HINDUNILVR.NS',
            'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ASIANPAINT.NS', 'MARUTI.NS', 'BAJFINANCE.NS',
            'LT.NS', 'HCLTECH.NS', 'AXISBANK.NS', 'KOTAKBANK.NS', 'TITAN.NS', 'ULTRACEMCO.NS',
            'WIPRO.NS', 'NESTLEIND.NS', 'POWERGRID.NS', 'NTPC.NS', 'ONGC.NS', 'TATAMOTORS.NS',
            'TECHM.NS'
        ],
        'malaysia': [
            '1155.KL', 'PBBANK.KL', '5225.KL', '3816.KL', '1066.KL', '2445.KL', '5347.KL',
            '1295.KL', '4197.KL', '5183.KL', '6012.KL', '1961.KL', '2658.KL', '4863.KL',
            '3034.KL', '4715.KL', '5285.KL', '2267.KL', '6947.KL', '1503.KL'
        ]
    }

def get_comprehensive_swing_signals(progress_callback=None, top_n: int = 15) -> Dict:
    """Comprehensive scan using ULTRA-FAST batch processing"""
    print("🚀 COMPREHENSIVE SCAN -> REDIRECTING TO ULTRA-FAST BATCH PROCESSING")
    return get_ultra_fast_swing_signals(progress_callback=progress_callback, top_n=top_n)

def get_ultra_fast_swing_signals(progress_callback=None, top_n: int = 15) -> Dict:
    """ULTRA-FAST market scan using batch downloads and concurrent processing"""
    print("⚡ ULTRA-FAST MARKET SCAN STARTING...")
    print("🎯 Using optimized batch downloads + concurrent processing")
    
    # Import the high-performance scanner
    try:
        from .high_performance_scanner import HighPerformanceScanner
    except ImportError:
        # If high_performance_scanner not available, use built-in fast method
        print("⚠️ High-performance scanner not available, using built-in method")
        return get_daily_swing_signals()
    
    # Get comprehensive stock lists for maximum coverage
    try:
        from .market_stock_lists import get_comprehensive_market_watchlists
        watchlists = get_comprehensive_market_watchlists(validate=False)
        print("📊 COMPREHENSIVE MARKET COVERAGE:")
        print("🇺🇸 USA: 232 stocks (Major caps + Growth + Value + Sectors)")
        print("🇮🇳 India: 155 stocks (NSE large/mid/small caps + ETFs)")  
        print("🇲🇾 Malaysia: 53 stocks (Bursa Malaysia active stocks)")
        print("📈 Total: 440 stocks across all markets")
        print("\nThis provides comprehensive coverage for finding swing trading opportunities!")
    except ImportError:
        watchlists = get_market_watchlists()
        print("⚠️ Using basic stock lists")
    
    scanner = HighPerformanceScanner(max_workers=15, batch_size=30)
    
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
        
        # Update progress callback for market start
        if progress_callback:
            overall_progress = scanned_count / total_stocks
            progress_callback(f"Starting {market_name} scan ({len(symbols)} stocks)", overall_progress)
        
        # Scan this market using high-performance scanner
        market_result = scanner.fast_market_scan(
            symbols, market_name, 
            progress_callback=lambda msg, prog: progress_callback(
                f"{market_name}: {msg}", 
                (scanned_count + prog * len(symbols)) / total_stocks
            ) if progress_callback else None,
            top_n=top_n
        )
        
        results['markets'][market] = market_result
        scanned_count += len(symbols)
        
        print(f"✅ {market_name}: {market_result['opportunities_found']} opportunities in {market_result['total_time']:.1f}s")
    
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
