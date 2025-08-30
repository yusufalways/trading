"""
Advanced Technical Analysis Module
Addresses critical gaps identified in swing trading analysis
"""

import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import talib

class AdvancedTechnicalAnalysis:
    def __init__(self, symbol, period="1y"):
        self.symbol = symbol
        self.period = period
        self.data = None
        self.multi_timeframe_data = {}
        
    def fetch_multi_timeframe_data(self):
        """Fetch data for multiple timeframes"""
        timeframes = {
            'daily': '1d',
            'weekly': '1wk', 
            'hourly_4': '1h'  # We'll resample to 4h
        }
        
        for tf_name, interval in timeframes.items():
            try:
                if tf_name == 'hourly_4':
                    # Get hourly data and resample to 4H
                    ticker = yf.Ticker(self.symbol)
                    data = ticker.history(period="3mo", interval="1h")
                    # Resample to 4H
                    data_4h = data.resample('4H').agg({
                        'Open': 'first',
                        'High': 'max',
                        'Low': 'min',
                        'Close': 'last',
                        'Volume': 'sum'
                    }).dropna()
                    self.multi_timeframe_data[tf_name] = data_4h
                else:
                    ticker = yf.Ticker(self.symbol)
                    self.multi_timeframe_data[tf_name] = ticker.history(
                        period=self.period, interval=interval
                    )
            except Exception as e:
                print(f"Error fetching {tf_name} data: {e}")
        
        # Set primary data as daily
        self.data = self.multi_timeframe_data.get('daily')
        return self.multi_timeframe_data

    def volume_profile_analysis(self, lookback_days=50):
        """
        1. Volume Profile Analysis
        Analyze volume at different price levels
        """
        if self.data is None or len(self.data) < lookback_days:
            return {}
        
        recent_data = self.data.tail(lookback_days)
        
        # Create price bins
        price_range = recent_data['High'].max() - recent_data['Low'].min()
        bin_size = price_range / 20  # 20 price levels
        price_bins = np.arange(recent_data['Low'].min(), 
                              recent_data['High'].max() + bin_size, 
                              bin_size)
        
        # Calculate volume for each price level
        volume_profile = []
        for i in range(len(price_bins) - 1):
            level_volume = 0
            price_low = price_bins[i]
            price_high = price_bins[i + 1]
            
            for idx, row in recent_data.iterrows():
                # If price level overlaps with candle range
                if price_low <= row['High'] and price_high >= row['Low']:
                    # Distribute volume proportionally
                    overlap = min(price_high, row['High']) - max(price_low, row['Low'])
                    candle_range = row['High'] - row['Low']
                    if candle_range > 0:
                        level_volume += row['Volume'] * (overlap / candle_range)
            
            volume_profile.append({
                'price_level': (price_low + price_high) / 2,
                'volume': level_volume,
                'price_range': f"{price_low:.2f}-{price_high:.2f}"
            })
        
        # Find Point of Control (POC) - highest volume level
        poc = max(volume_profile, key=lambda x: x['volume'])
        
        # Volume analysis
        recent_volume_avg = recent_data['Volume'].rolling(20).mean().iloc[-1]
        latest_volume = recent_data['Volume'].iloc[-1]
        volume_ratio = latest_volume / recent_volume_avg if recent_volume_avg > 0 else 1
        
        return {
            'volume_profile': volume_profile,
            'poc_price': poc['price_level'],
            'poc_volume': poc['volume'],
            'volume_ratio': volume_ratio,
            'volume_trend': 'Above Average' if volume_ratio > 1.2 else 'Below Average' if volume_ratio < 0.8 else 'Normal',
            'accumulation_distribution': self.calculate_accumulation_distribution()
        }

    def calculate_accumulation_distribution(self):
        """Calculate Accumulation/Distribution Line"""
        if self.data is None or len(self.data) < 20:
            return 0
        
        recent_data = self.data.tail(20)
        ad_line = 0
        
        for idx, row in recent_data.iterrows():
            if row['High'] != row['Low']:
                money_flow_multiplier = ((row['Close'] - row['Low']) - (row['High'] - row['Close'])) / (row['High'] - row['Low'])
                money_flow_volume = money_flow_multiplier * row['Volume']
                ad_line += money_flow_volume
        
        return ad_line

    def identify_price_patterns(self):
        """
        2. Price Action Pattern Recognition
        Identify key patterns for swing trading
        """
        if self.data is None or len(self.data) < 50:
            return {}
        
        patterns = {}
        recent_data = self.data.tail(50)
        
        # Pattern detection
        patterns.update(self.detect_double_bottom())
        patterns.update(self.detect_head_and_shoulders())
        patterns.update(self.detect_triangles())
        patterns.update(self.detect_flags_pennants())
        
        return patterns

    def detect_double_bottom(self):
        """Detect double bottom pattern"""
        if len(self.data) < 30:
            return {'double_bottom': False}
        
        recent_lows = self.data['Low'].rolling(5).min()
        potential_bottoms = []
        
        # Find local minimums
        for i in range(5, len(recent_lows) - 5):
            if (recent_lows.iloc[i] <= recent_lows.iloc[i-5:i].min() and 
                recent_lows.iloc[i] <= recent_lows.iloc[i+1:i+6].min()):
                potential_bottoms.append({
                    'index': i,
                    'price': recent_lows.iloc[i],
                    'date': recent_lows.index[i]
                })
        
        # Check for double bottom pattern
        if len(potential_bottoms) >= 2:
            last_two = potential_bottoms[-2:]
            price_diff = abs(last_two[0]['price'] - last_two[1]['price'])
            price_tolerance = last_two[0]['price'] * 0.02  # 2% tolerance
            
            if price_diff <= price_tolerance:
                return {
                    'double_bottom': True,
                    'first_bottom': last_two[0],
                    'second_bottom': last_two[1],
                    'pattern_strength': 'Strong' if price_diff <= price_tolerance * 0.5 else 'Moderate'
                }
        
        return {'double_bottom': False}

    def detect_head_and_shoulders(self):
        """Detect head and shoulders / inverse head and shoulders"""
        # Simplified implementation - would need more sophisticated logic
        return {'head_and_shoulders': False, 'inverse_head_and_shoulders': False}

    def detect_triangles(self):
        """Detect triangle patterns"""
        # Simplified implementation
        return {'ascending_triangle': False, 'descending_triangle': False}

    def detect_flags_pennants(self):
        """Detect flag and pennant patterns"""
        # Simplified implementation
        return {'bull_flag': False, 'bear_flag': False}

    def timeframe_confluence_analysis(self):
        """
        3. Multiple Timeframe Analysis
        Check alignment across different timeframes
        """
        if not self.multi_timeframe_data:
            self.fetch_multi_timeframe_data()
        
        confluence = {}
        
        for tf_name, data in self.multi_timeframe_data.items():
            if data is None or len(data) < 20:
                continue
                
            # Calculate trend indicators for each timeframe
            data['MA20'] = data['Close'].rolling(20).mean()
            data['MA50'] = data['Close'].rolling(50).mean() if len(data) >= 50 else data['Close'].rolling(20).mean()
            
            latest = data.iloc[-1]
            trend = 'Bullish' if latest['Close'] > latest['MA20'] > latest['MA50'] else 'Bearish'
            
            # RSI
            rsi = talib.RSI(data['Close'].values, timeperiod=14)
            current_rsi = rsi[-1] if len(rsi) > 0 else 50
            
            confluence[tf_name] = {
                'trend': trend,
                'price_vs_ma20': 'Above' if latest['Close'] > latest['MA20'] else 'Below',
                'ma20_vs_ma50': 'Above' if latest['MA20'] > latest['MA50'] else 'Below',
                'rsi': current_rsi,
                'rsi_condition': 'Oversold' if current_rsi < 30 else 'Overbought' if current_rsi > 70 else 'Neutral'
            }
        
        # Calculate confluence score
        bullish_signals = sum(1 for tf in confluence.values() if tf['trend'] == 'Bullish')
        total_timeframes = len(confluence)
        confluence_score = (bullish_signals / total_timeframes * 100) if total_timeframes > 0 else 0
        
        return {
            'timeframes': confluence,
            'confluence_score': confluence_score,
            'alignment': 'Strong Bullish' if confluence_score >= 80 else 
                        'Weak Bullish' if confluence_score >= 60 else
                        'Neutral' if confluence_score >= 40 else
                        'Weak Bearish' if confluence_score >= 20 else 'Strong Bearish'
        }

    def market_structure_analysis(self):
        """
        4. Market Structure Analysis
        Identify swing points and trend structure
        """
        if self.data is None or len(self.data) < 20:
            return {}
        
        # Identify swing highs and lows
        swing_highs = []
        swing_lows = []
        
        lookback = 5
        for i in range(lookback, len(self.data) - lookback):
            # Swing High
            if (self.data['High'].iloc[i] > self.data['High'].iloc[i-lookback:i].max() and
                self.data['High'].iloc[i] > self.data['High'].iloc[i+1:i+lookback+1].max()):
                swing_highs.append({
                    'date': self.data.index[i],
                    'price': self.data['High'].iloc[i],
                    'index': i
                })
            
            # Swing Low
            if (self.data['Low'].iloc[i] < self.data['Low'].iloc[i-lookback:i].min() and
                self.data['Low'].iloc[i] < self.data['Low'].iloc[i+1:i+lookback+1].min()):
                swing_lows.append({
                    'date': self.data.index[i],
                    'price': self.data['Low'].iloc[i],
                    'index': i
                })
        
        # Analyze trend structure
        trend_structure = self.analyze_trend_structure(swing_highs, swing_lows)
        
        return {
            'swing_highs': swing_highs[-5:],  # Last 5 swing highs
            'swing_lows': swing_lows[-5:],    # Last 5 swing lows
            'trend_structure': trend_structure,
            'current_phase': self.determine_market_phase()
        }

    def analyze_trend_structure(self, swing_highs, swing_lows):
        """Analyze if we have higher highs/higher lows or lower highs/lower lows"""
        if len(swing_highs) < 2 or len(swing_lows) < 2:
            return 'Insufficient data'
        
        # Check last two swing points
        recent_highs = swing_highs[-2:]
        recent_lows = swing_lows[-2:]
        
        higher_highs = recent_highs[-1]['price'] > recent_highs[-2]['price']
        higher_lows = recent_lows[-1]['price'] > recent_lows[-2]['price']
        
        if higher_highs and higher_lows:
            return 'Uptrend (HH, HL)'
        elif not higher_highs and not higher_lows:
            return 'Downtrend (LH, LL)'
        else:
            return 'Sideways/Consolidation'

    def determine_market_phase(self):
        """Determine current market phase"""
        if self.data is None or len(self.data) < 50:
            return 'Unknown'
        
        # Simple phase determination based on price action and volume
        recent_data = self.data.tail(20)
        price_trend = (recent_data['Close'].iloc[-1] - recent_data['Close'].iloc[0]) / recent_data['Close'].iloc[0]
        volume_trend = recent_data['Volume'].rolling(10).mean().iloc[-1] / recent_data['Volume'].rolling(10).mean().iloc[-10]
        
        if price_trend > 0.05 and volume_trend > 1.1:
            return 'Markup (Trending Up)'
        elif price_trend < -0.05 and volume_trend > 1.1:
            return 'Markdown (Trending Down)'
        elif abs(price_trend) < 0.02:
            return 'Accumulation/Distribution (Sideways)'
        else:
            return 'Transition Phase'

    def momentum_divergence_analysis(self):
        """
        5. Momentum Divergence Analysis
        Identify bullish/bearish divergences
        """
        if self.data is None or len(self.data) < 50:
            return {}
        
        # Calculate RSI and MACD
        rsi = talib.RSI(self.data['Close'].values, timeperiod=14)
        macd, macd_signal, macd_hist = talib.MACD(self.data['Close'].values)
        
        # Find recent swing points in price and indicators
        price_swings = self.find_price_swings(self.data['Close'], 5)
        rsi_swings = self.find_price_swings(pd.Series(rsi), 5)
        macd_swings = self.find_price_swings(pd.Series(macd), 5)
        
        divergences = {
            'rsi_divergence': self.check_divergence(price_swings, rsi_swings),
            'macd_divergence': self.check_divergence(price_swings, macd_swings),
            'hidden_divergences': self.check_hidden_divergences(price_swings, rsi_swings)
        }
        
        return divergences

    def find_price_swings(self, series, lookback=5):
        """Find swing highs and lows in a series"""
        swings = []
        for i in range(lookback, len(series) - lookback):
            # Check for swing high
            if (series.iloc[i] > series.iloc[i-lookback:i].max() and
                series.iloc[i] > series.iloc[i+1:i+lookback+1].max()):
                swings.append({'index': i, 'price': series.iloc[i], 'type': 'high'})
            # Check for swing low
            elif (series.iloc[i] < series.iloc[i-lookback:i].min() and
                  series.iloc[i] < series.iloc[i+1:i+lookback+1].min()):
                swings.append({'index': i, 'price': series.iloc[i], 'type': 'low'})
        return swings

    def check_divergence(self, price_swings, indicator_swings):
        """Check for regular divergences between price and indicator"""
        if len(price_swings) < 2 or len(indicator_swings) < 2:
            return 'No divergence detected'
        
        # Get recent swings of same type
        price_highs = [s for s in price_swings[-4:] if s['type'] == 'high']
        price_lows = [s for s in price_swings[-4:] if s['type'] == 'low']
        indicator_highs = [s for s in indicator_swings[-4:] if s['type'] == 'high']
        indicator_lows = [s for s in indicator_swings[-4:] if s['type'] == 'low']
        
        # Check bullish divergence (price makes lower lows, indicator makes higher lows)
        if len(price_lows) >= 2 and len(indicator_lows) >= 2:
            if (price_lows[-1]['price'] < price_lows[-2]['price'] and
                indicator_lows[-1]['price'] > indicator_lows[-2]['price']):
                return 'Bullish divergence detected'
        
        # Check bearish divergence (price makes higher highs, indicator makes lower highs)
        if len(price_highs) >= 2 and len(indicator_highs) >= 2:
            if (price_highs[-1]['price'] > price_highs[-2]['price'] and
                indicator_highs[-1]['price'] < indicator_highs[-2]['price']):
                return 'Bearish divergence detected'
        
        return 'No significant divergence'

    def check_hidden_divergences(self, price_swings, indicator_swings):
        """Check for hidden divergences (trend continuation signals)"""
        # Simplified implementation
        return 'No hidden divergence analysis available'

    def enhanced_risk_management(self, entry_price, current_price):
        """
        8. Dynamic Risk Management
        ATR-based stops and position sizing
        """
        if self.data is None or len(self.data) < 20:
            return {}
        
        # Calculate ATR
        atr = talib.ATR(self.data['High'].values, self.data['Low'].values, 
                       self.data['Close'].values, timeperiod=14)
        current_atr = atr[-1] if len(atr) > 0 else 0
        
        # ATR-based stop loss
        atr_multiplier = 2.0  # Conservative multiplier
        atr_stop_loss = entry_price - (current_atr * atr_multiplier)
        
        # Calculate position size based on volatility
        account_risk_percent = 2.0  # Risk 2% of account
        risk_per_share = entry_price - atr_stop_loss
        
        # Dynamic targets based on ATR
        target_1 = entry_price + (current_atr * 2)  # 2 ATR target
        target_2 = entry_price + (current_atr * 3)  # 3 ATR target
        
        # Risk/Reward ratios
        rr_ratio_1 = (target_1 - entry_price) / risk_per_share if risk_per_share > 0 else 0
        rr_ratio_2 = (target_2 - entry_price) / risk_per_share if risk_per_share > 0 else 0
        
        return {
            'atr': current_atr,
            'atr_stop_loss': atr_stop_loss,
            'dynamic_targets': {
                'target_1': target_1,
                'target_2': target_2
            },
            'risk_reward_ratios': {
                'target_1_rr': rr_ratio_1,
                'target_2_rr': rr_ratio_2
            },
            'recommended_position_size': self.calculate_position_size(risk_per_share, account_risk_percent),
            'trailing_stop_strategy': self.get_trailing_stop_strategy(current_atr)
        }

    def calculate_position_size(self, risk_per_share, account_risk_percent, account_value=10000):
        """Calculate position size based on risk management"""
        if risk_per_share <= 0:
            return 0
        
        max_risk_amount = account_value * (account_risk_percent / 100)
        position_size = int(max_risk_amount / risk_per_share)
        
        return position_size

    def get_trailing_stop_strategy(self, atr):
        """Get trailing stop strategy based on ATR"""
        return {
            'type': 'ATR-based',
            'trail_distance': atr * 1.5,
            'activation_profit': atr * 1.0,
            'description': f'Trail stop by {atr * 1.5:.2f} points after {atr:.2f} profit'
        }

    def comprehensive_entry_analysis(self, entry_price=None):
        """
        Complete analysis combining all factors
        """
        if entry_price is None:
            entry_price = self.data['Close'].iloc[-1] if self.data is not None else 0
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'symbol': self.symbol,
            'entry_price': entry_price,
            'volume_analysis': self.volume_profile_analysis(),
            'pattern_analysis': self.identify_price_patterns(),
            'timeframe_confluence': self.timeframe_confluence_analysis(),
            'market_structure': self.market_structure_analysis(),
            'momentum_divergences': self.momentum_divergence_analysis(),
            'risk_management': self.enhanced_risk_management(entry_price, entry_price)
        }
        
        # Calculate overall setup quality score
        analysis['setup_quality_score'] = self.calculate_setup_score(analysis)
        analysis['entry_recommendation'] = self.get_entry_recommendation(analysis)
        
        return analysis

    def calculate_setup_score(self, analysis):
        """Calculate overall setup quality score (0-100)"""
        score = 0
        
        # Volume analysis (20 points)
        volume_analysis = analysis.get('volume_analysis', {})
        if volume_analysis.get('volume_trend') == 'Above Average':
            score += 15
        elif volume_analysis.get('volume_trend') == 'Normal':
            score += 10
        
        # Pattern analysis (20 points)
        patterns = analysis.get('pattern_analysis', {})
        if patterns.get('double_bottom', False):
            score += 20
        
        # Timeframe confluence (25 points)
        confluence = analysis.get('timeframe_confluence', {})
        confluence_score = confluence.get('confluence_score', 0)
        score += confluence_score * 0.25
        
        # Market structure (15 points)
        structure = analysis.get('market_structure', {})
        if 'Uptrend' in structure.get('trend_structure', ''):
            score += 15
        elif 'Sideways' in structure.get('trend_structure', ''):
            score += 8
        
        # Risk/Reward (20 points)
        risk_mgmt = analysis.get('risk_management', {})
        rr_ratios = risk_mgmt.get('risk_reward_ratios', {})
        best_rr = max(rr_ratios.get('target_1_rr', 0), rr_ratios.get('target_2_rr', 0))
        if best_rr >= 3:
            score += 20
        elif best_rr >= 2:
            score += 15
        elif best_rr >= 1.5:
            score += 10
        
        return min(score, 100)

    def get_entry_recommendation(self, analysis):
        """Get entry recommendation based on analysis"""
        score = analysis.get('setup_quality_score', 0)
        risk_mgmt = analysis.get('risk_management', {})
        best_rr = max(risk_mgmt.get('risk_reward_ratios', {}).get('target_1_rr', 0),
                     risk_mgmt.get('risk_reward_ratios', {}).get('target_2_rr', 0))
        
        if score >= 80 and best_rr >= 2:
            return {
                'action': 'STRONG BUY',
                'confidence': 'High',
                'reasons': ['High setup quality score', 'Excellent risk/reward ratio', 'Multiple confirmations']
            }
        elif score >= 60 and best_rr >= 1.5:
            return {
                'action': 'BUY',
                'confidence': 'Medium',
                'reasons': ['Good setup quality', 'Acceptable risk/reward', 'Some confirmations']
            }
        elif score >= 40:
            return {
                'action': 'WAIT',
                'confidence': 'Low',
                'reasons': ['Average setup quality', 'Wait for better entry', 'Consider scaling in']
            }
        else:
            return {
                'action': 'AVOID',
                'confidence': 'High',
                'reasons': ['Poor setup quality', 'Inadequate risk/reward', 'Multiple negative signals']
            }
