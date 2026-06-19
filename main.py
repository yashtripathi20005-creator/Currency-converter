#!/usr/bin/env python3
"""
Currency Converter - Main Application
A simple command-line currency converter using Exchange Rate API
"""

import sys
from currency_converter import CurrencyConverter
from config import Config

def display_welcome():
    """Display welcome message and instructions"""
    print("\n" + "="*60)
    print("         🌍 CURRENCY CONVERTER 🌍")
    print("="*60)
    print("Available commands:")
    print("  convert <amount> <from> <to>  - Convert currency")
    print("  list                        - List supported currencies")
    print("  info <currency>             - Get currency information")
    print("  update                      - Refresh exchange rates")
    print("  setbase <currency>          - Change base currency")
    print("  quit/exit                   - Exit the program")
    print("="*60 + "\n")

def display_currencies(converter):
    """Display list of supported currencies"""
    currencies = converter.get_supported_currencies()
    if not currencies:
        print("❌ No currency data available")
        return
    
    print("\n📊 Supported Currencies:")
    print("-" * 30)
    # Display in columns
    for i in range(0, len(currencies), 5):
        row = currencies[i:i+5]
        print("  ".join(f"{curr:<6}" for curr in row))
    print(f"\nTotal: {len(currencies)} currencies\n")

def display_currency_info(converter, currency_code):
    """Display information about a specific currency"""
    currency_code = currency_code.upper()
    if not Config.validate_currency_code(currency_code):
        print(f"❌ Invalid currency code: {currency_code}")
        return
    
    info = converter.get_currency_info(currency_code)
    print(f"\n📋 Currency Information:")
    print(f"  Code: {currency_code}")
    print(f"  Name: {info.get('name', 'Unknown')}")
    print(f"  Symbol: {info.get('symbol', 'N/A')}")
    
    # Get current rate against base currency
    try:
        rate = converter.get_rate(converter.base_currency, currency_code)
        print(f"  Rate (1 {converter.base_currency}): {rate:.4f} {currency_code}")
    except:
        print("  Rate: Not available")
    print()

def handle_convert(converter, args):
    """Handle currency conversion command"""
    if len(args) < 3:
        print("❌ Usage: convert <amount> <from_currency> <to_currency>")
        print("   Example: convert 100 USD EUR")
        return
    
    try:
        amount = float(args[0])
        from_currency = args[1].upper()
        to_currency = args[2].upper()
        
        if amount < 0:
            print("❌ Amount must be positive")
            return
        
        # Validate currency codes
        if not Config.validate_currency_code(from_currency):
            print(f"❌ Invalid currency code: {from_currency}")
            return
        if not Config.validate_currency_code(to_currency):
            print(f"❌ Invalid currency code: {to_currency}")
            return
        
        # Perform conversion
        result = converter.convert(amount, from_currency, to_currency)
        rate = converter.get_rate(from_currency, to_currency)
        
        print("\n💱 Conversion Result:")
        print(f"  {converter.format_amount(amount, from_currency)} = {converter.format_amount(result, to_currency)}")
        print(f"  Exchange Rate: 1 {from_currency} = {rate:.4f} {to_currency}")
        print(f"  Rate Source: {'Cache' if converter.last_updated else 'API'}")
        if converter.last_updated:
            print(f"  Last Updated: {converter.last_updated.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
    except ValueError:
        print("❌ Invalid amount. Please enter a valid number.")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main program loop"""
    # Initialize converter
    converter = CurrencyConverter()
    
    # Fetch initial rates
    print("🔄 Initializing currency converter...")
    if not converter.fetch_rates():
        print("❌ Failed to fetch exchange rates. Please check your API key and internet connection.")
        print("   Get a free API key at: https://exchangerate-api.com")
        sys.exit(1)
    
    display_welcome()
    
    # Command loop
    while True:
        try:
            command = input("💰 Enter command: ").strip()
            
            if not command:
                continue
            
            parts = command.split()
            cmd = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            
            if cmd in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            elif cmd == 'convert':
                handle_convert(converter, args)
            
            elif cmd == 'list':
                display_currencies(converter)
            
            elif cmd == 'info':
                if len(args) != 1:
                    print("❌ Usage: info <currency_code>")
                    print("   Example: info USD")
                else:
                    display_currency_info(converter, args[0])
            
            elif cmd == 'update':
                print("🔄 Fetching latest exchange rates...")
                if converter.fetch_rates():
                    print("✅ Rates updated successfully!")
                else:
                    print("❌ Failed to update rates. Using cached rates if available.")
            
            elif cmd == 'setbase':
                if len(args) != 1:
                    print("❌ Usage: setbase <currency_code>")
                    print("   Example: setbase EUR")
                else:
                    base = args[0].upper()
                    if not Config.validate_currency_code(base):
                        print(f"❌ Invalid currency code: {base}")
                    else:
                        print(f"🔄 Changing base currency to {base}...")
                        if converter.fetch_rates(base):
                            print(f"✅ Base currency changed to {base}")
                        else:
                            print(f"❌ Failed to change base currency to {base}")
            
            elif cmd == 'help':
                display_welcome()
            
            else:
                print(f"❌ Unknown command: {cmd}")
                print("   Type 'help' for available commands")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
