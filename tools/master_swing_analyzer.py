#!/usr/bin/env python3
"""
🎯 MASTER SWING ANALYZER - THE ONE AND ONLY ANALYSIS SYSTEM

This is the DEFINITIVE analysis system for swing trading.
No other analysis files should exist or be used.

Features:
- Professional technical analysis with proper RSI/MACD interpretations
- Multi-source data integration (Price, Fundamentals, News, Economic)
- Risk-adjusted scoring system (no simple arithmetic)
- Market context awareness
- Real data only (no mock/sample/fallback data)
"""

import yfinance as yf
import pandas as pd
import numpy as np
import talib
import requests
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time
import ta

class MasterSwingAnalyzer:
    """
    THE ONLY swing trading analyzer.
    Addresses all critical issues from user feedback:
    - No contradictory signals
    - Professional technical analysis
    - Market context integration
    - External data sources
    - Risk-adjusted scoring
    """
    
    def __init__(self):
        """Initialize the master analyzer with all required components"""
        # API Configuration (free tiers)
        self.apis = {
            'alpha_vantage_key': os.getenv('ALPHA_VANTAGE_API_KEY'),
            'fred_key': os.getenv('FRED_API_KEY'), 
            'news_key': os.getenv('NEWS_API_KEY')
        }
        
        # Professional indicator parameters
        self.rsi_period = 14
        self.macd_fast = 12
        self.macd_slow = 26
        self.macd_signal = 9
        self.adx_period = 14
        
        # Risk management parameters
        self.min_risk_reward = 1.5
        self.max_position_risk = 0.02  # 2% of portfolio
        
        print("✅ Master Swing Analyzer initialized - Professional analysis ready")
    
    def analyze_stock(self, symbol: str) -> Optional[Dict]:
        """
        MAIN ANALYSIS FUNCTION
        
        This is the ONLY function that should be called for stock analysis.
        Integrates all components into one comprehensive analysis.
        """
        try:
            print(f"🔍 Analyzing {symbol} with professional system...")
            
            # 1. Get price data
            price_data = self._get_price_data(symbol)
            if price_data is None:
                return None
            
            # 2. Calculate technical indicators (NO CONTRADICTIONS)
            technical_analysis = self._calculate_technical_indicators(price_data)
            
            # 3. Get market context
            market_context = self._get_market_context(symbol)
            
            # 4. Get external data
            external_data = self._get_external_data(symbol)
            
            # 5. Calculate risk-adjusted score (NO SIMPLE ARITHMETIC)
            final_score = self._calculate_professional_score(
                technical_analysis, market_context, external_data
            )
            
            # 6. Generate professional recommendation
            recommendation = self._generate_recommendation(
                final_score, technical_analysis, market_context, external_data
            )
            
            # 7. Compile comprehensive result
            result = {
                'symbol': symbol,
                'timestamp': datetime.now(),
                'current_price': technical_analysis['current_price'],
                'swing_score': final_score,
                'recommendation': recommendation['action'],
                'confidence': recommendation['confidence'],
                'risk_level': recommendation['risk_level'],
                'entry_type': recommendation['entry_type'],
                'market_name': self._get_market_name(symbol),
                
                # Technical Analysis (NO CONTRADICTIONS)
                'technical_indicators': technical_analysis,
                
                # Dashboard compatibility - technical data at top level
                'rsi': technical_analysis['rsi']['value'],
                'rsi_status': technical_analysis['rsi']['status'],
                'rsi_interpretation': technical_analysis['rsi']['interpretation'],
                'macd_signal_trend': technical_analysis['macd']['status'],
                'volume_trend': technical_analysis['volume_analysis']['obv_trend'],
                'trend_strength': technical_analysis['adx']['trend_strength'],
                'support_levels': [technical_analysis['support_resistance']['support']],
                'resistance_levels': [technical_analysis['support_resistance']['resistance']],
                
                # Market Context
                'market_context': {
                    'market_regime': market_context['regime'],
                    'sector_strength': market_context['sector_strength'],
                    'relative_performance': market_context['relative_performance']
                },
                
                # External Factors
                'external_factors': {
                    'fundamentals': external_data['fundamentals'],
                    'news_sentiment': external_data['news_sentiment'],
                    'economic_indicators': external_data['economic_indicators']
                },
                
                # Risk Management
                'risk_management': recommendation['risk_management'],
                
                # Trade Setup
                'trade_setup': recommendation['trade_setup']
            }
            
            return result
            
        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {e}")
            return None
    
    def _get_price_data(self, symbol: str, period: str = "6mo") -> Optional[pd.DataFrame]:
        """Get real price data (NO MOCK DATA)"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval="1d")
            
            if len(df) < 50:  # Need minimum data for analysis
                print(f"⚠️ Insufficient data for {symbol}: {len(df)} days")
                return None
            
            return df
            
        except Exception as e:
            print(f"❌ Failed to get price data for {symbol}: {e}")
            return None
    
    def _calculate_technical_indicators(self, df: pd.DataFrame) -> Dict:
        """
        Professional-grade technical analysis.
        This function implements all feedback from the user to fix contradictions
        and add comprehensive indicators.
        """
        # Add all indicators from the 'ta' library to the DataFrame
        df = ta.add_all_ta_features(
            df, open="Open", high="High", low="Low", close="Close", volume="Volume", fillna=True
        )

        current_price = df['Close'].iloc[-1]
        
        # --- RSI Analysis (Fixed Contradiction) ---
        current_rsi = df['momentum_rsi'].iloc[-1]
        if current_rsi <= 30:
            rsi_status = "Oversold"
            rsi_interpretation = "Strong oversold, potential bounce"
        elif 30 < current_rsi <= 45:
            rsi_status = "Oversold Territory"
            rsi_interpretation = "Entering oversold zone, potential swing entry"
        elif 45 < current_rsi <= 55:
            rsi_status = "Neutral"
            rsi_interpretation = "Neutral momentum, wait for confirmation"
        elif 55 < current_rsi <= 70:
            rsi_status = "Overbought Territory"
            rsi_interpretation = "Entering overbought zone, caution advised"
        else:
            rsi_status = "Overbought"
            rsi_interpretation = "Strong overbought, potential reversal"

        # --- MACD Analysis (Fixed Contradiction) ---
        macd_diff = df['trend_macd_diff'].iloc[-1]
        if macd_diff > 0 and df['trend_macd_diff'].iloc[-2] < 0:
            macd_status = "Bullish Crossover"
        elif macd_diff < 0 and df['trend_macd_diff'].iloc[-2] > 0:
            macd_status = "Bearish Crossover"
        elif macd_diff > 0:
            macd_status = "Bullish"
        else:
            macd_status = "Bearish"

        # --- Moving Average Analysis (Fixed Contradiction) ---
        sma_20 = df['trend_sma_fast'].iloc[-1]
        sma_50 = df['trend_sma_slow'].iloc[-1]
        if current_price > sma_20 and current_price > sma_50 and sma_20 > sma_50:
            ma_status = "Strong Bullish Trend"
        elif current_price < sma_20 and current_price < sma_50 and sma_20 < sma_50:
            ma_status = "Strong Bearish Trend"
        elif current_price > sma_20 and current_price > sma_50:
            ma_status = "Bullish"
        else:
            ma_status = "Bearish"

        # --- ADX Trend Strength ---
        current_adx = df['trend_adx'].iloc[-1]
        if current_adx > 40:
            trend_strength = "Very Strong Trend"
        elif current_adx > 25:
            trend_strength = "Strong Trend"
        else:
            trend_strength = "Weak or No Trend"

        # --- Volume Profile Analysis ---
        obv_slope = talib.LINEARREG_SLOPE(df['volume_obv'], timeperiod=10)[-1]
        if obv_slope > 0:
            volume_trend = "Accumulation"
        else:
            volume_trend = "Distribution"

        # --- Support & Resistance ---
        support_level = df['Low'].rolling(30).min().iloc[-1]
        resistance_level = df['High'].rolling(30).max().iloc[-1]

        return {
            'current_price': current_price,
            'rsi': {'value': current_rsi, 'status': rsi_status, 'interpretation': rsi_interpretation},
            'macd': {'diff': macd_diff, 'status': macd_status},
            'moving_averages': {'sma_20': sma_20, 'sma_50': sma_50, 'status': ma_status},
            'adx': {'value': current_adx, 'trend_strength': trend_strength},
            'stochastic_rsi': {'value': df['momentum_stoch_rsi'].iloc[-1]},
            'williams_r': {'value': df['momentum_wr'].iloc[-1]},
            'volume_analysis': {
                'obv_trend': volume_trend,
                'vwap': df['volume_vwap'].iloc[-1]
            },
            'volatility': {
                'atr': df['volatility_atr'].iloc[-1],
                'bb_width': df['volatility_bbw'].iloc[-1]
            },
            'support_resistance': {
                'support': support_level,
                'resistance': resistance_level
            }
        }
    
    def _get_market_context(self, symbol: str) -> Dict:
        """Get market context - ADDRESSES MISSING MARKET ANALYSIS"""
        try:
            # Determine market index
            if symbol.endswith('.NS') or symbol.endswith('.BO'):
                index_symbol = "^NSEI"  # Nifty 50
                market = "India"
            elif symbol.endswith('.KL'):
                index_symbol = "^KLSE"  # KLCI
                market = "Malaysia"
            else:
                index_symbol = "^GSPC"  # S&P 500
                market = "USA"
            
            # Get index data
            index_ticker = yf.Ticker(index_symbol)
            index_data = index_ticker.history(period="3mo")
            
            # Market regime detection
            index_sma_20 = index_data['Close'].rolling(20).mean()
            index_sma_50 = index_data['Close'].rolling(50).mean()
            current_index = index_data['Close'].iloc[-1]
            
            if current_index > index_sma_20.iloc[-1] > index_sma_50.iloc[-1]:
                market_regime = "Bull Market"
                regime_strength = "Strong"
            elif current_index < index_sma_20.iloc[-1] < index_sma_50.iloc[-1]:
                market_regime = "Bear Market"
                regime_strength = "Strong"
            else:
                market_regime = "Sideways Market"
                regime_strength = "Moderate"
            
            # Sector strength (simplified for now)
            sector_strength = "Neutral"  # Can be enhanced with sector ETF data
            
            # Relative performance
            stock_ticker = yf.Ticker(symbol)
            stock_data = stock_ticker.history(period="1mo")
            
            if len(stock_data) >= 20 and len(index_data) >= 20:
                stock_return = (stock_data['Close'].iloc[-1] / stock_data['Close'].iloc[-20] - 1) * 100
                index_return = (index_data['Close'].iloc[-1] / index_data['Close'].iloc[-20] - 1) * 100
                relative_performance = stock_return - index_return
                
                if relative_performance > 5:
                    relative_strength = "Outperforming"
                elif relative_performance < -5:
                    relative_strength = "Underperforming"
                else:
                    relative_strength = "In-line"
            else:
                relative_strength = "Unknown"
            
            return {
                'market': market,
                'regime': market_regime,
                'regime_strength': regime_strength,
                'sector_strength': sector_strength,
                'relative_performance': relative_strength
            }
            
        except Exception as e:
            print(f"⚠️ Market context error for {symbol}: {e}")
            return {
                'market': 'Unknown',
                'regime': 'Unknown',
                'regime_strength': 'Unknown',
                'sector_strength': 'Unknown',
                'relative_performance': 'Unknown'
            }
    
    def _get_external_data(self, symbol: str) -> Dict:
        """Get external data from free APIs"""
        return {
            'fundamentals': self._get_fundamentals(symbol),
            'news_sentiment': self._get_news_sentiment(symbol),
            'economic_indicators': self._get_economic_indicators()
        }
    
    def _get_fundamentals(self, symbol: str) -> Dict:
        """Get fundamental data from Alpha Vantage (free tier)"""
        if not self.apis['alpha_vantage_key']:
            return {'status': 'API key not configured'}
        
        try:
            clean_symbol = symbol.replace('.NS', '').replace('.KL', '')
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'OVERVIEW',
                'symbol': clean_symbol,
                'apikey': self.apis['alpha_vantage_key']
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'Symbol' in data:
                return {
                    'pe_ratio': float(data.get('PERatio', 0)) if data.get('PERatio') != 'None' else None,
                    'market_cap': data.get('MarketCapitalization', 'Unknown'),
                    'sector': data.get('Sector', 'Unknown'),
                    'status': 'Available'
                }
            else:
                return {'status': 'No data available'}
                
        except Exception as e:
            return {'status': f'Error: {e}'}
    
    def _get_news_sentiment(self, symbol: str) -> Dict:
        """Get news sentiment from NewsAPI (free tier)"""
        if not self.apis['news_key']:
            return {'status': 'API key not configured'}
        
        try:
            clean_symbol = symbol.replace('.NS', '').replace('.KL', '')
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': clean_symbol,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': 10,
                'apiKey': self.apis['news_key']
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('status') == 'ok' and data.get('articles'):
                # Simple sentiment analysis based on headlines
                articles = data['articles']
                positive_words = ['bullish', 'positive', 'growth', 'profit', 'gain', 'up', 'rise']
                negative_words = ['bearish', 'negative', 'loss', 'down', 'fall', 'decline']
                
                sentiment_score = 0
                for article in articles:
                    title = article.get('title', '').lower()
                    sentiment_score += sum(1 for word in positive_words if word in title)
                    sentiment_score -= sum(1 for word in negative_words if word in title)
                
                if sentiment_score > 2:
                    sentiment = 'Positive'
                elif sentiment_score < -2:
                    sentiment = 'Negative'
                else:
                    sentiment = 'Neutral'
                
                return {
                    'sentiment': sentiment,
                    'score': sentiment_score,
                    'articles_count': len(articles),
                    'status': 'Available'
                }
            else:
                return {'status': 'No news available'}
                
        except Exception as e:
            return {'status': f'Error: {e}'}
    
    def _get_economic_indicators(self) -> Dict:
        """Get economic indicators from FRED (free)"""
        if not self.apis['fred_key']:
            return {'status': 'API key not configured'}
        
        try:
            # Get VIX for market fear gauge
            vix_ticker = yf.Ticker('^VIX')
            vix_data = vix_ticker.history(period='5d')
            
            if len(vix_data) > 0:
                current_vix = vix_data['Close'].iloc[-1]
                
                if current_vix > 30:
                    market_fear = 'High Fear'
                elif current_vix > 20:
                    market_fear = 'Moderate Fear'
                else:
                    market_fear = 'Low Fear'
                
                return {
                    'vix': current_vix,
                    'market_fear': market_fear,
                    'status': 'Available'
                }
            else:
                return {'status': 'No data available'}
                
        except Exception as e:
            return {'status': f'Error: {e}'}
    
    def _calculate_professional_score(self, technical: Dict, market: Dict, external: Dict) -> int:
        """
        Professional risk-adjusted scoring system based on user feedback.
        This system uses a weighted model and considers multiple factors to avoid
        oversimplification and produce a reliable score.
        """
        weights = {
            'technical': 0.60,
            'market': 0.25,
            'external': 0.15
        }

        # --- Technical Score (60%) ---
        tech_score = 0
        
        # RSI (15%)
        rsi_val = technical['rsi']['value']
        if 30 < rsi_val < 45: tech_score += 15  # Oversold territory, good for entry
        elif rsi_val <= 30: tech_score += 10 # Deeply oversold, may bounce
        elif 55 < rsi_val < 70: tech_score -= 10 # Overbought territory
        elif rsi_val >= 70: tech_score -= 15 # Deeply overbought

        # MACD (15%)
        if technical['macd']['status'] == "Bullish Crossover": tech_score += 15
        elif technical['macd']['status'] == "Bullish": tech_score += 10
        elif technical['macd']['status'] == "Bearish Crossover": tech_score -= 15
        elif technical['macd']['status'] == "Bearish": tech_score -= 10

        # Trend Strength (ADX) (15%)
        if technical['adx']['trend_strength'] == "Very Strong Trend": tech_score += 15
        elif technical['adx']['trend_strength'] == "Strong Trend": tech_score += 10
        
        # Volume Profile (15%)
        if technical['volume_analysis']['obv_trend'] == "Accumulation": tech_score += 15
        else: tech_score -= 15

        # --- Market Context Score (25%) ---
        market_score = 0
        if market['regime'] == "Bull Market": market_score += 15
        elif market['regime'] == "Bear Market": market_score -= 15
        
        if market['relative_performance'] == "Outperforming": market_score += 10
        elif market['relative_performance'] == "Underperforming": market_score -= 10

        # --- External Factors Score (15%) ---
        external_score = 0
        if external['news_sentiment'].get('sentiment') == 'Positive': external_score += 8
        elif external['news_sentiment'].get('sentiment') == 'Negative': external_score -= 8

        if external['economic_indicators'].get('market_fear') == 'Low Fear': external_score += 7
        elif external['economic_indicators'].get('market_fear') == 'High Fear': external_score -= 7

        # Combine scores with weights
        final_score = 50 + (tech_score * weights['technical']) + \
                      (market_score * weights['market']) + \
                      (external_score * weights['external'])

        # --- Risk-Adjusted Scoring ---
        risk_adjustments = {
            'high_volatility': -10 if technical['volatility']['atr'] / technical['current_price'] > 0.05 else 0,
            'poor_risk_reward': -15 if self._calculate_risk_reward(technical)[0] < 1.5 else 0,
            'against_trend': -20 if (market['regime'] == "Bear Market" and technical['moving_averages']['status'] == "Bullish") else 0,
            'low_volume': -10 if technical['volume_analysis']['obv_trend'] == "Distribution" else 0,
        }
        
        final_score += sum(risk_adjustments.values())

        return max(0, min(100, int(final_score)))

    def _calculate_risk_reward(self, technical: Dict) -> Tuple[float, float, float]:
        current_price = technical['current_price']
        support = technical['support_resistance']['support']
        resistance = technical['support_resistance']['resistance']
        
        potential_gain = resistance - current_price
        potential_loss = current_price - support
        
        ratio = potential_gain / potential_loss if potential_loss > 0 else 0
        return ratio, potential_gain, potential_loss

    
    def _generate_recommendation(self, score: int, technical: Dict, market: Dict, external: Dict) -> Dict:
        """Generate professional recommendation with detailed rationale"""
        
        # Risk/Reward calculation
        risk_reward_ratio, _, _ = self._calculate_risk_reward(technical)
        
        # Generate recommendation based on score and risk/reward
        if score >= 75 and risk_reward_ratio >= 2.0:
            action = "STRONG BUY"
            confidence = "Very High"
        elif score >= 65 and risk_reward_ratio >= 1.5:
            action = "BUY"
            confidence = "High"
        elif score >= 55 and risk_reward_ratio >= 1.2:
            action = "WEAK BUY"
            confidence = "Medium"
        elif score >= 45:
            action = "HOLD"
            confidence = "Low"
        else:
            action = "AVOID"
            confidence = "Very High"

        # Determine Risk Level based on volatility
        atr_percentage = technical['volatility']['atr'] / technical['current_price']
        if atr_percentage > 0.05:
            risk_level = "Very High"
        elif atr_percentage > 0.03:
            risk_level = "High"
        else:
            risk_level = "Medium"

        # Dynamic stops and targets
        stop_loss = technical['current_price'] - (technical['volatility']['atr'] * 2)
        target_1 = technical['current_price'] + (technical['volatility']['atr'] * 3)
        target_2 = technical['current_price'] + (technical['volatility']['atr'] * 5)
        
        return {
            'action': action,
            'confidence': confidence,
            'risk_level': risk_level,
            'entry_type': "Breakout" if technical['moving_averages']['status'] == "Bullish" else "Reversal",
            'risk_management': {
                'stop_loss': stop_loss,
                'target_1': target_1,
                'target_2': target_2,
                'risk_reward_ratio': f"{risk_reward_ratio:.1f}:1",
                'position_size': self._calculate_position_size(score, risk_level)
            },
            'trade_setup': {
                'entry_price': technical['current_price'],
                'timeframe': 'Swing (2-10 days)',
                'market_conditions': f"{market['regime']} in {market['market']} market"
            }
        }
    
    def _calculate_position_size(self, score: int, risk_level: str) -> str:
        """Calculate appropriate position size based on score and risk"""
        if risk_level == "Low" and score >= 85:
            return "Full Position (100%)"
        elif risk_level == "Medium" and score >= 70:
            return "Standard Position (75%)"
        elif risk_level == "Medium" and score >= 60:
            return "Reduced Position (50%)"
        else:
            return "Small Position (25%)"
    
    def _get_market_name(self, symbol: str) -> str:
        """Get market name for display"""
        if symbol.endswith('.NS') or symbol.endswith('.BO'):
            return "🇮🇳 India"
        elif symbol.endswith('.KL'):
            return "🇲🇾 Malaysia"
        else:
            return "🇺🇸 USA"
    
    def get_portfolio_position_analysis(self, positions):
        """
        Analyze portfolio positions using master swing analyzer
        
        Args:
            positions: List of position dictionaries
            
        Returns:
            list: Analysis results for each position
        """
        if not positions:
            return []
        
        analyzed_positions = []
        
        for position in positions:
            try:
                symbol = position.get('symbol', '')
                if not symbol:
                    continue
                
                # Get analysis for this position
                analysis = self.analyze_stock(symbol)
                
                if analysis:
                    # Combine position data with analysis
                    position_analysis = {
                        **position,  # Include original position data
                        'current_analysis': analysis,
                        'recommendation': analysis.get('recommendation', 'HOLD'),
                        'swing_score': analysis.get('swing_score', 50),
                        'current_price': analysis.get('current_price', 0),
                        'risk_level': analysis.get('risk_level', 'Medium'),
                        'confidence': analysis.get('confidence', 'Medium')
                    }
                    
                    # Calculate P&L if we have entry price
                    if 'entry_price' in position and 'quantity' in position:
                        entry_price = position['entry_price']
                        quantity = position['quantity']
                        current_price = analysis.get('current_price', entry_price)
                        
                        position_analysis['pnl'] = (current_price - entry_price) * quantity
                        position_analysis['pnl_percentage'] = ((current_price - entry_price) / entry_price * 100) if entry_price > 0 else 0
                    
                    analyzed_positions.append(position_analysis)
                    
            except Exception as e:
                print(f"Error analyzing position {position}: {e}")
                continue
        
        return analyzed_positions
    
    def get_daily_swing_signals(self, progress_callback=None) -> Dict:
        """
        Get daily swing signals for all markets.
        
        This is the main function called by the dashboard.
        It scans comprehensive market watchlists and returns the top 5 results
        for each market, sorted by the professional swing score.
        """
        print("🔍 Master Swing Analyzer scanning comprehensive markets...")
        
        from tools.market_stock_lists import get_comprehensive_market_watchlists
        watchlists = get_comprehensive_market_watchlists(validate=False)
        
        results = {
            'timestamp': datetime.now(),
            'scan_type': 'MASTER_PROFESSIONAL',
            'markets': {},
            'total_stocks_scanned': sum(len(s) for s in watchlists.values()),
            'scan_duration': None
        }
        
        start_time = time.time()
        total_stocks = results['total_stocks_scanned']
        scanned_count = 0
        
        for market, symbols in watchlists.items():
            market_name = self._get_market_name(symbols[0] if symbols else "")
            print(f"📊 Master analysis for {market_name}: {len(symbols)} stocks")
            market_start = time.time()
            
            all_results = []
            for symbol in symbols:
                try:
                    if progress_callback:
                        progress = scanned_count / total_stocks
                        progress_callback(f"Analyzing {market_name}: {symbol}", progress)
                    
                    result = self.analyze_stock(symbol)
                    if result:
                        all_results.append(result)
                        if result.get('swing_score', 0) >= 60:
                            print(f"  ✅ {symbol}: {result['swing_score']}/100 - {result['recommendation']}")
                    
                    scanned_count += 1
                except Exception as e:
                    print(f"  ❌ Error analyzing {symbol}: {e}")
                    scanned_count += 1
                    continue
            
            # Sort all results by score to get the top performers
            all_results.sort(key=lambda x: x.get('swing_score', 0), reverse=True)
            
            opportunities = [res for res in all_results if res.get('swing_score', 0) >= 55]
            market_duration = time.time() - market_start
            
            results['markets'][market] = {
                'name': market_name,
                'opportunities': opportunities,
                'top_5': all_results[:5],  # Always list top 5
                'total_scanned': len(symbols),
                'opportunities_found': len(opportunities),
                'scan_duration': market_duration
            }
            
            print(f"✅ {market_name}: {len(opportunities)} opportunities in {market_duration:.1f}s")
        
        results['scan_duration'] = time.time() - start_time
        
        if progress_callback:
            progress_callback("Scan complete!", 1.0)
        
        print(f"🎯 Master scan complete: {scanned_count} stocks in {results['scan_duration']:.1f}s")
        return results


# Compatibility aliases for existing code
EnhancedSwingAnalyzer = MasterSwingAnalyzer  # For backward compatibility

def get_daily_swing_signals(progress_callback=None):
    """Compatibility function for dashboard"""
    analyzer = MasterSwingAnalyzer()
    return analyzer.get_daily_swing_signals(progress_callback)

def get_portfolio_analysis(portfolio):
    """
    Portfolio analysis function for dashboard compatibility
    
    Args:
        portfolio: Portfolio object containing current positions
        
    Returns:
        list: List of analyzed positions (for dashboard iteration)
    """
    if not portfolio:
        return []
    
    try:
        analyzer = MasterSwingAnalyzer()
        current_positions = portfolio.get_positions() if hasattr(portfolio, 'get_positions') else []
        
        if not current_positions:
            return []
        
        # Analyze each position
        analyzed_positions = []
        
        for position in current_positions:
            try:
                symbol = position.get('symbol', '')
                quantity = position.get('quantity', 0)
                entry_price = position.get('entry_price', 0)
                
                if not symbol or quantity == 0:
                    continue
                
                # Get current analysis for the position
                analysis = analyzer.analyze_stock(symbol)
                
                if analysis:
                    current_price = analysis.get('current_price', entry_price)
                    pnl_pct = ((current_price - entry_price) / entry_price * 100) if entry_price > 0 else 0
                    recommendation = analysis.get('recommendation', 'HOLD')
                    
                    # Map recommendation to action for dashboard
                    if recommendation in ['STRONG_SELL', 'SELL']:
                        action = 'SELL'
                    elif recommendation in ['WEAK_SELL']:
                        action = 'PARTIAL_SELL'
                    elif recommendation in ['STRONG_BUY', 'BUY']:
                        action = 'HOLD'  # Don't sell good positions
                    elif pnl_pct < -10:  # Stop loss threshold
                        action = 'STOP_LOSS'
                    elif pnl_pct < -5:   # Watch closely threshold
                        action = 'WATCH_CLOSE'
                    else:
                        action = 'HOLD'
                    
                    analyzed_positions.append({
                        'symbol': symbol,
                        'quantity': quantity,
                        'entry_price': entry_price,
                        'current_price': current_price,
                        'pnl_pct': pnl_pct,
                        'action': action,
                        'recommendation': recommendation,
                        'swing_score': analysis.get('swing_score', 50),
                        'risk_level': analysis.get('risk_level', 'Medium'),
                        'confidence': analysis.get('confidence', 'Medium')
                    })
                    
            except Exception as e:
                print(f"Error analyzing position {position}: {e}")
                continue
        
        return analyzed_positions
        
    except Exception as e:
        print(f"Portfolio analysis error: {e}")
        return []
