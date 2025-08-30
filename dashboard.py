"""
Swing Trading Dashboard - Comprehensive Web Interface
Run with: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
import time
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Trading configuration
TRADING_CONFIG = {
    'initial_capital': 10000,
    'max_positions': 8,
    'risk_per_trade': 0.02,  # 2% risk per trade
    'stop_loss_pct': 0.05,   # 5% stop loss
}

from tools.portfolio_manager import PaperTradingPortfolio
from tools.technical_analysis import TechnicalAnalyzer
from tools.enhanced_signals import get_daily_swing_signals, get_market_watchlists

# Helper functions for responsive design
def is_mobile():
    """Detect if user is on mobile device"""
    # For now, we'll use a simple check. In production, you could use user agent detection
    return st.session_state.get('mobile_view', False)

def create_responsive_columns(col_specs, mobile_stack=True):
    """Create responsive columns that stack on mobile"""
    if is_mobile() and mobile_stack:
        return [st.container() for _ in col_specs]
    else:
        return st.columns(col_specs)

def create_metric_card(title, value, delta=None, help_text=None):
    """Create a responsive metric card"""
    with st.container():
        if delta:
            st.metric(title, value, delta=delta, help=help_text)
        else:
            st.metric(title, value, help=help_text)

def create_expandable_section(title, content_func, expanded=False):
    """Create expandable sections for mobile-friendly display"""
    with st.expander(title, expanded=expanded):
        content_func()

def show_mobile_toggle():
    """Add mobile view toggle in sidebar"""
    st.sidebar.markdown("---")
    mobile_view = st.sidebar.checkbox("📱 Mobile View", value=st.session_state.get('mobile_view', False))
    st.session_state.mobile_view = mobile_view

# Page configuration
st.set_page_config(
    page_title="Swing Trading Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add responsive CSS for mobile optimization
st.markdown("""
<style>
    /* Mobile-first responsive design */
    .main .block-container {
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }
    
    /* Mobile optimization for small screens */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
        
        /* Stack columns on mobile */
        .stColumns > div {
            width: 100% !important;
            margin-bottom: 1rem;
        }
        
        /* Responsive metrics */
        .metric-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            padding: 0.5rem;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-bottom: 0.5rem;
        }
        
        /* Responsive tables */
        .dataframe {
            font-size: 0.8rem;
        }
        
        /* Sidebar auto-collapse on mobile */
        .css-1d391kg {
            width: 0px;
        }
        
        /* Tab adjustments for mobile */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.2rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.3rem 0.5rem;
            font-size: 0.8rem;
        }
    }
    
    /* Tablet optimization */
    @media (max-width: 1024px) and (min-width: 769px) {
        .stColumns > div {
            min-width: 300px;
        }
    }
    
    /* Enhanced metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Expandable sections for mobile */
    .mobile-section {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        margin-bottom: 1rem;
        overflow: hidden;
    }
    
    .mobile-section-header {
        background-color: #f8f9fa;
        padding: 0.75rem;
        cursor: pointer;
        font-weight: bold;
        border-bottom: 1px solid #e0e0e0;
    }
    
    .mobile-section-content {
        padding: 1rem;
    }
    
    /* Responsive charts */
    .js-plotly-plot {
        width: 100% !important;
    }
    
    /* Compact button styles */
    .stButton > button {
        width: 100%;
        margin-bottom: 0.5rem;
    }
    
    /* Responsive sidebar */
    @media (max-width: 768px) {
        .css-1d391kg {
            transform: translateX(-100%);
            transition: transform 0.3s ease;
        }
        
        .css-1d391kg.open {
            transform: translateX(0);
        }
    }
</style>
""", unsafe_allow_html=True)

class TradingDashboard:
    def __init__(self):
        self.analyzer = TechnicalAnalyzer()
        self.portfolio = PaperTradingPortfolio(initial_capital=TRADING_CONFIG['initial_capital'])
        
    def get_stock_analysis(self, symbol, period="6mo"):
        """Get comprehensive stock analysis"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            if len(data) < 50:
                return None
                
            # Calculate indicators
            data['SMA_20'] = self.analyzer.sma(data['Close'], 20)
            data['SMA_50'] = self.analyzer.sma(data['Close'], 50)
            data['RSI'] = self.analyzer.rsi(data['Close'])
            
            # MACD
            macd_data = self.analyzer.macd(data['Close'])
            data['MACD'] = macd_data['macd']
            data['MACD_Signal'] = macd_data['signal']
            
            # Bollinger Bands
            bb_data = self.analyzer.bollinger_bands(data['Close'])
            data['BB_Upper'] = bb_data['upper']
            data['BB_Lower'] = bb_data['lower']
            data['BB_Middle'] = bb_data['middle']
            
            # Generate signals
            latest = data.iloc[-1]
            signals = self.calculate_signals(data)
            
            return {
                'data': data,
                'latest': latest,
                'signals': signals,
                'symbol': symbol
            }
        except Exception as e:
            st.error(f"Error analyzing {symbol}: {e}")
            return None
    
    def calculate_signals(self, data):
        """Calculate trading signals and confidence"""
        latest = data.iloc[-1]
        prev = data.iloc[-2]
        
        signals = {}
        
        # Trend signals
        signals['sma_bullish'] = latest['SMA_20'] > latest['SMA_50']
        signals['price_above_sma20'] = latest['Close'] > latest['SMA_20']
        signals['sma_cross_up'] = (latest['SMA_20'] > latest['SMA_50'] and 
                                   prev['SMA_20'] <= prev['SMA_50'])
        
        # Momentum signals
        signals['rsi'] = latest['RSI']
        signals['rsi_oversold'] = latest['RSI'] < 30
        signals['rsi_overbought'] = latest['RSI'] > 70
        signals['rsi_bullish'] = 30 < latest['RSI'] < 70
        
        # MACD signals
        signals['macd_bullish'] = latest['MACD'] > latest['MACD_Signal']
        signals['macd_cross_up'] = (latest['MACD'] > latest['MACD_Signal'] and 
                                    prev['MACD'] <= prev['MACD_Signal'])
        
        # Bollinger Bands
        signals['bb_position'] = 'MIDDLE'
        if latest['Close'] < latest['BB_Lower']:
            signals['bb_position'] = 'LOWER'
        elif latest['Close'] > latest['BB_Upper']:
            signals['bb_position'] = 'UPPER'
        
        # Calculate confidence score
        confidence = self.calculate_confidence(signals)
        
        # Determine recommendation
        recommendation = self.get_recommendation(signals, confidence)
        
        signals['confidence'] = confidence
        signals['recommendation'] = recommendation
        
        return signals
    
    def calculate_confidence(self, signals):
        """Calculate confidence score 0-100"""
        score = 50  # Base score
        
        # Trend components (30 points)
        if signals['sma_bullish']: score += 15
        if signals['price_above_sma20']: score += 10
        if signals['sma_cross_up']: score += 20
        
        # Momentum components (25 points)
        if signals['macd_bullish']: score += 15
        if signals['macd_cross_up']: score += 20
        
        # Oscillator components (20 points)
        if signals['rsi_oversold']: score += 20
        elif signals['rsi_overbought']: score -= 20
        elif signals['rsi_bullish']: score += 10
        
        # Mean reversion (15 points)
        if signals['bb_position'] == 'LOWER': score += 15
        elif signals['bb_position'] == 'UPPER': score -= 15
        
        # Bearish adjustments
        if not signals['sma_bullish']: score -= 20
        if not signals['macd_bullish']: score -= 15
        
        return max(0, min(100, score))
    
    def get_recommendation(self, signals, confidence):
        """Get trading recommendation"""
        if confidence >= 80:
            if signals['sma_cross_up'] or (signals['sma_bullish'] and signals['rsi_oversold']):
                return 'STRONG BUY'
            elif not signals['sma_bullish'] and signals['rsi_overbought']:
                return 'STRONG SELL'
        elif confidence >= 70:
            if signals['sma_bullish'] and signals['macd_bullish']:
                return 'BUY'
            elif not signals['sma_bullish'] and not signals['macd_bullish']:
                return 'SELL'
        elif confidence <= 30:
            return 'STRONG SELL'
        elif confidence <= 40:
            return 'SELL'
        
        return 'HOLD'

def main():
    dashboard = TradingDashboard()
    
    # Sidebar
    st.sidebar.title("🎯 Trading Controls")
    
    # Mobile view toggle
    show_mobile_toggle()
    
    # Market selection
    selected_market = st.sidebar.selectbox(
        "Select Market",
        ["All Markets", "🇺🇸 USA", "🇮🇳 India", "🇲🇾 Malaysia"]
    )
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data", type="primary"):
        st.cache_data.clear()
        # Force reload portfolio from disk
        dashboard.portfolio = PaperTradingPortfolio(initial_capital=TRADING_CONFIG['initial_capital'])
        st.success("✅ Data refreshed!")
        st.rerun()
    
    # Portfolio actions
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Portfolio Actions")
    
    if st.sidebar.button("📈 Update Positions"):
        dashboard.portfolio.update_positions()
        # Reload portfolio from disk to ensure fresh data
        dashboard.portfolio = PaperTradingPortfolio(initial_capital=TRADING_CONFIG['initial_capital'])
        st.sidebar.success("Positions updated!")
    
    # Main content
    st.title("📈 Swing Trading Dashboard")
    st.markdown("*Real-time signals, portfolio tracking, and performance analytics*")
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🎯 Live Signals", 
        "💼 Portfolio", 
        "📊 Analytics",
        "🏆 Performance",
        "📜 Trade History",
        "⚙️ Settings"
    ])
    
    with tab1:
        show_live_signals(dashboard, selected_market)
    
    with tab2:
        show_portfolio(dashboard)
    
    with tab3:
        show_performance(dashboard)
    
    with tab4:
        show_charts(dashboard)
    
    with tab5:
        show_trade_history(dashboard)
    
    with tab6:
        show_portfolio_settings(dashboard)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_market_signals(market_filter):
    """Get signals for selected market"""
    dashboard = TradingDashboard()
    
    if market_filter == "All Markets":
        markets = get_market_watchlists()
    elif market_filter == "🇺🇸 USA":
        watchlists = get_market_watchlists()
        markets = {"usa": watchlists["usa"]}
    elif market_filter == "🇮🇳 India":
        watchlists = get_market_watchlists()
        markets = {"india": watchlists["india"]}
    elif market_filter == "🇲🇾 Malaysia":
        watchlists = get_market_watchlists()
        markets = {"malaysia": watchlists["malaysia"]}

    all_signals = []
    processed_symbols = set()  # Track processed symbols to avoid duplicates
    
    for market_name, symbols in markets.items():
        for symbol in symbols[:8]:  # Limit to 8 stocks per market for performance
            if symbol in processed_symbols:
                continue
            processed_symbols.add(symbol)
            
            analysis = dashboard.get_stock_analysis(symbol)
            if analysis:
                signals = analysis['signals']
                latest = analysis['latest']
                
                # Determine currency and price display
                if symbol.endswith('.NS') or symbol.endswith('.BO'):
                    currency = 'INR'
                    # yfinance already provides Indian stocks in INR
                    price_display = f"₹{latest['Close']:,.2f}"
                    raw_price = latest['Close']
                elif symbol.endswith('.KL'):
                    currency = 'MYR'
                    # yfinance already provides Malaysian stocks in MYR
                    price_display = f"RM{latest['Close']:,.2f}"
                    raw_price = latest['Close']
                else:
                    currency = 'USD'
                    price_display = f"${latest['Close']:,.2f}"
                    raw_price = latest['Close']
                
                all_signals.append({
                    'Symbol': symbol,
                    'Market': market_name.title(),
                    'Price': price_display,
                    'Price_Raw': raw_price,
                    'Currency': currency,
                    'Signal': signals['recommendation'],
                    'Confidence': f"{signals['confidence']}%",
                    'RSI': f"{signals['rsi']:.1f}",
                    'Trend': '📈' if signals['sma_bullish'] else '📉',
                    'MACD': '🟢' if signals['macd_bullish'] else '🔴',
                    'BB_Position': signals['bb_position'],
                    'confidence_num': signals['confidence']
                })
    
    return all_signals

def show_live_signals(dashboard, selected_market):
    """Display enhanced swing trading signals with portfolio analysis"""
    st.header("🎯 Daily Swing Trading Signals")
    
    # Initialize session state for swing data if not exists
    if 'swing_data' not in st.session_state:
        st.session_state.swing_data = None
        st.session_state.last_scan_time = None
    
    # Manual refresh controls at the top
    col_refresh1, col_refresh2, col_refresh3 = st.columns([1, 1, 2])
    
    with col_refresh1:
        manual_refresh = st.button("🔄 Refresh Signals", type="primary", help="Manually refresh swing trading signals")
    
    with col_refresh2:
        if st.session_state.last_scan_time:
            st.write(f"⏰ Last scan: {st.session_state.last_scan_time.strftime('%H:%M:%S')}")
        else:
            st.write("⏰ No data loaded")
    
    with col_refresh3:
        st.info("💡 Use 'Refresh Signals' button to update data. No auto-refresh to prevent interruptions.")
        
        # Show recent activity
        if 'recent_trades' in st.session_state and st.session_state.recent_trades:
            with st.expander("📝 Recent Activity", expanded=False):
                for trade in st.session_state.recent_trades[-3:]:  # Show last 3
                    st.write(f"• {trade}")
                if st.button("Clear Activity", key="clear_activity"):
                    st.session_state.recent_trades = []
    
    # Only fetch new data if manual refresh is clicked or no data exists
    if manual_refresh or st.session_state.swing_data is None:
        with st.spinner("🔍 Analyzing swing opportunities across markets..."):
            from tools.enhanced_signals import get_daily_swing_signals, get_portfolio_analysis
            
            # Get cached market data
            st.session_state.swing_data = get_daily_swing_signals()
            
            # Get fresh portfolio analysis (not cached)
            if st.session_state.swing_data and dashboard.portfolio:
                st.session_state.swing_data['portfolio_analysis'] = get_portfolio_analysis(dashboard.portfolio)
            
            st.session_state.last_scan_time = datetime.now()
        
        if st.session_state.swing_data:
            st.success("✅ Signals updated successfully!")
        else:
            st.error("❌ Failed to fetch signals. Please try again.")
    
    swing_data = st.session_state.swing_data
    
    if not swing_data:
        st.warning("🔄 Please click 'Refresh Signals' to load swing trading opportunities.")
        return

    # Summary metrics - Responsive layout
    total_opportunities = sum(len(market['opportunities']) for market in swing_data['markets'].values())
    strong_setups = sum(len([opp for opp in market['opportunities'] if opp['swing_score'] >= 70]) 
                       for market in swing_data['markets'].values())
    
    # Create responsive metric cards
    if is_mobile():
        # Stack metrics vertically on mobile
        create_metric_card("🔍 Total Opportunities", total_opportunities)
        create_metric_card("💪 Strong Setups (70+)", strong_setups)
        
        portfolio_positions = len(swing_data.get('portfolio_analysis', []))
        create_metric_card("📊 Portfolio Positions", portfolio_positions)
        
        last_update = swing_data['timestamp'].strftime("%H:%M")
        create_metric_card("🕒 Last Update", last_update)
    else:
        # Use columns for desktop
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🔍 Total Opportunities", total_opportunities)
        
        with col2:
            st.metric("💪 Strong Setups (70+)", strong_setups)
        
        with col3:
            portfolio_positions = len(swing_data.get('portfolio_analysis', []))
            st.metric("📊 Portfolio Positions", portfolio_positions)
        
        with col4:
            last_update = swing_data['timestamp'].strftime("%H:%M")
            st.metric("🕒 Last Update", last_update)
    
    # Portfolio positions analysis (if any) - Mobile-responsive
    if swing_data.get('portfolio_analysis'):
        
        def show_portfolio_analysis():
            st.markdown("**Your existing positions with updated swing analysis:**")
            
            for position in swing_data['portfolio_analysis']:
                symbol = position['symbol']
                action = position['action']
                pnl_pct = position['pnl_pct']
                current_price = position['current_price']
                
                # Color coding for actions
                if action in ['SELL', 'PARTIAL_SELL']:
                    action_color = "🟢"
                    action_text = f"**{action}**"
                elif action in ['STOP_LOSS', 'WATCH_CLOSE']:
                    action_color = "🔴"
                    action_text = f"**{action}**"
                else:
                    action_color = "🟡"
                    action_text = action
                
                # Price formatting
                if '.NS' in symbol:
                    price_str = f"₹{current_price:.2f}"
                elif '.KL' in symbol:
                    price_str = f"RM{current_price:.2f}"
                else:
                    price_str = f"${current_price:.2f}"
                
                with st.expander(f"{action_color} {symbol} | {price_str} | P&L: {pnl_pct:+.1f}% | {action_text}"):
                    if is_mobile():
                        # Stack vertically on mobile
                        st.write("**Position Details:**")
                        st.write(f"• Entry Price: {price_str.replace(str(current_price), str(position['entry_price']))}")
                        st.write(f"• Shares: {position['shares']}")
                        st.write(f"• Current P&L: {pnl_pct:+.1f}%")
                        
                        st.write("**Analysis Signals:**")
                        for signal in position['signals'][:3]:
                            st.write(f"• {signal}")
                        
                        # Action buttons - mobile layout
                        st.write("**Actions:**")
                        if action == 'SELL':
                            if st.button(f"🔴 SELL ALL {symbol}", key=f"sell_{symbol}"):
                                result = dashboard.portfolio.sell_stock(symbol, current_price, 
                                                                      shares=position['shares'], 
                                                                      reason="SWING_SIGNAL")
                                if result['success']:
                                    st.success(f"✅ {result['message']}")
                                    st.rerun()
                                else:
                                    st.error(f"❌ {result['message']}")
                        
                        elif action == 'PARTIAL_SELL':
                            sell_qty = st.number_input(f"Shares to sell ({symbol}):", 
                                                     min_value=1, 
                                                     max_value=position['shares'],
                                                     value=min(position['shares'] // 2, 10),
                                                     key=f"partial_{symbol}")
                            if st.button(f"📉 PARTIAL SELL {symbol}", key=f"partial_sell_{symbol}"):
                                result = dashboard.portfolio.sell_stock(symbol, current_price, 
                                                                      shares=sell_qty, 
                                                                      reason="PARTIAL_PROFIT")
                                if result['success']:
                                    st.success(f"✅ {result['message']}")
                                    st.rerun()
                                else:
                                    st.error(f"❌ {result['message']}")
                    else:
                        # Use columns for desktop
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Position Details:**")
                            st.write(f"• Entry Price: {price_str.replace(str(current_price), str(position['entry_price']))}")
                            st.write(f"• Shares: {position['shares']}")
                            st.write(f"• Current P&L: {pnl_pct:+.1f}%")
                        
                        with col2:
                            st.write("**Analysis Signals:**")
                            for signal in position['signals'][:3]:
                                st.write(f"• {signal}")
                        
                        # Action buttons - desktop layout
                        if action == 'SELL':
                            if st.button(f"🔴 SELL ALL {symbol}", key=f"sell_{symbol}"):
                                result = dashboard.portfolio.sell_stock(symbol, current_price, 
                                                                      shares=position['shares'], 
                                                                      reason="SWING_SIGNAL")
                                if result['success']:
                                    st.success(f"✅ {result['message']}")
                                    st.rerun()
                                else:
                                    st.error(f"❌ {result['message']}")
                        
                        elif action == 'PARTIAL_SELL':
                            sell_col1, sell_col2 = st.columns(2)
                            with sell_col1:
                                sell_qty = st.number_input(f"Shares to sell ({symbol}):", 
                                                         min_value=1, 
                                                         max_value=position['shares'],
                                                         value=min(position['shares'] // 2, 10),
                                                         key=f"partial_{symbol}")
                            with sell_col2:
                                if st.button(f"📉 PARTIAL SELL {symbol}", key=f"partial_sell_{symbol}"):
                                    result = dashboard.portfolio.sell_stock(symbol, current_price, 
                                                                          shares=sell_qty, 
                                                                          reason="PARTIAL_PROFIT")
                                    if result['success']:
                                        st.success(f"✅ {result['message']}")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {result['message']}")
        
        if is_mobile():
            create_expandable_section("🎯 Current Portfolio Analysis", show_portfolio_analysis, expanded=True)
        else:
            st.subheader("🎯 Current Portfolio Analysis")
            show_portfolio_analysis()
        
        st.markdown("---")
    
    # Market opportunities - Mobile responsive
    def show_market_opportunities():
        for market_key, market_data in swing_data['markets'].items():
            market_name = market_data['name']
            opportunities = market_data['opportunities']
            
            if opportunities:
                
                def show_market_data():
                    if is_mobile():
                        # Mobile-friendly card layout
                        for i, opp in enumerate(opportunities, 1):
                            symbol = opp['symbol']
                            price = opp['current_price']
                            score = opp['swing_score']
                            recommendation = opp['recommendation']
                            entry_type = opp['entry_type']
                            risk_reward = opp['risk_reward']
                            
                            # Format price
                            if '.NS' in symbol:
                                price_str = f"₹{price:.2f}"
                            elif '.KL' in symbol:
                                price_str = f"RM{price:.2f}"
                            else:
                                price_str = f"${price:.2f}"
                            
                            # Color code based on score
                            if score >= 80:
                                score_color = "🟢"
                            elif score >= 60:
                                score_color = "🟡"
                            else:
                                score_color = "🔴"
                            
                            with st.container():
                                st.markdown(f"""
                                **#{i} {symbol}** {score_color} **Score: {score}**
                                - **Price**: {price_str}
                                - **Signal**: {recommendation}
                                - **Setup**: {entry_type}  
                                - **Risk:Reward**: {risk_reward}
                                - **Signals**: {', '.join(opp['signals'][:2])}
                                """)
                                
                                # Buy button for mobile
                                if st.button(f"🟢 BUY {symbol}", key=f"buy_{symbol}_{market_key}"):
                                    st.session_state.selected_stock_for_buy = opp
                                    st.rerun()
                                
                                st.markdown("---")
                    
                    else:
                        # Desktop table layout
                        display_data = []
                        for opp in opportunities:
                            symbol = opp['symbol']
                            price = opp['current_price']
                            score = opp['swing_score']
                            recommendation = opp['recommendation']
                            entry_type = opp['entry_type']
                            risk_reward = opp['risk_reward']
                            
                            # Format price
                            if '.NS' in symbol:
                                price_str = f"₹{price:.2f}"
                            elif '.KL' in symbol:
                                price_str = f"RM{price:.2f}"
                            else:
                                price_str = f"${price:.2f}"
                            
                            display_data.append({
                                'Symbol': symbol,
                                'Price': price_str,
                                'Score': score,
                                'Signal': recommendation,
                                'Setup': entry_type,
                                'R:R': risk_reward,
                                'Key Signals': ', '.join(opp['signals'][:2])
                            })
                        
                        df = pd.DataFrame(display_data)
                        st.dataframe(df, use_container_width=True)
                        
                        # Action buttons for desktop
                        if len(opportunities) > 0:
                            st.markdown("**Quick Actions:**")
                            action_cols = create_responsive_columns([1]*min(5, len(opportunities)), mobile_stack=False)
                            
                            for i, (col, opp) in enumerate(zip(action_cols, opportunities[:5])):
                                with col:
                                    if st.button(f"🟢 BUY {opp['symbol']}", key=f"buy_{opp['symbol']}_{market_key}"):
                                        st.session_state.selected_stock_for_buy = opp
                                        st.rerun()
                
                if is_mobile():
                    create_expandable_section(f"{market_name} ({len(opportunities)} opportunities)", show_market_data, expanded=True)
                else:
                    st.markdown(f"### {market_name}")
                    show_market_data()
            
            else:
                if not is_mobile():
                    st.info(f"No strong swing opportunities found in {market_name} market today.")
    
    if is_mobile():
        create_expandable_section("🌍 Market Opportunities", show_market_opportunities, expanded=True)
    else:
        st.subheader("🌍 Top 5 Swing Opportunities by Market")
        show_market_opportunities()
    
    # Market scanning summary - Responsive
    def show_scanning_summary():
        if is_mobile():
            # Stack summary vertically on mobile
            for market_key, market_data in swing_data['markets'].items():
                market_name = market_data['name']
                scanned = market_data['total_scanned']
                found = market_data['opportunities_found']
                
                create_metric_card(
                    f"{market_name}",
                    f"{found} opportunities",
                    f"from {scanned} stocks"
                )
        else:
            # Use columns for desktop
            summary_cols = st.columns(3)
            for i, (market_key, market_data) in enumerate(swing_data['markets'].items()):
                with summary_cols[i % 3]:
                    market_name = market_data['name']
                    scanned = market_data['total_scanned']
                    found = market_data['opportunities_found']
                    
                    st.metric(
                        f"{market_name}",
                        f"{found} opportunities",
                        f"from {scanned} stocks"
                    )
    
    st.markdown("---")
    if is_mobile():
        create_expandable_section("📊 Scanning Summary", show_scanning_summary, expanded=False)
    else:
        st.subheader("📊 Scanning Summary")
        show_scanning_summary()
    
    summary_cols = st.columns(3)
    for i, (market_key, market_data) in enumerate(swing_data['markets'].items()):
        with summary_cols[i]:
            market_name = market_data['name']
            scanned = market_data['total_scanned']
            found = market_data['opportunities_found']
            
            st.metric(
                f"{market_name}",
                f"{found} opportunities",
                f"from {scanned} stocks"
            )
    
    # Data management section
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh All Data", type="secondary", help="Refresh all swing signals"):
            # Clear cached data and refresh
            st.session_state.swing_data = None
            st.rerun()
    
    with col2:
        if st.button("🧹 Clear Cache", help="Clear all cached analysis data"):
            # Clear streamlit cache
            st.cache_data.clear()
            st.success("✅ Cache cleared")
    
    with col3:
        scan_time = st.session_state.last_scan_time
        if scan_time:
            time_ago = (datetime.now() - scan_time).total_seconds() / 60
            st.write(f"🕐 Data age: {time_ago:.1f} minutes")
        else:
            st.write("🕐 No data loaded")
    
    # Show watchlist if exists
    if 'watchlist' in st.session_state and st.session_state.watchlist:
        st.markdown("---")
        with st.expander("👁️ Your Watchlist", expanded=False):
            watchlist_col1, watchlist_col2 = st.columns([3, 1])
            
            with watchlist_col1:
                for symbol in st.session_state.watchlist:
                    st.write(f"• {symbol}")
            
            with watchlist_col2:
                if st.button("Clear Watchlist", key="clear_watchlist"):
                    st.session_state.watchlist = []
                    st.success("✅ Watchlist cleared")
    
    # Detailed Technical Analysis Section
    st.markdown("---")
    st.header("📈 Detailed Stock Analysis")
    st.markdown("**Comprehensive technical analysis for all swing opportunities with charts, levels, and clear justification**")
    
    # Analysis selection
    all_opportunities = []
    for market_key, market_data in swing_data['markets'].items():
        for opp in market_data['opportunities']:
            opp['market_name'] = market_data['name']
            all_opportunities.append(opp)
    
    if all_opportunities:
        # Sort by swing score for better organization
        all_opportunities.sort(key=lambda x: x['swing_score'], reverse=True)
        
        # Initialize session state for detailed analysis selections
        if 'selected_stocks_for_analysis' not in st.session_state:
            st.session_state.selected_stocks_for_analysis = []
        if 'analysis_depth' not in st.session_state:
            st.session_state.analysis_depth = "Comprehensive"
        
        # Stock selection for detailed analysis - Responsive
        stock_symbols = [f"{opp['symbol']} ({opp['market_name']}) - Score: {opp['swing_score']}" for opp in all_opportunities]
        
        if is_mobile():
            # Mobile layout - stack controls vertically
            st.markdown("🔍 **Select stocks for detailed analysis:**")
            default_selection = stock_symbols[:3] if not st.session_state.selected_stocks_for_analysis else st.session_state.selected_stocks_for_analysis
            
            selected_stocks = st.multiselect(
                "Choose up to 5 stocks:",
                stock_symbols,
                default=[s for s in default_selection if s in stock_symbols],
                help="Choose up to 5 stocks for comprehensive technical analysis",
                key="detailed_analysis_selector"
            )
            
            analysis_depth = st.selectbox(
                "📊 Analysis Depth:",
                ["Essential", "Comprehensive", "Expert"],
                index=["Essential", "Comprehensive", "Expert"].index(st.session_state.analysis_depth),
                help="Essential: Key levels only | Comprehensive: Full analysis | Expert: All indicators",
                key="analysis_depth_selector"
            )
        else:
            # Desktop layout - use columns
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Use session state for persistence
                default_selection = stock_symbols[:3] if not st.session_state.selected_stocks_for_analysis else st.session_state.selected_stocks_for_analysis
                
                selected_stocks = st.multiselect(
                    "🔍 Select stocks for detailed analysis:",
                    stock_symbols,
                    default=[s for s in default_selection if s in stock_symbols],  # Filter valid options
                    help="Choose up to 5 stocks for comprehensive technical analysis",
                    key="detailed_analysis_selector"
                )
            
            with col2:
                analysis_depth = st.selectbox(
                    "📊 Analysis Depth:",
                    ["Essential", "Comprehensive", "Expert"],
                    index=["Essential", "Comprehensive", "Expert"].index(st.session_state.analysis_depth),
                    help="Essential: Key levels only | Comprehensive: Full analysis | Expert: All indicators",
                    key="analysis_depth_selector"
                )
        
        # Update session state
        st.session_state.selected_stocks_for_analysis = selected_stocks
        st.session_state.analysis_depth = analysis_depth
        
        # Generate detailed analysis for selected stocks
        for stock_option in selected_stocks[:5]:  # Limit to 5 for performance
            # Extract symbol from the option string
            symbol = stock_option.split(' (')[0]
            selected_stock = next(opp for opp in all_opportunities if opp['symbol'] == symbol)
            
            # Create detailed analysis section
            with st.expander(f"📊 **{symbol}** - Detailed Technical Analysis", expanded=True):
                
                # Header with key metrics
                score = selected_stock['swing_score']
                price = selected_stock['current_price']
                market_name = selected_stock['market_name']
                entry_type = selected_stock['entry_type']
                recommendation = selected_stock['recommendation']
                
                # Currency formatting
                if '.NS' in symbol:
                    currency_symbol = "₹"
                elif '.KL' in symbol:
                    currency_symbol = "RM"
                else:
                    currency_symbol = "$"
                
                # Main metrics row - Mobile Responsive
                if is_mobile():
                    # Mobile: Stack metrics in 2x2 + 1 layout
                    metric_row1_col1, metric_row1_col2 = st.columns(2)
                    with metric_row1_col1:
                        score_color = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
                        st.metric("Swing Score", f"{score_color} {score}/100")
                    with metric_row1_col2:
                        st.metric("Current Price", f"{currency_symbol}{price:.2f}")
                    
                    metric_row2_col1, metric_row2_col2 = st.columns(2)
                    with metric_row2_col1:
                        st.metric("Market", market_name)
                    with metric_row2_col2:
                        signal_color = "🟢" if recommendation == "STRONG BUY" else "🟡"
                        st.metric("Signal", f"{signal_color} {recommendation}")
                    
                    # Setup type in its own row
                    st.metric("Setup Type", entry_type)
                else:
                    # Desktop: 5-column layout
                    metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)
                    
                    with metric_col1:
                        score_color = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
                        st.metric("Swing Score", f"{score_color} {score}/100")
                    
                    with metric_col2:
                        st.metric("Current Price", f"{currency_symbol}{price:.2f}")
                    
                    with metric_col3:
                        st.metric("Market", market_name)
                    
                    with metric_col4:
                        signal_color = "🟢" if recommendation == "STRONG BUY" else "🟡"
                        st.metric("Signal", f"{signal_color} {recommendation}")
                    
                    with metric_col5:
                        st.metric("Setup Type", entry_type)
                
                # Detailed analysis sections - Mobile Responsive
                if is_mobile():
                    # Mobile: Use expandable sections for better organization
                    with st.container():
                        # Support & Resistance Analysis
                        with st.expander("🎯 Support & Resistance Levels", expanded=True):
                            # Get detailed levels from the analysis
                            support_levels = selected_stock.get('support_levels', [price * 0.95, price * 0.90])
                            resistance_levels = selected_stock.get('resistance_levels', [price * 1.05, price * 1.10])
                            
                            # Current position relative to levels
                            nearest_support = max([level for level in support_levels if level <= price], default=price * 0.95)
                            nearest_resistance = min([level for level in resistance_levels if level >= price], default=price * 1.05)
                            
                            support_distance = ((price - nearest_support) / price) * 100
                            resistance_distance = ((nearest_resistance - price) / price) * 100
                            
                            # Support levels
                            st.markdown("**🟢 Support Levels:**")
                            for i, level in enumerate(sorted(support_levels, reverse=True)[:3]):
                                distance = ((price - level) / price) * 100
                                strength = "Strong" if i == 0 else "Medium" if i == 1 else "Weak"
                                st.write(f"• **{strength}**: {currency_symbol}{level:.2f} ({distance:+.1f}%)")
                            
                            # Resistance levels  
                            st.markdown("**🔴 Resistance Levels:**")
                            for i, level in enumerate(sorted(resistance_levels)[:3]):
                                distance = ((level - price) / price) * 100
                                strength = "Strong" if i == 0 else "Medium" if i == 1 else "Weak"
                                st.write(f"• **{strength}**: {currency_symbol}{level:.2f} (+{distance:.1f}%)")
                            
                            # Position analysis
                            st.markdown("**📍 Current Position:**")
                            if support_distance <= 3:
                                st.success(f"✅ Near Support ({support_distance:.1f}% above)")
                            elif resistance_distance <= 3:
                                st.warning(f"⚠️ Near Resistance ({resistance_distance:.1f}% below)")
                            else:
                                st.info("🎯 In middle range - good for swing entry")
                else:
                    # Desktop: Three-column layout for detailed analysis
                    analysis_col1, analysis_col2, analysis_col3 = st.columns([1, 1, 1])
                    
                    # Column 1: Support & Resistance Analysis
                    with analysis_col1:
                        st.markdown("### 🎯 **Support & Resistance Levels**")
                    
                    # Get detailed levels from the analysis
                    support_levels = selected_stock.get('support_levels', [price * 0.95, price * 0.90])
                    resistance_levels = selected_stock.get('resistance_levels', [price * 1.05, price * 1.10])
                    
                    # Current position relative to levels
                    nearest_support = max([level for level in support_levels if level <= price], default=price * 0.95)
                    nearest_resistance = min([level for level in resistance_levels if level >= price], default=price * 1.05)
                    
                    support_distance = ((price - nearest_support) / price) * 100
                    resistance_distance = ((nearest_resistance - price) / price) * 100
                    
                    # Support levels
                    st.markdown("**🟢 Support Levels:**")
                    for i, level in enumerate(sorted(support_levels, reverse=True)[:3]):
                        distance = ((price - level) / price) * 100
                        strength = "Strong" if i == 0 else "Medium" if i == 1 else "Weak"
                        st.write(f"• **{strength}**: {currency_symbol}{level:.2f} ({distance:+.1f}%)")
                    
                    # Resistance levels  
                    st.markdown("**🔴 Resistance Levels:**")
                    for i, level in enumerate(sorted(resistance_levels)[:3]):
                        distance = ((level - price) / price) * 100
                        strength = "Strong" if i == 0 else "Medium" if i == 1 else "Weak"
                        st.write(f"• **{strength}**: {currency_symbol}{level:.2f} (+{distance:.1f}%)")
                    
                    # Position analysis
                    st.markdown("**📍 Current Position:**")
                    if support_distance <= 3:
                        st.success(f"✅ Near Support ({support_distance:.1f}% above)")
                    elif resistance_distance <= 3:
                        st.warning(f"⚠️ Near Resistance ({resistance_distance:.1f}% below)")
                    else:
                        st.info("🎯 In middle range - good for swing entry")
                
                # Column 2: Technical Indicators
                with analysis_col2:
                    st.markdown("### 📊 **Technical Indicators**")
                    
                    # Get technical data from enhanced analysis
                    rsi = selected_stock.get('rsi', 45 + (score - 50) * 0.6)
                    macd_signal = selected_stock.get('macd_signal_trend', 'Bullish' if score > 60 else 'Bearish')
                    volume_trend = selected_stock.get('volume_trend', 'High' if score > 70 else 'Normal')
                    bollinger = selected_stock.get('bollinger_bands', {})
                    stochastic = selected_stock.get('stochastic', 50)
                    trend_strength = selected_stock.get('trend_strength', 'Neutral')
                    momentum = selected_stock.get('momentum', 0)
                    volatility = selected_stock.get('volatility', 20)
                    
                    # RSI Analysis
                    st.markdown("**📈 RSI (14-day):**")
                    rsi_color = "🟢" if 30 <= rsi <= 70 else "🔴" if rsi > 70 else "🟡"
                    rsi_signal = "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral"
                    st.write(f"{rsi_color} **{rsi:.1f}** - {rsi_signal}")
                    
                    # MACD Analysis
                    st.markdown("**📊 MACD Signal:**")
                    macd_color = "🟢" if macd_signal == 'Bullish' else "🔴"
                    st.write(f"{macd_color} **{macd_signal}** momentum")
                    
                    # Moving Averages
                    st.markdown("**📈 Moving Averages:**")
                    sma_20 = selected_stock.get('sma_20', price)
                    sma_50 = selected_stock.get('sma_50', price)
                    ma20_pos = "Above" if price > sma_20 else "Below"
                    ma50_pos = "Above" if price > sma_50 else "Below"
                    ma20_color = "🟢" if ma20_pos == "Above" else "🔴"
                    ma50_color = "🟢" if ma50_pos == "Above" else "🔴"
                    st.write(f"{ma20_color} **MA(20)**: {ma20_pos} ({currency_symbol}{sma_20:.2f})")
                    st.write(f"{ma50_color} **MA(50)**: {ma50_pos} ({currency_symbol}{sma_50:.2f})")
                    
                    # Volume Analysis
                    st.markdown("**📊 Volume Analysis:**")
                    vol_color = "🟢" if volume_trend == 'High' else "🟡" if volume_trend == 'Normal' else "🔴"
                    st.write(f"{vol_color} **Volume**: {volume_trend}")
                    
                    if analysis_depth in ["Comprehensive", "Expert"]:
                        # Additional indicators for comprehensive analysis
                        st.markdown("**🔄 Additional Signals:**")
                        
                        # Stochastic
                        stoch_signal = "Overbought" if stochastic > 80 else "Oversold" if stochastic < 20 else "Neutral"
                        st.write(f"• **Stochastic**: {stochastic:.1f} ({stoch_signal})")
                        
                        # Trend strength
                        trend_color = "🟢" if "Up" in trend_strength else "🔴" if "Down" in trend_strength else "🟡"
                        st.write(f"• **Trend**: {trend_color} {trend_strength}")
                        
                        # Momentum
                        momentum_color = "🟢" if momentum > 0 else "🔴"
                        st.write(f"• **Momentum**: {momentum_color} {momentum:+.1f}%")
                        
                        # Volatility
                        vol_level = "High" if volatility > 30 else "Low" if volatility < 15 else "Normal"
                        st.write(f"• **Volatility**: {volatility:.1f}% ({vol_level})")
                
                    if analysis_depth == "Expert":
                        # Expert level indicators
                        st.markdown("**🎯 Expert Indicators:**")
                        
                        # Bollinger Band position
                        if bollinger:
                            bb_position = ((price - bollinger.get('lower', price)) / 
                                         (bollinger.get('upper', price) - bollinger.get('lower', price))) * 100
                            bb_signal = "Upper" if bb_position > 75 else "Lower" if bb_position < 25 else "Middle"
                            st.write(f"• **BB Position**: {bb_position:.0f}% ({bb_signal})")
                        
                        # Volume ratio
                        volume_ratio = selected_stock.get('volume_ratio', 1.0)
                        st.write(f"• **Volume Ratio**: {volume_ratio:.1f}x average")
                        
                        # Risk metrics
                        st.write(f"• **Risk Level**: {'High' if volatility > 25 else 'Medium' if volatility > 15 else 'Low'}")
                
                # Column 3: Trade Setup & Risk Management
                with analysis_col3:
                    st.markdown("### 🎯 **Trade Setup & Risk Management**")
                    
                    # Entry price and timing
                    entry_price = price
                    target_price = nearest_resistance
                    stop_loss = nearest_support
                    
                    # Risk/Reward calculation
                    potential_gain = target_price - entry_price
                    potential_loss = entry_price - stop_loss
                    risk_reward = potential_gain / potential_loss if potential_loss > 0 else 0
                    
                    st.markdown("**🎯 Entry Strategy:**")
                    st.write(f"• **Entry Price**: {currency_symbol}{entry_price:.2f}")
                    st.write(f"• **Entry Type**: {entry_type}")
                    st.write(f"• **Best Time**: Market open or breakout")
                    
                    st.markdown("**🎯 Targets & Stops:**")
                    gain_pct = (potential_gain / entry_price) * 100
                    loss_pct = (potential_loss / entry_price) * 100
                    
                    st.write(f"• **Target 1**: {currency_symbol}{target_price:.2f} (+{gain_pct:.1f}%)")
                    if len(resistance_levels) > 1:
                        target2 = sorted(resistance_levels)[1] if len(resistance_levels) > 1 else target_price * 1.05
                        gain2_pct = ((target2 - entry_price) / entry_price) * 100
                        st.write(f"• **Target 2**: {currency_symbol}{target2:.2f} (+{gain2_pct:.1f}%)")
                    
                    st.write(f"• **Stop Loss**: {currency_symbol}{stop_loss:.2f} (-{loss_pct:.1f}%)")
                    
                    # Position sizing suggestion
                    st.markdown("**💰 Position Sizing:**")
                    risk_per_trade = 2  # 2% risk per trade
                    account_size = 10000  # Base calculation
                    max_loss = account_size * (risk_per_trade / 100)
                    shares = int(max_loss / potential_loss) if potential_loss > 0 else 10
                    
                    st.write(f"• **Suggested Size**: {shares} shares")
                    st.write(f"• **Investment**: {currency_symbol}{shares * entry_price:,.0f}")
                    st.write(f"• **Max Risk**: {currency_symbol}{max_loss:.0f} ({risk_per_trade}%)")
                    
                    # Enhanced Profit/Loss Calculations
                    st.markdown("---")
                    st.markdown("**💰 Profit/Loss Projections:**")
                    
                    # Target 1 P&L
                    target1_profit = shares * (target_price - entry_price)
                    target1_profit_pct = ((target_price - entry_price) / entry_price) * 100
                    
                    # Target 2 P&L (if exists)
                    if len(resistance_levels) > 1:
                        target2 = sorted(resistance_levels)[1] if len(resistance_levels) > 1 else target_price * 1.05
                        target2_profit = shares * (target2 - entry_price)
                        target2_profit_pct = ((target2 - entry_price) / entry_price) * 100
                    
                    # Stop Loss P&L
                    stop_loss_amount = shares * (stop_loss - entry_price)
                    stop_loss_pct = ((stop_loss - entry_price) / entry_price) * 100
                    
                    # Display projections
                    st.markdown("**🎯 If Target 1 Hit:**")
                    profit_color = "🟢" if target1_profit > 0 else "🔴"
                    st.write(f"{profit_color} **Profit**: {currency_symbol}{target1_profit:,.0f} (+{target1_profit_pct:.1f}%)")
                    st.write(f"📈 **Total Value**: {currency_symbol}{(shares * entry_price) + target1_profit:,.0f}")
                    
                    if len(resistance_levels) > 1:
                        st.markdown("**🎯 If Target 2 Hit:**")
                        profit2_color = "🟢" if target2_profit > 0 else "🔴"
                        st.write(f"{profit2_color} **Profit**: {currency_symbol}{target2_profit:,.0f} (+{target2_profit_pct:.1f}%)")
                        st.write(f"📈 **Total Value**: {currency_symbol}{(shares * entry_price) + target2_profit:,.0f}")
                    
                    st.markdown("**🛑 If Stop Loss Hit:**")
                    loss_color = "🔴"
                    st.write(f"{loss_color} **Loss**: {currency_symbol}{stop_loss_amount:,.0f} ({stop_loss_pct:.1f}%)")
                    st.write(f"📉 **Total Value**: {currency_symbol}{(shares * entry_price) + stop_loss_amount:,.0f}")
                    
                    # Summary box
                    st.markdown("---")
                    st.markdown("**📊 Risk/Reward Summary:**")
                    best_case = target2_profit if len(resistance_levels) > 1 else target1_profit
                    worst_case = abs(stop_loss_amount)
                    actual_risk_reward = best_case / worst_case if worst_case > 0 else 0
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("🟢 Best Case", f"{currency_symbol}{best_case:,.0f}")
                    with col2:
                        st.metric("🔴 Worst Case", f"-{currency_symbol}{worst_case:,.0f}")
                    
                    rr_display_color = "🟢" if actual_risk_reward >= 2 else "🟡" if actual_risk_reward >= 1.5 else "🔴"
                    st.write(f"{rr_display_color} **Actual R/R Ratio**: {actual_risk_reward:.1f}:1")
                
                # Detailed Justification Section
                st.markdown("---")
                st.markdown("### 📝 **Analysis Justification**")
                
                # Price chart visualization (text-based)
                with st.expander("📈 **Price Chart & Levels**", expanded=False):
                    # Create a simple text-based chart showing price relative to support/resistance
                    support_levels = selected_stock.get('support_levels', [nearest_support])
                    resistance_levels = selected_stock.get('resistance_levels', [nearest_resistance])
                    
                    chart_data = []
                    
                    # Add resistance levels
                    for i, level in enumerate(sorted(resistance_levels, reverse=True)[:3]):
                        distance = ((level - price) / price) * 100
                        strength = "🔴🔴🔴" if i == 0 else "🔴🔴" if i == 1 else "🔴"
                        chart_data.append((level, f"{strength} Resistance", distance))
                    
                    # Add current price
                    chart_data.append((price, "💙 CURRENT PRICE", 0))
                    
                    # Add support levels
                    for i, level in enumerate(sorted(support_levels, reverse=True)[:3]):
                        distance = ((price - level) / price) * 100
                        strength = "🟢🟢🟢" if i == 0 else "🟢🟢" if i == 1 else "🟢"
                        chart_data.append((level, f"{strength} Support", distance))
                    
                    # Sort by price (highest to lowest)
                    chart_data.sort(key=lambda x: x[0], reverse=True)
                    
                    # Display chart
                    st.markdown("**Price Levels Chart:**")
                    for level_price, level_type, distance in chart_data:
                        if "CURRENT" in level_type:
                            st.markdown(f"**{currency_symbol}{level_price:.2f}** ← {level_type}")
                        else:
                            st.markdown(f"{currency_symbol}{level_price:.2f} {level_type} ({abs(distance):+.1f}%)")
                    
                    # Add Bollinger Bands if available
                    bollinger = selected_stock.get('bollinger_bands')
                    if bollinger:
                        st.markdown("**📊 Bollinger Bands:**")
                        st.markdown(f"• Upper Band: {currency_symbol}{bollinger['upper']:.2f}")
                        st.markdown(f"• Middle Band: {currency_symbol}{bollinger['middle']:.2f}")
                        st.markdown(f"• Lower Band: {currency_symbol}{bollinger['lower']:.2f}")
                        
                        # Position within bands
                        bb_position = ((price - bollinger['lower']) / (bollinger['upper'] - bollinger['lower'])) * 100
                        if bb_position > 80:
                            st.warning(f"⚠️ Price at {bb_position:.0f}% of Bollinger Band range (overbought)")
                        elif bb_position < 20:
                            st.success(f"✅ Price at {bb_position:.0f}% of Bollinger Band range (oversold)")
                        else:
                            st.info(f"📊 Price at {bb_position:.0f}% of Bollinger Band range (normal)")
                
                # Create justification based on the signals and analysis
                justification_points = []
                
                # Technical strength points
                if score >= 80:
                    justification_points.append("🟢 **Very Strong Setup**: Multiple technical indicators align for high-probability trade")
                elif score >= 60:
                    justification_points.append("🟡 **Good Setup**: Several positive technical signals present")
                else:
                    justification_points.append("🔴 **Caution**: Mixed signals, consider smaller position size")
                
                # Support/Resistance justification
                if entry_type == "Support Bounce":
                    justification_points.append(f"🎯 **Support Bounce Play**: Price testing strong support at {currency_symbol}{nearest_support:.2f}")
                elif entry_type == "Resistance Break":
                    justification_points.append(f"🚀 **Breakout Play**: Price breaking above resistance at {currency_symbol}{nearest_resistance:.2f}")
                elif entry_type == "Pullback Entry":
                    justification_points.append("📈 **Pullback Entry**: Healthy correction in uptrend offers good entry")
                
                # Risk management justification
                if risk_reward >= 2:
                    justification_points.append(f"✅ **Excellent Risk/Reward**: {risk_reward:.1f}:1 ratio exceeds minimum 2:1 requirement")
                elif risk_reward >= 1.5:
                    justification_points.append(f"✅ **Good Risk/Reward**: {risk_reward:.1f}:1 ratio meets trading criteria")
                else:
                    justification_points.append(f"⚠️ **Marginal Risk/Reward**: {risk_reward:.1f}:1 ratio below optimal, consider smaller size")
                
                # Market context
                justification_points.append(f"🌍 **Market Context**: {market_name} market conditions favor this setup type")
                
                # Volume and momentum
                if volume_trend == "High":
                    justification_points.append("📊 **Volume Confirmation**: High volume supports the price movement")
                
                # Technical indicator alignment
                if rsi_signal == "Neutral":
                    justification_points.append("📈 **RSI Favorable**: RSI in healthy range, room for movement")
                
                # Display justification points
                for point in justification_points:
                    st.markdown(f"• {point}")
                
                # Risk warnings
                st.markdown("**⚠️ Risk Considerations:**")
                risk_warnings = []
                
                if rsi > 70:
                    risk_warnings.append("RSI overbought - watch for potential reversal")
                if resistance_distance <= 2:
                    risk_warnings.append("Very close to resistance - limited upside")
                if volume_trend == "Low":
                    risk_warnings.append("Low volume - lack of conviction in move")
                
                if risk_warnings:
                    for warning in risk_warnings:
                        st.markdown(f"• 🔴 {warning}")
                else:
                    st.markdown("• ✅ No major risk flags identified")
                
                # Trading plan summary
                st.markdown("---")
                col_plan1, col_plan2 = st.columns(2)
                
                with col_plan1:
                    st.markdown("**📋 Action Plan:**")
                    st.markdown(f"1. **Enter** at {currency_symbol}{entry_price:.2f}")
                    st.markdown(f"2. **Set stop** at {currency_symbol}{stop_loss:.2f}")
                    st.markdown(f"3. **Target 1** at {currency_symbol}{target_price:.2f}")
                    st.markdown(f"4. **Trail stop** as price advances")
                
                with col_plan2:
                    st.markdown("**⏰ Timing:**")
                    st.markdown("• Best entry: Market open or on breakout")
                    st.markdown("• Monitor: Every 4-6 hours")
                    st.markdown("• Hold time: 2-10 days typical")
                    st.markdown("• Review: Daily after market close")
                
                # Quick action buttons for this stock
                st.markdown("---")
                
                # Enhanced Buy/Sell System with Profit/Loss Confirmation
                st.markdown("### 💱 **Trade Execution**")
                
                # Initialize session state for trade confirmation
                trade_key = f"trade_confirm_{symbol}"
                if trade_key not in st.session_state:
                    st.session_state[trade_key] = {"mode": None, "quantity": 0, "show_confirmation": False}
                
                trade_state = st.session_state[trade_key]
                
                # Buy Section
                st.markdown("**🟢 Buy Order**")
                buy_col1, buy_col2 = st.columns([1, 1])
                
                with buy_col1:
                    buy_quantity = st.number_input(
                        "Shares to buy:",
                        min_value=1,
                        max_value=10000,
                        value=shares,  # Default to recommended quantity
                        step=1,
                        key=f"buy_input_{symbol}"
                    )
                
                with buy_col2:
                    if st.button(f"🟢 PREVIEW BUY", key=f"preview_buy_{symbol}", type="primary"):
                        trade_state["mode"] = "buy"
                        trade_state["quantity"] = buy_quantity
                        trade_state["show_confirmation"] = True
                
                # Show Buy Confirmation with Profit/Loss Projections
                if trade_state["show_confirmation"] and trade_state["mode"] == "buy":
                    st.markdown("---")
                    st.markdown("**🔍 Buy Order Confirmation**")
                    
                    # Calculate projections for custom quantity
                    custom_investment = buy_quantity * entry_price
                    custom_target1_profit = buy_quantity * (target_price - entry_price)
                    custom_target1_total = custom_investment + custom_target1_profit
                    custom_stop_loss = buy_quantity * (stop_loss - entry_price)
                    custom_stop_total = custom_investment + custom_stop_loss
                    
                    # Enhanced projections for second target if available
                    if len(resistance_levels) > 1:
                        target2 = sorted(resistance_levels)[1] if len(resistance_levels) > 1 else target_price * 1.05
                        custom_target2_profit = buy_quantity * (target2 - entry_price)
                        custom_target2_total = custom_investment + custom_target2_profit
                    
                    # Display order summary
                    order_col1, order_col2 = st.columns([1, 1])
                    
                    with order_col1:
                        st.info(f"""
                        **📋 Order Summary:**
                        • Symbol: {symbol}
                        • Quantity: {buy_quantity:,} shares
                        • Entry Price: {currency_symbol}{entry_price:.2f}
                        • Total Investment: {currency_symbol}{custom_investment:,.0f}
                        """)
                    
                    with order_col2:
                        st.warning(f"""
                        **🎯 Profit/Loss Projections:**
                        
                        **Target 1 ({currency_symbol}{target_price:.2f}):**
                        🟢 Profit: {currency_symbol}{custom_target1_profit:,.0f}
                        📈 Total: {currency_symbol}{custom_target1_total:,.0f}
                        
                        **Stop Loss ({currency_symbol}{stop_loss:.2f}):**
                        🔴 Loss: {currency_symbol}{custom_stop_loss:,.0f}
                        📉 Total: {currency_symbol}{custom_stop_total:,.0f}
                        """)
                    
                    # Show second target if available
                    if len(resistance_levels) > 1:
                        st.success(f"""
                        **🚀 Target 2 ({currency_symbol}{target2:.2f}):**
                        🟢 Max Profit: {currency_symbol}{custom_target2_profit:,.0f}
                        📈 Total: {currency_symbol}{custom_target2_total:,.0f}
                        """)
                    
                    # Confirm/Cancel buttons
                    confirm_col1, confirm_col2, confirm_col3 = st.columns([1, 1, 1])
                    
                    with confirm_col1:
                        if st.button(f"✅ CONFIRM BUY", key=f"confirm_buy_{symbol}", type="primary"):
                            result = dashboard.portfolio.buy_stock(symbol, price, confidence=score, shares=buy_quantity)
                            if result['success']:
                                st.success(f"✅ {result['message']}")
                                # Store successful trade in session state
                                if 'recent_trades' not in st.session_state:
                                    st.session_state.recent_trades = []
                                st.session_state.recent_trades.append(f"Bought {buy_quantity} shares of {symbol}")
                                # Clear swing data to force refresh on next manual refresh
                                st.session_state.swing_data = None
                                # Reset trade state
                                trade_state["show_confirmation"] = False
                                trade_state["mode"] = None
                            else:
                                st.error(f"❌ {result['message']}")
                    
                    with confirm_col2:
                        if st.button(f"❌ CANCEL", key=f"cancel_buy_{symbol}"):
                            trade_state["show_confirmation"] = False
                            trade_state["mode"] = None
                            st.info("Buy order cancelled")
                    
                    with confirm_col3:
                        st.caption("Review the projections before confirming")
                
                # Check if user already owns this stock for selling
                portfolio_positions = dashboard.portfolio.get_current_positions()
                owned_shares = 0
                avg_cost = 0
                
                for pos in portfolio_positions:
                    if pos['symbol'] == symbol:
                        owned_shares = pos['shares']
                        avg_cost = pos['avg_price']
                        break
                
                if owned_shares > 0:
                    st.markdown("---")
                    st.markdown("**🔴 Sell Order**")
                    st.info(f"You own {owned_shares:.0f} shares at avg cost {currency_symbol}{avg_cost:.2f}")
                    
                    sell_col1, sell_col2 = st.columns([1, 1])
                    
                    with sell_col1:
                        sell_quantity = st.number_input(
                            "Shares to sell:",
                            min_value=1,
                            max_value=int(owned_shares),
                            value=min(int(owned_shares), 100),
                            step=1,
                            key=f"sell_input_{symbol}"
                        )
                    
                    with sell_col2:
                        if st.button(f"🔴 PREVIEW SELL", key=f"preview_sell_{symbol}", type="secondary"):
                            trade_state["mode"] = "sell"
                            trade_state["quantity"] = sell_quantity
                            trade_state["show_confirmation"] = True
                    
                    # Show Sell Confirmation with Profit/Loss
                    if trade_state["show_confirmation"] and trade_state["mode"] == "sell":
                        st.markdown("---")
                        st.markdown("**🔍 Sell Order Confirmation**")
                        
                        # Calculate sell projections
                        sell_proceeds = sell_quantity * price
                        cost_basis = sell_quantity * avg_cost
                        total_pnl = sell_proceeds - cost_basis
                        pnl_pct = (total_pnl / cost_basis) * 100 if cost_basis > 0 else 0
                        
                        # Display sell summary
                        sell_sum_col1, sell_sum_col2 = st.columns([1, 1])
                        
                        with sell_sum_col1:
                            st.info(f"""
                            **📋 Sell Order Summary:**
                            • Symbol: {symbol}
                            • Quantity: {sell_quantity:,} shares
                            • Current Price: {currency_symbol}{price:.2f}
                            • Avg Cost: {currency_symbol}{avg_cost:.2f}
                            • Proceeds: {currency_symbol}{sell_proceeds:,.0f}
                            """)
                        
                        with sell_sum_col2:
                            pnl_color = "success" if total_pnl >= 0 else "error"
                            pnl_emoji = "🟢" if total_pnl >= 0 else "🔴"
                            
                            if pnl_color == "success":
                                st.success(f"""
                                **💰 Profit/Loss Summary:**
                                {pnl_emoji} **Total P&L: {currency_symbol}{total_pnl:,.0f}**
                                📊 Return: {pnl_pct:+.1f}%
                                💵 Cost Basis: {currency_symbol}{cost_basis:,.0f}
                                💸 Proceeds: {currency_symbol}{sell_proceeds:,.0f}
                                """)
                            else:
                                st.error(f"""
                                **💰 Profit/Loss Summary:**
                                {pnl_emoji} **Total P&L: {currency_symbol}{total_pnl:,.0f}**
                                📊 Return: {pnl_pct:+.1f}%
                                💵 Cost Basis: {currency_symbol}{cost_basis:,.0f}
                                💸 Proceeds: {currency_symbol}{sell_proceeds:,.0f}
                                """)
                        
                        # Confirm/Cancel sell buttons
                        sell_confirm_col1, sell_confirm_col2, sell_confirm_col3 = st.columns([1, 1, 1])
                        
                        with sell_confirm_col1:
                            if st.button(f"✅ CONFIRM SELL", key=f"confirm_sell_{symbol}", type="primary"):
                                result = dashboard.portfolio.sell_stock(symbol, price, shares=sell_quantity)
                                if result['success']:
                                    pnl_msg = f"Profit: {currency_symbol}{total_pnl:,.0f}" if total_pnl >= 0 else f"Loss: {currency_symbol}{abs(total_pnl):,.0f}"
                                    st.success(f"✅ {result['message']} | {pnl_msg}")
                                    # Store successful trade in session state
                                    if 'recent_trades' not in st.session_state:
                                        st.session_state.recent_trades = []
                                    st.session_state.recent_trades.append(f"Sold {sell_quantity} shares of {symbol} for {pnl_msg}")
                                    # Clear swing data to force refresh on next manual refresh
                                    st.session_state.swing_data = None
                                    # Reset trade state
                                    trade_state["show_confirmation"] = False
                                    trade_state["mode"] = None
                                else:
                                    st.error(f"❌ {result['message']}")
                        
                        with sell_confirm_col2:
                            if st.button(f"❌ CANCEL", key=f"cancel_sell_{symbol}"):
                                trade_state["show_confirmation"] = False
                                trade_state["mode"] = None
                                st.info("Sell order cancelled")
                        
                        with sell_confirm_col3:
                            st.caption("Review P&L before confirming")
    
    else:
        st.info("No swing opportunities available for detailed analysis at this time.")


def show_portfolio(dashboard):
    """Display portfolio overview - Mobile responsive"""
    st.header("💼 Portfolio Overview")
    
    # Quick actions at the top - Responsive
    if is_mobile():
        # Stack actions vertically on mobile
        if st.button("🔄 Reset Portfolio", key="quick_reset_portfolio", type="secondary"):
            with st.spinner("Resetting portfolio..."):
                result = dashboard.portfolio.reset_portfolio()
                if result['success']:
                    st.success("✅ Portfolio reset successfully!")
                    st.rerun()
                else:
                    st.error(f"❌ Reset failed: {result['message']}")
        
        if st.button("🗑️ Clear History", key="quick_clear_history", type="secondary"):
            with st.spinner("Clearing history..."):
                result = dashboard.portfolio.clear_history()
                if result['success']:
                    st.success("✅ History cleared successfully!")
                    st.rerun()
                else:
                    st.error(f"❌ Clear failed: {result['message']}")
    else:
        # Use columns for desktop
        action_col1, action_col2, action_col3 = st.columns([2, 1, 1])
        
        with action_col2:
            if st.button("🔄 Reset Portfolio", key="quick_reset_portfolio", type="secondary"):
                with st.spinner("Resetting portfolio..."):
                    result = dashboard.portfolio.reset_portfolio()
                    if result['success']:
                        st.success("✅ Portfolio reset successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ Reset failed: {result['message']}")
        
        with action_col3:
            if st.button("🗑️ Clear History", key="quick_clear_history", type="secondary"):
                with st.spinner("Clearing history..."):
                    result = dashboard.portfolio.clear_history()
                    if result['success']:
                        st.success("✅ History cleared successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ Clear failed: {result['message']}")
    
    st.markdown("---")
    
    # Update positions
    dashboard.portfolio.update_positions()
    
    # Get metrics
    metrics = dashboard.portfolio.get_performance_metrics()
    positions = dashboard.portfolio.get_current_positions()
    
    # Multi-Currency Portfolio Overview - Responsive
    def show_currency_overview():
        currency_metrics = metrics['currency_metrics']
        
        if is_mobile():
            # Stack currency summaries vertically on mobile
            for currency, symbol in [('USD', '🇺🇸'), ('INR', '🇮🇳'), ('MYR', '🇲🇾')]:
                data = currency_metrics[currency]
                currency_symbol = '$' if currency == 'USD' else '₹' if currency == 'INR' else 'RM'
                
                with st.container():
                    st.markdown(f"### {symbol} {currency} Portfolio")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric(
                            "💰 Portfolio Value",
                            f"{currency_symbol}{data['current_value']:,.2f}",
                            f"{currency_symbol}{data['total_return']:,.2f}"
                        )
                    
                    with col2:
                        st.metric(
                            "📈 Performance",
                            f"{data.get('total_return_pct', 0):.2f}%",
                            f"{currency_symbol}{data['cash']:,.2f} cash"
                        )
                    
                    st.markdown("---")
        else:
            # Use columns for desktop
            col1, col2, col3 = st.columns(3)
            
            with col1:
                usd_data = currency_metrics['USD']
                st.markdown("### 🇺🇸 USD Portfolio")
                st.metric(
                    "💰 Portfolio Value",
                    f"${usd_data['current_value']:,.2f}",
                    f"${usd_data['total_return']:,.2f}"
                )
                st.metric(
                    "📈 Performance", 
                    f"{usd_data.get('total_return_pct', 0):.2f}%",
                    f"${usd_data['cash']:,.2f} cash"
                )
            
            with col2:
                inr_data = currency_metrics['INR']
                st.markdown("### 🇮🇳 INR Portfolio")
                st.metric(
                    "💰 Portfolio Value",
                    f"₹{inr_data['current_value']:,.2f}",
                    f"₹{inr_data['total_return']:,.2f}"
                )
                st.metric(
                    "📈 Performance",
                    f"{inr_data.get('total_return_pct', 0):.2f}%",
                    f"₹{inr_data['cash']:,.2f} cash"
                )
            
            with col3:
                myr_data = currency_metrics['MYR']
                st.markdown("### �� MYR Portfolio")
                st.metric(
                    "💰 Portfolio Value",
                    f"RM{myr_data['current_value']:,.2f}",
                    f"RM{myr_data['total_return']:,.2f}"
                )
                st.metric(
                    "📈 Performance",
                    f"{myr_data.get('total_return_pct', 0):.2f}%",
                    f"RM{myr_data['cash']:,.2f} cash"
                )
    
    if is_mobile():
        create_expandable_section("💱 Multi-Currency Portfolio Summary", show_currency_overview, expanded=True)
    else:
        st.subheader("💱 Multi-Currency Portfolio Summary")
        show_currency_overview()
    
    st.markdown("---")
    
    
    # Current positions
    if positions:
        st.metric(
            "💰 Portfolio Value",
            f"₹{inr_data['current_value']:,.2f}",
            f"₹{inr_data['total_return']:,.2f}"
        )
        st.metric(
            "📈 Return",
            f"{inr_data['total_return_pct']:.2f}%",
            delta=f"{inr_data['total_return_pct']:.2f}%"
        )
        st.metric("💵 Cash", f"₹{inr_data['cash']:,.2f}")
        st.metric("📊 Positions", inr_data['positions_count'])
    
    with col3:
        myr_data = currency_metrics['MYR']
        st.markdown("### 🇲🇾 MYR Portfolio")
        st.metric(
            "💰 Portfolio Value",
            f"RM{myr_data['current_value']:,.2f}",
            f"RM{myr_data['total_return']:,.2f}"
        )
        st.metric(
            "📈 Return",
            f"{myr_data['total_return_pct']:.2f}%",
            delta=f"{myr_data['total_return_pct']:.2f}%"
        )
        st.metric("💵 Cash", f"RM{myr_data['cash']:,.2f}")
        st.metric("📊 Positions", myr_data['positions_count'])
    
    st.markdown("---")
    
    # Overall summary
    total_positions = sum(data['positions_count'] for data in currency_metrics.values())
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🌍 Total Positions", total_positions)
    with col2:
        st.info("� **No Currency Conversion** - Each market tracked separately for clearer performance insights!")
    with col3:
        # Best performing currency
        best_currency = max(currency_metrics.keys(), key=lambda k: currency_metrics[k]['total_return_pct'])
        best_return = currency_metrics[best_currency]['total_return_pct']
        currency_flag = '🇺🇸' if best_currency == 'USD' else '🇮🇳' if best_currency == 'INR' else '🇲🇾'
        st.metric("🏆 Best Performer", f"{currency_flag} {best_currency}", f"{best_return:.2f}%")
    
    # Current positions
    if positions:
        st.subheader("📈 Current Positions")
        
        # Enhanced positions display
        for position in positions:
            symbol = position['symbol']
            current_price = position['current_price']
            entry_price = position['avg_price']
            shares = position['shares']
            current_value = position['current_value']
            unrealized_pnl = position['unrealized_pnl']
            unrealized_pnl_pct = position['unrealized_pnl_pct']
            currency = position.get('currency', 'USD')
            
            # Get currency symbol
            currency_symbol = '₹' if currency == 'INR' else 'RM' if currency == 'MYR' else '$'
            
            # Calculate target and stop-loss prices
            target_price = position['target_price']
            stop_loss_price = position['stop_loss_price']
            
            # Determine status color
            if unrealized_pnl > 0:
                status_color = "🟢"
                status = "PROFIT"
            elif unrealized_pnl < 0:
                status_color = "🔴" 
                status = "LOSS"
            else:
                status_color = "🟡"
                status = "BREAKEVEN"
            
            with st.expander(f"{status_color} {symbol} - {status} ({unrealized_pnl_pct:.1f}%)", expanded=True):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📊 Position Info", f"{shares} shares")
                    st.write(f"**Entry Price:** {currency_symbol}{entry_price:.2f}")
                    st.write(f"**Current Price:** {currency_symbol}{current_price:.2f}")
                
                with col2:
                    st.metric("💰 Current Value", f"{currency_symbol}{current_value:,.2f}")
                    st.metric("📈 Unrealized P&L", f"{currency_symbol}{unrealized_pnl:,.2f}", f"{unrealized_pnl_pct:.1f}%")
                
                with col3:
                    target_gain = (target_price - current_price) * shares
                    stop_loss = (current_price - stop_loss_price) * shares
                    
                    st.metric("🎯 Target Price", f"{currency_symbol}{target_price:.2f}")
                    st.write(f"**To Target:** {currency_symbol}{target_gain:,.2f}")
                    st.metric("🛡️ Stop-Loss Price", f"{currency_symbol}{stop_loss_price:.2f}")
                    st.write(f"**Risk Amount:** {currency_symbol}{stop_loss:,.2f}")
                
                with col4:
                    # Progress bars for target/stop-loss
                    if current_price >= target_price:
                        st.success("🎯 TARGET REACHED!")
                        progress_val = 1.0
                    elif current_price <= stop_loss_price:
                        st.error("🛡️ STOP-LOSS HIT!")
                        progress_val = 0.0
                    else:
                        # Calculate progress toward target
                        progress_val = (current_price - entry_price) / (target_price - entry_price)
                        progress_val = max(0, min(1, progress_val))
                    
                    st.progress(progress_val, f"Progress to Target: {progress_val*100:.1f}%")
                
                # Action buttons
                st.markdown("---")
                
                # Enhanced Portfolio Trading with Confirmation
                st.markdown("### 💱 **Portfolio Trading**")
                
                # Initialize session state for portfolio trade confirmation
                portfolio_trade_key = f"portfolio_trade_{symbol}"
                if portfolio_trade_key not in st.session_state:
                    st.session_state[portfolio_trade_key] = {"mode": None, "quantity": 0, "show_confirmation": False}
                
                portfolio_trade_state = st.session_state[portfolio_trade_key]
                
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                
                # Check for auto-sell conditions
                should_sell, reason = dashboard.portfolio.should_sell_position(symbol, current_price)
                
                with btn_col1:
                    st.markdown("**🔴 Sell Shares**")
                    # Sell shares with quantity selection
                    sell_quantity = st.number_input(
                        "Shares to sell:",
                        min_value=1,
                        max_value=shares,
                        value=min(shares, 5),
                        step=1,
                        key=f"sell_qty_{symbol}"
                    )
                    
                    # Sell preview button
                    if should_sell:
                        if st.button(f"🔴 PREVIEW SELL {sell_quantity} ({reason})", key=f"preview_auto_sell_{symbol}", type="primary"):
                            portfolio_trade_state["mode"] = "sell"
                            portfolio_trade_state["quantity"] = sell_quantity
                            portfolio_trade_state["show_confirmation"] = True
                    else:
                        if st.button(f"💸 PREVIEW SELL {sell_quantity}", key=f"preview_manual_sell_{symbol}"):
                            portfolio_trade_state["mode"] = "sell"
                            portfolio_trade_state["quantity"] = sell_quantity
                            portfolio_trade_state["show_confirmation"] = True
                    
                    # Sell All button
                    if st.button(f"🔴 PREVIEW SELL ALL ({shares:.0f})", key=f"preview_sell_all_{symbol}", type="secondary"):
                        portfolio_trade_state["mode"] = "sell"
                        portfolio_trade_state["quantity"] = shares
                        portfolio_trade_state["show_confirmation"] = True
                
                with btn_col2:
                    st.markdown("**🟢 Buy More Shares**")
                    # Add shares with quantity selection
                    buy_quantity = st.number_input(
                        "Shares to buy:",
                        min_value=1,
                        max_value=1000,
                        value=5,
                        step=1,
                        key=f"buy_qty_{symbol}"
                    )
                    
                    if st.button(f"➕ PREVIEW BUY {buy_quantity}", key=f"preview_add_{symbol}"):
                        portfolio_trade_state["mode"] = "buy"
                        portfolio_trade_state["quantity"] = buy_quantity
                        portfolio_trade_state["show_confirmation"] = True
                
                with btn_col3:
                    st.write(f"**Days Held:** {(datetime.now() - datetime.fromisoformat(position['entry_date'].replace('Z', '+00:00').replace('+00:00', ''))).days}")
                    if should_sell:
                        st.warning(f"⚠️ **Auto-sell triggered**: {reason}")
                
                # Show Portfolio Trade Confirmation
                if portfolio_trade_state["show_confirmation"]:
                    st.markdown("---")
                    
                    if portfolio_trade_state["mode"] == "sell":
                        st.markdown("**🔍 Sell Order Confirmation**")
                        
                        # Calculate sell P&L
                        sell_proceeds = portfolio_trade_state["quantity"] * current_price
                        cost_basis = portfolio_trade_state["quantity"] * entry_price
                        total_pnl = sell_proceeds - cost_basis
                        pnl_pct = (total_pnl / cost_basis) * 100 if cost_basis > 0 else 0
                        
                        # Display sell summary in columns
                        conf_col1, conf_col2 = st.columns([1, 1])
                        
                        with conf_col1:
                            st.info(f"""
                            **📋 Sell Order Summary:**
                            • Symbol: {symbol}
                            • Shares to Sell: {portfolio_trade_state["quantity"]:,}
                            • Current Price: {currency_symbol}{current_price:.2f}
                            • Avg Cost: {currency_symbol}{entry_price:.2f}
                            • Gross Proceeds: {currency_symbol}{sell_proceeds:,.0f}
                            """)
                        
                        with conf_col2:
                            pnl_color = "success" if total_pnl >= 0 else "error"
                            pnl_emoji = "🟢" if total_pnl >= 0 else "🔴"
                            
                            if pnl_color == "success":
                                st.success(f"""
                                **💰 Profit/Loss Analysis:**
                                {pnl_emoji} **Total P&L: {currency_symbol}{total_pnl:,.0f}**
                                📊 Return: {pnl_pct:+.1f}%
                                💵 Cost Basis: {currency_symbol}{cost_basis:,.0f}
                                💸 Net Proceeds: {currency_symbol}{sell_proceeds:,.0f}
                                """)
                            else:
                                st.error(f"""
                                **💰 Profit/Loss Analysis:**
                                {pnl_emoji} **Total P&L: {currency_symbol}{total_pnl:,.0f}**
                                📊 Return: {pnl_pct:+.1f}%
                                💵 Cost Basis: {currency_symbol}{cost_basis:,.0f}
                                💸 Net Proceeds: {currency_symbol}{sell_proceeds:,.0f}
                                """)
                        
                        # Confirmation buttons for sell
                        sell_conf_col1, sell_conf_col2, sell_conf_col3 = st.columns([1, 1, 1])
                        
                        with sell_conf_col1:
                            if st.button(f"✅ CONFIRM SELL", key=f"confirm_portfolio_sell_{symbol}", type="primary"):
                                sell_reason = reason if should_sell else "MANUAL"
                                result = dashboard.portfolio.sell_stock(symbol, current_price, shares=portfolio_trade_state["quantity"], reason=sell_reason)
                                if result['success']:
                                    pnl_msg = f"Profit: {currency_symbol}{total_pnl:,.0f}" if total_pnl >= 0 else f"Loss: {currency_symbol}{abs(total_pnl):,.0f}"
                                    st.success(f"✅ {result['message']} | {pnl_msg}")
                                    portfolio_trade_state["show_confirmation"] = False
                                    portfolio_trade_state["mode"] = None
                                else:
                                    st.error(f"❌ {result['message']}")
                        
                        with sell_conf_col2:
                            if st.button(f"❌ CANCEL SELL", key=f"cancel_portfolio_sell_{symbol}"):
                                portfolio_trade_state["show_confirmation"] = False
                                portfolio_trade_state["mode"] = None
                                st.info("Sell order cancelled")
                        
                        with sell_conf_col3:
                            st.caption("Review P&L before selling")
                    
                    elif portfolio_trade_state["mode"] == "buy":
                        st.markdown("**🔍 Buy Order Confirmation**")
                        
                        # Calculate buy details
                        buy_investment = portfolio_trade_state["quantity"] * current_price
                        new_total_shares = shares + portfolio_trade_state["quantity"]
                        new_avg_cost = ((shares * entry_price) + buy_investment) / new_total_shares
                        
                        # Display buy summary
                        buy_conf_col1, buy_conf_col2 = st.columns([1, 1])
                        
                        with buy_conf_col1:
                            st.info(f"""
                            **📋 Buy Order Summary:**
                            • Symbol: {symbol}
                            • Additional Shares: {portfolio_trade_state["quantity"]:,}
                            • Current Price: {currency_symbol}{current_price:.2f}
                            • Investment: {currency_symbol}{buy_investment:,.0f}
                            """)
                        
                        with buy_conf_col2:
                            st.success(f"""
                            **📊 Position After Purchase:**
                            • Current Shares: {shares:,.0f}
                            • New Total Shares: {new_total_shares:,.0f}
                            • Current Avg Cost: {currency_symbol}{entry_price:.2f}
                            • New Avg Cost: {currency_symbol}{new_avg_cost:.2f}
                            """)
                        
                        # Confirmation buttons for buy
                        buy_conf_col1, buy_conf_col2, buy_conf_col3 = st.columns([1, 1, 1])
                        
                        with buy_conf_col1:
                            if st.button(f"✅ CONFIRM BUY", key=f"confirm_portfolio_buy_{symbol}", type="primary"):
                                result = dashboard.portfolio.buy_stock(symbol, current_price, 75, shares=portfolio_trade_state["quantity"])
                                if result['success']:
                                    st.success(f"✅ {result['message']}")
                                    portfolio_trade_state["show_confirmation"] = False
                                    portfolio_trade_state["mode"] = None
                                else:
                                    st.error(f"❌ {result['message']}")
                        
                        with buy_conf_col2:
                            if st.button(f"❌ CANCEL BUY", key=f"cancel_portfolio_buy_{symbol}"):
                                portfolio_trade_state["show_confirmation"] = False
                                portfolio_trade_state["mode"] = None
                                st.info("Buy order cancelled")
                        
                        with buy_conf_col3:
                            st.caption("Review new position before buying")
        
        # Summary table
        st.subheader("📊 Positions Summary Table")
        positions_df = pd.DataFrame(positions)
        
        # Format for display
        summary_data = []
        for _, pos in positions_df.iterrows():
            # Use original currency prices for display
            entry_price_original = pos.get('avg_price_original', pos['avg_price'])
            current_price_original = pos.get('current_price_original', pos['current_price'])
            target_price = pos.get('target_price', entry_price_original * 1.10)
            stop_price = pos.get('stop_loss_price', entry_price_original * 0.95)
            currency = pos.get('currency', 'USD')
            currency_symbol = '₹' if currency == 'INR' else 'RM' if currency == 'MYR' else '$'
            
            summary_data.append({
                'Symbol': pos['symbol'],
                'Shares': f"{pos['shares']:.0f}",
                'Entry': f"{currency_symbol}{entry_price_original:.2f}",
                'Current': f"{currency_symbol}{current_price_original:.2f}",
                'Target': f"{currency_symbol}{target_price:.2f}",
                'Stop-Loss': f"{currency_symbol}{stop_price:.2f}",
                'Value': f"{currency_symbol}{pos['current_value']:,.2f}",
                'P&L': f"{currency_symbol}{pos['unrealized_pnl']:,.2f}",
                'P&L %': f"{pos['unrealized_pnl_pct']:.1f}%",
                'Status': 'TARGET' if current_price_original >= target_price else 
                         'STOP-LOSS' if current_price_original <= stop_price else 'HOLDING'
            })
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            
            # Style the summary table
            def style_status(val):
                if val == 'TARGET':
                    return 'background-color: #d4edda; color: #155724'
                elif val == 'STOP-LOSS':
                    return 'background-color: #f8d7da; color: #721c24'
                elif 'HOLDING':
                    return 'background-color: #fff3cd; color: #856404'
                return ''
            
            styled_summary = summary_df.style.map(style_status, subset=['Status'])
            st.dataframe(styled_summary, width='stretch')
    else:
        st.info("📝 No current positions. Start trading from the Live Signals tab!")
        
        # Show sample trade calculation
        st.subheader("💡 Sample Trade Example")
        st.write("**Here's how a trade would work:**")
        
        example_price = 100.00
        shares = int(1000 / example_price)  # $1000 position
        target = example_price * 1.10
        stop = example_price * 0.95
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Example Stock", f"${example_price:.2f}")
            st.write(f"**Position Size:** {shares} shares")
            st.write(f"**Investment:** ${shares * example_price:,.2f}")
        
        with col2:
            st.metric("🎯 Target (+10%)", f"${target:.2f}")
            st.write(f"**Potential Gain:** ${(target - example_price) * shares:.2f}")
        
        with col3:
            st.metric("🛡️ Stop-Loss (-5%)", f"${stop:.2f}")
            st.write(f"**Max Risk:** ${(example_price - stop) * shares:.2f}")
        
        st.info("💡 Risk/Reward Ratio: 1:2 (Risk $50 to potentially gain $100)")

def show_performance(dashboard):
    """Display performance analytics"""
    st.header("📊 Performance Analytics")
    
    metrics = dashboard.portfolio.get_performance_metrics()
    
    # Performance summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🎯 Win Rate", f"{metrics['win_rate']:.1f}%")
        st.metric("📈 Average Win", f"{metrics['avg_win']:.2f}%")
    
    with col2:
        st.metric("📉 Average Loss", f"{metrics['avg_loss']:.2f}%")
        st.metric("⬇️ Max Drawdown", f"{metrics['max_drawdown']:.2f}%")
    
    with col3:
        st.metric("🔢 Total Trades", metrics['total_trades'])
        if metrics['best_trade']:
            st.metric("🏆 Best Trade", f"{metrics['best_trade']['pnl_pct']:.2f}%")
    
    # Portfolio value chart
    daily_values = dashboard.portfolio.portfolio['daily_values']
    
    if len(daily_values) > 1:
        st.subheader("📈 Portfolio Value Over Time")
        
        df_values = pd.DataFrame(daily_values)
        df_values['date'] = pd.to_datetime(df_values['date'])
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_values['date'],
            y=df_values['value'],
            mode='lines+markers',
            name='Portfolio Value',
            line=dict(color='#1f77b4', width=3)
        ))
        
        # Add benchmark line (initial capital)
        fig.add_hline(
            y=dashboard.portfolio.initial_capital,
            line_dash="dash",
            line_color="red",
            annotation_text="Initial Capital"
        )
        
        fig.update_layout(
            title="Portfolio Performance",
            xaxis_title="Date",
            yaxis_title="Portfolio Value ($)",
            hovermode='x'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Trade history
    trade_history = dashboard.portfolio.portfolio['trade_history']
    completed_trades = [t for t in trade_history if t['action'] == 'SELL']
    
    if completed_trades:
        st.subheader("💼 Trade History")
        
        trades_df = pd.DataFrame(completed_trades)
        trades_df['P&L'] = trades_df['pnl'].apply(lambda x: f"${x:,.2f}")
        trades_df['Return %'] = trades_df['pnl_pct'].apply(lambda x: f"{x:.2f}%")
        trades_df['Date'] = pd.to_datetime(trades_df['date']).dt.strftime('%Y-%m-%d')
        
        display_trades = trades_df[['symbol', 'Date', 'shares', 'price', 'P&L', 'Return %', 'reason']]
        display_trades.columns = ['Symbol', 'Date', 'Shares', 'Sell Price', 'P&L', 'Return %', 'Reason']
        
        st.dataframe(display_trades, use_container_width=True)

def show_charts(dashboard):
    """Display detailed charts"""
    st.header("📈 Technical Analysis Charts")
    
    # Stock selector
    all_symbols = []
    watchlists = get_market_watchlists()
    for symbols in watchlists.values():
        all_symbols.extend(symbols[:5])  # Limit for performance
    
    selected_symbol = st.selectbox("Select Stock for Analysis", all_symbols)
    
    if selected_symbol:
        with st.spinner(f"Loading {selected_symbol} chart..."):
            analysis = dashboard.get_stock_analysis(selected_symbol, period="1y")
        
        if analysis:
            data = analysis['data']
            signals = analysis['signals']
            
            # Create subplots
            fig = make_subplots(
                rows=3, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                subplot_titles=(f'{selected_symbol} Price & Moving Averages', 'RSI', 'MACD'),
                row_heights=[0.6, 0.2, 0.2]
            )
            
            # Price chart with moving averages
            fig.add_trace(
                go.Candlestick(
                    x=data.index,
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    name='Price'
                ),
                row=1, col=1
            )
            
            # Moving averages
            fig.add_trace(
                go.Scatter(x=data.index, y=data['SMA_20'], name='SMA 20', line=dict(color='orange')),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=data.index, y=data['SMA_50'], name='SMA 50', line=dict(color='red')),
                row=1, col=1
            )
            
            # Bollinger Bands
            fig.add_trace(
                go.Scatter(x=data.index, y=data['BB_Upper'], name='BB Upper', line=dict(color='gray', dash='dash')),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=data.index, y=data['BB_Lower'], name='BB Lower', line=dict(color='gray', dash='dash')),
                row=1, col=1
            )
            
            # RSI
            fig.add_trace(
                go.Scatter(x=data.index, y=data['RSI'], name='RSI', line=dict(color='purple')),
                row=2, col=1
            )
            
            # RSI levels
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
            
            # MACD
            fig.add_trace(
                go.Scatter(x=data.index, y=data['MACD'], name='MACD', line=dict(color='blue')),
                row=3, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=data.index, y=data['MACD_Signal'], name='Signal', line=dict(color='red')),
                row=3, col=1
            )
            
            fig.update_layout(
                height=800,
                title=f"{selected_symbol} Technical Analysis",
                xaxis_rangeslider_visible=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Current analysis
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Current Analysis")
                st.write(f"**Recommendation:** {signals['recommendation']}")
                st.write(f"**Confidence:** {signals['confidence']}%")
                st.write(f"**Current Price:** ${analysis['latest']['Close']:.2f}")
                st.write(f"**RSI:** {signals['rsi']:.1f}")
            
            with col2:
                st.subheader("🎯 Signal Details")
                st.write(f"**Trend (SMA):** {'Bullish' if signals['sma_bullish'] else 'Bearish'}")
                st.write(f"**MACD:** {'Bullish' if signals['macd_bullish'] else 'Bearish'}")
                st.write(f"**BB Position:** {signals['bb_position']}")
                
                if signals['recommendation'] in ['BUY', 'STRONG BUY']:
                    st.success("🟢 This stock shows buying opportunity!")
                elif signals['recommendation'] in ['SELL', 'STRONG SELL']:
                    st.error("🔴 This stock shows selling signals!")
                else:
                    st.info("🟡 This stock is in a neutral zone.")

def show_trade_history(dashboard):
    """Display comprehensive trade history with profit/loss tracking"""
    st.header("📋 Trade History & Analytics")
    
    # Get trade history
    trade_history = dashboard.portfolio.portfolio.get('trade_history', [])
    
    if not trade_history:
        st.info("No trades executed yet. Start trading to see your history here!")
        return
    
    # Trade summary metrics
    st.subheader("📊 Trading Summary")
    
    buys = [t for t in trade_history if t['action'] == 'BUY']
    sells = [t for t in trade_history if t['action'] == 'SELL']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Trades", len(trade_history))
        st.metric("Buy Orders", len(buys))
    
    with col2:
        st.metric("Sell Orders", len(sells))
        if sells:
            winning_trades = len([s for s in sells if s.get('pnl_usd', 0) > 0])
            win_rate = (winning_trades / len(sells)) * 100
            st.metric("Win Rate", f"{win_rate:.1f}%")
    
    with col3:
        if sells:
            total_pnl = sum(s.get('pnl_usd', 0) for s in sells)
            total_pnl_pct = sum(s.get('pnl_pct', 0) for s in sells) / len(sells)
            st.metric("Total Realized P&L", f"${total_pnl:.2f}")
            st.metric("Avg Return per Trade", f"{total_pnl_pct:.2f}%")
    
    with col4:
        if sells:
            best_trade = max(sells, key=lambda x: x.get('pnl_pct', 0))
            worst_trade = min(sells, key=lambda x: x.get('pnl_pct', 0))
            st.metric("Best Trade", f"{best_trade.get('pnl_pct', 0):.2f}%")
            st.metric("Worst Trade", f"{worst_trade.get('pnl_pct', 0):.2f}%")
    
    # Filters
    st.subheader("🔍 Filter Trades")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        action_filter = st.selectbox("Action", ["All", "BUY", "SELL"])
    
    with col2:
        symbol_filter = st.selectbox("Symbol", ["All"] + list(set(t['symbol'] for t in trade_history)))
    
    with col3:
        date_range = st.date_input("Date Range", value=[])
    
    # Filter trades
    filtered_trades = trade_history
    
    if action_filter != "All":
        filtered_trades = [t for t in filtered_trades if t['action'] == action_filter]
    
    if symbol_filter != "All":
        filtered_trades = [t for t in filtered_trades if t['symbol'] == symbol_filter]
    
    # Display detailed trade table
    st.subheader(f"📈 Trade Details ({len(filtered_trades)} trades)")
    
    if filtered_trades:
        # Create enhanced DataFrame for display
        trade_data = []
        for trade in reversed(filtered_trades[-50:]):  # Show last 50 trades
            currency = trade.get('currency', 'USD')
            currency_symbol = '₹' if currency == 'INR' else 'RM' if currency == 'MYR' else '$'
            
            # Format trade data with proper currency
            trade_row = {
                'ID': trade.get('id', 'N/A'),
                'Date': trade.get('date', trade.get('timestamp', ''))[:10],
                'Time': trade.get('timestamp', trade.get('date', ''))[-8:] if 'timestamp' in trade else '',
                'Symbol': trade['symbol'],
                'Action': '🟢 BUY' if trade['action'] == 'BUY' else '🔴 SELL',
                'Shares': trade['shares'],
                'Price': f"{currency_symbol}{trade.get('price_original', trade['price']):.2f}",
                'Total': f"{currency_symbol}{trade.get('total_original', trade.get('total', trade['shares'] * trade['price'])):.2f}",
                'Currency': currency
            }
            
            # Add P&L info for sells
            if trade['action'] == 'SELL':
                pnl_original = trade.get('pnl_original', trade.get('pnl', 0))
                pnl_pct = trade.get('pnl_pct', 0)
                trade_row['P&L'] = f"{currency_symbol}{pnl_original:+.2f}"
                trade_row['P&L %'] = f"{pnl_pct:+.2f}%"
                trade_row['Holding Days'] = trade.get('holding_days', 0)
                trade_row['Reason'] = trade.get('reason', 'N/A')
            else:
                trade_row['P&L'] = '-'
                trade_row['P&L %'] = '-'
                trade_row['Holding Days'] = '-'
                trade_row['Reason'] = trade.get('trade_reason', 'Signal')
            
            trade_data.append(trade_row)
        
        # Display as interactive table
        df_trades = pd.DataFrame(trade_data)
        
        # Style the table
        def style_action(val):
            if '🟢 BUY' in str(val):
                return 'background-color: #d4edda; color: #155724;'
            elif '🔴 SELL' in str(val):
                return 'background-color: #f8d7da; color: #721c24;'
            return ''
        
        def style_pnl(val):
            if isinstance(val, str) and val != '-':
                if '+' in val:
                    return 'background-color: #d4edda; color: #155724; font-weight: bold;'
                elif '-' in val:
                    return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
            return ''
        
        styled_df = df_trades.style.map(style_action, subset=['Action'])
        if 'P&L' in df_trades.columns:
            styled_df = styled_df.map(style_pnl, subset=['P&L', 'P&L %'])
        
        st.dataframe(styled_df, use_container_width=True, height=400)
        
        # Trade statistics by symbol
        if sells:
            st.subheader("📊 Performance by Symbol")
            
            symbol_stats = {}
            for trade in sells:
                symbol = trade['symbol']
                if symbol not in symbol_stats:
                    symbol_stats[symbol] = {
                        'trades': 0,
                        'total_pnl': 0,
                        'wins': 0,
                        'total_days': 0
                    }
                
                symbol_stats[symbol]['trades'] += 1
                symbol_stats[symbol]['total_pnl'] += trade.get('pnl_usd', 0)
                if trade.get('pnl_usd', 0) > 0:
                    symbol_stats[symbol]['wins'] += 1
                symbol_stats[symbol]['total_days'] += trade.get('holding_days', 0)
            
            stats_data = []
            for symbol, stats in symbol_stats.items():
                win_rate = (stats['wins'] / stats['trades']) * 100 if stats['trades'] > 0 else 0
                avg_holding = stats['total_days'] / stats['trades'] if stats['trades'] > 0 else 0
                
                stats_data.append({
                    'Symbol': symbol,
                    'Total Trades': stats['trades'],
                    'Win Rate': f"{win_rate:.1f}%",
                    'Total P&L': f"${stats['total_pnl']:.2f}",
                    'Avg P&L per Trade': f"${stats['total_pnl']/stats['trades']:.2f}",
                    'Avg Holding Days': f"{avg_holding:.1f}"
                })
            
            df_stats = pd.DataFrame(stats_data)
            st.dataframe(df_stats, use_container_width=True)
        
        # Export trades
        st.subheader("💾 Export Trade Data")
        
        if st.button("📥 Download Trade History as CSV"):
            csv = df_trades.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"trade_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    else:
        st.info("No trades match the selected filters.")

def show_learning_center(dashboard):
    """Display learning and improvement insights"""
    st.header("🎓 Learning Center")
    
    # Performance insights
    metrics = dashboard.portfolio.get_performance_metrics()
    
    st.subheader("📈 Performance Insights")
    
    # Win rate analysis
    if metrics['total_trades'] > 0:
        if metrics['win_rate'] < 50:
            st.warning(f"🎯 **Improvement Needed**: Your win rate is {metrics['win_rate']:.1f}%. Consider:")
            st.write("• Using higher confidence thresholds (75%+ instead of 70%)")
            st.write("• Focusing on fewer, higher-quality setups")
            st.write("• Implementing stricter entry criteria")
        elif metrics['win_rate'] > 70:
            st.success(f"🏆 **Excellent**: Win rate of {metrics['win_rate']:.1f}% is very good!")
        else:
            st.info(f"👍 **Good**: Win rate of {metrics['win_rate']:.1f}% is solid.")
    
    # Risk management insights
    if metrics['max_drawdown'] > 10:
        st.error(f"⚠️ **Risk Alert**: Max drawdown of {metrics['max_drawdown']:.1f}% is high. Consider:")
        st.write("• Reducing position sizes")
        st.write("• Using tighter stop-losses")
        st.write("• Better diversification across sectors")
    
    # Strategy performance by market
    st.subheader("🌍 Market Performance Analysis")
    
    trade_history = dashboard.portfolio.portfolio['trade_history']
    completed_trades = [t for t in trade_history if t['action'] == 'SELL']
    
    if completed_trades:
        trades_df = pd.DataFrame(completed_trades)
        
        # Analyze by market (simplified by symbol suffix)
        trades_df['market'] = trades_df['symbol'].apply(lambda x: 
            'India' if '.NS' in x else 
            'Malaysia' if '.KL' in x else 
            'USA'
        )
        
        market_performance = trades_df.groupby('market').agg({
            'pnl_pct': ['mean', 'count'],
            'pnl': 'sum'
        }).round(2)
        
        st.write("**Performance by Market:**")
        for market in market_performance.index:
            avg_return = market_performance.loc[market, ('pnl_pct', 'mean')]
            trade_count = market_performance.loc[market, ('pnl_pct', 'count')]
            total_pnl = market_performance.loc[market, ('pnl', 'sum')]
            
            st.write(f"• **{market}**: {avg_return:.2f}% avg return, {trade_count} trades, ${total_pnl:.2f} total P&L")
    
    # Educational content
    st.subheader("📚 Trading Education")
    
    with st.expander("🎯 Understanding Confidence Scores"):
        st.write("""
        **How Confidence Scores Work:**
        
        • **80-100%**: Strong signals with multiple confirmations
        • **70-79%**: Good signals with most indicators aligned
        • **60-69%**: Moderate signals, proceed with caution
        • **Below 60%**: Weak signals, avoid trading
        
        **What affects confidence:**
        • Trend alignment (SMA 20 vs SMA 50)
        • Momentum (MACD signals)
        • Overbought/oversold levels (RSI)
        • Mean reversion opportunities (Bollinger Bands)
        """)
    
    with st.expander("⚠️ Risk Management Rules"):
        st.write("""
        **Key Risk Management Principles:**
        
        • **Position Size**: Never risk more than 2% per trade
        • **Stop Loss**: Set at 5% below entry price
        • **Take Profit**: Target 10% gains for 2:1 risk/reward
        • **Diversification**: Max 8 positions across different sectors
        • **Cash Reserve**: Keep 20% in cash for opportunities
        
        **When to Exit:**
        • Stop loss is hit (-5%)
        • Take profit target reached (+10%)
        • Signal changes to SELL
        • Better opportunities arise
        """)
    
    with st.expander("📈 Technical Indicators Explained"):
        st.write("""
        **Moving Averages (SMA):**
        • SMA 20 > SMA 50: Uptrend
        • SMA 20 < SMA 50: Downtrend
        • Crossovers are strong signals
        
        **RSI (Relative Strength Index):**
        • Above 70: Overbought (consider selling)
        • Below 30: Oversold (consider buying)
        • 30-70: Normal range
        
        **MACD:**
        • MACD line above signal line: Bullish momentum
        • MACD line below signal line: Bearish momentum
        • Crossovers indicate momentum shifts
        
        **Bollinger Bands:**
        • Price near upper band: Potentially overbought
        • Price near lower band: Potentially oversold
        • Price in middle: Neutral zone
        """)
    
    # Current market conditions
    st.subheader("🌡️ Current Market Conditions")
    
    # Simple market sentiment based on recent signals
    recent_signals = get_market_signals("All Markets")
    if recent_signals:
        df_signals = pd.DataFrame(recent_signals)
        
        buy_pct = len(df_signals[df_signals['Signal'].str.contains('BUY')]) / len(df_signals) * 100
        avg_confidence = df_signals['confidence_num'].mean()
        
        if buy_pct > 60:
            st.success(f"🟢 **Bullish Market**: {buy_pct:.1f}% buy signals detected")
        elif buy_pct < 40:
            st.error(f"🔴 **Bearish Market**: {100-buy_pct:.1f}% sell signals detected")
        else:
            st.info(f"🟡 **Neutral Market**: Mixed signals ({buy_pct:.1f}% bullish)")
        
        st.write(f"**Average Signal Confidence**: {avg_confidence:.1f}%")

def show_portfolio_settings(dashboard):
    """Display portfolio management and reset options"""
    st.header("⚙️ Portfolio Settings & Management")
    
    # Current portfolio status
    metrics = dashboard.portfolio.get_performance_metrics()
    positions = dashboard.portfolio.get_current_positions()
    
    st.subheader("📊 Current Portfolio Status")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Total Value", f"${metrics['total_value']:,.2f}")
    
    with col2:
        st.metric("📈 Positions", len(positions))
    
    with col3:
        st.metric("📜 Trades", metrics['total_trades'])
    
    with col4:
        st.metric("📊 Return", f"{metrics['total_return_pct']:.2f}%")
    
    # Cash balances breakdown
    st.subheader("💵 Current Cash Balances")
    cash_balances = metrics.get('cash_balances', {'USD': metrics['cash']})
    
    cash_col1, cash_col2, cash_col3 = st.columns(3)
    with cash_col1:
        st.info(f"🇺🇸 **USD**: ${cash_balances.get('USD', 0):,.2f}")
    with cash_col2:
        st.info(f"🇮🇳 **INR**: ₹{cash_balances.get('INR', 0):,.2f}")
    with cash_col3:
        st.info(f"🇲🇾 **MYR**: RM{cash_balances.get('MYR', 0):,.2f}")
    
    # Reset Options
    st.markdown("---")
    st.subheader("🔄 Portfolio Reset Options")
    
    st.warning("⚠️ **Warning**: Reset operations cannot be undone. Use with caution!")
    
    # Reset options in columns
    reset_col1, reset_col2, reset_col3 = st.columns(3)
    
    with reset_col1:
        st.markdown("### 🏦 Portfolio Reset")
        st.write("Resets cash to initial amounts and clears all positions, but keeps trade history.")
        st.write("**Initial amounts:**")
        st.write("• USD: $10,000")
        st.write("• INR: ₹100,000") 
        st.write("• MYR: RM10,000")
        
        if st.button("🔄 Reset Portfolio", type="primary", key="reset_portfolio"):
            with st.spinner("Resetting portfolio..."):
                result = dashboard.portfolio.reset_portfolio()
                if result['success']:
                    st.success(result['message'])
                    st.balloons()
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(result['message'])
    
    with reset_col2:
        st.markdown("### 📜 Clear History")
        st.write("Clears all trading history but keeps current positions and cash balances.")
        st.write("**This will remove:**")
        st.write("• All trade records")
        st.write("• Performance history")
        st.write("• Daily value tracking")
        
        if st.button("🗑️ Clear History", type="secondary", key="clear_history"):
            with st.spinner("Clearing history..."):
                result = dashboard.portfolio.clear_history()
                if result['success']:
                    st.success(result['message'])
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(result['message'])
    
    with reset_col3:
        st.markdown("### 🧹 Complete Reset")
        st.write("**DANGER**: Completely resets everything to factory defaults.")
        st.write("**This will:**")
        st.write("• Clear all positions")
        st.write("• Clear all history")
        st.write("• Reset cash to initial")
        st.write("• Start completely fresh")
        
        # Double confirmation for complete reset
        if st.checkbox("I understand this will delete everything", key="confirm_complete"):
            if st.button("🧹 COMPLETE RESET", type="primary", key="full_reset"):
                with st.spinner("Performing complete reset..."):
                    result = dashboard.portfolio.full_reset()
                    if result['success']:
                        st.success(result['message'])
                        st.balloons()
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(result['message'])
        else:
            st.button("🧹 COMPLETE RESET", disabled=True, key="full_reset_disabled")
    
    # Backup Information
    st.markdown("---")
    st.subheader("💾 Backup Information")
    st.info("""
    **Before resetting, consider:**
    • Your current portfolio data is stored in `data/paper_portfolio.json`
    • You can manually backup this file before resetting
    • Reset operations create a backup info log for reference
    
    **Original Design:**
    • Starting cash: $10,000 USD, ₹100,000 INR, RM10,000 MYR
    • No automatic trading - all decisions are manual
    • Multi-currency support with proper conversions
    """)
    
    # Show current file path
    import os
    portfolio_path = os.path.abspath("data/paper_portfolio.json")
    st.caption(f"📁 Portfolio file: `{portfolio_path}`")

if __name__ == "__main__":
    main()
