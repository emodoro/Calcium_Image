"""
Script de inicio rápido para la aplicación.
Ejecuta este archivo para lanzar el panel de inteligencia.
"""

import subprocess
import sys
import os

def main():
    """
    Función principal que ejecuta la aplicación de Streamlit.
    """
    print("=" * 60)
    print("  Panel de Inteligencia - Imagen de Calcio Neuronal")
    print("=" * 60)
    print()
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('app.py'):
        print("❌ Error: No se encuentra app.py")
        print("   Asegúrate de ejecutar este script desde el directorio raíz del proyecto")
        sys.exit(1)
    
    # Verificar dependencias
    print("🔍 Verificando dependencias...")
    try:
        import streamlit
        import pandas
        import numpy
        import scipy
        import plotly
        print("✅ Todas las dependencias están instaladas")
    except ImportError as e:
        print(f"❌ Falta instalar dependencias: {e}")
        print("   Ejecuta: pip install -r requirements.txt")
        sys.exit(1)
    
    print()
    print("🚀 Iniciando aplicación...")
    print()
    print("La aplicación se abrirá en tu navegador")
    print("URL: http://localhost:8501")
    print()
    print("Para detener la aplicación, presiona Ctrl+C")
    print("=" * 60)
    print()
    
    # Ejecutar Streamlit
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print()
        print("=" * 60)
        print("✅ Aplicación detenida correctamente")
        print("=" * 60)
    except Exception as e:
        print(f"❌ Error al ejecutar la aplicación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
