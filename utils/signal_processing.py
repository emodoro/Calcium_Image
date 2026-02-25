"""
Módulo para procesamiento de señales de calcio.
Implementa algoritmos de suavizado, detección de eventos y cálculo de métricas.
"""

import numpy as np
import pandas as pd
from scipy import signal
from scipy.integrate import trapezoid
from config import *


class SignalProcessor:
    """
    Clase para procesar señales de imagen de calcio.
    Implementa suavizado, detección robusta de eventos y cálculo de métricas.
    """
    
    def __init__(self, signal_data, time_array):
        """
        Inicializa el procesador de señales.
        
        Args:
            signal_data (np.ndarray): Array con datos de señal
            time_array (np.ndarray): Array con puntos de tiempo
        """
        self.original_signal = signal_data
        self.time = time_array
        self.smoothed_signal = None
        self.event_mask = None
        
    def apply_savgol_filter(self, window=SG_WINDOW, polyorder=SG_POLYORDER):
        """
        Aplica filtro Savitzky-Golay para suavizar la señal.
        
        Args:
            window (int): Tamaño de ventana (debe ser impar)
            polyorder (int): Orden del polinomio de ajuste
            
        Returns:
            np.ndarray: Señal suavizada
        """
        # Asegurar que window es impar
        if window % 2 == 0:
            window += 1
        
        self.smoothed_signal = signal.savgol_filter(
            self.original_signal, 
            window_length=window, 
            polyorder=polyorder
        )
        
        return self.smoothed_signal
    
    def robust_event_detection(self, 
                               w=SIGNAL_WINDOW, 
                               k_up=K_UP, 
                               k_down=K_DOWN,
                               influence=INFLUENCE,
                               use_smoothed=True,
                               run_min=RUN_MIN,
                               adyacent_pre_points=5,
                               adyacent_post_points=5):
        """
        Detección robusta de eventos usando baseline móvil y umbrales adaptativos.
        Implementa el mismo enfoque que el notebook: dos máscaras separadas para subidas y bajadas
        que se combinan en una sola máscara.
        
        Args:
            w (int): Ventana para baseline móvil
            k_up (float): Factor umbral para eventos de subida
            k_down (float): Factor umbral para eventos de bajada
            influence (float): Influencia del nuevo valor en baseline (0-1)
            use_smoothed (bool): Si True, usa señal suavizada
            run_min (int): Puntos mínimos para unir eventos fragmentados
            adyacent_pre_points (int): Puntos previos a evaluar para extender eventos
            adyacent_post_points (int): Puntos posteriores a evaluar para extender eventos
            
        Returns:
            tuple: (event_mask, baseline, std_dev) donde:
                - event_mask: Array con 1=subida, -1=bajada, 0=sin evento
                - baseline: Array con baseline móvil
                - std_dev: Array con desviación estándar móvil
        """
        # Seleccionar señal a procesar
        if use_smoothed and self.smoothed_signal is not None:
            x = self.smoothed_signal.copy()
        else:
            x = self.original_signal.copy()
        
        N = len(x)
        
        # Validar tamaño mínimo
        if N < w * 2:
            # Señal muy corta, retornar arrays vacíos
            return np.zeros(N), np.zeros(N), np.zeros(N)
        
        # --- MÁSCARA PARA SUBIDAS: k_up=k_up, k_down=k_down ---
        mask_up = self._detect_events_with_params(x, w, k_up, k_down, influence, run_min, 
                                                   adyacent_pre_points, adyacent_post_points)
        
        # --- MÁSCARA PARA BAJADAS: k_up=k_down*2 (como 1.65*2=3.29), k_down=k_down ---
        # Esto replica el comportamiento del notebook donde usa k_up=3.29 y k_down=1.65
        mask_down = self._detect_events_with_params(x, w, k_down * 2, k_down, influence, run_min,
                                                     adyacent_pre_points, adyacent_post_points)
        
        # --- COMBINAR MÁSCARAS como en el notebook ---
        event_mask = np.zeros(N)
        event_mask[mask_up == 1] = 1      # Subidas de mask_up
        event_mask[mask_down == -1] = -1  # Bajadas de mask_down
        
        # Calcular baseline y desviación para la máscara combinada
        # (usando los valores de la máscara para subidas para consistencia)
        _, baseline_array, std_array = self._detect_events_with_baseline(
            x, w, k_up, k_down, influence, run_min, 
            adyacent_pre_points, adyacent_post_points
        )
        
        self.event_mask = event_mask
        return event_mask, baseline_array, std_array
    
    def _detect_events_with_params(self, x, w, k_up, k_down, influence, run_min, 
                                    adyacent_pre_points, adyacent_post_points):
        """
        Detección de eventos con parámetros específicos. Retorna solo la máscara.
        """
        N = len(x)
        event_mask = np.zeros(N)
        x_filtered = x[:w].copy()
        
        # Baseline inicial
        baseline = np.nanmedian(x_filtered)
        std_dev = np.nanmedian(np.abs(x_filtered - baseline)) / 0.6745
        
        # Detección
        for i in range(w, N):
            difference = x[i] - baseline
            
            if (difference > k_up * std_dev and difference > 0) or (difference > 0 and event_mask[i-1] == 1):
                event_mask[i] = 1
                x_filtered = np.append(x_filtered, influence * x[i] + (1 - influence) * x_filtered[-1])
            elif (difference < -k_down * std_dev and difference < 0) or (difference < 0 and event_mask[i-1] == -1):
                event_mask[i] = -1
                x_filtered = np.append(x_filtered, influence * x[i] + (1 - influence) * x_filtered[-1])
            else:
                event_mask[i] = 0
                x_filtered = np.append(x_filtered, x[i])
            
            # Unir eventos cercanos
            if i > w + run_min:
                if event_mask[i] == 1 and np.sum(event_mask[i-run_min:i-1] == 1) > 0.8 * run_min:
                    event_mask[i-run_min:i] = 1
                elif event_mask[i] == -1 and np.sum(event_mask[i-run_min:i-1] == -1) > 0.8 * run_min:
                    event_mask[i-run_min:i] = -1
            
            x_filtered = x_filtered[-w:]
            baseline = np.nanmedian(x_filtered)
            mad = np.nanmedian(np.abs(x_filtered - baseline))
            std_dev = 1.4826 * mad
        
        # Refinar eventos
        puntos_previos = 5
        cambios = True
        while cambios:
            cambios = False
            for i in range(1, len(event_mask) - 1):
                if event_mask[i] == 1 and (np.sum(x[i-puntos_previos:i] <= x[i]) >= 0.8 * puntos_previos):
                    if event_mask[i-1] != 1:
                        event_mask[i-1] = 1
                        cambios = True
                elif event_mask[i] == -1 and (np.sum(x[i-puntos_previos:i] >= x[i]) >= 0.8 * puntos_previos):
                    if event_mask[i-1] != -1:
                        event_mask[i-1] = -1
                        cambios = True
        
        # Llenar huecos
        for i in range(adyacent_pre_points, len(event_mask) - adyacent_post_points - 1):
            if event_mask[i] == 0 and \
               np.any(event_mask[i-adyacent_pre_points:i] == 1) and \
               np.any(event_mask[i+1:i+1+adyacent_post_points] == 1):
                event_mask[i] = 1
            elif event_mask[i] == 0 and \
                 np.any(event_mask[i-adyacent_pre_points:i] == -1) and \
                 np.any(event_mask[i+1:i+1+adyacent_post_points] == -1):
                event_mask[i] = -1
        
        return event_mask
    
    def _detect_events_with_baseline(self, x, w, k_up, k_down, influence, run_min,
                                      adyacent_pre_points, adyacent_post_points):
        """
        Detección de eventos retornando máscara, baseline y desviación.
        """
        N = len(x)
        event_mask = np.zeros(N)
        x_filtered = x[:w].copy()
        baseline_array = np.zeros(N)
        std_array = np.zeros(N)
        
        baseline = np.nanmedian(x_filtered)
        std_dev = np.nanmedian(np.abs(x_filtered - baseline)) / 0.6745
        
        baseline_array[:w] = baseline
        std_array[:w] = std_dev
        
        for i in range(w, N):
            difference = x[i] - baseline
            
            if (difference > k_up * std_dev and difference > 0) or (difference > 0 and event_mask[i-1] == 1):
                event_mask[i] = 1
                x_filtered = np.append(x_filtered, influence * x[i] + (1 - influence) * x_filtered[-1])
            elif (difference < -k_down * std_dev and difference < 0) or (difference < 0 and event_mask[i-1] == -1):
                event_mask[i] = -1
                x_filtered = np.append(x_filtered, influence * x[i] + (1 - influence) * x_filtered[-1])
            else:
                event_mask[i] = 0
                x_filtered = np.append(x_filtered, x[i])
            
            if i > w + run_min:
                if event_mask[i] == 1 and np.sum(event_mask[i-run_min:i-1] == 1) > 0.8 * run_min:
                    event_mask[i-run_min:i] = 1
                elif event_mask[i] == -1 and np.sum(event_mask[i-run_min:i-1] == -1) > 0.8 * run_min:
                    event_mask[i-run_min:i] = -1
            
            x_filtered = x_filtered[-w:]
            baseline = np.nanmedian(x_filtered)
            mad = np.nanmedian(np.abs(x_filtered - baseline))
            std_dev = 1.4826 * mad
            
            baseline_array[i] = baseline
            std_array[i] = std_dev
        
        puntos_previos = 5
        cambios = True
        while cambios:
            cambios = False
            for i in range(1, len(event_mask) - 1):
                if event_mask[i] == 1 and (np.sum(x[i-puntos_previos:i] <= x[i]) >= 0.8 * puntos_previos):
                    if event_mask[i-1] != 1:
                        event_mask[i-1] = 1
                        cambios = True
                elif event_mask[i] == -1 and (np.sum(x[i-puntos_previos:i] >= x[i]) >= 0.8 * puntos_previos):
                    if event_mask[i-1] != -1:
                        event_mask[i-1] = -1
                        cambios = True
        
        for i in range(adyacent_pre_points, len(event_mask) - adyacent_post_points - 1):
            if event_mask[i] == 0 and \
               np.any(event_mask[i-adyacent_pre_points:i] == 1) and \
               np.any(event_mask[i+1:i+1+adyacent_post_points] == 1):
                event_mask[i] = 1
            elif event_mask[i] == 0 and \
                 np.any(event_mask[i-adyacent_pre_points:i] == -1) and \
                 np.any(event_mask[i+1:i+1+adyacent_post_points] == -1):
                event_mask[i] = -1
        
        self.event_mask = event_mask
        return event_mask, baseline_array, std_array
    
    def calculate_derivative(self):
        """
        Calcula la derivada de la señal suavizada.
        
        Returns:
            np.ndarray: Derivada temporal de la señal
        """
        if self.smoothed_signal is None:
            self.apply_savgol_filter()
        
        return np.gradient(self.smoothed_signal, self.time)
    
    def detect_event_bounds(self, event_mask=None):
        """
        Detecta los límites (inicio y fin) de cada evento en la máscara.
        
        Args:
            event_mask (np.ndarray, optional): Máscara de eventos. Si None, usa la calculada.
            
        Returns:
            dict: Diccionario con 'up_start', 'up_end', 'down_start', 'down_end'
        """
        if event_mask is None:
            event_mask = self.event_mask
        
        if event_mask is None:
            raise ValueError("No hay máscara de eventos. Ejecuta robust_event_detection() primero.")
        
        # Eventos de subida
        up_events = event_mask > 0
        up_starts = []
        up_ends = []
        
        # Eventos de bajada
        down_events = event_mask < 0
        down_starts = []
        down_ends = []
        
        # Detectar transiciones
        in_up_event = False
        in_down_event = False
        
        for i in range(1, len(event_mask)):
            # Eventos de subida
            if up_events[i] and not up_events[i-1]:  # Inicio de subida
                up_starts.append(self.time[i])
                in_up_event = True
            elif not up_events[i] and up_events[i-1]:  # Fin de subida
                up_ends.append(self.time[i-1])
                in_up_event = False
            
            # Eventos de bajada
            if down_events[i] and not down_events[i-1]:  # Inicio de bajada
                down_starts.append(self.time[i])
                in_down_event = True
            elif not down_events[i] and down_events[i-1]:  # Fin de bajada
                down_ends.append(self.time[i-1])
                in_down_event = False
        
        # Cerrar eventos que llegan hasta el final
        if in_up_event:
            up_ends.append(self.time[-1])
        if in_down_event:
            down_ends.append(self.time[-1])
        
        return {
            'up_start': up_starts,
            'up_end': up_ends,
            'down_start': down_starts,
            'down_end': down_ends
        }


def calculate_stimulus_metrics(signal_data, time_array, event_mask, 
                               stimulus_start, stimulus_end, next_stimulus_start=None):
    """
    Calcula métricas para un estímulo específico.
    
    Args:
        signal_data (np.ndarray): Datos de señal
        time_array (np.ndarray): Array de tiempo
        event_mask (np.ndarray): Máscara de eventos
        stimulus_start (float): Tiempo de inicio del estímulo
        stimulus_end (float): Tiempo de fin del estímulo
        next_stimulus_start (float, optional): Inicio del siguiente estímulo
        
    Returns:
        dict: Diccionario con métricas calculadas, o None si no hay datos válidos
    """
    try:
        # Determinar fin efectivo: hasta el siguiente estímulo o hasta el final
        effective_end = next_stimulus_start if next_stimulus_start is not None else time_array[-1]
        
        # Verificar que el rango temporal es válido
        valid_time_range = np.where((time_array >= stimulus_start) & (time_array <= effective_end))[0]
        if len(valid_time_range) == 0:
            # No hay puntos en el rango temporal
            return None


        
        # Encontrar primer evento de subida después del inicio del estímulo
        start_indices = np.where((time_array >= stimulus_start) & 
                                (time_array <= effective_end) & 
                                (event_mask == 1))[0]
        
        if len(start_indices) > 0:
            start_idx = start_indices[0]
        else:
            # Si no hay eventos de subida, usar el inicio del rango temporal
            fallback_start = np.where(time_array >= stimulus_start)[0]
            if len(fallback_start) == 0:
                return None
            start_idx = fallback_start[0]
        
        # Encontrar último evento de bajada DESPUÉS del evento de subida y antes del siguiente estímulo
        end_indices = np.where((time_array > time_array[start_idx]) & 
                              (time_array <= effective_end) & 
                              (event_mask == -1))[0]
        
        if len(end_indices) > 0:
            end_idx = end_indices[-1]
        else:
            # Si no hay eventos de bajada después de la subida, usar el fin del rango temporal
            fallback_end = np.where(time_array <= effective_end)[0]
            if len(fallback_end) == 0:
                return None
            end_idx = fallback_end[-1]
        
        # Verificar que tenemos un rango válido
        if start_idx >= end_idx or start_idx >= len(signal_data) or end_idx >= len(signal_data):
            return None
        
        # Extraer segmento de señal
        signal_segment = signal_data[start_idx:end_idx+1]
        time_segment = time_array[start_idx:end_idx+1]
        
        # Verificar que tenemos datos
        if len(signal_segment) < 2 or len(time_segment) < 2:
            return None
        
        # Calcular baseline local (línea recta entre inicio y fin)
        baseline_local = np.linspace(signal_segment[0], signal_segment[-1], len(signal_segment))
        
        # Señal corregida
        signal_corrected = signal_segment - baseline_local
        
        # Calcular métricas
        area_total = trapezoid(signal_corrected, time_segment)
        
        # Área en el primer minuto
        try:
            one_min_indices = int(1 / (time_array[1] - time_array[0]))
            area_1min = trapezoid(
                signal_corrected[:one_min_indices], 
                time_segment[:one_min_indices]
            ) if len(signal_corrected) > one_min_indices else area_total
        except:
            area_1min = area_total
        
        # Máximo
        max_value = np.max(signal_corrected)
        
        # Duración
        duration = time_segment[-1] - time_segment[0]
        
        return {
            'start_time': time_segment[0],
            'end_time': time_segment[-1],
            'duration': duration,
            'area_total': area_total,
            'area_1min': area_1min,
            'max_value': max_value,
            'signal_corrected': signal_corrected,
            'time_corrected': time_segment,
            'baseline_local': baseline_local
        }
    
    except Exception as e:
        # Si hay cualquier error, retornar None
        return None


def estimate_sampling_rate(time_array_minutes):
    """
    Estima la frecuencia de muestreo en Hz a partir de un array de tiempo en minutos.
    """
    if len(time_array_minutes) < 2:
        return 0.0
    dt_min = np.nanmedian(np.diff(time_array_minutes))
    dt_seconds = dt_min * 60.0
    if dt_seconds <= 0:
        return 0.0
    return 1.0 / dt_seconds


def interpolate_masked_signal(signal_data, keep_mask):
    """
    Interpola segmentos excluidos para mantener muestreo uniforme.

    Args:
        signal_data (np.ndarray): Señal original
        keep_mask (np.ndarray): True donde mantener la señal

    Returns:
        np.ndarray: Señal con segmentos excluidos interpolados
    """
    x = np.asarray(signal_data, dtype=float).copy()
    keep_mask = np.asarray(keep_mask, dtype=bool)
    if keep_mask.all():
        return x

    idx = np.arange(len(x))
    valid = keep_mask & np.isfinite(x)
    if valid.sum() < 2:
        return x

    x[~keep_mask] = np.interp(idx[~keep_mask], idx[valid], x[valid])
    return x


def apply_butter_filter(signal_data, sampling_rate_hz, filter_type,
                        cutoff_hz, order=4):
    """
    Aplica un filtro Butterworth con filtfilt.

    Args:
        signal_data (np.ndarray): Señal a filtrar
        sampling_rate_hz (float): Frecuencia de muestreo en Hz
        filter_type (str): 'lowpass', 'highpass', 'bandpass', 'bandstop'
        cutoff_hz (float or tuple): Frecuencias de corte en Hz
        order (int): Orden del filtro

    Returns:
        np.ndarray: Señal filtrada
    """
    if filter_type == 'none':
        return np.asarray(signal_data, dtype=float)

    if sampling_rate_hz <= 0:
        return np.asarray(signal_data, dtype=float)

    nyquist = 0.5 * sampling_rate_hz

    if isinstance(cutoff_hz, (tuple, list, np.ndarray)):
        if len(cutoff_hz) != 2 or cutoff_hz[0] is None or cutoff_hz[1] is None:
            return np.asarray(signal_data, dtype=float)
        if cutoff_hz[0] <= 0 or cutoff_hz[1] >= nyquist or cutoff_hz[0] >= cutoff_hz[1]:
            return np.asarray(signal_data, dtype=float)
        cutoff = [c / nyquist for c in cutoff_hz]
    else:
        if cutoff_hz is None or cutoff_hz <= 0 or cutoff_hz >= nyquist:
            return np.asarray(signal_data, dtype=float)
        cutoff = cutoff_hz / nyquist

    b, a = signal.butter(order, cutoff, btype=filter_type, analog=False)
    return signal.filtfilt(b, a, np.asarray(signal_data, dtype=float))


def compute_fft_spectrum(signal_data, sampling_rate_hz, detrend=True, window='hann'):
    """
    Calcula el espectro de magnitud usando FFT real.

    Args:
        signal_data (np.ndarray): Señal a analizar
        sampling_rate_hz (float): Frecuencia de muestreo en Hz
        detrend (bool): Restar la media antes de FFT
        window (str|None): 'hann' o None

    Returns:
        tuple: (freqs_hz, magnitude)
    """
    x = np.asarray(signal_data, dtype=float)
    if detrend:
        x = x - np.nanmean(x)

    if window == 'hann':
        win = np.hanning(len(x))
        x = x * win

    fft_vals = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(len(x), d=1.0 / sampling_rate_hz)
    magnitude = np.abs(fft_vals)
    return freqs, magnitude


def apply_fft_filter(signal_data, sampling_rate_hz, filter_type, cutoff_hz):
    """
    Filtra una señal en el dominio de la frecuencia usando FFT.

    Args:
        signal_data (np.ndarray): Señal a filtrar
        sampling_rate_hz (float): Frecuencia de muestreo en Hz
        filter_type (str): 'lowpass', 'highpass', 'bandpass', 'bandstop'
        cutoff_hz (float|tuple): Frecuencias de corte en Hz

    Returns:
        np.ndarray: Señal filtrada (tiempo)
    """
    if sampling_rate_hz <= 0 or filter_type == 'none':
        return np.asarray(signal_data, dtype=float)

    x = np.asarray(signal_data, dtype=float)
    n = len(x)
    freqs = np.fft.rfftfreq(n, d=1.0 / sampling_rate_hz)
    fft_vals = np.fft.rfft(x)

    mask = np.ones_like(freqs, dtype=bool)
    if filter_type == 'lowpass':
        mask = freqs <= cutoff_hz
    elif filter_type == 'highpass':
        mask = freqs >= cutoff_hz
    elif filter_type == 'bandpass':
        low, high = cutoff_hz
        mask = (freqs >= low) & (freqs <= high)
    elif filter_type == 'bandstop':
        low, high = cutoff_hz
        mask = (freqs < low) | (freqs > high)

    fft_vals[~mask] = 0.0
    return np.fft.irfft(fft_vals, n=n)
