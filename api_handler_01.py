import os
import requests
import sqlite3
import json
import datetime
from dotenv import load_dotenv
from requests.exceptions import HTTPError, Timeout, RequestException
import logging

logging.basicConfig(
    filename="application.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

class APIHandler:
    def __init__(self):
        load_dotenv()
        
        # Load environment variables
        self.api_key = os.getenv("API_KEY")
        self.api_host = os.getenv("API_HOST")
        self.season = os.getenv("SEASON")
        self.db_config = {
            "name": os.getenv("DB_NAME"),
            "username": os.getenv("DB_USERNAME"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT"),
        }

        # Validate environment variables
        if not all([self.api_key, self.api_host, self.season]):
            logging.error("Environment variables for API are missing.")
            raise EnvironmentError("Incorrectly configured environment")

        if not all(self.db_config.values()):
            logging.error("Environment variables for database are missing.")
            raise EnvironmentError("Incorrectly configured database environment")

        # Initialize SQLite cache
        self.cache_conn = sqlite3.connect('api_cache.db', check_same_thread=False)
        self._init_cache_table()
        logging.info("APIHandler initialized successfully.")

    def __del__(self):
        # Close the SQLite connection when the instance is destroyed
        if self.cache_conn:
            self.cache_conn.close()
            logging.info("SQLite connection closed.")

    def _init_cache_table(self):
        cursor = self.cache_conn.cursor()
        try:
            # Drop the table if it exists
            cursor.execute('DROP TABLE IF EXISTS api_cache')
            cursor.execute(''' 
                CREATE TABLE IF NOT EXISTS api_cache (
                    league_id INTEGER,
                    season INTEGER,
                    timestamp DATETIME,
                    response_data TEXT,
                    PRIMARY KEY (league_id, season)
                )
            ''')
            self.cache_conn.commit()
            logging.info("Cache table initialized successfully.")
        except sqlite3.Error as e:
            logging.error(f"Failed to initialize cache table: {e}")

    def get_api_response(self, league_id):
        # Check cache first
        cached_data = self._get_cached_response(league_id)
        if cached_data is not None:
            logging.info(f"Using cached data for league_id {league_id}.")
            return self.db_config, cached_data
        else:
            logging.info(f"No cached data found for league_id {league_id}. Proceeding with API call.")

        # Proceed with API call if no valid cache
        url = "https://v3.football.api-sports.io/standings"
        headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': self.api_host,
        }
        query_string = {"season": self.season, "league": league_id}

        try:
            logging.info(f"Fetching data for league_id {league_id}...")
            response = requests.get(url, headers=headers, params=query_string, timeout=10)
            response.raise_for_status()
            response_data = response.json()['response']
            logging.info(f"Data fetched successfully for league_id {league_id}.")
            
            # Cache the response
            self._cache_response(league_id, response_data)
            logging.info(f"Response data cached for league_id {league_id}.")
            return self.db_config, response_data

        except (HTTPError, Timeout, RequestException, Exception) as e:
            logging.error(f"Error occurred for league_id {league_id}: {e}")
            self._log_error(f"Error: {e}")
            return self.db_config, None

    def _get_cached_response(self, league_id):
        ttl_hours = 6  # Configurable TTL (6 hours)
        ttl = datetime.timedelta(hours=ttl_hours)
        current_time = datetime.datetime.now()

        cursor = self.cache_conn.cursor()
        cursor.execute('''
            SELECT response_data, timestamp 
            FROM api_cache 
            WHERE league_id = ? AND season = ?
        ''', (league_id, self.season))
        row = cursor.fetchone()

        if not row:
            return None

        response_data_str, timestamp_str = row
        timestamp = datetime.datetime.fromisoformat(timestamp_str)

        if (current_time - timestamp) > ttl:
            return None

        try:
            return json.loads(response_data_str)
        except json.JSONDecodeError:
            logging.error("Failed to decode cached data for league_id {league_id}")
            return None

    def _cache_response(self, league_id, response_data):
        try:
            response_data_str = json.dumps(response_data)
            current_time = datetime.datetime.now().isoformat()
            cursor = self.cache_conn.cursor()
            cursor.execute(''' 
                INSERT OR REPLACE INTO api_cache 
                (league_id, season, timestamp, response_data)
                VALUES (?, ?, ?, ?)
            ''', (league_id, self.season, current_time, response_data_str))
            self.cache_conn.commit()
            logging.info(f"Successfully cached response for league_id {league_id}.")
        except Exception as e:
            logging.error(f"Failed to cache response for league_id {league_id}: {e}")

    @staticmethod
    def _log_error(message):
        with open("error_log.txt", "a") as log_file:
            log_file.write(message + "\n")
        logging.error(message)