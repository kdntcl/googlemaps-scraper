# -*- coding: utf-8 -*-

"""
Archivo de configuración para el scraper de centros de salud.
Contiene las listas de ubicaciones y categorías de búsqueda para el área de la salud.
"""

# --- Ubicaciones Geográficas ---
# Comunas del Gran Concepción y zonas aledañas de interés.
COMUNAS_GRAN_CONCEPCION = [
    "Concepción",
    "Talcahuano",
    "San Pedro de la Paz",
    "Hualpén",
    "Chiguayante",
    "Penco",
    "Tomé",
    "Coronel",
    "Lota",
    "Hualqui"
]

# Lista consolidada de ubicaciones activas para el scraper.
# Se mantiene simple, buscando en las comunas principales.
ACTIVE_LOCATIONS = COMUNAS_GRAN_CONCEPCION

# --- Categorías de Búsqueda de Salud ---
# Términos específicos para encontrar centros de salud públicos y administrativos.
ACTIVE_CATEGORIES = [
    "DAS Dirección de Administración de Salud Municipal",
    "CESFAM",
    "Centro de Salud Familiar",
    "Centro de Salud",
    "Posta Rural",
    "Consultorio"
]

# --- Configuración de la Base de Datos ---
# Ruta a la nueva base de datos para los prospectos de salud.
DB_PATH_SALUD = 'data/database/salud_prospectos.db'
