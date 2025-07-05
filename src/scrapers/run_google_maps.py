import subprocess
import os
import logging
import sys
import time
import psutil
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add project root to the Python path to allow imports from src
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(PROJECT_ROOT)

# Now we can import from src.config
from src.config import ACTIVE_CATEGORIES, ACTIVE_LOCATIONS

# --- Configuration ---
SCRAPER_VENDOR_DIR = os.path.join(PROJECT_ROOT, 'vendor', 'google-maps-scrapper')
VENV_PYTHON = os.path.join(SCRAPER_VENDOR_DIR, '.venv', 'bin', 'python')
SCRAPER_MAIN_SCRIPT = os.path.join(SCRAPER_VENDOR_DIR, 'main.py')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'data', 'raw', 'google_maps')
TOTAL_RESULTS_PER_QUERY = 200  # Number of results to scrape per query

def generate_search_queries():
    """
    Generates a list of search queries based on the active configuration.
    """
    queries = []
    # Using the active category and location lists from config.py
    for category in ACTIVE_CATEGORIES:
        for location in ACTIVE_LOCATIONS:
            # Format: "categoría en ubicación, Chile"
            queries.append(f'"{category}" en {location}, Chile')
    
    logging.info(f"Generated {len(queries)} search queries based on the active strategic configuration.")
    return queries

def get_memory_usage():
    """Returns the current memory usage of the process in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024) # in MB

def run_google_maps_scraper(queries, chunk_size=50, pause_between_chunks=10):
    """
    Runs the Google Maps scraper in chunks to manage resources.

    Args:
        queries (list): A list of search strings.
        chunk_size (int): The number of queries to process in each batch.
        pause_between_chunks (int): The number of seconds to pause between chunks.
    """
    if not os.path.exists(VENV_PYTHON):
        logging.error(f"Scraper virtual environment not found at {VENV_PYTHON}")
        logging.error("Please run the setup steps.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    logging.info(f"Output will be saved to: {OUTPUT_DIR}")
    output_csv_path = os.path.join(OUTPUT_DIR, 'google_maps_results.csv')

    total_queries = len(queries)
    num_chunks = (total_queries + chunk_size - 1) // chunk_size

    for i in range(num_chunks):
        start_index = i * chunk_size
        end_index = start_index + chunk_size
        chunk = queries[start_index:end_index]

        logging.info(f"--- Processing Chunk {i + 1}/{num_chunks} ({len(chunk)} queries) ---")
        logging.info(f"Initial memory usage: {get_memory_usage():.2f} MB")

        for j, query in enumerate(chunk):
            query_num = start_index + j + 1
            logging.info(f"--- Running query {query_num}/{total_queries}: {query} ---")

            command = [
                VENV_PYTHON, SCRAPER_MAIN_SCRIPT, '--search', query,
                '--total', str(TOTAL_RESULTS_PER_QUERY), '--output', output_csv_path, '--append'
            ]

            try:
                # Run the scraper with a timeout and without check=True to handle errors manually
                process = subprocess.run(
                    command, capture_output=True, text=True, cwd=SCRAPER_VENDOR_DIR, timeout=120
                )

                if process.returncode == 0:
                    logging.info(f"Successfully completed query: {query}")
                    if process.stderr:
                        # Log warnings from the scraper even on success
                        logging.warning(f"Scraper STDERR:\n{process.stderr}")
                else:
                    # The scraper script failed (e.g., timeout, no results found)
                    logging.error(f"Scraper failed for query: '{query}' with code {process.returncode}")
                    logging.error(f"STDERR:\n{process.stderr}")

            except subprocess.TimeoutExpired:
                logging.error(f"Subprocess for query '{query}' timed out after 120 seconds. Moving on.")
            except Exception as e:
                # Catch any other unexpected errors in the wrapper script
                logging.error(f"An unexpected wrapper error occurred for query '{query}': {e}")
                # We do not break the loop, allowing the process to continue
        
        mem_usage = get_memory_usage()
        logging.info(f"Finished Chunk {i + 1}/{num_chunks}. Memory usage: {mem_usage:.2f} MB")

        if (i + 1) < num_chunks:
            if mem_usage > MEMORY_THRESHOLD_MB:
                logging.warning(f"Memory usage ({mem_usage:.2f} MB) exceeded threshold ({MEMORY_THRESHOLD_MB} MB). Pausing for 30 seconds.")
                time.sleep(30)
            else:
                logging.info(f"Pausing for {pause_between_chunks} seconds before next chunk...")
                time.sleep(pause_between_chunks)

    logging.info("--- Google Maps scraping process finished. ---")
    if os.path.exists(output_csv_path):
        logging.info(f"All results saved to {output_csv_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the Google Maps Scraper with specific queries or from config.")
    parser.add_argument(
        '--queries',
        nargs='+',
        help='A list of specific queries to run. Overrides the config file.'
    )
    args = parser.parse_args()

    if args.queries:
        search_queries = args.queries
        logging.info(f"Running with {len(search_queries)} queries provided from command line.")
    else:
        logging.info("No specific queries provided, generating from config file.")
        search_queries = generate_search_queries()
    
    run_google_maps_scraper(search_queries)
