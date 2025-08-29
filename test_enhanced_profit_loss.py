#!/usr/bin/env python3
"""
Test Enhanced Profit/Loss Calculations
Testing the new profit/loss projections with actual dollar amounts.
"""

def test_profit_loss_calculations():
    """Test the enhanced profit/loss calculations"""
    
    # Sample data based on your example
    entry_price = 4.27  # RM
    target1 = 4.33      # RM (+1.4%)
    target2 = 4.38      # RM (+2.6%)
    stop_loss = 4.20    # RM (-1.6%)
    shares = 2857       # Recommended shares
    currency_symbol = "RM"
    
    print("🧪 Testing Enhanced Profit/Loss Calculations")
    print("=" * 50)
    
    # Investment calculation
    investment = shares * entry_price
    print(f"💰 Investment: {currency_symbol}{investment:,.0f}")
    print(f"📊 Shares: {shares}")
    print(f"💵 Entry Price: {currency_symbol}{entry_price:.2f}")
    
    print("\n🎯 Profit/Loss Projections:")
    print("-" * 30)
    
    # Target 1 calculations
    target1_profit = shares * (target1 - entry_price)
    target1_profit_pct = ((target1 - entry_price) / entry_price) * 100
    target1_total_value = investment + target1_profit
    
    print(f"🟢 Target 1 ({currency_symbol}{target1:.2f}):")
    print(f"   Profit: {currency_symbol}{target1_profit:,.0f} (+{target1_profit_pct:.1f}%)")
    print(f"   Total Value: {currency_symbol}{target1_total_value:,.0f}")
    
    # Target 2 calculations
    target2_profit = shares * (target2 - entry_price)
    target2_profit_pct = ((target2 - entry_price) / entry_price) * 100
    target2_total_value = investment + target2_profit
    
    print(f"\n🟢 Target 2 ({currency_symbol}{target2:.2f}):")
    print(f"   Profit: {currency_symbol}{target2_profit:,.0f} (+{target2_profit_pct:.1f}%)")
    print(f"   Total Value: {currency_symbol}{target2_total_value:,.0f}")
    
    # Stop loss calculations
    stop_loss_amount = shares * (stop_loss - entry_price)
    stop_loss_pct = ((stop_loss - entry_price) / entry_price) * 100
    stop_loss_total_value = investment + stop_loss_amount
    
    print(f"\n🔴 Stop Loss ({currency_symbol}{stop_loss:.2f}):")
    print(f"   Loss: {currency_symbol}{stop_loss_amount:,.0f} ({stop_loss_pct:.1f}%)")
    print(f"   Total Value: {currency_symbol}{stop_loss_total_value:,.0f}")
    
    # Risk/Reward summary
    best_case = target2_profit
    worst_case = abs(stop_loss_amount)
    risk_reward_ratio = best_case / worst_case if worst_case > 0 else 0
    
    print(f"\n📊 Risk/Reward Summary:")
    print("-" * 25)
    print(f"🟢 Best Case: {currency_symbol}{best_case:,.0f}")
    print(f"🔴 Worst Case: -{currency_symbol}{worst_case:,.0f}")
    print(f"⚖️ R/R Ratio: {risk_reward_ratio:.1f}:1")
    
    # Validate calculations
    print(f"\n✅ Validation:")
    expected_investment = 2857 * 4.27
    expected_target1_profit = 2857 * (4.33 - 4.27)
    expected_stop_loss = 2857 * (4.20 - 4.27)
    
    print(f"Investment match: {abs(investment - expected_investment) < 1}")
    print(f"Target 1 profit match: {abs(target1_profit - expected_target1_profit) < 1}")
    print(f"Stop loss match: {abs(stop_loss_amount - expected_stop_loss) < 1}")
    
    print(f"\n🎯 Summary for your Malaysian stock:")
    print(f"   • If target 1 hit: You gain {currency_symbol}{target1_profit:,.0f}")
    print(f"   • If target 2 hit: You gain {currency_symbol}{target2_profit:,.0f}")
    print(f"   • If stop loss hit: You lose {currency_symbol}{abs(stop_loss_amount):,.0f}")

if __name__ == "__main__":
    test_profit_loss_calculations()
