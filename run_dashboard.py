#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple script to run the Streamlit dashboard
"""
import subprocess
import sys
import os

def main():
    """Run the Streamlit dashboard"""
    print("🚀 Starting Telegram Bot Dashboard...")
    print("📊 Opening at http://localhost:8501")
    
    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_dashboard.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Failed to start dashboard: {e}")
        print("💡 Make sure you have installed the requirements:")
        print("   pip install -r requirements.txt")

if __name__ == "__main__":
    main()
