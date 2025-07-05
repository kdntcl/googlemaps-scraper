# Plan de Acción: Generación de Prospectos para Convenios Dentales

Este documento describe el plan de trabajo del proyecto, cuyo objetivo es construir una base de datos de empresas del Gran Concepción, **enfocada y optimizada para la prospección de convenios dentales**.

---

## Fase 1: Recopilación de Datos Base (Google Maps)

**Estado: Implementación completada. Pendiente de ejecución masiva.**

- [x] **1.1. Definición Estratégica:**
  - [x] Se re-enfocó el objetivo hacia empresas con potencial para convenios.
  - [x] Se definieron y curaron las ubicaciones y categorías de búsqueda en `src/config.py`.

- [x] **1.2. Implementación de Scrapers y Procesamiento:**
  - [x] Se integró y optimizó un scraper de Google Maps (`run_google_maps.py`).
  - [x] Se desarrolló el script `build_database.py` que procesa los datos crudos y los inserta en una base de datos SQLite, preparando la estructura para la Fase 2.

- [ ] **1.3. Ejecución Masiva:**
  - [ ] Lanzar `src/scrapers/run_google_maps.py` para recopilar datos de todas las categorías estratégicas.
  - [ ] Ejecutar `src/processing/build_database.py` para construir la base de datos inicial completa.

---

## Fase 2: Enriquecimiento con Correos Electrónicos

**Estado: Implementación y validación completadas. Pendiente de ejecución masiva.**

- [x] **2.1. Implementación del Scraper de Correos:**
  - [x] Se desarrolló el script `src/scrapers/email_scraper.py` utilizando `crawl4ai`.
  - [x] Se implementó una lógica de **scraping con estado**: la base de datos registra qué sitios web han sido procesados (`estado_scraping`) para evitar trabajo redundante.
  - [x] Se incluyó una lista negra de dominios (redes sociales, etc.) para optimizar el proceso.

- [x] **2.2. Validación del Flujo de Trabajo Completo:**
  - [x] Se realizó una prueba de extremo a extremo con un conjunto de datos de muestra.
  - [x] Se validó que el sistema completo (Fase 1 -> Fase 2) funciona correctamente: recopila empresas, las inserta en la base de datos, procesa los sitios web pendientes y actualiza su estado de forma fiable.

- [ ] **2.3. Ejecución Masiva:**
  - [ ] Una vez completada la Fase 1, lanzar `src/scrapers/email_scraper.py` para procesar todos los sitios web de la base de datos.

---

## Fase 3: Mantenimiento y Futuras Mejoras

**Estado: Pendiente.**

- [ ] **3.1. Unificación y Deduplicación Final:**
  - [ ] A futuro, si se integran nuevas fuentes de datos, implementar una estrategia robusta para consolidar y eliminar duplicados.

- [x] **3.2. Documentación Continua:**
  - [x] El `README.md` y `TASKS.md` han sido actualizados para reflejar la arquitectura y el estado actual del proyecto.
