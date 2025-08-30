#!/usr/bin/env python3
"""
Test Comprehensive Market Scanning
Tests the new comprehensive stock list system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.market_stock_lists import get_comprehensive_market_watchlists
from tools.enhanced_signals import get_comprehensive_swing_signals, EnhancedSwingAnalyzer
import time

def test_stock_lists():
    """Test the comprehensive stock list generation"""
    print("🧪 TESTING COMPREHENSIVE STOCK LISTS")
    print("=" * 50)
    
    # Test stock list generation
    watchlists = get_comprehensive_market_watchlists(validate=False)
    
    print(f"📊 STOCK LIST SUMMARY:")
    total_stocks = 0
    for market, stocks in watchlists.items():
        print(f"  🌍 {market.upper()}: {len(stocks)} stocks")
        total_stocks += len(stocks)
        print(f"    Sample: {stocks[:5]}...")
    
    print(f"📈 TOTAL: {total_stocks} stocks across all markets")
    return watchlists

def test_sample_analysis():
    """Test analysis on a small sample of stocks"""
    print("\n🔬 TESTING SAMPLE ANALYSIS")
    print("=" * 50)
    
    analyzer = EnhancedSwingAnalyzer()
    
    # Test a few stocks from each market
    test_stocks = {
        'usa': ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA'],
        'india': ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS'],
        'malaysia': ['1155.KL', '1023.KL', '5225.KL', '6012.KL']
    }
    
    results = {}
    for market, symbols in test_stocks.items():
        print(f"\n🌍 Testing {market.upper()} stocks:")
        market_results = []
        
        for symbol in symbols:
            try:
                result = analyzer.calculate_swing_signals(symbol)
                if result:
                    score = result.get('swing_score', 0)
                    recommendation = result.get('recommendation', 'Unknown')
                    print(f"  ✅ {symbol}: {score}/100 - {recommendation}")
                    market_results.append(result)
                else:
                    print(f"  ❌ {symbol}: No data")
            except Exception as e:
                print(f"  ❌ {symbol}: Error - {str(e)}")
        
        results[market] = market_results
        good_opportunities = [r for r in market_results if r.get('swing_score', 0) >= 70]
        print(f"  🎯 {len(good_opportunities)}/{len(market_results)} good opportunities (70+ score)")
    
    return results

def test_comprehensive_scan_small():
    """Test comprehensive scan on a smaller subset"""
    print("\n🚀 TESTING MINI COMPREHENSIVE SCAN")
    print("=" * 50)
    
    # Create a mini comprehensive scan with just top stocks
    print("⚠️ Running mini scan with ~30 stocks to test the system...")
    
    def progress_callback(message, progress):
        print(f"📊 Progress: {progress*100:.1f}% - {message}")
    
    start_time = time.time()
    
    try:
        # This will use the comprehensive scan but with smaller lists
        result = get_comprehensive_swing_signals(
            progress_callback=progress_callback,
            top_n=5
        )
        
        elapsed_time = time.time() - start_time
        
        print(f"\n✅ MINI SCAN COMPLETE in {elapsed_time:.1f} seconds")
        print(f"📊 Markets scanned: {len(result['markets'])}")
        
        total_opportunities = sum(len(market['opportunities']) for market in result['markets'].values())
        print(f"🎯 Total opportunities found: {total_opportunities}")
        
        for market, data in result['markets'].items():
            print(f"  🌍 {data['name']}: {len(data['opportunities'])} opportunities from {data['total_scanned']} stocks")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in comprehensive scan: {e}")
        return None

if __name__ == "__main__":
    print("🧪 COMPREHENSIVE MARKET SCANNING TEST")
    print("=" * 60)
    
    # Test 1: Stock list generation
    watchlists = test_stock_lists()
    
    # Test 2: Sample analysis
    analysis_results = test_sample_analysis()
    
    # Test 3: Mini comprehensive scan
    scan_result = test_comprehensive_scan_small()
    
    print("\n🎯 TEST SUMMARY:")
    print("=" * 60)
    
    if watchlists:
        total_stocks = sum(len(stocks) for stocks in watchlists.values())
        print(f"✅ Stock lists generated: {total_stocks} total stocks")
    
    if analysis_results:
        total_tested = sum(len(results) for results in analysis_results.values())
        print(f"✅ Analysis tested: {total_tested} stocks analyzed successfully")
    
    if scan_result:
        print(f"✅ Comprehensive scan tested: System working correctly")
        print(f"📊 Ready to scan {sum(len(stocks) for stocks in watchlists.values())} stocks!")
    else:
        print(f"❌ Comprehensive scan failed: Check error messages above")
    
    print(f"\n💡 NEXT STEPS:")
    print(f"1. Run the dashboard: streamlit run dashboard.py")
    print(f"2. Click '🚀 Full Scan' to scan all {sum(len(stocks) for stocks in watchlists.values())} stocks")
    print(f"3. Wait 15-45 minutes for comprehensive results")
    print(f"4. Find many more swing trading opportunities!")
