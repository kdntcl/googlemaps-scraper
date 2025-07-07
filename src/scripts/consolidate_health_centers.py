import pandas as pd
import os

def main():
    """
    Consolida las listas de nombres de centros de salud extraídos del sitio web
    del Servicio de Salud Concepción en un único archivo CSV.
    """
    # Datos de centros de salud con su comuna
    centros = {
        'CESFAM': [
            ("CESFAM Dr. Víctor Manuel Fernández", "Concepción"), ("CESFAM Lorenzo Arenas", "Concepción"),
            ("CESFAM O'Higgins", "Concepción"), ("CESFAM Pedro de Valdivia", "Concepción"),
            ("CESFAM Santa Sabina", "Concepción"), ("CESFAM Tucapel", "Concepción"),
            ("CESFAM Juan Soto Fernández", "Concepción"), ("CESFAM Chiguayante", "Chiguayante"),
            ("CESFAM La Leonera", "Chiguayante"), ("CESFAM San Pedro", "San Pedro de la Paz"),
            ("CESFAM Candelaria", "San Pedro de la Paz"), ("CESFAM Boca Sur", "San Pedro de la Paz"),
            ("CESFAM San Pedro de la Costa", "San Pedro de la Paz"), ("CESFAM Lagunillas", "Coronel"),
            ("CESFAM Yobilo", "Coronel"), ("CESFAM Lota Alto", "Lota"),
            ("CESFAM Dr. Juan Cartes Arias", "Lota"), ("CESFAM Hualqui", "Hualqui"),
            ("CESFAM Florida", "Florida"), ("CESFAM Dr. Carlos Echeverría", "Santa Juana"),
            ("CESFAM Bellavista", "Penco")
        ],
        'Hospital': [
            ("Hospital Clínico Regional Dr. Guillermo Grant Benavente", "Concepción"),
            ("Hospital Traumatológico Concepción", "Concepción"), ("Hospital San José", "Coronel"),
            ("Hospital de Lota", "Lota"), ("Hospital Clorinda Avello", "Santa Juana"),
            ("Hospital San Agustín", "Florida")
        ],
        'CECOSF': [
            ("CECOSF Chaimávida", "Concepción"), ("CECOSF Boca Sur Viejo", "San Pedro de la Paz"),
            ("CECOSF Michaihue", "San Pedro de la Paz"), ("CECOSF Escuadrón", "Coronel"),
            ("CECOSF Lagunillas", "Coronel"), ("CECOSF Puerto Sur I. Sta. María", "Coronel"),
            ("CECOSF Colcura", "Lota"), ("CECOSF Hualqui", "Hualqui"), ("CECOSF Copiulemu", "Florida")
        ],
        'Posta Rural': [
            ("Posta de Salud Rural Patagual", "Coronel"), ("Posta de Salud Rural Puerto Norte Isla Santa María", "Coronel"),
            ("Posta de Salud Rural Granerillos", "Florida"), ("Posta de Salud Rural Los Monteros", "Florida"),
            ("Posta de Salud Rural Manco", "Florida"), ("Posta de Salud Rural Roa", "Florida"),
            ("Posta de Salud Rural Quilacoya", "Hualqui"), ("Posta de Salud Rural Puerto Talcamávida", "Hualqui"),
            ("Posta de Salud Rural Chacay", "Santa Juana"), ("Posta de Salud Rural La Generala", "Santa Juana"),
            ("Posta de Salud Rural Colico Alto", "Santa Juana"), ("Posta de Salud Rural Purgatorio", "Santa Juana"),
            ("Posta de Salud Rural Tanahuillín", "Santa Juana"), ("Posta de Salud Rural Torre Dorada", "Santa Juana")
        ],
        'DAS': [
            ("DAS Concepción", "Concepción"), ("DAS San Pedro de la Paz", "San Pedro de la Paz"),
            ("DAS Chiguayante", "Chiguayante"), ("DAS Coronel", "Coronel"),
            ("DAS Lota", "Lota"), ("DAS Santa Juana", "Santa Juana"),
            ("DAS Hualqui", "Hualqui"), ("DAS Florida", "Florida"),
            ("DAS Penco", "Penco")
        ]
    }

    # Crear una lista de diccionarios para el DataFrame final
    lista_df = []
    for tipo, establecimientos in centros.items():
        for nombre, comuna in establecimientos:
            lista_df.append({'nombre': nombre, 'tipo': tipo, 'comuna': comuna})

    # Crear DataFrame a partir de la lista
    df_total = pd.DataFrame(lista_df)



    # Definir ruta de salida y crear directorio si no existe
    output_path = 'data/raw/salud_publica/centros_salud_ssc.csv'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Guardar en CSV
    df_total.to_csv(output_path, index=False, encoding='utf-8')

    print(f"Archivo CSV creado exitosamente en: {output_path}")
    print(f"Total de establecimientos consolidados: {len(df_total)}")

if __name__ == '__main__':
    main()
