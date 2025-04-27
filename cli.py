"""
Weather CLI commands and entry point.
"""
from weather_service import get_current_weather, get_forecast
from typing import Optional, Dict, Any

def print_help() -> None:
    print("""
Weather CLI Commands:
  weather <city>     Show current weather for <city>
  forecast <city>    Show 5-day forecast for <city>
  help               Show this help message
  quit / exit / q    Quit the application
    """)

def display_current_weather(city: str, weather: Optional[Dict[str, Any]]) -> None:
    if not weather:
        print(f"Could not fetch weather for '{city}'. Please check the city name or try again later.")
        return
    print(f"\nCurrent weather in {weather['city']}:")
    print(f"  Temperature: {weather['temp']}°C")
    print(f"  Condition: {weather['condition'].title()}")
    print(f"  Humidity: {weather['humidity']}%")
    print(f"  Wind Speed: {weather['wind_speed']} m/s")

def display_forecast(city: str, forecast: Optional[Dict[str, Any]]) -> None:
    if not forecast or not forecast.get('forecasts'):
        print(f"Could not fetch forecast for '{city}'. Please check the city name or try again later.")
        return
    print(f"\n5-Day Forecast for {forecast['city']}:")
    for item in forecast['forecasts'][:10]:  # Show next 10 time slots (~2 days)
        print(f"  {item['datetime']}: {item['temp']}°C, {item['condition'].title()}")

def main():
    print("Welcome to the Weather CLI App! Type 'help' for commands.")
    while True:
        user_input = input("weather> ").strip()
        if not user_input:
            continue
        parts = user_input.split(maxsplit=1)
        command = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ''
        if command in ('quit', 'exit', 'q'):
            print("Goodbye!")
            break
        elif command == 'help':
            print_help()
        elif command == 'weather':
            if not arg:
                print("Usage: weather <city>")
                continue
            weather = get_current_weather(arg)
            display_current_weather(arg, weather)
        elif command == 'forecast':
            if not arg:
                print("Usage: forecast <city>")
                continue
            forecast = get_forecast(arg)
            display_forecast(arg, forecast)
        else:
            print(f"Unknown command: {command}. Type 'help' for available commands.")

