#!/usr/bin/env python
"""
Main module for Weather CLI Application.

Sets up configuration and environment variables, then runs the CLI.
"""
import os
import sys
import logging
import weather_api
from cli import main as cli_run
from pathlib import Path
from dotenv import load_dotenv

# Configure logging and environment
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

# Load .env file if present
env_path = Path('.') / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=str(env_path))
    logging.info("Loaded environment variables from .env")

# Load API key from environment
api_key = os.getenv('OPENWEATHER_API_KEY')
if not api_key:
    logging.error("Environment variable OPENWEATHER_API_KEY not set. Please export it and try again.")
    sys.exit(1)
# Assign to weather_api module
weather_api.API_KEY = api_key
logging.info("OPENWEATHER_API_KEY loaded successfully.")

if __name__ == "__main__":
    cli_run()