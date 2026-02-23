# 🚀 INICIO RÁPIDO - Panel de Imagen de Calcio

## ⚡ Ejecución en 3 Pasos

### 1. Instalar Dependencias (Primera vez solamente)

```bash
pip install -r requirements.txt
```

### 2. Ejecutar la Aplicación

**Opción A - Usando el script de inicio:**
```bash
python run.py
```

**Opción B - Directamente con Streamlit:**
```bash
streamlit run app.py
```

### 3. ¡Listo!

La aplicación se abrirá automáticamente en tu navegador en:
```
http://localhost:8501
```

---

## 📖 Uso Básico

### Primera Vez

1. **La aplicación carga automáticamente** el experimento de ejemplo: `ID002_A_002`
2. **Explora las secciones** usando el menú lateral:
   - 🏠 Inicio: Vista general
   - 📖 Origen: Información sobre los datos
   - 📊 Datos: Explicación de la señal
   - 🔬 EDA: **¡Análisis interactivo completo!**
   - 💡 Conclusiones: Hallazgos principales

3. **En la sección EDA** encontrarás:
   - Visualización de señales con estímulos
   - Comparación original vs suavizada
   - Detección automática de eventos
   - Cálculo de métricas (AUC, Máximo, Duración)
   - Descarga de resultados en CSV

### Usar tus Propios Datos

1. **Desmarca** "Usar archivos por defecto" en el menú lateral
2. **Sube** tu archivo `.txt` (señales de calcio)
3. **Sube** tu archivo `.csv` (información de estímulos)
4. **Ajusta parámetros** si es necesario
5. **¡Explora los resultados!**

---

## ⚙️ Parámetros Recomendados

### Para señales con poco ruido:
- Ventana de suavizado: **11-15**
- Factor umbral: **1.65**

### Para señales con mucho ruido:
- Ventana de suavizado: **21-31**
- Factor umbral: **2.0-2.5**

### Para eventos rápidos:
- Ventana baseline: **10-15**
- Puntos mínimos unir: **5-10**

### Para eventos lentos:
- Ventana baseline: **20-30**
- Puntos mínimos unir: **15-20**

---

## 💡 Consejos

✅ **Comienza con los parámetros por defecto** - están optimizados para la mayoría de casos

✅ **Visualiza señales individuales** primero antes de procesar todo

✅ **Ajusta parámetros gradualmente** y observa cambios en tiempo real

✅ **Descarga resultados en CSV** para análisis posterior en Excel/Python

✅ **Usa los filtros** para enfocarte en ROIs o estímulos específicos

---

## ❓ Problemas Comunes

### La aplicación no inicia
```bash
# Verifica que Streamlit esté instalado
pip install streamlit

# Verifica que estés en el directorio correcto
cd image_calcio
```

### Error al cargar datos
- Verifica que los archivos tengan el formato correcto (ver README.md)
- Asegúrate de que el CSV use `;` como separador
- Verifica que el decimal sea `,` en el CSV

### Procesamiento muy lento
- Reduce el número de ROIs seleccionadas
- Usa datos de ejemplo más pequeños
- Cierra otras aplicaciones pesadas

---

## 📊 Formato de Archivos

### Tu archivo .txt debe tener:
```
VERSION	1200
Time[MSec.]	Ratio	Ratio	...
%.1f	%.4f	%.4f	...
Time	ROI(1-1)	ROI(1-2)	...
GraphNo	1	2	...
0.0	0.243900	0.196900	...
```

### Tu archivo .csv debe tener:
```csv
;inicio;fin
nombre_estimulo;3;20
otro_estimulo;20;23
```

---

## 🆘 Soporte

Para más información:
- 📖 Ver `README.md` - Documentación completa
- 📚 Ver `GUIA_ANALISIS_IMAGEN_CALCIO.md` - Metodología detallada
- 💻 Ver `notebooks/imagen_calcio.ipynb` - Código de referencia

---

**¡Disfruta del análisis! 🧬**
