"""
Módulo para el procesamiento y carga de datos de imagen de calcio.
Contiene funciones para leer archivos .txt y .csv, y preparar los datos para análisis.
"""

import pandas as pd
import numpy as np
import os
from config import *


class CalciumDataLoader:
    """
    Clase para cargar y gestionar datos de imagen de calcio.
    
    Attributes:
        txt_path (str): Ruta al archivo de registro .txt
        csv_path (str): Ruta al archivo de estímulos .csv
        data (pd.DataFrame): DataFrame con datos de señal de calcio
        stimuli_data (pd.DataFrame): DataFrame con información de estímulos
    """
    
    def __init__(self, txt_path=None, csv_path=None):
        """
        Inicializa el cargador de datos.
        
        Args:
            txt_path (str, optional): Ruta al archivo .txt. Si es None, usa ruta por defecto.
            csv_path (str, optional): Ruta al archivo .csv. Si es None, usa ruta por defecto.
        """
        self.txt_path = txt_path or DEFAULT_TXT_FILE
        self.csv_path = csv_path or DEFAULT_CSV_FILE
        self.data = None
        self.stimuli_data = None
        self.time_array = None
        self.roi_columns = None
        
    def load_txt_data(self):
        """
        Carga el archivo .txt con datos de imagen de calcio.
        
        Returns:
            pd.DataFrame: DataFrame con columna Time y columnas ROI_n
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            ValueError: Si el formato del archivo es incorrecto
        """
        if not os.path.exists(self.txt_path):
            raise FileNotFoundError(f"Archivo no encontrado: {self.txt_path}")
        
        try:
            # Leer archivo .txt con configuración específica
            self.data = pd.read_csv(
                self.txt_path, 
                sep=TXT_SEPARATOR, 
                skiprows=TXT_SKIPROWS, 
                header=TXT_HEADER
            )
            
            # Renombrar columnas: Time + ROI_1, ROI_2, ...
            self.data.columns = ['Time'] + [f'ROI_{i}' for i in range(1, len(self.data.columns))]
            
            # Convertir tiempo de milisegundos a minutos
            self.data['Time'] = self.data['Time'] / MS_TO_MIN
            
            # Guardar array de tiempo y columnas de ROIs
            self.time_array = self.data['Time'].to_numpy()
            self.roi_columns = [col for col in self.data.columns if col.startswith('ROI_')]
            
            return self.data
            
        except Exception as e:
            raise ValueError(f"Error al leer archivo .txt: {str(e)}")
    
    def load_csv_data(self):
        """
        Carga el archivo .csv con información de estímulos.
        
        Returns:
            pd.DataFrame: DataFrame con columnas de nombre, inicio y fin de estímulos
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            ValueError: Si el formato del archivo es incorrecto
        """
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"Archivo no encontrado: {self.csv_path}")
        
        try:
            # Leer archivo .csv con configuración específica
            self.stimuli_data = pd.read_csv(
                self.csv_path, 
                sep=CSV_SEPARATOR, 
                decimal=CSV_DECIMAL
            )
            
            # Convertir nombres de estímulos a mayúsculas para consistencia
            self.stimuli_data.iloc[:, 0] = self.stimuli_data.iloc[:, 0].str.upper()
            
            return self.stimuli_data
            
        except Exception as e:
            raise ValueError(f"Error al leer archivo .csv: {str(e)}")
    
    def load_all_data(self):
        """
        Carga tanto datos de señal como de estímulos.
        
        Returns:
            tuple: (data DataFrame, stimuli_data DataFrame)
        """
        self.load_txt_data()
        self.load_csv_data()
        return self.data, self.stimuli_data
    
    def get_roi_data(self, roi_name):
        """
        Obtiene los datos de una ROI específica.
        
        Args:
            roi_name (str): Nombre de la ROI (ej: 'ROI_1')
            
        Returns:
            np.ndarray: Array con los valores de la ROI
        """
        if self.data is None:
            raise ValueError("Datos no cargados. Ejecuta load_txt_data() primero.")
        
        if roi_name not in self.data.columns:
            raise ValueError(f"ROI {roi_name} no encontrada en los datos.")
        
        return self.data[roi_name].to_numpy()
    
    def get_stimulus_info(self, stimulus_name):
        """
        Obtiene información de un estímulo específico.
        
        Args:
            stimulus_name (str): Nombre del estímulo
            
        Returns:
            dict: Diccionario con 'inicio', 'fin' y 'duracion' del estímulo
        """
        if self.stimuli_data is None:
            raise ValueError("Datos de estímulos no cargados. Ejecuta load_csv_data() primero.")
        
        stimulus_row = self.stimuli_data[self.stimuli_data.iloc[:, 0] == stimulus_name.upper()]
        
        if stimulus_row.empty:
            raise ValueError(f"Estímulo {stimulus_name} no encontrado.")
        
        return {
            'inicio': stimulus_row['inicio'].values[0],
            'fin': stimulus_row['fin'].values[0],
            'duracion': stimulus_row['fin'].values[0] - stimulus_row['inicio'].values[0]
        }
    
    def create_stimulus_masks(self):
        """
        Crea máscaras binarias para cada estímulo.
        
        Returns:
            dict: Diccionario con máscaras por estímulo (1 = sin estímulo, 0 = con estímulo)
        """
        if self.data is None or self.stimuli_data is None:
            raise ValueError("Datos no cargados completamente.")
        
        masks = {}
        total_mask = np.ones(len(self.data))  # Máscara total combinada
        
        # Iterar sobre cada estímulo
        for index, row in self.stimuli_data.iterrows():
            start_time = row['inicio']
            end_time = row['fin']
            stimulus_name = row.iloc[0]
            
            # Crear máscara individual: 1 fuera del estímulo, 0 dentro
            mask = np.ones(len(self.data))
            mask[(self.data['Time'] >= start_time) & (self.data['Time'] <= end_time)] = 0
            
            masks[stimulus_name] = mask
            total_mask *= mask  # Combinar todas las máscaras
        
        masks['TOTAL'] = total_mask
        return masks
    
    def get_data_summary(self):
        """
        Genera un resumen de los datos cargados.
        
        Returns:
            dict: Diccionario con información sobre los datos
        """
        if self.data is None:
            return {"error": "Datos no cargados"}
        
        summary = {
            'num_rois': len(self.roi_columns),
            'roi_names': self.roi_columns,
            'duration_minutes': self.time_array[-1] - self.time_array[0],
            'num_timepoints': len(self.time_array),
            'sampling_rate_hz': 1 / (np.mean(np.diff(self.time_array)) * 60),  # Aproximado
            'num_stimuli': len(self.stimuli_data) if self.stimuli_data is not None else 0,
            'stimuli_names': self.stimuli_data.iloc[:, 0].tolist() if self.stimuli_data is not None else []
        }
        
        return summary


def validate_uploaded_files(txt_file, csv_file):
    """
    Valida que los archivos subidos tengan el formato correcto.
    
    Args:
        txt_file: Archivo .txt subido
        csv_file: Archivo .csv subido
        
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    # Validar extensiones
    if txt_file is not None and not txt_file.name.endswith('.txt'):
        return False, "El archivo de registro debe ser .txt"
    
    if csv_file is not None and not csv_file.name.endswith('.csv'):
        return False, "El archivo de estímulos debe ser .csv"
    
    return True, "Archivos válidos"
