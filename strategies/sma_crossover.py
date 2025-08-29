"""
Simple Moving Average Crossover Strategy
A classic swing trading strategy using SMA crossovers
"""

import pandas as pd
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.technical_analysis import TechnicalAnalyzer

class SMACrossoverStrategy:
    """
    Simple Moving Average Crossover Strategy for Swing Trading
    
    Buy Signal: When fast SMA crosses above slow SMA
    Sell Signal: When fast SMA crosses below slow SMA
    """
    
    def __init__(self, fast_period: int = 20, slow_period: int = 50):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.analyzer = TechnicalAnalyzer()
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on SMA crossover
        """
        df = data.copy()
        
        # Calculate SMAs
        df['SMA_Fast'] = self.analyzer.sma(df['Close'], self.fast_period)
        df['SMA_Slow'] = self.analyzer.sma(df['Close'], self.slow_period)
        
        # Calculate crossovers
        df['SMA_Diff'] = df['SMA_Fast'] - df['SMA_Slow']
        df['Previous_Diff'] = df['SMA_Diff'].shift(1)
        
        # Generate signals
        df['Signal'] = 0
        df['Position'] = 0
        
        # Buy signal: Fast SMA crosses above Slow SMA
        buy_condition = (df['SMA_Diff'] > 0) & (df['Previous_Diff'] <= 0)
        df.loc[buy_condition, 'Signal'] = 1
        
        # Sell signal: Fast SMA crosses below Slow SMA
        sell_condition = (df['SMA_Diff'] < 0) & (df['Previous_Diff'] >= 0)
        df.loc[sell_condition, 'Signal'] = -1
        
        # Calculate position (1 for long, 0 for no position)
        df['Position'] = df['Signal'].replace(to_replace=0, method='ffill').fillna(0)
        df['Position'] = df['Position'].replace(-1, 0)  # Convert sell signals to no position
        
        return df
    
    def calculate_returns(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate strategy returns
        """
        df = data.copy()
        
        # Calculate daily returns
        df['Daily_Return'] = df['Close'].pct_change()
        
        # Calculate strategy returns
        df['Strategy_Return'] = df['Daily_Return'] * df['Position'].shift(1)
        
        # Calculate cumulative returns
        df['Cumulative_Return'] = (1 + df['Daily_Return']).cumprod()
        df['Strategy_Cumulative_Return'] = (1 + df['Strategy_Return']).cumprod()
        
        return df
    
    def backtest(self, data: pd.DataFrame) -> dict:
        """
        Perform backtesting and return performance metrics
        """
        df = self.generate_signals(data)
        df = self.calculate_returns(df)
        
        # Calculate performance metrics
        total_trades = len(df[df['Signal'] != 0])
        buy_trades = len(df[df['Signal'] == 1])
        sell_trades = len(df[df['Signal'] == -1])
        
        # Returns
        total_return = df['Cumulative_Return'].iloc[-1] - 1
        strategy_return = df['Strategy_Cumulative_Return'].iloc[-1] - 1
        
        # Sharpe ratio (assuming 252 trading days)
        strategy_sharpe = df['Strategy_Return'].mean() / df['Strategy_Return'].std() * np.sqrt(252)
        
        # Maximum drawdown
        rolling_max = df['Strategy_Cumulative_Return'].expanding().max()
        drawdown = df['Strategy_Cumulative_Return'] / rolling_max - 1
        max_drawdown = drawdown.min()
        
        results = {
            'strategy_name': f'SMA Crossover ({self.fast_period}/{self.slow_period})',
            'total_trades': total_trades,
            'buy_signals': buy_trades,
            'sell_signals': sell_trades,
            'buy_and_hold_return': total_return,
            'strategy_return': strategy_return,
            'sharpe_ratio': strategy_sharpe,
            'max_drawdown': max_drawdown,
            'data': df
        }
        
        return results
