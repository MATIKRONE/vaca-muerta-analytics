import streamlit as st
import pandas as pd
import altair as alt
from src.cleaner import OGDDataCleaner
from pathlib import Path

# Configuración de la página
st.set_page_config(page_title='Monitor Vaca Muerta', layout='wide', page_icon='🛢️')

st.title('Monitor de Producción - Vaca Muerta')
st.markdown("Análisis avanzado y salud de reservorios de la Cuenca Neuquina (Producción No Convencional).")

# Caché y carga de datos
@st.cache_data
def cargar_datos() -> pd.DataFrame:
    ruta = Path('data/produccion.parquet')
    if not ruta.exists():
        st.error("No se encontró la base de datos. Ejecutá data_builder.py primero.")
        st.stop()
        
    limpiador = OGDDataCleaner(ruta)
    df = limpiador.load_data().filter_vaca_muerta().optimize_and_clean().get_processed_data()
    return df

with st.spinner('Cargando y limpiando datos...'):
    df_limpio = cargar_datos()

# Barra lateral para filtros
st.sidebar.header('Panel de Control')

# Filtro 1: Rango de años (Slider)
anio_min, anio_max = int(df_limpio['anio'].min()), int(df_limpio['anio'].max())

if anio_min == anio_max:
    st.sidebar.info(f"📅 Mostrando datos del año {anio_min}")
    rango_anios = (anio_min, anio_max)
else:
    rango_anios = st.sidebar.slider("Rango Temporal", anio_min, anio_max, (anio_min, anio_max))

# Filtro 2: Empresa
empresas_disponibles = ["Todas"] + sorted(df_limpio['empresa'].unique().tolist())
empresa_seleccionada = st.sidebar.selectbox("Operadora", empresas_disponibles)

# Aplicamos filtros 1 y 2
mask_anios = (df_limpio['anio'] >= rango_anios[0]) & (df_limpio['anio'] <= rango_anios[1])
if empresa_seleccionada != "Todas":
    mask_empresa = df_limpio['empresa'] == empresa_seleccionada
    df_filtrado = df_limpio[mask_anios & mask_empresa]
else:
    df_filtrado = df_limpio[mask_anios]

# Filtro 3: Yacimiento
pozos_por_area = df_filtrado.groupby('areayacimiento')['idpozo'].nunique().sort_values(ascending=False)
opciones_yacimientos = [f"{area} ({pozos} pozos)" for area, pozos in pozos_por_area.items()]
yacimientos_disponibles = ["Todos"] + opciones_yacimientos

yacimiento_seleccionado = st.sidebar.selectbox("Área / Yacimiento", yacimientos_disponibles)

if yacimiento_seleccionado != "Todos":
    area_limpia = yacimiento_seleccionado.rsplit(" (", 1)[0]
    df_filtrado = df_filtrado[df_filtrado['areayacimiento'] == area_limpia]

# Validación: Si los filtros dejan el df vacío, frenamos la app amablemente
if df_filtrado.empty:
    st.warning("No hay datos de producción para los filtros seleccionados.")
    st.stop()



# SECCIÓN 1: MÉTRICAS Y KPIS
st.subheader("Indicadores Principales")

col1, col2, col3, col4, col5 = st.columns(5)

pet = df_filtrado['prod_pet'].sum()
gas = df_filtrado['prod_gas'].sum()
agua_total = df_filtrado['prod_agua'].sum()
liquido_total = pet + agua_total

water_cut = (agua_total / liquido_total) * 100 if liquido_total > 0 else 0
gor = (gas * 1000 / pet) if pet > 0 else 0

with col1:
    st.metric("Pozos Activos", f"{df_filtrado['idpozo'].nunique():,}".replace(",", "."))
with col2:
    st.metric("Petróleo (m³)", f"{pet:,.0f}".replace(",", "."))
with col3:
    st.metric("Gas (Mm³)", f"{gas:,.0f}".replace(",", "."))
with col4:
    st.metric("Water Cut", f"{water_cut:.1f}%", help="Menor es mejor.")
with col5:
    st.metric("GOR", f"{gor:.0f}", help="m³ gas / m³ petróleo.")

st.divider()



# SECCIÓN 2: EVOLUCIÓN TEMPORAL (La magia de las series de tiempo)
st.subheader("Evolución de la Producción")

# Agrupamos por fecha y sumamos
df_temporal = df_filtrado.groupby('fecha')[['prod_pet', 'prod_gas']].sum().reset_index()

# Necesitamos "derretir" (melt) el dataframe para que Altair pueda graficar ambas líneas juntas
df_melted = df_temporal.melt(id_vars=['fecha'], var_name='Tipo', value_name='Producción (m³)')
# Renombramos para la leyenda
df_melted['Tipo'] = df_melted['Tipo'].map({'prod_pet': 'Petróleo', 'prod_gas': 'Gas'})

grafico_temporal = alt.Chart(df_melted).mark_line(point=True).encode(
    x=alt.X('fecha:T', title='Fecha'),
    y=alt.Y('Producción (m³):Q', title='Producción Mensual'),
    color=alt.Color('Tipo:N', title='Fluido', scale=alt.Scale(domain=['Petróleo', 'Gas'], range=['#2ca02c', '#1f77b4'])),
    tooltip=[
        alt.Tooltip('fecha:T', title='Mes', format='%Y-%m'),
        alt.Tooltip('Tipo:N', title='Fluido'),
        alt.Tooltip('Producción (m³):Q', title='Volumen', format=',.0f')
    ]
).properties(height=350).interactive() # .interactive() permite hacer zoom y paneo

st.altair_chart(grafico_temporal, use_container_width=True)

st.divider()



# SECCIÓN 3: RANKING DE POZOS
st.subheader("Top 10 Pozos por Producción de Petróleo Acumulada")

top_pozos = df_filtrado.groupby(['sigla', 'empresa'])['prod_pet'].sum().reset_index()
top_pozos = top_pozos.sort_values(by='prod_pet', ascending=False).head(10)

grafico_barras = alt.Chart(top_pozos).mark_bar(cornerRadiusEnd=4).encode( # Esquinas redondeadas
    x=alt.X('prod_pet:Q', title='Producción Total (m³)', axis=alt.Axis(format='~s')),
    y=alt.Y('sigla:N', title='Pozo', sort='-x'), 
    color=alt.Color('empresa:N', legend=alt.Legend(title="Operadora", orient="bottom")),
    tooltip=[
        alt.Tooltip('sigla', title='Pozo'), 
        alt.Tooltip('empresa', title='Empresa'),
        alt.Tooltip('prod_pet', title='Producción (m³)', format=',.0f')
    ]
).properties(height=400)

st.altair_chart(grafico_barras, use_container_width=True)



# SECCIÓN 4: ANÁLISIS DE RESERVORIO (WATER CUT Y GOR TEMPORAL)
st.subheader("Análisis de Reservorio: Evolución de KPIs Técnicos")
st.markdown("Observá cómo el *Flowback* inicial y el cambio estratégico hacia el Shale Oil afectaron las métricas históricas.")

# Agrupamos por fecha para calcular los KPIs mes a mes
df_kpi_temporal = df_filtrado.groupby('fecha')[['prod_pet', 'prod_gas', 'prod_agua']].sum().reset_index()

# Calculamos el Liquido Total para evitar errores de división por cero
df_kpi_temporal['Liquido_Total'] = df_kpi_temporal['prod_pet'] + df_kpi_temporal['prod_agua']

# Calculamos Water Cut (%) mes a mes
df_kpi_temporal['Water Cut (%)'] = df_kpi_temporal.apply(
    lambda x: (x['prod_agua'] / x['Liquido_Total'] * 100) if x['Liquido_Total'] > 0 else 0, axis=1
)

# Calculamos GOR (m3/m3) mes a mes
df_kpi_temporal['GOR (m³/m³)'] = df_kpi_temporal.apply(
    lambda x: (x['prod_gas'] * 1000 / x['prod_pet']) if x['prod_pet'] > 0 else 0, axis=1
)

# Creamos el gráfico de Water Cut (Tipo Área para que se vea como un volumen)
grafico_wc = alt.Chart(df_kpi_temporal).mark_area(opacity=0.6, color='#17becf').encode(
    x=alt.X('fecha:T', title='Fecha'),
    y=alt.Y('Water Cut (%):Q', title='Water Cut (%)', scale=alt.Scale(zero=False)),
    tooltip=[
        alt.Tooltip('fecha:T', title='Mes', format='%Y-%m'), 
        alt.Tooltip('Water Cut (%):Q', title='Water Cut', format='.1f')
    ]
).properties(height=300, title='Evolución del Corte de Agua (Water Cut)').interactive()

# Creamos el gráfico de GOR (Línea)
grafico_gor = alt.Chart(df_kpi_temporal).mark_line(color='#ff7f0e', strokeWidth=3).encode(
    x=alt.X('fecha:T', title='Fecha'),
    y=alt.Y('GOR (m³/m³):Q', title='GOR (m³/m³)', scale=alt.Scale(zero=False)),
    tooltip=[
        alt.Tooltip('fecha:T', title='Mes', format='%Y-%m'), 
        alt.Tooltip('GOR (m³/m³):Q', title='GOR', format='.0f')
    ]
).properties(height=300, title='Evolución de la Relación Gas-Petróleo (GOR)').interactive()

# Mostramos los gráficos uno al lado del otro
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.altair_chart(grafico_wc, use_container_width=True)
with col_graf2:
    st.altair_chart(grafico_gor, use_container_width=True)