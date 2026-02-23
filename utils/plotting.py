"""
Módulo para creación de visualizaciones interactivas con Plotly.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from config import STIMULUS_COLORS


class CalciumPlotter:
    """
    Clase para crear visualizaciones de datos de imagen de calcio.
    """
    
    @staticmethod
    def plot_signal_with_stimuli(time, signal, stimuli_data, 
                                 title="Señal de Calcio con Estímulos",
                                 roi_name="ROI"):
        """
        Crea gráfico de señal con zonas de estímulos sombreadas.
        
        Args:
            time (np.ndarray): Array de tiempo
            signal (np.ndarray): Array de señal
            stimuli_data (pd.DataFrame): DataFrame con información de estímulos
            title (str): Título del gráfico
            roi_name (str): Nombre de la ROI
            
        Returns:
            plotly.graph_objects.Figure: Figura de Plotly
        """
        fig = go.Figure()
        
        # Agregar señal principal
        fig.add_trace(go.Scatter(
            x=time,
            y=signal,
            mode='lines',
            name='Señal Original',
            line=dict(color='black', width=1)
        ))
        
        # Agregar zonas de estímulos
        for i in range(len(stimuli_data)):
            row = stimuli_data.iloc[i]
            
            # Obtener nombre del estímulo
            if 'Stimuli' in stimuli_data.columns:
                stimulus_name = str(row['Stimuli'])
            elif stimuli_data.columns[0] not in ['inicio', 'fin']:
                stimulus_name = str(row.iloc[0])
            else:
                stimulus_name = f"Estímulo {i+1}"
            
            start_time = row['inicio']
            end_time = row['fin']
            color = STIMULUS_COLORS[i % len(STIMULUS_COLORS)]
            
            # Zona sombreada
            fig.add_vrect(
                x0=start_time,
                x1=end_time,
                fillcolor=color,
                opacity=0.2,
                layer="below",
                line_width=0,
            )
            
            # Anotación del estímulo
            fig.add_annotation(
                x=(start_time + end_time) / 2,
                y=max(signal) * 0.9,
                text=stimulus_name,
                showarrow=False,
                font=dict(size=10, color=color),
                textangle=0
            )
        
        fig.update_layout(
            title=f"{title} - {roi_name}",
            xaxis_title="Tiempo (min)",
            yaxis_title="Intensidad de Fluorescencia (ratio)",
            hovermode='x unified',
            template='plotly_white',
            height=500
        )
        
        return fig
    
    @staticmethod
    def plot_original_vs_smoothed(time, original, smoothed, roi_name="ROI"):
        """
        Compara señal original vs suavizada.
        
        Args:
            time (np.ndarray): Array de tiempo
            original (np.ndarray): Señal original
            smoothed (np.ndarray): Señal suavizada
            roi_name (str): Nombre de la ROI
            
        Returns:
            plotly.graph_objects.Figure: Figura de Plotly
        """
        fig = go.Figure()
        
        # Señal original (transparente)
        fig.add_trace(go.Scatter(
            x=time,
            y=original,
            mode='lines',
            name='Original',
            line=dict(color='gray', width=1),
            opacity=0.5
        ))
        
        # Señal suavizada (desplazada ligeramente para visualización)
        fig.add_trace(go.Scatter(
            x=time,
            y=smoothed + 0.01,
            mode='lines',
            name='Suavizada (+0.01)',
            line=dict(color='red', width=2)
        ))
        
        fig.update_layout(
            title=f"Comparación: Original vs Suavizada - {roi_name}",
            xaxis_title="Tiempo (min)",
            yaxis_title="Intensidad de Fluorescencia",
            hovermode='x unified',
            template='plotly_white',
            height=500
        )
        
        return fig
    
    @staticmethod
    def plot_event_detection(time, signal, event_mask, baseline, std_dev, 
                            k_up=1.65, k_down=1.65, roi_name="ROI", stimuli_data=None):
        """
        Visualiza detección de eventos con umbrales adaptativos.
        
        Args:
            time (np.ndarray): Array de tiempo
            signal (np.ndarray): Señal procesada
            event_mask (np.ndarray): Máscara de eventos
            baseline (np.ndarray): Baseline móvil
            std_dev (np.ndarray): Desviación estándar móvil
            k_up (float): Factor umbral superior
            k_down (float): Factor umbral inferior
            roi_name (str): Nombre de la ROI
            stimuli_data (pd.DataFrame, optional): DataFrame con información de estímulos
            
        Returns:
            plotly.graph_objects.Figure: Figura de Plotly
        """
        # Crear subplots: señal arriba, máscara abajo
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=(f'Señal y Umbrales - {roi_name}', 'Eventos Detectados'),
            row_heights=[0.7, 0.3]
        )
        
        # --- Subplot 1: Señal con umbrales ---
        # Señal original
        fig.add_trace(go.Scatter(
            x=time, y=signal,
            mode='lines',
            name='Señal',
            line=dict(color='black', width=1)
        ), row=1, col=1)
        
        # Zona de detección (relleno entre umbrales)
        upper_threshold = baseline + k_up * std_dev
        lower_threshold = baseline - k_down * std_dev
        
        fig.add_trace(go.Scatter(
            x=time, y=upper_threshold,
            mode='lines',
            name='Umbral Superior',
            line=dict(color='magenta', width=1, dash='dot'),
            showlegend=True
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=time, y=lower_threshold,
            mode='lines',
            name='Umbral Inferior',
            line=dict(color='magenta', width=1, dash='dot'),
            fill='tonexty',
            fillcolor='rgba(255, 0, 255, 0.1)',
            showlegend=True
        ), row=1, col=1)
        
        # --- Subplot 2: Máscara de eventos ---
        fig.add_trace(go.Scatter(
            x=time, y=event_mask,
            mode='lines',
            name='Eventos',
            line=dict(color='blue', width=1),
            showlegend=False
        ), row=2, col=1)
        
        # Línea horizontal en 0
        fig.add_hline(y=0, line_dash="dash", line_color="black", 
                     opacity=0.5, row=2, col=1)
        
        # Sombrear zonas de eventos
        # Eventos de subida (verde)
        up_events = event_mask > 0
        for i in range(1, len(up_events)):
            if up_events[i] and not up_events[i-1]:  # Inicio
                start_idx = i
            elif not up_events[i] and up_events[i-1]:  # Fin
                fig.add_vrect(
                    x0=time[start_idx], x1=time[i-1],
                    fillcolor="green", opacity=0.2,
                    layer="below", line_width=0,
                    row=2, col=1
                )
        
        # Eventos de bajada (rojo)
        down_events = event_mask < 0
        for i in range(1, len(down_events)):
            if down_events[i] and not down_events[i-1]:  # Inicio
                start_idx = i
            elif not down_events[i] and down_events[i-1]:  # Fin
                fig.add_vrect(
                    x0=time[start_idx], x1=time[i-1],
                    fillcolor="red", opacity=0.2,
                    layer="below", line_width=0,
                    row=2, col=1
                )
        
        # --- AHORA agregar bandas de estímulos DESPUÉS de las trazas ---
        if stimuli_data is not None:
            print(f"DEBUG: Procesando {len(stimuli_data)} estímulos")
            print(f"DEBUG: Columnas del DataFrame: {stimuli_data.columns.tolist()}")
            print(f"DEBUG: Rango de tiempo: {time[0]:.2f} a {time[-1]:.2f}")
            
            for i in range(len(stimuli_data)):
                row = stimuli_data.iloc[i]
                
                # Obtener nombre del estímulo
                if 'Stimuli' in stimuli_data.columns:
                    stimulus_name = str(row['Stimuli'])
                elif stimuli_data.columns[0] not in ['inicio', 'fin']:
                    stimulus_name = str(row.iloc[0])
                else:
                    stimulus_name = f"Estímulo {i+1}"
                
                start_time = row['inicio']
                end_time = row['fin']
                color = STIMULUS_COLORS[i % len(STIMULUS_COLORS)]
                
                print(f"DEBUG: Estímulo {i}: '{stimulus_name}' - Inicio: {start_time}, Fin: {end_time}, Color: {color}")
                
                # Banda vertical completa en subplot 1 (señal y umbrales)
                fig.add_vrect(
                    x0=start_time,
                    x1=end_time,
                    fillcolor=color,
                    opacity=0.3,
                    line_width=0,
                    row=1, col=1
                )
                
                # Banda vertical completa en subplot 2 (eventos detectados)
                fig.add_vrect(
                    x0=start_time,
                    x1=end_time,
                    fillcolor=color,
                    opacity=0.3,
                    line_width=0,
                    row=2, col=1
                )
                
                # Líneas verticales delimitadoras en subplot 1
                fig.add_vline(
                    x=start_time,
                    line_width=2,
                    line_dash="dash",
                    line_color=color,
                    opacity=0.8,
                    row=1, col=1
                )
                fig.add_vline(
                    x=end_time,
                    line_width=2,
                    line_dash="dash",
                    line_color=color,
                    opacity=0.8,
                    row=1, col=1
                )
                
                # Líneas verticales delimitadoras en subplot 2
                fig.add_vline(
                    x=start_time,
                    line_width=2,
                    line_dash="dash",
                    line_color=color,
                    opacity=0.8,
                    row=2, col=1
                )
                fig.add_vline(
                    x=end_time,
                    line_width=2,
                    line_dash="dash",
                    line_color=color,
                    opacity=0.8,
                    row=2, col=1
                )
                
                # Anotación del estímulo en subplot 1
                fig.add_annotation(
                    x=(start_time + end_time) / 2,
                    y=max(signal) * 0.95,
                    text=stimulus_name,
                    showarrow=False,
                    font=dict(size=10, color=color, family="Arial Black"),
                    textangle=0,
                    row=1, col=1
                )
        
        fig.update_xaxes(title_text="Tiempo (min)", row=2, col=1)
        fig.update_yaxes(title_text="Fluorescencia", row=1, col=1)
        fig.update_yaxes(title_text="Evento", row=2, col=1)
        
        fig.update_layout(
            height=700,
            hovermode='x unified',
            template='plotly_white',
            showlegend=True
        )
        
        return fig
    
    @staticmethod
    def plot_metrics_comparison(results_df, metric='area_total', group_by='Stimuli'):
        """
        Crea gráfico de comparación de métricas.
        
        Args:
            results_df (pd.DataFrame): DataFrame con resultados
            metric (str): Métrica a visualizar
            group_by (str): Variable para agrupar ('Stimuli' o 'ROI')
            
        Returns:
            plotly.graph_objects.Figure: Figura de Plotly
        """
        if metric not in results_df.columns:
            raise ValueError(f"Métrica {metric} no encontrada en resultados")
        
        # Crear boxplot
        fig = px.box(
            results_df,
            x=group_by,
            y=metric,
            color=group_by,
            title=f"Comparación de {metric.replace('_', ' ').title()} por {group_by}",
            points="all",  # Mostrar todos los puntos
            hover_data=results_df.columns
        )
        
        fig.update_layout(
            xaxis_title=group_by,
            yaxis_title=metric.replace('_', ' ').title(),
            template='plotly_white',
            height=500,
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def plot_heatmap(results_df, metric='area_total'):
        """
        Crea heatmap de métricas por ROI y Estímulo.
        
        Args:
            results_df (pd.DataFrame): DataFrame con resultados
            metric (str): Métrica a visualizar
            
        Returns:
            plotly.graph_objects.Figure: Figura de Plotly
        """
        # Pivotar datos
        pivot_data = results_df.pivot(index='ROI', columns='Stimuli', values=metric)
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_data.values,
            x=pivot_data.columns,
            y=pivot_data.index,
            colorscale='Viridis',
            text=np.round(pivot_data.values, 3),
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title=metric.replace('_', ' ').title())
        ))
        
        fig.update_layout(
            title=f"Heatmap: {metric.replace('_', ' ').title()} por ROI y Estímulo",
            xaxis_title="Estímulo",
            yaxis_title="ROI",
            template='plotly_white',
            height=600
        )
        
        return fig
    
    @staticmethod
    def plot_summary_stats(results_df):
        """
        Crea dashboard de estadísticas resumen.
        
        Args:
            results_df (pd.DataFrame): DataFrame con resultados
            
        Returns:
            plotly.graph_objects.Figure: Figura de Plotly
        """
        # Crear subplots para diferentes métricas
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Área Total', 'Área 1er Minuto', 'Máximo', 'Duración'),
            specs=[[{"type": "box"}, {"type": "box"}],
                   [{"type": "box"}, {"type": "box"}]]
        )
        
        metrics = ['area_total', 'area_1min', 'max_value', 'duration']
        positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
        
        for metric, (row, col) in zip(metrics, positions):
            for stimulus in results_df['Stimuli'].unique():
                data = results_df[results_df['Stimuli'] == stimulus][metric]
                fig.add_trace(
                    go.Box(y=data, name=stimulus, showlegend=(row==1 and col==1)),
                    row=row, col=col
                )
        
        fig.update_layout(
            height=800,
            title_text="Resumen de Métricas por Estímulo",
            template='plotly_white'
        )
        
        return fig
