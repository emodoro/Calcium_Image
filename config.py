"""
Configuración global de la aplicación de análisis de imagen de calcio.
Este archivo contiene constantes y configuraciones utilizadas en toda la aplicación.
"""

import os

# ========== RUTAS POR DEFECTO ==========
# Rutas de archivos por defecto para el análisis
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_EXPERIMENT_DIR = os.path.join(BASE_DIR, 'Experimentos', 'ID002_A_002')
DEFAULT_TXT_FILE = os.path.join(DEFAULT_EXPERIMENT_DIR, 'ID002_A_002.txt')
DEFAULT_CSV_FILE = os.path.join(DEFAULT_EXPERIMENT_DIR, 'estimulos.csv')

# ========== PARÁMETROS DE PROCESAMIENTO ==========
# Parámetros del filtro Savitzky-Golay para suavizado de señal
SG_WINDOW = 15          # Tamaño de ventana (debe ser impar)
SG_POLYORDER = 3        # Orden del polinomio

# Parámetros de filtrado por Transformada de Fourier (TF)
TF_FILTER_ENABLED = False
TF_FILTER_TYPE = 'bandpass'  # 'lowpass', 'highpass', 'bandpass', 'bandstop'
TF_CUTOFF_LOW_HZ = 0.02
TF_CUTOFF_HIGH_HZ = 0.30
TF_FILTER_ORDER = 4

# Señal usada para detección de eventos: 'sg', 'butterworth', 'original'
DETECTION_SIGNAL_SOURCE = 'sg'

# Parámetros para detección robusta de eventos en la señal
SIGNAL_WINDOW = 20      # Ventana para cálculo de baseline móvil
K_UP = 1.65             # Factor umbral para detección de subida
K_DOWN = 1.65           # Factor umbral para detección de bajada
INFLUENCE = 0.95        # Influencia del nuevo valor en baseline (0-1)
RUN_MIN = 10            # Puntos mínimos para unir eventos fragmentados

# Parámetros para detección por derivada
DERIVATIVE_WINDOW = 20  # Ventana para sigma local en derivada
DERIVATIVE_K = 1.65     # Factor umbral para derivada

# ========== VISUALIZACIÓN ==========
# Colores para diferentes estímulos en gráficos
STIMULUS_COLORS = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']

# Configuración de figuras por defecto
FIGURE_DPI = 100
FIGURE_WIDTH = 12
FIGURE_HEIGHT = 5

# ========== MÉTRICAS ==========
# Factor de conversión de milisegundos a minutos
MS_TO_MIN = 1000 * 60

# ========== INTERFAZ DE USUARIO ==========
# Títulos y descripciones de secciones
APP_TITLE = "📊 Panel de Inteligencia - Imagen de Calcio Neuronal"
APP_DESCRIPTION = """
Esta aplicación permite analizar datos de imagen de calcio en células neuronales,
identificando automáticamente eventos de activación y calculando métricas clave.
"""

# Nombres de secciones
SECTIONS = {
    'home': '🏠 Inicio',
    'origin': '📖 Origen de los Datos',
    'data_explanation': '📊 Explicación de la Data',
    'eda': '🔬 Análisis Exploratorio (EDA)',
    'spectral': '🎵 Análisis Espectral',
    'conclusions': '💡 Conclusiones'
}

# ========== CONFIGURACIÓN DE DATOS ==========
# Configuración para lectura del archivo .txt
TXT_SEPARATOR = '\t'        # Separador en archivo .txt
TXT_SKIPROWS = 3           # Filas a saltar en archivo .txt
TXT_HEADER = 1             # Fila de encabezados

# Configuración para lectura del archivo .csv
CSV_SEPARATOR = ';'        # Separador en archivo .csv
CSV_DECIMAL = ','          # Separador decimal en archivo .csv

# ========== VALIDACIÓN ==========
# Valores mínimos/máximos para parámetros
MIN_WINDOW = 5
MAX_WINDOW = 100
MIN_K_FACTOR = 0.5
MAX_K_FACTOR = 5.0
MIN_INFLUENCE = 0.0
MAX_INFLUENCE = 1.0

# ========== MENSAJES ==========
ERROR_MESSAGES = {
    'file_not_found': '❌ Archivo no encontrado. Por favor verifica la ruta.',
    'invalid_format': '❌ Formato de archivo inválido. Revisa el formato esperado.',
    'no_data': '❌ No se encontraron datos en el archivo.',
    'processing_error': '❌ Error durante el procesamiento. Revisa los parámetros.'
}

SUCCESS_MESSAGES = {
    'data_loaded': '✅ Datos cargados correctamente.',
    'processing_complete': '✅ Procesamiento completado con éxito.',
    'file_uploaded': '✅ Archivo subido correctamente.'
}

# ========== CONFIGURACIÓN DE PÁGINA ==========
PAGE_CONFIG = {
    'page_title': 'Análisis Imagen de Calcio',
    'page_icon': '🧬',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}
