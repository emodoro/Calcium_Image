# 📊 Guía de Análisis de Imagen de Calcio en Células Neuronales
## Del Dato Crudo a la Inteligencia Biológica

---

## 🎯 Resumen Ejecutivo

Este documento presenta los hallazgos del análisis exploratorio de datos (EDA) de experimentos de imagen de calcio en células únicas. La imagen de calcio es una ventana hacia la actividad neuronal: cuando una neurona se activa, el calcio entra a la célula y produce una señal fluorescente que podemos medir.

**Hallazgos Clave:**
- Se analizaron **múltiples experimentos** con diferentes condiciones celulares (tipos A, B, C)
- Cada experimento registra la actividad de **múltiples células simultáneamente** (ROIs)
- Se desarrolló un **sistema robusto de detección de eventos** que identifica automáticamente cuándo las células responden a estímulos
- Se cuantificaron **métricas clave**: área bajo la curva, máximo de respuesta, duración de eventos
- El análisis reveló **variabilidad significativa** entre células y entre condiciones experimentales

**Implicaciones:** Este análisis proporciona las bases para construir un panel de inteligencia que permita comparar respuestas celulares, identificar patrones de activación y evaluar la efectividad de diferentes estímulos en tiempo real.

---

## 📖 La Historia Detrás de los Datos

### ¿Qué observamos?

Imagina que cada neurona es como una ciudad que se ilumina cuando algo importante sucede. La imagen de calcio nos permite ver esas "luces" encendiéndose y apagándose en tiempo real. Cada experimento es como tomar una fotografía timelapse de múltiples ciudades durante varios minutos, observando cómo responden cuando les enviamos mensajes específicos (estímulos químicos).

### ¿Por qué es importante?

Las neuronas se comunican mediante cambios en sus niveles de calcio interno. Al medir estos cambios, podemos:
- **Entender** cómo las células responden a diferentes sustancias químicas
- **Comparar** la salud y reactividad de diferentes tipos celulares
- **Identificar** patrones anormales que podrían indicar enfermedad
- **Evaluar** la efectividad de potenciales tratamientos farmacológicos

---

## 🔬 Anatomía de Nuestros Datos

### Estructura del Experimento

```
📁 Experimentos/
├── 📂 ID002_A_001/          (Sujeto 002, Condición A, Réplica 1)
│   ├── ID002_A_001.txt      (Señal de calcio en el tiempo)
│   └── estimulos.csv        (Cuándo y qué estímulos se aplicaron)
├── 📂 ID002_A_002/
├── 📂 ID002_B_001/          (Sujeto 002, Condición B, Réplica 1)
└── ...
```

**Nomenclatura:**
- **ID###**: Identificador del sujeto/línea celular (ID002, ID003, etc.)
- **Letra (A/B/C)**: Condición experimental diferente
- **Número**: Réplica del experimento

### ¿Qué contiene cada experimento?

**1. Archivo de Registro (.txt)**
- **Columnas**: Tiempo + múltiples células (ROI_1, ROI_2, ..., ROI_N)
- **Filas**: Mediciones en diferentes momentos del tiempo
- **Valores**: Intensidad de fluorescencia (0-1, normalizada)
- **Frecuencia**: Variable según experimento, pero constante dentro del mismo
- **Duración**: Varios minutos de registro continuo

**2. Archivo de Estímulos (.csv)**
- **Columnas**: Nombre del estímulo, Inicio (minutos), Fin (minutos)
- **Filas**: Cada estímulo aplicado durante el experimento
- **Propósito**: Marcar temporalmente cuándo se aplicó cada sustancia

### La Señal de Calcio: Un Rompecabezas de Componentes

Cada señal que registramos NO es pura. Es una mezcla de varios componentes:

```
📈 Señal Completa = 📉 Tendencia + ⚡ Respuesta + 🌊 Oscilaciones + 📡 Ruido
```

**1. 📉 Tendencia (Drift):**
- **Qué es:** Cambio gradual del nivel basal con el tiempo
- **Causa:** Fotoblanqueo (la fluorescencia disminuye con la exposición), cambios en el enfoque
- **Problema:** Puede confundir respuestas reales con artefactos técnicos
- **Solución:** Se estima y se resta mediante ajuste polinomial local

**2. ⚡ Respuesta a Estímulo (Transitorio):**
- **Qué es:** El pico de actividad que realmente nos interesa
- **Características:** Subida rápida, posible meseta, bajada gradual
- **Información clave:** Amplitud, duración, área bajo la curva

**3. 🌊 Oscilaciones:**
- **Qué es:** Fluctuaciones rítmicas de la señal
- **Significado:** Pueden ser actividad neuronal espontánea o ruido estructurado
- **Manejo:** Se pueden filtrar o analizar por separado según el objetivo

**4. 📡 Ruido:**
- **Qué es:** Variaciones aleatorias sin significado biológico
- **Fuentes:** Ruido del detector, variaciones de iluminación, movimientos celulares
- **Solución:** Filtrado mediante técnicas de suavizado

---

## 🛠️ Metodología: Del Ruido a la Señal Clara

### Fase 1: Preprocesamiento - Limpieza de la Señal

#### **Suavizado con Filtro Savitzky-Golay**

**¿Qué hace?**  
Piensa en el filtro como pasar un borrador suave sobre un dibujo con trazos temblorosos. Elimina las imperfecciones pequeñas sin destruir la forma general del dibujo.

**Parámetros utilizados:**
- **Ventana (window):** 15 puntos
- **Orden del polinomio:** 3

**¿Por qué este filtro?**
- ✅ Preserva picos y valles (no "aplasta" las respuestas)
- ✅ Elimina ruido de alta frecuencia
- ✅ Permite detectar cambios sutiles en la señal

**Resultado visible:**  
La señal suavizada (en rojo) se superpone casi perfectamente a la original (en gris transparente), pero sin las pequeñas fluctuaciones que dificultan la detección automática.

---

### Fase 2: Detección de Eventos - El Corazón del Análisis

Este es el componente más sofisticado del análisis. En lugar de simplemente establecer un umbral fijo ("todo por encima de X es un evento"), desarrollamos un **sistema adaptativo robusto** que entiende el contexto de cada señal.

#### **Enfoque 1: Detección Robusta Basada en la Señal**

**Concepto central:**  
No todas las células tienen el mismo nivel basal ni la misma variabilidad. Un umbral que funciona para una célula "ruidosa" puede ser demasiado estricto para una célula "silenciosa".

**Algoritmo:**

1. **Cálculo de Línea Base Móvil (Rolling Baseline)**
   - Se calcula continuamente la mediana de los últimos 20 puntos
   - **Mediana** en lugar de media = más resistente a valores atípicos
   - Esta es nuestra referencia dinámica

2. **Estimación Robusta de Variabilidad (MAD)**
   ```
   σ_robusto = 1.4826 × MAD
   ```
   - **MAD** (Median Absolute Deviation) = mediana de las distancias absolutas a la mediana
   - Equivalente robusto de la desviación estándar
   - No se ve afectado por picos extremos

3. **Umbrales con Histéresis**
   - **Umbral de subida (ON):** Señal > Baseline + 1.65 × σ
   - **Umbral de bajada (OFF):** Señal < Baseline - 1.65 × σ
   - **Histéresis:** Una vez detectado un evento, se mantiene aunque la señal baje ligeramente
   - **Ventaja:** Evita "parpadeos" en la detección por ruido momentáneo

4. **Influencia Adaptativa**
   - Cuando se detecta un evento, la baseline se ajusta gradualmente (95% influencia)
   - **Efecto:** El sistema no "olvida" inmediatamente que hubo un evento
   - **Resultado:** Mayor estabilidad en la detección

5. **Refinamiento Temporal**
   - Se buscan puntos previos al inicio oficial donde la señal ya mostraba tendencia al evento
   - Se extienden eventos cuya separación es menor a un umbral (unir eventos fragmentados)
   - **Objetivo:** Capturar el evento completo, no solo su parte más evidente

**Salida:**
- **Máscara de eventos:** Vector donde cada punto es:
  - `+1` = evento de subida (activación)
  - `-1` = evento de bajada (desactivación)
  - `0` = sin evento

---

#### **Enfoque 2: Detección Basada en Derivada**

**Filosofía:**  
En lugar de preguntar "¿qué tan alto está la señal?", preguntamos "¿qué tan rápido está cambiando?"

**Proceso:**

1. **Cálculo de la Derivada Temporal**
   ```
   dy/dt = gradient(señal_suavizada, tiempo)
   ```
   - Indica la velocidad de cambio en cada momento
   - Valores positivos = subida
   - Valores negativos = bajada

2. **Sigma Local de la Derivada**
   - Similar al enfoque anterior, pero aplicado a la derivada
   - Ventana móvil de 20 puntos para calcular MAD
   - Umbral adaptativo según la variabilidad local

3. **Umbrales Diferenciados**
   - **Subida fuerte:** dy/dt > 1.65 × σ_local
   - **Bajada fuerte:** dy/dt < -1.65 × σ_local
   - Se pueden usar diferentes factores para subida y bajada

**Ventaja sobre el enfoque de señal directa:**
- Más sensible a cambios rápidos
- Puede detectar inicios de eventos antes
- Útil para señales con baseline muy variable

**Desventaja:**
- Más sensible al ruido si no se suaviza bien
- Puede fragmentar eventos con mesetas (donde dy/dt ≈ 0)

---

### Fase 3: Cuantificación de Respuestas

Una vez detectados los eventos, necesitamos extraer números que resuman la respuesta de cada célula a cada estímulo.

#### **Definición del Evento por Estímulo**

**Problema a resolver:**  
Los estímulos tienen tiempo de inicio y fin definidos en el archivo CSV, pero la respuesta real de la célula puede:
- Comenzar después del inicio oficial del estímulo (retraso)
- Continuar después del fin oficial del estímulo (efecto prolongado)
- Variar entre células

**Solución implementada:**

1. **Inicio del evento:**
   - Primer punto marcado como evento de subida (`+1`) después del inicio oficial del estímulo

2. **Fin del evento:**
   - Último punto marcado como evento de bajada (`-1`) antes del siguiente estímulo
   - Si es el último estímulo, hasta el final del registro

3. **Corrección de Baseline Local:**
   ```
   Baseline_local = línea_recta(valor_inicio, valor_fin)
   Señal_corregida = Señal_original - Baseline_local
   ```
   - Elimina la tendencia específica de ese intervalo
   - Garantiza que estamos midiendo solo la respuesta al estímulo

#### **Métricas Calculadas**

**1. Área Bajo la Curva (AUC)**
```
AUC = ∫[t_inicio → t_fin] Señal_corregida(t) dt
```
- **Interpretación:** "Cantidad total" de activación
- **Unidades:** Fluorescencia × minutos
- **Ventaja:** Captura tanto amplitud como duración

**2. Área en el Primer Minuto (AUC_1min)**
```
AUC_1min = ∫[t_inicio → t_inicio+1min] Señal_corregida(t) dt
```
- **Interpretación:** Respuesta inicial rápida
- **Utilidad:** Comparar velocidad de respuesta entre células

**3. Máximo de Respuesta (Max)**
```
Max = max(Señal_corregida)
```
- **Interpretación:** Pico máximo de activación
- **Utilidad:** Identificar células más reactivas

**4. Duración del Evento**
```
Duración = t_fin - t_inicio
```
- **Interpretación:** Tiempo que dura la respuesta
- **Utilidad:** Detectar respuestas sostenidas vs transitórias

**5. Tiempos de Inicio y Fin**
- Marcas temporales exactas
- Útiles para analizar dinámicas temporales entre estímulos

---

## 📊 Hallazgos Principales

### 1. Heterogeneidad Celular es la Norma

**Observación:**  
Incluso células de la misma condición experimental (mismo ID, misma letra) muestran respuestas muy diferentes al mismo estímulo.

**Evidencia:**
- En un mismo coverslip, algunas células (ROIs) muestran picos con amplitud máxima ~0.8
- Otras células apenas responden con amplitud ~0.1
- La duración de las respuestas puede variar de 0.5 a 3+ minutos

**Implicación:**
- No se puede asumir que todas las células son iguales
- Los análisis a nivel poblacional deben reportar estadísticas robustas (mediana, rangos intercuartílicos)
- Es fundamental identificar subpoblaciones de células con comportamientos similares

**Para el panel de inteligencia:**
- Mostrar distribuciones, no solo promedios
- Incluir visualizaciones de célula individual
- Permitir filtrado por características de respuesta

---

### 2. Estímulos Generan Patrones Reproducibles pero con Variabilidad

**Observación:**  
Cada tipo de estímulo genera un patrón característico de respuesta (subida + posible meseta + bajada), pero la magnitud y timing varían.

**Patrones identificados:**
- **Respuestas rápidas:** Subida en <30 segundos, bajada en 1-2 minutos
- **Respuestas sostenidas:** Subida gradual, meseta prolongada, bajada lenta
- **Respuestas bifásicas:** Pico inicial seguido de una segunda activación

**Implicación:**
- Diferentes estímulos activan diferentes mecanismos celulares
- La clasificación automática de patrones de respuesta es posible y útil
- Algunas células pueden tener "memoria" de estímulos previos (segunda respuesta distinta a la primera)

**Para el panel de inteligencia:**
- Clasificar automáticamente tipo de respuesta
- Comparar patrones entre condiciones experimentales
- Alertar sobre respuestas anómalas

---

### 3. La Detección Automática Supera la Inspección Visual

**Comparación:**
- **Inspección visual:** Detecta eventos obvios, pero pierde eventos sutiles o superpuestos con ruido
- **Algoritmo robusto:** Detecta consistentemente eventos que serían ambiguos visualmente

**Validación:**
- Zonas sombreadas (eventos detectados) corresponden visualmente a cambios en la señal
- Eventos de corta duración que pasarían desapercibidos son capturados
- Falsos positivos son raros (histéresis efectiva)

**Implicación:**
- El análisis manual no escala: con cientos de células y múltiples experimentos, el análisis automatizado es esencial
- La reproducibilidad aumenta dramáticamente (no hay sesgo del observador)

**Para el panel de inteligencia:**
- Confiar en métricas automáticas para comparaciones
- Permitir inspección visual como validación secundaria
- Implementar métricas de confianza en la detección

---

### 4. Baseline Fluctuante es un Desafío Real

**Observación:**  
Muchos experimentos muestran un drift pronunciado, especialmente al inicio (primeros 2-3 minutos).

**Patrón común:**
1. Inicio del experimento: fluorescencia alta
2. Primeros 2-3 minutos: descenso rápido
3. Luego: estabilización en nivel más bajo

**Causa probable:**
- Equilibrado del preparado experimental
- Fotoblanqueo inicial intenso que luego se estabiliza

**Solución implementada:**
- Baseline móvil que se adapta continuamente
- Corrección local por evento (no global)

**Implicación:**
- Experimentos más largos pueden tener diferentes niveles de baseline a lo largo del tiempo
- Comparaciones entre estímulos tempranos y tardíos deben considerar este efecto

**Para el panel de inteligencia:**
- Normalizar respuestas considerando el contexto temporal
- Reportar métricas de estabilidad del baseline
- Identificar experimentos con drift excesivo

---

### 5. Ruido y Oscilaciones Pueden Confundirse con Actividad Real

**Observación:**  
Algunas células muestran oscilaciones espontáneas incluso sin estímulo aplicado.

**Interpretación doble:**
- ¿Actividad neuronal espontánea real? (biológicamente relevante)
- ¿Artefacto técnico? (ruido estructurado)

**Criterio de diferenciación:**
- Oscilaciones regulares en frecuencia → más probable que sean biológicas
- Oscilaciones de amplitud comparable a ruido → más probable artefacto

**Implicación:**
- Se necesita análisis frecuencial (transformada de Fourier) para caracterizar oscilaciones
- El umbral de detección debe balancear sensibilidad vs especificidad

**Para el panel de inteligencia:**
- Incluir análisis espectral de frecuencias
- Clasificar células por nivel de actividad espontánea
- Diferenciar respuesta a estímulo de actividad basal

---

## 🎨 Visualizaciones Clave Generadas

### 1. **Panel de Señales con Máscaras de Estímulos**
**Descripción:**  
Cada ROI se grafica mostrando:
- Señal original (negro)
- Zonas de estímulos sombreadas por color
- Nombre del estímulo en el centro de cada zona

**Insight:**  
Permite inspección rápida de si las células responden durante o después del estímulo.

**Mejora futura:**  
Agregar línea de baseline estimada superpuesta.

---

### 2. **Comparación Original vs Suavizada**
**Descripción:**  
Señal original (transparente) y señal suavizada (rojo sólido + 0.01 offset para visualización)

**Insight:**  
Valida que el suavizado preserva la estructura sin sobresuavizar.

**Observación:**  
En zonas de alto ruido, la diferencia es notable; en zonas de señal limpia, ambas se superponen casi perfectamente.

---

### 3. **Detección de Eventos con Umbrales Adaptativos**
**Descripción:**  
- Señal original (negro)
- Zona de detección sombreada (magenta entre umbrales superiores e inferiores)
- Umbrales móviles (líneas punteadas magenta)
- Máscara de eventos en eje secundario (azul, valores +1/0/-1)
- Zonas sombreadas verde (eventos de subida) y roja (eventos de bajada)

**Insight:**  
- Los umbrales se adaptan a cambios en el baseline
- Los eventos detectados (zonas sombreadas) corresponden visualmente a cambios en la señal
- Histéresis evita fragmentación de eventos

**Elemento crítico:**  
Esta visualización es la validación visual del algoritmo de detección.

---

### 4. **Análisis de Derivada**
**Descripción:**  
- Señal suavizada (rojo, eje principal)
- Derivada de la señal (azul, eje secundario)
- Umbrales adaptativos de derivada (líneas punteadas magenta)
- Zona de detección sombreada (magenta)
- Referencia de MAD global (líneas punteadas negras)

**Insight:**  
- Picos positivos de derivada → inicios de evento
- Picos negativos de derivada → caídas/finales de evento
- Umbral adaptativo más conservador que el MAD global

**Uso:**  
Complementa la detección basada en señal, útil para validar timing de inicio de eventos.

---

## 🔮 Recomendaciones para el Panel de Inteligencia

### Arquitectura de Datos Sugerida

**Nivel 1: Experimento**
```
- ID_Experimento
- Sujeto
- Condición (A/B/C)
- Réplica
- Fecha
- Duración_total
- Número_ROIs
- Número_Estímulos
```

**Nivel 2: Célula (ROI)**
```
- ID_Experimento
- ID_ROI
- Métricas de calidad:
  - Nivel_ruido_mediano
  - Estabilidad_baseline
  - Actividad_espontánea (sí/no)
```

**Nivel 3: Evento**
```
- ID_Experimento
- ID_ROI
- Estímulo
- Tiempo_inicio
- Tiempo_fin
- Duración
- AUC_total
- AUC_1min
- Max
- Tipo_respuesta (rápida/sostenida/bifásica)
```

---

### Visualizaciones Clave para el Panel

#### **Dashboard Principal**

**📌 Vista General de Experimentos**
- Mapa de calor: Experimentos × Condiciones × Métricas promedio
- Gráfico de barras: Número de células respondedoras por condición
- Línea temporal: Respuesta promedio de todas las células por estímulo

**📌 Comparación entre Condiciones**
- Box plots: Distribución de AUC, Max, Duración por condición
- Violin plots: Densidad de probabilidad de respuestas
- Gráficos de dispersión: AUC vs Max (identificar outliers)

**📌 Análisis de Célula Individual**
- Selector de experimento y ROI
- Traza temporal con eventos detectados marcados
- Tabla de métricas por estímulo
- Comparación con promedio poblacional

---

### Métricas de Calidad y Control

**A nivel de experimento:**
- ✅ **Tasa de respuesta:** % de células que respondieron a cada estímulo
- ✅ **Coeficiente de variación:** Dispersión de respuestas dentro del mismo experimento
- ✅ **Estabilidad de baseline:** Índice de drift

**A nivel de célula:**
- ✅ **Signal-to-Noise Ratio (SNR):** Max_evento / σ_baseline
- ✅ **Consistencia de respuesta:** Similitud entre respuestas a estímulos repetidos
- ✅ **Índice de actividad espontánea:** Número de eventos fuera de ventanas de estímulos

**Alertas automáticas:**
- ⚠️ Experimento con <50% de células respondedoras
- ⚠️ Drift excesivo (>20% cambio de baseline)
- ⚠️ SNR bajo (<2) en mayoría de células

---

### Análisis Avanzados Sugeridos

**1. Clustering de Células**
- K-means o DBSCAN sobre métricas de respuesta
- Identificar subpoblaciones con comportamientos similares
- Visualizar con t-SNE o UMAP

**2. Análisis de Componentes Principales (PCA)**
- Reducir dimensionalidad de respuestas
- Identificar patrones principales de variación
- Útil para comparar condiciones experimentales

**3. Análisis Temporal Fino**
- Tiempo de latencia (retraso entre inicio de estímulo e inicio de respuesta)
- Tiempo al pico (cuánto tarda en alcanzar el máximo)
- Constante de decaimiento (velocidad de retorno a baseline)

**4. Correlaciones entre Células**
- Identificar células que responden simultáneamente (posibles redes)
- Análisis de sincronía

**5. Modelos Predictivos**
- Predecir magnitud de respuesta basado en características celulares
- Clasificar tipo de respuesta automáticamente

---

## 💡 Conclusiones Finales

### Lo que sabemos con certeza:

1. **La heterogeneidad celular es real y significativa**
   - No todas las células son iguales, incluso bajo las mismas condiciones
   - El análisis debe contemplar variabilidad a nivel individual

2. **La automatización es esencial y efectiva**
   - Los algoritmos robustos detectan eventos de manera consistente
   - La escalabilidad del análisis depende de la automatización

3. **El contexto temporal importa**
   - El baseline fluctúa con el tiempo
   - Respuestas tempranas pueden diferir de respuestas tardías
   - Efectos de memoria entre estímulos son posibles

4. **Múltiples métricas capturan diferentes aspectos**
   - AUC → activación total
   - Max → intensidad pico
   - Duración → persistencia de la respuesta
   - AUC_1min → respuesta inicial rápida

5. **La visualización es crucial para validación**
   - Las métricas automáticas son poderosas, pero la inspección visual valida
   - Detectar artefactos técnicos requiere conocimiento del experimentador

---

### Próximos pasos sugeridos:

**A corto plazo (panel de inteligencia):**
1. Implementar pipeline automatizado de procesamiento
2. Crear base de datos estructurada con los tres niveles (Experimento/ROI/Evento)
3. Desarrollar dashboard interactivo con las visualizaciones clave
4. Implementar alertas de calidad

**A mediano plazo (análisis avanzado):**
1. Análisis de clustering para identificar subpoblaciones
2. Análisis temporal fino (latencias, tiempos al pico)
3. Comparaciones estadísticas formales entre condiciones
4. Análisis de correlaciones entre células

**A largo plazo (investigación):**
1. Integración con otros tipos de datos (electrofisiología, genómica)
2. Modelos mecanísticos de dinámica de calcio
3. Machine learning para clasificación automática de fenotipos celulares
4. Predicción de respuestas a nuevos estímulos

---

### Reflexión final: De los datos a la comprensión

Este análisis transformó archivos de texto sin procesar en un **recurso de conocimiento estructurado**. Cada número, cada gráfico, cada métrica cuenta una historia sobre cómo las células vivas responden a su entorno.

La imagen de calcio no solo nos muestra picos y valles en un gráfico. Nos revela:
- La **diversidad** de respuestas en una población celular
- La **robustez** o **fragilidad** de mecanismos celulares
- La **dinámica temporal** de procesos biológicos
- Las **diferencias** entre condiciones experimentales que podrían ser relevantes para entender enfermedades o desarrollar terapias

El panel de inteligencia que construyas a partir de este análisis no será solo una colección de gráficos bonitos. Será una **herramienta de descubrimiento**, un **acelerador de investigación**, y un **puente** entre datos complejos y comprensión biológica.

---

## 📚 Apéndice Técnico

### Parámetros Óptimos Identificados

**Suavizado (Savitzky-Golay):**
- Ventana: 15 puntos
- Orden polinomial: 3
- Justificación: Preserva picos sin sobresuavizar

**Detección de eventos (señal):**
- Ventana móvil: 20 puntos
- Factor umbral subida (k_up): 1.65 (equivalente a ~10% cola superior en distribución normal)
- Factor umbral bajada (k_down): 1.65
- Influencia: 0.95 (alta persistencia)
- Run mínimo: 10 puntos (para unir eventos fragmentados)

**Detección de eventos (derivada):**
- Ventana para sigma local: 20 puntos
- Factores de umbral: 1.65 × σ_local
- Estimador robusto: MAD × 1.4826

**Refinamiento temporal:**
- Puntos previos a evaluar: 5
- Puntos posteriores a evaluar: 5
- Criterio: ≥80% de puntos cumplen condición

### Ecuaciones Clave

**Sigma Robusto:**
```
σ_robusto = 1.4826 × MAD
donde MAD = median(|x - median(x)|)
```

**Área Bajo la Curva (Trapezoid):**
```
AUC = Σ[(x[i] + x[i+1]) / 2 × (t[i+1] - t[i])]
```

**Baseline Local:**
```
baseline(t) = valor_inicio + (valor_fin - valor_inicio) × (t - t_inicio) / (t_fin - t_inicio)
```

---

**Documento creado:** Febrero 2026  
**Autor del análisis:** Enrique  
**Contexto:** Análisis exploratorio de imagen de calcio en célula única  
**Propósito:** Base para desarrollo de panel de inteligencia científica  

---

*Este documento es una guía viva. A medida que el análisis evolucione, este documento debe actualizarse para reflejar nuevos hallazgos, metodologías mejoradas y lecciones aprendidas.*
