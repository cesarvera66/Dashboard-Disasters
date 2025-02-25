# Desastres Naturales: Análisis Global del Impacto

Dashboard interactivo para el análisis y visualización de datos sobre desastres naturales a nivel mundial. Este proyecto proporciona una plataforma completa para explorar y comprender el impacto social y económico de los desastres naturales.

## Características Principales

📊 **Visualizaciones Interactivas**
- Gráficos de distribución de tipos de desastres
- Análisis temporal de eventos
- Mapas de distribución geográfica
- Relaciones entre variables clave

📈 **Análisis Detallado**
- Total de eventos por región
- Personas afectadas y muertes
- Daños económicos estimados
- Tendencias históricas
- Comparativas temporales

🔍 **Filtros Interactivos**
- Selección de país
- Rango de años
- Tipo de desastre
- Períodos de comparación

## Instalación

Para ejecutar el dashboard localmente:

```bash
# Clonar el repositorio
git clone https://github.com/cesarvera66/Dashboard-Disasters.git

# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el dashboard
streamlit run app.py
```

## Requisitos del Sistema

- Python 3.8+
- Streamlit 1.20+
- Pandas 1.4+
- Plotly 5.10+
- Numpy 1.22+

## Fuente de Datos

El dashboard utiliza datos del [EM-DAT (Emergency Events Database)](https://www.emdat.be/), mantenido por el Centro para la Investigación sobre Epidemiología de Desastres (CRED).

## Métricas Principales

- **Total de Eventos**: Número de desastres registrados
- **Personas Afectadas**: Suma de personas reportadas como afectadas
- **Muertes Totales**: Número de muertes directamente atribuidas
- **Daños Totales**: Estimación en millones de USD

## Visualizaciones

1. **Distribución de Tipos de Desastres**
- Gráfico de barras para tipos de desastres
- Análisis de frecuencia

2. **Daños Económicos**
- Gráfico circular de daños por tipo
- Comparativas temporales

3. **Evolución Temporal**
- Líneas de tendencia
- Análisis histórico

4. **Análisis Geográfico**
- Mapa mundial de eventos
- Distribución por región

## Contribuciones

Para contribuir al proyecto:

1. Fork del repositorio
2. Crear una nueva rama
3. Realizar los cambios
4. Abrir pull request

## Licencia

Este proyecto está bajo la licencia [MIT](LICENSE).

## Contacto

Cesar Vera
- Correo: [cesarvera6@gmail.com](mailto:cesarvera6@gmail.com)
- Portafolio: [https://cesarvera66.github.io/portfolio_cesarvera/](https://cesarvera66.github.io/portfolio_cesarvera/)