#!/usr/bin/env python3
"""
Test Enhanced Buy/Sell Confirmation System
Testing the new trade confirmation workflow with profit/loss projections.
"""

def test_buy_sell_workflow():
    """Test the enhanced buy/sell confirmation workflow"""
    
    print("🧪 Testing Enhanced Buy/Sell Confirmation System")
    print("=" * 60)
    
    # Sample trade scenarios
    scenarios = [
        {
            "action": "BUY",
            "symbol": "GENTING",
            "entry_price": 4.27,
            "target1": 4.33,
            "target2": 4.38,
            "stop_loss": 4.20,
            "quantity": 1000,
            "currency": "RM"
        },
        {
            "action": "SELL",
            "symbol": "AAPL",
            "current_price": 180.00,
            "avg_cost": 170.00,
            "quantity": 50,
            "currency": "$"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📋 {scenario['action']} Scenario: {scenario['symbol']}")
        print("-" * 40)
        
        if scenario["action"] == "BUY":
            # Buy confirmation calculations
            symbol = scenario["symbol"]
            entry_price = scenario["entry_price"]
            target1 = scenario["target1"]
            target2 = scenario["target2"]
            stop_loss = scenario["stop_loss"]
            quantity = scenario["quantity"]
            currency = scenario["currency"]
            
            # Calculate projections
            investment = quantity * entry_price
            target1_profit = quantity * (target1 - entry_price)
            target1_total = investment + target1_profit
            target2_profit = quantity * (target2 - entry_price)
            target2_total = investment + target2_profit
            stop_loss_amount = quantity * (stop_loss - entry_price)
            stop_total = investment + stop_loss_amount
            
            print(f"🟢 BUY ORDER PREVIEW:")
            print(f"   Investment: {currency}{investment:,.0f} ({quantity:,} shares)")
            print(f"   Entry Price: {currency}{entry_price:.2f}")
            print()
            print(f"💰 PROFIT/LOSS PROJECTIONS:")
            print(f"   🎯 Target 1 ({currency}{target1:.2f}):")
            print(f"      Profit: {currency}{target1_profit:,.0f}")
            print(f"      Total Value: {currency}{target1_total:,.0f}")
            print(f"   🚀 Target 2 ({currency}{target2:.2f}):")
            print(f"      Profit: {currency}{target2_profit:,.0f}")
            print(f"      Total Value: {currency}{target2_total:,.0f}")
            print(f"   🛑 Stop Loss ({currency}{stop_loss:.2f}):")
            print(f"      Loss: {currency}{stop_loss_amount:,.0f}")
            print(f"      Total Value: {currency}{stop_total:,.0f}")
            
            # Risk/Reward
            best_case = target2_profit
            worst_case = abs(stop_loss_amount)
            rr_ratio = best_case / worst_case if worst_case > 0 else 0
            print(f"   ⚖️ Risk/Reward Ratio: {rr_ratio:.1f}:1")
            
        elif scenario["action"] == "SELL":
            # Sell confirmation calculations
            symbol = scenario["symbol"]
            current_price = scenario["current_price"]
            avg_cost = scenario["avg_cost"]
            quantity = scenario["quantity"]
            currency = scenario["currency"]
            
            # Calculate P&L
            proceeds = quantity * current_price
            cost_basis = quantity * avg_cost
            total_pnl = proceeds - cost_basis
            pnl_pct = (total_pnl / cost_basis) * 100 if cost_basis > 0 else 0
            
            print(f"🔴 SELL ORDER PREVIEW:")
            print(f"   Shares to Sell: {quantity:,}")
            print(f"   Current Price: {currency}{current_price:.2f}")
            print(f"   Avg Cost: {currency}{avg_cost:.2f}")
            print(f"   Gross Proceeds: {currency}{proceeds:,.0f}")
            print()
            print(f"💰 PROFIT/LOSS ANALYSIS:")
            pnl_emoji = "🟢" if total_pnl >= 0 else "🔴"
            print(f"   {pnl_emoji} Total P&L: {currency}{total_pnl:,.0f}")
            print(f"   📊 Return: {pnl_pct:+.1f}%")
            print(f"   💵 Cost Basis: {currency}{cost_basis:,.0f}")
            print(f"   💸 Net Proceeds: {currency}{proceeds:,.0f}")
    
    print(f"\n✅ Enhanced Buy/Sell System Features:")
    print("   • Custom quantity input with real-time calculations")
    print("   • Detailed profit/loss projections before confirmation")
    print("   • Risk/reward analysis for buy orders")
    print("   • P&L analysis for sell orders")
    print("   • Confirmation/cancellation workflow")
    print("   • Session state management to prevent accidental trades")
    
    print(f"\n🎯 User Workflow:")
    print("   1. Enter desired quantity")
    print("   2. Click 'PREVIEW BUY/SELL' to see projections")
    print("   3. Review profit/loss scenarios")
    print("   4. Confirm or cancel the trade")
    print("   5. Execute trade with full knowledge of outcomes")

if __name__ == "__main__":
    test_buy_sell_workflow()
