# Reglas y Guía de Agentes — Simulación de Tráfico Vehicular con HMM
# IU Digital de Antioquia — Asignatura: Simulación (Grupo 25)

## 1. Contexto del Proyecto
Este repositorio contiene la implementación matemática, computacional y experimental de un **Modelo Oculto de Markov (HMM)** de tiempo discreto para modelar, simular, filtrar e inferir la dinámica estocástica del tráfico vehicular en un corredor arterial urbano.

- **Paquete principal:** `traffic_hmm/`
  - `model.py`: Motor matemático `TrafficHMM` (validación de Kolmogorov, simulación, Viterbi en log-espacio, Forward-Backward escalado, distribución estacionaria y tiempos de Kac).
  - `simulation.py`: Controlador de simulaciones 24h, validación Monte Carlo (1.000 réplicas) y escenarios de perturbación/incidentes.
  - `smart_city.py`: Motor de ciudad inteligente (48 mediciones de 30 min, semáforo urbano, cálculo de horas pico, índice de congestión 0-100, rutas alternas y huella de carbono de CO2).
  - `visualizations.py`: Generador de figuras científicas a 300 DPI y dashboards.
- **Puntos de entrada CLI:**
  - `main.py`: Simulación de investigación teórica (96 pasos de 15 min, 3 escenarios, matrices 3x3 nominales).
  - `simulacion_smart_traffic.py`: Simulación de Ciudad Inteligente (48 pasos de 30 min, 10 requisitos del prompt).
- **Cuadernos Google Colab:**
  - `Simulacion_Markov_Trafico_Colab.ipynb`: Cuaderno académico pre-ejecutado.
  - `Simulacion_HMM_SmartCity_Colab.ipynb`: Cuaderno de ciudad inteligente pre-ejecutado.

---

## 2. Convenciones Matemáticas y Notación Unificada
- **Quíntupla canónica:** $\lambda = (\mathcal{S}, \mathcal{V}, \boldsymbol{\pi}, A, B)$
- **Espacio de estados ocultos ($\mathcal{S}$):** Fluido ($S_1$), Moderado ($S_2$), Congestionado ($S_3$).
- **Espacio de observaciones visibles ($\mathcal{V}$):** Velocidad Alta ($V_1$), Velocidad Media ($V_2$), Velocidad Baja ($V_3$).
- **Axiomas estocásticos:** $\sum_i \pi_i = 1$, $\sum_j a_{ij} = 1$, $\sum_k b_{jk} = 1$.
- **Estabilidad numérica:** Siempre utilizar programación dinámica en log-espacio para el algoritmo de Viterbi y factores de escalamiento temporal en Forward-Backward para evitar underflow aritmético.

---

## 3. Directrices para Agentes de Pair Programming
1. **Rigor e integridad de la evidencia:**
   - Nunca inventar métricas, cifras experimentales ni citas bibliográficas.
   - Todo resultado numérico debe provenir de ejecuciones reales verificadas o cálculos analíticos exactos.
2. **Pruebas y verificación:**
   - Antes de confirmar cambios en el código, ejecutar la suite de pruebas unitarias:
     ```bash
     python -m unittest discover -s tests -v
     ```
   - Las 9 pruebas deben finalizar con estado `OK`.
3. **Control humano y decisiones:**
   - Distinguir claramente entre hechos empíricos verificados, inferencias y recomendaciones.
   - Consultar al usuario antes de modificar arquitecturas base o eliminar archivos existentes.
