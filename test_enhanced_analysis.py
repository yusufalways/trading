#!/usr/bin/env python3
"""
Test Enhanced Analysis Integration
Verify that all advanced features are working correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.enhanced_signals import EnhancedSwingAnalyzer, get_daily_swing_signals
from tools.advanced_technical_analysis import AdvancedTechnicalAnalysis
from tools.market_context_analyzer import MarketContextAnalyzer, EnhancedEntryChecklist

def test_enhanced_signals():
    """Test the enhanced signals with advanced analysis"""
    print("🧪 Testing Enhanced Signals Integration...")
    print("=" * 60)
    
    analyzer = EnhancedSwingAnalyzer()
    
    # Test with AAPL
    print("📊 Analyzing AAPL with enhanced features...")
    result = analyzer.calculate_swing_signals('AAPL')
    
    if result:
        print(f"✅ Symbol: {result['symbol']}")
        print(f"📈 Current Price: ${result['current_price']:.2f}")
        print(f"🎯 Swing Score: {result['swing_score']}/100")
        print(f"💡 Recommendation: {result['recommendation']}")
        print(f"📝 Entry Type: {result['entry_type']}")
        print(f"⚖️ Risk/Reward: {result['risk_reward']}")
        
        print("\n🔍 Signals:")
        for signal in result['signals']:
            print(f"  • {signal}")
        
        # Check if advanced analysis is available
        advanced_data = result.get('advanced_analysis', {})
        if advanced_data.get('advanced_available', False):
            print("\n🔬 Advanced Analysis:")
            setup_quality = advanced_data.get('setup_quality_score', 0)
            print(f"  • Setup Quality Score: {setup_quality}/100")
            
            confluence = advanced_data.get('confluence_data', {})
            confluence_score = confluence.get('confluence_score', 0)
            print(f"  • Multi-Timeframe Confluence: {confluence_score}%")
            
            volume_analysis = advanced_data.get('volume_profile', {})
            volume_trend = volume_analysis.get('volume_trend', 'Unknown')
            print(f"  • Volume Profile: {volume_trend}")
            
            patterns = advanced_data.get('pattern_analysis', {})
            if patterns.get('double_bottom', False):
                print("  • 🎯 Double Bottom Pattern Detected!")
        else:
            print("\n⚠️ Advanced analysis not available (install TA-Lib for full features)")
        
        print(f"\n📊 Enhanced Features Available:")
        print(f"  • Support Levels: {len(result.get('support_levels', []))} levels")
        print(f"  • Resistance Levels: {len(result.get('resistance_levels', []))} levels")
        print(f"  • Volume Trend: {result.get('volume_trend', 'N/A')}")
        print(f"  • Trend Strength: {result.get('trend_strength', 'N/A')}")
        print(f"  • Market: {result.get('market_name', 'N/A')}")
        
    else:
        print("❌ Failed to analyze AAPL")
    
    print("\n" + "=" * 60)

def test_full_scanning():
    """Test the full scanning system"""
    print("🔍 Testing Full Market Scanning...")
    print("=" * 60)
    
    try:
        results = get_daily_swing_signals()
        
        print(f"📅 Scan Timestamp: {results['timestamp']}")
        print(f"🌍 Markets Scanned: {len(results['markets'])}")
        
        total_opportunities = 0
        
        for market, data in results['markets'].items():
            market_name = data['name']
            opportunities = data['opportunities']
            scanned = data['total_scanned']
            found = data['opportunities_found']
            
            print(f"\n{market_name}:")
            print(f"  📊 Scanned: {scanned} stocks")
            print(f"  🎯 Opportunities: {found} found")
            
            total_opportunities += found
            
            # Show top 2 opportunities
            for i, opp in enumerate(opportunities[:2]):
                symbol = opp['symbol']
                score = opp['swing_score']
                recommendation = opp['recommendation']
                entry_type = opp['entry_type']
                price = opp['current_price']
                
                # Currency symbol
                if '.NS' in symbol:
                    currency = "₹"
                elif '.KL' in symbol:
                    currency = "RM"
                else:
                    currency = "$"
                
                print(f"    {i+1}. {symbol}: {currency}{price:.2f} | Score: {score}/100 | {recommendation} | {entry_type}")
        
        print(f"\n📈 Total Opportunities Found: {total_opportunities}")
        
        if total_opportunities > 0:
            print("✅ Market scanning is working correctly!")
        else:
            print("⚠️ No opportunities found - this could be normal in certain market conditions")
            
    except Exception as e:
        print(f"❌ Scanning failed: {e}")
    
    print("\n" + "=" * 60)

def test_advanced_modules():
    """Test individual advanced analysis modules"""
    print("🔬 Testing Advanced Analysis Modules...")
    print("=" * 60)
    
    try:
        # Test Advanced Technical Analysis
        print("1. Advanced Technical Analysis:")
        analyzer = AdvancedTechnicalAnalysis('AAPL')
        analysis = analyzer.comprehensive_entry_analysis(150.0)
        
        setup_score = analysis.get('setup_quality_score', 0)
        recommendation = analysis.get('entry_recommendation', {})
        print(f"   ✅ Setup Quality Score: {setup_score}/100")
        print(f"   ✅ Recommendation: {recommendation.get('action', 'N/A')}")
        
        # Test Market Context Analyzer
        print("\n2. Market Context Analysis:")
        market_analyzer = MarketContextAnalyzer()
        market_context = market_analyzer.comprehensive_market_analysis('AAPL')
        
        sentiment = market_context.get('overall_market_sentiment', 'Unknown')
        print(f"   ✅ Market Sentiment: {sentiment}")
        
        # Test Enhanced Entry Checklist
        print("\n3. Enhanced Entry Checklist:")
        entry_checker = EnhancedEntryChecklist()
        validation = entry_checker.validate_entry_setup(
            analysis, market_context, 150.0, 145.0, 160.0
        )
        
        total_score = validation.get('total_score', 0)
        final_recommendation = validation.get('recommendation', {})
        print(f"   ✅ Validation Score: {total_score}/100")
        print(f"   ✅ Final Action: {final_recommendation.get('action', 'N/A')}")
        
        print("\n🎉 All advanced modules working correctly!")
        
    except ImportError as e:
        print(f"⚠️ Advanced modules not available: {e}")
        print("💡 Install TA-Lib and other dependencies for full features")
        
    except Exception as e:
        print(f"❌ Advanced analysis error: {e}")
    
    print("\n" + "=" * 60)

def main():
    """Run all tests"""
    print("🚀 Enhanced Trading Analysis - Integration Test")
    print("=" * 60)
    
    # Test 1: Enhanced signals with single stock
    test_enhanced_signals()
    
    # Test 2: Full market scanning
    test_full_scanning()
    
    # Test 3: Advanced modules individually
    test_advanced_modules()
    
    print("🎯 Integration testing complete!")
    print("\n💡 Next Steps:")
    print("  1. Run the dashboard: streamlit run dashboard.py")
    print("  2. Login and select stocks for detailed analysis")
    print("  3. Check the '🔬 Advanced Technical Analysis' section")
    print("  4. Install TA-Lib for full advanced features: brew install ta-lib && pip install TA-Lib")

if __name__ == "__main__":
    main()
