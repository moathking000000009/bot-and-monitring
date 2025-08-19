#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Streamlit Dashboard for Telegram Bot
Comprehensive UI for monitoring and managing the bot
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path
import threading
import time
import json
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import bot modules with fallbacks
try:
    from config import Config
    CONFIG_AVAILABLE = True
except ImportError as e:
    st.error(f"❌ Failed to import config: {e}")
    CONFIG_AVAILABLE = False

try:
    from utils import data_manager, rate_limiter, groq_client
    UTILS_AVAILABLE = True
except ImportError as e:
    st.error(f"❌ Failed to import utils: {e}")
    UTILS_AVAILABLE = False

try:
    from bot_upgraded import TelegramBot
    BOT_AVAILABLE = True
except ImportError as e:
    st.error(f"❌ Failed to import bot: {e}")
    BOT_AVAILABLE = False

import streamlit.components.v1 as components

# Theme switcher
theme = st.sidebar.selectbox("🌈 Theme", ["Default", "Light", "Dark", "Purple"])
if theme == "Light":
    st.markdown("""
        <style>
        body, .main, .stApp { background: #f8f9fa !important; color: #222 !important; }
        </style>
    """, unsafe_allow_html=True)
elif theme == "Dark":
    st.markdown("""
        <style>
        body, .main, .stApp { background: #222 !important; color: #f8f9fa !important; }
        </style>
    """, unsafe_allow_html=True)
elif theme == "Purple":
    st.markdown("""
        <style>
        body, .main, .stApp { background: #6a4fb6 !important; color: #fff !important; }
        </style>
    """, unsafe_allow_html=True)
st.set_page_config(
    page_title="Telegram Bot Dashboard - جمعية حفظ النعمة",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-online { background-color: #00ff00; }
    .status-offline { background-color: #ff0000; }
    .status-warning { background-color: #ffaa00; }
    .stButton > button {
        width: 100%;
        margin: 0.5rem 0;
    }
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

class BotDashboard:
    """Main dashboard class"""
    
    def __init__(self):
        # Use st.session_state to persist objects across reruns
        if 'bot' not in st.session_state:
            st.session_state.bot = None
        if 'bot_running' not in st.session_state:
            st.session_state.bot_running = False
        
    def load_data(self):
        """Load data from Excel/CSV file with fallbacks"""
        try:
            if not UTILS_AVAILABLE:
                return pd.DataFrame()
            
            # Try to load data using data manager
            try:
                df = data_manager._load_data()
                if not df.empty:
                    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                return df
            except Exception as e:
                logger.warning(f"Data manager failed, trying direct file access: {e}")
                
                # Fallback: try to load files directly
                excel_file = getattr(Config, 'EXCEL_FILE', 'requests.xlsx') if CONFIG_AVAILABLE else 'requests.xlsx'
                csv_file = excel_file.replace('.xlsx', '.csv')
                
                if os.path.exists(excel_file):
                    try:
                        df = pd.read_excel(excel_file, engine='openpyxl')
                        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                        return df
                    except Exception:
                        # Try CSV fallback
                        if os.path.exists(csv_file):
                            df = pd.read_csv(csv_file)
                            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                            return df
                elif os.path.exists(csv_file):
                    df = pd.read_csv(csv_file)
                    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                    return df
                
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            st.error(f"❌ Error loading data: {e}")
            return pd.DataFrame()
    
    def get_bot_status(self):
        """Get current bot status"""
        if st.session_state.bot and st.session_state.bot.is_running:
            return "🟢 Online", "success"
        else:
            return "🔴 Offline", "error"
    
    def start_bot(self):
        """Start the bot in a separate thread"""
        if st.session_state.bot_running:
            return False
        
        try:
            if not BOT_AVAILABLE:
                st.error("❌ Bot module not available")
                return False
            
            # Create bot instance and start it using its internal method
            st.session_state.bot = TelegramBot()
            st.session_state.bot.start()
            st.session_state.bot_running = True
            time.sleep(2)  # Wait for bot to initialize
            return True
        except Exception as e:
            st.error(f"❌ Failed to start bot: {e}")
            st.session_state.bot_running = False
            return False
    
    def stop_bot(self):
        """Stop the bot gracefully"""
        if not st.session_state.bot_running:
            return True
        
        try:
            # Stop the bot using its internal method
            if st.session_state.bot:
                st.session_state.bot.stop()
            st.session_state.bot_running = False
            return True
        except Exception as e:
            st.error(f"❌ Failed to stop bot: {e}")
            return False

def main():
    """Main dashboard function"""
    
    # Initialize dashboard
    dashboard = BotDashboard()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Telegram Bot Dashboard</h1>
        <h3>جمعية حفظ النعمة - Hail Food Preservation Society</h3>
        <p>Comprehensive monitoring and management interface</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show import status
    if not all([CONFIG_AVAILABLE, UTILS_AVAILABLE, BOT_AVAILABLE]):
        st.warning("⚠️ Some modules are not available. Dashboard will run with limited functionality.")
    
    # Sidebar
    st.sidebar.title("🎛️ Control Panel")
    
    # Bot Control Section
    st.sidebar.header("Bot Control")
    
    if BOT_AVAILABLE:
        # Bot status
        status, _ = dashboard.get_bot_status()
        st.sidebar.markdown(f"**Status:** {status}")
        
        # Bot control buttons
        col1, col2 = st.sidebar.columns(2)
        
        if col1.button("🚀 Start Bot", type="primary"):
            if dashboard.start_bot():
                st.success("✅ Bot started successfully!")
                st.rerun()
        
        if col2.button("🛑 Stop Bot"):
            if dashboard.stop_bot():
                st.success("✅ Bot stopped successfully!")
                st.rerun()
        
        # Bot configuration
        st.sidebar.header("Configuration")
        if st.sidebar.button("⚙️ Reload Config"):
            try:
                if CONFIG_AVAILABLE:
                    Config.load_env()
                    st.success("✅ Configuration reloaded!")
                else:
                    st.error("❌ Config module not available")
            except Exception as e:
                st.error(f"❌ Failed to reload config: {e}")
    else:
        st.sidebar.error("❌ Bot modules are not available")
    
    # Quick stats in sidebar
    st.sidebar.header("📊 Quick Stats")
    try:
        df = dashboard.load_data()
        if not df.empty:
            total_requests = len(df)
            today_requests = len(df[df['timestamp'].dt.date == datetime.now().date()])
            unique_users = df['user_id'].nunique() if 'user_id' in df.columns else 0
            
            st.sidebar.metric("Total Requests", total_requests)
            st.sidebar.metric("Today's Requests", today_requests)
            st.sidebar.metric("Unique Users", unique_users)
        else:
            st.sidebar.info("No data available")
    except Exception as e:
        st.sidebar.error(f"Error loading stats: {e}")
    
    # Main content area
    if BOT_AVAILABLE:
        # Create tabs for different sections
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📊 Overview", "📈 Analytics", "💾 Data Management", 
            "🛡️ Security", "⚙️ Settings", "📝 Logs"
        ])
        
        with tab1:
            show_overview_tab(dashboard)
        
        with tab2:
            show_analytics_tab(dashboard)
        
        with tab3:
            show_data_management_tab(dashboard)
        
        with tab4:
            show_security_tab(dashboard)
        
        with tab5:
            show_settings_tab(dashboard)
        
        with tab6:
            show_logs_tab(dashboard)
    else:
        st.error("❌ Bot modules are not available. Please check your installation.")

def show_overview_tab(dashboard):
    """Show overview tab with key metrics"""
    st.header("📊 Bot Overview")
    
    # Load data
    df = dashboard.load_data()
    
    # Key metrics in a grid
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_requests = len(df) if not df.empty else 0
        st.markdown(f"""
        <div class="metric-container">
            <h3>📈 Total Requests</h3>
            <h2>{total_requests:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        today_requests = len(df[df['timestamp'].dt.date == datetime.now().date()]) if not df.empty else 0
        st.markdown(f"""
        <div class="metric-container">
            <h3>📅 Today's Requests</h3>
            <h2>{today_requests:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        unique_users = df['user_id'].nunique() if not df.empty and 'user_id' in df.columns else 0
        st.markdown(f"""
        <div class="metric-container">
            <h3>👥 Unique Users</h3>
            <h2>{unique_users:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        status, _ = dashboard.get_bot_status()
        status_emoji = "🟢" if "Online" in status else "🔴" if "Offline" in status else "🟡"
        st.markdown(f"""
        <div class="metric-container">
            <h3>🤖 Bot Status</h3>
            <h2>{status_emoji} {status.split()[1]}</h2>
        </div>
        """, unsafe_allow_html=True)
    

    # Real-Time Bot Status
    st.subheader("� Real-Time Bot Status")
    status, _ = dashboard.get_bot_status()
    st.info(f"Bot Status: {status}")
    if not df.empty:
        last_msg = df.iloc[-1]
        st.write(f"**Last Message:** {last_msg.get('message', '')}")
        st.write(f"**From:** {last_msg.get('username', '')} ({last_msg.get('user_id', '')}) at {last_msg.get('timestamp', '')}")

    # Notification System
    st.subheader("🔔 Notifications")
    if not df.empty:
        spam_users = df['user_id'].value_counts()[df['user_id'].value_counts() > 10]
        if not spam_users.empty:
            st.warning(f"⚠️ Potential spam detected for users: {', '.join(map(str, spam_users.index))}")
        else:
            st.success("✅ No suspicious activity detected")

    # User Message Timeline
    st.subheader("📈 User Message Timeline")
    if not df.empty:
        user_list = df['username'].dropna().unique().tolist()
        selected_user = st.selectbox("Select User for Timeline", user_list)
        user_df = df[df['username'] == selected_user]
        timeline = user_df.groupby(user_df['timestamp'].dt.date).size().reset_index(name='Messages')
        st.line_chart(timeline.set_index('timestamp'))

    # Intent Heatmap
    st.subheader("🔥 Intent Heatmap")
    if not df.empty and 'intent' in df.columns:
        heatmap_df = df.copy()
        heatmap_df['hour'] = heatmap_df['timestamp'].dt.hour
        heatmap = pd.pivot_table(heatmap_df, index='intent', columns='hour', values='message', aggfunc='count', fill_value=0)
        st.dataframe(heatmap, use_container_width=True)

    # Feedback Form
    st.subheader("💬 Feedback Form")
    with st.form("feedback_form"):
        feedback_text = st.text_area("Your feedback or issue:")
        submitted = st.form_submit_button("Submit Feedback")
        if submitted:
            st.success("Thank you for your feedback!")

    # Mobile Optimization Notice
    st.subheader("📱 Mobile Optimization")
    st.info("This dashboard is optimized for mobile. For best experience, use landscape mode.")

    # Download Logs
    st.subheader("📥 Download Logs")
    log_file = "bot.log"
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
        st.download_button(
            label="Download Log File",
            data=log_content,
            file_name=f"bot_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

    # Data Visualization
    st.subheader("📊 Data Visualization")
    if not df.empty:
        st.bar_chart(df['intent'].value_counts())
        st.area_chart(df.groupby(df['timestamp'].dt.date).size())

def show_analytics_tab(dashboard):
    """Show analytics tab with charts and insights"""
    st.header("📈 Analytics & Insights")
    
    df = dashboard.load_data()
    
    if df.empty:
        st.info("No data available for analytics")
        return
    
    # Time series analysis
    st.subheader("📅 Request Trends")
    
    # Daily requests
    daily_requests = df.groupby(df['timestamp'].dt.date).size().reset_index()
    daily_requests.columns = ['date', 'requests']
    
    fig_daily = px.line(daily_requests, x='date', y='requests', 
                        title="Daily Request Volume",
                        labels={'date': 'Date', 'requests': 'Number of Requests'})
    fig_daily.update_layout(height=400)
    st.plotly_chart(fig_daily, use_container_width=True)
    
    # Intent distribution
    st.subheader("🎯 Intent Distribution")
    
    if 'intent' in df.columns:
        intent_counts = df['intent'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_pie = px.pie(values=intent_counts.values, names=intent_counts.index,
                             title="Intent Distribution")
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            fig_bar = px.bar(x=intent_counts.index, y=intent_counts.values,
                             title="Intent Counts",
                             labels={'x': 'Intent Type', 'y': 'Count'})
            fig_bar.update_layout(height=400)
            st.plotly_chart(fig_bar, use_container_width=True)
    
    # User activity analysis
    st.subheader("👥 User Activity Analysis")
    
    if 'user_id' in df.columns:
        user_activity = df.groupby('user_id').agg({
            'timestamp': 'count',
            'username': 'first',
            'intent': lambda x: x.mode().iloc[0] if not x.empty else 'Unknown'
        }).reset_index()
        user_activity.columns = ['User ID', 'Message Count', 'Username', 'Most Common Intent']
        
        st.dataframe(user_activity.sort_values('Message Count', ascending=False), 
                     use_container_width=True)
    
    # Hourly activity
    st.subheader("⏰ Hourly Activity Pattern")
    
    hourly_activity = df.groupby(df['timestamp'].dt.hour).size().reset_index()
    hourly_activity.columns = ['hour', 'requests']
    
    fig_hourly = px.bar(hourly_activity, x='hour', y='requests',
                        title="Requests by Hour of Day",
                        labels={'hour': 'Hour (24h)', 'requests': 'Number of Requests'})
    fig_hourly.update_layout(height=400)
    st.plotly_chart(fig_hourly, use_container_width=True)

def show_data_management_tab(dashboard):
    """Show data management tab"""
    st.header("💾 Data Management")
    
    # Data overview
    df = dashboard.load_data()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📁 Data Overview")
        if not df.empty:
            excel_file = getattr(Config, 'EXCEL_FILE', 'requests.xlsx') if CONFIG_AVAILABLE else 'requests.xlsx'
            file_size = os.path.getsize(excel_file) if os.path.exists(excel_file) else 0
            st.write(f"**Total Records:** {len(df):,}")
            st.write(f"**File Size:** {file_size / 1024:.2f} KB")
            st.write(f"**Last Updated:** {df['timestamp'].max()}")
            st.write(f"**Date Range:** {df['timestamp'].min().date()} to {df['timestamp'].max().date()}")
        else:
            st.info("No data file found")
    
    with col2:
        st.subheader("🗂️ Backup Management")
        
        # List existing backups
        backup_dir = getattr(Config, 'BACKUP_DIR', 'backups') if CONFIG_AVAILABLE else 'backups'
        backup_path = Path(backup_dir)
        if backup_path.exists():
            backups = list(backup_path.glob("*.xlsx")) + list(backup_path.glob("*.csv"))
            if backups:
                st.write(f"**Available Backups:** {len(backups)}")
                latest_backup = max(backups, key=os.path.getctime)
                st.write(f"**Latest:** {latest_backup.name}")
                st.write(f"**Latest Size:** {latest_backup.stat().st_size / 1024:.2f} KB")
            else:
                st.write("No backups found")
        else:
            st.write("Backup directory not found")
    
    # Data operations
    st.subheader("🔧 Data Operations")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Create Backup", type="primary"):
            try:
                if UTILS_AVAILABLE:
                    backup_path = data_manager.create_backup()
                    if backup_path:
                        st.success(f"✅ Backup created: {backup_path}")
                    else:
                        st.error("❌ Backup failed")
                else:
                    st.error("❌ Data manager not available")
            except Exception as e:
                st.error(f"❌ Backup error: {e}")
    
    with col2:
        if st.button("📥 Download Data", type="secondary"):
            if not df.empty:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"bot_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No data to download")
    
    with col3:
        if st.button("🗑️ Clear Data", type="secondary"):
            st.warning("Warning: This action cannot be undone.")
            if st.checkbox("I understand this will delete all data"):
                try:
                    excel_file = getattr(Config, 'EXCEL_FILE', 'requests.xlsx') if CONFIG_AVAILABLE else 'requests.xlsx'
                    if os.path.exists(excel_file):
                        os.remove(excel_file)
                        st.success("✅ Data cleared successfully")
                        st.rerun()
                    else:
                        st.warning("No data file to clear")
                except Exception as e:
                    st.error(f"❌ Failed to clear data: {e}")
    
    # Data preview
    st.subheader("👀 Data Preview")
    if not df.empty:
        # Add filters
        col1, col2, col3 = st.columns(3)

        with col1:
            selected_intent = st.selectbox("Filter by Intent", ['All'] + list(df['intent'].unique()))

        with col2:
            date_range = st.date_input("Date Range", value=(df['timestamp'].min().date(), df['timestamp'].max().date()))

        with col3:
            user_search = st.text_input("🔍 Search by Username or User ID", "")

        # Apply filters
        filtered_df = df.copy()
        if selected_intent != 'All':
            filtered_df = filtered_df[filtered_df['intent'] == selected_intent]

        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = filtered_df[(filtered_df['timestamp'].dt.date >= start_date) & (filtered_df['timestamp'].dt.date <= end_date)]

        if user_search:
            user_search_lower = user_search.lower()
            filtered_df = filtered_df[
                filtered_df['username'].astype(str).str.lower().str.contains(user_search_lower) |
                filtered_df['user_id'].astype(str).str.contains(user_search)
            ]

        st.write(f"**Showing {len(filtered_df)} of {len(df)} records**")
        st.dataframe(filtered_df, use_container_width=True)

        # Suggestion: Export filtered data
        csv_filtered = filtered_df.to_csv(index=False)
        st.download_button(
            label="📤 Export Filtered Data (CSV)",
            data=csv_filtered,
            file_name=f"filtered_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

        # Suggestion: User profile popup
        st.subheader("👤 User Profile Quick View")
        if user_search and not filtered_df.empty:
            user_row = filtered_df.iloc[0]
            st.info(f"**Username:** {user_row.get('username', 'N/A')}\n**User ID:** {user_row.get('user_id', 'N/A')}\n**Total Messages:** {filtered_df['user_id'].value_counts().get(user_row.get('user_id'), 1)}\n**Most Recent Intent:** {user_row.get('intent', 'N/A')}\n**Last Message:** {user_row.get('message', 'N/A')}")
    else:
        st.info("No data available for preview")

def show_security_tab(dashboard):
    """Show security and monitoring tab"""
    st.header("🛡️ Security & Monitoring")
    
    # Rate limiting status
    st.subheader("⏳ Rate Limiting Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if CONFIG_AVAILABLE:
            st.write("**Rate Limiting Configuration:**")
            st.write(f"• Max per minute: {Config.MAX_REQUESTS_PER_MINUTE}")
            st.write(f"• Max per hour: {Config.MAX_REQUESTS_PER_HOUR}")
        else:
            st.write("**Rate Limiting Configuration:**")
            st.write("• Max per minute: 10 (default)")
            st.write("• Max per hour: 100 (default)")
        
        if UTILS_AVAILABLE and hasattr(rate_limiter, 'requests_per_minute'):
            active_users = len(rate_limiter.requests_per_minute)
            st.write(f"• Active users: {active_users}")
    
    with col2:
        st.write("**Current Status:**")
        status, _ = dashboard.get_bot_status()
        st.write(f"• Bot: {status}")
        
        # Check file permissions
        try:
            excel_file = getattr(Config, 'EXCEL_FILE', 'requests.xlsx') if CONFIG_AVAILABLE else 'requests.xlsx'
            if os.access(excel_file, os.W_OK):
                st.write("• Data file: ✅ Writable")
            else:
                st.write("• Data file: ❌ Not writable")
        except:
            st.write("• Data file: ❓ Unknown")
    
    # Security monitoring
    st.subheader("🔍 Security Monitoring")
    
    # Recent suspicious activity
    df = dashboard.load_data()
    if not df.empty:
        # Check for potential spam (same user, many messages)
        if 'user_id' in df.columns:
            user_message_counts = df.groupby('user_id').size()
            potential_spam = user_message_counts[user_message_counts > 10]
            
            if not potential_spam.empty:
                st.warning("⚠️ Potential spam detected:")
                for user_id, count in potential_spam.items():
                    username = df[df['user_id'] == user_id]['username'].iloc[0] if 'username' in df.columns else 'Unknown'
                    st.write(f"• User {username} ({user_id}): {count} messages")
            else:
                st.success("✅ No suspicious activity detected")
    
    # System health
    st.subheader("🏥 System Health")
    
    health_checks = []
    
    # Check Excel file
    try:
        excel_file = getattr(Config, 'EXCEL_FILE', 'requests.xlsx') if CONFIG_AVAILABLE else 'requests.xlsx'
        if os.path.exists(excel_file):
            health_checks.append(("Data File", "✅ Accessible", "success"))
        else:
            health_checks.append(("Data File", "❌ Not found", "error"))
    except:
        health_checks.append(("Data File", "❓ Unknown", "warning"))
    
    # Check backup directory
    try:
        backup_dir = getattr(Config, 'BACKUP_DIR', 'backups') if CONFIG_AVAILABLE else 'backups'
        if os.path.exists(backup_dir):
            health_checks.append(("Backup Directory", "✅ Accessible", "success"))
        else:
            health_checks.append(("Backup Directory", "❌ Not found", "error"))
    except:
        health_checks.append(("Backup Directory", "❓ Unknown", "warning"))
    
    # Check Groq API
    try:
        if UTILS_AVAILABLE:
            test_response = groq_client.ask("test")
            if test_response:
                health_checks.append(("Groq API", "✅ Connected", "success"))
            else:
                health_checks.append(("Groq API", "⚠️ No response", "warning"))
        else:
            health_checks.append(("Groq API", "❌ Module not available", "error"))
    except:
        health_checks.append(("Groq API", "❌ Connection failed", "error"))
    
    # Display health status
    for check_name, status, color in health_checks:
        if color == "success":
            st.success(f"{check_name}: {status}")
        elif color == "warning":
            st.warning(f"{check_name}: {status}")
        else:
            st.error(f"{check_name}: {status}")

def show_settings_tab(dashboard):
    """Show settings and configuration tab"""
    st.header("⚙️ Settings & Configuration")
    
    # Environment variables
    st.subheader("🔐 Environment Variables")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Bot Configuration:**")
        if CONFIG_AVAILABLE:
            bot_token = Config.BOT_TOKEN or "Not set"
            bot_token_display = bot_token[:10] + "..." if len(bot_token) > 10 else bot_token
            st.write(f"• BOT_TOKEN: {bot_token_display}")
            
            groq_key = Config.GROQ_API_KEY or "Not set"
            groq_key_display = groq_key[:10] + "..." if len(groq_key) > 10 else groq_key
            st.write(f"• GROQ_API_KEY: {groq_key_display}")
        else:
            st.write("• BOT_TOKEN: Config module not available")
            st.write("• GROQ_API_KEY: Config module not available")
    
    with col2:
        st.write("**System Configuration:**")
        if CONFIG_AVAILABLE:
            st.write(f"• Excel File: {Config.EXCEL_FILE}")
            st.write(f"• Backup Directory: {Config.BACKUP_DIR}")
            st.write(f"• Log Level: {Config.LOG_LEVEL}")
        else:
            st.write("• Excel File: requests.xlsx (default)")
            st.write("• Backup Directory: backups (default)")
            st.write("• Log Level: INFO (default)")
    
    # Rate limiting settings
    st.subheader("⏳ Rate Limiting Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Current Settings:**")
        if CONFIG_AVAILABLE:
            st.write(f"• Max per minute: {Config.MAX_REQUESTS_PER_MINUTE}")
            st.write(f"• Max per hour: {Config.MAX_REQUESTS_PER_HOUR}")
            st.write(f"• Request timeout: {Config.REQUEST_TIMEOUT}s")
        else:
            st.write("• Max per minute: 10 (default)")
            st.write("• Max per hour: 100 (default)")
            st.write("• Request timeout: 30s (default)")
    
    with col2:
        st.write("**Groq Settings:**")
        if CONFIG_AVAILABLE:
            st.write(f"• Model: {Config.GROQ_MODEL}")
            st.write(f"• Temperature: {Config.GROQ_TEMPERATURE}")
        else:
            st.write("• Model: llama3-8b-8192 (default)")
            st.write("• Temperature: 0.7 (default)")
    
    # Admin configuration
    st.subheader("👑 Admin Configuration")
    
    # Show current admin IDs
    try:
        if BOT_AVAILABLE:
            bot_instance = TelegramBot()
            st.write(f"**Current Admin IDs:** {bot_instance.admin_ids}")
            st.info("💡 To change admin IDs, edit the admin_ids list in bot_upgraded.py")
        else:
            st.write("**Current Admin IDs:** Bot module not available")
    except Exception as e:
        st.error(f"❌ Could not load admin configuration: {e}")
    
    # Configuration actions
    st.subheader("🔧 Configuration Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Reload Configuration", type="primary"):
            try:
                if CONFIG_AVAILABLE:
                    Config.load_env()
                    st.success("✅ Configuration reloaded successfully!")
                    st.rerun()
                else:
                    st.error("❌ Config module not available")
            except Exception as e:
                st.error(f"❌ Failed to reload configuration: {e}")
    
    with col2:
        if st.button("📁 Open Config Directory", type="secondary"):
            config_path = Path(__file__).parent
            st.write(f"Configuration files are in: {config_path}")
            st.write("Files:")
            for file in config_path.glob("*.py"):
                st.write(f"• {file.name}")

def show_logs_tab(dashboard):
    """Show logs and debugging tab"""
    st.header("📝 Logs & Debugging")
    
    # Log file viewer
    st.subheader("📄 Log File Viewer")
    
    log_file = "bot.log"
    if os.path.exists(log_file):
        # Log file controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Refresh Logs", type="primary"):
                st.rerun()
        
        with col2:
            if st.button("📥 Download Logs", type="secondary"):
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                st.download_button(
                    label="📥 Download Log File",
                    data=log_content,
                    file_name=f"bot_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
        
        with col3:
            if st.button("🗑️ Clear Logs", type="secondary"):
                try:
                    with open(log_file, 'w', encoding='utf-8') as f:
                        f.write("")
                    st.success("✅ Logs cleared successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to clear logs: {e}")
        
        # Display logs
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            if log_content.strip():
                # Filter logs
                log_filter = st.text_input("🔍 Filter logs (leave empty for all):")
                
                if log_filter:
                    filtered_lines = [line for line in log_content.split('\n') 
                                     if log_filter.lower() in line.lower()]
                    filtered_content = '\n'.join(filtered_lines)
                else:
                    filtered_content = log_content
                
                # Show last N lines
                lines_to_show = st.slider("📊 Show last N lines:", 100, 1000, 500)
                lines = filtered_content.split('\n')
                recent_lines = lines[-lines_to_show:] if len(lines) > lines_to_show else lines
                
                st.text_area("Log Content:", '\n'.join(recent_lines), 
                             height=400, disabled=True)
                
                st.write(f"Showing {len(recent_lines)} of {len(lines)} total lines")
            else:
                st.info("Log file is empty")
                
        except Exception as e:
            st.error(f"❌ Error reading log file: {e}")
    else:
        st.warning("⚠️ Log file not found")
    
    # Real-time monitoring
    st.subheader("📡 Real-time Monitoring")
    
    if st.button("🔄 Check Current Status", type="primary"):
        try:
            # Check bot status
            status, _ = dashboard.get_bot_status()
            st.write(f"**Bot Status:** {status}")
            
            # Check data file
            excel_file = getattr(Config, 'EXCEL_FILE', 'requests.xlsx') if CONFIG_AVAILABLE else 'requests.xlsx'
            if os.path.exists(excel_file):
                file_size = os.path.getsize(excel_file)
                st.write(f"**Data File Size:** {file_size / 1024:.2f} KB")
            else:
                st.write("**Data File:** Not found")
            
            # Check backup directory
            backup_dir = getattr(Config, 'BACKUP_DIR', 'backups') if CONFIG_AVAILABLE else 'backups'
            backup_path = Path(backup_dir)
            if backup_path.exists():
                backup_count = len(list(backup_path.glob("*.xlsx")) + list(backup_path.glob("*.csv")))
                st.write(f"**Backup Count:** {backup_count}")
            else:
                st.write("**Backup Directory:** Not found")
                
        except Exception as e:
            st.error(f"❌ Status check failed: {e}")

if __name__ == "__main__":
    main()