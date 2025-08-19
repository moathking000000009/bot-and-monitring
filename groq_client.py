# -*- coding: utf-8 -*-
"""
Real Groq client with fallback to dummy client
"""
import logging
import os

logger = logging.getLogger(__name__)

class GroqClient:
    """Groq client with real API support and fallback"""
    
    def __init__(self, api_key=None, model="llama3-8b-8192"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model
        self.request_count = 0
        self._real_client = None
        
        # Try to initialize real client
        self._init_real_client()
        
        if not self._real_client:
            logger.warning("Using dummy Groq client - no real API key provided or client failed to initialize")
    
    def _init_real_client(self):
        """Initialize real Groq client if possible"""
        try:
            if self.api_key and self.api_key != "your_groq_api_key_here":
                import groq
                self._real_client = groq.Groq(api_key=self.api_key)
                logger.info("✅ Real Groq client initialized successfully")
            else:
                logger.info("No valid Groq API key provided")
        except ImportError:
            logger.warning("Groq library not installed - using dummy client")
        except Exception as e:
            logger.warning(f"Failed to initialize real Groq client: {e} - using dummy client")
    
    def ask(self, text):
        """Process a text request using real API or fallback"""
        try:
            self.request_count += 1
            
            # Try real API first
            if self._real_client:
                try:
                    response = self._real_client.chat.completions.create(
                        messages=[
                            {
                                "role": "system",
                                "content": """أنت مساعد افتراضي رسمي لجمعية حفظ النعمة بمنطقة حائل. 
                                دورك خدمة المتبرعين والمستفيدين والمتطوعين. 
                                أجب بالعربية المختصرة والمهذبة. 
                                صنّف الرسائل إلى: DONATION_FOOD / BENEFICIARY_REQUEST / VOLUNTEER_SIGNUP / OTHER."""
                            },
                            {
                                "role": "user",
                                "content": text
                            }
                        ],
                        model=self.model,
                        temperature=0.7,
                        max_tokens=500
                    )
                    
                    reply = response.choices[0].message.content
                    logger.info(f"Real Groq response #{self.request_count}: {reply[:50]}...")
                    return reply
                    
                except Exception as e:
                    logger.warning(f"Real Groq API failed: {e} - falling back to dummy client")
            
            # Fallback to dummy responses
            logger.info(f"Dummy Groq request #{self.request_count}: {text[:50]}...")
            
            # Generate mock response based on input
            if "تبرع" in text or "طعام" in text:
                response = "🍱 شكرًا لتبرعك بالطعام! فضلاً زوّدنا: الموقع بالتفصيل، نوع وكميّة الطعام، الوقت المناسب للاستلام، رقم التواصل."
            elif "مساعدة" in text or "سلة غذائية" in text:
                response = "🤝 حياك الله، لطلب المساعدة: الاسم الثلاثي، الحي/الموقع، عدد أفراد الأسرة، الحالة/الدخل التقريبي، رقم التواصل."
            elif "تطوع" in text or "متطوع" in text:
                response = "🙌 ممتنين لرغبتك بالتطوع: الاسم، العمر، المهارات/التخصص، الأوقات المناسبة، رقم التواصل."
            else:
                response = "👋 مرحبًا بك! وضّح طلبك باختصار وسنسعد بخدمتك. للتواصل المباشر: 0551965445"
            
            logger.info(f"Dummy response: {response[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"Error in Groq client: {e}")
            return "⚠️ حدث خطأ في معالجة طلبك. حاول مرة أخرى أو تواصل على 0551965445"
    
    def get_stats(self):
        """Get client statistics"""
        return {
            'request_count': self.request_count,
            'model': self.model,
            'api_key_configured': bool(self.api_key and self.api_key != "your_groq_api_key_here"),
            'real_client_available': bool(self._real_client)
        }

# Global instance
groq_client = GroqClient()
