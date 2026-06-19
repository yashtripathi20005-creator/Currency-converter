import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the currency converter"""
    
    # API Configuration
    API_KEY = os.getenv('EXCHANGE_RATE_API_KEY', '')
    BASE_URL = "https://v6.exchangerate-api.com/v6/"
    BASE_CURRENCY = os.getenv('BASE_CURRENCY', 'USD')
    
    # File paths
    CACHE_FILE = 'exchange_rates_cache.json'
    
    # Cache duration in seconds (24 hours)
    CACHE_DURATION = 86400
    
    @classmethod
    def get_api_url(cls, endpoint='latest'):
        """Get the full API URL"""
        if not cls.API_KEY:
            raise ValueError("API Key is required. Please set EXCHANGE_RATE_API_KEY in .env file")
        return f"{cls.BASE_URL}{cls.API_KEY}/{endpoint}"
    
    @classmethod
    def validate_currency_code(cls, currency_code):
        """Validate currency code format (3 uppercase letters)"""
        return len(currency_code) == 3 and currency_code.isalpha() and currency_code.isupper()
