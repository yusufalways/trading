# Cloud Deployment Guide for Swing Trading Dashboard

## Free Cloud Hosting Options

### 1. 🚀 **Streamlit Cloud (Recommended - Easiest)**
**Cost**: Completely FREE
**Steps**:
1. Push your code to GitHub (public repo)
2. Go to https://share.streamlit.io
3. Connect GitHub and deploy
4. Get permanent URL like: `https://yourusername-trading-dashboard-main-dashboard-xyz123.streamlit.app`

**Pros**: 
- Zero setup, native Streamlit support
- Automatic updates when you push to GitHub
- Built-in secrets management for API keys

**Cons**: 
- Must be public repo (or paid for private)
- Limited compute resources

### 2. 🐍 **Heroku (Good for Python apps)**
**Cost**: FREE tier available
**Steps**:
1. Create Heroku account
2. Install Heroku CLI
3. Add `Procfile` and `requirements.txt`
4. Deploy with `git push heroku main`

**Pros**: 
- Good Python support
- Custom domain possible
- More control over environment

**Cons**: 
- Sleeps after 30 min inactivity (free tier)
- More complex setup

### 3. ☁️ **Railway (Modern alternative)**
**Cost**: FREE tier with generous limits
**Steps**:
1. Connect GitHub to Railway
2. Deploy directly from repo
3. Automatic SSL and custom domain

**Pros**: 
- No sleep mode on free tier
- Modern interface
- Good performance

### 4. 🔥 **Google Cloud Run (Serverless)**
**Cost**: FREE tier (generous limits)
**Pros**: 
- Scales to zero (no cost when not used)
- Fast startup
- Professional grade

**Cons**: 
- Requires Docker knowledge
- More complex setup

### 5. 🌐 **Render (Simple deployment)**
**Cost**: FREE tier available
**Pros**: 
- Easy deployment
- Good documentation
- No sleep mode

## Quick Setup Instructions

### Option 1: Streamlit Cloud (Easiest - 10 minutes)

1. **Prepare Repository**:
   ```bash
   # Create GitHub repo and push your code
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/trading-dashboard.git
   git push -u origin main
   ```

2. **Deploy**:
   - Go to https://share.streamlit.io
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Main file: `dashboard.py`
   - Click "Deploy"

3. **Configure Secrets** (for API keys):
   - In Streamlit Cloud app settings
   - Add secrets like:
     ```toml
     [secrets]
     alpha_vantage_key = "your_key_here"
     ```

### Option 2: Heroku Deployment

1. **Create Required Files**:
   ```bash
   # Procfile
   echo "web: streamlit run dashboard.py --server.port $PORT --server.address 0.0.0.0" > Procfile
   
   # runtime.txt (specify Python version)
   echo "python-3.12.0" > runtime.txt
   ```

2. **Deploy**:
   ```bash
   heroku create your-trading-dashboard
   git push heroku main
   ```

## Data Persistence in Cloud

### Option 1: Use Cloud Database (Recommended)
```python
# Replace JSON file with SQLite database
import sqlite3
import json

class CloudPortfolioManager:
    def __init__(self, db_url=None):
        if db_url:
            # Use cloud database (PostgreSQL, etc.)
            self.db = db_url
        else:
            # Use SQLite for simple cloud hosting
            self.db = 'portfolio.db'
```

### Option 2: Use GitHub as Storage
```python
# Automatically commit portfolio changes to GitHub
import subprocess

def save_portfolio_to_github(self):
    subprocess.run(['git', 'add', 'data/paper_portfolio.json'])
    subprocess.run(['git', 'commit', '-m', 'Update portfolio'])
    subprocess.run(['git', 'push'])
```

### Option 3: Use Cloud Storage
- **Google Drive API**: Free 15GB
- **Dropbox API**: Free 2GB  
- **AWS S3**: Free tier 5GB

## Pre-deployment Checklist

### 1. **Remove Local Dependencies**
```python
# Replace absolute paths with relative paths
# Update config files to use environment variables
```

### 2. **Add Environment Variables**
```python
import os

# Replace hardcoded values
API_KEY = os.getenv('ALPHA_VANTAGE_KEY', 'demo_key')
```

### 3. **Update Requirements**
```bash
pip freeze > requirements.txt
```

### 4. **Test Locally**
```bash
# Test with production-like settings
streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0
```

## Security Considerations

### 1. **API Keys Protection**
```python
# Never commit API keys to public repos
# Use environment variables or secrets management
```

### 2. **Authentication (Optional)**
```python
# Add login system if needed
import streamlit_authenticator as stauth
```

### 3. **Rate Limiting**
```python
# Implement caching to avoid API rate limits
@st.cache_data(ttl=300)  # 5-minute cache
def get_stock_data(symbol):
    # Your API calls here
```

## Expected Timeline
- **Streamlit Cloud**: 10-15 minutes
- **Heroku**: 30-45 minutes  
- **Railway**: 15-20 minutes
- **Google Cloud Run**: 1-2 hours (if new to Docker)

## Recommended Approach
1. Start with **Streamlit Cloud** (easiest)
2. If you need more control, upgrade to **Railway** or **Heroku**
3. For production use, consider **Google Cloud Run**

Would you like me to help you set up deployment for any of these options?
