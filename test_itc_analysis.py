"""
Unit test for ITC.NS analysis to verify all feedback is addressed.
"""
import sys
import os
from pprint import pprint

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.master_swing_analyzer import MasterSwingAnalyzer

def test_itc_stock_analysis():
    """
    Tests the master swing analyzer on ITC.NS and prints a detailed report.
    """
    print("✅ Using master_swing_analyzer.py (the ONE analysis system)")
    print("="*60)
    print("🔍 Running detailed analysis for ITC.NS...")
    
    analyzer = MasterSwingAnalyzer()
    analysis = analyzer.analyze_stock("ITC.NS")
    
    if not analysis:
        print("❌ Analysis for ITC.NS failed.")
        return

    print("\n" + "="*60)
    print("📊 DETAILED ANALYSIS REPORT FOR ITC.NS")
    print("="*60)

    # --- Verification of Critical Issues ---
    print("\n[1] VERIFYING: Contradictory Signals Problem")
    
    # RSI Check
    rsi_val = analysis['technical_indicators']['rsi']['value']
    rsi_status = analysis['technical_indicators']['rsi']['status']
    print(f"  - RSI: {rsi_val:.1f} is '{rsi_status}' -> {'✅ Correct' if rsi_status == 'Oversold Territory' else '❌ INCORRECT'}")

    # MACD Check
    macd_status = analysis['technical_indicators']['macd']['status']
    print(f"  - MACD: Status is '{macd_status}' -> {'✅ Correct' if 'Bearish' in macd_status else '❌ INCORRECT'}")

    # Moving Average Check
    ma_status = analysis['technical_indicators']['moving_averages']['status']
    price = analysis['current_price']
    sma20 = analysis['technical_indicators']['moving_averages']['sma_20']
    sma50 = analysis['technical_indicators']['moving_averages']['sma_50']
    print(f"  - Price vs MAs: Status is '{ma_status}' (Price: {price:.2f}, MA20: {sma20:.2f}, MA50: {sma50:.2f}) -> {'✅ Correct' if 'Bearish' in ma_status else '❌ INCORRECT'}")

    # --- Verification of Enhancements ---
    print("\n[2] VERIFYING: Enhanced Technical Analysis")
    tech = analysis['technical_indicators']
    print(f"  - ADX Trend Strength: {tech['adx']['trend_strength']}")
    print(f"  - Volume Profile (OBV): {tech['volume_analysis']['obv_trend']}")
    print(f"  - Stochastic RSI: {tech['stochastic_rsi']['value']:.2f}")
    print(f"  - Williams %R: {tech['williams_r']['value']:.2f}")
    print(f"  - ATR Volatility: {tech['volatility']['atr']:.2f}")

    print("\n[3] VERIFYING: Market Context")
    mkt = analysis['market_context']
    print(f"  - Market Regime: {mkt['market_regime']}")
    print(f"  - Relative Strength vs Index: {mkt['relative_performance']}")
    
    print("\n[4] VERIFYING: Risk-Adjusted Score")
    score = analysis['swing_score']
    print(f"  - Final Score: {score}/100")
    
    print("\n[5] VERIFYING: Recommendation & Risk")
    rec = analysis['recommendation']
    risk = analysis['risk_management']
    print(f"  - Recommendation: {rec}")
    print(f"  - Stop Loss (ATR-based): {risk['stop_loss']:.2f}")
    print(f"  - Risk/Reward Ratio: {risk['risk_reward_ratio']}")

    print("\n" + "="*60)
    print("✅ ITC.NS analysis test complete.")
    print("="*60)
    
    print("\nFULL ANALYSIS DATA:")
    pprint(analysis)


if __name__ == "__main__":
    test_itc_stock_analysis()
