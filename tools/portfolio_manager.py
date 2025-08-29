"""
Paper Trading Portfolio Manager
Tracks virtual trades, performance, and learning metrics
"""

import pandas as pd
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
import yfinance as yf

class CurrencyConverter:
    """Handle currency conversions for multi-market trading"""
    
    def __init__(self):
        self.exchange_rates = {
            'USD': 1.0,  # Base currency
            'INR': 83.0,  # Approximate rate
            'MYR': 4.5    # Approximate rate
        }
        self.last_updated = None
        
    def get_symbol_currency(self, symbol: str) -> str:
        """Determine currency based on symbol suffix"""
        if symbol.endswith('.NS') or symbol.endswith('.BO'):
            return 'INR'
        elif symbol.endswith('.KL'):
            return 'MYR'
        else:
            return 'USD'
    
    def update_exchange_rates(self):
        """Update exchange rates from free API"""
        try:
            # Using a free exchange rate API
            response = requests.get('https://api.exchangerate-api.com/v4/latest/USD', timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.exchange_rates = {
                    'USD': 1.0,
                    'INR': data['rates'].get('INR', 83.0),
                    'MYR': data['rates'].get('MYR', 4.5)
                }
                self.last_updated = datetime.now()
                print(f"✅ Exchange rates updated: 1 USD = {self.exchange_rates['INR']:.2f} INR, {self.exchange_rates['MYR']:.2f} MYR")
        except Exception as e:
            print(f"⚠️ Could not update exchange rates, using defaults: {e}")
    
    def convert_to_usd(self, amount: float, from_currency: str) -> float:
        """Convert amount from any currency to USD"""
        if from_currency == 'USD':
            return amount
        return amount / self.exchange_rates.get(from_currency, 1.0)
    
    def convert_from_usd(self, amount: float, to_currency: str) -> float:
        """Convert amount from USD to any currency"""
        if to_currency == 'USD':
            return amount
        return amount * self.exchange_rates.get(to_currency, 1.0)
    
    def convert_to_currency(self, amount: float, from_currency: str, to_currency: str) -> float:
        """Convert amount from one currency to another"""
        if from_currency == to_currency:
            return amount
        # Convert to USD first, then to target currency
        usd_amount = self.convert_to_usd(amount, from_currency)
        return self.convert_from_usd(usd_amount, to_currency)
    
    def format_currency(self, amount: float, currency: str) -> str:
        """Format amount with appropriate currency symbol"""
        symbols = {'USD': '$', 'INR': '₹', 'MYR': 'RM'}
        symbol = symbols.get(currency, currency + ' ')
        return f"{symbol}{amount:,.2f}"

class PaperTradingPortfolio:
    def __init__(self, initial_capital: float = 10000, data_file: str = "paper_portfolio.json"):
        self.initial_capital = initial_capital
        self.data_file = os.path.join("data", data_file)
        self.currency_converter = CurrencyConverter()
        self.portfolio = self.load_portfolio()
        
        # Update exchange rates on initialization
        if self.portfolio.get('settings', {}).get('auto_update_rates', True):
            self.currency_converter.update_exchange_rates()
        
    def load_portfolio(self) -> Dict:
        """Load portfolio from file or create new one"""
        if os.path.exists(self.data_file):
            # Load existing portfolio and migrate if necessary
            with open(self.data_file, 'r') as f:
                portfolio = json.load(f)
            
            # Migrate old single-currency format to multi-currency
            if isinstance(portfolio.get('cash'), (int, float)):
                # Old format - migrate to multi-currency
                old_cash = portfolio['cash']
                old_initial = portfolio.get('initial_capital', 10000)
                
                portfolio['cash'] = {
                    'USD': old_cash,
                    'INR': 100000,
                    'MYR': 10000
                }
                portfolio['initial_capital'] = {
                    'USD': old_initial,
                    'INR': 100000,
                    'MYR': 10000
                }
                portfolio['version'] = '2.0'
                print("📦 Migrated portfolio to multi-currency format")
            
            # Ensure new format has all required fields
            if 'cash' not in portfolio or not isinstance(portfolio['cash'], dict):
                portfolio['cash'] = {'USD': 10000, 'INR': 100000, 'MYR': 10000}
            if 'initial_capital' not in portfolio or not isinstance(portfolio['initial_capital'], dict):
                portfolio['initial_capital'] = {'USD': 10000, 'INR': 100000, 'MYR': 10000}
                
            # Migrate legacy portfolio data
            if 'settings' not in portfolio:
                portfolio['settings'] = {
                    'auto_update_rates': True,
                    'risk_per_trade': 0.02,
                    'max_positions': 10,
                    'manual_quantity': True
                }
            
            if 'base_currency' not in portfolio:
                portfolio['base_currency'] = 'USD'
            
            # Migrate existing positions to include currency info
            for symbol, position in portfolio.get('positions', {}).items():
                if 'currency' not in position:
                    position['currency'] = self.currency_converter.get_symbol_currency(symbol)
                
                if 'avg_price_original' not in position:
                    position['avg_price_original'] = position.get('avg_price', 0)
                
                if 'last_price_original' not in position:
                    position['last_price_original'] = position.get('last_price', position.get('avg_price', 0))
                
                if 'target_price_original' not in position:
                    position['target_price_original'] = position.get('target_price', position.get('avg_price', 0) * 1.10)
                
                if 'stop_loss_price_original' not in position:
                    position['stop_loss_price_original'] = position.get('stop_loss_price', position.get('avg_price', 0) * 0.95)
            
            # Migrate trade history
            for trade in portfolio.get('trade_history', []):
                if 'currency' not in trade:
                    trade['currency'] = self.currency_converter.get_symbol_currency(trade['symbol'])
                
                if 'price_original' not in trade:
                    trade['price_original'] = trade.get('price', 0)
                
                if 'total_original' not in trade:
                    trade['total_original'] = trade.get('total', trade.get('shares', 0) * trade.get('price', 0))
            
            return portfolio
            
        else:
            # Create new multi-currency portfolio
            return {
                'cash': {
                    'USD': 10000,
                    'INR': 100000,
                    'MYR': 10000
                },
                'initial_capital': {
                    'USD': 10000,
                    'INR': 100000,
                    'MYR': 10000
                },
                'positions': {},
                'trade_history': [],
                'daily_values': [],
                'created_date': datetime.now().isoformat(),
                'settings': {
                    'auto_update_rates': True,
                    'risk_per_trade': 0.02,
                    'max_positions': 20,
                    'stop_loss_pct': 0.05,
                    'take_profit_pct': 0.10,
                    'auto_trade': False
                },
                'version': '2.0'
            }
    
    def save_portfolio(self):
        """Save portfolio to file"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w') as f:
            json.dump(self.portfolio, f, indent=2)
    
    def get_current_price(self, symbol: str) -> float:
        """Get current stock price"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d')
            if not data.empty:
                return data['Close'].iloc[-1]
        except:
            pass
        return 0.0
    
    def buy_stock(self, symbol: str, price: float, confidence: int, shares: int = None, signal_date: str = None):
        """Execute a buy order with manual quantity selection and multi-currency support"""
        if signal_date is None:
            signal_date = datetime.now().isoformat()
            
        # Determine currency for this symbol
        symbol_currency = self.currency_converter.get_symbol_currency(symbol)
        
        # Convert price to USD for portfolio calculations
        price_usd = self.currency_converter.convert_to_usd(price, symbol_currency)
        
        # Calculate position size
        if shares is None:
            # Auto-calculate shares based on confidence and available cash
            available_cash = self.portfolio['cash'].get(symbol_currency, 0)
            confidence_multiplier = confidence / 100
            base_allocation = 0.10  # 10% base allocation
            target_allocation = base_allocation * confidence_multiplier
            target_position_value = available_cash * target_allocation
            shares = max(1, int(target_position_value / price))
        
        # Calculate total cost in original currency only
        total_cost = shares * price
        
        # Get available cash in the symbol's currency
        available_cash = self.portfolio['cash'].get(symbol_currency, 0)
        
        # Check if we have enough cash and position limits
        max_positions = self.portfolio['settings'].get('max_positions', 20)
        current_positions = len(self.portfolio['positions'])
        
        if total_cost > available_cash:
            return {
                'success': False, 
                'message': f"Insufficient {symbol_currency} funds. Need {self.currency_converter.format_currency(total_cost, symbol_currency)}, have {self.currency_converter.format_currency(available_cash, symbol_currency)}"
            }
        
        if current_positions >= max_positions and symbol not in self.portfolio['positions']:
            return {
                'success': False,
                'message': f"Maximum position limit ({max_positions}) reached"
            }
        
        if shares <= 0:
            return {
                'success': False,
                'message': "Invalid share quantity"
            }
        
        # Execute trade - deduct cash in the symbol's currency
        self.portfolio['cash'][symbol_currency] -= total_cost
        
        if symbol in self.portfolio['positions']:
            # Add to existing position
            existing = self.portfolio['positions'][symbol]
            total_shares = existing['shares'] + shares
            # Calculate weighted average price in original currency
            total_cost_combined = (existing['shares'] * existing['avg_price']) + (shares * price)
            avg_price = total_cost_combined / total_shares
            
            self.portfolio['positions'][symbol].update({
                'shares': total_shares,
                'avg_price': avg_price,  # Original currency only
                'last_price': price,     # Original currency only
                'currency': symbol_currency,
                'confidence': max(confidence, existing['confidence']),
                'target_price': avg_price * 1.10,
                'stop_loss_price': avg_price * 0.95,
                'last_updated': signal_date
            })
        else:
            # New position
            self.portfolio['positions'][symbol] = {
                'shares': shares,
                'avg_price': price,  # Original currency only
                'last_price': price, # Original currency only
                'currency': symbol_currency,
                'confidence': confidence,
                'entry_date': signal_date,
                'target_price': price * 1.10,
                'stop_loss_price': price * 0.95,
                'last_updated': signal_date
            }
        
        # Get portfolio value after trade
        portfolio_values = self.get_portfolio_value()
        portfolio_value_after = portfolio_values.get(symbol_currency, 0)
        
        # Record detailed trade
        self.portfolio['trade_history'].append({
            'id': len(self.portfolio['trade_history']) + 1,
            'symbol': symbol,
            'action': 'BUY',
            'shares': shares,
            'price': price,  # Original currency
            'currency': symbol_currency,
            'total': total_cost,  # Original currency
            'confidence': confidence,
            'date': signal_date,
            'timestamp': datetime.now().isoformat(),
            'cash_after': self.portfolio['cash'][symbol_currency],
            'portfolio_value_after': portfolio_value_after,
            'target_price': price * 1.10,
            'stop_loss_price': price * 0.95,
            'allocation_pct': (total_cost / portfolio_value_after) * 100 if portfolio_value_after > 0 else 0,
            'trade_reason': f'Signal confidence: {confidence}%'
        })
        
        self.save_portfolio()
        
        return {
            'success': True,
            'shares': shares,
            'symbol': symbol,
            'price': price,
            'total_cost': total_cost,
            'currency': symbol_currency,
            'target_price': price * 1.10,
            'stop_loss_price': price * 0.95,
            'message': f"Bought {shares} shares of {symbol} for {self.currency_converter.format_currency(total_cost, symbol_currency)}"
        }
    
    def sell_stock(self, symbol: str, price: float, shares: int = None, reason: str = "SIGNAL", signal_date: str = None):
        """Execute a sell order with partial selling support and multi-currency tracking"""
        if signal_date is None:
            signal_date = datetime.now().isoformat()
            
        if symbol not in self.portfolio['positions']:
            return {
                'success': False,
                'message': f"No position found for {symbol}"
            }
        
        position = self.portfolio['positions'][symbol]
        symbol_currency = position.get('currency', 'USD')
        
        # Convert price to USD for calculations
        price_usd = self.currency_converter.convert_to_usd(price, symbol_currency)
        
        # Determine shares to sell
        if shares is None:
            shares_to_sell = position['shares']  # Sell all
        else:
            shares_to_sell = min(shares, position['shares'])  # Sell requested amount or all available
        
        if shares_to_sell <= 0:
            return {
                'success': False,
                'message': "Invalid share quantity to sell"
            }
        
        # Calculate proceeds and P&L
        total_proceeds_usd = shares_to_sell * price_usd
        total_proceeds_original = shares_to_sell * price
        
        # Calculate P&L based on average cost
        cost_basis_usd = shares_to_sell * position['avg_price']
        cost_basis_original = shares_to_sell * position['avg_price_original']
        pnl_usd = total_proceeds_usd - cost_basis_usd
        pnl_original = total_proceeds_original - cost_basis_original
        pnl_pct = (pnl_usd / cost_basis_usd) * 100 if cost_basis_usd > 0 else 0
        
        # Calculate holding period
        entry_date = datetime.fromisoformat(position['entry_date'])
        sell_date = datetime.fromisoformat(signal_date)
        holding_days = (sell_date - entry_date).days
        
        # Execute trade - add proceeds to appropriate currency
        self.portfolio['cash'][symbol_currency] += total_proceeds_original
        
        # Record detailed trade
        trade_record = {
            'id': len(self.portfolio['trade_history']) + 1,
            'symbol': symbol,
            'action': 'SELL',
            'shares': shares_to_sell,
            'price': price_usd,
            'price_original': price,
            'currency': symbol_currency,
            'total_usd': total_proceeds_usd,
            'total_original': total_proceeds_original,
            'cost_basis_usd': cost_basis_usd,
            'cost_basis_original': cost_basis_original,
            'pnl_usd': pnl_usd,
            'pnl_original': pnl_original,
            'pnl_pct': pnl_pct,
            'reason': reason,
            'date': signal_date,
            'timestamp': datetime.now().isoformat(),
            'entry_date': position['entry_date'],
            'holding_days': holding_days,
            'entry_price_usd': position['avg_price'],
            'entry_price_original': position['avg_price_original'],
            'cash_after': self.portfolio['cash'][symbol_currency],
            'portfolio_value_after': self.get_portfolio_value(),
            'win_trade': pnl_usd > 0
        }
        
        self.portfolio['trade_history'].append(trade_record)
        
        # Update or remove position
        if shares_to_sell >= position['shares']:
            # Selling all shares - remove position
            del self.portfolio['positions'][symbol]
        else:
            # Partial sell - update position
            remaining_shares = position['shares'] - shares_to_sell
            self.portfolio['positions'][symbol]['shares'] = remaining_shares
            self.portfolio['positions'][symbol]['last_updated'] = signal_date
        
        self.save_portfolio()
        
        return {
            'success': True,
            'shares_sold': shares_to_sell,
            'proceeds_usd': total_proceeds_usd,
            'proceeds_original': total_proceeds_original,
            'pnl_usd': pnl_usd,
            'pnl_original': pnl_original,
            'pnl_pct': pnl_pct,
            'currency': symbol_currency,
            'holding_days': holding_days,
            'message': f"Sold {shares_to_sell} shares of {symbol} for {self.currency_converter.format_currency(total_proceeds_original, symbol_currency)} (P&L: {self.currency_converter.format_currency(pnl_original, symbol_currency)})"
        }
    
    def update_positions(self):
        """Update current prices for all positions"""
        for symbol in list(self.portfolio['positions'].keys()):
            current_price = self.get_current_price(symbol)
            if current_price > 0:
                # Update price in original currency only
                self.portfolio['positions'][symbol]['last_price'] = current_price
        
        # Record daily portfolio value
        portfolio_values = self.get_portfolio_value()
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Update or add today's value (using separate currency system)
        daily_values = self.portfolio['daily_values']
        
        if daily_values and daily_values[-1]['date'] == today:
            daily_values[-1]['value'] = portfolio_values
        else:
            daily_values.append({
                'date': today,
                'value': portfolio_values,
                'cash': self.portfolio['cash']
            })
        
        self.save_portfolio()
    
    def get_portfolio_value(self) -> Dict[str, float]:
        """Calculate portfolio value for each currency separately"""
        portfolio_values = {}
        
        # Calculate value for each currency
        for currency in ['USD', 'INR', 'MYR']:
            # Start with cash balance
            cash_balance = self.portfolio['cash'].get(currency, 0)
            
            # Add position values in the same currency
            positions_value = 0
            for symbol, position in self.portfolio['positions'].items():
                if position.get('currency') == currency:
                    # Use current price for position valuation, fallback to avg_price
                    current_price = position.get('current_price', position['avg_price'])
                    position_value = position['shares'] * current_price
                    positions_value += position_value
            
            portfolio_values[currency] = cash_balance + positions_value
        
        return portfolio_values
    
    def get_performance_metrics(self) -> Dict:
        """Calculate performance metrics for each currency separately"""
        portfolio_values = self.get_portfolio_value()
        
        # Calculate metrics for each currency
        currency_metrics = {}
        
        for currency in ['USD', 'INR', 'MYR']:
            current_value = portfolio_values.get(currency, 0)
            initial_capital = self.portfolio['initial_capital'].get(currency, 0)
            
            total_return = current_value - initial_capital
            total_return_pct = (total_return / initial_capital) * 100 if initial_capital > 0 else 0
            
            # Count positions in this currency
            positions_count = sum(1 for pos in self.portfolio['positions'].values() if pos.get('currency') == currency)
            
            currency_metrics[currency] = {
                'current_value': current_value,
                'initial_capital': initial_capital,
                'total_return': total_return,
                'total_return_pct': total_return_pct,
                'cash': self.portfolio['cash'].get(currency, 0),
                'positions_count': positions_count
            }
        
        # Analyze completed trades for overall stats
        completed_trades = [t for t in self.portfolio['trade_history'] if t['action'] == 'SELL']
        
        if completed_trades:
            winning_trades = [t for t in completed_trades if t.get('pnl_original', t.get('pnl', 0)) > 0]
            losing_trades = [t for t in completed_trades if t.get('pnl_original', t.get('pnl', 0)) <= 0]
            
            win_rate = len(winning_trades) / len(completed_trades) * 100
            avg_win = sum(t.get('pnl_pct', 0) for t in winning_trades) / len(winning_trades) if winning_trades else 0
            avg_loss = sum(t.get('pnl_pct', 0) for t in losing_trades) / len(losing_trades) if losing_trades else 0
            
            best_trade = max(completed_trades, key=lambda x: x.get('pnl_pct', 0))
            worst_trade = min(completed_trades, key=lambda x: x.get('pnl_pct', 0))
        else:
            win_rate = 0
            avg_win = 0
            avg_loss = 0
            best_trade = None
            worst_trade = None
        
        # Calculate max drawdown from daily values
        max_drawdown = 0
        if self.portfolio['daily_values']:
            # For separate currency system, calculate combined USD equivalent for drawdown
            peak_value = 0
            for daily_record in self.portfolio['daily_values']:
                if isinstance(daily_record['value'], dict):
                    # New format: convert all to USD for drawdown calculation
                    daily_usd_value = 0
                    for currency, amount in daily_record['value'].items():
                        daily_usd_value += self.currency_converter.convert_to_usd(amount, currency)
                else:
                    # Old format: already in USD
                    daily_usd_value = daily_record['value']
                
                # Track peak and calculate drawdown
                if daily_usd_value > peak_value:
                    peak_value = daily_usd_value
                elif peak_value > 0:
                    drawdown = ((peak_value - daily_usd_value) / peak_value) * 100
                    max_drawdown = max(max_drawdown, drawdown)
        
        # Calculate total USD equivalent value for compatibility
        total_value_usd = sum(
            self.currency_converter.convert_to_usd(value, currency) 
            for currency, value in portfolio_values.items()
        )
        
        # Calculate combined total return for compatibility
        total_initial_usd = sum(
            self.currency_converter.convert_to_usd(self.portfolio['initial_capital'][currency], currency)
            for currency in ['USD', 'INR', 'MYR']
        )
        total_return_usd = total_value_usd - total_initial_usd
        total_return_pct = (total_return_usd / total_initial_usd) * 100 if total_initial_usd > 0 else 0
        
        # Calculate combined cash for compatibility
        total_cash_usd = sum(
            self.currency_converter.convert_to_usd(self.portfolio['cash'][currency], currency)
            for currency in ['USD', 'INR', 'MYR']
        )
        
        # Overall combined metrics (for compatibility)
        total_positions = sum(metrics['positions_count'] for metrics in currency_metrics.values())
        
        return {
            'currency_metrics': currency_metrics,
            'total_positions': total_positions,
            'total_trades': len(completed_trades),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'best_trade': best_trade,
            'worst_trade': worst_trade,
            'max_drawdown': max_drawdown,
            'total_value': total_value_usd,
            'total_return': total_return_usd,
            'total_return_pct': total_return_pct,
            'cash': total_cash_usd,
            'cash_balances': self.portfolio['cash'],
            'positions_count': total_positions,
            'portfolio_values': portfolio_values
        }
    
    def get_current_positions(self) -> List[Dict]:
        """Get current positions with P&L in original currencies"""
        positions = []
        for symbol, position in self.portfolio['positions'].items():
            # All calculations in original currency
            current_price = position['last_price']
            avg_price = position['avg_price']
            
            current_value = position['shares'] * current_price
            cost_basis = position['shares'] * avg_price
            unrealized_pnl = current_value - cost_basis
            unrealized_pnl_pct = (unrealized_pnl / cost_basis) * 100 if cost_basis > 0 else 0
            
            # Get target and stop loss prices
            target_price = position.get('target_price', avg_price * 1.10)
            stop_loss_price = position.get('stop_loss_price', avg_price * 0.95)
            
            # Calculate progress to target
            price_range = target_price - stop_loss_price
            current_progress = current_price - stop_loss_price
            progress_pct = (current_progress / price_range) * 100 if price_range > 0 else 0
            
            # Days held
            try:
                entry_date = datetime.fromisoformat(position['entry_date'])
                days_held = (datetime.now() - entry_date).days
            except:
                days_held = 0
            
            positions.append({
                'symbol': symbol,
                'shares': position['shares'],
                'avg_price': avg_price,
                'current_price': current_price,
                'target_price': target_price,
                'stop_loss_price': stop_loss_price,
                'current_value': current_value,
                'cost_basis': cost_basis,
                'unrealized_pnl': unrealized_pnl,
                'unrealized_pnl_pct': unrealized_pnl_pct,
                'progress_pct': progress_pct,
                'confidence': position['confidence'],
                'currency': position.get('currency', 'USD'),
                'entry_date': position['entry_date'],
                'days_held': days_held,
                'last_updated': position.get('last_updated', position['entry_date'])
            })
        
        return sorted(positions, key=lambda x: abs(x['unrealized_pnl_pct']), reverse=True)
    
    def get_portfolio_summary(self) -> dict:
        """Get comprehensive portfolio summary with performance metrics"""
        total_value = self.get_portfolio_value()
        initial_value = 10000.0  # Starting value
        total_return = ((total_value - initial_value) / initial_value) * 100
        
        # Get position details
        positions_summary = self.get_current_positions()
        
        # Calculate totals
        total_unrealized_pnl = sum(pos['unrealized_pnl'] for pos in positions_summary)
        
        # Analyze trade history
        wins = 0
        losses = 0
        total_realized_pnl = 0
        
        sell_trades = [t for t in self.portfolio['trade_history'] if t['action'] == 'SELL']
        for trade in sell_trades:
            # Handle backward compatibility for trade records
            pnl_value = trade.get('pnl_usd', trade.get('pnl', 0))
            total_realized_pnl += pnl_value
            if pnl_value > 0:
                wins += 1
            else:
                losses += 1
        
        total_trades = wins + losses
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        
        return {
            'total_value': total_value,
            'cash': self.portfolio['cash'],
            'total_return_pct': total_return,
            'total_return_amount': total_value - initial_value,
            'unrealized_pnl': total_unrealized_pnl,
            'realized_pnl': total_realized_pnl,
            'positions': positions_summary,
            'position_count': len(positions_summary),
            'total_trades': total_trades,
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'trade_history': self.portfolio['trade_history']
        }
    
    def should_sell_position(self, symbol: str, current_price: float) -> tuple:
        """Check if position should be sold based on stop-loss/take-profit"""
        if symbol not in self.portfolio['positions']:
            return False, ""
        
        position = self.portfolio['positions'][symbol]
        entry_price = position['avg_price']
        
        # Calculate percentage change
        pct_change = (current_price - entry_price) / entry_price * 100
        
        # Stop loss at -5%
        if pct_change <= -5:
            return True, "STOP_LOSS"
        
        # Take profit at +10%
        if pct_change >= 10:
            return True, "TAKE_PROFIT"
        
        return False, ""

    def reset_portfolio(self) -> dict:
        """Reset portfolio to initial state - clear positions and restore cash"""
        try:
            # Store current state for backup
            backup_data = {
                'positions_count': len(self.portfolio['positions']),
                'total_trades': len(self.portfolio.get('trade_history', [])),
                'cash_before': self.portfolio['cash'].copy(),
                'reset_date': datetime.now().isoformat()
            }
            
            # Reset to initial cash balances
            self.portfolio['cash'] = {
                'USD': 10000,
                'INR': 100000,
                'MYR': 10000
            }
            
            # Clear all positions
            self.portfolio['positions'] = {}
            
            # Update initial capital to match reset values
            self.portfolio['initial_capital'] = {
                'USD': 10000,
                'INR': 100000,
                'MYR': 10000
            }
            
            # Clear daily values (performance history)
            if 'daily_values' in self.portfolio:
                self.portfolio['daily_values'] = []
            
            # Save the reset portfolio
            self.save_portfolio()
            
            return {
                'success': True,
                'message': f"Portfolio reset successfully! Cleared {backup_data['positions_count']} positions and restored initial cash balances.",
                'backup_info': backup_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to reset portfolio: {str(e)}"
            }

    def clear_history(self) -> dict:
        """Clear all trading history but keep current positions"""
        try:
            history_count = len(self.portfolio.get('trade_history', []))
            
            # Clear trade history
            self.portfolio['trade_history'] = []
            
            # Clear daily values (performance history)
            if 'daily_values' in self.portfolio:
                self.portfolio['daily_values'] = []
            
            # Save the updated portfolio
            self.save_portfolio()
            
            return {
                'success': True,
                'message': f"Trading history cleared successfully! Removed {history_count} trade records."
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to clear history: {str(e)}"
            }

    def full_reset(self) -> dict:
        """Complete reset - clear positions, history, and restore cash"""
        try:
            # Store current state for backup
            backup_data = {
                'positions_count': len(self.portfolio['positions']),
                'total_trades': len(self.portfolio.get('trade_history', [])),
                'cash_before': self.portfolio['cash'].copy(),
                'reset_date': datetime.now().isoformat()
            }
            
            # Reset everything
            self.portfolio = {
                'cash': {
                    'USD': 10000,
                    'INR': 100000,
                    'MYR': 10000
                },
                'initial_capital': {
                    'USD': 10000,
                    'INR': 100000,
                    'MYR': 10000
                },
                'positions': {},
                'trade_history': [],
                'daily_values': [],
                'version': '2.0',
                'created_date': datetime.now().isoformat(),
                'last_reset': datetime.now().isoformat()
            }
            
            # Save the completely reset portfolio
            self.save_portfolio()
            
            return {
                'success': True,
                'message': f"Complete reset successful! Cleared {backup_data['positions_count']} positions, {backup_data['total_trades']} trades, and restored all cash balances.",
                'backup_info': backup_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to perform full reset: {str(e)}"
            }
