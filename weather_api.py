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

def fetch_current_weather(city: str) -> Optional[Dict[str, Any]]:
    """
    Fetch current weather for a given city using OpenWeatherMap.
    Returns a dict with temperature (C), weather condition, etc., or raises an exception on error.
    Caches results for CACHE_TTL seconds.
    """
    # Check cache
    key = city.lower()
    now = time.time()
    entry = _cache['current'].get(key)
    if entry and (now - entry['timestamp'] < CACHE_TTL):
        return entry['data']
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric',
    }
    try:
        resp = requests.get(BASE_URL_CURRENT, params=params, timeout=5)
        if resp.status_code == 404:
            raise CityNotFoundError(f"City '{city}' not found")
        resp.raise_for_status()
        data = resp.json()
        result = {
            'city': data['name'],
            'temp': data['main']['temp'],
            'condition': data['weather'][0]['description'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'],
        }
        # Cache result
        _cache['current'][key] = {'timestamp': now, 'data': result}
        return result
    except CityNotFoundError:
        # Propagate city not found separately
        raise
    except HTTPError as e:
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
    # Check cache
    key = city.lower()
    now = time.time()
    entry = _cache['forecast'].get(key)
    if entry and (now - entry['timestamp'] < CACHE_TTL):
        return entry['data']
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric',
    }
    try:
        resp = requests.get(BASE_URL_FORECAST, params=params, timeout=5)
        if resp.status_code == 404:
            raise CityNotFoundError(f"City '{city}' not found")
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
        # Cache result
        _cache['forecast'][key] = {'timestamp': now, 'data': result}
        return result
    except CityNotFoundError:
        # Propagate missing city
        raise
    except HTTPError as e:
        raise WeatherAPIError(f"HTTP error fetching forecast for '{city}': {e}") from e
    except RequestException as e:
        raise WeatherAPIError(f"Request error fetching forecast for '{city}': {e}") from e
    except Exception as e:
        raise WeatherAPIError(f"Unexpected error processing forecast data for '{city}': {e}") from e
