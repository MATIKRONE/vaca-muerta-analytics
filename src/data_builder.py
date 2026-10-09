import pandas as pd
from pathlib import Path
import logging
from renamer import renombrar_archivos_crudos

# Configuración de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

def limpiar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Estandariza columnas y maneja la ausencia de idpozo."""
    df.columns = df.columns.str.lower()

    if 'idpozo' not in df.columns and 'sigla' in df.columns:
        logging.info("Columna 'idpozo' no encontrada. Reemplazando con 'sigla'.")
        df['idpozo'] = df['sigla']
    else:
        logging.warning("No se encontró 'idpozo' ni 'sigla' en el dataset.")

    return df



def unificar_datasets():
    logging.info("Iniciando la unificación de datos...")
    # Path(__file__) detecta automáticamente donde está este script (src/)
    # .parent.parent sube a la carpeta raiz del proyecto
    directorio_base = Path(__file__).parent.parent
    ruta_raw = directorio_base / 'data' / 'raw'
    ruta_salida = directorio_base / 'data' / 'produccion.parquet'

    logging.info("Estandarizando nombres de archivos en raw...")
    renombrar_archivos_crudos()

    # Buscamos los archivos CSV
    archivos_csv = list(ruta_raw.glob('*.csv'))

    if not archivos_csv:
        logging.error(f"No se encontraron archivos en {ruta_raw}")
        return

    lista_dataframes = []

    for archivo in archivos_csv:
        logging.info(f"Leyendo: {archivo.name}...")
        try:
            df = pd.read_csv(archivo, low_memory=False)
            df_limpio = limpiar_dataframe(df)
            lista_dataframes.append(df_limpio)

        except Exception as e:
            logging.error(f"Error al leer {archivo.name}: {e}")

    # Concatenación y guardado
    if lista_dataframes:
        df_maestro = pd.concat(lista_dataframes, ignore_index=True)
        df_maestro.to_parquet(ruta_salida, index=False)

        logging.info(f"Archivo maestro creado en {ruta_salida.name}")
        logging.info(f"Años detectados: {anios}")
    else:
        logging.warning("No se pudo procesar ningún DataFrame")

if __name__ == "__main__":
    unificar_datasets()