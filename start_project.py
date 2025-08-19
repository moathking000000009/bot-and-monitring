#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Startup script for Telegram Bot Project
Launches bot and dashboard with simple menu
"""
import os
import sys
import subprocess
import threading
import time
from pathlib import Path

def check_environment():
    """Check if environment is properly set up"""
    print("🔍 Checking environment...")
    
    # Check if .env exists
    if not Path(".env").exists():
        print("❌ .env file not found!")
        print("📝 Creating .env from template...")
        try:
            if Path("env.example").exists():
                import shutil
                shutil.copy("env.example", ".env")
                print("✅ .env created from template")
                print("⚠️  Please edit .env with your actual bot token and API key")
                return False
            else:
                print("❌ env.example not found")
                return False
        except Exception as e:
            print(f"❌ Failed to create .env: {e}")
            return False
    
    # Check required environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    bot_token = os.getenv("BOT_TOKEN") or os.getenv("BOT")
    groq_key = os.getenv("GROQ_API_KEY") or os.getenv("GROQ")
    
    if not bot_token:
        print("❌ BOT_TOKEN not set in .env file")
        return False
    
    if not groq_key:
        print("❌ GROQ_API_KEY not set in .env file")
        return False
    
    print("✅ Environment check passed")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def start_bot():
    """Start the Telegram bot"""
    print("🤖 Starting Telegram bot...")
    try:
        subprocess.run([sys.executable, "bot_upgraded.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot failed to start: {e}")

def start_dashboard():
    """Start the Streamlit dashboard"""
    print("🎛️ Starting Streamlit dashboard...")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_dashboard.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Dashboard failed to start: {e}")

def start_both():
    """Start both bot and dashboard in separate threads"""
    print("🚀 Starting both bot and dashboard...")
    
    # Start bot in background thread
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    
    # Wait a moment for bot to initialize
    time.sleep(3)
    
    # Start dashboard in main thread
    start_dashboard()

def main():
    """Main startup function"""
    print("🤖 Telegram Bot Project - جمعية حفظ النعمة")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment setup incomplete")
        print("Please edit .env file with your credentials and run again")
        input("Press Enter to exit...")
        return
    
    # Check dependencies
    try:
        import telegram
        import streamlit
        import groq
        print("✅ All required packages are available")
    except ImportError:
        print("⚠️  Some packages missing, installing dependencies...")
        if not install_dependencies():
            print("❌ Failed to install dependencies")
            input("Press Enter to exit...")
            return
    
    print("\n🎯 Choose an option:")
    print("1. Start Telegram Bot only")
    print("2. Start Dashboard only")
    print("3. Start Both (Bot + Dashboard)")
    print("4. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == "1":
                start_bot()
                break
            elif choice == "2":
                start_dashboard()
                break
            elif choice == "3":
                start_both()
                break
            elif choice == "4":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            break

if __name__ == "__main__":
    main()
