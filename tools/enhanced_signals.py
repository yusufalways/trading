#!/usr/bin/env python3
"""
Enhanced Daily Signals - CLEAN VERSION
Ultra-fast batch processing only - no fallback methods
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
from typing import Dict, List, Optional
import logging
import time

# Import unified analysis system
try:
    from .unified_swing_analyzer import UnifiedSwingAnalyzer
    UNIFIED_ANALYSIS_AVAILABLE = True
except ImportError:
    print("Unified analysis not available - using basic analysis")
    UNIFIED_ANALYSIS_AVAILABLE = False

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
            return self.unified_analyzer.analyze_symbol(symbol, period)
        else:
            # Basic fallback analysis
            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(period=period, interval="1d")
                
                if df.empty or len(df) < 20:
                    return None
                
                current_price = df['Close'].iloc[-1]
                
                # Basic technical indicators
                sma_20 = df['Close'].rolling(20).mean().iloc[-1]
                sma_50 = df['Close'].rolling(50).mean().iloc[-1] if len(df) >= 50 else sma_20
                
                # Simple scoring
                score = 50
                if current_price > sma_20 > sma_50:
                    score += 20
                elif current_price > sma_20:
                    score += 10
                
                # Volume check
                avg_volume = df['Volume'].rolling(20).mean().iloc[-1]
                current_volume = df['Volume'].iloc[-1]
                if current_volume > avg_volume * 1.5:
                    score += 10
                
                # Simple momentum
                price_change = (current_price / df['Close'].iloc[-6] - 1) * 100 if len(df) >= 6 else 0
                if 2 <= price_change <= 8:
                    score += 15
                
                recommendation = "STRONG BUY" if score >= 75 else "BUY" if score >= 65 else "WEAK BUY" if score >= 55 else "HOLD"
                
                market_name = "🇮🇳 India" if symbol.endswith('.NS') or symbol.endswith('.BO') else "🇲🇾 Malaysia" if symbol.endswith('.KL') else "🇺🇸 USA"
                
                return {
                    'symbol': symbol,
                    'current_price': current_price,
                    'swing_score': max(0, min(100, score)),
                    'recommendation': recommendation,
                    'entry_type': "Swing Entry",
                    'risk_reward': f"{2.0:.1f}:1",  # Default risk/reward ratio
                    'market_name': market_name,
                    'signals': [f"Price: ${current_price:.2f}", f"Score: {score}/100"]
                }
                
            except Exception as e:
                print(f"Error analyzing {symbol}: {e}")
                return None

@st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes
def get_daily_swing_signals() -> Dict:
    """Get daily swing trading signals with caching"""
    return _get_swing_signals_internal()

def _get_swing_signals_internal() -> Dict:
    """Internal function to get swing signals"""
    print("🔍 Quick scanning ~73 major stocks across markets...")
    
    analyzer = EnhancedSwingAnalyzer()
    
    # Basic market watchlists
    watchlists = get_market_watchlists()
    
    results = {
        'timestamp': datetime.now(),
        'scan_type': 'QUICK',
        'markets': {},
        'total_stocks_scanned': sum(len(symbols) for symbols in watchlists.values()),
        'scan_duration': None
    }
    
    start_time = time.time()
    
    for market, symbols in watchlists.items():
        market_name = "🇺🇸 USA" if market == 'usa' else "🇮🇳 India" if market == 'india' else "🇲🇾 Malaysia"
        
        print(f"📊 Analyzing {market_name}: {len(symbols)} stocks")
        market_start = time.time()
        opportunities = []
        
        for symbol in symbols:
            try:
                result = analyzer.calculate_swing_signals(symbol)
                if result and result.get('swing_score', 0) >= 60:
                    opportunities.append(result)
            except Exception as e:
                print(f"❌ Error analyzing {symbol}: {e}")
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
