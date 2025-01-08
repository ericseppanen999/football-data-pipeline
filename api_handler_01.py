import os
import requests
from dotenv import load_dotenv
from requests.exceptions import HTTPError, Timeout, RequestException
import logging

# Configure logging
logging.basicConfig(
    filename="application.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

class APIHandler:

    def __init__(self):
        load_dotenv()
        
        # load environment variables
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

        # check if all environment variables are set
        if not all([self.api_key, self.api_host, self.season]):
            logging.error("Environment variables for API are missing.")
            raise EnvironmentError("incorrectly configured environment")


        if not all(self.db_config.values()):
            logging.error("Environment variables for database are missing.")
            raise EnvironmentError("incorrectly configured database environment")

        logging.info("APIHandler initialized successfully.")

    
    def get_api_response(self,league_id):
        # define the url, headers and query string
        url = "https://v3.football.api-sports.io/standings"
        headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': self.api_host,
        }
        query_string = {
            "season": self.season,
            "league": league_id,
        }

        # make the request
        try:
            logging.info(f"Fetching data for league_id {league_id}...")
            response = requests.get(url, headers=headers, params=query_string, timeout=10)
            response.raise_for_status()
            logging.info(f"Data fetched successfully for league_id {league_id}.")
            return self.db_config, response.json()['response']
        
        except HTTPError as e:
            logging.error(f"HTTP error occurred for league_id {league_id}: {e}")
            self._log_error(f"http error occurred: {e}")

        except Timeout as e:
            logging.error(f"Timeout error occurred for league_id {league_id}: {e}")
            self._log_error(f"timeout error occurred: {e}")

        except RequestException as e:
            logging.error(f"Request error occurred for league_id {league_id}: {e}")
            self._log_error(f"request error occurred: {e}")

        except Exception as e:
            logging.error(f"Unexpected error occurred for league_id {league_id}: {e}")
            self._log_error(f"unexpected error occurred: {e}")

        return self.db_config, None


    # log error messages to a file
    @staticmethod
    def _log_error(message):
        with open("error_log.txt", "a") as log_file:
            log_file.write(message + "\n")
        logging.error(message)
