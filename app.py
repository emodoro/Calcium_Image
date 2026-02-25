"""
Panel de Inteligencia - Análisis de Imagen de Calcio Neuronal
=============================================================

Aplicación de Streamlit para análisis interactivo de datos de imagen de calcio.

Autor: Desarrollado como panel de inteligencia científica
Fecha: Febrero 2026
Versión: 1.0

Características:
- Carga de archivos .txt (señales) y .csv (estímulos)
- Procesamiento automático con filtros adaptativos
- Detección robusta de eventos
- Cálculo de métricas clave
- Visualizaciones interactivas con Plotly
- Exportación de resultados

Estructura:
- config.py: Configuración global
- utils/: Módulos de procesamiento
- components/: Componentes de UI
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import tempfile
from pathlib import Path

# Importar configuración
from config import *

# Importar utilidades
from utils.data_processor import CalciumDataLoader, validate_uploaded_files
from utils.signal_processing import (
    SignalProcessor,
    calculate_stimulus_metrics,
    apply_butter_filter,
    estimate_sampling_rate
)
from utils.plotting import CalciumPlotter

# Importar componentes de UI
from components.sidebar import render_sidebar, show_data_summary
from components.sections import (
    render_home_section,
    render_origin_section,
    render_data_explanation_section,
    render_eda_section,
    render_spectral_analysis_section,
    render_conclusions_section
)


# ========== CONFIGURACIÓN DE PÁGINA ==========
st.set_page_config(**PAGE_CONFIG)


# ========== ESTILOS CSS PERSONALIZADOS ==========
def apply_custom_css():
    """
    Aplica estilos CSS personalizados para mejorar la UX/UI.
    """
    st.markdown("""
    <style>
    /* Estilos generales */
    .main {
        padding: 2rem;
    }
    
    /* Título principal */
    h1 {
        color: #1f77b4;
        border-bottom: 3px solid #4ECDC4;
        padding-bottom: 0.5rem;
    }
    
    /* Subtítulos */
    h2 {
        color: #2c3e50;
        margin-top: 2rem;
        border-left: 4px solid #4ECDC4;
        padding-left: 1rem;
    }
    
    h3 {
        color: #34495e;
    }
    
    /* Métricas */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
    }
    
    /* Botones */
    .stButton>button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Tarjetas de información */
    .stAlert {
        border-radius: 10px;
        padding: 1.5rem;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Tablas */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    /* Selectbox y otros inputs */
    .stSelectbox, .stMultiSelect {
        border-radius: 8px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        font-weight: 500;
    }
    
    /* Scrollbar personalizado */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    </style>
    """, unsafe_allow_html=True)


# ========== FUNCIONES DE PROCESAMIENTO ==========
def load_data(use_default, txt_file=None, csv_file=None):
    """
    Carga los datos desde archivos por defecto o subidos por el usuario.
    
    Args:
        use_default (bool): Si usar archivos por defecto
        txt_file: Archivo .txt subido (opcional)
        csv_file: Archivo .csv subido (opcional)
        
    Returns:
        CalciumDataLoader: Instancia del cargador de datos con datos cargados
    """
    try:
        if use_default:
            # Usar archivos por defecto
            loader = CalciumDataLoader()
        else:
            # Validar archivos subidos
            if txt_file is None or csv_file is None:
                st.error("Por favor sube ambos archivos (.txt y .csv)")
                return None
            
            # Guardar archivos temporalmente
            with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp_txt:
                tmp_txt.write(txt_file.getvalue())
                txt_path = tmp_txt.name
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_csv:
                tmp_csv.write(csv_file.getvalue())
                csv_path = tmp_csv.name
            
            loader = CalciumDataLoader(txt_path, csv_path)
        
        # Cargar datos
        with st.spinner('Cargando datos...'):
            loader.load_all_data()
        
        return loader
        
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return None


def process_signals(loader, config):
    """
    Procesa todas las señales aplicando suavizado y detección de eventos.
    
    Args:
        loader (CalciumDataLoader): Cargador de datos
        config (dict): Configuración de parámetros
        
    Returns:
        dict: Diccionario con señales procesadas por ROI
    """
    processed_signals = {}
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    rois_to_process = config['selected_rois'] if config['selected_rois'] else loader.roi_columns
    
    for i, roi_name in enumerate(rois_to_process):
        status_text.text(f"Procesando {roi_name}...")
        
        # Obtener señal
        signal_data = loader.get_roi_data(roi_name)
        time_array = loader.time_array
        
        # Crear procesador
        processor = SignalProcessor(signal_data, time_array)
        
        # Aplicar suavizado
        smoothed = processor.apply_savgol_filter(
            window=config['sg_window'],
            polyorder=config['sg_polyorder']
        )

        # Filtrado Butterworth para reducción de ruido
        sampling_rate_hz = estimate_sampling_rate(time_array)
        tf_filtered = None
        detection_source = config.get('detection_signal_source', 'sg')
        if sampling_rate_hz > 0:
            tf_filter_type = config.get('tf_filter_type', 'bandpass')
            tf_filter_order = config.get('tf_filter_order', 4)
            if tf_filter_type in ['lowpass', 'highpass']:
                cutoff = config.get('tf_cutoff_high') if tf_filter_type == 'lowpass' else config.get('tf_cutoff_low')
            else:
                cutoff = (config.get('tf_cutoff_low'), config.get('tf_cutoff_high'))

            if cutoff is not None and not (isinstance(cutoff, tuple) and None in cutoff):
                tf_filtered = apply_butter_filter(
                    signal_data,
                    sampling_rate_hz,
                    tf_filter_type,
                    cutoff,
                    order=tf_filter_order
                )
        
        # Detección de eventos usando la señal seleccionada
        if detection_source == 'butterworth' and tf_filtered is not None:
            processor.smoothed_signal = tf_filtered
            use_smoothed = True
        elif detection_source == 'original':
            use_smoothed = False
        else:
            use_smoothed = True

        event_mask, baseline, std_dev = processor.robust_event_detection(
            w=config['signal_window'],
            k_up=config['k_up'],
            k_down=config['k_down'],
            influence=config['influence'],
            run_min=config['run_min'],
            use_smoothed=use_smoothed
        )
        
        # Guardar resultados
        processed_signals[roi_name] = {
            'original': signal_data,
            'smoothed': smoothed,
            'tf_filtered': tf_filtered,
            'event_mask': event_mask,
            'baseline': baseline,
            'std_dev': std_dev,
            'processor': processor
        }
        
        # Actualizar barra de progreso
        progress_bar.progress((i + 1) / len(rois_to_process))
    
    status_text.empty()
    progress_bar.empty()
    
    return processed_signals


def calculate_all_metrics(loader, processed_signals, config):
    """
    Calcula métricas para todos los ROIs y estímulos.
    
    Args:
        loader (CalciumDataLoader): Cargador de datos
        processed_signals (dict): Señales procesadas
        config (dict): Configuración
        
    Returns:
        pd.DataFrame: DataFrame con todas las métricas calculadas
    """
    results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    rois_to_process = list(processed_signals.keys())
    total_iterations = len(rois_to_process) * len(loader.stimuli_data)
    current_iteration = 0
    
    for roi_name, proc_data in processed_signals.items():
        signal_smoothed = proc_data['smoothed']
        event_mask = proc_data['event_mask']
        time_array = loader.time_array
        
        # Iterar sobre estímulos
        for idx, stim_row in loader.stimuli_data.iterrows():
            # Usar columna 'Stimuli' si existe, sino primera columna
            stimulus_name = stim_row['Stimuli'] if 'Stimuli' in stim_row else stim_row.iloc[0]
            stimulus_start = stim_row['inicio']
            stimulus_end = stim_row['fin']
            
            # Determinar fin efectivo (hasta siguiente estímulo o final)
            if idx < len(loader.stimuli_data) - 1:
                next_start = loader.stimuli_data.iloc[idx + 1]['inicio']
            else:
                next_start = None
            
            status_text.text(f"Calculando métricas: {roi_name} - {stimulus_name}")
            
            # Calcular métricas
            try:
                metrics = calculate_stimulus_metrics(
                    signal_smoothed,
                    time_array,
                    event_mask,
                    stimulus_start,
                    stimulus_end,
                    next_start
                )
                
                # Solo agregar si hay métricas válidas
                if metrics is not None:
                    results.append({
                        'ROI': roi_name,
                        'Stimuli': stimulus_name,
                        'start_time': metrics['start_time'],
                        'end_time': metrics['end_time'],
                        'duration': metrics['duration'],
                        'area_total': metrics['area_total'],
                        'area_1min': metrics['area_1min'],
                        'max_value': metrics['max_value']
                    })
                else:
                    # No se pudo calcular métricas (sin eventos detectados)
                    # Agregar fila con valores NaN
                    results.append({
                        'ROI': roi_name,
                        'Stimuli': stimulus_name,
                        'start_time': np.nan,
                        'end_time': np.nan,
                        'duration': 0.0,
                        'area_total': 0.0,
                        'area_1min': 0.0,
                        'max_value': 0.0
                    })
            except Exception as e:
                # Error inesperado - agregar valores NaN
                results.append({
                    'ROI': roi_name,
                    'Stimuli': stimulus_name,
                    'start_time': np.nan,
                    'end_time': np.nan,
                    'duration': 0.0,
                    'area_total': 0.0,
                    'area_1min': 0.0,
                    'max_value': 0.0
                })
            
            current_iteration += 1
            progress_bar.progress(current_iteration / total_iterations)
    
    status_text.empty()
    progress_bar.empty()
    
    # Crear DataFrame y mostrar resumen
    results_df = pd.DataFrame(results)
    
    # Contar ROIs sin eventos detectados
    if len(results_df) > 0:
        invalid_rows = results_df[results_df['duration'] == 0].shape[0]
        total_rows = len(results_df)
        if invalid_rows > 0:
            st.info(f"""
            ℹ️ **Nota sobre la detección de eventos:**
            
            - Total de análisis: {total_rows}
            - Con eventos detectados: {total_rows - invalid_rows}
            - Sin eventos detectados: {invalid_rows}
            
            Algunas ROIs no mostraron eventos claros en ciertos estímulos. 
            Esto puede deberse a:
            - Células poco reactivas
            - Parámetros de detección muy estrictos
            - Ruido alto en la señal
            
            💡 **Sugerencia**: Ajusta los parámetros de detección en el menú lateral si crees que hay falsos negativos.
            """)
    
    return results_df


# ========== FUNCIÓN PRINCIPAL ==========
def main():
    """
    Función principal de la aplicación.
    """
    # Aplicar estilos CSS
    apply_custom_css()
    
    # ===== RENDERIZAR SIDEBAR Y OBTENER CONFIGURACIÓN =====
    config = render_sidebar()
    
    # ===== INICIALIZAR SESSION STATE =====
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    
    # ===== CARGAR DATOS =====
    # Cargar datos si es necesario
    if config['use_default'] or (config['txt_file'] is not None and config['csv_file'] is not None):
        # Verificar si necesitamos recargar datos
        need_reload = False
        
        if not st.session_state.data_loaded:
            need_reload = True
        elif 'last_config' in st.session_state:
            # Verificar si cambió la fuente de datos
            if st.session_state.last_config['use_default'] != config['use_default']:
                need_reload = True
        
        if need_reload:
            loader = load_data(config['use_default'], config['txt_file'], config['csv_file'])
            
            if loader is not None:
                # Guardar en session state
                st.session_state.data_loader = loader
                st.session_state.calcium_data = loader.data
                st.session_state.stimuli_data = loader.stimuli_data
                st.session_state.time_array = loader.time_array
                st.session_state.data_summary = loader.get_data_summary()
                st.session_state.data_loaded = True
                
                # Guardar listas para selectores
                st.session_state.available_rois = loader.roi_columns
                st.session_state.available_stimuli = loader.stimuli_data.iloc[:, 0].tolist()
                
                st.success(SUCCESS_MESSAGES['data_loaded'])
                
                # Forzar reprocesamiento
                if 'processed_signals' in st.session_state:
                    del st.session_state['processed_signals']
                if 'results_df' in st.session_state:
                    del st.session_state['results_df']
    
    # Mostrar resumen de datos en sidebar
    if st.session_state.data_loaded:
        show_data_summary(st.session_state.data_summary)
    
    # ===== PROCESAR SEÑALES SI ES NECESARIO =====
    if st.session_state.data_loaded:
        # Verificar si necesitamos reprocesar
        need_reprocess = False
        
        if 'processed_signals' not in st.session_state:
            need_reprocess = True
        elif 'last_config' in st.session_state:
            # Verificar si cambiaron parámetros importantes
            params_to_check = ['sg_window', 'sg_polyorder', 'signal_window', 'k_up', 'k_down', 'influence', 'run_min']
            params_to_check.extend([
                'tf_filter_type',
                'tf_filter_order',
                'tf_cutoff_low',
                'tf_cutoff_high',
                'detection_signal_source'
            ])
            for param in params_to_check:
                if st.session_state.last_config.get(param) != config.get(param):
                    need_reprocess = True
                    break
            
            # Verificar si cambiaron ROIs seleccionadas
            if set(st.session_state.last_config.get('selected_rois', [])) != set(config.get('selected_rois', [])):
                need_reprocess = True
        
        if need_reprocess:
            with st.spinner('Procesando señales...'):
                processed = process_signals(st.session_state.data_loader, config)
                st.session_state.processed_signals = processed
                
                # Calcular métricas
                results_df = calculate_all_metrics(
                    st.session_state.data_loader,
                    processed,
                    config
                )
                st.session_state.results_df = results_df
                
                st.success(SUCCESS_MESSAGES['processing_complete'])
    
    # Guardar configuración actual
    st.session_state.last_config = config.copy()
    
    # ===== RENDERIZAR SECCIÓN SELECCIONADA =====
    plotter = CalciumPlotter()
    
    if config['section'] == 'home':
        render_home_section()
    
    elif config['section'] == 'origin':
        render_origin_section()
    
    elif config['section'] == 'data_explanation':
        render_data_explanation_section()
    
    elif config['section'] == 'eda':
        render_eda_section(config, plotter)
    
    elif config['section'] == 'spectral':
        render_spectral_analysis_section(config, plotter)
    
    elif config['section'] == 'conclusions':
        render_conclusions_section()
    
    # ===== FOOTER =====
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #7f8c8d; padding: 2rem 0;'>
        <p><strong>Panel de Inteligencia - Imagen de Calcio Neuronal</strong></p>
        <p>Versión 1.0 | Febrero 2026</p>
        <p>Desarrollado con ❤️ usando Streamlit, Pandas, NumPy y Plotly</p>
    </div>
    """, unsafe_allow_html=True)


# ========== PUNTO DE ENTRADA ==========
if __name__ == "__main__":
    main()
