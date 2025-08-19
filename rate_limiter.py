# -*- coding: utf-8 -*-
"""
Lightweight rate limiter with dict-based tracking
"""
import time
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple rate limiter using dictionaries"""
    
    def __init__(self, max_per_minute=10, max_per_hour=100):
        self.max_per_minute = max_per_minute
        self.max_per_hour = max_per_hour
        self.requests_per_minute = defaultdict(list)
        self.requests_per_hour = defaultdict(list)
        self._cleanup_old_entries()
    
    def _cleanup_old_entries(self):
        """Clean up old timestamp entries"""
        current_time = time.time()
        
        # Clean minute entries (older than 60 seconds)
        for user_id in list(self.requests_per_minute.keys()):
            self.requests_per_minute[user_id] = [
                ts for ts in self.requests_per_minute[user_id] 
                if current_time - ts < 60
            ]
            if not self.requests_per_minute[user_id]:
                del self.requests_per_minute[user_id]
        
        # Clean hour entries (older than 3600 seconds)
        for user_id in list(self.requests_per_hour.keys()):
            self.requests_per_hour[user_id] = [
                ts for ts in self.requests_per_hour[user_id] 
                if current_time - ts < 3600
            ]
            if not self.requests_per_hour[user_id]:
                del self.requests_per_hour[user_id]
    
    def is_allowed(self, user_id):
        """Check if user is allowed to make a request"""
        try:
            current_time = time.time()
            
            # Clean up old entries periodically
            if current_time % 10 < 1:  # Every ~10 seconds
                self._cleanup_old_entries()
            
            # Check minute limit
            minute_requests = self.requests_per_minute[user_id]
            minute_requests = [ts for ts in minute_requests if current_time - ts < 60]
            
            if len(minute_requests) >= self.max_per_minute:
                logger.warning(f"Rate limit exceeded for user {user_id}: {len(minute_requests)} requests in last minute")
                return False
            
            # Check hour limit
            hour_requests = self.requests_per_hour[user_id]
            hour_requests = [ts for ts in hour_requests if current_time - ts < 3600]
            
            if len(hour_requests) >= self.max_per_hour:
                logger.warning(f"Rate limit exceeded for user {user_id}: {len(hour_requests)} requests in last hour")
                return False
            
            # Add current request
            self.requests_per_minute[user_id].append(current_time)
            self.requests_per_hour[user_id].append(current_time)
            
            return True
            
        except Exception as e:
            logger.error(f"Error in rate limiter: {e}")
            # Allow request if rate limiter fails
            return True
    
    def get_user_stats(self, user_id):
        """Get rate limiting stats for a user"""
        try:
            current_time = time.time()
            
            minute_requests = len([
                ts for ts in self.requests_per_minute.get(user_id, [])
                if current_time - ts < 60
            ])
            
            hour_requests = len([
                ts for ts in self.requests_per_hour.get(user_id, [])
                if current_time - ts < 3600
            ])
            
            return {
                'minute_requests': minute_requests,
                'hour_requests': hour_requests,
                'minute_limit': self.max_per_minute,
                'hour_limit': self.max_per_hour
            }
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {
                'minute_requests': 0,
                'hour_requests': 0,
                'minute_limit': self.max_per_minute,
                'hour_limit': self.max_per_hour
            }

# Global instance
rate_limiter = RateLimiter()
