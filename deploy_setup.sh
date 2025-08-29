#!/bin/bash
# Quick Cloud Deployment Script

echo "🚀 Swing Trading Dashboard - Cloud Deployment Setup"
echo "=================================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📂 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit: Swing Trading Dashboard"
    echo "✅ Git repository initialized"
else
    echo "📂 Git repository already exists"
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# Streamlit
.streamlit/secrets.toml

# Data files (optional - uncomment if you don't want to deploy with existing trades)
# data/paper_portfolio.json

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
EOF
    echo "✅ .gitignore created"
fi

# Check requirements.txt
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt found"
else
    echo "❌ requirements.txt not found - creating basic one"
    cat > requirements.txt << EOF
streamlit>=1.39.0
pandas>=1.5.0
numpy>=1.21.0
yfinance>=0.2.0
plotly>=5.0.0
requests>=2.31.0
python-dateutil>=2.8.2
EOF
fi

# Check if Procfile exists
if [ -f "Procfile" ]; then
    echo "✅ Procfile found (for Heroku deployment)"
else
    echo "📝 Creating Procfile for Heroku..."
    echo "web: streamlit run dashboard.py --server.port \$PORT --server.address 0.0.0.0 --server.headless true" > Procfile
fi

echo ""
echo "🎯 Next Steps for Cloud Deployment:"
echo ""
echo "OPTION 1 - Streamlit Cloud (Easiest):"
echo "1. Push code to GitHub:"
echo "   git remote add origin https://github.com/yourusername/trading-dashboard.git"
echo "   git push -u origin main"
echo "2. Go to https://share.streamlit.io"
echo "3. Connect GitHub and deploy"
echo "4. Add secrets in app settings if needed"
echo ""
echo "OPTION 2 - Heroku:"
echo "1. Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli"
echo "2. heroku login"
echo "3. heroku create your-trading-dashboard"
echo "4. git push heroku main"
echo ""
echo "OPTION 3 - Railway:"
echo "1. Go to https://railway.app"
echo "2. Connect GitHub repository"
echo "3. Deploy automatically"
echo ""
echo "📊 Your current portfolio data:"
python3 -c "
try:
    from tools.portfolio_manager import PaperTradingPortfolio
    from config.watchlist import TRADING_CONFIG
    portfolio = PaperTradingPortfolio(initial_capital=TRADING_CONFIG['initial_capital'])
    positions = portfolio.get_current_positions()
    print(f'  📈 {len(positions)} positions will be deployed')
    for pos in positions:
        print(f'     • {pos[\"symbol\"]}: {pos[\"shares\"]} shares')
except Exception as e:
    print(f'  ⚠️  Could not load portfolio: {e}')
"
echo ""
echo "✅ Setup complete! Choose a deployment option above."
