# Monitor de Producción - Vaca Muerta (ETL + Dashboard)

Este repositorio contiene un pipeline de datos (ETL) y una aplicación web interactiva desarrollada en Streamlit. El proyecto procesa datos públicos de la Secretaría de Energía de la Nación Argentina ("Capítulo IV") para monitorear y analizar la producción de hidrocarburos no convencionales en la Cuenca Neuquina (Vaca Muerta).

El objetivo es aplicar **buenas prácticas de Ingeniería de Software** (POO, modularización, principios DRY e Idempotencia) para transformar archivos pesados y desestructurados del gobierno en un panel de control interactivo con métricas clave de la industria (Water Cut, GOR, declinación de producción).

## Características Principales

- **Arquitectura ETL Modular:** Separación estricta entre extracción/limpieza de datos (Backend) y visualización (Frontend).
- **Carga Incremental:** Sistema de actualización mensual de datos idempotente, que evita duplicados y optimiza tiempos de cómputo.
- **Optimización de Memoria:** Uso de formato `.parquet` y tipos de datos categóricos en Pandas, reduciendo el peso de los datos drásticamente respecto al CSV original.
- **Análisis de Reservorio:** Cálculo y visualización temporal del Corte de Agua (Flowback) y la Relación Gas-Petróleo (GOR) para entender las estrategias de perforación (Tight Gas vs. Shale Oil).

## Stack Tecnológico

- **Python 3.10+**
- **Pandas & Parquet:** Ingesta, limpieza, optimización y guardado de datos.
- **Pathlib & Logging:** Manejo robusto de rutas relativas y auditoría de procesos en consola.
- **Streamlit:** Desarrollo de la interfaz gráfica y panel de control.
- **Altair:** Gráficos interactivos y series de tiempo.

## Estructura del Proyecto

```text
vaca-muerta-analytics/
├── data/                   # Datos (Ignorada en Git por tamaño)
│   ├── raw/                # CSVs crudos descargados del gobierno
│   └── produccion.parquet  # Base de datos maestra optimizada
│
├── src/                    # Backend de Datos (ETL)
│   ├── __init__.py
│   ├── renamer.py          # Estandarización de nombres de archivos crudos
│   ├── data_builder.py     # Construcción inicial de la base de datos
│   ├── updater.py          # Actualización incremental (mes a mes)
│   └── cleaner.py          # Clase OGDDataCleaner (Filtrado de Vaca Muerta)
│
├── notebooks/              # Análisis Exploratorio de Datos (EDA)
│   └── 01_exploracion.ipynb
│
├── app.py                  # Frontend: Dashboard interactivo de Streamlit
├── requirements.txt        # Dependencias del proyecto
└── README.md               # Documentación
```

## CÓMO EJECUTAR EL PROYECTO LOCALMENTE

### 1. Clonar el repositorio y entrar a la carpeta
git clone https://github.com/TU_USUARIO/vaca-muerta-analytics.git
cd vaca-muerta-analytics

### 2. Crear el entorno virtual
python -m venv venv

### 3. Activar el entorno virtual 
#### (NOTA: Usá el de Windows o el de Mac/Linux dependiendo de tu sistema)

#### -> Si usás Windows:
venv\Scripts\activate

##### -> Si usás Linux o Mac:
source venv/bin/activate

### 4. Instalar las dependencias necesarias
pip install -r requirements.txt

### 5. IMPORTANTE ANTES DE SEGUIR:
##### Descargá los CSV del "Capítulo IV" desde datos.gob.ar 
##### y guardalos dentro de la carpeta "data/raw/" de tu proyecto.

### 6. Construir la base de datos (Ejecutar el ETL)
python src/data_builder.py

### 7. Levantar la aplicación interactiva
streamlit run app.py