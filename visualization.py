"""
Visualization module for Weather CLI Application.

Provides functions to create and save charts:
- plot_temperature_forecast
- plot_condition_frequency
"""
from typing import Dict, Any
from datetime import datetime
import matplotlib.pyplot as plt

def plot_temperature_forecast(forecast: Dict[str, Any], output_path: str) -> str:
    """
    Plot temperature forecast over time and save to file.

    Args:
        forecast: Dict returned by fetch_forecast with keys 'city' and 'forecasts'.
        output_path: File path (including extension) to save the plot.

    Returns:
        The output_path where the chart was saved.
    """
    dates = [
        datetime.strptime(item['datetime'], '%Y-%m-%d %H:%M:%S')
        for item in forecast.get('forecasts', [])
    ]
    temps = [item['temp'] for item in forecast.get('forecasts', [])]

    plt.figure(figsize=(10, 5))
    plt.plot(dates, temps, marker='o', linestyle='-')
    plt.title(f"Temperature Forecast for {forecast.get('city', '')}")
    plt.xlabel("Date and Time")
    plt.ylabel("Temperature (°C)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    return output_path

def plot_condition_frequency(forecast: Dict[str, Any], output_path: str) -> str:
    """
    Create a bar chart of weather condition frequencies and save to file.

    Args:
        forecast: Dict returned by fetch_forecast with keys 'city' and 'forecasts'.
        output_path: File path (including extension) to save the bar chart.

    Returns:
        The output_path where the chart was saved.
    """
    conditions = [item['condition'] for item in forecast.get('forecasts', [])]
    freq: Dict[str, int] = {}
    for cond in conditions:
        freq[cond] = freq.get(cond, 0) + 1

    labels = list(freq.keys())
    counts = list(freq.values())

    plt.figure(figsize=(10, 5))
    plt.bar(labels, counts, color='skyblue')
    plt.title(f"Weather Condition Frequency for {forecast.get('city', '')}")
    plt.xlabel("Condition")
    plt.ylabel("Frequency")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    return output_path
