import os
import sys
import sqlite3
import csv
import logging

# --- Configuración de Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Añadir el directorio raíz del proyecto a sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

from src.config import DB_PATH

# --- Rutas de Archivos ---
EXPORT_DIR = os.path.join(PROJECT_ROOT, 'data', 'exports')
EXPORT_FILE_PATH = os.path.join(EXPORT_DIR, 'prospectos_concepcion.csv')

def create_export_directory():
    """Crea el directorio de exportación si no existe."""
    if not os.path.exists(EXPORT_DIR):
        logging.info(f"Creando directorio de exportación en: {EXPORT_DIR}")
        os.makedirs(EXPORT_DIR)

def export_data_to_csv():
    """
    Conecta a la base de datos, extrae los datos consolidados de las empresas
    y los guarda en un archivo CSV.
    """
    logging.info(f"Conectando a la base de datos en: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = """
        SELECT
            e.nombre AS \"Nombre\",
            e.direccion AS \"Dirección\",
            e.categoria_google AS \"Categoría\",
            GROUP_CONCAT(DISTINCT t.numero) AS \"Teléfonos\",
            GROUP_CONCAT(DISTINCT w.url) AS \"Sitios Web\",
            GROUP_CONCAT(DISTINCT em.email) AS \"Correos Electrónicos\",
            e.fuente AS \"Fuente\"
        FROM
            empresas e
        LEFT JOIN
            telefonos t ON e.id = t.empresa_id
        LEFT JOIN
            webs w ON e.id = w.empresa_id
        LEFT JOIN
            emails em ON e.id = em.empresa_id
        GROUP BY
            e.id, e.nombre, e.direccion, e.categoria_google, e.fuente
        ORDER BY
            e.nombre;
    """

    logging.info("Ejecutando consulta para consolidar datos...")
    cursor.execute(query)
    rows = cursor.fetchall()
    
    # Obtener los nombres de las columnas
    headers = [description[0] for description in cursor.description]
    
    conn.close()
    logging.info(f"Consulta finalizada. Se encontraron {len(rows)} registros consolidados.")

    # Escribir los datos al archivo CSV
    try:
        logging.info(f"Escribiendo datos en el archivo CSV: {EXPORT_FILE_PATH}")
        with open(EXPORT_FILE_PATH, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)  # Escribir la fila de encabezado
            writer.writerows(rows)   # Escribir los datos
        
        logging.info("¡Exportación completada exitosamente!")
        logging.info(f"El archivo se ha guardado en: {EXPORT_FILE_PATH}")

    except IOError as e:
        logging.error(f"Error al escribir el archivo CSV: {e}")

def main():
    """Función principal para orquestar la exportación."""
    logging.info("--- Iniciando el proceso de exportación a CSV ---")
    create_export_directory()
    export_data_to_csv()
    logging.info("--- Proceso de exportación finalizado ---")

if __name__ == '__main__':
    main()
