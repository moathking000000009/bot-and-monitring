# Telegram Bot Dashboard - جمعية حفظ النعمة  

A professional-grade Telegram bot dashboard with comprehensive features including AI-powered responses, rate limiting, data management, and a Streamlit-based interface.  

---

## Features  

### Core Bot Features  
- **AI-Powered Responses**: Uses Groq API for intelligent conversation handling.  
- **Rate Limiting & Spam Protection**: Built-in protection against abuse.  
- **Automatic Data Backups**: Excel/CSV-based data storage with automatic backups.  
- **Comprehensive Error Handling**: Robust error handling and logging.  
- **Statistics & Monitoring**: Built-in analytics and health monitoring.  
- **Admin Commands**: Restricted commands for administrators.  

### Dashboard Features  
- **Theme Switcher**: Choose between Default, Light, Dark, and Purple themes.  
- **Overview**: Real-time metrics, recent activity, and bot status.  
- **Analytics**: Interactive charts, user message timeline, and intent heatmap.  
- **Data Management**: Search/filter by user, backup creation, data export, and management.  
- **Security**: Rate limiting status, threat detection, and notification system.  
- **Settings**: Configuration management and environment variables.  
- **Logs**: Real-time log monitoring, download logs, and debugging.  
- **Feedback Form**: Submit feedback or report issues directly from the dashboard.  
- **Mobile Optimization**: Responsive layout for mobile devices.  
- **Real-Time Bot Status**: Live status and last message info.  
- **Enhanced Data Visualization**: Bar/area charts for intents and activity.  

---

## Quick Start (Clean Machine)  

### 1. Install Dependencies  
```bash
pip install -r requirements.txt
2. Run the Dashboard
bash
نسخ
تحرير
# Option 1: Direct Streamlit command
streamlit run streamlit_dashboard.py

# Option 2: Use the helper script
python run_dashboard.py

# Option 3: Manual Streamlit command
python -m streamlit run streamlit_dashboard.py --server.port 8501
The dashboard will be available at:
http://localhost:8501

Project Structure
bash
نسخ
تحرير
chatbot/
├── streamlit_dashboard.py    # Main dashboard application
├── config.py                 # Configuration with sane defaults
├── utils/                    # Utility modules
│   ├── __init__.py
│   ├── data_manager.py       # Excel/CSV data handling
│   ├── rate_limiter.py       # Rate limiting logic
│   └── groq_client.py        # Dummy Groq client
├── bot_upgraded.py           # Minimal bot stub
├── requirements.txt          # Essential dependencies
├── run_dashboard.py          # Dashboard launcher
├── env.example               # Environment template
├── .gitignore                # Git ignore rules
└── README.md                 # Documentation
Configuration
Environment Variables (Optional)
Create a .env file for custom configuration:

env
نسخ
تحرير
# Bot configuration
BOT_TOKEN=your_telegram_bot_token_here
GROQ_API_KEY=your_groq_api_key_here

# File paths
EXCEL_FILE=requests.xlsx
BACKUP_DIR=backups

# Rate limiting
MAX_REQUESTS_PER_MINUTE=10
MAX_REQUESTS_PER_HOUR=100

# Logging
LOG_LEVEL=INFO
Default Values
If no .env file is provided, the system uses these defaults:

Data File: requests.xlsx

Backup Directory: backups/

Rate Limits: 10/minute, 100/hour

Log Level: INFO

Dashboard Usage
Starting the Dashboard
The dashboard runs fully standalone and will:

Auto-create necessary directories and files.

Fall back to CSV if Excel engine is unavailable.

Handle missing modules gracefully with fallbacks.

Show import status for troubleshooting.

Dashboard Tabs
Overview: Key metrics and recent activity.

Analytics: Charts and user behavior analysis.

Data Management: Backup and data operations.

Security: Rate limiting and threat monitoring.

Settings: Configuration management.

Logs: Real-time log viewing.

Troubleshooting
Common Issues
Dashboard Won’t Start

bash
نسخ
تحرير
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Streamlit installation
streamlit --version
Import Errors

The dashboard handles missing modules gracefully.

Check the import status warning at the top.

All functionality will work with fallbacks.

Excel/CSV Issues

Dashboard automatically falls back to CSV if Excel fails.

Ensure openpyxl is installed:

bash
نسخ
تحرير
pip install openpyxl
Check file permissions in the project directory.

Port Already in Use

bash
نسخ
تحرير
# Use different port
streamlit run streamlit_dashboard.py --server.port 8502
Data File Issues
Missing file: Dashboard creates empty structure automatically.

Permission errors: Check write permissions in project directory.

Corrupted files: Use backup feature or clear data option.

Data Management
Automatic Features
File creation on first run.

Automatic timestamped backups.

Format fallback: Excel → CSV.

Graceful error recovery.

Manual Operations
Create Backup: Click backup button in Data Management tab.

Export Data: Download as CSV from Data Management tab.

Clear Data: Available with confirmation checkbox.

Security Features
Rate Limiting: Built-in protection against abuse.

File Permissions: Automatic permission checking.

Data Validation: Input sanitization and validation.

Error Logging: Comprehensive error tracking.

Mobile Support
The dashboard is fully responsive and works on:

Desktop computers

Tablets

Mobile phones

All modern browsers

Production Deployment
Systemd Service (Linux)
bash
نسخ
تحرير
# Create service file
sudo nano /etc/systemd/system/telegram-dashboard.service

[Unit]
Description=Telegram Bot Dashboard
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/chatbot
ExecStart=/usr/bin/python -m streamlit run streamlit_dashboard.py --server.port 8501
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start service
sudo systemctl enable telegram-dashboard
sudo systemctl start telegram-dashboard
Docker Deployment
dockerfile
نسخ
تحرير
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_dashboard.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
Dependencies
Core Dependencies
streamlit==1.28.1 – Web dashboard framework.

pandas==2.1.4 – Data processing and analysis.

plotly==5.17.0 – Interactive charts and visualizations.

Data Support
openpyxl==3.1.2 – Excel file handling (with CSV fallback).

Utilities
python-dotenv==1.0.0 – Environment variable management.

python-dateutil==2.8.2 – Date/time utilities.

Support
Getting Help
Check the dashboard status – Import warnings show what’s missing.

Review error messages – Clear error descriptions with solutions.

Check file permissions – Ensure write access to project directory.

Verify dependencies – Run pip list to check installed packages.

Common Solutions
Missing modules:

bash
نسخ
تحرير
pip install -r requirements.txt
Permission errors: Ensure correct directory write permissions.

Port conflicts: Use a different port (--server.port 8502).

Data issues: Use backup/restore features.

License
This project is open source and available under the MIT License.

Quick Commands Summary
bash
نسخ
تحرير
# 1. Install everything
pip install -r requirements.txt

# 2. Run dashboard
streamlit run streamlit_dashboard.py

# 3. Access at
http://localhost:8501
