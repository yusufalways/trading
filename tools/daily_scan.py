#!/usr/bin/env python3
"""
Daily Swing Trading Scanner - Quick Integration
Run this daily to get swing trading opportunities
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.swing_scanner import SwingTradingScanner, get_expanded_watchlists
from datetime import datetime

def quick_daily_scan():
    """Run a quick daily scan for swing opportunities"""
    print(f"📅 Daily Swing Scan - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    scanner = SwingTradingScanner()
    watchlists = get_expanded_watchlists()
    
    # Quick scan - top 10 per market for speed
    quick_lists = {
        'usa': watchlists['usa'][:10],
        'india': watchlists['india'][:10], 
        'malaysia': watchlists['malaysia'][:10]
    }
    
    all_opportunities = []
    
    for market, symbols in quick_lists.items():
        market_name = f"🇺🇸 US" if market == 'usa' else f"🇮🇳 India" if market == 'india' else f"🇲🇾 Malaysia"
        opportunities = scanner.scan_market(symbols, f"{market_name} (Quick)")
        all_opportunities.extend(opportunities)
    
    # Show top 10 overall
    print(f"\n🏆 Today's Top 10 Swing Opportunities:")
    print("-" * 60)
    
    if all_opportunities:
        for i, opp in enumerate(all_opportunities[:10], 1):
            symbol = opp['symbol']
            price = opp['current_price']
            score = opp['setup_score']
            recommendation = opp['recommendation']
            
            # Format price based on market
            if '.NS' in symbol:
                price_str = f"₹{price:.2f}"
                flag = "🇮🇳"
            elif '.KL' in symbol:
                price_str = f"RM{price:.2f}"
                flag = "🇲🇾"
            else:
                price_str = f"${price:.2f}"
                flag = "🇺🇸"
            
            print(f"{i:2}. {flag} {symbol:<15} {price_str:<12} Score:{score:3} {recommendation}")
    else:
        print("   No strong opportunities found today.")
    
    print(f"\n💡 For detailed analysis, run: python3 tools/swing_scanner.py")
    print(f"📊 For charts, check TradingView.com with these symbols")
    
    return all_opportunities[:5]  # Return top 5 for dashboard integration

if __name__ == "__main__":
    quick_daily_scan()
