import os
import sys
import sqlite3
import logging
import re
import asyncio
import psutil
import time
from urllib.parse import urlparse, urljoin
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from bs4 import BeautifulSoup
# LXMLWebScrapingStrategy ya no es necesaria al renderizar con JavaScript

# --- Configuración de Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Añadir el directorio raíz del proyecto a sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

from src.config import DB_PATH

# --- Expresión Regular para Emails ---
EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

# --- Lista Negra de Dominios ---
DOMAIN_BLACKLIST = [
    'facebook.com',
    'instagram.com',
    'twitter.com',
    'linkedin.com',
    'youtube.com',
    'tiktok.com',
    'google.com',
    'whatsapp.com',
    'telegram.org',
    'w3.org',
    'sentry.io',
    'jsdelivr.net'
]

def normalize_url(url):
    """Asegura que la URL tenga un esquema, prefiriendo https, y elimina espacios."""
    if not url:
        return None
    url = url.strip()
    parsed = urlparse(url)
    if not parsed.scheme:
        return f'https://{url}'
    return url

async def find_emails_on_site(crawler: AsyncWebCrawler, empresa_id: int, base_url: str):
    """
    Realiza un rastreo dirigido:
    1. Analiza la página principal y extrae correos.
    2. Busca enlaces de contacto y páginas relevantes.
    3. Rastrea esas páginas específicas para encontrar más correos.
    """
    all_emails = set()
    urls_to_crawl = set()
    processed_urls = set()

    # 1. Rastrear la página principal para buscar correos y enlaces de contacto
    try:
        logging.info(f"[Empresa ID: {empresa_id}] Analizando página principal: {base_url}")
        main_page_result = await crawler.arun(base_url)
        processed_urls.add(base_url)

        if main_page_result and main_page_result.success and main_page_result.html:
            # Extraer correos de la página principal
            found_on_main = EMAIL_REGEX.findall(main_page_result.html)
            if found_on_main:
                all_emails.update(email.lower() for email in found_on_main)

            # Buscar enlaces de contacto con BeautifulSoup
            soup = BeautifulSoup(main_page_result.html, 'html.parser')
            contact_keywords = ['contacto', 'contact', 'nosotros', 'quienes-somos', 'about', 'empresa']
            
            for link in soup.find_all('a', href=True):
                href = link['href'].lower()
                link_text = link.get_text().lower()
                
                if any(keyword in href for keyword in contact_keywords) or any(keyword in link_text for keyword in contact_keywords):
                    full_url = urljoin(base_url, link['href'])
                    if urlparse(full_url).netloc == urlparse(base_url).netloc:
                        urls_to_crawl.add(full_url)

    except Exception as e:
        logging.error(f"[Empresa ID: {empresa_id}] Error analizando la página principal {base_url}: {e}")
        return all_emails # Devolver lo encontrado hasta ahora

    # 2. Rastrear las páginas de contacto encontradas
    urls_to_crawl.discard(base_url) # Evitar rastrear la página principal de nuevo

    if not urls_to_crawl:
        logging.info(f"[Empresa ID: {empresa_id}] No se encontraron enlaces de contacto. Se revisó solo la página principal.")
        return all_emails

    logging.info(f"[Empresa ID: {empresa_id}] Rastreando páginas de contacto encontradas: {urls_to_crawl}")

    for url in urls_to_crawl:
        if url in processed_urls:
            continue
        try:
            logging.info(f"[Empresa ID: {empresa_id}] Rastreado página de contacto: {url}")
            result = await crawler.arun(url)
            if result and result.success and result.html:
                found = EMAIL_REGEX.findall(result.html)
                if found:
                    all_emails.update(email.lower() for email in found)
            processed_urls.add(url)
        except Exception as e:
            logging.error(f"[Empresa ID: {empresa_id}] Error rastreando la página de contacto {url}: {e}")

    return all_emails

def check_memory_and_pause(threshold=90.0, pause_duration=30):
    """Verifica el uso de memoria y pausa si supera un umbral."""
    memory_usage = psutil.virtual_memory().percent
    if memory_usage > threshold:
        logging.warning(f"Uso de memoria ({memory_usage:.2f}%) supera el umbral de {threshold}%. Pausando por {pause_duration} segundos.")
        time.sleep(pause_duration)
        logging.info("Reanudando el proceso después de la pausa.")

def get_empresas_pendientes_de_scrapeo():
    """Obtiene empresas cuyo estado de scraping es 'pendiente'."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = """
        SELECT e.id, w.url
        FROM empresas e
        JOIN webs w ON e.id = w.empresa_id
        WHERE w.estado_scraping = 'pendiente'
    """
    
    cursor.execute(query)
    empresas = cursor.fetchall()
    conn.close()
    logging.info(f"Encontradas {len(empresas)} empresas pendientes de scrapeo.")
    return empresas

def save_emails(empresa_id, emails):
    """Guarda una lista de correos para una empresa en la BD."""
    if not emails:
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for email in emails:
        try:
            # Se omite fecha_creacion porque la tabla la añade por defecto
            cursor.execute("INSERT INTO emails (empresa_id, email) VALUES (?, ?)", (empresa_id, email))
            logging.info(f"Email '{email}' guardado para la empresa ID {empresa_id}.")
        except sqlite3.IntegrityError:
            logging.warning(f"Email '{email}' ya existe para la empresa ID {empresa_id}.")
    conn.commit()
    conn.close()

def update_scraping_status(empresa_id, url, status):
    """Actualiza el estado de scraping de una web en la BD."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE webs 
            SET estado_scraping = ?, fecha_ultimo_scraping = CURRENT_TIMESTAMP 
            WHERE empresa_id = ? AND url = ?
        """, (status, empresa_id, url))
        conn.commit()
        logging.info(f"Estado de scraping actualizado a '{status}' para la empresa ID {empresa_id} y URL {url}.")
    except sqlite3.Error as e:
        logging.error(f"Error al actualizar el estado de scraping para la empresa ID {empresa_id}: {e}")
    finally:
        conn.close()

async def main():
    """Función principal para orquestar el scraping de emails con manejo de recursos."""
    logging.info("--- Iniciando Fase 2: Scraper de Correos con crawl4ai ---")
    
    empresas = get_empresas_pendientes_de_scrapeo()
    
    # --- Lógica de Chunks y Monitoreo ---
    chunk_size = 5  # Procesar de 5 en 5 para no saturar la memoria con deep crawl
    total_empresas = len(empresas)
    logging.info(f"Se procesarán {total_empresas} empresas en lotes de {chunk_size}.")

    # Habilitar JavaScript para renderizar contenido dinámico
    browser_config = BrowserConfig(
        headless=True,
        java_script_enabled=True
    )

    # La configuración de rastreo profundo (deep_crawl_strategy) ya no es necesaria aquí,
    # la nueva función find_emails_on_site implementa una lógica de rastreo dirigido.
    async with AsyncWebCrawler(config=browser_config) as crawler:
        for i in range(0, total_empresas, chunk_size):
            chunk = empresas[i:i + chunk_size]
            logging.info(f"--- Procesando Lote {i//chunk_size + 1}/{(total_empresas + chunk_size - 1)//chunk_size} (Empresas {i+1}-{min(i+chunk_size, total_empresas)}) ---")
            
            check_memory_and_pause()

            for empresa_id, website_from_db in chunk:
                website = normalize_url(website_from_db)
                if not website:
                    logging.warning(f"[Empresa ID: {empresa_id}] URL inválida: '{website_from_db}'. Omitiendo.")
                    continue

                domain = urlparse(website).netloc.replace('www.', '')
                if any(blacklisted_domain in domain for blacklisted_domain in DOMAIN_BLACKLIST):
                    logging.info(f"[Empresa ID: {empresa_id}] Omitiendo {domain} (lista negra).")
                    continue
                
                try:
                    # El timeout envuelve todo el proceso de rastreo dirigido para un sitio.
                    emails = await asyncio.wait_for(
                        find_emails_on_site(crawler, empresa_id, website),
                        timeout=45.0  # Aumentado a 45s para dar tiempo al rastreo de 2-3 páginas
                    )
                    if emails:
                        save_emails(empresa_id, emails)
                        update_scraping_status(empresa_id, website, 'exitoso_con_email')
                    else:
                        logging.info(f"[Empresa ID: {empresa_id}] No se encontraron correos en {website}")
                        update_scraping_status(empresa_id, website, 'exitoso_sin_email')

                except asyncio.TimeoutError:
                    logging.warning(f"[Empresa ID: {empresa_id}] El procesamiento de {website} excedió el tiempo límite de 45s. Omitiendo.")
                    update_scraping_status(empresa_id, website, 'fallido')
                except Exception as e:
                    logging.error(f"[Empresa ID: {empresa_id}] Error al procesar {website}: {e}")
                    update_scraping_status(empresa_id, website, 'fallido')

            if i + chunk_size < total_empresas:
                logging.info("Pausa de 15 segundos entre lotes para liberar recursos.")
                time.sleep(15)

if __name__ == "__main__":
    asyncio.run(main())
