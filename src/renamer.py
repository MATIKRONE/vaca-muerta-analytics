import re
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def renombrar_archivos_crudos() -> None:
    """Busca archivos con nombres largos en data/raw y los renombra al formato prod_AAAA.csv"""
    logging.info("Iniciando limpieza de nombres de archivos...")
    
    # Rutas dinámicas
    directorio_base = Path(__file__).parent.parent
    ruta_carpeta = directorio_base / 'data' / 'raw'
    
    archivos = list(ruta_carpeta.glob('*.csv'))
    
    if not archivos:
        logging.warning("No se encontraron archivos CSV en data/raw/")
        return

    for archivo_viejo in archivos:
        nombre_base = archivo_viejo.name
        
        # Si ya tiene el formato correcto, lo saltamos
        if nombre_base.startswith('prod_'):
            continue
            
        # Buscamos un año que empiece con 20 para ser más precisos
        match_anio = re.search(r'(20\d{2})', nombre_base)
        
        if match_anio:
            anio = match_anio.group(1)
            nuevo_nombre = f"prod_{anio}.csv"
            archivo_nuevo = ruta_carpeta / nuevo_nombre
            
            # Si por casualidad ya existe un archivo con ese nombre nuevo, lo borramos primero para evitar que el script falle por conflicto
            if archivo_nuevo.exists():
                archivo_nuevo.unlink()
                
            # Renombramos usando pathlib
            archivo_viejo.rename(archivo_nuevo)
            logging.info(f"Renombrado: {nombre_base} -> {nuevo_nombre}")
        else:
            logging.warning(f"No se encontró un año válido en el archivo: {nombre_base}")

if __name__ == "__main__":
    renombrar_archivos_crudos()