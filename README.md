# Simulación Estocástica de Tráfico Vehicular con Modelo Oculto de Markov (HMM)

![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Course](https://img.shields.io/badge/Asignatura-Simulación-orange.svg)
![Institution](https://img.shields.io/badge/Institución-IU%20Digital%20de%20Antioquia-blue)

Este repositorio contiene la implementación matemática, computacional y experimental de un **Modelo Oculto de Markov (Hidden Markov Model - HMM)** para modelar, simular y predecir la dinámica estocástica del tráfico vehicular en un corredor urbano arterial. 

Trabajo desarrollado para la **Actividad Didáctica 2 (Módulo 2: Distribuciones de Probabilidad y Procesos Estocásticos)**.

---

## 📋 Tabla de Contenidos
- [Descripción del Problema y Justificación](#-descripción-del-problema-y-justificación)
- [Fundamentación Matemática del HMM](#-fundamentación-matemática-del-hmm)
  - [Estados Ocultos vs. Observaciones Visibles](#estados-ocultos-vs-observaciones-visibles)
  - [Vector de Probabilidades Iniciales ($\pi$)](#vector-de-probabilidades-iniciales-pi)
  - [Matriz de Transición de Estados ($A$)](#matriz-de-transición-de-estados-a)
  - [Matriz de Emisión de Sensores ($B$)](#matriz-de-emisión-de-sensores-b)
- [Algoritmos Implementados](#-algoritmos-implementados)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Instalación y Requisitos](#-instalación-y-requisitos)
- [Instrucciones de Ejecución](#-instrucciones-de-ejecución)
  - [1. Ejecución del Script Principal](#1-ejecución-del-script-principal)
  - [2. Exploración Interactiva en Jupyter Notebook](#2-exploración-interactiva-en-jupyter-notebook)
  - [3. Generación del Informe Oficial en Word (.docx)](#3-generación-del-informe-oficial-en-word-docx)
- [Resultados Principales y Visualizaciones](#-resultados-principales-y-visualizaciones)
- [Equipo de Trabajo](#-equipo-de-trabajo)
- [Licencia](#-licencia)

---

## 🚗 Descripción del Problema y Justificación

El tráfico vehicular en corredores urbanos presenta una naturaleza intrínsecamente estocástica. Las condiciones de circulación no son deterministas, sino que fluctúan por decisiones individuales, efectos acordeón de frenado, horas pico e incidentes imprevistos.

### ¿Por qué un Modelo Oculto de Markov (HMM)?
En la realidad del monitoreo vial existen dos capas fundamentales:
1. **La Condición Macroscópica Real (Estado Oculto - Latente):** El nivel de servicio o grado de congestión global de una arteria vial ($Fluido$, $Moderado$, $Congestionado$) es una propiedad sistémica continua que no puede medirse de forma omnisciente ni directa en todo el corredor.
2. **Las Mediciones de Sensores (Observaciones Visibles):** Los radares de velocidad, cámaras y espiras electromagnéticas reportan velocidades puntuales ($Alta$, $Media$, $Baja$). Estas lecturas poseen **ruido e incertidumbre**: por ejemplo, un camión pesado en una vía fluida puede generar una lectura de velocidad baja, o en un trancón severo un automóvil puede acelerar brevemente produciendo una lectura de velocidad moderada.

El HMM desacopla el estado físico real de las evidencias ruidosas de los sensores, permitiendo reconstruir la trayectoria más probable del tráfico mediante inferencia probabilística.

---

## 📐 Fundamentación Matemática del HMM

El modelo se define formalmente mediante la tupla $\lambda = (\mathcal{S}, \mathcal{V}, \pi, A, B)$ para intervalos de tiempo $\Delta t = 15$ minutos (96 pasos por día):

### Estados Ocultos vs. Observaciones Visibles
* **Espacio de Estados Ocultos $\mathcal{S}$ ($N = 3$):**
  * $S_1 = \text{Fluido}$: Flujo libre, densidad baja ($\le 15 \text{ veh/km/carril}$).
  * $S_2 = \text{Moderado}$: Flujo continuo, densidad media ($15 - 35 \text{ veh/km/carril}$).
  * $S_3 = \text{Congestionado}$: Saturación, régimen stop-and-go ($> 35 \text{ veh/km/carril}$).

* **Espacio de Observaciones Visibles $\mathcal{V}$ ($M = 3$):**
  * $V_1 = \text{Velocidad Alta}$: $v > 60\text{ km/h}$.
  * $V_2 = \text{Velocidad Media}$: $30 \le v \le 60\text{ km/h}$.
  * $V_3 = \text{Velocidad Baja}$: $v < 30\text{ km/h}$.

### Vector de Probabilidades Iniciales ($\pi$)
Distribución al iniciar la observación a las 06:00 AM:
$$\pi = [\pi_{\text{Fluido}}, \pi_{\text{Moderado}}, \pi_{\text{Congestionado}}] = [0.70, 0.20, 0.10]$$

### Matriz de Transición de Estados ($A$)
Gobierna la inercia del tráfico entre intervalos consecutivos de 15 minutos ($a_{ij} = P(X_{t+1} = s_j \mid X_t = s_i)$):

$$A = \begin{pmatrix}
0.70 & 0.25 & 0.05 \\
0.20 & 0.60 & 0.20 \\
0.05 & 0.30 & 0.65
\end{pmatrix}$$

* **Inercia temporal:** Diagonal dominante ($0.70, 0.60, 0.65$), reflejando persistencia en el estado actual.
* **Gradualidad:** La transición directa $Fluido \to Congestionado$ es baja ($5\%$), requiriendo habitualmente pasar por $Moderado$ ($25\%$).

### Matriz de Emisión de Sensores ($B$)
Probabilidad de que el radar reporte una velocidad dada la condición real ($b_{jk} = P(Y_t = v_k \mid X_t = s_j)$):

$$B = \begin{pmatrix}
0.80 & 0.15 & 0.05 \\
0.20 & 0.65 & 0.15 \\
0.05 & 0.20 & 0.75
\end{pmatrix}$$

---

## ⚙️ Algoritmos Implementados

1. **Simulador Estocástico Monte Carlo:** Generación de secuencias temporales mediante muestreo de funciones de distribución acumulada sobre variables categóricas.
2. **Algoritmo de Viterbi:** Programación dinámica en escala logarítmica para decodificar la secuencia óptima de estados ocultos que maximiza $P(X \mid Y, \lambda)$, evitando el subdesbordamiento numérico (underflow).
3. **Algoritmo Forward:** Inducción escalada para calcular la verosimilitud de la secuencia de observaciones $P(Y \mid \lambda)$.
4. **Distribución Estacionaria Teórica:** Resolución exacta del sistema lineal $(A^T - I)\pi^{*T} = 0$ con $\sum \pi^*_i = 1$.
5. **Tiempos de Permanencia (Holding Times):** Cálculo de los tiempos continuos medios en cada estado: $E[T_i] = \frac{1}{1 - a_{ii}}$.

---

## 📂 Estructura del Proyecto

```text
.
├── traffic_hmm/                     # Paquete principal en Python
│   ├── __init__.py                  # Exposición de clases principales
│   ├── model.py                     # Definición de la clase TrafficHMM
│   ├── simulation.py                # Controlador de escenarios y Monte Carlo
│   └── visualizations.py            # Generador de gráficos (300 DPI)
├── results/                         # Gráficos generados y exportaciones CSV
│   ├── fig1_matrices_transicion_emision.png
│   ├── fig2_simulacion_jornada_24h.png
│   ├── fig3_convergencia_distribucion_estacionaria.png
│   ├── fig4_validacion_monte_carlo.png
│   ├── fig5_escenario_incidente_recuperacion.png
│   ├── fig6_matriz_confusion_viterbi.png
│   ├── simulacion_jornada_24h.csv
│   └── resumen_modelo_markov.csv
├── main.py                          # Script principal de ejecución CLI
├── simulacion_trafico.ipynb         # Cuaderno interactivo Jupyter
├── generate_doc.py                  # Generador del informe Word oficial
├── Palacios_Camilo_Markov.docx      # Informe escrito oficial entregable
├── GUION_VIDEO_SUSTENTACION.md      # Guion y estructura para el video
├── requirements.txt                 # Dependencias del proyecto
└── README.md                        # Documentación del repositorio
```

---

## 💻 Instalación y Requisitos

### Requisitos Previos
* Python 3.10 o superior instalado.
* Git instalado.

### Clonar e Instalar Dependencias
```bash
# 1. Clonar el repositorio
git clone https://github.com/camilopalacios/markov-traffic-simulation.git
cd markov-traffic-simulation

# 2. Crear un entorno virtual (recomendado)
python -m venv venv

# En Windows:
venv\Scripts\activate
# En Linux/macOS:
source venv/bin/activate

# 3. Instalar dependencias requeridas
pip install -r requirements.txt
```

---

## 🚀 Instrucciones de Ejecución

### 1. Ejecución del Script Principal
Para ejecutar la simulación completa, validar el modelo con 1,000 réplicas Monte Carlo y exportar todos los gráficos y tablas:

```bash
python main.py
```

**Salida en Consola:**
* Parámetros de matrices $A$ y $B$.
* Distribución estacionaria analítica ($\pi^*$) y tiempos de permanencia.
* Resultados de la simulación de 24 horas y exactitud del filtro de Viterbi.
* Validación Monte Carlo (Ley de Grandes Números y MAE).
* Guardado automático de figuras en la carpeta `results/`.

### 2. Exploración Interactiva en Jupyter Notebook
Para ejecutar la simulación celda por celda de manera interactiva:

```bash
jupyter notebook simulacion_trafico.ipynb
```
*(O ábrelo directamente en VS Code con la extensión de Jupyter).*

### 3. Generación del Informe Oficial en Word (.docx)
El proyecto incluye un script automatizado que construye el informe oficial con formato académico, tablas estilizadas y las 6 imágenes incrustadas:

```bash
python generate_doc.py
```
Generará `Palacios_Camilo_Markov.docx` listo para subir a la plataforma Canvas.

---

## 📊 Resultados Principales y Visualizaciones

### 1. Matrices Estocásticas de Transición y Emisión
La diagonal principal de $A$ demuestra la inercia temporal, mientras que $B$ modela el ruido en los sensores de velocidad.

![Matrices de Transición y Emisión](results/fig1_matrices_transicion_emision.png)

### 2. Serie de Tiempo de 24 Horas e Inferencia de Viterbi
El algoritmo de Viterbi logra una exactitud de reconstrucción del **73.96%** sobre las observaciones de los sensores, actuando como un filtro estocástico que estabiliza la estimación.

![Simulación 24 Horas](results/fig2_simulacion_jornada_24h.png)

### 3. Convergencia a la Distribución Estacionaria
Independiente de la condición inicial (100% Fluido o 100% Congestionado), el sistema converge asintóticamente al estado estable $\pi^* = [31.68\%, 40.59\%, 27.72\%]$ en menos de 2 horas (6 a 8 pasos).

![Convergencia Estacionaria](results/fig3_convergencia_distribucion_estacionaria.png)

### 4. Validación Monte Carlo (1,000 Réplicas / 96,000 Intervalos)
Confirmación empírica de la Ley de los Grandes Números con un Error Absoluto Medio (MAE) inferior a **0.0075** frente a la distribución teórica.

![Validación Monte Carlo](results/fig4_validacion_monte_carlo.png)

### 5. Resiliencia ante Accidentes o Lluvia Extrema
Simulación de perturbación exógena forzada entre los pasos 32 y 44 (14:00 a 17:00). Se evidencia la rápida detección del colapso vial y la curva de recuperación paulatina.

![Escenario de Incidente](results/fig5_escenario_incidente_recuperacion.png)

### 6. Matriz de Confusión de Inferencia
Cero confusiones críticas entre estados extremos (nunca se clasifica congestión severa como flujo libre).

![Matriz de Confusión](results/fig6_matriz_confusion_viterbi.png)

---

## 👥 Equipo de Trabajo

* **Camilo Palacios** - *Desarrollo de Simulación, Modelado Matemático e Implementación HMM*
* *(Compañeros de equipo de trabajo inscritos en Canvas)*

---

## 📄 Licencia

Este proyecto está distribuido bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.
