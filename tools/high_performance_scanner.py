#!/usr/bin/env python3
"""
High-Performance Market Scanner
Optimized for speed using concurrent processing and batch downloads
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import concurrent.futures
import time
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class HighPerformanceScanner:
    """Optimized scanner using concurrent processing and batch downloads"""
    
    def __init__(self, max_workers: int = 10, batch_size: int = 50):
        self.max_workers = max_workers
        self.batch_size = batch_size
        
        # Import unified analyzer
        try:
            from .unified_swing_analyzer import UnifiedSwingAnalyzer
            self.unified_analyzer = UnifiedSwingAnalyzer()
            self.analysis_available = True
        except ImportError:
            print("⚠️ Unified analysis not available")
            self.analysis_available = False
    
    def batch_download_data(self, symbols: List[str], period: str = "1mo") -> Dict[str, pd.DataFrame]:
        """Download data for multiple symbols in batches"""
        all_data = {}
        
        # Split symbols into batches
        for i in range(0, len(symbols), self.batch_size):
            batch_symbols = symbols[i:i + self.batch_size]
            
            try:
                # Use batch download
                batch_str = " ".join(batch_symbols)
                print(f"📦 Downloading batch {i//self.batch_size + 1}: {len(batch_symbols)} symbols")
                
                data = yf.download(
                    batch_str, 
                    period=period, 
                    group_by='ticker',
                    threads=True,
                    progress=False
                )
                
                # Extract individual DataFrames
                if len(batch_symbols) == 1:
                    # Single symbol case
                    all_data[batch_symbols[0]] = data
                else:
                    # Multiple symbols case
                    for symbol in batch_symbols:
                        try:
                            if symbol in data.columns.levels[0]:
                                symbol_data = data[symbol].dropna()
                                if not symbol_data.empty:
                                    all_data[symbol] = symbol_data
                        except (KeyError, AttributeError):
                            # Symbol not found in batch
                            continue
                
                # Small delay between batches to avoid rate limiting
                time.sleep(0.2)
                
            except Exception as e:
                print(f"❌ Batch download failed: {e}")
                # Fallback to individual downloads for this batch
                for symbol in batch_symbols:
                    try:
                        ticker = yf.Ticker(symbol)
                        symbol_data = ticker.history(period=period)
                        if not symbol_data.empty:
                            all_data[symbol] = symbol_data
                        time.sleep(0.1)  # Rate limiting
                    except Exception:
                        continue
        
        return all_data
    
    def calculate_quick_score(self, data: pd.DataFrame, symbol: str) -> Optional[Dict]:
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
            price_change_20d = (current_price / data['Close'].iloc[-21] - 1) * 100 if len(data) >= 21 else 0
            
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
                'price_change_20d': price_change_20d,
                'signals': [
                    f"RSI: {current_rsi:.1f}",
                    f"Volume: {volume_ratio:.1f}x avg",
                    f"5d change: {price_change_5d:.1f}%"
                ],
                'market_name': self._get_market_name(symbol)
            }
            
        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {e}")
            return None
    
    def _get_market_name(self, symbol: str) -> str:
        """Determine market name from symbol"""
        if symbol.endswith('.NS') or symbol.endswith('.BO'):
            return "🇮🇳 India"
        elif symbol.endswith('.KL'):
            return "🇲🇾 Malaysia"
        else:
            return "🇺🇸 USA"
    
    def concurrent_analysis(self, symbol_data_pairs: List[Tuple[str, pd.DataFrame]], 
                          progress_callback=None) -> List[Dict]:
        """Analyze multiple symbols concurrently"""
        
        def analyze_single(pair):
            symbol, data = pair
            return self.calculate_quick_score(data, symbol)
        
        results = []
        total_pairs = len(symbol_data_pairs)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_symbol = {
                executor.submit(analyze_single, pair): pair[0] 
                for pair in symbol_data_pairs
            }
            
            # Collect results as they complete
            for i, future in enumerate(concurrent.futures.as_completed(future_to_symbol)):
                symbol = future_to_symbol[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                    
                    # Update progress
                    if progress_callback and i % 10 == 0:
                        progress = (i + 1) / total_pairs
                        progress_callback(f"Analyzing: {symbol} ({i+1}/{total_pairs})", progress)
                        
                except Exception as e:
                    print(f"❌ Analysis failed for {symbol}: {e}")
        
        return results
    
    def fast_market_scan(self, symbols: List[str], market_name: str, 
                        progress_callback=None, top_n: int = 15) -> Dict:
        """High-performance market scan"""
        
        print(f"🚀 Fast scanning {market_name} - {len(symbols)} symbols")
        start_time = time.time()
        
        # Step 1: Batch download all data
        if progress_callback:
            progress_callback(f"Downloading {market_name} data...", 0.1)
        
        all_data = self.batch_download_data(symbols, period="1mo")
        download_time = time.time() - start_time
        
        print(f"📦 Downloaded {len(all_data)}/{len(symbols)} symbols in {download_time:.1f}s")
        
        # Step 2: Concurrent analysis
        if progress_callback:
            progress_callback(f"Analyzing {market_name} symbols...", 0.3)
        
        symbol_data_pairs = list(all_data.items())
        analysis_start = time.time()
        
        results = self.concurrent_analysis(symbol_data_pairs, progress_callback)
        analysis_time = time.time() - analysis_start
        
        # Step 3: Sort and filter results
        results.sort(key=lambda x: x.get('swing_score', 0), reverse=True)
        top_opportunities = results[:top_n]
        
        total_time = time.time() - start_time
        
        return {
            'name': market_name,
            'opportunities': top_opportunities,
            'total_scanned': len(symbols),
            'total_downloaded': len(all_data),
            'opportunities_found': len(results),
            'top_displayed': len(top_opportunities),
            'download_time': download_time,
            'analysis_time': analysis_time,
            'total_time': total_time,
            'avg_time_per_stock': total_time / len(symbols) if symbols else 0
        }

def get_ultra_fast_swing_signals(progress_callback=None, top_n: int = 15) -> Dict:
    """Ultra-fast comprehensive market scan using optimized algorithms"""
    
    print("⚡ ULTRA-FAST MARKET SCAN STARTING...")
    print("🎯 Using optimized batch downloads + concurrent processing")
    
    # Get comprehensive stock lists
    try:
        from .market_stock_lists import get_comprehensive_market_watchlists
        watchlists = get_comprehensive_market_watchlists(validate=False)
    except ImportError:
        from .enhanced_signals import get_market_watchlists
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
        
        # Scan this market
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

if __name__ == "__main__":
    # Test the ultra-fast scanner
    def test_progress(message, progress):
        print(f"Progress: {progress*100:.1f}% - {message}")
    
    result = get_ultra_fast_swing_signals(progress_callback=test_progress, top_n=10)
    
    print("\n🎯 TOP OPPORTUNITIES FOUND:")
    for market, data in result['markets'].items():
        print(f"\n{data['name']}:")
        for opp in data['opportunities'][:3]:  # Show top 3
            print(f"  🟢 {opp['symbol']}: {opp['swing_score']}/100 - {opp['recommendation']}")
