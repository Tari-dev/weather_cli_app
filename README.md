# Weather CLI App

A simple command-line weather application in Python.

## Features
- Fetches current weather and forecast by city name
- Uses a free API (OpenWeatherMap, no registration required)
- Simple CLI interface

## Setup

1. **Create a virtualenv with pyenv:**

   ```sh
   pyenv virtualenv 3.9.13 weather-cli-env
   pyenv activate weather-cli-env
   ```

2. **Install dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

3. **Run the app:**

   ```sh
   python main.py
   ```

## Notes
- The app uses the [OpenWeatherMap](https://openweathermap.org/api) API (no key needed for basic usage).
- If you want to use another API, update `weather_api.py` and add your API key if required.
