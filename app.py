import streamlit as st
import pandas as pd
import altair as alt
from src.cleaner import OGDDataCleaner
from pathlib import Path
import gdown

# DESCARGA DE DATOS DESDE GOOGLE DRIVE
URL_DRIVE = f'https://drive.google.com/file/d/11yBjYystY3xkZ4JUse2feT1jqDksIshy/view?usp=sharing'

ruta_datos = Path('data/produccion.parquet')

# Si la carpeta 'data' no existe, la crea
ruta_datos.parent.mkdir(parents=True, exist_ok=True)

# Si el archivo parquet no existe en el sistema, lo descarga de Drive
if not ruta_datos.exists():
    with st.spinner('☁️ Descargando base de datos desde Google Drive (esto tomará 1 o 2 minutos solo la primera vez)...'):
        gdown.download(URL_DRIVE, str(ruta_datos), quiet=False)
        st.success('¡Datos descargados con éxito!')

# ==========================================
# 2. CARGA DE DATOS (El código que ya tenías)
# ==========================================
@st.cache_data
def cargar_datos():
    # Asegurate de que la ruta coincida con la que acabamos de usar
    return pd.read_parquet(ruta_datos)
    
df = cargar_datos()

# (A partir de acá sigue el resto de tu código normal de filtros y pestañas...)

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



# CREADOR DE PESTAÑAS
tab1, tab2, tab3 = st.tabs([
    "📊 1. Resumen Ejecutivo", 
    "📈 2. Dinámica de Producción", 
    "🔬 3. Salud del Reservorio"
])

# PESTAÑA 1: VISIÓN DE NEGOCIO Y LIDERAZGO
with tab1:
    st.subheader("Panorama General")
    
    # KPIs Comerciales (solo 3 columnas para no abrumar)
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    pet = df_filtrado['prod_pet'].sum()
    gas = df_filtrado['prod_gas'].sum()
    
    col_kpi1.metric("Pozos Activos", f"{df_filtrado['idpozo'].nunique():,}".replace(",", "."))
    col_kpi2.metric("Petróleo Acumulado (m³)", f"{pet:,.0f}".replace(",", "."))
    col_kpi3.metric("Gas Acumulado (Mm³)", f"{gas:,.0f}".replace(",", "."))
    
    st.divider()
    
    # Gráficos de Negocio uno al lado del otro
    col_negocio1, col_negocio2 = st.columns(2)
    
    with col_negocio1:
        # 1. MARKET SHARE (Gráfico de Dona) - Filtrado al Top 5
        df_market = df_filtrado.groupby('empresa')['prod_pet'].sum().reset_index()
        # Ordenamos de mayor a menor y nos quedamos con las 5 principales
        df_market = df_market.sort_values(by='prod_pet', ascending=False).head(5)
        # Limpiamos los ceros
        df_market = df_market[df_market['prod_pet'] > 0]
        
        grafico_dona = alt.Chart(df_market).mark_arc(innerRadius=60).encode(
            theta=alt.Theta(field="prod_pet", type="quantitative"),
            color=alt.Color(
                field="empresa", 
                type="nominal", 
                sort=alt.EncodingSortField(field="prod_pet", order="descending"),
                legend=alt.Legend(title="Operadora")
            ),
            # ¡Acá está la magia! Le decimos a Altair que ordene las porciones del gráfico
            order=alt.Order(field="prod_pet", type="quantitative", sort="descending"),
            tooltip=[
                alt.Tooltip('empresa', title='Empresa'), 
                alt.Tooltip('prod_pet', title='Petróleo (m³)', format=',.0f')
            ]
        ).properties(
            height=350, 
            title='Market Share: Top 5 Operadoras (Petróleo)'
        )
        st.altair_chart(grafico_dona, use_container_width=True)

    with col_negocio2:
        # Top 10 Pozos (Barras)
        top_pozos = df_filtrado.groupby(['sigla', 'empresa'])['prod_pet'].sum().reset_index().sort_values(by='prod_pet', ascending=False).head(10)
        grafico_barras = alt.Chart(top_pozos).mark_bar(cornerRadiusEnd=4).encode(
            x=alt.X('prod_pet:Q', title='Producción (m³)', axis=alt.Axis(format='~s')),
            y=alt.Y('sigla:N', title='Pozo', sort='-x'),
            color=alt.Color('empresa:N', legend=None),
            tooltip=[alt.Tooltip('sigla', title='Pozo'), alt.Tooltip('prod_pet', title='Petróleo', format=',.0f')]
        ).properties(height=350, title='Top 10 Pozos (Petróleo)')
        st.altair_chart(grafico_barras, use_container_width=True)

# PESTAÑA 2: ANÁLISIS OPERATIVO
with tab2:
    st.subheader("Comportamiento Histórico y Perfil de Fluidos")
    
    # Evolución Temporal
    df_temporal = df_filtrado.groupby('fecha')[['prod_pet', 'prod_gas']].sum().reset_index()
    df_melted = df_temporal.melt(id_vars=['fecha'], var_name='Tipo', value_name='Producción (m³)')
    df_melted['Tipo'] = df_melted['Tipo'].map({'prod_pet': 'Petróleo', 'prod_gas': 'Gas'})
    
    grafico_temporal = alt.Chart(df_melted).mark_line(point=True).encode(
        x=alt.X('fecha:T', title='Fecha'),
        y=alt.Y('Producción (m³):Q', title='Producción Mensual'),
        color=alt.Color('Tipo:N', title='Fluido', scale=alt.Scale(domain=['Petróleo', 'Gas'], range=['#2ca02c', '#1f77b4'])),
        tooltip=[alt.Tooltip('fecha:T', title='Mes', format='%Y-%m'), alt.Tooltip('Tipo:N'), alt.Tooltip('Producción (m³):Q', format=',.0f')]
    ).properties(height=350, title='Evolución de Producción (Mensual)').interactive()
    
    st.altair_chart(grafico_temporal, use_container_width=True)
    
    # Scatter Plot
    df_dispersion = df_filtrado.groupby(['sigla', 'areayacimiento'])[['prod_pet', 'prod_gas']].sum().reset_index()
    
    top_5_yacimientos = df_dispersion['areayacimiento'].value_counts().head(5).index.tolist()
    df_dispersion_top = df_dispersion[df_dispersion['areayacimiento'].isin(top_5_yacimientos)]
    
    grafico_scatter = alt.Chart(df_dispersion_top).mark_circle(size=60, opacity=0.6).encode(
        x=alt.X('prod_pet:Q', title='Petróleo Acumulado (m³)', scale=alt.Scale(type='symlog')),
        y=alt.Y('prod_gas:Q', title='Gas Acumulado (Mm³)', scale=alt.Scale(type='symlog')),
        color=alt.Color(
            'areayacimiento:N', 
            # ¡Acá está el truco! labelLimit=0 evita que Altair corte los nombres
            legend=alt.Legend(title="Yacimiento (Top 5)", labelLimit=0)
        ),
        tooltip=[
            alt.Tooltip('sigla', title='Pozo'), 
            alt.Tooltip('areayacimiento', title='Yacimiento'), 
            alt.Tooltip('prod_pet', format=',.0f'), 
            alt.Tooltip('prod_gas', format=',.0f')
        ]
    ).properties(
        height=350, 
        title='Perfil de Fluidos por Pozo (Top 5 Yacimientos)'
    ).interactive()
    
    st.altair_chart(grafico_scatter, use_container_width=True)

# PESTAÑA 3: INGENIERÍA DE RESERVORIOS
with tab3:
    st.subheader("Indicadores Técnicos de Madurez del Yacimiento")
    st.markdown("Análisis del *Flowback* inicial y transición estratégica (Tight Gas a Shale Oil).")
    
    # KPIs de Ingeniería
    agua_total = df_filtrado['prod_agua'].sum()
    liquido_total = pet + agua_total
    water_cut = (agua_total / liquido_total) * 100 if liquido_total > 0 else 0
    gor = (gas * 1000 / pet) if pet > 0 else 0
    
    col_ing1, col_ing2 = st.columns(2)
    col_ing1.metric("Water Cut Promedio Histórico", f"{water_cut:.1f}%")
    col_ing2.metric("GOR Promedio Histórico", f"{gor:.0f} m³/m³")
    
    st.divider()
    
    # Gráficos de Ingeniería
    df_kpi_temporal = df_filtrado.groupby('fecha')[['prod_pet', 'prod_gas', 'prod_agua']].sum().reset_index()
    df_kpi_temporal['Liquido_Total'] = df_kpi_temporal['prod_pet'] + df_kpi_temporal['prod_agua']
    df_kpi_temporal['Water Cut (%)'] = df_kpi_temporal.apply(lambda x: (x['prod_agua'] / x['Liquido_Total'] * 100) if x['Liquido_Total'] > 0 else 0, axis=1)
    df_kpi_temporal['GOR (m³/m³)'] = df_kpi_temporal.apply(lambda x: (x['prod_gas'] * 1000 / x['prod_pet']) if x['prod_pet'] > 0 else 0, axis=1)
    
    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        grafico_wc = alt.Chart(df_kpi_temporal).mark_area(opacity=0.6, color='#17becf').encode(
            x=alt.X('fecha:T', title='Fecha'),
            y=alt.Y('Water Cut (%):Q', title='Water Cut (%)', scale=alt.Scale(zero=False)),
            tooltip=[alt.Tooltip('fecha:T', format='%Y-%m'), alt.Tooltip('Water Cut (%):Q', format='.1f')]
        ).properties(height=300, title='Evolución del Corte de Agua (Water Cut)').interactive()
        st.altair_chart(grafico_wc, use_container_width=True)
        
    with col_graf2:
        grafico_gor = alt.Chart(df_kpi_temporal).mark_line(color='#ff7f0e', strokeWidth=3).encode(
            x=alt.X('fecha:T', title='Fecha'),
            y=alt.Y('GOR (m³/m³):Q', title='GOR (m³/m³)', scale=alt.Scale(zero=False)),
            tooltip=[alt.Tooltip('fecha:T', format='%Y-%m'), alt.Tooltip('GOR (m³/m³):Q', format='.0f')]
        ).properties(height=300, title='Evolución de Relación Gas-Petróleo (GOR)').interactive()
        st.altair_chart(grafico_gor, use_container_width=True)