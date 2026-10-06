# Monitor de Produccion - Vaca Muerta

Este repositorio contiene una aplicacion web interactiva desarrollada con Streamlit que procesa y visualiza datos publicos de produccion de petroleo y gas en Argentina, especificamente enfocada en los recursos no convencionales de la Cuenca Neuquina (Vaca Muerta).

El objetivo principal del proyecto fue construir un pipeline de datos estructurado utilizando programacion orientada a objetos (POO) para ingerir, limpiar y filtrar el dataset del "Capitulo IV" publicado por la Secretaria de Energia, el cual suele ser bastante pesado y requiere limpieza previa antes de su analisis.

## Stack tecnologico

* Python
* Pandas (procesamiento y limpieza de datos)
* Streamlit (interfaz grafica)

## Estructura del repositorio

El codigo esta separado para mantener la logica de limpieza aislada del frontend:

```text
vaca-muerta-analytics/
├── data/                   # Carpeta ignorada en git (aca va el CSV descargado)
├── notebooks/              # Pruebas y analisis exploratorio inicial
│   └── 01_exploracion.ipynb
├── src/                    # Logica principal
│   ├── __init__.py
│   └── cleaner.py          # Clase OGDDataCleaner con el pipeline de limpieza
├── app.py                  # Dashboard de Streamlit
├── requirements.txt        # Dependencias
└── README.md
```

## Como correr el proyecto localmente

1. Clonar el repositorio:
```bash
git clone https://github.com/TU_USUARIO/vaca-muerta-analytics.git
cd vaca-muerta-analytics
```

2. Crear y activar un entorno virtual:
```bash
python -m venv venv

# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

3. Instalar las dependencias necesarias:
```bash
pip install -r requirements.txt
```

4. Descargar los datos:
Por cuestiones de peso, el dataset original no esta incluido en el repositorio.
* Entrar a la pagina de Datos Abiertos de la Republica Argentina (datos.gob.ar).
* Buscar "Capitulo IV" y descargar el CSV llamado "Produccion de pozos de gas y petroleo con identificador".
* Guardar el archivo dentro de la carpeta `data/` y renombrarlo a `produccion.csv`.

5. Levantar la aplicacion:
```bash
streamlit run app.py
```
El dashboard se va a abrir automaticamente en el navegador en la direccion `http://localhost:8501`.

---

Creado por [Tu Nombre / Apellido]
[Link a tu LinkedIn o Portfolio]