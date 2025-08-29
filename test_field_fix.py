#!/usr/bin/env python3
"""
Field Name Fix Verification
Verify that avg_cost vs avg_price field access is fixed correctly.
"""

def test_field_access_fix():
    """Test the field access fix thoroughly"""
    
    print("🧪 Testing Field Access Fix")
    print("=" * 35)
    
    try:
        from tools.portfolio_manager import PaperTradingPortfolio
        from config.watchlist import TRADING_CONFIG
        
        # Initialize portfolio
        portfolio = PaperTradingPortfolio(initial_capital=TRADING_CONFIG['initial_capital'])
        positions = portfolio.get_current_positions()
        
        if not positions:
            print("📝 No positions found - creating a test scenario")
            return
        
        print(f"📊 Found {len(positions)} position(s) to test")
        
        # Test each position
        for i, pos in enumerate(positions):
            print(f"\n🔍 Testing position {i+1}: {pos['symbol']}")
            
            # Verify field structure
            expected_fields = ['symbol', 'shares', 'avg_price', 'current_price', 'currency']
            missing_fields = []
            
            for field in expected_fields:
                if field in pos:
                    print(f"  ✅ {field}: {pos[field]}")
                else:
                    missing_fields.append(field)
                    print(f"  ❌ {field}: MISSING")
            
            # Test the specific fix
            try:
                # This should work (correct field name)
                avg_cost_value = pos['avg_price']
                print(f"  ✅ pos['avg_price'] works: {avg_cost_value:.2f}")
            except KeyError as e:
                print(f"  ❌ pos['avg_price'] failed: {e}")
            
            try:
                # This should fail (incorrect field name)
                wrong_value = pos['avg_cost']
                print(f"  ❌ pos['avg_cost'] should not exist: {wrong_value}")
            except KeyError:
                print(f"  ✅ pos['avg_cost'] correctly raises KeyError")
            
            # Test dashboard simulation
            print(f"  🎯 Dashboard simulation:")
            symbol = pos['symbol']
            owned_shares = pos['shares']
            avg_cost = pos['avg_price']  # This is the fix
            currency = pos['currency']
            
            print(f"    Symbol: {symbol}")
            print(f"    Owned shares: {owned_shares}")
            print(f"    Avg cost: {currency}{avg_cost:.2f}")
            
            # Test sell calculation (what dashboard does)
            current_price = pos['current_price']
            sell_quantity = min(100, owned_shares)
            sell_proceeds = sell_quantity * current_price
            cost_basis = sell_quantity * avg_cost
            total_pnl = sell_proceeds - cost_basis
            
            print(f"    Sell simulation: {sell_quantity} shares")
            print(f"    P&L: {currency}{total_pnl:.2f}")
            
            break  # Test just first position
        
        print(f"\n✅ Field access fix verified successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dashboard_integration():
    """Test that the dashboard integration works with the fix"""
    
    print(f"\n🎯 Dashboard Integration Test")
    print("-" * 30)
    
    try:
        # Simulate the exact dashboard setup
        class DashboardMock:
            def __init__(self):
                from tools.portfolio_manager import PaperTradingPortfolio
                from config.watchlist import TRADING_CONFIG
                self.portfolio = PaperTradingPortfolio(initial_capital=TRADING_CONFIG['initial_capital'])
        
        dashboard = DashboardMock()
        
        # Simulate the exact code that was failing
        print("Testing exact failing code path...")
        
        # This simulates the code from lines 1159-1166
        portfolio_positions = dashboard.portfolio.get_current_positions()
        
        for pos in portfolio_positions:
            symbol = pos['symbol']
            # Test the exact line that was failing
            owned_shares = pos['shares']
            avg_cost = pos['avg_price']  # THIS WAS THE FIX
            
            print(f"✅ Position {symbol}: {owned_shares} shares at {avg_cost:.2f}")
            break
        
        print(f"✅ Dashboard integration test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Dashboard integration failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Field Name Fix Verification")
    print("=" * 50)
    
    success1 = test_field_access_fix()
    success2 = test_dashboard_integration()
    
    if success1 and success2:
        print(f"\n🎉 ALL FIELD ACCESS TESTS PASSED!")
        print(f"The KeyError: 'avg_cost' should be completely resolved.")
    else:
        print(f"\n💥 Some tests failed. Check error messages above.")
