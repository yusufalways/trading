#!/usr/bin/env python3
"""
Launch the Swing Trading Dashboard
"""

import subprocess
import sys
import os

def main():
    print("🚀 Starting Swing Trading Dashboard...")
    print("=" * 50)
    
    # Change to the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Launch Streamlit dashboard
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "dashboard.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        print("\n💡 Try running manually:")
        print(f"   cd {script_dir}")
        print("   streamlit run dashboard.py")

if __name__ == "__main__":
    main()
