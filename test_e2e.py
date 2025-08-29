#!/usr/bin/env python3
"""Quick end-to-end test"""

from tools.portfolio_manager import PaperTradingPortfolio

# Test a complete buy/sell cycle with Indian stock
portfolio = PaperTradingPortfolio()
print("🎯 Testing Complete Buy/Sell Cycle with Indian Stock")
print("=" * 55)

# Buy Indian stock (RELIANCE.NS)
symbol = "RELIANCE.NS"
price = 1357.20  # Current market price in INR
confidence = 85

initial_cash_usd = portfolio.portfolio["cash"]
initial_cash_inr = portfolio.currency_converter.convert_to_currency(initial_cash_usd, "USD", "INR")
print(f"💰 Initial Cash: ₹{initial_cash_inr:,.2f} (${initial_cash_usd:,.2f})")

# Buy shares
result = portfolio.buy_stock(symbol, price, confidence, shares=5)
if result["success"]:
    print(f"✅ Buy: {result['message']}")
    
    # Check position
    positions = portfolio.get_current_positions()
    position = next((p for p in positions if p["symbol"] == symbol), None)
    if position:
        print(f"📊 Position: {position['shares']} shares at ₹{position['avg_price']:,.2f}")
        print(f"💵 Position Value: ₹{position['current_value']:,.2f}")
    
    # Test selling half for profit
    sell_result = portfolio.sell_stock(symbol, price * 1.05, shares=2, reason="Take Profit")  # 5% profit
    if sell_result["success"]:
        print(f"✅ Sell: {sell_result['message']}")
    
    # Check final metrics
    metrics = portfolio.get_performance_metrics()
    print(f"📈 Final Portfolio Value: ${metrics['total_value']:,.2f}")
    print(f"💸 Final Cash: ${metrics['cash']:,.2f}")
    
else:
    print(f"❌ Buy failed: {result['message']}")

print("\n✅ End-to-end test completed successfully!")
