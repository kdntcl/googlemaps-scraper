import os
import sys
import subprocess
import logging
import time
import pandas as pd

# --- Configuración de Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Añadir el directorio raíz del proyecto a sys.path ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(PROJECT_ROOT)

# --- Constantes y Rutas ---
SCRAPER_VENDOR_DIR = os.path.join(PROJECT_ROOT, 'vendor', 'google-maps-scraper')
VENV_PYTHON = os.path.join(SCRAPER_VENDOR_DIR, '.venv', 'bin', 'python')
SCRAPER_MAIN_SCRIPT = os.path.join(SCRAPER_VENDOR_DIR, 'main.py')

INPUT_CSV_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw', 'salud_publica', 'centros_salud_ssc.csv')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'data', 'exports', 'google_maps_salud')
RESULTS_FILE = os.path.join(OUTPUT_DIR, 'google_maps_salud_results.csv')

def run_scraper_for_query(query, output_file):
    """Ejecuta el scraper de Google Maps para una consulta específica."""
    if not os.path.exists(VENV_PYTHON):
        logging.error(f"El entorno virtual del scraper no se encuentra en: {VENV_PYTHON}")
        return

    command = [
        VENV_PYTHON,
        SCRAPER_MAIN_SCRIPT,
        '-s', query,       # Argumento correcto para la búsqueda
        '-t', '3',         # Limitar a 3 resultados para obtener el más relevante
        '-o', output_file,
        '--append'
    ]
    try:
        process = subprocess.run(command, capture_output=True, text=True, cwd=SCRAPER_VENDOR_DIR, timeout=120)
        if process.returncode == 0:
            logging.info(f"Consulta '{query}' completada exitosamente.")
        else:
            logging.error(f"Error al ejecutar el scraper para la consulta '{query}'. Salida: {process.stderr.strip()}")
    except subprocess.TimeoutExpired:
        logging.error(f"Timeout al ejecutar el scraper para la consulta '{query}'.")
    except Exception as e:
        logging.error(f"Ocurrió un error inesperado para la consulta '{query}': {e}")

def main():
    """Lee los centros de salud, genera consultas y ejecuta el scraper."""
    logging.info("--- Iniciando scraping de Google Maps para Centros de Salud ---")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not os.path.exists(INPUT_CSV_PATH):
        logging.error(f"El archivo de entrada no se encuentra: {INPUT_CSV_PATH}")
        return

    df = pd.read_csv(INPUT_CSV_PATH)
    # --- Generación de Consultas ---
    # 1. Consultas para cada centro de salud
    search_queries = [f"{row['nombre']}, {row['comuna']}, Bío Bío, Chile" for index, row in df.iterrows()]

    # 2. Consultas para DAS y Municipalidad por cada comuna única
    unique_communes = df['comuna'].unique()
    for comuna in unique_communes:
        search_queries.append(f'"DAS {comuna}", Bío Bío, Chile')
        search_queries.append(f'"Municipalidad de {comuna}", Bío Bío, Chile')

    # Eliminar duplicados si los hubiera
    search_queries = sorted(list(set(search_queries)))
    total_queries = len(search_queries)
    logging.info(f"Se ejecutarán {total_queries} consultas de búsqueda.")

    # Limpiar archivo de resultados si existe para empezar de cero
    if os.path.exists(RESULTS_FILE):
        os.remove(RESULTS_FILE)
        logging.info(f"Archivo de resultados anterior eliminado: {RESULTS_FILE}")

    for i, query in enumerate(search_queries):
        logging.info(f"--- Procesando consulta {i+1}/{total_queries}: {query} ---")
        run_scraper_for_query(query, RESULTS_FILE)
        time.sleep(3) # Pausa prudente entre consultas

    logging.info("--- Scraping de Google Maps (Salud) finalizado ---")

if __name__ == '__main__':
    main()


