# -*- coding: utf-8 -*-
"""
Data manager for handling Excel/CSV data with fallbacks
"""
import os
import pandas as pd
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DataManager:
    """Data manager with Excel/CSV fallback support"""
    
    def __init__(self, excel_file="requests.xlsx", backup_dir="backups"):
        self.excel_file = excel_file
        self.backup_dir = backup_dir
        self.csv_file = excel_file.replace('.xlsx', '.csv')
        self._ensure_directories()
        self._ensure_data_file()
    
    def _ensure_directories(self):
        """Ensure backup directory exists"""
        Path(self.backup_dir).mkdir(exist_ok=True)
    
    def _ensure_data_file(self):
        """Ensure data file exists with proper structure"""
        if not os.path.exists(self.excel_file) and not os.path.exists(self.csv_file):
            # Create empty data file
            empty_df = pd.DataFrame(columns=[
                'timestamp', 'user_id', 'username', 'first_name', 
                'last_name', 'intent', 'message', 'reply'
            ])
            self._save_data(empty_df)
    
    def _save_data(self, df):
        """Save data with Excel/CSV fallback"""
        try:
            # Try Excel first
            df.to_excel(self.excel_file, index=False, engine='openpyxl')
            logger.info(f"Data saved to Excel: {self.excel_file}")
        except ImportError:
            # Fallback to CSV if openpyxl not available
            df.to_csv(self.csv_file, index=False)
            logger.info(f"Data saved to CSV: {self.csv_file}")
        except Exception as e:
            # Final fallback to CSV
            logger.warning(f"Excel save failed, using CSV: {e}")
            df.to_csv(self.csv_file, index=False)
    
    def _load_data(self):
        """Load data with Excel/CSV fallback"""
        try:
            if os.path.exists(self.excel_file):
                return pd.read_excel(self.excel_file, engine='openpyxl')
            elif os.path.exists(self.csv_file):
                return pd.read_csv(self.csv_file)
            else:
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return pd.DataFrame()
    
    def save_to_excel(self, row_data):
        """Save a single row of data"""
        try:
            df = self._load_data()
            new_row = pd.DataFrame([row_data])
            df = pd.concat([df, new_row], ignore_index=True)
            self._save_data(df)
            return True
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            return False
    
    def get_statistics(self):
        """Get basic statistics from data"""
        try:
            df = self._load_data()
            
            if df.empty:
                return {
                    'total_requests': 0,
                    'today_requests': 0,
                    'intents': {}
                }
            
            # Convert timestamp to datetime if it's not already
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                
                # Filter out invalid timestamps
                df = df.dropna(subset=['timestamp'])
                
                # Get today's requests
                today = datetime.now().date()
                today_requests = len(df[df['timestamp'].dt.date == today])
            else:
                today_requests = 0
            
            # Get intent distribution
            intents = {}
            if 'intent' in df.columns:
                intent_counts = df['intent'].value_counts()
                intents = intent_counts.to_dict()
            
            return {
                'total_requests': len(df),
                'today_requests': today_requests,
                'intents': intents
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {
                'total_requests': 0,
                'today_requests': 0,
                'intents': {}
            }
    
    def create_backup(self):
        """Create a backup of the data file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Determine source file
            if os.path.exists(self.excel_file):
                source_file = self.excel_file
                backup_name = f"backup_{timestamp}.xlsx"
            elif os.path.exists(self.csv_file):
                source_file = self.csv_file
                backup_name = f"backup_{timestamp}.csv"
            else:
                logger.warning("No data file found to backup")
                return None
            
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            # Copy file
            import shutil
            shutil.copy2(source_file, backup_path)
            
            logger.info(f"Backup created: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None

# Global instance
data_manager = DataManager()
