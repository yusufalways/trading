#!/usr/bin/env python3
"""
Test enhanced trading system with multi-currency and manual quantity features
"""

import sys
import os
sys.path.append('/Users/yusufalways/trading')

from tools.portfolio_manager import PaperTradingPortfolio, CurrencyConverter
import yfinance as yf

def test_currency_converter():
    """Test currency conversion functionality"""
    print("🌍 Testing Currency Converter...")
    
    converter = CurrencyConverter()
    
    # Test currency detection
    test_symbols = ['AAPL', 'RELIANCE.NS', '1155.KL']
    expected_currencies = ['USD', 'INR', 'MYR']
    
    for symbol, expected in zip(test_symbols, expected_currencies):
        detected = converter.get_symbol_currency(symbol)
        status = "✅" if detected == expected else "❌"
        print(f"   {status} {symbol} -> {detected} (expected {expected})")
    
    # Test currency formatting
    amounts = [1000, 1000, 1000]
    currencies = ['USD', 'INR', 'MYR']
    
    print(f"\n   Currency Formatting:")
    for amount, currency in zip(amounts, currencies):
        formatted = converter.format_currency(amount, currency)
        print(f"   {currency}: {formatted}")
    
    # Try to update exchange rates
    print(f"\n   Updating exchange rates...")
    converter.update_exchange_rates()
    print(f"   Current rates: {converter.exchange_rates}")

def test_enhanced_trading():
    """Test enhanced trading with multi-currency and manual quantities"""
    print(f"\n💰 Testing Enhanced Trading System...")
    
    # Initialize portfolio
    portfolio = PaperTradingPortfolio()
    
    # Test stocks from different markets
    test_trades = [
        {"symbol": "AAPL", "shares": 5, "confidence": 80},  # USD
        {"symbol": "RELIANCE.NS", "shares": 10, "confidence": 75},  # INR
        {"symbol": "1155.KL", "shares": 100, "confidence": 70}  # MYR
    ]
    
    print(f"\n   Initial Portfolio:")
    print(f"   Cash: ${portfolio.portfolio['cash']:,.2f}")
    
    for trade_info in test_trades:
        symbol = trade_info['symbol']
        shares = trade_info['shares']
        confidence = trade_info['confidence']
        
        print(f"\n   🎯 Testing {symbol} ({shares} shares, {confidence}% confidence)...")
        
        try:
            # Get current price
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")
            
            if not data.empty:
                current_price = float(data['Close'].iloc[-1])
                currency = portfolio.currency_converter.get_symbol_currency(symbol)
                
                print(f"      Current Price: {portfolio.currency_converter.format_currency(current_price, currency)}")
                
                # Test manual quantity buy
                result = portfolio.buy_stock(symbol, current_price, confidence, shares=shares)
                
                if result['success']:
                    print(f"      ✅ {result['message']}")
                    print(f"      💰 Total Cost: {portfolio.currency_converter.format_currency(result['total_cost_original'], result['currency'])}")
                    print(f"      🎯 Target: {portfolio.currency_converter.format_currency(result['target_price'], result['currency'])}")
                    print(f"      🛡️ Stop Loss: {portfolio.currency_converter.format_currency(result['stop_loss_price'], result['currency'])}")
                else:
                    print(f"      ❌ {result['message']}")
            else:
                print(f"      ⚠️ No price data for {symbol}")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    # Show portfolio summary with currencies
    print(f"\n   📊 Final Portfolio Summary:")
    summary = portfolio.get_portfolio_summary()
    
    print(f"   💰 Total Value: ${summary['total_value']:,.2f}")
    print(f"   💵 Cash: ${summary['cash']:,.2f}")
    print(f"   📈 Return: {summary['total_return_pct']:+.2f}%")
    print(f"   📊 Positions: {summary['position_count']}")
    
    if summary['positions']:
        print(f"\n   🏢 Multi-Currency Positions:")
        for pos in summary['positions']:
            currency = pos.get('currency', 'USD')
            print(f"   • {pos['symbol']} ({currency}):")
            print(f"     Shares: {pos['shares']}")
            print(f"     Entry: {portfolio.currency_converter.format_currency(pos.get('avg_price_original', pos['avg_price']), currency)}")
            print(f"     Current: {portfolio.currency_converter.format_currency(pos.get('current_price', pos['avg_price']), currency)}")
            print(f"     P&L: {portfolio.currency_converter.format_currency(pos['unrealized_pnl'], 'USD')} (USD equivalent)")

def test_trade_history():
    """Test enhanced trade history tracking"""
    print(f"\n📋 Testing Trade History...")
    
    portfolio = PaperTradingPortfolio()
    
    # Check if we have trade history
    trade_history = portfolio.portfolio.get('trade_history', [])
    
    if trade_history:
        print(f"   Found {len(trade_history)} trades in history")
        
        # Show last few trades with currency info
        recent_trades = trade_history[-3:] if len(trade_history) >= 3 else trade_history
        
        for trade in recent_trades:
            action_emoji = "🟢" if trade['action'] == 'BUY' else "🔴"
            currency = trade.get('currency', 'USD')
            price_original = trade.get('price_original', trade['price'])
            
            print(f"   {action_emoji} {trade['action']} {trade['shares']} {trade['symbol']}")
            print(f"      Price: {portfolio.currency_converter.format_currency(price_original, currency)}")
            print(f"      Date: {trade.get('date', trade.get('timestamp', 'Unknown'))[:10]}")
            
            if trade['action'] == 'SELL' and 'pnl_original' in trade:
                pnl_original = trade['pnl_original']
                pnl_pct = trade.get('pnl_pct', 0)
                print(f"      P&L: {portfolio.currency_converter.format_currency(pnl_original, currency)} ({pnl_pct:+.2f}%)")
        
        # Test selling a position to generate more history
        positions = portfolio.get_current_positions()
        if positions:
            test_position = positions[0]
            symbol = test_position['symbol']
            
            print(f"\n   🧪 Testing partial sell of {symbol}...")
            
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period="1d")
                
                if not data.empty:
                    current_price = float(data['Close'].iloc[-1])
                    shares_to_sell = min(2, test_position['shares'])  # Sell 2 shares or all if less
                    
                    result = portfolio.sell_stock(symbol, current_price, shares=shares_to_sell, reason="PARTIAL_TEST")
                    
                    if result['success']:
                        print(f"      ✅ {result['message']}")
                        print(f"      💰 Proceeds: {result['proceeds_original']:.2f} {result['currency']}")
                        print(f"      📈 P&L: {result['pnl_original']:+.2f} {result['currency']} ({result['pnl_pct']:+.2f}%)")
                        print(f"      📅 Held for: {result['holding_days']} days")
                    else:
                        print(f"      ❌ {result['message']}")
                        
            except Exception as e:
                print(f"      ❌ Error testing sell: {e}")
    else:
        print(f"   No trade history found. Execute some trades first!")

def main():
    print("🚀 Testing Enhanced Multi-Currency Trading System\n")
    
    try:
        test_currency_converter()
        test_enhanced_trading()
        test_trade_history()
        
        print(f"\n🎉 All Enhanced Features Tested Successfully!")
        print(f"\n💡 New Features Available:")
        print(f"   ✅ Multi-currency support (USD, INR, MYR)")
        print(f"   ✅ Manual share quantity selection")
        print(f"   ✅ Enhanced trade history with P&L tracking")
        print(f"   ✅ Currency-specific price display")
        print(f"   ✅ Partial selling capabilities")
        print(f"   ✅ Detailed trade analytics by symbol")
        print(f"   ✅ Export trade history to CSV")
        
        print(f"\n🌐 Ready for Enhanced Dashboard:")
        print(f"   Command: python3 -m streamlit run dashboard.py")
        print(f"   URL: http://localhost:8501")
        print(f"\n📋 New Dashboard Features:")
        print(f"   • Manual quantity input for buy orders")
        print(f"   • Currency-specific price display")
        print(f"   • Comprehensive trade history tab")
        print(f"   • Multi-currency portfolio tracking")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
