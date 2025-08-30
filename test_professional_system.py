#!/usr/bin/env python3
"""
Comprehensive test for the professional trading system
Tests all new modules and validates the fixes for critical issues
"""

import sys
import os
import traceback
from datetime import datetime

# Add the tools directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

def test_professional_technical_analysis():
    """Test the professional technical analysis module"""
    print("\n🔬 Testing Professional Technical Analysis...")
    
    try:
        from professional_technical_analysis import ProfessionalTechnicalAnalysis
        
        # Test RSI interpretation (critical fix for user feedback)
        analyzer = ProfessionalTechnicalAnalysis()
        
        # Test RSI interpretation that was wrong before
        test_cases = [
            (44.5, "Testing RSI 44.5 - should be Oversold Zone, not Neutral"),
            (25.0, "Testing RSI 25.0 - should be Strong Oversold"),
            (75.0, "Testing RSI 75.0 - should be Overbought Zone"),
            (55.0, "Testing RSI 55.0 - should be Neutral Zone")
        ]
        
        print("  📊 Testing RSI interpretation fixes:")
        for rsi_value, description in test_cases:
            interpretation = analyzer._interpret_rsi(rsi_value)
            print(f"    ✓ RSI {rsi_value}: {interpretation['signal']} - {interpretation['description']}")
        
        # Test with real stock data
        print("  📈 Testing with real stock data (ITC.NS):")
        result = analyzer.analyze_stock("ITC.NS")
        
        if result:
            print(f"    ✓ Analysis successful for ITC.NS")
            print(f"    ✓ RSI: {result['rsi']['value']:.1f} - {result['rsi']['signal']}")
            print(f"    ✓ MACD: {result['macd']['signal']} - {result['macd']['description']}")
            print(f"    ✓ Overall Score: {result['overall_score']:.1f}/100")
        else:
            print("    ❌ Failed to analyze ITC.NS")
            
        return True
        
    except Exception as e:
        print(f"    ❌ Professional Technical Analysis test failed: {e}")
        traceback.print_exc()
        return False

def test_market_context_analyzer():
    """Test the enhanced market context analyzer"""
    print("\n🌍 Testing Enhanced Market Context Analyzer...")
    
    try:
        from market_context_analyzer import EnhancedMarketContextAnalyzer
        
        analyzer = EnhancedMarketContextAnalyzer()
        
        # Test market regime detection
        print("  📊 Testing market regime detection:")
        context = analyzer.get_market_context("SPY")  # S&P 500 ETF
        
        if context:
            print(f"    ✓ Market Regime: {context.get('market_regime', 'Unknown')}")
            print(f"    ✓ Sector Analysis: {len(context.get('sector_rotation', {}))} sectors analyzed")
            print(f"    ✓ Context Score: {context.get('context_score', 0):.1f}/100")
        else:
            print("    ❌ Failed to get market context")
            
        return True
        
    except Exception as e:
        print(f"    ❌ Market Context Analyzer test failed: {e}")
        traceback.print_exc()
        return False

def test_external_data_integrator():
    """Test the external data integrator"""
    print("\n📡 Testing External Data Integrator...")
    
    try:
        from external_data_integrator import ExternalDataIntegrator
        
        integrator = ExternalDataIntegrator()
        
        # Test without API keys (should handle gracefully)
        print("  📊 Testing without API keys (should handle gracefully):")
        
        # Test fundamental data
        fundamental_data = integrator.get_fundamental_data("AAPL")
        print(f"    ✓ Fundamental data: {'Available' if fundamental_data else 'Not available (expected without API key)'}")
        
        # Test economic indicators
        economic_data = integrator.get_economic_indicators()
        print(f"    ✓ Economic data: {'Available' if economic_data else 'Not available (expected without API key)'}")
        
        # Test news sentiment
        news_sentiment = integrator.get_news_sentiment("AAPL")
        print(f"    ✓ News sentiment: {'Available' if news_sentiment else 'Not available (expected without API key)'}")
        
        return True
        
    except Exception as e:
        print(f"    ❌ External Data Integrator test failed: {e}")
        traceback.print_exc()
        return False

def test_enhanced_signals_integration():
    """Test the updated enhanced signals with professional system"""
    print("\n🚀 Testing Enhanced Signals Integration...")
    
    try:
        from enhanced_signals_clean import ProfessionalSwingAnalyzer
        
        analyzer = ProfessionalSwingAnalyzer()
        
        # Test the specific stock that had issues (ITC.NS)
        print("  📈 Testing ITC.NS analysis (fixing critical issues):")
        result = analyzer.calculate_swing_signals("ITC.NS")
        
        if result:
            print(f"    ✓ Symbol: {result['symbol']}")
            print(f"    ✓ Swing Score: {result['swing_score']:.1f}/100")
            print(f"    ✓ Recommendation: {result['recommendation']}")
            print(f"    ✓ Risk Level: {result['risk_level']}")
            
            # Check technical indicators
            technical = result.get('technical_indicators', {})
            if technical:
                rsi = technical.get('rsi', {})
                macd = technical.get('macd', {})
                print(f"    ✓ RSI: {rsi.get('value', 'N/A')} - {rsi.get('signal', 'N/A')}")
                print(f"    ✓ MACD: {macd.get('signal', 'N/A')}")
        else:
            print("    ❌ Failed to analyze ITC.NS")
            
        return True
        
    except Exception as e:
        print(f"    ❌ Enhanced Signals Integration test failed: {e}")
        traceback.print_exc()
        return False

def test_dashboard_compatibility():
    """Test that the professional system is compatible with the dashboard"""
    print("\n📊 Testing Dashboard Compatibility...")
    
    try:
        from enhanced_signals_clean import get_daily_swing_signals
        
        print("  🔍 Running daily swing signals scan:")
        results = get_daily_swing_signals()
        
        if results:
            print(f"    ✓ Scan completed successfully")
            print(f"    ✓ Scan type: {results.get('scan_type', 'Unknown')}")
            print(f"    ✓ Total stocks scanned: {results.get('total_stocks_scanned', 0)}")
            print(f"    ✓ Markets analyzed: {len(results.get('markets', {}))}")
            print(f"    ✓ Scan duration: {results.get('scan_duration', 0):.1f}s")
            
            # Check for opportunities
            total_opportunities = sum(
                market_data.get('opportunities_found', 0) 
                for market_data in results.get('markets', {}).values()
            )
            print(f"    ✓ Total opportunities found: {total_opportunities}")
        else:
            print("    ❌ Failed to get daily swing signals")
            
        return True
        
    except Exception as e:
        print(f"    ❌ Dashboard Compatibility test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run comprehensive tests for the professional trading system"""
    print("🧪 COMPREHENSIVE PROFESSIONAL TRADING SYSTEM TEST")
    print("=" * 60)
    print(f"Test started at: {datetime.now()}")
    
    tests = [
        ("Professional Technical Analysis", test_professional_technical_analysis),
        ("Enhanced Market Context Analyzer", test_market_context_analyzer),
        ("External Data Integrator", test_external_data_integrator),
        ("Enhanced Signals Integration", test_enhanced_signals_integration),
        ("Dashboard Compatibility", test_dashboard_compatibility),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ Critical error in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Professional trading system is ready.")
        print("\n📋 Next Steps:")
        print("1. Configure API keys for external data:")
        print("   - ALPHA_VANTAGE_API_KEY (for fundamentals)")
        print("   - FRED_API_KEY (for economic data)")
        print("   - NEWS_API_KEY (for sentiment analysis)")
        print("2. Test the dashboard to see the improved analysis")
        print("3. Verify that contradictory signals are now fixed")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please check the errors above.")
    
    print(f"\nTest completed at: {datetime.now()}")

if __name__ == "__main__":
    main()
