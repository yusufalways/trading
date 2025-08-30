#!/usr/bin/env python3
"""
Legacy Code Cleanup Script
Removes unused analysis methods from enhanced_signals.py after unified analysis implementation
"""

import re
import os

def clean_enhanced_signals():
    """Remove legacy analysis code and orphaned methods"""
    
    file_path = "/Users/yusufalways/trading/tools/enhanced_signals.py"
    
    # Read the current file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Methods to completely remove (they're duplicated or orphaned)
    methods_to_remove = [
        '_legacy_analysis',  # Not used since unified analysis implemented
    ]
    
    # Find and remove each method
    for method_name in methods_to_remove:
        pattern = rf'    def {method_name}\(.*?\n(?:        .*\n)*?(?=    def|\nclass|\n# |$)'
        content = re.sub(pattern, '', content, flags=re.MULTILINE | re.DOTALL)
    
    # Remove duplicate method fragments and orphaned code
    # Remove the duplicate calculation block that got orphaned
    orphaned_pattern = r'            if current_macd > current_macd_signal:.*?return None\n'
    content = re.sub(orphaned_pattern, '', content, flags=re.MULTILINE | re.DOTALL)
    
    # Clean up extra blank lines
    content = re.sub(r'\n\n\n+', '\n\n', content)
    
    # Write back the cleaned content
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Cleaned up enhanced_signals.py:")
    print(f"   - Removed {len(methods_to_remove)} legacy methods")
    print("   - Removed orphaned code fragments")
    print("   - Cleaned up formatting")

def validate_dashboard_imports():
    """Ensure dashboard can still import required functions"""
    try:
        from tools.enhanced_signals import get_daily_swing_signals, get_market_watchlists, get_portfolio_analysis
        print("✅ Dashboard imports validated successfully")
        return True
    except ImportError as e:
        print(f"❌ Dashboard import validation failed: {e}")
        return False

def main():
    """Run the cleanup process"""
    print("🧹 Starting legacy code cleanup...")
    
    # Create backup
    backup_path = "/Users/yusufalways/trading/tools/enhanced_signals.py.backup"
    os.system(f"cp /Users/yusufalways/trading/tools/enhanced_signals.py {backup_path}")
    print(f"📦 Created backup at {backup_path}")
    
    # Clean the file
    clean_enhanced_signals()
    
    # Validate imports still work
    if validate_dashboard_imports():
        print("🎉 Cleanup completed successfully!")
        print("💡 The unified analysis system is now the primary analysis engine")
        print("🔄 Dashboard compatibility maintained through wrapper methods")
    else:
        print("⚠️  Import validation failed - restoring backup")
        os.system(f"cp {backup_path} /Users/yusufalways/trading/tools/enhanced_signals.py")

if __name__ == "__main__":
    main()
