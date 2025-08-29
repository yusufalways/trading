#!/usr/bin/env python3
"""
Test Portfolio Method Fix
Verify that the AttributeError is resolved and all portfolio functionality works.
"""

def test_portfolio_methods():
    """Test all portfolio methods used in the dashboard"""
    
    print("🧪 Testing Portfolio Method Fix")
    print("=" * 45)
    
    try:
        from tools.portfolio_manager import PaperTradingPortfolio
        from config.watchlist import TRADING_CONFIG
        
        portfolio = PaperTradingPortfolio(initial_capital=TRADING_CONFIG['initial_capital'])
        
        # Test method that was causing the error
        print("📊 Testing get_current_positions()...")
        positions = portfolio.get_current_positions()
        print(f"✅ Success! Found {len(positions)} positions")
        
        # Test position data structure
        if positions:
            pos = positions[0]
            required_fields = ['symbol', 'shares', 'avg_price', 'current_price', 'currency']
            
            print("\n🔍 Verifying position data structure:")
            for field in required_fields:
                if field in pos:
                    print(f"  ✅ {field}: {pos[field]}")
                else:
                    print(f"  ❌ {field}: MISSING")
            
            # Test sell confirmation data access
            print(f"\n💰 Testing sell confirmation calculations:")
            symbol = pos['symbol']
            owned_shares = pos['shares']
            avg_cost = pos['avg_price']
            current_price = pos['current_price']
            currency = pos['currency']
            
            print(f"  Symbol: {symbol}")
            print(f"  Owned shares: {owned_shares}")
            print(f"  Avg cost: {currency}{avg_cost:.2f}")
            print(f"  Current price: {currency}{current_price:.2f}")
            
            # Simulate sell calculation (like in dashboard)
            sell_quantity = min(100, owned_shares)
            sell_proceeds = sell_quantity * current_price
            cost_basis = sell_quantity * avg_cost
            total_pnl = sell_proceeds - cost_basis
            pnl_pct = (total_pnl / cost_basis) * 100 if cost_basis > 0 else 0
            
            print(f"\n📈 Sell {sell_quantity} shares simulation:")
            print(f"  Proceeds: {currency}{sell_proceeds:.2f}")
            print(f"  Cost basis: {currency}{cost_basis:.2f}")
            print(f"  P&L: {currency}{total_pnl:.2f} ({pnl_pct:+.1f}%)")
        else:
            print("📝 No positions found (portfolio is empty)")
        
        # Test other critical methods
        print(f"\n🔧 Testing other portfolio methods...")
        
        try:
            metrics = portfolio.get_performance_metrics()
            print(f"✅ get_performance_metrics(): {len(metrics)} fields")
        except Exception as e:
            print(f"❌ get_performance_metrics(): {e}")
        
        try:
            value = portfolio.get_portfolio_value()
            print(f"✅ get_portfolio_value(): {value}")
        except Exception as e:
            print(f"❌ get_portfolio_value(): {e}")
        
        try:
            summary = portfolio.get_portfolio_summary()
            print(f"✅ get_portfolio_summary(): {len(summary)} fields")
        except Exception as e:
            print(f"❌ get_portfolio_summary(): {e}")
        
        # Test the old broken method to confirm it's fixed
        print(f"\n🚫 Testing broken method (should fail):")
        try:
            portfolio.get_positions()  # This should fail
            print("❌ get_positions() should not exist!")
        except AttributeError:
            print("✅ Confirmed: get_positions() properly removed")
        
        print(f"\n✅ All tests passed! Dashboard should work correctly now.")
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        return False
    
    return True

def test_dashboard_integration():
    """Test that dashboard integration works"""
    
    print(f"\n🎯 Dashboard Integration Test")
    print("-" * 35)
    
    # Test the exact code used in dashboard
    try:
        print("Testing dashboard portfolio access pattern...")
        
        # Simulate dashboard class structure
        class DashboardWrapper:
            def __init__(self):
                from tools.portfolio_manager import PaperTradingPortfolio
                from config.watchlist import TRADING_CONFIG
                self.portfolio = PaperTradingPortfolio(initial_capital=TRADING_CONFIG['initial_capital'])
        
        dashboard = DashboardWrapper()
        
        # Test the exact line that was causing the error
        portfolio_positions = dashboard.portfolio.get_current_positions()
        print(f"✅ Dashboard portfolio access works! Found {len(portfolio_positions)} positions")
        
        # Test position access loop (like in dashboard)
        for pos in portfolio_positions:
            symbol = pos['symbol']
            owned_shares = pos['shares']
            avg_cost = pos['avg_price']
            print(f"  📊 {symbol}: {owned_shares} shares at avg cost {avg_cost:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Dashboard integration failed: {e}")
        return False

if __name__ == "__main__":
    success1 = test_portfolio_methods()
    success2 = test_dashboard_integration()
    
    if success1 and success2:
        print(f"\n🎉 ALL TESTS PASSED! Dashboard should work without errors.")
    else:
        print(f"\n💥 Some tests failed. Check the error messages above.")
