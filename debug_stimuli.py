import sys
sys.path.insert(0, '.')
from utils.data_processor import CalciumDataLoader
from config import *

# Cargar datos
loader = CalciumDataLoader(DEFAULT_TXT_FILE, DEFAULT_CSV_FILE)
loader.load_all_data()

print('Estimulos data:')
print(loader.stimuli_data)
print()
print('Tipo:', type(loader.stimuli_data))
print('Columnas:', loader.stimuli_data.columns.tolist())
print()
print('Primera fila:')
print(loader.stimuli_data.iloc[0])
print()
print('Acceso a valores:')
for i in range(len(loader.stimuli_data)):
    row = loader.stimuli_data.iloc[i]
    print(f'  [{i}] Stimuli={row["Stimuli"]}, inicio={row["inicio"]}, fin={row["fin"]}')
