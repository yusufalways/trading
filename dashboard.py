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

# Import authentication
from auth import check_authentication, show_login_form, show_logout_option, require_authentication

# Trading configuration
TRADING_CONFIG = {
    'initial_capital': 10000,
    'max_positions': 8,
    'risk_per_trade': 0.02,  # 2% risk per trade
    'stop_loss_pct': 0.05,   # 5% stop loss
}

from tools.portfolio_manager import PaperTradingPortfolio

# ✅ USING MASTER SWING ANALYZER - THE ONE AND ONLY ANALYSIS SYSTEM
from tools.master_swing_analyzer import MasterSwingAnalyzer, get_daily_swing_signals
from tools.market_stock_lists import get_comprehensive_market_watchlists

# Master analyzer is the only analysis system needed
MASTER_ANALYZER = MasterSwingAnalyzer()

def get_daily_swing_signals_with_progress(progress_callback=None):
    """Compatibility wrapper for the dashboard"""
    return get_daily_swing_signals(progress_callback)

# Compatibility flags
ULTRA_FAST_AVAILABLE = True  # Master analyzer handles all scanning
ADVANCED_ANALYSIS_AVAILABLE = True  # Master analyzer has advanced features

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
    page_title="🔐 Secure Trading Dashboard",
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
        # ✅ Using master analyzer - the one and only analysis system
        self.analyzer = MASTER_ANALYZER
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

def show_live_signals(dashboard, selected_market):
    """Display enhanced swing trading signals with portfolio analysis"""
    st.header("🎯 Daily Swing Trading Signals")
    
    # Initialize session state for swing data if not exists
    if 'swing_data' not in st.session_state:
        st.session_state.swing_data = None
        st.session_state.last_scan_time = None
    
    # Manual refresh controls at the top
    col_refresh1, col_refresh2 = st.columns([1, 3])
    
    with col_refresh1:
        if st.button("🚀 Scan All Markets", type="primary", help="Run a full scan using the Master Analyzer"):
            st.session_state.swing_data = None # Clear previous results
            st.session_state.last_scan_time = datetime.now()
            
            progress_bar = st.progress(0, text="Initializing scan...")
            
            def progress_callback(message, progress):
                progress_bar.progress(progress, text=message)

            try:
                # Use the master analyzer directly
                results = dashboard.analyzer.get_daily_swing_signals(progress_callback)
                st.session_state.swing_data = results
                progress_bar.progress(1.0, text="Scan complete!")
                time.sleep(1) # Keep message on screen
                progress_bar.empty()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Scan failed: {e}")
                progress_bar.empty()

    with col_refresh2:
        if st.session_state.last_scan_time:
            st.info(f"Last scan: {st.session_state.last_scan_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Display results
    if st.session_state.swing_data:
        results = st.session_state.swing_data
        
        st.subheader("Scan Summary")
        summary_cols = st.columns(3)
        summary_cols[0].metric("Total Stocks Scanned", results['total_stocks_scanned'])
        summary_cols[1].metric("Total Scan Duration", f"{results['scan_duration']:.1f}s")
        
        for market_key, market_data in results['markets'].items():
            if selected_market != "All Markets" and market_data['name'] != selected_market:
                continue

            st.markdown(f"### {market_data['name']} Top 5 Results")
            
            if not market_data['top_5']:
                st.warning(f"No stocks found for {market_data['name']}.")
                continue

            df = pd.DataFrame(market_data['top_5'])
            
            # Format for display
            df_display = pd.DataFrame()
            df_display['Symbol'] = df['symbol']
            df_display['Price'] = df['current_price'].map('{:,.2f}'.format)
            df_display['Score'] = df['swing_score']
            df_display['Recommendation'] = df['recommendation']
            df_display['Risk'] = df['risk_level']
            df_display['Confidence'] = df['confidence']
            
            st.dataframe(df_display.style.apply(style_rows, axis=1), use_container_width=True)

            # Detailed view for each of the top 5
            for index, row in df.iterrows():
                with st.expander(f"🔍 Detailed Analysis for {row['symbol']}"):
                    display_detailed_analysis(row)
    else:
        st.info("Click 'Scan All Markets' to get the latest swing trading signals.")

def display_detailed_analysis(stock_data):
    """Displays a detailed breakdown of a stock's analysis."""
    cols = st.columns([2, 3])
    
    with cols[0]:
        st.metric("Swing Score", f"{stock_data['swing_score']}/100")
        st.metric("Recommendation", stock_data['recommendation'])
        st.metric("Risk Level", stock_data['risk_level'])
        st.metric("Confidence", stock_data['confidence'])

    with cols[1]:
        st.markdown("**Technical Analysis**")
        tech = stock_data['technical_indicators']
        st.text(f"RSI: {tech['rsi']['value']:.1f} ({tech['rsi']['status']})")
        st.text(f"MACD: {tech['macd']['status']}")
        st.text(f"Trend Strength (ADX): {tech['adx']['trend_strength']}")
        st.text(f"Volume (OBV): {tech['volume_analysis']['obv_trend']}")
        
        st.markdown("**Risk Management**")
        risk = stock_data['risk_management']
        st.text(f"Stop Loss: {risk['stop_loss']:.2f}")
        st.text(f"Target 1: {risk['target_1']:.2f}")
        st.text(f"Risk/Reward: {risk['risk_reward_ratio']}")

def style_rows(row):
    """Style dataframe rows based on recommendation"""
    if 'BUY' in row['Recommendation']:
        return ['background-color: #2E7D32'] * len(row) # Dark Green
    elif 'SELL' in row['Recommendation']:
        return ['background-color: #C62828'] * len(row) # Dark Red
    elif 'HOLD' in row['Recommendation']:
        return ['background-color: #FF8F00'] * len(row) # Amber
    else: # AVOID
        return ['background-color: #455A64'] * len(row) # Blue Grey

def main():
    dashboard = TradingDashboard()
    
    # Sidebar
    st.sidebar.title("🎯 Trading Controls")
    
    # Show logout option in sidebar
    show_logout_option()
    
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
        markets = get_comprehensive_market_watchlists()
    elif market_filter == "🇺🇸 USA":
        watchlists = get_comprehensive_market_watchlists()
        markets = {"usa": watchlists["usa"]}
    elif market_filter == "🇮🇳 India":
        watchlists = get_comprehensive_market_watchlists()
        markets = {"india": watchlists["india"]}
    elif market_filter == "🇲🇾 Malaysia":
        watchlists = get_comprehensive_market_watchlists()
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
    col_refresh1, col_refresh2 = st.columns([1, 3])
    
    with col_refresh1:
        if st.button("🚀 Scan All Markets", type="primary", help="Run a full scan using the Master Analyzer"):
            st.session_state.swing_data = None # Clear previous results
            st.session_state.last_scan_time = datetime.now()
            
            progress_bar = st.progress(0, text="Initializing scan...")
            
            def progress_callback(message, progress):
                progress_bar.progress(progress, text=message)

            try:
                # Use the master analyzer directly
                results = dashboard.analyzer.get_daily_swing_signals(progress_callback)
                st.session_state.swing_data = results
                progress_bar.progress(1.0, text="Scan complete!")
                time.sleep(1) # Keep message on screen
                progress_bar.empty()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Scan failed: {e}")
                progress_bar.empty()

    with col_refresh2:
        if st.session_state.last_scan_time:
            st.info(f"Last scan: {st.session_state.last_scan_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Display results
    if st.session_state.swing_data:
        results = st.session_state.swing_data
        
        st.subheader("Scan Summary")
        summary_cols = st.columns(3)
        summary_cols[0].metric("Total Stocks Scanned", results['total_stocks_scanned'])
        summary_cols[1].metric("Total Scan Duration", f"{results['scan_duration']:.1f}s")
        
        for market_key, market_data in results['markets'].items():
            if selected_market != "All Markets" and market_data['name'] != selected_market:
                continue

            st.markdown(f"### {market_data['name']} Top 5 Results")
            
            if not market_data['top_5']:
                st.warning(f"No stocks found for {market_data['name']}.")
                continue

            df = pd.DataFrame(market_data['top_5'])
            
            # Format for display
            df_display = pd.DataFrame()
            df_display['Symbol'] = df['symbol']
            df_display['Price'] = df['current_price'].map('{:,.2f}'.format)
            df_display['Score'] = df['swing_score']
            df_display['Recommendation'] = df['recommendation']
            df_display['Risk'] = df['risk_level']
            df_display['Confidence'] = df['confidence']
            
            st.dataframe(df_display.style.apply(style_rows, axis=1), use_container_width=True)

            # Detailed view for each of the top 5
            for index, row in df.iterrows():
                with st.expander(f"🔍 Detailed Analysis for {row['symbol']}"):
                    display_detailed_analysis(row)
    else:
        st.info("Click 'Scan All Markets' to get the latest swing trading signals.")

def display_detailed_analysis(stock_data):
    """Displays a detailed breakdown of a stock's analysis."""
    cols = st.columns([2, 3])
    
    with cols[0]:
        st.metric("Swing Score", f"{stock_data['swing_score']}/100")
        st.metric("Recommendation", stock_data['recommendation'])
        st.metric("Risk Level", stock_data['risk_level'])
        st.metric("Confidence", stock_data['confidence'])

    with cols[1]:
        st.markdown("**Technical Analysis**")
        tech = stock_data['technical_indicators']
        st.text(f"RSI: {tech['rsi']['value']:.1f} ({tech['rsi']['status']})")
        st.text(f"MACD: {tech['macd']['status']}")
        st.text(f"Trend Strength (ADX): {tech['adx']['trend_strength']}")
        st.text(f"Volume (OBV): {tech['volume_analysis']['obv_trend']}")
        
        st.markdown("**Risk Management**")
        risk = stock_data['risk_management']
        st.text(f"Stop Loss: {risk['stop_loss']:.2f}")
        st.text(f"Target 1: {risk['target_1']:.2f}")
        st.text(f"Risk/Reward: {risk['risk_reward_ratio']}")

def style_rows(row):
    """Style dataframe rows based on recommendation"""
    if 'BUY' in row['Recommendation']:
        return ['background-color: #2E7D32'] * len(row) # Dark Green
    elif 'SELL' in row['Recommendation']:
        return ['background-color: #C62828'] * len(row) # Dark Red
    elif 'HOLD' in row['Recommendation']:
        return ['background-color: #FF8F00'] * len(row) # Amber
    else: # AVOID
        return ['background-color: #455A64'] * len(row) # Blue Grey

def main():
    dashboard = TradingDashboard()
    
    # Sidebar
    st.sidebar.title("🎯 Trading Controls")
    
    # Show logout option in sidebar
    show_logout_option()
    
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
        markets = get_comprehensive_market_watchlists()
    elif market_filter == "🇺🇸 USA":
        watchlists = get_comprehensive_market_watchlists()
        markets = {"usa": watchlists["usa"]}
    elif market_filter == "🇮🇳 India":
        watchlists = get_comprehensive_market_watchlists()
        markets = {"india": watchlists["india"]}
    elif market_filter == "🇲🇾 Malaysia":
        watchlists = get_comprehensive_market_watchlists()
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
    col_refresh1, col_refresh2 = st.columns([1, 3])
    
    with col_refresh1:
        if st.button("🚀 Scan All Markets", type="primary", help="Run a full scan using the Master Analyzer"):
            st.session_state.swing_data = None # Clear previous results
            st.session_state.last_scan_time = datetime.now()
            
            progress_bar = st.progress(0, text="Initializing scan...")
            
            def progress_callback(message, progress):
                progress_bar.progress(progress, text=message)

            try:
                # Use the master analyzer directly
                results = dashboard.analyzer.get_daily_swing_signals(progress_callback)
                st.session_state.swing_data = results
                progress_bar.progress(1.0, text="Scan complete!")
                time.sleep(1) # Keep message on screen
                progress_bar.empty()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Scan failed: {e}")
                progress_bar.empty()

    with col_refresh2:
        if st.session_state.last_scan_time:
            st.info(f"Last scan: {st.session_state.last_scan_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Display results
    if st.session_state.swing_data:
        results = st.session_state.swing_data
        
        st.subheader("Scan Summary")
        summary_cols = st.columns(3)
        summary_cols[0].metric("Total Stocks Scanned", results['total_stocks_scanned'])
        summary_cols[1].metric("Total Scan Duration", f"{results['scan_duration']:.1f}s")
        
        for market_key, market_data in results['markets'].items():
            if selected_market != "All Markets" and market_data['name'] != selected_market:
                continue

            st.markdown(f"### {market_data['name']} Top 5 Results")
            
            if not market_data['top_5']:
                st.warning(f"No stocks found for {market_data['name']}.")
                continue

            df = pd.DataFrame(market_data['top_5'])
            
            # Format for display
            df_display = pd.DataFrame()
            df_display['Symbol'] = df['symbol']
            df_display['Price'] = df['current_price'].map('{:,.2f}'.format)
            df_display['Score'] = df['swing_score']
            df_display['Recommendation'] = df['recommendation']
            df_display['Risk'] = df['risk_level']
            df_display['Confidence'] = df['confidence']
            
            st.dataframe(df_display.style.apply(style_rows, axis=1), use_container_width=True)

            # Detailed view for each of the top 5
            for index, row in df.iterrows():
                with st.expander(f"🔍 Detailed Analysis for {row['symbol']}"):
                    display_detailed_analysis(row)
    else:
        st.info("Click 'Scan All Markets' to get the latest swing trading signals.")

def display_detailed_analysis(stock_data):
    """Displays a detailed breakdown of a stock's analysis."""
    cols = st.columns([2, 3])
    
    with cols[0]:
        st.metric("Swing Score", f"{stock_data['swing_score']}/100")
        st.metric("Recommendation", stock_data['recommendation'])
        st.metric("Risk Level", stock_data['risk_level'])
        st.metric("Confidence", stock_data['confidence'])

    with cols[1]:
        st.markdown("**Technical Analysis**")
        tech = stock_data['technical_indicators']
        st.text(f"RSI: {tech['rsi']['value']:.1f} ({tech['rsi']['status']})")
        st.text(f"MACD: {tech['macd']['status']}")
        st.text(f"Trend Strength (ADX): {tech['adx']['trend_strength']}")
        st.text(f"Volume (OBV): {tech['volume_analysis']['obv_trend']}")
        
        st.markdown("**Risk Management**")
        risk = stock_data['risk_management']
        st.text(f"Stop Loss: {risk['stop_loss']:.2f}")
        st.text(f"Target 1: {risk['target_1']:.2f}")
        st.text(f"Risk/Reward: {risk['risk_reward_ratio']}")

def style_rows(row):
    """Style dataframe rows based on recommendation"""
    if 'BUY' in row['Recommendation']:
        return ['background-color: #2E7D32'] * len(row) # Dark Green
    elif 'SELL' in row['Recommendation']:
        return ['background-color: #C62828'] * len(row) # Dark Red
    elif 'HOLD' in row['Recommendation']:
        return ['background-color: #FF8F00'] * len(row) # Amber
    else: # AVOID
        return ['background-color: #455A64'] * len(row) # Blue Grey

def main():
    dashboard = TradingDashboard()
    
    # Sidebar
    st.sidebar.title("🎯 Trading Controls")
    
    # Show logout option in sidebar
    show_logout_option()
    
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
        markets = get_comprehensive_market_watchlists()
    elif market_filter == "🇺🇸 USA":
        watchlists = get_comprehensive_market_watchlists()
        markets = {"usa": watchlists["usa"]}
    elif market_filter == "🇮🇳 India":
        watchlists = get_comprehensive_market_watchlists()
        markets = {"india": watchlists["india"]}
    elif market_filter == "🇲🇾 Malaysia":
        watchlists = get_comprehensive_market_watchlists()
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
    col_refresh1, col_refresh2 = st.columns([1, 3])
    
    with col_refresh1:
        if st.button("🚀 Scan All Markets", type="primary", help="Run a full scan using the Master Analyzer"):
            st.session_state.swing_data = None # Clear previous results
            st.session_state.last_scan_time = datetime.now()
            
            progress_bar = st.progress(0, text="Initializing scan...")
            
            def progress_callback(message, progress):
                progress_bar.progress(progress, text=message)

            try:
                # Use the master analyzer directly
                results = dashboard.analyzer.get_daily_swing_signals(progress_callback)
                st.session_state.swing_data = results
                progress_bar.progress(1.0, text="Scan complete!")
                time.sleep(1) # Keep message on screen
                progress_bar.empty()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Scan failed: {e}")
                progress_bar.empty()

    with col_refresh2:
        if st.session_state.last_scan_time:
            st.info(f"Last scan: {st.session_state.last_scan_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Display results
    if st.session_state.swing_data:
        results = st.session_state.swing_data
        
        st.subheader("Scan Summary")
        summary_cols = st.columns(3)
        summary_cols[0].metric("Total Stocks Scanned", results['total_stocks_scanned'])
        summary_cols[1].metric("Total Scan Duration", f"{results['scan_duration']:.1f}s")
        
        for market_key, market_data in results['markets'].items():
            if selected_market != "All Markets" and market_data['name'] != selected_market:
                continue

            st.markdown(f"### {market_data['name']} Top 5 Results")
            
            if not market_data['top_5']:
                st.warning(f"No stocks found for {market_data['name']}.")
                continue

            df = pd.DataFrame(market_data['top_5'])
            
            # Format for display
            df_display = pd.DataFrame()
            df_display['Symbol'] = df['symbol']
            df_display['Price'] = df['current_price'].map('{:,.2f}'.format)
            df_display['Score'] = df['swing_score']
            df_display['Recommendation'] = df['recommendation']
            df_display['Risk'] = df['risk_level']
            df_display['Confidence'] = df['confidence']
            
            st.dataframe(df_display.style.apply(style_rows, axis=1), use_container_width=True)

            # Detailed view for each of the top 5
            for index, row in df.iterrows():
                with st.expander(f"🔍 Detailed Analysis for {row['symbol']}"):
                    display_detailed_analysis(row)
    else:
        st.info("Click 'Scan All Markets' to get the latest swing trading signals.")

def display_detailed_analysis(stock_data):
    """Displays a detailed breakdown of a stock's analysis."""
    cols = st.columns([2, 3])
    
    with cols[0]:
        st.metric("Swing Score", f"{stock_data['swing_score']}/100")
        st.metric("Recommendation", stock_data['recommendation'])
        st.metric("Risk Level", stock_data['risk_level'])
        st.metric("Confidence", stock_data['confidence'])

    with cols[1]:
        st.markdown("**Technical Analysis**")
        tech = stock_data['technical_indicators']
        st.text(f"RSI: {tech['rsi']['value']:.1f} ({tech['rsi']['status']})")
        st.text(f"MACD: {tech['macd']['status']}")
        st.text(f"Trend Strength (ADX): {tech['adx']['trend_strength']}")
        st.text(f"Volume (OBV): {tech['volume_analysis']['obv_trend']}")
        
        st.markdown("**Risk Management**")
        risk = stock_data['risk_management']
        st.text(f"Stop Loss: {risk['stop_loss']:.2f}")
        st.text(f"Target 1: {risk['target_1']:.2f}")
        st.text(f"Risk/Reward: {risk['risk_reward_ratio']}")

def style_rows(row):
    """Style dataframe rows based on recommendation"""
    if 'BUY' in row['Recommendation']:
        return ['background-color: #2E7D32'] * len(row) # Dark Green
    elif 'SELL' in row['Recommendation']:
        return ['background-color: #C62828'] * len(row) # Dark Red
    elif 'HOLD' in row['Recommendation']:
        return ['background-color: #FF8F00'] * len(row) # Amber
    else: # AVOID
        return ['background-color: #455A64'] * len(row) # Blue Grey

def main():
    dashboard = TradingDashboard()
    
    # Sidebar
    st.sidebar.title("🎯 Trading Controls")
    
    # Show logout option in sidebar
    show_logout_option()
    
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
        markets = get_comprehensive_market_watchlists()
    elif market_filter == "🇺🇸 USA":
        watchlists = get_comprehensive_market_watchlists()
        markets = {"usa": watchlists["usa"]}
    elif market_filter == "🇮🇳 India":
        watchlists = get_comprehensive_market_watchlists()
        markets = {"india": watchlists["india"]}
    elif market_filter == "🇲🇾 Malaysia":
        watchlists = get_comprehensive_market_watchlists()
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
    col_refresh1, col_refresh2 = st.columns([1, 3])
    
    with col_refresh1:
        if st.button("🚀 Scan All Markets", type="primary", help="Run a full scan using the Master Analyzer"):
            st.session_state.swing_data = None # Clear previous results
            st.session_state.last_scan_time = datetime.now()
            
            progress_bar = st.progress(0, text="Initializing scan...")
            
            def progress_callback(message, progress):
                progress_bar.progress(progress, text=message)

            try:
                # Use the master analyzer directly
                results = dashboard.analyzer.get_daily_swing_signals(progress_callback)
                st.session_state.swing_data = results
                progress_bar.progress(1.0, text="Scan complete!")
                time.sleep(1) # Keep message on screen
                progress_bar.empty()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Scan failed: {e}")
                progress_bar.empty()

    with col_refresh2:
        if st.session_state.last_scan_time:
            st.info(f"Last scan: {st.session_state.last_scan_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Display results
    if st.session_state.swing_data:
        results = st.session_state.swing_data
        
        st.subheader("Scan Summary")
        summary_cols = st.columns(3)
        summary_cols[0].metric("Total Stocks Scanned", results['total_stocks_scanned'])
        summary_cols[1].metric("Total Scan Duration", f"{results['scan_duration']:.1f}s")
        
        for market_key, market_data in results['markets'].items():
            if selected_market != "All Markets" and market_data['name'] != selected_market:
                continue

            st.markdown(f"### {market_data['name']} Top 5 Results")
            
            if not market_data['top_5']:
                st.warning(f"No stocks found for {market_data['name']}.")
                continue

            df = pd.DataFrame(market_data['top_5'])
            
            # Format for display
            df_display = pd.DataFrame()
            df_display['Symbol'] = df['symbol']
            df_display['Price'] = df['current_price'].map('{:,.2f}'.format)
            df_display['Score'] = df['swing_score']
            df_display['Recommendation'] = df['recommendation']
            df_display['Risk'] = df['risk_level']
            df_display['Confidence'] = df['confidence']
            
            st.dataframe(df_display.style.apply(style_rows, axis=1), use_container_width=True)

            # Detailed view for each of the top 5
            for index, row in df.iterrows():
                with st.expander(f"🔍 Detailed Analysis for {row['symbol']}"):
                    display_detailed_analysis(row)
    else:
        st.info("Click 'Scan All Markets' to get the latest swing trading signals.")

def display_detailed_analysis(stock_data):
    """Displays a detailed breakdown of a stock's analysis."""
    cols = st.columns([2, 3])
    
    with cols[0]:
        st.metric("Swing Score", f"{stock_data['swing_score']}/100")
        st.metric("Recommendation", stock_data['recommendation'])
        st.metric("Risk Level", stock_data['risk_level'])
        st.metric("Confidence", stock_data['confidence'])

    with cols[1]:
        st.markdown("**Technical Analysis**")
        tech = stock_data['technical_indicators']
        st.text(f"RSI: {tech['rsi']['value']:.1f} ({tech['rsi']['status']})")
        st.text(f"MACD: {tech['macd']['status']}")
        st.text(f"Trend Strength (ADX): {tech['adx']['trend_strength']}")
        st.text(f"Volume (OBV): {tech['volume_analysis']['obv_trend']}")
        
        st.markdown("**Risk Management**")
        risk = stock_data['risk_management']
        st.text(f"Stop Loss: {risk['stop_loss']:.2f}")
        st.text(f"Target 1: {risk['target_1']:.2f}")
        st.text(f"Risk/Reward: {risk['risk_reward_ratio']}")

def style_rows(row):
    """Style dataframe rows based on recommendation"""
    if 'BUY' in row['Recommendation']:
        return ['background-color: #2E7D32'] * len(row) # Dark Green
    elif 'SELL' in row['Recommendation']:
        return ['background-color: #C62828'] * len(row) # Dark Red
    elif 'HOLD' in row['Recommendation']:
        return ['background-color: #FF8F00'] * len(row) # Amber
    else: # AVOID
        return ['background-color: #455A64'] * len(row) # Blue Grey

def main():
    dashboard = TradingDashboard()
    
    # Sidebar
    st.sidebar.title("🎯 Trading Controls")
    
    # Show logout option in sidebar
    show_logout_option()
    
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
        markets = get_comprehensive_market_watchlists()
    elif market_filter == "🇺🇸 USA":
        watchlists = get_comprehensive_market_watchlists()
        markets = {"usa": watchlists["usa"]}
    elif market_filter == "🇮🇳 India":
        watchlists = get_comprehensive_market_watchlists()
        markets = {"india": watchlists["india"]}
    elif market_filter == "🇲🇾 Malaysia":
        watchlists = get_comprehensive_market_watchlists()
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
    col_refresh1, col_refresh2 = st.columns([1, 3])
    
    with col_refresh1:
        if st.button("🚀 Scan All Markets", type="primary", help="Run a full scan using the Master Analyzer"):
            st.session_state.swing_data = None # Clear previous results
            st.session_state.last_scan_time = datetime.now()
            
            progress_bar = st.progress(0, text="Initializing scan...")
            
            def progress_callback(message, progress):
                progress_bar.progress(progress, text=message)

            try:
                # Use the master analyzer directly
                results = dashboard.analyzer.get_daily_swing_signals(progress_callback)
                st.session_state.swing_data = results
                progress_bar.progress(1.0, text="Scan complete!")
                time.sleep(1) # Keep message on screen
                progress_bar.empty()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Scan failed: {e}")
                progress_bar.empty()

    with col_refresh2:
        if st.session_state.last_scan_time:
            st.info(f"Last scan: {st.session_state.last_scan_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Display results
    if st.session_state.swing_data:
        results = st.session_state.swing_data
        
        st.subheader("Scan Summary")
        summary_cols = st.columns(3)
        summary_cols[0].metric("Total Stocks Scanned", results['total_stocks_scanned'])
        summary_cols[1].metric("Total Scan Duration", f"{results['scan_duration']:.1f}s")
        
        for market_key, market_data in results['markets'].items():
            if selected_market != "All Markets" and market_data['name'] != selected_market:
                continue

            st.markdown(f"### {market_data['name']} Top 5 Results")
            
            if not market_data['top_5']:
                st.warning(f"No stocks found for {market_data['name']}.")
                continue

            df = pd.DataFrame(market_data['top_5'])
            
            # Format for display
            df_display = pd.DataFrame()
            df_display['Symbol'] = df['symbol']
            df_display['Price'] = df['current_price'].map('{:,.2f}'.format)
            df_display['Score'] = df['swing_score']
            df_display['Recommendation'] = df['recommendation']
            df_display['Risk'] = df['risk_level']
            df_display['Confidence'] = df['confidence']
            
            st.dataframe(df_display.style.apply(style_rows, axis=1), use_container_width=True)

            # Detailed view for each of the top 5
            for index, row in df.iterrows():
                with st.expander(f"🔍 Detailed Analysis for {row['symbol']}"):
                    display_detailed_analysis(row)
    else:
        st.info("Click 'Scan All Markets' to get the latest swing trading signals.")

def display_detailed_analysis(stock_data):
    """Displays a detailed breakdown of a stock's analysis."""
    cols = st.columns([2, 3])
    
    with cols[0]:
        st.metric("Swing Score", f"{stock_data['swing_score']}/100")
        st.metric("Recommendation", stock_data['recommendation'])
        st.metric("Risk Level", stock_data['risk_level'])
        st.metric("Confidence", stock_data['confidence'])

    with cols[1]:
        st.markdown("**Technical Analysis**")
        tech = stock_data['technical_indicators']
        st.text(f"RSI: {tech['rsi']['value']:.1f} ({tech['rsi']['status']})")
        st.text(f"MACD: {tech['macd']['status']}")
        st.text(f"Trend Strength (ADX): {tech['adx']['trend_strength']}")
        st.text(f"Volume (OBV): {tech['volume_analysis']['obv_trend']}")
        
        st.markdown("**Risk Management**")
        risk = stock_data['risk_management']
        st.text(f"Stop Loss: {risk['stop_loss']:.2f}")
        st.text(f"Target 1: {risk['target_1']:.2f}")
        st.text(f"Risk/Reward: {risk['risk_reward_ratio']}")

def style_rows(row):
    """Style dataframe rows based on recommendation"""
    if 'BUY' in row['Recommendation']:
        return ['background-color: #2E7D32'] * len(row) # Dark Green
    elif 'SELL' in row['Recommendation']:
        return ['background-color: #C62828'] * len(row) # Dark Red
    elif 'HOLD' in row['Recommendation']:
        return ['background-color: #FF8F00'] * len(row) # Amber
    else: # AVOID
        return ['background-color: #455A64'] * len(row) # Blue Grey

def main():
    dashboard = TradingDashboard()
    
    # Sidebar
    st.sidebar.title("🎯 Trading Controls")
    
    # Show logout option in sidebar
    show_logout_option()
    
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
        markets = get_comprehensive_market_watchlists()
    elif market_filter == "🇺🇸 USA":
        watchlists = get_comprehensive_market_watchlists()
        markets = {"usa": watchlists["usa"]}
    elif market_filter == "🇮🇳 India":
        watchlists = get_comprehensive_market_watchlists()
        markets = {"india": watchlists["india"]}
    elif market_filter == "🇲🇾 Malaysia":
        watchlists = get_comprehensive_market_watchlists()
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
    col_refresh1, col_refresh2 = st.columns([1, 3])
    
    with col_refresh1:
        if st.button("🚀 Scan All Markets", type="primary", help="Run a full scan using the Master Analyzer"):
            st.session_state.swing_data = None # Clear previous results
            st.session_state.last_scan_time = datetime.now()
            
            progress_bar = st.progress(0, text="Initializing scan...")
            
            def progress_callback(message, progress):
                progress_bar.progress(progress, text=message)

            try:
                # Use the master analyzer directly
                results = dashboard.analyzer.get_daily_swing_signals(progress_callback)
                st.session_state.swing_data = results
                progress_bar.progress(1.0, text="Scan complete!")
                time.sleep(1) # Keep message on screen
                progress_bar.empty()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Scan failed: {e}")
                progress_bar.empty()

    with col_refresh2:
        if st.session_state.last_scan_time:
            st.info(f"Last scan: {st.session_state.last_scan_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Display results
    if st.session_state.swing_data:
        results = st.session_state.swing_data
        
        st.subheader("Scan Summary")
        summary_cols = st.columns(3)
        summary_cols[0].metric("Total Stocks Scanned", results['total_stocks_scanned'])
        summary_cols[1].metric("Total Scan Duration", f"{results['scan_duration']:.1f}s")
        
        for market_key, market_data in results['markets'].items():
            if selected_market != "All Markets" and market_data['name'] != selected_market:
                continue

            st.markdown(f"### {market_data['name']} Top 5 Results")
            
            if not market_data['top_5']:
                st.warning(f"No stocks found for {market_data['name']}.")
                continue

            df = pd.DataFrame(market_data['top_5'])
            
            # Format for display
            df_display = pd.DataFrame()
            df_display['Symbol'] = df['symbol']
            df_display['Price'] = df['current_price'].map('{:,.2f}'.format)
            df_display['Score'] = df['swing_score']
            df_display['Recommendation'] = df['recommendation']
            df_display['Risk'] = df['risk_level']
            df_display['Confidence'] = df['confidence']
            
            st.dataframe(df_display.style.apply(style_rows, axis=1), use_container_width=True)

            # Detailed view for each of the top 5
            for index, row in df.iterrows():
                with st.expander(f"🔍 Detailed Analysis for {row['symbol']}"):
                    display_detailed_analysis(row)
    else:
        st.info("Click 'Scan All Markets' to get the latest swing trading signals.")

def display_detailed_analysis(stock_data):
    """Displays a detailed breakdown of a stock's analysis."""
    cols = st.columns([2, 3])
    
    with cols[0]:
        st.metric("Swing Score", f"{stock_data['swing_score']}/100")
        st.metric("Recommendation", stock_data['recommendation'])
        st.metric("Risk Level", stock_data['risk_level'])
        st.metric("Confidence", stock_data['confidence'])

    with cols[1]:
        st.markdown("**Technical Analysis**")
        tech = stock_data['technical_indicators']
        st.text(f"RSI: {tech['rsi']['value']:.1f} ({tech['rsi']['status']})")
        st.text(f"MACD: {tech['macd']['status']}")
        st.text(f"Trend Strength (ADX): {tech['adx']['trend_strength']}")
        st.text(f"Volume (OBV): {tech['volume_analysis']['obv_trend']}")
        
        st.markdown("**Risk Management**")
        risk = stock_data['risk_management']
        st.text(f"Stop Loss: {risk['stop_loss']:.2f}")
        st.text(f"Target 1: {risk['target_1']:.2f}")
        st.text(f"Risk/Reward: {risk['risk_reward_ratio']}")

def style_rows(row):
    """Style dataframe rows based on recommendation"""
    if 'BUY' in row['Recommendation']:
        return ['background-color: #2E7D32'] * len(row) # Dark Green
    elif 'SELL' in row['Recommendation']:
        return ['background-color: #C62828'] * len(row) # Dark Red
    elif 'HOLD'
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
    """Display detailed charts for scanned opportunities"""
    st.header("📈 Technical Analysis Charts")
    
    # Get scan results from session
    scan_results = st.session_state.get('scan_results', {})
    
    # Collect all opportunities from scan results
    all_scanned_stocks = []
    if scan_results and 'markets' in scan_results:
        for market_name, market_data in scan_results['markets'].items():
            opportunities = market_data.get('opportunities', [])
            for opp in opportunities:
                all_scanned_stocks.append({
                    'symbol': opp['symbol'],
                    'market_name': opp.get('market_name', market_name),
                    'score': opp['swing_score'],
                    'recommendation': opp['recommendation'],
                    'price': opp['current_price']
                })
    
    if not all_scanned_stocks:
        st.warning("📊 No scan results available. Please run a scan first from the Live Signals tab.")
        st.info("💡 The Performance tab shows charts for stocks found during your latest scan.")
        return
    
    # Sort by score for better organization
    all_scanned_stocks.sort(key=lambda x: x['score'], reverse=True)
    
    # Create stock options with more detail
    stock_options = []
    for stock in all_scanned_stocks:
        currency = "₹" if '.NS' in stock['symbol'] else "RM" if '.KL' in stock['symbol'] else "$"
        option_text = f"{stock['symbol']} ({stock['market_name']}) - Score: {stock['score']}/100 - {currency}{stock['price']:.2f}"
        stock_options.append(option_text)
    
    # Display scan summary
    st.subheader("🎯 Scan Results Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Total Opportunities", len(all_scanned_stocks))
        strong_buys = len([s for s in all_scanned_stocks if s['score'] >= 75])
        st.metric("🟢 Strong Buy Signals", strong_buys)
    
    with col2:
        buys = len([s for s in all_scanned_stocks if 65 <= s['score'] < 75])
        st.metric("🟡 Buy Signals", buys)
        avg_score = sum(s['score'] for s in all_scanned_stocks) / len(all_scanned_stocks)
        st.metric("📈 Average Score", f"{avg_score:.1f}/100")
    
    with col3:
        markets = len(set(s['market_name'] for s in all_scanned_stocks))
        st.metric("🌍 Markets Scanned", markets)
        if scan_results.get('total_stocks_scanned'):
            st.metric("⚡ Scan Speed", f"{scan_results['total_stocks_scanned']} stocks")
    
    # Stock selector with scanned results
    st.subheader("📊 Select Stock for Technical Analysis")
    selected_option = st.selectbox(
        "Choose from scanned opportunities (sorted by score):",
        stock_options,
        help="These are the actual stocks found during your latest scan"
    )
    
    if selected_option:
        # Extract symbol from selected option
        selected_symbol = selected_option.split(' (')[0]
        selected_stock_data = next(s for s in all_scanned_stocks if s['symbol'] == selected_symbol)
        
        st.info(f"📈 Analyzing **{selected_symbol}** - Scanner Score: **{selected_stock_data['score']}/100** ({selected_stock_data['recommendation']})")
        
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
            
            # Enhanced analysis section with scanner comparison
            st.subheader("🔍 Technical Analysis vs Scanner Results")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 📊 Chart Analysis")
                st.write(f"**Chart Recommendation:** {signals['recommendation']}")
                st.write(f"**Chart Confidence:** {signals['confidence']}%")
                currency = "₹" if '.NS' in selected_symbol else "RM" if '.KL' in selected_symbol else "$"
                st.write(f"**Current Price:** {currency}{analysis['latest']['Close']:.2f}")
                st.write(f"**RSI:** {signals['rsi']:.1f}")
            
            with col2:
                st.markdown("### ⚡ Scanner Results")
                st.write(f"**Scanner Score:** {selected_stock_data['score']}/100")
                st.write(f"**Scanner Recommendation:** {selected_stock_data['recommendation']}")
                st.write(f"**Market:** {selected_stock_data['market_name']}")
                
                # Score interpretation
                if selected_stock_data['score'] >= 75:
                    st.success("🟢 Strong Buy Signal")
                elif selected_stock_data['score'] >= 65:
                    st.info("🟡 Buy Signal") 
                else:
                    st.warning("⚠️ Weak Signal")
            
            with col3:
                st.markdown("### 🎯 Technical Signals")
                st.write(f"**Trend (SMA):** {'🟢 Bullish' if signals['sma_bullish'] else '🔴 Bearish'}")
                st.write(f"**MACD:** {'🟢 Bullish' if signals['macd_bullish'] else '🔴 Bearish'}")
                st.write(f"**BB Position:** {signals['bb_position']}")
                
                # RSI interpretation
                rsi = signals['rsi']
                if rsi > 70:
                    st.write("**RSI Status:** 🔴 Overbought")
                elif rsi < 30:
                    st.write("**RSI Status:** 🟢 Oversold")
                else:
                    st.write("**RSI Status:** 🟡 Neutral")
            
            # Analysis consistency check
            st.markdown("---")
            st.subheader("🔄 Analysis Consistency")
            
            # Compare scanner vs chart recommendations
            scanner_bullish = selected_stock_data['score'] >= 65
            chart_bullish = signals['recommendation'] in ['BUY', 'STRONG BUY']
            
            if scanner_bullish and chart_bullish:
                st.success("✅ **CONSISTENT SIGNALS**: Both scanner and chart analysis show bullish signals!")
                st.write("🎯 **Action**: This appears to be a good swing trading opportunity")
            elif scanner_bullish and not chart_bullish:
                st.warning("⚠️ **MIXED SIGNALS**: Scanner is bullish but chart shows bearish/neutral signals")
                st.write("🔍 **Action**: Consider waiting for better chart confirmation")
            elif not scanner_bullish and chart_bullish:
                st.warning("⚠️ **MIXED SIGNALS**: Chart is bullish but scanner score is low")
                st.write("🔍 **Action**: Scanner may have found other risk factors")
            else:
                st.error("🔴 **BEARISH CONSENSUS**: Both systems show weak/negative signals")
                st.write("❌ **Action**: Avoid this trade opportunity")
            
            # Additional insights
            st.markdown("**💡 Trading Insights:**")
            insights = []
            
            if signals['rsi'] < 35:
                insights.append("• RSI below 35 suggests potential oversold bounce opportunity")
            elif signals['rsi'] > 65:
                insights.append("• RSI above 65 suggests momentum but watch for reversal")
                
            if signals['sma_bullish']:
                insights.append("• Price above moving averages indicates uptrend")
            else:
                insights.append("• Price below moving averages indicates downtrend")
                
            if selected_stock_data['score'] >= 80:
                insights.append("• High scanner score indicates multiple positive technical factors")
            elif selected_stock_data['score'] <= 40:
                insights.append("• Low scanner score suggests multiple risk factors present")
            
            for insight in insights:
                st.write(insight)
        
        else:
            st.error(f"❌ Unable to load chart data for {selected_symbol}")
            st.info("� This might be due to data provider issues or delisted stock")
    
    # Market overview for scanned stocks
    st.markdown("---")
    st.subheader("🌍 Market Overview from Scan")
    
    # Group by market
    markets_summary = {}
    for stock in all_scanned_stocks:
        market = stock['market_name']
        if market not in markets_summary:
            markets_summary[market] = []
        markets_summary[market].append(stock)
    
    market_cols = st.columns(len(markets_summary))
    
    for i, (market, stocks) in enumerate(markets_summary.items()):
        with market_cols[i]:
            st.markdown(f"### {market}")
            avg_score = sum(s['score'] for s in stocks) / len(stocks)
            st.metric("📊 Average Score", f"{avg_score:.1f}/100")
            st.metric("🔢 Opportunities", len(stocks))
            
            # Top performer in this market
            top_stock = max(stocks, key=lambda x: x['score'])
            st.write(f"🏆 **Top**: {top_stock['symbol']}")
            st.write(f"Score: {top_stock['score']}/100")

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

def app_entry_point():
    """Main application entry point with authentication"""
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Check authentication first
    if not check_authentication():
        # Clear any cached content and show login
        st.cache_data.clear()
        st.cache_resource.clear()
        show_login_form()
        st.stop()  # Prevent any further execution
    else:
        # User is authenticated, show main dashboard
        main()

if __name__ == "__main__":
    app_entry_point()
