import pytest
import requests
import weather_api

@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before each test to ensure isolation."""
    weather_api._cache['current'].clear()
    weather_api._cache['forecast'].clear()

class DummyResponse:
    """A dummy response object to simulate requests.Response."""
    def __init__(self, data, status_code=200):
        self._data = data
        self.status_code = status_code

    def raise_for_status(self):
        if not (200 <= self.status_code < 300):
            raise requests.HTTPError(f"Status code: {self.status_code}")

    def json(self):
        return self._data

# Tests for fetch_current_weather

def test_fetch_current_weather_success(mocker):
    """Test fetch_current_weather returns correct dict on valid response."""
    data = {
        'name': 'TestCity',
        'main': {'temp': 20, 'humidity': 45},
        'weather': [{'description': 'sunny'}],
        'wind': {'speed': 3.1}
    }
    mocker.patch('weather_api.requests.get', return_value=DummyResponse(data))
    result = weather_api.fetch_current_weather('TestCity')
    assert result == {
        'city': 'TestCity',
        'temp': 20,
        'condition': 'sunny',
        'humidity': 45,
        'wind_speed': 3.1
    }


def test_fetch_current_weather_http_error(mocker):
    """Test fetch_current_weather raises CityNotFoundError on 404."""
    mock_resp = DummyResponse({}, status_code=404)
    mocker.patch('weather_api.requests.get', return_value=mock_resp)
    with pytest.raises(weather_api.CityNotFoundError):
        weather_api.fetch_current_weather('NoCity')


def test_fetch_current_weather_exception(mocker):
    """Test fetch_current_weather raises WeatherAPIError on network exception."""
    mocker.patch('weather_api.requests.get', side_effect=Exception("Network"))
    with pytest.raises(weather_api.WeatherAPIError):
        weather_api.fetch_current_weather('ErrorCity')


def test_fetch_current_weather_caching(mocker):
    """Test that fetch_current_weather uses cache for repeated calls."""
    call_count = {'count': 0}
    data = {
        'name': 'CacheCity',
        'main': {'temp': 10, 'humidity': 60},
        'weather': [{'description': 'rain'}],
        'wind': {'speed': 2.0}
    }
    def fake_get(*args, **kwargs):
        call_count['count'] += 1
        return DummyResponse(data)
    mocker.patch('weather_api.requests.get', side_effect=fake_get)
    res1 = weather_api.fetch_current_weather('CacheCity')
    res2 = weather_api.fetch_current_weather('CacheCity')
    assert call_count['count'] == 1
    assert res1 == res2


def test_fetch_current_weather_cache_expiry(mocker):
    """Test that cache expires after CACHE_TTL seconds."""
    data = {
        'name': 'ExpireCity',
        'main': {'temp': 5, 'humidity': 70},
        'weather': [{'description': 'fog'}],
        'wind': {'speed': 1.5}
    }
    call_count = {'count': 0}
    def fake_get(*args, **kwargs):
        call_count['count'] += 1
        return DummyResponse(data)
    mocker.patch('weather_api.requests.get', side_effect=fake_get)
    # Simulate time progression: initial, within TTL, after TTL
    base_time = 1000
    times = [base_time, base_time, base_time + weather_api.CACHE_TTL + 1]
    mocker.patch('weather_api.time.time', side_effect=lambda: times.pop(0))
    res1 = weather_api.fetch_current_weather('ExpireCity')
    res2 = weather_api.fetch_current_weather('ExpireCity')
    res3 = weather_api.fetch_current_weather('ExpireCity')
    assert call_count['count'] == 2
    assert res1 == res2 == res3

# Tests for fetch_forecast

def test_fetch_forecast_success(mocker):
    """Test fetch_forecast returns correct dict on valid response."""
    data = {
        'city': {'name': 'TestCity'},
        'list': [
            {'dt_txt': '2025-01-01 00:00:00', 'main': {'temp': 1}, 'weather': [{'description': 'snow'}]},
            {'dt_txt': '2025-01-01 03:00:00', 'main': {'temp': 2}, 'weather': [{'description': 'cloudy'}]},
        ]
    }
    mocker.patch('weather_api.requests.get', return_value=DummyResponse(data))
    result = weather_api.fetch_forecast('TestCity')
    assert result['city'] == 'TestCity'
    assert isinstance(result['forecasts'], list)
    assert result['forecasts'][0] == {
        'datetime': '2025-01-01 00:00:00',
        'temp': 1,
        'condition': 'snow'
    }


def test_fetch_forecast_http_error(mocker):
    """Test fetch_forecast raises WeatherAPIError on HTTP error status."""
    mock_resp = DummyResponse({}, status_code=500)
    mocker.patch('weather_api.requests.get', return_value=mock_resp)
    with pytest.raises(weather_api.WeatherAPIError):
        weather_api.fetch_forecast('BadCity')


def test_fetch_forecast_exception(mocker):
    """Test fetch_forecast raises WeatherAPIError on exception."""
    mocker.patch('weather_api.requests.get', side_effect=Exception("API Down"))
    with pytest.raises(weather_api.WeatherAPIError):
        weather_api.fetch_forecast('ErrorCity')


def test_fetch_forecast_caching(mocker):
    """Test that fetch_forecast uses cache for repeated calls."""
    call_count = {'count': 0}
    data = {
        'city': {'name': 'CacheCity'},
        'list': [
            {'dt_txt': '2025-01-01 00:00:00', 'main': {'temp': 3}, 'weather': [{'description': 'sunny'}]}
        ]
    }
    def fake_get(*args, **kwargs):
        call_count['count'] += 1
        return DummyResponse(data)
    mocker.patch('weather_api.requests.get', side_effect=fake_get)
    res1 = weather_api.fetch_forecast('CacheCity')
    res2 = weather_api.fetch_forecast('CacheCity')
    assert call_count['count'] == 1
    assert res1 == res2


def test_fetch_forecast_cache_expiry(mocker):
    """Test that forecast cache expires after CACHE_TTL seconds."""
    data = {
        'city': {'name': 'ExpireCity'},
        'list': [
            {'dt_txt': '2025-01-01 06:00:00', 'main': {'temp': 4}, 'weather': [{'description': 'windy'}]}
        ]
    }
    call_count = {'count': 0}
    def fake_get(*args, **kwargs):
        call_count['count'] += 1
        return DummyResponse(data)
    mocker.patch('weather_api.requests.get', side_effect=fake_get)
    base_time = 2000
    times = [base_time, base_time, base_time + weather_api.CACHE_TTL + 1]
    mocker.patch('weather_api.time.time', side_effect=lambda: times.pop(0))
    res1 = weather_api.fetch_forecast('ExpireCity')
    res2 = weather_api.fetch_forecast('ExpireCity')
    res3 = weather_api.fetch_forecast('ExpireCity')
    assert call_count['count'] == 2
    assert res1 == res2 == res3
