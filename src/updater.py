import pandas as pd
import re
import logging
from pathlib import Path
from data_builder import limpiar_dataframe
from renamer import renombrar_archivos_crudos

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def actualizar_incremental() -> None:
    """Actualiza el dataset maestro borrando el último año y recargándolo con datos frescos."""
    directorio_base = Path(__file__).parent.parent
    ruta_raw = directorio_base / 'data' / 'raw'
    ruta_maestro = directorio_base / 'data' / 'produccion.parquet'

    renombrar_archivos_crudos()

    if not ruta_maestro.exists():
        logging.error("No se encontró producción.parquet. Corré data_builder.py primero.")
        return

    logging.info("Leyendo base de datos maestra...")
    df_maestro = pd.read_parquet(ruta_maestro)

    # Detectamos el último año que tenemos en la base
    ultimo_anio = df_maestro['anio'].max()
    logging.info(f"Último año detectado en la base: {ultimo_anio}. Preparando actualización...")

    # Borramos los registros de ese año para no duplicarlos
    df_maestro = df_maestro[df_maestro['anio'] < ultimo_anio].copy()

    # Buscamos en la carpeta raw los archivos de ese año en adelante
    archivos_nuevos = []
    for archivo in ruta_raw.glob('prod_*.csv'):
        match = re.search(r'(\d{4})', archivo.name)
        if match and int(match.group(1)) >= ultimo_anio:
            archivos_nuevos.append(archivo)

    if not archivos_nuevos:
        logging.warning("No se encontraron archivos para actualizar en data/raw")
        return

    lista_dfs = []
    for archivo in archivos_nuevos:
        logging.info(f"Procesando datos frescos de: {archivo.name}...")
        try:
            df = pd.read_csv(archivo, low_memory=False)
            df = limpiar_dataframe(df)

            lista_dfs.append(df)
        except Exception as e:
            logging.error(f"Error procesando {archivo.name}: {e}")
        

    # Unimos el historial intacto con los meses nuevos procesados
    if lista_dfs:
        df_reciente = pd.concat(lista_dfs, ignore_index=True)
        df_final = pd.concat([df_maestro, df_reciente], ignore_index=True)

        logging.info("Guardando base de datos actualizada...")
        df_final.to_parquet(ruta_maestro, index=False)
        logging.info(f"¡Actualización completa! Total de filas: {len(df_final):,}".replace(',', '.'))
    else:
        logging.error("No se pudo procesar la nueva data.")

if __name__ == "__main__":
    actualizar_incremental()