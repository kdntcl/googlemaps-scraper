# -*- coding: utf-8 -*-
"""
Archivo de Configuración Estratégica para Scraper de Google Maps

Este archivo centraliza la configuración para la búsqueda de empresas 
con potencial para convenios dentales.

Para modificar el alcance del scrapeo, simplemente edita las listas
de ubicaciones y categorías a continuación.
"""

# ==============================================================================
# CONFIGURACIÓN ACTIVA PARA LA BÚSQUEDA DE PROSPECTOS
# ==============================================================================

# --- 1. Definición Geográfica Estratégica ---
# Se prioriza Concepción y sus comunas aledañas, y se desglosa Concepción
# en barrios para una búsqueda más granular.

COMUNAS_CERCANAS = [
    "San Pedro de la Paz",
    "Chiguayante",
    "Hualpén",
    "Talcahuano",
]

SECTORES_CONCEPCION = [
    # Centro y alrededores
    "Centro de Concepción",
    "Parque Ecuador",
    "Barrio Universitario",
    "Plaza Perú",
    "Plaza de Armas",
    "Barrio Estación",
    "Remodelación Paicaví",

    # Ejes principales
    "Paicaví",
    "Avenida Los Carrera",

    # Sectores residenciales y comerciales
    "Barrio Norte",
    "Villa San Francisco",
    "Santa Sabina",
    "Lomas de San Andrés",
    "Lomas de Bellavista",
    "Lomas de San Sebastián",
    "Villa Universitaria",
    "Collao",
    "Nonguén",
    "Palomares",
    "Pedro de Valdivia",
    "Pedro de Valdivia Bajo",
    "Agüita de la Perdiz",
    "Lorenzo Arenas",
    "Laguna Redonda",
    "Pedro del Río Zañartu",
]

# Lista final de ubicaciones a buscar.
ACTIVE_LOCATIONS = ["Concepción"] + SECTORES_CONCEPCION + COMUNAS_CERCANAS


# --- 2. Rutas y Nombres de Archivos ---
import os
# Apuntar a la raíz del proyecto, un nivel arriba de 'src'
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'database', 'concepcion_empresas.db')
OUTPUT_DIR_BASE = os.path.join(PROJECT_ROOT, 'data')

# --- 3. Categorías de Empresas Estratégicas ---
# Enfocadas en empresas con potencial de tener equipos de trabajo.

ACTIVE_CATEGORIES = [
    # Retail y Servicios con alto personal

    "Centro comercial",
    "Gimnasio",
    "Centro deportivo",
    "Hotel",
    "Notaría",
    "Ferretería",
    "Automotora",
    "Tienda de electrónica",
    "Librería",
    
    # Oficinas y Empresas
    "Empresa de construcción",
    "Inmobiliaria",
    "Oficina de arquitectos",
    "Agencia de publicidad",
    "Empresa de seguridad",
    "Empresa de logística",
    "Centro de negocios",
    "Oficina corporativa",
    "Consultora",
    "Estudio de abogados",
    "Oficina de contabilidad",
    "Corredora de propiedades",
    "Agencia de viajes",
    "Imprenta",

    # Educación (excluyendo universidades)
    "Colegio",
    "Escuela",
    "Liceo",
    "Instituto Profesional",
    "Jardín infantil",
    "Sala cuna",
    "Preuniversitario",

    # Salud (Clínicas con personal, no consultas individuales)
    "Clínica veterinaria",

    # Medios
    "Radio",
    "Canal de televisión",
    "Diario"
]
