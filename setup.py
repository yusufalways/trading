#!/usr/bin/env python3
"""
Setup script for the Swing Trading Analysis Workspace
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install required Python packages"""
    print("Installing Python requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing requirements: {e}")
        return False
    return True

def create_env_file():
    """Create .env file from template"""
    template_path = Path("config/api_keys.env.template")
    env_path = Path("config/.env")
    
    if template_path.exists() and not env_path.exists():
        print("Creating .env file from template...")
        with open(template_path, 'r') as template:
            content = template.read()
        
        with open(env_path, 'w') as env_file:
            env_file.write(content)
        
        print("✓ .env file created! Please update it with your API keys.")
    else:
        print("ℹ .env file already exists or template not found.")

def create_data_directories():
    """Ensure all data directories exist"""
    directories = [
        "data/india",
        "data/malaysia", 
        "data/usa",
        "strategies",
        "analysis",
        "tools",
        "ai_models",
        "config",
        "docs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✓ Data directories created!")

def main():
    """Main setup function"""
    print("=" * 60)
    print("SWING TRADING WORKSPACE SETUP")
    print("=" * 60)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Create directories
    create_data_directories()
    
    # Create .env file
    create_env_file()
    
    # Install requirements
    if install_requirements():
        print("\n" + "=" * 60)
        print("SETUP COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Update config/.env with your API keys")
        print("2. Run: python tools/data_collector.py")
        print("3. Explore the Jupyter notebook: analysis/getting_started.ipynb")
        print("4. Read the documentation in: docs/swing_trading_guide.md")
    else:
        print("\n" + "=" * 60)
        print("SETUP FAILED!")
        print("=" * 60)
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main()
