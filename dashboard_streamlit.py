import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------------------------------------
# 1) CONFIGURACIÓN DE LA PÁGINA
# ----------------------------------------------------------------
st.set_page_config(page_title="Desastres Naturales: Análisis Global del Impacto", layout="wide")

# Encabezado
st.title("Desastres Naturales: Análisis del Impacto Global")
st.markdown("**Descripción:** Este dashboard ofrece una visión global y dinámica del impacto social y económico de los desastres naturales a nivel mundial. A través de la exploración interactiva de datos.")

# ----------------------------------------------------------------
# 2) CARGA Y LIMPIEZA DE DATOS
# ----------------------------------------------------------------
@st.cache_data
def cargar_datos():
    """Carga y limpia los datos del archivo Excel."""
    try:
        file_path = "data/emdat-country-profiles_2025_01_27.xlsx"
        df = pd.read_excel(file_path, sheet_name='EM-DAT Version 2025-01-27')

        # Limpiar nombres de columnas
        df.columns = df.columns.str.strip()

        # Seleccionar columnas necesarias
        columnas_necesarias = [
            'Year', 'Country', 'ISO', 'Disaster Group', 'Disaster Subgroup',
            'Disaster Type', 'Disaster Subtype', 'Total Events', 'Total Affected',
            'Total Deaths', 'Total Damage (USD, original)', 'Total Damage (USD, adjusted)',
            'CPI'
        ]
        df = df[[col for col in columnas_necesarias if col in df.columns]]

        # Eliminar filas con NaN en columnas clave
        df = df.dropna(subset=['Year', 'Disaster Type', 'ISO', 'Country', 'Total Events'])

        # Convertir tipos de datos
        df['Year'] = df['Year'].astype(int)
        df['Total Events'] = df['Total Events'].astype(int)
        df['Total Affected'] = pd.to_numeric(df['Total Affected'], errors='coerce')
        df['Total Deaths'] = pd.to_numeric(df['Total Deaths'], errors='coerce')
        df['Total Damage (USD, original)'] = pd.to_numeric(df['Total Damage (USD, original)'], errors='coerce')
        df['Total Damage (USD, adjusted)'] = pd.to_numeric(df['Total Damage (USD, adjusted)'], errors='coerce')
        df['CPI'] = pd.to_numeric(df['CPI'], errors='coerce')

        return df

    except Exception as e:
        st.error(f"Error al cargar los datos: {str(e)}")
        return None

# Cargar datos
df = cargar_datos()
if df is None:
    st.stop()

# ----------------------------------------------------------------
# 3) FILTROS
# ----------------------------------------------------------------
with st.spinner("Actualizando reporte..."):
    # Crear columnas para los filtros
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        hosp_df = sorted(df['Country'].unique())
        hosp = st.selectbox("País:", ["Todos los países"] + hosp_df, help="Filtrar por país específico")

    with col2:
        lista_anios = sorted(df['Year'].unique())
        anio_inicio = st.selectbox("Fecha inicio:", lista_anios, index=lista_anios.index(2000), help="Selecciona el año inicial")

    with col3:
        anio_fin = st.selectbox("Fecha final:", lista_anios, index=lista_anios.index(2024), help="Selecciona el año final")

    with col4:
        lista_tipos = ['Todos los desastres'] + sorted(df['Disaster Type'].unique())
        tipo_desastre = st.selectbox("Tipo de desastre:", lista_tipos, index=0, help="Selecciona el tipo de desastre")

    # Función para filtrar datos
    def filtrar_df(df, pais, anio_inicio, anio_fin, tipo_desastre):
        df_filtrado = df.copy()
        if pais != "Todos los países":
            df_filtrado = df_filtrado[df_filtrado['Country'] == pais]
        df_filtrado = df_filtrado[(df_filtrado['Year'] >= anio_inicio) & (df_filtrado['Year'] <= anio_fin)]
        if tipo_desastre != "Todos los desastres":
            df_filtrado = df_filtrado[df_filtrado['Disaster Type'] == tipo_desastre]
        return df_filtrado

    # Filtrar datos según los filtros seleccionados
    df_filtrado = filtrar_df(df, hosp, anio_inicio, anio_fin, tipo_desastre)
#------------------------------------------------------------------------------------------------------------
    # Métricas
    # 1) Calcular métricas del rango seleccionado
total_eventos = df_filtrado['Total Events'].sum()
total_afectados = df_filtrado['Total Affected'].sum()
total_muertes = df_filtrado['Total Deaths'].sum()
total_danos = df_filtrado['Total Damage (USD, original)'].sum() / 1e6

# 2) Calcular métricas del rango anterior (por ejemplo, hasta el año anterior)
if anio_fin > anio_inicio:
    df_filtrado_prev = filtrar_df(df, hosp, anio_inicio, anio_fin - 1, tipo_desastre)
    prev_eventos = df_filtrado_prev['Total Events'].sum()
    prev_afectados = df_filtrado_prev['Total Affected'].sum()
    prev_muertes = df_filtrado_prev['Total Deaths'].sum()
    prev_danos = df_filtrado_prev['Total Damage (USD, original)'].sum() / 1e6
else:
    # Si no hay período anterior, asumimos 0 para evitar errores
    prev_eventos = 0
    prev_afectados = 0
    prev_muertes = 0
    prev_danos = 0

# 3) Calcular deltas
delta_eventos = total_eventos - prev_eventos
delta_afectados = total_afectados - prev_afectados
delta_muertes = total_muertes - prev_muertes
delta_danos = total_danos - prev_danos

# Función para forzar el cero a verde (colocando un valor negativo muy pequeño)
def force_green_if_zero(delta_value):
    if delta_value == 0:
        # Forzamos un valor negativo diminuto para que se pinte de verde
        return -0.000001
    else:
        return delta_value

# 4) Mostrar métricas con flechas
m1, m2, m3, m4 = st.columns((1, 1, 1, 1))

m1.metric(
    label="Total de Eventos",
    value=f"{total_eventos:,}",
    delta=f"{force_green_if_zero(delta_eventos):+,.0f}",
    delta_color="inverse"  # Rojo si sube, verde si baja o ~0
)

m2.metric(
    label="Personas Afectadas",
    value=f"{int(total_afectados):,}",
    delta=f"{force_green_if_zero(delta_afectados):+,.0f}",
    delta_color="inverse"
)

m3.metric(
    label="Muertes Totales",
    value=f"{int(total_muertes):,}",
    delta=f"{force_green_if_zero(delta_muertes):+,.0f}",
    delta_color="inverse"
)

m4.metric(
    label="Daños Totales (Millones USD)",
    value=f"{total_danos:.2f}",
    delta=f"{force_green_if_zero(delta_danos):+.2f}",
    delta_color="inverse"
)
# 5) descripcion de metricas
st.caption(
    "Estas métricas ofrecen una visión rápida del impacto de los desastres en términos de frecuencia (eventos), "
    "magnitud humana (personas afectadas y muertes) y costos económicos (daños). Al compararlas con el período anterior, "
    "se pueden identificar tendencias de incremento o disminución"
)


# ----------------------------------------------------------------
# 4) GRÁFICOS
# ----------------------------------------------------------------
g1, g2, g3 = st.columns((1, 1, 1)) # Columnas agrupadas para los gráficos 1, 2 y 3
col1, col2 = st.columns([3, 2])    # Columnas agrupadas para los graficos 4 y 5

# Gráfico 1: Distribución de Tipos de Desastres
df_group_tipo = df_filtrado.groupby('Disaster Type', as_index=False)['Total Events'].sum().sort_values('Total Events', ascending=False)
fig1 = px.bar(
    df_group_tipo,
    x='Disaster Type',
    y='Total Events',
    title="Distribución de Tipos de Desastres",
    template='seaborn'
)
fig1.update_traces(marker_color='#264653')
fig1.update_layout(margin=dict(l=0, r=10, b=10, t=30), yaxis_title=None, xaxis_title=None)
with g1:
    st.plotly_chart(fig1.update_layout(xaxis={'fixedrange': True}, yaxis={'fixedrange': True}), use_container_width=True, config={'displayModeBar': False})
    st.caption("Análisis: Esta gráfica permite identificar cuáles son los tipos de desastres más frecuentes, facilitando el enfoque en estrategias de prevención y asignación de recursos.")


# Gráfico 2: Daños Económicos por Tipo de Desastre
df_group_danos = df_filtrado.groupby('Disaster Type', as_index=False)['Total Damage (USD, original)'].sum().sort_values('Total Damage (USD, original)', ascending=False)
fig2 = px.pie(
    df_group_danos,
    names='Disaster Type',
    values='Total Damage (USD, original)',
    hole=0.9,
    title="Daños Económicos por Tipo de Desastre",
    template='seaborn'
)
# Actualizar trazas para formatear los valores como dólares
fig2.update_traces(
    texttemplate='$%{value:,.0f}',
    hovertemplate='%{label}: $%{value:,.0f}<extra></extra>'
)
fig2.update_layout(margin=dict(l=0, r=10, b=10, t=30))
with g2:
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("Análisis: Esta gráfica circular muestra la distribución de los daños económicos entre los distintos tipos de desastres, permitiendo identificar cuáles generan mayor impacto económico.")


# Gráfico 3: Evolución de Eventos por Año
df_group_tiempo = df_filtrado.groupby('Year', as_index=False)['Total Events'].sum()
fig3 = px.line(
    df_group_tiempo,
    x='Year',
    y='Total Events',
    title="Evolución de Eventos por Año",
    template='seaborn'
)
fig3.update_traces(line_color='#7A9E9F')
fig3.update_layout(margin=dict(l=0, r=10, b=10, t=30), yaxis_title=None, xaxis_title=None)
with g3:
    st.plotly_chart(fig3.update_layout(xaxis={'fixedrange': True}, yaxis={'fixedrange': True}), use_container_width=True, config={'displayModeBar': False})
    st.caption("Análisis: Esta gráfica muestra la evolución en el tiempo de la cantidad total de eventos, permitiendo identificar tendencias y detectar años con mayor actividad de desastres para un análisis histórico y predictivo.")


# Gráfico 4: Total de Afectados por Año y Subgrupo de Desastre
# (1) Agrupar datos totales por año para las barras
df_year_total = df_filtrado.groupby('Year', as_index=False)['Total Affected'].sum()

# (2) Verificar existencia de la columna "Disaster Subgroup" o usar "Disaster Subtype"
if 'Disaster Subgroup' in df_filtrado.columns:
    grouping_column = 'Disaster Subgroup'
elif 'Disaster Type' in df_filtrado.columns:
    grouping_column = 'Disaster Type'
else:
    st.error("No se encontró una columna válida para el subgrupo de desastres.")
    st.stop()

# (3) Agrupar datos por año y por la columna seleccionada para las líneas
df_subgroup = df_filtrado.groupby(['Year', grouping_column], as_index=False)['Total Affected'].sum()

# (4) Crear figura combinada
fig_combined = go.Figure()

# (5) Agregar el rastro de barras para el total
fig_combined.add_trace(
    go.Bar(
        x=df_year_total['Year'],
        y=df_year_total['Total Affected'],
        name='Total Afectados',
        marker_color='lightgray',
        opacity=0.6  # Para que las líneas se vean mejor
    )
)

# (6) Agregar un rastro de línea por cada subgrupo
for subgroup in df_subgroup[grouping_column].unique():
    df_temp = df_subgroup[df_subgroup[grouping_column] == subgroup]
    fig_combined.add_trace(
        go.Scatter(
            x=df_temp['Year'],
            y=df_temp['Total Affected'],
            mode='lines+markers',
            name=subgroup
        )
    )

# (7) Ajustar diseño
fig_combined.update_layout(
    title='Total de Afectados por Año y Subgrupo de Desastre',
    xaxis_title='Año',
    yaxis_title='Total de Afectados',
    barmode='group',  # las barras se agrupan
    template='seaborn',
    legend_title='Subgrupo de Desastre',
    hovermode='x unified'
)

with col1:
    st.plotly_chart(fig_combined.update_layout(xaxis={'fixedrange': True}, yaxis={'fixedrange': True}), use_container_width=True, config={'displayModeBar': False})
    st.caption("Análisis: Esta gráfica combinada muestra el total de afectados por año con barras y, adicionalmente, desglosa la información por subgrupo (o tipo) de desastre mediante líneas. Esto permite identificar tendencias generales y evaluar la contribución específica de cada subgrupo en distintos períodos.")


# Gráfico 5 Sunburst: Muertes Totales por Subgrupo y Tipo
# 1) Agrupar datos 
df_sunburst = df_filtrado.groupby(
    ['Disaster Subgroup', 'Disaster Type'], 
    as_index=False
)['Total Deaths'].sum()

# 2) Crear el Sunburst con color continuo
fig_sunburst = px.sunburst(
    df_sunburst,
    path=['Disaster Subgroup', 'Disaster Type'],       # Jerarquía de anillos
    values='Total Deaths',             # Tamaño de cada sector
    color='Total Deaths',              # Campo numérico para el gradiente
    color_continuous_scale=px.colors.sequential.Plasma,# Escala de color (morado->amarillo)
    hover_data=['Total Deaths'],       # Datos en el hover
    title='Muertes Totales por Subgrupo y Tipo de Desastre'
)

# 3) Mostrarlo en Streamlit
with col2:
    st.plotly_chart(fig_sunburst, use_container_width=True)
    st.caption("Análisis: Esta visualización sunburst permite identificar, de forma jerárquica, cuáles subgrupos y tipos de desastres han generado la mayor cantidad de muertes, facilitando la detección de eventos con mayor impacto letal.")


# Grafico 6: 
fig_scatter = px.scatter(
    df_filtrado,
    x='Total Affected',
    y='Total Damage (USD, original)',
    color='Disaster Type',
    size='Total Events',
    hover_data=['Year', 'Country'],
    title="Relación entre Personas Afectadas y Daños Económicos"
)

st.plotly_chart(fig_scatter.update_layout(xaxis={'fixedrange': True}, yaxis={'fixedrange': True}), use_container_width=True, config={'displayModeBar': False})
st.caption("Análisis: Este gráfico de dispersión ilustra la relación entre el número de personas afectadas y los daños económicos. El tamaño de cada punto refleja el número de eventos y el color diferencia el tipo de desastre, facilitando la identificación de patrones y outliers para evaluar correlaciones entre los indicadores.")

# Grafico 7: Mapa estilo Ejemplo
df_mapa = df_filtrado.groupby('ISO', as_index=False)['Total Events'].sum()

fig_mapa = px.choropleth(
    df_mapa,
    locations='ISO',
    color='Total Events',
    hover_name=df_mapa['ISO'].map(df_filtrado.set_index('ISO')['Country'].to_dict()),
    color_continuous_scale=px.colors.diverging.Portland, # Escala de color tipo ejemplo (púrpura a amarillo)
    title='Total de Eventos de Desastres por País'
)

fig_mapa.update_geos(
    showland=True,     # Mostrar tierra
    landcolor="whitesmoke", # Color de la tierra (gris muy claro)
    showcoastlines=True, # Mostrar líneas costeras
    countrycolor="lightgray", # Color de las fronteras de países
)

fig_mapa.update_layout(
    margin=dict(l=0, r=0, b=0, t=30),
    
    
)

st.plotly_chart(fig_mapa, use_container_width=True)
st.caption("Análisis: Este mapa muestra la distribución geográfica del total de eventos de desastres por país, utilizando una escala de color divergente y destacando elementos geográficos para una visualización clara y tradicional.")

 
# ----------------------------------------------------------------
# 5) TABLAS
# ----------------------------------------------------------------
cw1, cw2 = st.columns((2.5, 1.7))

# Tabla 1: Resumen de Desastres por País
tabla_resumen = df_filtrado.groupby('Country', as_index=False).agg({
    'Total Events': 'sum',
    'Total Affected': 'sum',
    'Total Deaths': 'sum',
    'Total Damage (USD, original)': 'sum'
}).sort_values('Total Events', ascending=False)

fig_tabla = go.Figure(
    data=[go.Table(
        header=dict(
            values=list(tabla_resumen.columns),
            fill_color=None,
            font=dict(color='black', size=12),
            align='left'
        ),
        cells=dict(
            values=[tabla_resumen[col] for col in tabla_resumen.columns],
            fill_color=None,
            font=dict(color='black', size=12),
            align='left'
        )
    )]
)
fig_tabla.update_layout(
    title_text="Resumen de Desastres por País",
    title_x=0,
    margin=dict(l=0, r=10, b=10, t=30),
    height=480
)
with cw1:
    st.plotly_chart(fig_tabla, use_container_width=True)
    st.caption("Análisis: Esta tabla resume la cantidad total de eventos, personas afectadas, muertes y daños económicos por país, permitiendo identificar los países más vulnerables y priorizar esfuerzos de prevención y respuesta ante desastres.")


# Tabla 2: Detalle de Desastres Recientes
tabla_detalle = df_filtrado[['Country', 'Disaster Type', 'Year', 'Total Events', 'Total Affected']].sort_values('Year', ascending=False).head(10)

fig_detalle = go.Figure(
    data=[go.Table(
        header=dict(
            values=list(tabla_detalle.columns),
            fill_color=None,
            font=dict(color='black', size=12),
            align='left'
        ),
        cells=dict(
            values=[tabla_detalle[col] for col in tabla_detalle.columns],
            fill_color=None,
            font=dict(color='black', size=12),
            align='left'
        )
    )]
)
fig_detalle.update_layout(
    title_text="Detalle de Desastres Recientes",
    title_x=0,
    margin=dict(l=0, r=10, b=10, t=30),
    height=480
)
with cw2:
    st.plotly_chart(fig_detalle, use_container_width=True)
    st.caption("Análisis: Este detalle muestra los 10 desastres más recientes, facilitando la identificación rápida de eventos recientes y su impacto en términos de número de eventos y personas afectadas.")

# ----------------------------------------------------------------
# 6) BARRA LATERAL - DOCUMENTACIÓN Y ACERCA DE
# ----------------------------------------------------------------
with st.expander("Documentación y Acerca de"):

    st.write("**Disclaimer:**")
    st.markdown("""
        **Uso Responsable de la Información:**

        Este dashboard se proporciona con fines **informativos y educativos únicamente**.  El análisis presentado aquí es un resumen de datos disponibles públicamente sobre desastres naturales y **no debe ser interpretado como asesoramiento profesional** para la toma de decisiones en situaciones de emergencia real, planificación de riesgos, políticas públicas o cualquier otra aplicación crítica.

        **Limitaciones Inherentes:**

        * Los datos sobre desastres naturales, aunque valiosos, tienen **limitaciones inherentes** (como se detalla en la sección "Fuente de Datos").  La exhaustividad y precisión de los datos pueden variar.
        * Las visualizaciones y métricas presentadas son **interpretaciones basadas en los datos disponibles** y pueden no reflejar la complejidad total de los eventos de desastre ni todos los factores relevantes.
        * Este dashboard es una **herramienta de análisis exploratorio** y no reemplaza el juicio experto ni la consulta a fuentes de información oficiales y especializadas en gestión de riesgos y desastres.

        **Responsabilidad del Usuario:**

        El **uso de este dashboard y la interpretación de la información presentada son responsabilidad exclusiva del usuario**.  El creador de este dashboard no asume ninguna responsabilidad por las decisiones o acciones tomadas basándose en la información aquí contenida.

        **Para información oficial y actualizada sobre desastres naturales, siempre consulta fuentes gubernamentales y organizaciones especializadas reconocidas.**
    """, True) # True para permitir Markdown dentro de st.write


    st.write("\n***") # Separador visual

    st.write("**Fuente de Datos:**")
    st.markdown("""
        Este dashboard utiliza datos del **EM-DAT (Emergency Events Database)**,  gestionado por el Centro para la Investigación sobre Epidemiología de Desastres (CRED).

        **Fuente Específica:**  EM-DAT Public Database <br>
        **Versión:** Version 2025-01-27

        **Limitaciones de los Datos:**
        * EM-DAT se basa en datos reportados y puede haber **subregistro** de eventos, especialmente en regiones con menor capacidad de reporte o para desastres de menor escala.
        * Los **daños económicos** son estimados y pueden variar en metodología de cálculo entre diferentes fuentes y países.
        * La **calidad y exhaustividad** de los datos pueden variar según el país y el periodo de tiempo.
        * EM-DAT tiene **criterios específicos para la inclusión** de desastres en su base de datos (e.g., deben cumplir al menos uno de los siguientes: 10 o más personas muertas, 100 o más personas afectadas, declaración de estado de emergencia, llamamiento a asistencia internacional). Esto significa que algunos desastres de menor impacto podrían no estar incluidos.

        Para más información sobre la metodología de recolección de datos y las definiciones, consulta el sitio web oficial de EM-DAT: [https://www.emdat.be/](https://www.emdat.be/)
    """, True) # True para permitir Markdown dentro de st.write

    st.write("\n***") # Separador visual

    st.write("**Metodología de Análisis:**")
    st.markdown("""
        El análisis en este dashboard es principalmente **descriptivo y exploratorio**. Se utilizan visualizaciones (gráficos y mapas) y tablas resumen para:

        * **Describir la distribución** de los desastres por tipo, país y a lo largo del tiempo.
        * **Explorar la relación** entre diferentes variables como personas afectadas, muertes y daños económicos.
        * **Identificar tendencias** y patrones en los datos de desastres naturales a nivel global.

        Las métricas principales se calculan como **sumatorias** de los valores relevantes (eventos, afectados, muertes, daños) para los filtros seleccionados (país, rango de años, tipo de desastre).
    """)

    st.write("\n***") # Separador visual

    st.write("**Definiciones de Métricas Clave:**")
    st.markdown("""
        * **Total de Eventos:** Número total de desastres naturales registrados que cumplen los criterios de EM-DAT para el filtro seleccionado.
        * **Personas Afectadas:**  Suma del número de personas reportadas como afectadas por los desastres (incluye heridos, damnificados, personas que requieren asistencia inmediata, etc.) para el filtro seleccionado.
        * **Muertes Totales:** Suma del número de muertes directamente atribuidas a los desastres naturales para el filtro seleccionado.
        * **Daños Totales (Millones USD):** Suma estimada de los daños económicos directos causados por los desastres naturales, expresados en millones de dólares estadounidenses (USD original).
    """)

    st.write("\n***") # Separador visual

    st.write("**Creado por:**")
    st.markdown("""
        Cesar Vera <br>
        Analista de Datos <br>
        correo: cesarvera6@gmail.com <br>
        Portafolio: https://cesarvera66.github.io/portfolio_cesarvera/
    """, True) # True para permitir Markdown dentro de st.write
