"""
Market Context and Catalyst Analysis Module
Addresses market breadth, sentiment, and catalyst calendar
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from typing import Dict, List, Optional

class MarketContextAnalyzer:
    def __init__(self):
        self.sector_etfs = {
            'Technology': 'XLK',
            'Financials': 'XLF', 
            'Healthcare': 'XLV',
            'Energy': 'XLE',
            'Consumer Discretionary': 'XLY',
            'Industrials': 'XLI',
            'Materials': 'XLB',
            'Utilities': 'XLU',
            'Real Estate': 'XLRE',
            'Consumer Staples': 'XLP',
            'Communications': 'XLC'
        }
        
        self.market_indices = {
            'S&P 500': '^GSPC',
            'NASDAQ': '^IXIC',
            'Dow Jones': '^DJI',
            'Russell 2000': '^RUT',
            'VIX': '^VIX'
        }

    def analyze_sector_performance(self, period="1mo"):
        """
        6. Market Breadth & Sentiment Analysis
        Analyze sector rotation and relative strength
        """
        sector_performance = {}
        
        for sector, etf in self.sector_etfs.items():
            try:
                ticker = yf.Ticker(etf)
                data = ticker.history(period=period)
                
                if len(data) > 0:
                    performance = ((data['Close'].iloc[-1] - data['Close'].iloc[0]) / 
                                 data['Close'].iloc[0] * 100)
                    
                    # Calculate relative strength vs S&P 500
                    spy = yf.Ticker('SPY').history(period=period)
                    spy_performance = ((spy['Close'].iloc[-1] - spy['Close'].iloc[0]) / 
                                     spy['Close'].iloc[0] * 100)
                    
                    relative_strength = performance - spy_performance
                    
                    sector_performance[sector] = {
                        'performance': performance,
                        'relative_strength': relative_strength,
                        'strength_rating': self.get_strength_rating(relative_strength)
                    }
                    
            except Exception as e:
                print(f"Error analyzing {sector}: {e}")
        
        # Rank sectors by performance
        sorted_sectors = sorted(sector_performance.items(), 
                              key=lambda x: x[1]['performance'], reverse=True)
        
        return {
            'sector_performance': sector_performance,
            'top_sectors': sorted_sectors[:3],
            'bottom_sectors': sorted_sectors[-3:],
            'market_rotation_analysis': self.analyze_rotation_pattern(sector_performance)
        }

    def get_strength_rating(self, relative_strength):
        """Rate sector strength relative to market"""
        if relative_strength > 2:
            return 'Very Strong'
        elif relative_strength > 0:
            return 'Strong'
        elif relative_strength > -2:
            return 'Weak'
        else:
            return 'Very Weak'

    def analyze_rotation_pattern(self, sector_performance):
        """Analyze sector rotation to determine market phase"""
        # Defensive vs Cyclical analysis
        defensive_sectors = ['Utilities', 'Consumer Staples', 'Healthcare']
        cyclical_sectors = ['Technology', 'Financials', 'Energy', 'Industrials']
        
        defensive_avg = np.mean([sector_performance.get(s, {}).get('performance', 0) 
                               for s in defensive_sectors if s in sector_performance])
        
        cyclical_avg = np.mean([sector_performance.get(s, {}).get('performance', 0) 
                              for s in cyclical_sectors if s in sector_performance])
        
        if cyclical_avg > defensive_avg + 2:
            return 'Risk-On (Cyclical Leadership)'
        elif defensive_avg > cyclical_avg + 2:
            return 'Risk-Off (Defensive Leadership)'
        else:
            return 'Neutral (Mixed Leadership)'

    def get_market_internals(self):
        """Analyze market breadth indicators"""
        try:
            # Get advance/decline data (simplified using major indices)
            indices_data = {}
            
            for name, symbol in self.market_indices.items():
                ticker = yf.Ticker(symbol)
                data = ticker.history(period="5d")
                
                if len(data) > 0:
                    # Calculate recent performance
                    performance = ((data['Close'].iloc[-1] - data['Close'].iloc[0]) / 
                                 data['Close'].iloc[0] * 100)
                    
                    indices_data[name] = {
                        'current_price': data['Close'].iloc[-1],
                        'performance_5d': performance,
                        'volume_trend': self.analyze_volume_trend(data)
                    }
            
            # VIX analysis for sentiment
            vix_analysis = self.analyze_vix_sentiment(indices_data.get('VIX', {}))
            
            return {
                'indices_performance': indices_data,
                'vix_sentiment': vix_analysis,
                'market_breadth_summary': self.summarize_market_breadth(indices_data)
            }
            
        except Exception as e:
            return {'error': f'Could not fetch market internals: {e}'}

    def analyze_volume_trend(self, data):
        """Analyze volume trend for an instrument"""
        if len(data) < 5:
            return 'Insufficient data'
        
        recent_avg = data['Volume'].tail(3).mean()
        longer_avg = data['Volume'].mean()
        
        if recent_avg > longer_avg * 1.2:
            return 'Increasing'
        elif recent_avg < longer_avg * 0.8:
            return 'Decreasing'
        else:
            return 'Stable'

    def analyze_vix_sentiment(self, vix_data):
        """Analyze VIX for market sentiment"""
        if not vix_data or 'current_price' not in vix_data:
            return {'sentiment': 'Unknown', 'level': 'Unknown'}
        
        vix_level = vix_data['current_price']
        
        if vix_level < 15:
            sentiment = 'Complacent'
            level = 'Very Low'
        elif vix_level < 20:
            sentiment = 'Calm'
            level = 'Low'
        elif vix_level < 30:
            sentiment = 'Elevated'
            level = 'Medium'
        elif vix_level < 40:
            sentiment = 'Fear'
            level = 'High'
        else:
            sentiment = 'Panic'
            level = 'Very High'
        
        return {
            'sentiment': sentiment,
            'level': level,
            'vix_value': vix_level,
            'trading_implication': self.get_vix_trading_implication(vix_level)
        }

    def get_vix_trading_implication(self, vix_level):
        """Get trading implications from VIX level"""
        if vix_level < 15:
            return 'Low volatility - good for trend following strategies'
        elif vix_level < 20:
            return 'Normal volatility - standard strategies apply'
        elif vix_level < 30:
            return 'Elevated volatility - use wider stops, smaller positions'
        else:
            return 'High volatility - extreme caution, consider contrarian plays'

    def summarize_market_breadth(self, indices_data):
        """Summarize overall market breadth"""
        if not indices_data:
            return 'Unknown'
        
        positive_performers = sum(1 for data in indices_data.values() 
                                if isinstance(data, dict) and data.get('performance_5d', 0) > 0)
        total_indices = len([k for k in indices_data.keys() if k != 'VIX'])
        
        if positive_performers >= total_indices * 0.8:
            return 'Broad Market Strength'
        elif positive_performers >= total_indices * 0.6:
            return 'Moderate Market Strength'
        elif positive_performers >= total_indices * 0.4:
            return 'Mixed Market Performance'
        else:
            return 'Broad Market Weakness'

    def get_economic_calendar(self, days_ahead=7):
        """
        7. Catalyst Calendar Analysis
        Get upcoming economic events and earnings
        """
        # This would integrate with economic calendar APIs
        # For now, providing a framework and sample data
        
        upcoming_events = {
            'high_impact_events': [
                {
                    'date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
                    'event': 'FOMC Meeting',
                    'impact': 'High',
                    'description': 'Federal Reserve interest rate decision'
                },
                {
                    'date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
                    'event': 'Non-Farm Payrolls',
                    'impact': 'High',
                    'description': 'Monthly employment report'
                }
            ],
            'earnings_this_week': self.get_earnings_calendar(),
            'economic_indicators': [
                {
                    'date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                    'indicator': 'CPI Data',
                    'impact': 'Medium',
                    'expected': 'Monitor for inflation trends'
                }
            ]
        }
        
        return upcoming_events

    def get_earnings_calendar(self):
        """Get earnings calendar for major stocks"""
        # This would integrate with earnings calendar APIs
        # Sample implementation
        return [
            {
                'symbol': 'AAPL',
                'date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
                'time': 'After Market Close',
                'estimated_eps': '$1.25'
            },
            {
                'symbol': 'GOOGL',
                'date': (datetime.now() + timedelta(days=4)).strftime('%Y-%m-%d'),
                'time': 'After Market Close',
                'estimated_eps': '$1.45'
            }
        ]

    def analyze_stock_specific_catalysts(self, symbol):
        """Analyze stock-specific catalysts and events"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            catalysts = {
                'upcoming_earnings': self.get_next_earnings_date(info),
                'analyst_upgrades_downgrades': self.get_recent_analyst_actions(symbol),
                'insider_trading': 'API integration needed',
                'institutional_flow': 'API integration needed',
                'sector_events': self.get_sector_specific_events(symbol)
            }
            
            return catalysts
            
        except Exception as e:
            return {'error': f'Could not analyze catalysts for {symbol}: {e}'}

    def get_next_earnings_date(self, stock_info):
        """Get next earnings date from stock info"""
        # This would be enhanced with proper earnings calendar API
        return {
            'date': 'TBD - API integration needed',
            'estimate': stock_info.get('forwardEps', 'N/A'),
            'guidance': 'Monitor company guidance'
        }

    def get_recent_analyst_actions(self, symbol):
        """Get recent analyst upgrades/downgrades"""
        # This would integrate with financial news APIs
        return {
            'recent_changes': 'API integration needed',
            'consensus_rating': 'Monitor analyst sentiment',
            'price_targets': 'Track target changes'
        }

    def get_sector_specific_events(self, symbol):
        """Get sector-specific events that might affect the stock"""
        # This would be enhanced with sector-specific news and events
        return {
            'regulatory_changes': 'Monitor for sector regulations',
            'commodity_prices': 'Track relevant commodity impacts',
            'seasonal_factors': 'Consider seasonal trading patterns'
        }

    def comprehensive_market_analysis(self, symbol=None):
        """Complete market context analysis"""
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'sector_analysis': self.analyze_sector_performance(),
            'market_internals': self.get_market_internals(),
            'economic_calendar': self.get_economic_calendar(),
            'overall_market_sentiment': None
        }
        
        if symbol:
            analysis['stock_specific_catalysts'] = self.analyze_stock_specific_catalysts(symbol)
        
        # Determine overall market sentiment
        analysis['overall_market_sentiment'] = self.determine_market_sentiment(analysis)
        
        return analysis

    def determine_market_sentiment(self, analysis):
        """Determine overall market sentiment from all factors"""
        sentiment_score = 0
        
        # Sector rotation analysis
        rotation = analysis.get('sector_analysis', {}).get('market_rotation_analysis', '')
        if 'Risk-On' in rotation:
            sentiment_score += 2
        elif 'Risk-Off' in rotation:
            sentiment_score -= 2
        
        # VIX sentiment
        vix_sentiment = analysis.get('market_internals', {}).get('vix_sentiment', {})
        vix_level = vix_sentiment.get('level', 'Unknown')
        if vix_level in ['Very Low', 'Low']:
            sentiment_score += 1
        elif vix_level in ['High', 'Very High']:
            sentiment_score -= 2
        
        # Market breadth
        breadth = analysis.get('market_internals', {}).get('market_breadth_summary', '')
        if 'Strength' in breadth:
            sentiment_score += 1
        elif 'Weakness' in breadth:
            sentiment_score -= 1
        
        # Determine overall sentiment
        if sentiment_score >= 3:
            return 'Very Bullish'
        elif sentiment_score >= 1:
            return 'Bullish'
        elif sentiment_score <= -3:
            return 'Very Bearish'
        elif sentiment_score <= -1:
            return 'Bearish'
        else:
            return 'Neutral'

class EnhancedEntryChecklist:
    """
    Enhanced Entry Criteria Checklist
    Comprehensive validation before trade entry
    """
    
    def __init__(self):
        self.minimum_score = 70  # Minimum score for trade consideration
        self.required_rr_ratio = 2.0  # Minimum risk/reward ratio
    
    def validate_entry_setup(self, technical_analysis, market_context, entry_price, stop_loss, target):
        """Comprehensive entry validation"""
        
        checklist = {
            'technical_score': 0,
            'market_context_score': 0,
            'risk_management_score': 0,
            'total_score': 0,
            'validation_results': {},
            'recommendation': None
        }
        
        # Technical Analysis Validation (50 points)
        tech_score = self.validate_technical_setup(technical_analysis)
        checklist['technical_score'] = tech_score
        
        # Market Context Validation (30 points)
        context_score = self.validate_market_context(market_context)
        checklist['market_context_score'] = context_score
        
        # Risk Management Validation (20 points)
        risk_score = self.validate_risk_management(entry_price, stop_loss, target)
        checklist['risk_management_score'] = risk_score
        
        # Calculate total score
        checklist['total_score'] = tech_score + context_score + risk_score
        
        # Generate detailed validation results
        checklist['validation_results'] = self.generate_validation_details(
            technical_analysis, market_context, entry_price, stop_loss, target
        )
        
        # Final recommendation
        checklist['recommendation'] = self.generate_recommendation(checklist)
        
        return checklist
    
    def validate_technical_setup(self, technical_analysis):
        """Validate technical setup components"""
        score = 0
        
        # Setup quality score from technical analysis
        setup_quality = technical_analysis.get('setup_quality_score', 0)
        score += min(setup_quality * 0.3, 30)  # Max 30 points
        
        # Timeframe confluence
        confluence = technical_analysis.get('timeframe_confluence', {})
        confluence_score = confluence.get('confluence_score', 0)
        if confluence_score >= 80:
            score += 10
        elif confluence_score >= 60:
            score += 7
        elif confluence_score >= 40:
            score += 5
        
        # Volume confirmation
        volume_analysis = technical_analysis.get('volume_analysis', {})
        if volume_analysis.get('volume_trend') == 'Above Average':
            score += 10
        elif volume_analysis.get('volume_trend') == 'Normal':
            score += 5
        
        return min(score, 50)
    
    def validate_market_context(self, market_context):
        """Validate market context factors"""
        score = 0
        
        # Overall market sentiment
        sentiment = market_context.get('overall_market_sentiment', 'Neutral')
        if sentiment in ['Very Bullish', 'Bullish']:
            score += 10
        elif sentiment == 'Neutral':
            score += 5
        
        # Sector strength
        sector_analysis = market_context.get('sector_analysis', {})
        rotation = sector_analysis.get('market_rotation_analysis', '')
        if 'Risk-On' in rotation:
            score += 10
        elif 'Neutral' in rotation:
            score += 5
        
        # VIX level appropriateness
        vix_sentiment = market_context.get('market_internals', {}).get('vix_sentiment', {})
        vix_level = vix_sentiment.get('level', 'Unknown')
        if vix_level in ['Low', 'Medium']:
            score += 10
        elif vix_level == 'High':
            score += 5  # High vol can be traded but with caution
        
        return min(score, 30)
    
    def validate_risk_management(self, entry_price, stop_loss, target):
        """Validate risk management parameters"""
        score = 0
        
        if entry_price <= 0 or stop_loss <= 0 or target <= 0:
            return 0
        
        # Calculate R/R ratio
        risk = entry_price - stop_loss
        reward = target - entry_price
        
        if risk > 0:
            rr_ratio = reward / risk
            
            if rr_ratio >= 3:
                score += 20
            elif rr_ratio >= 2:
                score += 15
            elif rr_ratio >= 1.5:
                score += 10
            elif rr_ratio >= 1:
                score += 5
        
        return min(score, 20)
    
    def generate_validation_details(self, technical_analysis, market_context, entry_price, stop_loss, target):
        """Generate detailed validation breakdown"""
        return {
            'strong_points': self.identify_strong_points(technical_analysis, market_context),
            'weak_points': self.identify_weak_points(technical_analysis, market_context),
            'risk_assessment': self.assess_risks(entry_price, stop_loss, target),
            'improvement_suggestions': self.suggest_improvements(technical_analysis, market_context)
        }
    
    def identify_strong_points(self, technical_analysis, market_context):
        """Identify strengths in the setup"""
        strong_points = []
        
        # Technical strengths
        if technical_analysis.get('setup_quality_score', 0) >= 70:
            strong_points.append('High technical setup quality score')
        
        confluence = technical_analysis.get('timeframe_confluence', {})
        if confluence.get('confluence_score', 0) >= 70:
            strong_points.append('Strong multi-timeframe confluence')
        
        # Market context strengths
        sentiment = market_context.get('overall_market_sentiment', 'Neutral')
        if sentiment in ['Very Bullish', 'Bullish']:
            strong_points.append('Supportive market sentiment')
        
        return strong_points
    
    def identify_weak_points(self, technical_analysis, market_context):
        """Identify weaknesses in the setup"""
        weak_points = []
        
        # Technical weaknesses
        if technical_analysis.get('setup_quality_score', 0) < 50:
            weak_points.append('Low technical setup quality score')
        
        # Market context weaknesses
        sentiment = market_context.get('overall_market_sentiment', 'Neutral')
        if sentiment in ['Very Bearish', 'Bearish']:
            weak_points.append('Negative market sentiment')
        
        vix_sentiment = market_context.get('market_internals', {}).get('vix_sentiment', {})
        if vix_sentiment.get('level') in ['Very High', 'High']:
            weak_points.append('High market volatility/fear')
        
        return weak_points
    
    def assess_risks(self, entry_price, stop_loss, target):
        """Assess risk factors"""
        risks = []
        
        if entry_price > 0 and stop_loss > 0:
            risk_percent = ((entry_price - stop_loss) / entry_price) * 100
            if risk_percent > 5:
                risks.append(f'High stop loss risk: {risk_percent:.1f}%')
            
            if target > 0:
                reward = target - entry_price
                risk = entry_price - stop_loss
                if risk > 0:
                    rr_ratio = reward / risk
                    if rr_ratio < 2:
                        risks.append(f'Poor R/R ratio: {rr_ratio:.1f}:1')
        
        return risks
    
    def suggest_improvements(self, technical_analysis, market_context):
        """Suggest improvements to the setup"""
        suggestions = []
        
        if technical_analysis.get('setup_quality_score', 0) < 70:
            suggestions.append('Wait for higher quality technical setup')
        
        confluence = technical_analysis.get('timeframe_confluence', {})
        if confluence.get('confluence_score', 0) < 60:
            suggestions.append('Wait for better timeframe alignment')
        
        volume_analysis = technical_analysis.get('volume_analysis', {})
        if volume_analysis.get('volume_trend') != 'Above Average':
            suggestions.append('Wait for volume confirmation')
        
        return suggestions
    
    def generate_recommendation(self, checklist):
        """Generate final recommendation based on checklist"""
        total_score = checklist['total_score']
        
        if total_score >= 85:
            return {
                'action': 'STRONG BUY',
                'confidence': 'Very High',
                'position_size': 'Full position (within risk limits)',
                'rationale': 'Excellent setup with multiple confirmations'
            }
        elif total_score >= 70:
            return {
                'action': 'BUY',
                'confidence': 'High',
                'position_size': '75% of normal position',
                'rationale': 'Good setup with solid confirmations'
            }
        elif total_score >= 55:
            return {
                'action': 'SCALE IN',
                'confidence': 'Medium',
                'position_size': '50% of normal position',
                'rationale': 'Decent setup, consider partial entry'
            }
        elif total_score >= 40:
            return {
                'action': 'WAIT',
                'confidence': 'Low',
                'position_size': 'No position',
                'rationale': 'Setup needs improvement before entry'
            }
        else:
            return {
                'action': 'AVOID',
                'confidence': 'High',
                'position_size': 'No position',
                'rationale': 'Poor setup quality, avoid entry'
            }
