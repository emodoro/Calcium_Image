"""
Componentes de secciones de contenido de la aplicación.
Cada función renderiza una sección específica del panel.
"""

import streamlit as st
import pandas as pd
import numpy as np
from config import APP_TITLE, APP_DESCRIPTION
from utils.signal_processing import (
    estimate_sampling_rate,
    interpolate_masked_signal,
    apply_butter_filter,
    compute_fft_spectrum
)


def render_home_section():
    """
    Renderiza la sección de inicio/bienvenida.
    """
    st.title(APP_TITLE)
    st.markdown(APP_DESCRIPTION)
    
    # Tarjetas informativas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        ### 📖 Origen
        Conoce la fuente y estructura de los datos de imagen de calcio.
        """)
    
    with col2:
        st.info("""
        ### 📊 Datos
        Explora las características y componentes de las señales registradas.
        """)
    
    with col3:
        st.info("""
        ### 🔬 Análisis
        Análisis exploratorio completo con detección automática de eventos.
        """)
    
    st.markdown("---")
    
    # Sección de inicio rápido
    st.markdown("## 🚀 Inicio Rápido")
    
    st.markdown("""
    1. **Carga tus datos**: Usa los archivos por defecto o sube tus propios archivos .txt y .csv desde el menú lateral.
    2. **Ajusta parámetros**: Personaliza los parámetros de procesamiento según tus necesidades.
    3. **Explora secciones**: Navega por las diferentes secciones para análisis completo.
    4. **Visualiza resultados**: Interactúa con gráficos y descarga métricas calculadas.
    """)
    
    # Características principales
    st.markdown("---")
    st.markdown("## ✨ Características Principales")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🔍 Procesamiento Avanzado**
        - Suavizado con filtro Savitzky-Golay
        - Detección robusta de eventos con umbrales adaptativos
        - Cálculo automático de baseline móvil
        - Estimación robusta de variabilidad (MAD)
        
        **📈 Métricas Calculadas**
        - Área bajo la curva (AUC total y 1er minuto)
        - Máximo de respuesta
        - Duración de eventos
        - Tiempos de inicio y fin
        """)
    
    with col2:
        st.markdown("""
        **📊 Visualizaciones Interactivas**
        - Señales con máscaras de estímulos
        - Comparación original vs suavizada
        - Detección de eventos en tiempo real
        - Heatmaps y comparaciones estadísticas
        
        **💾 Exportación de Resultados**
        - Tablas de métricas en formato CSV
        - Gráficos de alta resolución
        - Reportes completos de análisis
        """)
    
    st.markdown("---")
    
    # Información sobre los datos
    if 'data_loaded' in st.session_state and st.session_state.data_loaded:
        st.success("✅ Datos cargados y listos para análisis")
        
        # Mostrar resumen básico
        if 'data_summary' in st.session_state:
            summary = st.session_state.data_summary
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🔬 ROIs", summary.get('num_rois', 0))
            with col2:
                st.metric("💉 Estímulos", summary.get('num_stimuli', 0))
            with col3:
                st.metric("⏱️ Duración", f"{summary.get('duration_minutes', 0):.1f} min")
            with col4:
                st.metric("📊 Puntos", summary.get('num_timepoints', 0))
    else:
        st.warning("⚠️ No hay datos cargados. Selecciona archivos en el menú lateral.")


def render_origin_section():
    """
    Renderiza la sección sobre el origen de los datos.
    """
    st.title("📖 Origen de los Datos")
    
    st.markdown("""
    ## La Técnica de Imagen de Calcio
    
    La imagen de calcio en célula única es una ventana hacia la actividad neuronal. Cuando una neurona 
    se activa, el calcio entra a la célula y produce una señal fluorescente que podemos medir.
    
    ### ¿Qué Observamos?
    
    Imagina que cada neurona es como una ciudad que se ilumina cuando algo importante sucede. La imagen 
    de calcio nos permite ver esas "luces" encendiéndose y apagándose en tiempo real.
    """)
    
    # Estructura de datos
    st.markdown("---")
    st.markdown("## 📁 Estructura de los Datos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Archivo de Registro (.txt)
        
        Contiene la información longitudinal de la señal de calcio:
        
        - **Columnas**: Tiempo + múltiples células (ROI_1, ROI_2, ..., ROI_N)
        - **Filas**: Mediciones en diferentes momentos del tiempo
        - **Valores**: Intensidad de fluorescencia (0-1, normalizada)
        - **Frecuencia**: Variable según experimento
        - **Duración**: Varios minutos de registro continuo
        """)
    
    with col2:
        st.markdown("""
        ### Archivo de Estímulos (.csv)
        
        Marca temporalmente los estímulos aplicados:
        
        - **Columnas**: Nombre del estímulo, Inicio (min), Fin (min)
        - **Filas**: Cada estímulo aplicado durante el experimento
        - **Propósito**: Identificar cuándo se aplicó cada sustancia
        - **Uso**: Correlacionar respuestas con estímulos específicos
        """)
    
    # Nomenclatura
    st.markdown("---")
    st.markdown("## 🏷️ Nomenclatura de Experimentos")
    
    st.info("""
    **Formato**: `ID###_X_###`
    
    - **ID###**: Identificador del sujeto/línea celular (ej: ID002, ID003)
    - **Letra (A/B/C)**: Condición experimental diferente
    - **Número**: Réplica del experimento
    
    **Ejemplo**: `ID002_A_002` = Sujeto 002, Condición A, Réplica 2
    """)
    
    # Importancia
    st.markdown("---")
    st.markdown("## 💡 ¿Por Qué es Importante?")
    
    st.markdown("""
    Las neuronas se comunican mediante cambios en sus niveles de calcio interno. Al medir estos cambios, podemos:
    
    1. **Entender** cómo las células responden a diferentes sustancias químicas
    2. **Comparar** la salud y reactividad de diferentes tipos celulares
    3. **Identificar** patrones anormales que podrían indicar enfermedad
    4. **Evaluar** la efectividad de potenciales tratamientos farmacológicos
    """)


def render_data_explanation_section():
    """
    Renderiza la sección de explicación de datos.
    """
    st.title("📊 Explicación de la Data")
    
    st.markdown("""
    ## Anatomía de la Señal de Calcio
    
    Cada señal que registramos NO es pura. Es una mezcla de varios componentes:
    """)
    
    # Componentes de la señal
    st.markdown("### 📈 Señal Completa = 📉 Tendencia + ⚡ Respuesta + 🌊 Oscilaciones + 📡 Ruido")
    
    # Tabs para cada componente
    tab1, tab2, tab3, tab4 = st.tabs(["📉 Tendencia", "⚡ Respuesta", "🌊 Oscilaciones", "📡 Ruido"])
    
    with tab1:
        st.markdown("""
        ### Tendencia (Drift)
        
        **Qué es:** Cambio gradual del nivel basal con el tiempo.
        
        **Causas:**
        - Fotoblanqueo (la fluorescencia disminuye con la exposición)
        - Cambios en el enfoque
        - Deriva del preparado experimental
        
        **Problema:** Puede confundir respuestas reales con artefactos técnicos.
        
        **Solución:** Se estima y se resta mediante ajuste polinomial local y baseline móvil.
        """)
    
    with tab2:
        st.markdown("""
        ### Respuesta a Estímulo (Transitorio)
        
        **Qué es:** El pico de actividad que realmente nos interesa.
        
        **Características:**
        - Subida rápida
        - Posible meseta
        - Bajada gradual
        
        **Información clave:**
        - Amplitud del pico
        - Duración de la respuesta
        - Área bajo la curva (cantidad total de activación)
        """)
    
    with tab3:
        st.markdown("""
        ### Oscilaciones
        
        **Qué es:** Fluctuaciones rítmicas de la señal.
        
        **Significado:**
        - Pueden ser actividad neuronal espontánea (biológicamente relevante)
        - O ruido estructurado (artefacto técnico)
        
        **Manejo:**
        - Se pueden filtrar mediante suavizado
        - O analizar por separado según el objetivo del estudio
        """)
    
    with tab4:
        st.markdown("""
        ### Ruido
        
        **Qué es:** Variaciones aleatorias sin significado biológico.
        
        **Fuentes:**
        - Ruido del detector de imagen
        - Variaciones de iluminación
        - Movimientos celulares
        
        **Solución:** Filtrado mediante técnicas de suavizado (Savitzky-Golay).
        """)
    
    # Metodología de procesamiento
    st.markdown("---")
    st.markdown("## 🛠️ Metodología de Procesamiento")
    
    st.markdown("""
    ### Fase 1: Preprocesamiento - Limpieza de la Señal
    
    **Suavizado con Filtro Savitzky-Golay**
    
    Piensa en el filtro como pasar un borrador suave sobre un dibujo con trazos temblorosos. 
    Elimina las imperfecciones pequeñas sin destruir la forma general del dibujo.
    
    - **Ventana:** Número de puntos adyacentes a considerar
    - **Orden del polinomio:** Grado de ajuste (mayor = más flexible)
    - **Ventaja:** Preserva picos y valles sin "aplastarlos"
    """)
    
    st.markdown("""
    ### Fase 2: Detección de Eventos - El Corazón del Análisis
    
    **Sistema Adaptativo Robusto**
    
    En lugar de un umbral fijo, usamos un sistema que entiende el contexto de cada señal:
    
    1. **Baseline Móvil**: Se calcula continuamente la mediana de los últimos N puntos
    2. **Variabilidad Robusta (MAD)**: Estimación resistente a valores atípicos
    3. **Umbrales con Histéresis**: Diferentes umbrales para activar y desactivar detección
    4. **Influencia Adaptativa**: El sistema "recuerda" eventos recientes
    5. **Refinamiento Temporal**: Extiende eventos capturando su inicio real
    """)
    
    st.markdown("""
    ### Fase 3: Cuantificación de Respuestas
    
    **Métricas Calculadas:**
    
    - **Área Bajo la Curva (AUC)**: Cantidad total de activación (fluorescencia × tiempo)
    - **AUC 1er Minuto**: Respuesta inicial rápida
    - **Máximo**: Pico máximo de activación
    - **Duración**: Tiempo que dura la respuesta
    - **Tiempos**: Inicio y fin exactos de cada evento
    """)
    
    # Mostrar datos cargados si existen
    if 'data_loaded' in st.session_state and st.session_state.data_loaded:
        st.markdown("---")
        st.markdown("## 📋 Vista Previa de Datos Cargados")
        
        if 'calcium_data' in st.session_state:
            data = st.session_state.calcium_data
            st.dataframe(data.head(20), use_container_width=True)
            
            st.caption(f"Mostrando primeras 20 filas de {len(data)} puntos temporales totales")
        
        if 'stimuli_data' in st.session_state:
            st.markdown("### Estímulos Aplicados")
            st.dataframe(st.session_state.stimuli_data, use_container_width=True)


def render_eda_section(config, plotter):
    """
    Renderiza la sección de análisis exploratorio de datos (EDA).
    
    Args:
        config (dict): Configuración de parámetros
        plotter: Instancia de CalciumPlotter
    """
    st.title("🔬 Análisis Exploratorio de Datos (EDA)")
    
    if 'data_loaded' not in st.session_state or not st.session_state.data_loaded:
        st.warning("⚠️ Por favor carga los datos primero desde el menú lateral.")
        return
    
    # Subsecciones del EDA
    eda_tab1, eda_tab2, eda_tab3, eda_tab4 = st.tabs([
        "📈 Señales Originales",
        "🔄 Preprocesamiento",
        "⚡ Detección de Eventos",
        "📊 Métricas y Resultados"
    ])
    
    # --- TAB 1: Señales Originales ---
    with eda_tab1:
        st.markdown("## Visualización de Señales con Estímulos")
        
        # Selector de ROI
        selected_roi = st.selectbox(
            "Selecciona una ROI para visualizar:",
            options=config['selected_rois'] if config['selected_rois'] else st.session_state.get('available_rois', []),
            key='eda_roi_selector'
        )
        
        if selected_roi:
            # Obtener datos
            time = st.session_state.time_array
            signal = st.session_state.calcium_data[selected_roi].to_numpy()
            stimuli = st.session_state.stimuli_data
            
            # Crear gráfico
            fig = plotter.plot_signal_with_stimuli(time, signal, stimuli, roi_name=selected_roi)
            st.plotly_chart(fig, use_container_width=True)
            
            st.info("""
            **Interpretación:**
            - Las zonas sombreadas indican períodos de aplicación de estímulos
            - Observa cómo la señal responde durante y después de cada estímulo
            - Variaciones antes de estímulos pueden indicar actividad espontánea
            """)
    
    # --- TAB 2: Preprocesamiento ---
    with eda_tab2:
        st.markdown("## Suavizado de Señal")
        
        if 'processed_signals' not in st.session_state:
            st.info("Procesando señales...")
            # Este procesamiento se hace en el main cuando se cargan los datos
        
        selected_roi = st.selectbox(
            "Selecciona una ROI:",
            options=config['selected_rois'] if config['selected_rois'] else st.session_state.get('available_rois', []),
            key='preprocessing_roi_selector'
        )
        
        if selected_roi and 'processed_signals' in st.session_state:
            if selected_roi in st.session_state.processed_signals:
                proc = st.session_state.processed_signals[selected_roi]
                
                time = st.session_state.time_array
                original = proc['original']
                smoothed = proc['smoothed']
                tf_filtered = proc.get('tf_filtered')
                
                col_left, col_right = st.columns(2)
                with col_left:
                    fig_sg = plotter.plot_time_domain_comparison(
                        time,
                        original,
                        smoothed,
                        roi_name=selected_roi,
                        title="Señal Original vs Suavizada (SG)"
                    )
                    st.plotly_chart(fig_sg, use_container_width=True)

                with col_right:
                    if tf_filtered is not None:
                        fig_tf = plotter.plot_time_domain_comparison(
                            time,
                            original,
                            tf_filtered,
                            roi_name=selected_roi,
                            title="Señal Original vs Filtrada (TF)"
                        )
                        st.plotly_chart(fig_tf, use_container_width=True)
                    else:
                        st.info("Activa el filtrado por TF en el menú lateral para ver esta comparación.")
                
                st.success("""
                **Resultado del Suavizado:**
                - La señal suavizada (roja) preserva la forma general
                - Se eliminan fluctuaciones de alta frecuencia (ruido)
                - Los picos de actividad se mantienen claramente visibles
                """)
    
    # --- TAB 3: Detección de Eventos ---
    with eda_tab3:
        st.markdown("## Detección Robusta de Eventos")
        
        selected_roi = st.selectbox(
            "Selecciona una ROI:",
            options=config['selected_rois'] if config['selected_rois'] else st.session_state.get('available_rois', []),
            key='detection_roi_selector'
        )
        
        if selected_roi and 'processed_signals' in st.session_state:
            if selected_roi in st.session_state.processed_signals:
                proc = st.session_state.processed_signals[selected_roi]
                
                time = st.session_state.time_array
                detection_source = config.get('detection_signal_source', 'sg')
                if detection_source == 'butterworth':
                    signal = proc.get('tf_filtered')
                    if signal is None:
                        signal = proc['smoothed']
                        st.info("No hay señal Butterworth disponible. Usando señal suavizada (SG).")
                elif detection_source == 'original':
                    signal = proc['original']
                else:
                    signal = proc['smoothed']
                event_mask = proc['event_mask']
                baseline = proc['baseline']
                std_dev = proc['std_dev']
                stimuli = st.session_state.stimuli_data
                
                # Obtener datos de métricas para esta ROI
                metrics_for_roi = None
                if 'results_df' in st.session_state:
                    metrics_for_roi = st.session_state.results_df[
                        st.session_state.results_df['ROI'] == selected_roi
                    ].copy()
                
                # Gráfico de detección
                fig = plotter.plot_event_detection(
                    time, signal, event_mask, baseline, std_dev,
                    k_up=config['k_up'], k_down=config['k_down'],
                    roi_name=selected_roi,
                    stimuli_data=stimuli,
                    metrics_data=metrics_for_roi
                )
                st.plotly_chart(fig, use_container_width=True)

                st.caption(
                    f"Señal usada para detección: { {'sg': 'Suavizada (SG)', 'butterworth': 'Filtrada (Butterworth)', 'original': 'Original'}.get(detection_source, 'Suavizada (SG)') }"
                )
                
                st.info("""
                **Interpretación de la Detección:**
                
                - **Panel Superior**: Señal con umbrales adaptativos (zona magenta)
                - **Panel Inferior**: Intervalos de eventos detectados según dataset de métricas
                - Cada rectángulo representa un intervalo de evento para su correspondiente estímulo
                
                Los umbrales se adaptan continuamente al contexto local de la señal.
                """)
                
                # Estadísticas de eventos
                col1, col2, col3 = st.columns(3)
                
                if metrics_for_roi is not None and len(metrics_for_roi) > 0:
                    num_events = len(metrics_for_roi)
                    avg_duration = metrics_for_roi['duration'].mean()
                    avg_area = metrics_for_roi['area_total'].mean()
                else:
                    num_events = 0
                    avg_duration = 0
                    avg_area = 0
                
                with col1:
                    st.metric("Eventos Detectados", int(num_events))
                with col2:
                    st.metric("Duración Promedio (min)", f"{avg_duration:.2f}")
                with col3:
                    st.metric("Área Promedio", f"{avg_area:.2f}")
    
    # --- TAB 4: Métricas y Resultados ---
    with eda_tab4:
        st.markdown("## Métricas Calculadas por Estímulo")
        
        if 'results_df' in st.session_state:
            results_df = st.session_state.results_df
            
            # Filtrar por ROIs y estímulos seleccionados
            if config['selected_rois']:
                results_df = results_df[results_df['ROI'].isin(config['selected_rois'])]
            if config['selected_stimuli']:
                results_df = results_df[results_df['Stimuli'].isin(config['selected_stimuli'])]
            
            # Mostrar tabla de resultados
            st.dataframe(results_df, use_container_width=True)
            
            # Botón de descarga
            csv = results_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Resultados (CSV)",
                data=csv,
                file_name='calcium_metrics.csv',
                mime='text/csv',
            )
            
            st.markdown("---")
            st.markdown("### Visualizaciones Comparativas")
            
            # Selector de métrica
            metric = st.selectbox(
                "Selecciona métrica a visualizar:",
                options=['area_total', 'area_1min', 'max_value', 'duration'],
                format_func=lambda x: {
                    'area_total': 'Área Total',
                    'area_1min': 'Área 1er Minuto',
                    'max_value': 'Máximo',
                    'duration': 'Duración'
                }[x]
            )
            
            # Tipo de gráfico
            plot_type = st.radio(
                "Tipo de visualización:",
                options=['boxplot', 'heatmap', 'summary'],
                format_func=lambda x: {
                    'boxplot': '📊 Boxplot',
                    'heatmap': '🔥 Heatmap',
                    'summary': '📈 Resumen Múltiple'
                }[x],
                horizontal=True
            )
            
            # Renderizar gráfico seleccionado
            if plot_type == 'boxplot':
                group_by = st.radio("Agrupar por:", ['Stimuli', 'ROI'], horizontal=True)
                fig = plotter.plot_metrics_comparison(results_df, metric=metric, group_by=group_by)
                st.plotly_chart(fig, use_container_width=True)
            
            elif plot_type == 'heatmap':
                fig = plotter.plot_heatmap(results_df, metric=metric)
                st.plotly_chart(fig, use_container_width=True)
            
            elif plot_type == 'summary':
                fig = plotter.plot_summary_stats(results_df)
                st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.warning("No hay resultados calculados aún.")


def render_spectral_analysis_section(config, plotter):
    """
    Renderiza la sección de análisis espectral con filtros y FFT.
    """
    st.title("🎵 Análisis Espectral")

    if 'data_loaded' not in st.session_state or not st.session_state.data_loaded:
        st.warning("⚠️ Por favor carga los datos primero desde el menú lateral.")
        return

    if 'time_array' not in st.session_state or 'calcium_data' not in st.session_state:
        st.warning("⚠️ No se encontraron datos en memoria. Recarga la aplicación.")
        return

    time = st.session_state.time_array
    rois = config['selected_rois'] if config['selected_rois'] else st.session_state.get('available_rois', [])

    selected_roi = st.selectbox(
        "Selecciona una ROI para análisis espectral:",
        options=rois,
        key='spectral_roi_selector'
    )

    if not selected_roi:
        st.info("Selecciona una ROI para continuar.")
        return

    source = st.radio(
        "Fuente de señal:",
        options=["Original", "Suavizada"],
        horizontal=True,
        key='spectral_signal_source'
    )

    signal_data = st.session_state.calcium_data[selected_roi].to_numpy()
    if source == "Suavizada":
        if 'processed_signals' in st.session_state and selected_roi in st.session_state.processed_signals:
            signal_data = st.session_state.processed_signals[selected_roi]['smoothed']
        else:
            st.info("No hay señal suavizada disponible. Usando señal original.")

    # Ventana temporal
    time_min = float(time[0])
    time_max = float(time[-1])
    step = max((time_max - time_min) / 200.0, 0.01)
    window_start, window_end = st.slider(
        "Ventana temporal (min):",
        min_value=time_min,
        max_value=time_max,
        value=(time_min, time_max),
        step=step,
        key='spectral_time_window'
    )

    window_mask = (time >= window_start) & (time <= window_end)
    if np.sum(window_mask) < 4:
        st.warning("La ventana seleccionada es demasiado corta para análisis espectral.")
        return

    time_seg = time[window_mask]
    signal_seg = signal_data[window_mask]

    st.markdown("---")
    st.markdown("### 🔧 Opciones de Segmentación")

    col1, col2 = st.columns(2)
    with col1:
        exclude_stimuli = st.checkbox(
            "Excluir intervalos de estímulos",
            value=False,
            help="Interpola los intervalos de estímulo para reducir su influencia espectral."
        )
    with col2:
        exclude_events = st.checkbox(
            "Excluir eventos detectados",
            value=False,
            help="Interpola los eventos detectados para centrarse en oscilaciones de fondo.",
            disabled='processed_signals' not in st.session_state
        )

    keep_mask = np.ones_like(signal_seg, dtype=bool)

    if exclude_stimuli and 'stimuli_data' in st.session_state:
        stimuli = st.session_state.stimuli_data
        for _, row in stimuli.iterrows():
            start_time = float(row['inicio'])
            end_time = float(row['fin'])
            keep_mask &= ~((time_seg >= start_time) & (time_seg <= end_time))

    if exclude_events and 'processed_signals' in st.session_state:
        event_mask = st.session_state.processed_signals[selected_roi]['event_mask']
        event_mask_seg = event_mask[window_mask]
        keep_mask &= (event_mask_seg == 0)

    if not keep_mask.all():
        signal_seg = interpolate_masked_signal(signal_seg, keep_mask)
        st.caption("Se interpolaron segmentos excluidos para mantener muestreo uniforme.")

    sampling_rate_hz = estimate_sampling_rate(time_seg)
    if sampling_rate_hz <= 0:
        st.warning("No fue posible estimar la frecuencia de muestreo.")
        return

    nyquist_hz = 0.5 * sampling_rate_hz

    st.markdown("---")
    st.markdown("### 🎚️ Filtros Espectrales")

    col1, col2, col3 = st.columns(3)
    with col1:
        filter_type = st.selectbox(
            "Tipo de filtro:",
            options=['none', 'lowpass', 'highpass', 'bandpass', 'bandstop'],
            format_func=lambda x: {
                'none': 'Sin filtro',
                'lowpass': 'Paso bajo',
                'highpass': 'Paso alto',
                'bandpass': 'Paso banda',
                'bandstop': 'Rechaza banda'
            }[x],
            key='spectral_filter_type'
        )
    with col2:
        units = st.selectbox(
            "Unidades de frecuencia:",
            options=['Hz', 'ciclos/min'],
            key='spectral_units'
        )
    with col3:
        filter_order = st.slider(
            "Orden del filtro:",
            min_value=2,
            max_value=8,
            value=4,
            step=1,
            key='spectral_filter_order'
        )

    max_freq_display = nyquist_hz if units == 'Hz' else nyquist_hz * 60.0
    default_cutoff_display = min(max_freq_display * 0.25, max_freq_display * 0.9)
    cutoff_hz = None

    if filter_type in ['lowpass', 'highpass']:
        cutoff_display = st.number_input(
            "Frecuencia de corte:",
            min_value=0.0,
            max_value=max_freq_display,
            value=float(default_cutoff_display),
            step=max(max_freq_display / 200.0, 0.01),
            key='spectral_cutoff_single'
        )
        cutoff_hz = cutoff_display if units == 'Hz' else cutoff_display / 60.0
    elif filter_type in ['bandpass', 'bandstop']:
        col_low, col_high = st.columns(2)
        with col_low:
            low_display = st.number_input(
                "Corte inferior:",
                min_value=0.0,
                max_value=max_freq_display,
                value=float(max_freq_display * 0.1),
                step=max(max_freq_display / 200.0, 0.01),
                key='spectral_cutoff_low'
            )
        with col_high:
            high_display = st.number_input(
                "Corte superior:",
                min_value=0.0,
                max_value=max_freq_display,
                value=float(max_freq_display * 0.3),
                step=max(max_freq_display / 200.0, 0.01),
                key='spectral_cutoff_high'
            )
        if low_display >= high_display:
            st.error("El corte inferior debe ser menor que el superior.")
            return
        cutoff_hz = (
            low_display if units == 'Hz' else low_display / 60.0,
            high_display if units == 'Hz' else high_display / 60.0
        )

    detrend = st.checkbox(
        "Restar media antes de FFT",
        value=True,
        key='spectral_detrend'
    )
    use_window = st.checkbox(
        "Aplicar ventana Hann",
        value=True,
        key='spectral_window'
    )

    if filter_type != 'none' and cutoff_hz is not None:
        if isinstance(cutoff_hz, tuple):
            if cutoff_hz[0] <= 0 or cutoff_hz[1] >= nyquist_hz:
                st.error("Las frecuencias de corte deben estar entre 0 y Nyquist.")
                return
        else:
            if cutoff_hz <= 0 or cutoff_hz >= nyquist_hz:
                st.error("La frecuencia de corte debe estar entre 0 y Nyquist.")
                return

    filtered_signal = apply_butter_filter(
        signal_seg,
        sampling_rate_hz,
        filter_type,
        cutoff_hz if cutoff_hz is not None else 0.0,
        order=filter_order
    )

    window_name = 'hann' if use_window else None
    freqs_hz, mag_before = compute_fft_spectrum(
        signal_seg,
        sampling_rate_hz,
        detrend=detrend,
        window=window_name
    )
    _, mag_after = compute_fft_spectrum(
        filtered_signal,
        sampling_rate_hz,
        detrend=detrend,
        window=window_name
    )

    freqs_display = freqs_hz if units == 'Hz' else freqs_hz * 60.0
    units_label = "Hz" if units == 'Hz' else "ciclos/min"

    st.markdown("---")
    st.markdown("### 📈 Señal y Espectro")

    fig_time = plotter.plot_time_domain_comparison(
        time_seg,
        signal_seg,
        filtered_signal,
        roi_name=selected_roi
    )
    st.plotly_chart(fig_time, use_container_width=True)

    fig_spec = plotter.plot_spectral_comparison(
        freqs_display,
        mag_before,
        mag_after,
        units_label=units_label,
        title="Espectro de la Transformada de Fourier"
    )
    if st.checkbox("Escala logarítmica en magnitud", value=False, key='spectral_log_scale'):
        fig_spec.update_yaxes(type='log')
    st.plotly_chart(fig_spec, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🔍 Frecuencia Dominante")

    max_search_display = max_freq_display * 0.95
    range_min_default = max_search_display * 0.02
    range_max_default = max_search_display * 0.5
    search_min, search_max = st.slider(
        "Rango de búsqueda de pico dominante:",
        min_value=0.0,
        max_value=max_search_display,
        value=(range_min_default, range_max_default),
        step=max(max_freq_display / 200.0, 0.01),
        key='spectral_peak_range'
    )

    peak_mask = (freqs_display >= search_min) & (freqs_display <= search_max)
    if np.any(peak_mask):
        peak_idx = np.argmax(mag_after[peak_mask])
        dominant_freq_display = freqs_display[peak_mask][peak_idx]
        dominant_freq_hz = freqs_hz[peak_mask][peak_idx]
        dominant_mag = mag_after[peak_mask][peak_idx]
        period_seconds = 1.0 / dominant_freq_hz if dominant_freq_hz > 0 else 0.0
        period_minutes = period_seconds / 60.0 if period_seconds > 0 else 0.0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Frecuencia dominante", f"{dominant_freq_display:.4f} {units_label}")
        with col2:
            st.metric("Periodo", f"{period_minutes:.2f} min")
        with col3:
            st.metric("Magnitud", f"{dominant_mag:.4f}")
    else:
        st.info("No se encontraron picos en el rango seleccionado.")

    st.caption(
        f"Frecuencia de muestreo estimada: {sampling_rate_hz:.3f} Hz | "
        f"Nyquist: {nyquist_hz:.3f} Hz"
    )


def render_conclusions_section():
    """
    Renderiza la sección de conclusiones.
    """
    st.title("💡 Conclusiones y Hallazgos")
    
    st.markdown("""
    ## Hallazgos Principales del Análisis
    
    ### 1. 🧬 Heterogeneidad Celular es la Norma
    
    **Observación:** Incluso células de la misma condición experimental muestran respuestas muy diferentes 
    al mismo estímulo.
    
    **Evidencia:**
    - Algunas células (ROIs) muestran picos con amplitud máxima ~0.8
    - Otras células apenas responden con amplitud ~0.1
    - La duración de las respuestas puede variar de 0.5 a 3+ minutos
    
    **Implicación:**
    - No se puede asumir que todas las células son iguales
    - Los análisis deben reportar estadísticas robustas (mediana, rangos intercuartílicos)
    - Es fundamental identificar subpoblaciones de células
    """)
    
    st.markdown("---")
    
    st.markdown("""
    ### 2. ⚡ Estímulos Generan Patrones Reproducibles
    
    **Observación:** Cada tipo de estímulo genera un patrón característico de respuesta, pero la magnitud 
    y timing varían entre células.
    
    **Patrones identificados:**
    - **Respuestas rápidas:** Subida en <30 segundos, bajada en 1-2 minutos
    - **Respuestas sostenidas:** Subida gradual, meseta prolongada, bajada lenta
    - **Respuestas bifásicas:** Pico inicial seguido de una segunda activación
    
    **Para investigación:**
    - Diferentes estímulos activan diferentes mecanismos celulares
    - La clasificación automática de patrones es posible y útil
    """)
    
    st.markdown("---")
    
    st.markdown("""
    ### 3. 🤖 La Detección Automática Supera la Inspección Visual
    
    **Ventajas del análisis automatizado:**
    - Detecta eventos sutiles que podrían pasar desapercibidos
    - Mantiene consistencia entre múltiples experimentos
    - Elimina sesgo del observador
    - Escala a cientos de células simultáneamente
    
    **Validación:**
    - Zonas sombreadas (eventos detectados) corresponden visualmente a cambios en la señal
    - Eventos de corta duración son capturados consistentemente
    - Falsos positivos son raros gracias a histéresis
    """)
    
    st.markdown("---")
    
    st.markdown("""
    ### 4. 📊 Múltiples Métricas Capturan Diferentes Aspectos
    
    Las diferentes métricas nos dan información complementaria:
    
    - **AUC Total** → Activación total acumulada
    - **AUC 1er Minuto** → Respuesta inicial rápida
    - **Máximo** → Intensidad pico de activación
    - **Duración** → Persistencia de la respuesta
    
    **Importancia:** Una sola métrica no cuenta la historia completa. Se necesita análisis multidimensional.
    """)
    
    st.markdown("---")
    
    # Recomendaciones
    st.markdown("## 🎯 Recomendaciones")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Para Análisis Futuros
        
        **A corto plazo:**
        - ✅ Implementar pipeline automatizado
        - ✅ Crear base de datos estructurada
        - ✅ Desarrollar alertas de calidad
        
        **A mediano plazo:**
        - 🔄 Análisis de clustering (identificar subpoblaciones)
        - 🔄 Análisis temporal fino (latencias, tiempos al pico)
        - 🔄 Comparaciones estadísticas formales
        """)
    
    with col2:
        st.markdown("""
        ### Para Investigación
        
        **Análisis avanzados:**
        - 🔬 Correlaciones entre células
        - 🔬 Análisis frecuencial (oscilaciones)
        - 🔬 Modelos predictivos
        - 🔬 Machine learning para clasificación
        
        **Integración:**
        - 🧪 Combinar con datos electrofisiológicos
        - 🧪 Correlacionar con datos genómicos
        """)
    
    st.markdown("---")
    
    # Reflexión final
    st.success("""
    ### 🌟 Reflexión Final
    
    Este análisis ha transformado archivos de texto sin procesar en un **recurso de conocimiento estructurado**. 
    
    La imagen de calcio no solo nos muestra picos y valles en un gráfico. Nos revela:
    - La **diversidad** de respuestas en una población celular
    - La **robustez** o **fragilidad** de mecanismos celulares
    - La **dinámica temporal** de procesos biológicos
    - Las **diferencias** entre condiciones que podrían ser clave para entender enfermedades
    
    Este panel no es solo una colección de gráficos. Es una **herramienta de descubrimiento**, 
    un **acelerador de investigación**, y un **puente** entre datos complejos y comprensión biológica.
    """)
    
    # Mostrar estadísticas finales si hay datos
    if 'results_df' in st.session_state:
        st.markdown("---")
        st.markdown("## 📈 Estadísticas del Análisis Actual")
        
        results_df = st.session_state.results_df
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total ROIs Analizadas", results_df['ROI'].nunique())
        with col2:
            st.metric("Total Estímulos", results_df['Stimuli'].nunique())
        with col3:
            st.metric("Total Eventos", len(results_df))
        with col4:
            avg_duration = results_df['duration'].mean()
            st.metric("Duración Promedio", f"{avg_duration:.2f} min")
