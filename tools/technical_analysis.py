"""
Technical Analysis Tools for Swing Trading
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict

class TechnicalAnalyzer:
    """
    Technical analysis tools for swing trading strategies
    """
    
    @staticmethod
    def sma(data: pd.Series, window: int) -> pd.Series:
        """Simple Moving Average"""
        return data.rolling(window=window).mean()
    
    @staticmethod
    def ema(data: pd.Series, window: int) -> pd.Series:
        """Exponential Moving Average"""
        return data.ewm(span=window).mean()
    
    @staticmethod
    def rsi(data: pd.Series, window: int = 14) -> pd.Series:
        """Relative Strength Index"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """MACD Indicator"""
        ema_fast = TechnicalAnalyzer.ema(data, fast)
        ema_slow = TechnicalAnalyzer.ema(data, slow)
        macd_line = ema_fast - ema_slow
        signal_line = TechnicalAnalyzer.ema(macd_line, signal)
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    @staticmethod
    def bollinger_bands(data: pd.Series, window: int = 20, std_dev: int = 2) -> Dict[str, pd.Series]:
        """Bollinger Bands"""
        sma = TechnicalAnalyzer.sma(data, window)
        std = data.rolling(window=window).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return {
            'upper': upper_band,
            'middle': sma,
            'lower': lower_band
        }
    
    @staticmethod
    def stochastic(high: pd.Series, low: pd.Series, close: pd.Series, 
                  k_window: int = 14, d_window: int = 3) -> Dict[str, pd.Series]:
        """Stochastic Oscillator"""
        lowest_low = low.rolling(window=k_window).min()
        highest_high = high.rolling(window=k_window).max()
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_window).mean()
        
        return {
            'k': k_percent,
            'd': d_percent
        }
    
    @staticmethod
    def support_resistance(data: pd.Series, window: int = 20) -> Dict[str, float]:
        """Identify support and resistance levels"""
        recent_data = data.tail(window)
        support = recent_data.min()
        resistance = recent_data.max()
        
        return {
            'support': support,
            'resistance': resistance,
            'range': resistance - support
        }

class SwingTradingSignals:
    """
    Generate swing trading signals based on technical analysis
    """
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.analyzer = TechnicalAnalyzer()
    
    def generate_signals(self) -> pd.DataFrame:
        """
        Generate comprehensive swing trading signals
        """
        df = self.data.copy()
        
        # Calculate indicators
        df['SMA_20'] = self.analyzer.sma(df['Close'], 20)
        df['SMA_50'] = self.analyzer.sma(df['Close'], 50)
        df['EMA_12'] = self.analyzer.ema(df['Close'], 12)
        df['RSI'] = self.analyzer.rsi(df['Close'])
        
        # MACD
        macd_data = self.analyzer.macd(df['Close'])
        df['MACD'] = macd_data['macd']
        df['MACD_Signal'] = macd_data['signal']
        
        # Bollinger Bands
        bb_data = self.analyzer.bollinger_bands(df['Close'])
        df['BB_Upper'] = bb_data['upper']
        df['BB_Lower'] = bb_data['lower']
        
        # Generate signals
        df['Signal'] = 0
        df['Signal_Strength'] = 0
        
        # Buy signals
        buy_conditions = [
            (df['Close'] > df['SMA_20']) & (df['SMA_20'] > df['SMA_50']),  # Uptrend
            df['RSI'] < 70,  # Not overbought
            df['MACD'] > df['MACD_Signal'],  # MACD bullish
            df['Close'] > df['BB_Lower']  # Above lower Bollinger Band
        ]
        
        # Sell signals
        sell_conditions = [
            (df['Close'] < df['SMA_20']) & (df['SMA_20'] < df['SMA_50']),  # Downtrend
            df['RSI'] > 30,  # Not oversold
            df['MACD'] < df['MACD_Signal'],  # MACD bearish
            df['Close'] < df['BB_Upper']  # Below upper Bollinger Band
        ]
        
        # Calculate signal strength
        for i, (buy_cond, sell_cond) in enumerate(zip(buy_conditions, sell_conditions)):
            df.loc[buy_cond, 'Signal_Strength'] += 1
            df.loc[sell_cond, 'Signal_Strength'] -= 1
        
        # Set signals based on strength
        df.loc[df['Signal_Strength'] >= 2, 'Signal'] = 1  # Buy
        df.loc[df['Signal_Strength'] <= -2, 'Signal'] = -1  # Sell
        
        return df
