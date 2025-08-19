# -*- coding: utf-8 -*-
"""
Utility functions for the Telegram Bot
"""
import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict
import pandas as pd
import aiofiles
from groq import Groq
from config import Config

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter for user requests"""
    
    def __init__(self):
        self.requests_per_minute: Dict[int, List[datetime]] = defaultdict(list)
        self.requests_per_hour: Dict[int, List[datetime]] = defaultdict(list)
    
    def is_allowed(self, user_id: int) -> bool:
        """Check if user is allowed to make a request"""
        now = datetime.now()
        
        # Clean old requests
        self._clean_old_requests(user_id, now)
        
        # Check minute limit
        if len(self.requests_per_minute[user_id]) >= Config.MAX_REQUESTS_PER_MINUTE:
            return False
        
        # Check hour limit
        if len(self.requests_per_hour[user_id]) >= Config.MAX_REQUESTS_PER_HOUR:
            return False
        
        # Add current request
        self.requests_per_minute[user_id].append(now)
        self.requests_per_hour[user_id].append(now)
        
        return True
    
    def _clean_old_requests(self, user_id: int, now: datetime) -> None:
        """Remove old requests from tracking"""
        # Remove requests older than 1 minute
        minute_ago = now - timedelta(minutes=1)
        self.requests_per_minute[user_id] = [
            req for req in self.requests_per_minute[user_id] 
            if req > minute_ago
        ]
        
        # Remove requests older than 1 hour
        hour_ago = now - timedelta(hours=1)
        self.requests_per_hour[user_id] = [
            req for req in self.requests_per_hour[user_id] 
            if req > hour_ago
        ]

class DataManager:
    """Manages data storage and backup operations"""
    
    def __init__(self):
        self.excel_file = Config.EXCEL_FILE
        self.backup_dir = Config.BACKUP_DIR
    
    def save_to_excel(self, row: Dict[str, Any]) -> bool:
        """Save data to Excel file"""
        try:
            if os.path.exists(self.excel_file):
                df = pd.read_excel(self.excel_file, engine="openpyxl")
                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
            else:
                df = pd.DataFrame([row])
            
            df.to_excel(self.excel_file, index=False, engine="openpyxl")
            logger.info("✅ Data saved to Excel")
            return True
        except Exception as e:
            logger.error("❌ Excel save error: %s", e)
            return False
    
    def create_backup(self) -> Optional[str]:
        """Create a backup of the Excel file"""
        try:
            if not os.path.exists(self.excel_file):
                logger.warning("No Excel file to backup")
                return None
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_{timestamp}.xlsx"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Copy file
            import shutil
            shutil.copy2(self.excel_file, backup_path)
            logger.info("✅ Backup created: %s", backup_path)
            return backup_path
        except Exception as e:
            logger.error("❌ Backup creation failed: %s", e)
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics from the Excel file"""
        try:
            if not os.path.exists(self.excel_file):
                return {"total_requests": 0, "intents": {}}
            
            df = pd.read_excel(self.excel_file, engine="openpyxl")
            stats = {
                "total_requests": len(df),
                "intents": df.get("intent", pd.Series()).value_counts().to_dict(),
                "today_requests": len(df[pd.to_datetime(df["timestamp"]).dt.date == datetime.now().date()])
            }
            return stats
        except Exception as e:
            logger.error("❌ Statistics error: %s", e)
            return {"total_requests": 0, "intents": {}, "error": str(e)}

class GroqClient:
    """Wrapper for Groq API client"""
    
    def __init__(self):
        self.client = Groq(api_key=Config.GROQ_API_KEY)
    
    def ask(self, user_message: str) -> str:
        """Send a message to Groq and get response"""
        try:
            response = self.client.chat.completions.create(
                model=Config.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": Config.SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=Config.GROQ_TEMPERATURE,
            )
            reply = response.choices[0].message.content
            logger.info("✅ Groq reply OK")
            return reply
        except Exception as e:
            logger.error("❌ Groq Error: %s", e)
            return "⚠️ عذرًا، حدث خطأ أثناء الاتصال بالنموذج."

def detect_intent(text: str) -> str:
    """Detect the intent of a message"""
    t = (text or "").strip().lower()
    
    # Food donation keywords
    if any(k in t for k in ["تبرع", "طعام", "أكل", "وجبات", "وليمة", "فائض"]):
        return "DONATION_FOOD"
    
    # Beneficiary request keywords
    if any(k in t for k in ["سلة", "مساعدة", "معونة", "احتاج", "محتاجة", "فقراء"]):
        return "BENEFICIARY_REQUEST"
    
    # Volunteer signup keywords
    if any(k in t for k in ["تطوع", "متطوع", "تطوّع", "ساعد"]):
        return "VOLUNTEER_SIGNUP"
    
    return "OTHER"

def mask_sensitive_data(value: Optional[str], head: int = 6, tail: int = 4) -> str:
    """Mask sensitive data for logging"""
    if not value:
        return "None"
    return value[:head] + "…" + value[-tail:] if len(value) > head + tail else value

def setup_logging() -> None:
    """Setup logging configuration"""
    logging.basicConfig(
        format=Config.LOG_FORMAT,
        level=getattr(logging, Config.LOG_LEVEL.upper()),
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("bot.log", encoding="utf-8")
        ]
    )

# Global instances
rate_limiter = RateLimiter()
data_manager = DataManager()
groq_client = GroqClient()
