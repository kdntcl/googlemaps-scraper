import os
import sys
import pandas as pd
import sqlite3
import logging

# --- Configuración de Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuración de Rutas ---
# Añadir el directorio raíz del proyecto a sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

from src.config import DB_PATH

# Rutas de archivos
INPUT_CSV_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw', 'google_maps', 'google_maps_results.csv')

# --- Funciones de Base de Datos ---
def create_db_schema(cursor):
    """Crea las tablas de la base de datos si no existen."""
    # Tabla de empresas (tabla principal)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS empresas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        direccion TEXT,
        categoria_google TEXT, 
        fuente TEXT NOT NULL
    );
    """)
    # Tabla de teléfonos (relacionada con empresas)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS telefonos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        empresa_id INTEGER,
        numero TEXT NOT NULL,
        FOREIGN KEY (empresa_id) REFERENCES empresas (id)
    );
    """)
    # Tabla de sitios web (relacionada con empresas)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS webs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        empresa_id INTEGER,
        url TEXT NOT NULL,
        estado_scraping TEXT DEFAULT 'pendiente' NOT NULL,
        fecha_ultimo_scraping TIMESTAMP,
        FOREIGN KEY (empresa_id) REFERENCES empresas(id)
    );
    """)
    # Tabla de correos (relacionada con empresas)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS emails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        empresa_id INTEGER,
        email TEXT NOT NULL,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
        FOREIGN KEY (empresa_id) REFERENCES empresas(id)
    );
    """)
    logging.info("Esquema de la base de datos verificado/creado exitosamente.")

# --- Funciones de Limpieza ---
def clean_phone_number(phone):
    """Limpia y estandariza los números de teléfono."""
    if not isinstance(phone, str):
        return None
    # Eliminar caracteres no numéricos excepto el '+' inicial
    cleaned = ''.join(filter(str.isdigit, phone))
    if len(cleaned) >= 8:
        return cleaned
    return None

# --- Lógica Principal ---
def main():
    """Lee los datos de Google Maps, los limpia y los inserta en la base de datos SQLite."""
    if not os.path.exists(INPUT_CSV_PATH):
        logging.error(f"El archivo de entrada no se encontró en: {INPUT_CSV_PATH}")
        return

    # Asegurarse de que el directorio de la base de datos exista
    db_dir = os.path.dirname(DB_PATH)
    os.makedirs(db_dir, exist_ok=True)

    logging.info(f"Conectando a la base de datos en: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Asegurarse de que el esquema de la DB exista
    create_db_schema(cursor)

    logging.info(f"Leyendo datos desde: {INPUT_CSV_PATH}")
    # Usar on_bad_lines='warn' para que el parser ignore las líneas con formato incorrecto
    # en lugar de fallar. Esto es crucial para manejar los CSV imperfectos del scraping.
    df = pd.read_csv(INPUT_CSV_PATH, on_bad_lines='warn')

    # Renombrar columnas para consistencia
    df.rename(columns={
        'name': 'nombre',
        'address': 'direccion',
        'website': 'web',
        'phone_number': 'telefono',
        'place_type': 'categoria_google'
    }, inplace=True)

    empresas_agregadas = 0
    telefonos_agregados = 0
    webs_agregadas = 0

    for _, row in df.iterrows():
        nombre_empresa = row.get('nombre')
        # Robust check for missing or empty names (handles NaN, None, and empty strings)
        if pd.isna(nombre_empresa) or not str(nombre_empresa).strip():
            continue

        # 1. Verificar si la empresa ya existe (por nombre)
        cursor.execute("SELECT id FROM empresas WHERE nombre = ?", (nombre_empresa,))
        result = cursor.fetchone()

        if result:
            empresa_id = result[0]
            logging.debug(f"La empresa '{nombre_empresa}' ya existe con ID: {empresa_id}")
        else:
            # 2. Si no existe, insertarla
            cursor.execute("""
                INSERT INTO empresas (nombre, direccion, categoria_google, fuente)
                VALUES (?, ?, ?, ?)
            """, (nombre_empresa, row.get('direccion'), row.get('categoria_google'), 'google_maps'))
            empresa_id = cursor.lastrowid
            empresas_agregadas += 1
            logging.info(f"Nueva empresa agregada: '{nombre_empresa}' con ID: {empresa_id}")

        # 3. Procesar y agregar teléfono
        phone = clean_phone_number(row.get('telefono'))
        if phone:
            cursor.execute("SELECT id FROM telefonos WHERE numero = ? AND empresa_id = ?", (phone, empresa_id))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO telefonos (empresa_id, numero) VALUES (?, ?)", (empresa_id, phone))
                telefonos_agregados += 1

        # 4. Procesar y agregar web
        web = row.get('web')
        if isinstance(web, str) and web:
            cursor.execute("SELECT id FROM webs WHERE url = ? AND empresa_id = ?", (web, empresa_id))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO webs (empresa_id, url) VALUES (?, ?)", (empresa_id, web))
                webs_agregadas += 1

    conn.commit()
    conn.close()

    logging.info("--- Proceso de integración finalizado ---")
    logging.info(f"Nuevas empresas agregadas: {empresas_agregadas}")
    logging.info(f"Nuevos teléfonos agregados: {telefonos_agregados}")
    logging.info(f"Nuevas webs agregadas: {webs_agregadas}")

if __name__ == "__main__":
    main()
