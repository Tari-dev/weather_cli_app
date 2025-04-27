"""
Weather service interface module.
Wraps weather_api and provides get_current_weather and get_forecast functions.
"""
from typing import Optional, Dict, Any
from weather_api import fetch_current_weather, fetch_forecast

def get_current_weather(city: str) -> Optional[Dict[str, Any]]:
    """
    Returns current weather for the given city, or None on error.
    """
    return fetch_current_weather(city)

def get_forecast(city: str) -> Optional[Dict[str, Any]]:
    """
    Returns 5-day forecast for the given city, or None on error.
    """
    return fetch_forecast(city)
