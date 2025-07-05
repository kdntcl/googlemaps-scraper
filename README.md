# Scraper Estratégico de Empresas - Concepción

Este proyecto está diseñado para construir una base de datos de prospectos de alta calidad en Concepción y sus alrededores. Opera en dos fases principales:

1.  **Fase 1: Recopilación de Datos.** Utiliza Google Maps para obtener una lista inicial de empresas, incluyendo nombre, dirección, teléfono y, crucialmente, su sitio web.
2.  **Fase 2: Enriquecimiento de Contactos.** Procesa los sitios web recopilados para extraer direcciones de correo electrónico, implementando una lógica de estado para garantizar un proceso eficiente y sin redundancias.

---

## Arquitectura del Proyecto

La estructura del proyecto está organizada para separar la configuración, los scrapers y el procesamiento de datos, facilitando su mantenimiento y escalabilidad.

```
concepcion_scraper/
├── data/
│   ├── raw/
│   │   └── google_maps/      # Almacena los CSV brutos de Google Maps.
│   └── database/             # Contiene la base de datos final (concepcion_empresas.db).
├── src/
│   ├── __init__.py
│   ├── config.py             # Archivo central para definir ubicaciones y categorías.
│   ├── scrapers/
│   │   ├── run_google_maps.py # Orquesta el scraping de Google Maps.
│   │   └── email_scraper.py   # Orquesta el scraping de correos desde sitios web.
│   └── processing/
│       └── build_database.py # Procesa los datos brutos y los integra en la BD.
├── vendor/
│   └── google-maps-scrapper/ # Submódulo del scraper de Google Maps.
├── .venv/                    # Entorno virtual principal.
├── requirements.txt          # Dependencias del proyecto.
└── README.md                 # Este documento.
```

---

## Flujo de Trabajo

El proceso completo, desde la recolección hasta el enriquecimiento, está automatizado y se ejecuta en dos fases claras.

### Fase 1: Recopilación de Datos Base (Google Maps)

El objetivo de esta fase es poblar la base de datos con empresas y sus sitios web.

**Paso 1.1: Configuración Inicial (Solo una vez)**

El scraper de Google Maps (submódulo en `vendor`) requiere su propio entorno virtual con Python 3.9.

1.  **Navega al directorio del scraper:**
    ```bash
    cd vendor/google-maps-scrapper
    ```
2.  **Crea y activa el entorno virtual:**
    ```bash
    python3.9 -m venv .venv
    source .venv/bin/activate
    ```
3.  **Instala sus dependencias y navegadores:**
    ```bash
    pip install -r requirements.txt
    playwright install
    deactivate # Vuelve a tu entorno principal
    ```

**Paso 1.2: Ejecutar el Scraper de Google Maps**

Este comando inicia la recolección de datos usando las ubicaciones y categorías definidas en `src/config.py`.

```bash
# Desde la raíz del proyecto
python src/scrapers/run_google_maps.py
```
Los resultados se guardan en `data/raw/google_maps/google_maps_results.csv`.

**Paso 1.3: Construir la Base de Datos Inicial**

Este comando procesa el CSV, limpia los datos y los inserta en la base de datos SQLite. Los sitios web se añaden con un estado inicial de `'pendiente'`.

```bash
# Desde la raíz del proyecto
python src/processing/build_database.py
```
La base de datos se crea en `data/database/concepcion_empresas.db`.

### Fase 2: Enriquecimiento con Correos Electrónicos

Esta fase toma los sitios web pendientes de la base de datos y busca correos electrónicos.

**Paso 2.1: Ejecutar el Scraper de Correos**

```bash
# Desde la raíz del proyecto
python src/scrapers/email_scraper.py
```

**Lógica de Funcionamiento:**

1.  **Selección de Objetivos:** El script consulta la base de datos y selecciona únicamente los sitios web cuyo `estado_scraping` es `'pendiente'`.
2.  **Scraping Inteligente:** Utiliza la librería `crawl4ai` para analizar los sitios. Ignora dominios en una lista negra (ej. `facebook.com`, `instagram.com`) para mayor eficiencia.
3.  **Actualización de Estado:** Una vez procesado un sitio, actualiza su estado en la base de datos para evitar volver a analizarlo. Los posibles estados son:
    *   `exitoso_con_email`: Se encontraron y guardaron correos.
    *   `exitoso_sin_email`: Se analizó el sitio completo, pero no se encontraron correos.
    *   `fallido`: Ocurrió un error técnico durante el análisis (ej. el sitio no carga, error de certificado).
    *   `omitido_blacklist`: El dominio estaba en la lista negra.
4.  **Almacenamiento:** Los correos encontrados se guardan en la tabla `emails`, vinculados a su empresa correspondiente.

---

## Estado Actual del Proyecto

*   **Fases 1 y 2 Implementadas:** Todo el flujo de trabajo, desde la recolección de datos en Google Maps hasta el enriquecimiento con correos, está completamente implementado y funcional.
*   **Sistema Validado:** La arquitectura de dos fases y la lógica de scraping con estado han sido probadas con éxito en un conjunto de datos de muestra.
*   **Listo para Escalar:** El sistema está preparado para una ejecución a gran escala con la lista completa de categorías y ubicaciones estratégicas.

---

## Estrategia de Búsqueda

Toda la estrategia de búsqueda (qué y dónde buscar) se controla desde un único archivo:

-   **`src/config.py`**: Modifica las listas `ACTIVE_LOCATIONS` y `ACTIVE_CATEGORIES` en este archivo para ajustar el alcance de tu búsqueda. No es necesario tocar ningún otro script.

---

## Licencia y Notas

Este proyecto utiliza un scraper de código abierto de terceros. Toda la información recolectada proviene de fuentes públicas. El uso final de los datos es responsabilidad del usuario.
