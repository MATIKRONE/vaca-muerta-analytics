import streamlit as st
import pandas as pd
from src.cleaner import OGDDataCleaner

# Configuración de la página
st.set_page_config(page_title = 'Monitor Vaca Muerta', layout = 'wide')

st.title('Monitor de Producción - Vaca Muerta')
st.markdown("Análisis de la producción no convencional de la Cuenca Neuquina.")

# Caché y carga de datos
# Usamos @st.cache_data para que Streamlit no vuelva a procesar el CSV pesado cada vez que tocamos un filtro
@st.cache_data
def cargar_datos():
    ruta = 'data/produccion.csv'
    limpiador = OGDDataCleaner(ruta)
    df = limpiador.load_data().filter_vaca_muerta().optimize_and_clean().get_processed_data()
    return df

with st.spinner('Cargando y limpiando datos...'):
    df_limpio = cargar_datos()

# Barra lateral para filtros
st.sidebar.header('Filtros')

# Obtenemos las empresas únicas y agregamos "Todas" como opción al principio
empresas_disponibles = ['Todas'] + df_limpio['empresa'].dropna().unique().tolist()
empresa_seleccionada = st.sidebar.selectbox('Selecciona una Empresa Operadora', empresas_disponibles)

# Filtramos el DataFrame según lo que elija el usuario
if empresa_seleccionada != 'Todas':
    df_filtrado = df_limpio[df_limpio['empresa'] == empresa_seleccionada]
else:
    df_filtrado = df_limpio

# Metricas principales
st.subheader(f"Métricas Generales: {empresa_seleccionada}")

col1, col2, col3 = st.columns(3)
with col1:
    total_pozos = df_filtrado['idpozo'].nunique()
    st.metric("Pozos Activos", total_pozos)
with col2:
    prod_total_pet = df_filtrado['prod_pet'].sum()
    # 1. Formateamos el número y cambiamos comas por puntos
    texto_petroleo = f"{prod_total_pet:,.0f}".replace(',', '.')
    st.metric("Producción Total Petróleo (m3)", texto_petroleo)
with col3:
    prod_total_gas = df_filtrado['prod_gas'].sum()
    texto_gas = f"{prod_total_gas:,.0f}".replace(',', '.')
    st.metric("Producción Total Gas (Mm3)", texto_gas)

# Gráficos
st.subheader("Top 10 Pozos Petroleros")
# Agrupamos por pozo y sumamos la producción de petróleo, luego ordenamos y tomamos los 10 primeros
top_pozos = df_filtrado.groupby('idpozo')['prod_pet'].sum().sort_values(ascending=False).head(10)

# Tabla cruda (Opcional para inspección)
with st.expander("Ver tabla de datos limpios"):
    st.dataframe(df_filtrado.head(100))