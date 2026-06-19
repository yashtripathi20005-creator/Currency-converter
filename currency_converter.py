import json
import time
import requests
from datetime import datetime, timedelta
from config import Config

class CurrencyConverter:
    """Main class for currency conversion operations"""
    
    def __init__(self):
        self.api_key = Config.API_KEY
        self.base_url = Config.BASE_URL
        self.base_currency = Config.BASE_CURRENCY
        self.cache_file = Config.CACHE_FILE
        self.cache_duration = Config.CACHE_DURATION
        self.rates = {}
        self.last_updated = None
        
        # Load cached rates if available
        self._load_cache()
    
    def _load_cache(self):
        """Load exchange rates from cache file if valid"""
        try:
            with open(self.cache_file, 'r') as f:
                cache = json.load(f)
                
            # Check if cache is still valid
            cache_time = datetime.fromisoformat(cache['timestamp'])
            if datetime.now() - cache_time < timedelta(seconds=self.cache_duration):
                self.rates = cache['rates']
                self.last_updated = cache_time
                print(f"✅ Loaded rates from cache (updated: {self.last_updated})")
                return True
            else:
                print("⏰ Cache expired, fetching fresh rates...")
                return False
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            print("📡 No valid cache found, fetching rates from API...")
            return False
    
    def _save_cache(self):
        """Save current exchange rates to cache file"""
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'rates': self.rates
        }
        with open(self.cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
        print(f"💾 Rates cached successfully")
    
    def fetch_rates(self, base_currency=None):
        """Fetch latest exchange rates from API"""
        if base_currency:
            self.base_currency = base_currency
        
        if not Config.validate_currency_code(self.base_currency):
            raise ValueError(f"Invalid currency code: {self.base_currency}")
        
        try:
            url = Config.get_api_url(f'latest/{self.base_currency}')
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('result') == 'success':
                self.rates = data['conversion_rates']
                self.last_updated = datetime.now()
                self._save_cache()
                print(f"✅ Rates fetched successfully for {self.base_currency}")
                return True
            else:
                error_msg = data.get('error-type', 'Unknown error')
                raise Exception(f"API Error: {error_msg}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            if self.rates:
                print("⚠️ Using cached rates as fallback")
                return True
            return False
        except Exception as e:
            print(f"❌ Error fetching rates: {e}")
            if self.rates:
                print("⚠️ Using cached rates as fallback")
                return True
            return False
    
    def get_rate(self, from_currency, to_currency):
        """Get exchange rate between two currencies"""
        if not self.rates:
            raise Exception("No exchange rates available. Please fetch rates first.")
        
        if not Config.validate_currency_code(from_currency):
            raise ValueError(f"Invalid currency code: {from_currency}")
        
        if not Config.validate_currency_code(to_currency):
            raise ValueError(f"Invalid currency code: {to_currency}")
        
        # If base currency is the same as from_currency, direct conversion
        if from_currency == self.base_currency:
            if to_currency not in self.rates:
                raise ValueError(f"Currency {to_currency} not found in rates")
            return self.rates[to_currency]
        
        # If to_currency is the base currency, inverse conversion
        if to_currency == self.base_currency:
            if from_currency not in self.rates:
                raise ValueError(f"Currency {from_currency} not found in rates")
            return 1 / self.rates[from_currency]
        
        # Cross-currency conversion
        if from_currency not in self.rates:
            raise ValueError(f"Currency {from_currency} not found in rates")
        if to_currency not in self.rates:
            raise ValueError(f"Currency {to_currency} not found in rates")
        
        # Convert from_currency to base, then to to_currency
        return self.rates[to_currency] / self.rates[from_currency]
    
    def convert(self, amount, from_currency, to_currency):
        """Convert amount from one currency to another"""
        try:
            rate = self.get_rate(from_currency, to_currency)
            converted_amount = amount * rate
            return round(converted_amount, 2)
        except Exception as e:
            raise Exception(f"Conversion failed: {e}")
    
    def get_supported_currencies(self):
        """Get list of supported currency codes"""
        if not self.rates:
            return []
        return sorted(self.rates.keys())
    
    def get_currency_info(self, currency_code):
        """Get additional information about a currency"""
        currency_info = {
            'USD': {'name': 'US Dollar', 'symbol': '$'},
            'EUR': {'name': 'Euro', 'symbol': '€'},
            'GBP': {'name': 'British Pound', 'symbol': '£'},
            'JPY': {'name': 'Japanese Yen', 'symbol': '¥'},
            'INR': {'name': 'Indian Rupee', 'symbol': '₹'},
            'CNY': {'name': 'Chinese Yuan', 'symbol': '¥'},
            'CAD': {'name': 'Canadian Dollar', 'symbol': 'C$'},
            'AUD': {'name': 'Australian Dollar', 'symbol': 'A$'},
            'CHF': {'name': 'Swiss Franc', 'symbol': 'Fr'},
            'NZD': {'name': 'New Zealand Dollar', 'symbol': 'NZ$'},
            # Add more currencies as needed
        }
        return currency_info.get(currency_code, {'name': currency_code, 'symbol': ''})
    
    def format_amount(self, amount, currency_code):
        """Format amount with currency symbol"""
        info = self.get_currency_info(currency_code)
        symbol = info.get('symbol', '')
        if symbol:
            return f"{symbol}{amount:,.2f}"
        return f"{amount:,.2f} {currency_code}"
