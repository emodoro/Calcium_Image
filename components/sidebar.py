"""
Componente del sidebar (menú lateral) de la aplicación.
Contiene controles de navegación, carga de archivos y parámetros.
"""

import streamlit as st
import os
from config import *


def render_sidebar():
    """
    Renderiza el sidebar completo con navegación y controles.
    
    Returns:
        dict: Diccionario con configuraciones seleccionadas por el usuario
    """
    with st.sidebar:
        # Logo o título
        st.markdown("# 🧬 Imagen de Calcio")
        st.markdown("---")
        
        # === NAVEGACIÓN ===
        st.markdown("### 📌 Navegación")
        section = st.radio(
            "Selecciona una sección:",
            options=list(SECTIONS.keys()),
            format_func=lambda x: SECTIONS[x],
            key='navigation'
        )
        
        st.markdown("---")
        
        # === CARGA DE ARCHIVOS ===
        st.markdown("### 📂 Carga de Archivos")
        
        use_default = st.checkbox(
            "Usar archivos por defecto", 
            value=True,
            help="Usa ID002_A_002 como ejemplo"
        )
        
        txt_file = None
        csv_file = None
        
        if not use_default:
            txt_file = st.file_uploader(
                "Archivo de registro (.txt)",
                type=['txt'],
                help="Archivo con datos de imagen de calcio"
            )
            
            csv_file = st.file_uploader(
                "Archivo de estímulos (.csv)",
                type=['csv'],
                help="Archivo con información de estímulos"
            )
        
        st.markdown("---")
        
        # === PARÁMETROS DE PROCESAMIENTO ===
        st.markdown("### ⚙️ Parámetros")
        
        with st.expander("Suavizado (Savitzky-Golay)", expanded=False):
            sg_window = st.slider(
                "Tamaño de ventana",
                min_value=MIN_WINDOW,
                max_value=50,
                value=SG_WINDOW,
                step=2,
                help="Debe ser un número impar"
            )
            # Asegurar que sea impar
            if sg_window % 2 == 0:
                sg_window += 1
            
            sg_polyorder = st.slider(
                "Orden del polinomio",
                min_value=2,
                max_value=5,
                value=SG_POLYORDER,
                help="Orden del polinomio de ajuste"
            )
        
        with st.expander("Detección de Eventos", expanded=False):
            signal_window = st.slider(
                "Ventana baseline móvil",
                min_value=MIN_WINDOW,
                max_value=MAX_WINDOW,
                value=SIGNAL_WINDOW,
                help="Ventana para calcular baseline adaptativo"
            )
            
            k_up = st.slider(
                "Factor umbral subida",
                min_value=MIN_K_FACTOR,
                max_value=MAX_K_FACTOR,
                value=float(K_UP),
                step=0.1,
                help="Multiplicador de sigma para detectar subidas"
            )
            
            k_down = st.slider(
                "Factor umbral bajada",
                min_value=MIN_K_FACTOR,
                max_value=MAX_K_FACTOR,
                value=float(K_DOWN),
                step=0.1,
                help="Multiplicador de sigma para detectar bajadas"
            )
            
            influence = st.slider(
                "Influencia",
                min_value=MIN_INFLUENCE,
                max_value=MAX_INFLUENCE,
                value=float(INFLUENCE),
                step=0.05,
                help="Influencia del nuevo valor en baseline (0-1)"
            )
            
            run_min = st.slider(
                "Puntos mínimos para unir eventos",
                min_value=2,
                max_value=30,
                value=RUN_MIN,
                help="Unir eventos separados por menos de estos puntos"
            )
        
        st.markdown("---")
        
        # === FILTROS DE VISUALIZACIÓN ===
        st.markdown("### 🎯 Filtros")
        
        # Estos se llenarán dinámicamente cuando haya datos cargados
        selected_rois = st.multiselect(
            "ROIs a visualizar",
            options=st.session_state.get('available_rois', []),
            default=st.session_state.get('available_rois', [])[:3] if st.session_state.get('available_rois', []) else [],
            help="Selecciona las ROIs que quieres analizar"
        )
        
        selected_stimuli = st.multiselect(
            "Estímulos a analizar",
            options=st.session_state.get('available_stimuli', []),
            default=st.session_state.get('available_stimuli', []),
            help="Selecciona los estímulos de interés"
        )
        
        st.markdown("---")
        
        # === INFORMACIÓN ===
        with st.expander("ℹ️ Información", expanded=False):
            st.markdown("""
            **Panel de Inteligencia**
            
            Versión: 1.0
            
            Desarrollado para análisis de imagen de calcio en células neuronales.
            
            **Características:**
            - Detección robusta de eventos
            - Cálculo automático de métricas
            - Visualizaciones interactivas
            - Análisis estadístico
            """)
        
        # Botón de reset (al final)
        if st.button("🔄 Resetear Aplicación", type="secondary"):
            # Limpiar session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Retornar configuración
    return {
        'section': section,
        'use_default': use_default,
        'txt_file': txt_file,
        'csv_file': csv_file,
        'sg_window': sg_window,
        'sg_polyorder': sg_polyorder,
        'signal_window': signal_window,
        'k_up': k_up,
        'k_down': k_down,
        'influence': influence,
        'run_min': run_min,
        'selected_rois': selected_rois,
        'selected_stimuli': selected_stimuli
    }


def show_data_summary(data_summary):
    """
    Muestra resumen de datos en el sidebar.
    
    Args:
        data_summary (dict): Diccionario con resumen de datos
    """
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📊 Datos Cargados")
        
        if data_summary:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("ROIs", data_summary.get('num_rois', 0))
                st.metric("Estímulos", data_summary.get('num_stimuli', 0))
            with col2:
                st.metric("Duración", f"{data_summary.get('duration_minutes', 0):.1f} min")
                st.metric("Muestreo", f"{data_summary.get('sampling_rate_hz', 0):.2f} Hz")
