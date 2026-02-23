# 📊 Panel de Inteligencia - Imagen de Calcio Neuronal

Panel interactivo de análisis de datos de imagen de calcio en células neuronales, desarrollado con Streamlit.

## 🌟 Características

- **Carga de Datos Flexible**: Sube tus propios archivos .txt y .csv o usa datos de ejemplo
- **Procesamiento Avanzado**: 
  - Suavizado con filtro Savitzky-Golay
  - Detección robusta de eventos con umbrales adaptativos
  - Baseline móvil con estimación robusta (MAD)
- **Métricas Automáticas**:
  - Área bajo la curva (total y primer minuto)
  - Máximo de respuesta
  - Duración de eventos
  - Tiempos de inicio y fin
- **Visualizaciones Interactivas**:
  - Señales con máscaras de estímulos
  - Comparación original vs suavizada
  - Detección de eventos en tiempo real
  - Heatmaps y análisis estadístico
- **Exportación de Resultados**: Descarga métricas en formato CSV

## 📁 Estructura del Proyecto

```
image_calcio/
├── app.py                      # Aplicación principal de Streamlit
├── config.py                   # Configuración global
├── requirements.txt            # Dependencias Python
├── README.md                   # Este archivo
├── utils/                      # Módulos de utilidades
│   ├── __init__.py
│   ├── data_processor.py      # Carga y procesamiento de datos
│   ├── signal_processing.py   # Procesamiento de señales
│   └── plotting.py            # Visualizaciones con Plotly
├── components/                 # Componentes de UI
│   ├── __init__.py
│   ├── sidebar.py             # Menú lateral
│   └── sections.py            # Secciones de contenido
├── Experimentos/              # Datos de experimentos
│   └── ID002_A_002/          # Ejemplo por defecto
│       ├── ID002_A_002.txt
│       └── estimulos.csv
├── notebooks/                 # Jupyter notebooks de referencia
│   └── imagen_calcio.ipynb
└── GUIA_ANALISIS_IMAGEN_CALCIO.md  # Documentación detallada
```

## 🚀 Instalación y Uso

### Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Paso 1: Instalar Dependencias

```bash
cd image_calcio
pip install -r requirements.txt
```

### Paso 2: Ejecutar la Aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

## 📖 Guía de Uso

### 1. Navegación

Usa el menú lateral para navegar entre secciones:
- **🏠 Inicio**: Visión general y características
- **📖 Origen**: Información sobre la fuente de datos
- **📊 Explicación**: Componentes de la señal y metodología
- **🔬 EDA**: Análisis exploratorio interactivo
- **💡 Conclusiones**: Hallazgos y recomendaciones

### 2. Carga de Datos

**Opción A: Usar Datos por Defecto**
- Marca "Usar archivos por defecto" en el sidebar
- Se cargará automáticamente ID002_A_002

**Opción B: Subir tus Propios Archivos**
- Desmarca "Usar archivos por defecto"
- Sube tu archivo .txt (registro de señales)
- Sube tu archivo .csv (información de estímulos)

### 3. Ajustar Parámetros

Expande las secciones en el sidebar para ajustar:

**Suavizado (Savitzky-Golay)**
- Tamaño de ventana (5-50, impar)
- Orden del polinomio (2-5)

**Detección de Eventos**
- Ventana baseline móvil (5-100)
- Factor umbral subida (0.5-5.0)
- Factor umbral bajada (0.5-5.0)
- Influencia (0.0-1.0)
- Puntos mínimos para unir eventos (2-30)

### 4. Filtros de Visualización

- **ROIs a visualizar**: Selecciona cuáles células analizar
- **Estímulos a analizar**: Filtra por estímulos de interés

### 5. Explorar Resultados en EDA

La sección de EDA contiene 4 pestañas:

1. **Señales Originales**: Visualiza señales con zonas de estímulos
2. **Preprocesamiento**: Compara original vs suavizada
3. **Detección de Eventos**: Ve umbrales adaptativos y eventos detectados
4. **Métricas y Resultados**: Analiza métricas calculadas y descarga resultados

## 📊 Formato de Datos

### Archivo de Registro (.txt)

```
VERSION	1200
Time[MSec.]	Ratio	Ratio	...
%.1f	%.4f	%.4f	...
Time	ROI(1-1)	ROI(1-2)	...
GraphNo	1	2	...
0.0	0.243900	0.196900	...
5095.5	0.248600	0.192200	...
...
```

- Columna 1: Tiempo en milisegundos
- Columnas 2+: Intensidad de fluorescencia para cada ROI

### Archivo de Estímulos (.csv)

```csv
;inicio;fin
depositos;3;20
soce;20;23
```

- Columna 1: Nombre del estímulo
- Columna 2: Tiempo de inicio (minutos)
- Columna 3: Tiempo de fin (minutos)

## 🔬 Metodología

### Procesamiento de Señal

1. **Suavizado**: Filtro Savitzky-Golay para reducir ruido preservando picos
2. **Baseline Móvil**: Cálculo continuo de mediana en ventana deslizante
3. **Variabilidad Robusta**: Estimación MAD (Median Absolute Deviation)
4. **Detección con Histéresis**: Umbrales adaptativos para subida/bajada
5. **Refinamiento Temporal**: Extensión de eventos hacia atrás y unión de fragmentos

### Cálculo de Métricas

Para cada ROI y estímulo:
- **Inicio**: Primer evento de subida después del inicio del estímulo
- **Fin**: Último evento de bajada antes del siguiente estímulo
- **Baseline Local**: Línea recta entre valor inicial y final
- **Señal Corregida**: Señal original menos baseline local

**Métricas**:
- AUC Total: ∫ señal_corregida dt
- AUC 1min: ∫ señal_corregida dt (primeros 60 segundos)
- Máximo: max(señal_corregida)
- Duración: tiempo_fin - tiempo_inicio

## 🎨 Personalización

### Modificar Configuración

Edita `config.py` para cambiar:
- Rutas por defecto
- Parámetros de procesamiento
- Colores de visualización
- Mensajes de la aplicación

### Agregar Nuevas Secciones

1. Crea función en `components/sections.py`
2. Agrega sección en `config.SECTIONS`
3. Incluye en `app.py` main()

### Personalizar Visualizaciones

Modifica `utils/plotting.py` para:
- Cambiar estilos de gráficos
- Agregar nuevos tipos de plots
- Ajustar layouts de Plotly

## 📝 Notas Técnicas

### Dependencias Principales

- **streamlit**: Framework de la aplicación web
- **pandas**: Manipulación de datos
- **numpy**: Operaciones numéricas
- **scipy**: Procesamiento de señales
- **plotly**: Visualizaciones interactivas

### Performance

- El procesamiento se realiza bajo demanda
- Los resultados se cachean en `st.session_state`
- Solo se reprocesa si cambian parámetros relevantes

### Session State

Variables guardadas en `st.session_state`:
- `data_loaded`: Estado de carga de datos
- `calcium_data`: DataFrame con señales
- `stimuli_data`: DataFrame con estímulos
- `processed_signals`: Señales procesadas por ROI
- `results_df`: DataFrame con métricas calculadas

## 🐛 Solución de Problemas

### Error al cargar archivos

- Verifica que los archivos tengan el formato correcto
- Asegúrate de usar separador `;` en CSV
- Revisa que el separador decimal sea `,` en CSV

### Procesamiento lento

- Reduce el número de ROIs seleccionadas
- Aumenta el tamaño de la ventana de suavizado
- Usa datos de ejemplo más pequeños

### Gráficos no se muestran

- Actualiza la página (F5)
- Verifica que Plotly esté instalado correctamente
- Prueba con otro navegador

## 📚 Referencias

- **Documentación de Análisis**: Ver `GUIA_ANALISIS_IMAGEN_CALCIO.md`
- **Notebook de Referencia**: `notebooks/imagen_calcio.ipynb`
- **Streamlit Docs**: https://docs.streamlit.io
- **Plotly Docs**: https://plotly.com/python/

## 🤝 Contribuciones

Para mejorar esta aplicación:

1. Identifica el módulo relevante
2. Implementa tu mejora
3. Documenta los cambios
4. Prueba exhaustivamente

## 📧 Contacto

Para preguntas o sugerencias sobre esta aplicación, contacta al equipo de desarrollo.

## 📄 Licencia

Este proyecto es software de investigación científica.

---

**Desarrollado con ❤️ para investigación en neurociencia**

Versión 1.0 - Febrero 2026
