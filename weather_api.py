"""
Weather API interaction module for OpenWeatherMap.

- Requires an OpenWeatherMap API key (https://openweathermap.org/api)
- Provides functions to fetch current weather and 5-day forecast by city name
- Caches results to minimize API calls
"""
import requests
from typing import Optional, Dict, Any
import time
from requests.exceptions import HTTPError, RequestException

API_KEY = "YOUR_API_KEY"  # <-- Replace with your OpenWeatherMap API key
BASE_URL_CURRENT = "https://api.openweathermap.org/data/2.5/weather"
BASE_URL_FORECAST = "https://api.openweathermap.org/data/2.5/forecast"
CACHE_TTL = 600  # seconds

# In-memory cache: { (endpoint, city): (timestamp, data) }
_cache: Dict[str, Dict[str, Any]] = {
    'current': {},
    'forecast': {}
}

class WeatherAPIError(Exception):
    """Base exception for weather API errors."""

class CityNotFoundError(WeatherAPIError):
    """Raised when the specified city is not found by the API."""

def _cache_get(endpoint: str, city: str) -> Optional[Dict[str, Any]]:
    entry = _cache[endpoint].get(city.lower())
    if entry and (time.time() - entry['timestamp'] < CACHE_TTL):
        return entry['data']
    return None

def _cache_set(endpoint: str, city: str, data: Dict[str, Any]) -> None:
    _cache[endpoint][city.lower()] = {'timestamp': time.time(), 'data': data}

def fetch_current_weather(city: str) -> Optional[Dict[str, Any]]:
    """
    Fetch current weather for a given city using OpenWeatherMap.
    Returns a dict with temperature (C), weather condition, etc., or raises an exception on error.
    Caches results for CACHE_TTL seconds.
    """
    cached = _cache_get('current', city)
    if cached:
        return cached
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric',
    }
    try:
        resp = requests.get(BASE_URL_CURRENT, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        result = {
            'city': data['name'],
            'temp': data['main']['temp'],
            'condition': data['weather'][0]['description'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'],
        }
        _cache_set('current', city, result)
        return result
    except HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            raise CityNotFoundError(f"City '{city}' not found") from e
        raise WeatherAPIError(f"HTTP error fetching current weather for '{city}': {e}") from e
    except RequestException as e:
        raise WeatherAPIError(f"Request error fetching current weather for '{city}': {e}") from e
    except Exception as e:
        raise WeatherAPIError(f"Unexpected error processing current weather for '{city}': {e}") from e

def fetch_forecast(city: str) -> Optional[Dict[str, Any]]:
    """
    Fetch 5-day weather forecast for a given city using OpenWeatherMap.
    Returns a dict with a list of forecasts or raises an exception on error.
    Caches results for CACHE_TTL seconds.
    """
    cached = _cache_get('forecast', city)
    if cached:
        return cached
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric',
    }
    try:
        resp = requests.get(BASE_URL_FORECAST, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        forecasts = []
        for item in data['list']:
            forecasts.append({
                'datetime': item['dt_txt'],
                'temp': item['main']['temp'],
                'condition': item['weather'][0]['description'],
            })
        result = {
            'city': data['city']['name'],
            'forecasts': forecasts
        }
        _cache_set('forecast', city, result)
        return result
    except HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            raise CityNotFoundError(f"City '{city}' not found") from e
        raise WeatherAPIError(f"HTTP error fetching forecast for '{city}': {e}") from e
    except RequestException as e:
        raise WeatherAPIError(f"Request error fetching forecast for '{city}': {e}") from e
    except Exception as e:
        raise WeatherAPIError(f"Unexpected error processing forecast data for '{city}': {e}") from e
