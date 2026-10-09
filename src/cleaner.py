import pandas as pd
from pathlib import Path
import logging

class OGDDataCleaner:
    """Clase para ingestar, limpiar y filtrar los datos del OGD"""

    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.df: pd.DataFrame = None

    def load_data(self):
        """Carga el CSV original en memoria"""
        logging.info(f"Cargando datos desde {self.file_path.name}...")

        if self.file_path.suffix == '.parquet':
            # Si le pasamos el maestro, usa el motor rápido de Parquet
            self.df = pd.read_parquet(self.file_path)
        else:
            # Si le pasamos un archivo crudo del gobierno, usa el motor de CSV
            self.df = pd.read_csv(self.file_path, low_memory=False)
        return self

    def filter_vaca_muerta(self) -> 'OGDDataCleaner':
        """Filtra el dataset para dejar unicamente producción no convencional de la Cuenca Neuquina"""
        if self.df is None:
            raise ValueError("Primero debes cargar los datos usando load_data()")

        logging.info("Filtrando por Cuenca Neuquina y recurso No Convencional")

        # Filtramos por tipo de recurso y cuenca
        mask_no_convencional = self.df['tipo_de_recurso'].str.upper() == 'NO CONVENCIONAL'
        mask_cuenca = self.df['cuenca'].str.upper() == 'NEUQUINA'

        # Usamos .copy() para evitar SettingWithCopyWarning
        self.df = self.df[mask_no_convencional & mask_cuenca].copy()

        logging.info(f"Filas retenidas post-filtro:{len(self.df):,}")
        return self

    def optimize_and_clean(self):
        """Reduce el tamaño del dataset, maneja valores nulos y crea variables temporales"""
        logging.info("Optimizando variables y limpiando valores nulos...")

        # Seleccionamos solo las columnas necesarias para el dashboard
        columnas_necesarias = ['idpozo', 'sigla', 'empresa', 'anio', 'mes', 'prod_pet', 'prod_gas', 'prod_agua', 'formacion', 'areayacimiento']
        cols_presentes = [c for c in columnas_necesarias if c in self.df.columns]
        self.df = self.df[cols_presentes].copy()

        # Rellenamos nulos
        columnas_produccion = ['prod_pet', 'prod_gas', 'prod_agua']
        cols_prod_presentes = [c for c in columnas_produccion if c in self.df.columns]
        self.df[cols_prod_presentes] = self.df[cols_prod_presentes].fillna(0)

        # Creación de fecha
        if 'anio' in self.df.columns and 'mes' in self.df.columns:
            # Creamos una columna datetime armando un string 'YYYY-MM-01'
            self.df['fecha'] = pd.to_datetime(
                self.df['anio'].astype(str) + "-" + self.df['mes'].astype(str) + "-01"
            )

        # Optimización de memoria
        cols_categoricas = ['empresa', 'formacion', 'areayacimiento']
        for col in cols_categoricas:
            if col in cols_categoricas:
                self.df[col] = self.df[col].astype('category')

        return self

    def get_processed_data(self) -> pd.DataFrame:
        """Devuelve el DataFrame limpio"""
        return self.df