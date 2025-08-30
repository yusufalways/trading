# 🤖 STRICT AI RULES - MUST FOLLOW ALWAYS

## 🚨 **CRITICAL RULES - NO EXCEPTIONS**

### 1. **ONE ANALYSIS SYSTEM ONLY**
- **SCAN STOCKS** Always more than 400+ list
- **ONLY USE**: `tools/master_swing_analyzer.py` 
- **NEVER CREATE** new analysis scripts
- **NEVER USE** backup, clean, corrupted, old versions
- **NEVER REFERENCE** enhanced_signals.py, technical_analysis.py, or any other analyzer
- **Streamlit** Make sure it works in local as wel as streamlit app

### 2. **NO MOCK/SAMPLE/FALLBACK DATA**
- **REAL DATA ONLY** from yfinance
- **NO HARDCODED** scores or prices
- **NO FAKE** recommendations
- **FAIL GRACEFULLY** if data unavailable

### 3. **DASHBOARD INTEGRATION**
- **ALWAYS USE** the master analyzer in dashboard.py
- **NEVER CHANGE** the dashboard to use different scripts
- **ONE IMPORT** only: `from tools.master_swing_analyzer import MasterSwingAnalyzer`

### 4. **CODE MODIFICATIONS**
- **ONLY EDIT** existing master_swing_analyzer.py
- **NEVER CREATE** new analysis files
- **ALWAYS ASK** before major structural changes
- **DOCUMENT** all changes in the file

### 5. **ERROR HANDLING**
- **NEVER CREATE** fallback analyzers
- **FIX THE ISSUE** in the master analyzer
- **LOG ERRORS** clearly
- **RETURN NONE** if analysis fails

## 🎯 **TECHNICAL STANDARDS**

### **Indicator Calculations**
- **RSI**: 0-30 (Oversold), 30-70 (Neutral), 70-100 (Overbought)
- **MACD**: Proper crossover detection, no contradictions
- **Volume**: Real volume analysis, not high/low flags
- **Trend**: ADX-based trend strength measurement

### **Scoring System**
- **Technical**: 60% weight (RSI, MACD, ADX, Volume)
- **Market Context**: 25% weight (Sector, Regime, Relative Strength)
- **External**: 15% weight (Fundamentals, News, Economic)
- **NO SIMPLE ARITHMETIC**: No score = 50 + 20 approaches

### **Data Sources**
- **Price Data**: yfinance only
- **Fundamentals**: Alpha Vantage API (free tier)
- **Economic**: FRED API (free)
- **News**: NewsAPI (free tier)
- **NO MOCK DATA** ever

## 🔧 **FILE STRUCTURE**

### **ALLOWED FILES**
```
tools/master_swing_analyzer.py     ← ONLY analysis file
tools/market_stock_lists.py        ← Stock lists only
tools/portfolio_manager.py         ← Portfolio only
dashboard.py                       ← Main dashboard
```

### **FORBIDDEN ACTIONS**
- ❌ Creating enhanced_signals_v2.py
- ❌ Creating backup files  
- ❌ Creating clean versions
- ❌ Using multiple analyzers
- ❌ Importing old scripts
- ❌ Fallback systems

## 🚀 **WORKFLOW RULES**

### **When User Reports Issues:**
1. **IDENTIFY** the issue in master_swing_analyzer.py
2. **FIX** the issue in the same file
3. **TEST** the fix
4. **NEVER** create new files

### **When Adding Features:**
1. **ADD** to master_swing_analyzer.py
2. **EXTEND** existing classes/methods
3. **MAINTAIN** backward compatibility
4. **DOCUMENT** changes

### **When Debugging:**
1. **EXAMINE** master_swing_analyzer.py code
2. **TRACE** the issue
3. **FIX** in the same file
4. **VERIFY** fix works

## 📋 **RESPONSE FORMAT**

### **Always Start With:**
```
✅ Using master_swing_analyzer.py (the ONE analysis system)
🔍 Issue identified: [specific problem]
🔧 Fix: [what will be changed in master_swing_analyzer.py]
```

### **Never Say:**
- "I'll create a new analyzer"
- "Let me make a backup"
- "I'll use the enhanced_signals script"
- "Let me create a fallback system"

## 🎯 **SUCCESS METRICS**

- ✅ ONE analysis file only
- ✅ NO contradictory signals
- ✅ Real data only
- ✅ Consistent dashboard integration
- ✅ Professional-grade analysis
- ✅ No confusion about which script to use

## 🚨 **VIOLATION CONSEQUENCES**

If AI violates these rules:
1. **STOP** and acknowledge the violation
2. **DELETE** any newly created files
3. **REVERT** to master_swing_analyzer.py
4. **FIX** the issue properly


Testing:
1. python3 -m streamlit run dashboard.py --server.port=8504
2. Opened Simple Browser at http://localhost:8504
3. Observe terminal output for errors and fix it if any
4. Make sure all local packages are updated in streamlit also.

---

# 🎯 **THE GOLDEN RULE**

## **ONE ANALYSIS SYSTEM. ONE SOURCE OF TRUTH. NO EXCEPTIONS.**

**File: `tools/master_swing_analyzer.py`**
**Import: `from tools.master_swing_analyzer import MasterSwingAnalyzer`**
**Usage: `analyzer = MasterSwingAnalyzer()`**

**ANYTHING ELSE IS WRONG.**
