#!/usr/bin/env python3
"""
External Data Integration Module
Integrates free APIs for enhanced market analysis
"""

import requests
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import time

class ExternalDataIntegrator:
    """
    Integrates free APIs to enhance trading analysis
    Addresses missing external data context issue
    """
    
    def __init__(self):
        # Free API endpoints and keys (users need to get their own)
        self.apis = {
            'alpha_vantage': {
                'base_url': 'https://www.alphavantage.co/query',
                'key': None,  # User needs to set: export ALPHA_VANTAGE_API_KEY=your_key
                'rate_limit': 5,  # calls per minute for free tier
                'daily_limit': 500
            },
            'fred': {
                'base_url': 'https://api.stlouisfed.org/fred/series/observations',
                'key': None,  # User needs to set: export FRED_API_KEY=your_key
                'rate_limit': 120,  # calls per minute
                'daily_limit': None  # Unlimited for free
            },
            'newsapi': {
                'base_url': 'https://newsapi.org/v2/everything',
                'key': None,  # User needs to set: export NEWS_API_KEY=your_key
                'rate_limit': 1000,  # requests per day for free tier
                'daily_limit': 1000
            }
        }
        
        # Economic indicators from FRED
        self.economic_indicators = {
            'GDP': 'GDP',
            'Inflation': 'CPIAUCSL',
            'Unemployment': 'UNRATE',
            'Fed Funds Rate': 'FEDFUNDS',
            'Consumer Confidence': 'UMCSENT',
            'Dollar Index': 'DTWEXBGS',
            'Oil Price': 'DCOILWTICO',
            'Gold Price': 'GOLDAMGBD228NLBM'
        }
        
        # Get API keys from environment variables
        import os
        self.apis['alpha_vantage']['key'] = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.apis['fred']['key'] = os.getenv('FRED_API_KEY')
        self.apis['newsapi']['key'] = os.getenv('NEWS_API_KEY')
        
    def check_api_availability(self) -> Dict[str, bool]:
        """Check which APIs are available based on API keys"""
        availability = {}
        for api_name, config in self.apis.items():
            availability[api_name] = config['key'] is not None
        
        return availability
    
    def get_alpha_vantage_fundamentals(self, symbol: str) -> Optional[Dict]:
        """
        Get fundamental data from Alpha Vantage (Free tier: 5 calls/min, 500/day)
        """
        if not self.apis['alpha_vantage']['key']:
            print("⚠️ Alpha Vantage API key not found. Set ALPHA_VANTAGE_API_KEY environment variable")
            return None
        
        try:
            # Company Overview
            params = {
                'function': 'OVERVIEW',
                'symbol': symbol.replace('.NS', '').replace('.KL', ''),  # Remove exchange suffixes
                'apikey': self.apis['alpha_vantage']['key']
            }
            
            response = requests.get(self.apis['alpha_vantage']['base_url'], params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for API limits
                if 'Note' in data:
                    print("⚠️ Alpha Vantage API limit reached")
                    return None
                
                if 'Symbol' in data:
                    return {
                        'symbol': data.get('Symbol'),
                        'name': data.get('Name'),
                        'sector': data.get('Sector'),
                        'industry': data.get('Industry'),
                        'market_cap': self.safe_float(data.get('MarketCapitalization')),
                        'pe_ratio': self.safe_float(data.get('PERatio')),
                        'eps': self.safe_float(data.get('EPS')),
                        'dividend_yield': self.safe_float(data.get('DividendYield')),
                        'price_to_book': self.safe_float(data.get('PriceToBookRatio')),
                        'beta': self.safe_float(data.get('Beta')),
                        '52_week_high': self.safe_float(data.get('52WeekHigh')),
                        '52_week_low': self.safe_float(data.get('52WeekLow')),
                        'analyst_target_price': self.safe_float(data.get('AnalystTargetPrice')),
                        'description': data.get('Description', '')[:200] + '...' if data.get('Description') else ''
                    }
            
            return None
            
        except Exception as e:
            print(f"Error fetching Alpha Vantage data for {symbol}: {e}")
            return None
    
    def get_fundamental_data(self, symbol: str) -> Optional[Dict]:
        """Alias for get_alpha_vantage_fundamentals for compatibility"""
        return self.get_alpha_vantage_fundamentals(symbol)
    
    def get_economic_indicators(self, indicators: List[str] = None) -> Dict[str, Dict]:
        """
        Get economic indicators from FRED API (Free, unlimited)
        """
        if not self.apis['fred']['key']:
            print("⚠️ FRED API key not found. Set FRED_API_KEY environment variable")
            return {}
        
        if indicators is None:
            indicators = ['GDP', 'Inflation', 'Unemployment', 'Fed Funds Rate']
        
        economic_data = {}
        
        for indicator in indicators:
            if indicator in self.economic_indicators:
                try:
                    series_id = self.economic_indicators[indicator]
                    
                    # Get latest data point
                    params = {
                        'series_id': series_id,
                        'api_key': self.apis['fred']['key'],
                        'file_type': 'json',
                        'limit': 12,  # Last 12 observations
                        'sort_order': 'desc'
                    }
                    
                    response = requests.get(self.apis['fred']['base_url'], params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        observations = data.get('observations', [])
                        
                        if observations:
                            # Get latest valid observation
                            latest_value = None
                            latest_date = None
                            
                            for obs in observations:
                                if obs['value'] != '.':  # FRED uses '.' for missing values
                                    latest_value = float(obs['value'])
                                    latest_date = obs['date']
                                    break
                            
                            if latest_value is not None:
                                # Calculate trend (compare with previous value)
                                trend = 'Stable'
                                if len(observations) > 1:
                                    prev_value = None
                                    for obs in observations[1:]:
                                        if obs['value'] != '.':
                                            prev_value = float(obs['value'])
                                            break
                                    
                                    if prev_value:
                                        change = ((latest_value - prev_value) / prev_value) * 100
                                        if change > 1:
                                            trend = 'Rising'
                                        elif change < -1:
                                            trend = 'Falling'
                                
                                economic_data[indicator] = {
                                    'value': latest_value,
                                    'date': latest_date,
                                    'trend': trend,
                                    'series_id': series_id
                                }
                    
                    # Rate limiting for FRED API
                    time.sleep(0.5)  # 120 calls per minute = 0.5 seconds between calls
                    
                except Exception as e:
                    print(f"Error fetching {indicator}: {e}")
                    continue
        
        return economic_data
    
    def get_news_sentiment(self, symbol: str, days: int = 7) -> Optional[Dict]:
        """
        Get news sentiment from NewsAPI (Free tier: 1000 requests/day)
        """
        if not self.apis['newsapi']['key']:
            print("⚠️ NewsAPI key not found. Set NEWS_API_KEY environment variable")
            return None
        
        try:
            # Get company name or use symbol
            company_name = symbol.replace('.NS', '').replace('.KL', '')
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            params = {
                'q': f'{company_name} OR {symbol}',
                'from': start_date.strftime('%Y-%m-%d'),
                'to': end_date.strftime('%Y-%m-%d'),
                'sortBy': 'relevancy',
                'language': 'en',
                'pageSize': 20,
                'apiKey': self.apis['newsapi']['key']
            }
            
            response = requests.get(self.apis['newsapi']['base_url'], params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                if articles:
                    # Simple sentiment analysis based on keywords
                    positive_words = ['buy', 'bullish', 'growth', 'profit', 'earnings beat', 'upgrade', 'strong', 'gains']
                    negative_words = ['sell', 'bearish', 'loss', 'decline', 'downgrade', 'weak', 'falls', 'drops']
                    
                    sentiment_scores = []
                    
                    for article in articles:
                        title = article.get('title', '').lower()
                        description = article.get('description', '').lower()
                        content = f"{title} {description}"
                        
                        positive_count = sum(1 for word in positive_words if word in content)
                        negative_count = sum(1 for word in negative_words if word in content)
                        
                        if positive_count > negative_count:
                            sentiment_scores.append(1)
                        elif negative_count > positive_count:
                            sentiment_scores.append(-1)
                        else:
                            sentiment_scores.append(0)
                    
                    # Calculate overall sentiment
                    if sentiment_scores:
                        avg_sentiment = np.mean(sentiment_scores)
                        total_articles = len(articles)
                        
                        if avg_sentiment > 0.2:
                            sentiment = "Positive"
                        elif avg_sentiment < -0.2:
                            sentiment = "Negative"
                        else:
                            sentiment = "Neutral"
                        
                        return {
                            'sentiment': sentiment,
                            'score': avg_sentiment,
                            'article_count': total_articles,
                            'confidence': 'High' if total_articles >= 10 else 'Medium' if total_articles >= 5 else 'Low',
                            'latest_headlines': [article.get('title') for article in articles[:3]]
                        }
            
            return None
            
        except Exception as e:
            print(f"Error fetching news sentiment for {symbol}: {e}")
            return None
    
    def get_earnings_calendar(self, symbol: str) -> Optional[Dict]:
        """
        Get earnings information (simplified version using Alpha Vantage)
        """
        if not self.apis['alpha_vantage']['key']:
            return None
        
        try:
            params = {
                'function': 'EARNINGS_CALENDAR',
                'symbol': symbol.replace('.NS', '').replace('.KL', ''),
                'horizon': '3month',
                'apikey': self.apis['alpha_vantage']['key']
            }
            
            response = requests.get(self.apis['alpha_vantage']['base_url'], params=params, timeout=10)
            
            if response.status_code == 200:
                # Alpha Vantage returns CSV for earnings calendar
                if 'reportDate' in response.text:
                    lines = response.text.strip().split('\n')
                    if len(lines) > 1:
                        # Parse first earnings date
                        data_line = lines[1].split(',')
                        if len(data_line) >= 2:
                            earnings_date = data_line[1]
                            
                            # Calculate days until earnings
                            try:
                                earnings_dt = datetime.strptime(earnings_date, '%Y-%m-%d')
                                days_until = (earnings_dt - datetime.now()).days
                                
                                return {
                                    'next_earnings_date': earnings_date,
                                    'days_until_earnings': days_until,
                                    'is_earnings_soon': days_until <= 5,
                                    'earnings_risk': 'High' if days_until <= 2 else 'Medium' if days_until <= 7 else 'Low'
                                }
                            except:
                                pass
            
            return None
            
        except Exception as e:
            print(f"Error fetching earnings calendar for {symbol}: {e}")
            return None
    
    def comprehensive_external_analysis(self, symbol: str) -> Dict:
        """
        Comprehensive analysis using all available external data sources
        """
        analysis = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'data_sources': {},
            'risk_factors': [],
            'catalysts': [],
            'external_score': 50  # Neutral base score
        }
        
        # Check API availability
        api_status = self.check_api_availability()
        analysis['api_availability'] = api_status
        
        # Fundamental Analysis
        if api_status['alpha_vantage']:
            fundamentals = self.get_alpha_vantage_fundamentals(symbol)
            if fundamentals:
                analysis['data_sources']['fundamentals'] = fundamentals
                
                # Adjust score based on fundamentals
                if fundamentals.get('pe_ratio'):
                    pe = fundamentals['pe_ratio']
                    if 10 <= pe <= 20:
                        analysis['external_score'] += 10
                    elif pe > 30:
                        analysis['external_score'] -= 5
                        analysis['risk_factors'].append(f"High P/E ratio: {pe}")
                
                if fundamentals.get('beta'):
                    beta = fundamentals['beta']
                    if beta > 1.5:
                        analysis['risk_factors'].append(f"High volatility stock (Beta: {beta})")
                    elif beta < 0.8:
                        analysis['catalysts'].append(f"Defensive stock (Beta: {beta})")
                
                # Earnings information
                earnings_info = self.get_earnings_calendar(symbol)
                if earnings_info:
                    analysis['data_sources']['earnings'] = earnings_info
                    if earnings_info['is_earnings_soon']:
                        analysis['risk_factors'].append(f"Earnings in {earnings_info['days_until_earnings']} days - increased volatility expected")
        
        # Economic Context
        if api_status['fred']:
            economic_data = self.get_economic_indicators(['Fed Funds Rate', 'Inflation', 'Consumer Confidence'])
            if economic_data:
                analysis['data_sources']['economic_indicators'] = economic_data
                
                # Adjust score based on economic environment
                if 'Fed Funds Rate' in economic_data:
                    fed_rate = economic_data['Fed Funds Rate']
                    if fed_rate['trend'] == 'Rising':
                        analysis['external_score'] -= 5
                        analysis['risk_factors'].append("Rising interest rates environment")
                    elif fed_rate['trend'] == 'Falling':
                        analysis['external_score'] += 5
                        analysis['catalysts'].append("Falling interest rates supportive")
        
        # News Sentiment
        if api_status['newsapi']:
            news_sentiment = self.get_news_sentiment(symbol)
            if news_sentiment:
                analysis['data_sources']['news_sentiment'] = news_sentiment
                
                # Adjust score based on sentiment
                if news_sentiment['sentiment'] == 'Positive':
                    analysis['external_score'] += 10
                    analysis['catalysts'].append(f"Positive news sentiment ({news_sentiment['article_count']} articles)")
                elif news_sentiment['sentiment'] == 'Negative':
                    analysis['external_score'] -= 10
                    analysis['risk_factors'].append(f"Negative news sentiment ({news_sentiment['article_count']} articles)")
        
        # Generate recommendations
        analysis['recommendation'] = self.generate_external_recommendation(analysis['external_score'], analysis['risk_factors'], analysis['catalysts'])
        
        return analysis
    
    def generate_external_recommendation(self, score: int, risk_factors: List[str], catalysts: List[str]) -> Dict:
        """Generate recommendation based on external analysis"""
        
        if score >= 70:
            recommendation = "POSITIVE EXTERNAL FACTORS"
            confidence = "High"
        elif score >= 55:
            recommendation = "FAVORABLE EXTERNAL ENVIRONMENT"
            confidence = "Medium"
        elif score >= 45:
            recommendation = "NEUTRAL EXTERNAL FACTORS"
            confidence = "Medium"
        elif score >= 30:
            recommendation = "SOME EXTERNAL HEADWINDS"
            confidence = "Medium"
        else:
            recommendation = "SIGNIFICANT EXTERNAL RISKS"
            confidence = "High"
        
        return {
            'recommendation': recommendation,
            'score': score,
            'confidence': confidence,
            'risk_count': len(risk_factors),
            'catalyst_count': len(catalysts)
        }
    
    def safe_float(self, value: str) -> Optional[float]:
        """Safely convert string to float"""
        try:
            return float(value) if value and value != 'None' else None
        except (ValueError, TypeError):
            return None
