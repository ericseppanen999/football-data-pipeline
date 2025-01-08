import subprocess
import logging


logging.basicConfig(
    filename="orchestrator.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def run_database_handler():
    try:
        logging.info("Starting database handler...")
        subprocess.run(["python", "database_handler_02.py"], check=True)
        logging.info("Database handler completed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error while running database handler: {e}")
        raise

def run_streamlit_app():
    try:
        logging.info("Starting Streamlit app...")
        subprocess.run(["streamlit", "run", "app.py"], check=True)
        logging.info("Streamlit app launched successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error while launching Streamlit app: {e}")
        raise

if __name__ == "__main__":
    try:
        run_database_handler()
        
        run_streamlit_app()
    except Exception as e:
        logging.error(f"An error occurred in the orchestrator: {e}")
