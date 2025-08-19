# 🤖 Telegram Bot Dashboard - جمعية حفظ النعمة

A professional-grade Telegram bot dashboard with comprehensive features including AI-powered responses, rate limiting, data management, and a beautiful Streamlit interface.

## 🌟 **Features**

### **Core Bot Features**
- **AI-Powered Responses**: Uses Groq API for intelligent conversation handling
- **Rate Limiting & Spam Protection**: Built-in protection against abuse
- **Automatic Data Backups**: Excel/CSV-based data storage with automatic backups
- **Comprehensive Error Handling**: Robust error handling and logging
- **Statistics & Monitoring**: Built-in analytics and health monitoring
- **Admin Commands**: Restricted commands for administrators

### **Dashboard Features**
- **🌈 Theme Switcher**: Choose between Default, Light, Dark, and Purple themes
- **📊 Overview**: Real-time metrics, recent activity, and bot status
- **📈 Analytics**: Interactive charts, user message timeline, and intent heatmap
- **💾 Data Management**: Search/filter by user, backup creation, data export, and management
- **🛡️ Security**: Rate limiting status, threat detection, and notification system
- **⚙️ Settings**: Configuration management and environment variables
- **📝 Logs**: Real-time log monitoring, download logs, and debugging
- **💬 Feedback Form**: Submit feedback or report issues directly from the dashboard
- **📱 Mobile Optimization**: Responsive layout for mobile devices
- **📡 Real-Time Bot Status**: Live status and last message info
- **📤 Enhanced Data Visualization**: Bar/area charts for intents and activity

## 🚀 **Quick Start (Clean Machine)**

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Run the Dashboard**
```bash
# Option 1: Direct Streamlit command
streamlit run streamlit_dashboard.py

# Option 2: Use the helper script
python run_dashboard.py

# Option 3: Manual Streamlit command
python -m streamlit run streamlit_dashboard.py --server.port 8501
```

The dashboard will open at `http://localhost:8501`

## 📁 **Project Structure**

```
chatbot/
├── 🤖 streamlit_dashboard.py    # Main dashboard application (27KB)
├── ⚙️ config.py                 # Configuration with sane defaults (3KB)
├── 🛠️ utils/                    # Utility modules
│   ├── __init__.py              # Package initialization
│   ├── data_manager.py          # Excel/CSV data handling (6KB)
│   ├── rate_limiter.py          # Rate limiting logic (4KB)
│   └── groq_client.py           # Dummy Groq client (2KB)
├── 🤖 bot_upgraded.py           # Minimal bot stub (3KB)
├── 📚 requirements.txt           # Essential dependencies (343B)
├── 🚀 run_dashboard.py          # Dashboard launcher (1KB)
├── 🔐 env.example               # Environment template (684B)
├── 🚫 .gitignore                # Git ignore rules (452B)
└── 📖 README.md                 # This documentation (7KB)
```

## ⚙️ **Configuration**

### **Environment Variables (Optional)**
Create a `.env` file for custom configuration:
```env
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
```

### **Default Values**
If no `.env` file is provided, the system uses these defaults:
- **Data File**: `requests.xlsx`
- **Backup Directory**: `backups/`
- **Rate Limits**: 10/minute, 100/hour
- **Log Level**: INFO

## 🎛️ **Dashboard Usage**

### **Starting the Dashboard**
The dashboard runs completely standalone and will:
1. **Auto-create** necessary directories and files
2. **Fall back** to CSV if Excel engine is unavailable
3. **Handle missing modules** gracefully with fallbacks
4. **Show import status** for troubleshooting

### **Dashboard Tabs**
1. **📊 Overview**: Key metrics and recent activity
2. **📈 Analytics**: Charts and user behavior analysis
3. **💾 Data Management**: Backup and data operations
4. **🛡️ Security**: Rate limiting and threat monitoring
5. **⚙️ Settings**: Configuration management
6. **📝 Logs**: Real-time log viewing

## 🔧 **Troubleshooting**

### **Common Issues**

1. **Dashboard Won't Start**
   ```bash
   # Check Python version
   python --version  # Should be 3.8+
   
   # Reinstall dependencies
   pip install -r requirements.txt --force-reinstall
   
   # Check Streamlit installation
   streamlit --version
   ```

2. **Import Errors**
   - The dashboard handles missing modules gracefully
   - Check the import status warning at the top
   - All functionality will work with fallbacks

3. **Excel/CSV Issues**
   - Dashboard automatically falls back to CSV if Excel fails
   - Ensure `openpyxl` is installed: `pip install openpyxl`
   - Check file permissions in the project directory

4. **Port Already in Use**
   ```bash
   # Use different port
   streamlit run streamlit_dashboard.py --server.port 8502
   ```

### **Data File Issues**
- **Missing data file**: Dashboard creates empty structure automatically
- **Permission errors**: Check write permissions in project directory
- **Corrupted files**: Use backup feature or clear data option

## 📊 **Data Management**

### **Automatic Features**
- **File Creation**: Empty data structure created on first run
- **Backup System**: Automatic timestamped backups
- **Format Fallback**: Excel → CSV if needed
- **Error Recovery**: Graceful handling of file issues

### **Manual Operations**
- **Create Backup**: Click backup button in Data Management tab
- **Export Data**: Download as CSV from Data Management tab
- **Clear Data**: Option available with confirmation checkbox

## 🛡️ **Security Features**

- **Rate Limiting**: Built-in protection against abuse
- **File Permissions**: Automatic permission checking
- **Data Validation**: Input sanitization and validation
- **Error Logging**: Comprehensive error tracking

## 📱 **Mobile Support**

The dashboard is fully responsive and works on:
- ✅ Desktop computers
- ✅ Tablets
- ✅ Mobile phones
- ✅ All modern browsers

## 🚀 **Production Deployment**

### **Systemd Service (Linux)**
```bash
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
```

### **Docker Deployment**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_dashboard.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
```

## 📚 **Dependencies**

### **Core Dependencies**
- `streamlit==1.28.1` - Web dashboard framework
- `pandas==2.1.4` - Data processing and analysis
- `plotly==5.17.0` - Interactive charts and visualizations

### **Data Support**
- `openpyxl==3.1.2` - Excel file handling (with CSV fallback)

### **Utilities**
- `python-dotenv==1.0.0` - Environment variable management
- `python-dateutil==2.8.2` - Date/time utilities

## 🤝 **Support**

### **Getting Help**
1. **Check the dashboard status** - Import warnings show what's missing
2. **Review error messages** - Clear error descriptions with solutions
3. **Check file permissions** - Ensure write access to project directory
4. **Verify dependencies** - Run `pip list` to check installed packages

### **Common Solutions**
- **Missing modules**: Install with `pip install -r requirements.txt`
- **Permission errors**: Check directory write permissions
- **Port conflicts**: Use different port with `--server.port 8502`
- **Data issues**: Use backup/restore features in dashboard

## 📄 **License**

This project is open source and available under the MIT License.

---

## 🎯 **Quick Commands Summary**

```bash
# 1. Install everything
pip install -r requirements.txt

# 2. Run dashboard
streamlit run streamlit_dashboard.py

# 3. Access at
# http://localhost:8501
```

**Your Telegram Bot Dashboard is now ready to run on any clean machine!** 🎉

The dashboard includes comprehensive error handling, automatic fallbacks, and graceful degradation when modules are missing. Start with the quick commands above and explore all the features through the intuitive web interface.

