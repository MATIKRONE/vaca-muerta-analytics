import pandas as pd

class OGDDataCleaner:
    """Clase para ingestar, limpiar y filtrar los datos del OGD"""
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None

    def load_data(self):
        """Carga el CSV original en memoria"""
        self.df = pd.read_csv(self.file_path, low_memory=False)
        return self

    def filter_vaca_muerta(self):
        """Filtra el dataset para dejar unicamente producción no convencional de la Cuenca Neuquina"""
        if self.df is None:
            raise ValueError("Primero debes cargar los datos usando load_data()")

        # Filtramos por tipo de recurso y cuenca
        mask_no_convencional = self.df['tipo_de_recurso'] == 'NO CONVENCIONAL'
        mask_cuenca = self.df['cuenca'] == 'NEUQUINA'

        self.df = self.df[mask_no_convencional & mask_cuenca]
        return self

    def optimize_and_clean(self):
        """Reduce el tamaño del dataset y maneja valores nulos"""
        # Seleccionamos solo las columnas necesarias para el dashboard
        columnas_necesarias = ['idpozo', 'sigla', 'empresa', 'anio', 'mes', 'prod_pet', 'prod_gas', 'prod_agua', 'formacion']
        self.df = self.df[columnas_necesarias]

        columnas_produccion = ['prod_pet', 'prod_gas', 'prod_agua']
        self.df[columnas_produccion] = self.df[columnas_produccion].fillna(0)

        return self

    def get_processed_data(self):
        """Devuelve el DataFrame limpio"""
        return self.df