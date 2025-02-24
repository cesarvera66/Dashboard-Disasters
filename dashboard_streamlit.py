import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------------------------------------
# 1) CONFIGURACIÓN DE LA PÁGINA
# ----------------------------------------------------------------
st.set_page_config(page_title="Dashboard de Desastres Naturales", layout="wide")

# Encabezado
st.title("Dashboard de Desastres Naturales")
st.markdown("**Descripción:** Análisis de impacto social y económico de desastres naturales ocurridos a nivel Global.")

# ----------------------------------------------------------------
# 2) CARGA Y LIMPIEZA DE DATOS
# ----------------------------------------------------------------
@st.cache_data
def cargar_datos():
    """Carga y limpia los datos del archivo Excel."""
    try:
        file_path = "C:/Users/Cesar/Downloads/emdat-country-profiles_2025_01_27.xlsx"
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

    # Métricas
    m1, m2, m3, m4 = st.columns((1, 1, 1, 1))

    total_eventos = df_filtrado['Total Events'].sum()
    total_afectados = df_filtrado['Total Affected'].sum()
    total_muertes = df_filtrado['Total Deaths'].sum()
    total_danos = df_filtrado['Total Damage (USD, original)'].sum() / 1e6

    m1.metric(label="Total de Eventos", value=f"{total_eventos:,}")
    m2.metric(label="Personas Afectadas", value=f"{int(total_afectados):,}")
    m3.metric(label="Muertes Totales", value=f"{int(total_muertes):,}")
    m4.metric(label="Daños Totales (Millones USD)", value=f"{total_danos:.2f}")

# ----------------------------------------------------------------
# 4) GRÁFICOS
# ----------------------------------------------------------------
g1, g2, g3 = st.columns((1, 1, 1))

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
g1.plotly_chart(fig1, use_container_width=True)

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
g2.plotly_chart(fig2, use_container_width=True)

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
g3.plotly_chart(fig3, use_container_width=True)

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

st.plotly_chart(fig_combined, use_container_width=True)

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
cw1.plotly_chart(fig_tabla, use_container_width=True)

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
cw2.plotly_chart(fig_detalle, use_container_width=True)

# ----------------------------------------------------------------
# 6) SECCIÓN DE CONTACTO
# ----------------------------------------------------------------
