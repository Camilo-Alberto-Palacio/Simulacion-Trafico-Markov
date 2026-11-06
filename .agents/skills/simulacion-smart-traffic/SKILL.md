---
name: simulacion-smart-traffic
description: Guía de ejecución, simulación y análisis de transporte inteligente para HMM de tráfico vehicular urbano.
---

# Simulación de Tráfico Vehicular con HMM para Ciudades Inteligentes

Esta skill guía la ejecución del modelo de ciudad inteligente, cálculo de métricas de transporte, predicción temporal, rutas alternativas e impacto ambiental.

## Flujo de Trabajo
1. **Configuración de Parámetros:**
   - Quíntupla canónica $\lambda = (\mathcal{S}, \mathcal{V}, \boldsymbol{\pi}, A, B)$ con preset de 3 estados (Fluido, Moderado, Congestionado) y 3 observaciones de velocidad (Alta, Media, Baja).
2. **Simulación de Jornada:**
   - Generación de 48 mediciones (intervalos de 30 minutos = 24 horas).
   - Generación estocástica de velocidades en km/h: Alta (80-100), Media (40-80), Baja (0-40).
3. **Inferencia y Semáforos:**
   - Decodificación con Algoritmo de Viterbi en log-espacio.
   - Suavizado marginal bayesiano Forward-Backward ($\gamma_t$).
   - Asignación de semáforos por período (🟢 Fluido, 🟡 Moderado, 🔴 Congestionado).
4. **Métricas de Transporte Urbano:**
   - Identificación de horas pico continuas.
   - Cálculo del Índice de Congestión ($I_c \in [0, 100]$): $I_c = 100 \times (1 - \bar{v} / 90)$.
   - Velocidad promedio por estado operacional y tiempo total en congestión.
5. **Predicción y Rutas:**
   - Predicción a futuro ($+1\text{h}, +2\text{h}, +4\text{h}, +6\text{h}$) mediante $\mathbf{e}_{\text{actual}} A^k$.
   - Activación de alertas de congestión y sugerencia de rutas alternativas con cálculo de ahorro de tiempo.
6. **Impacto Ambiental:**
   - Estimación de emisiones de $\text{CO}_2$ (toneladas/día) y combustible desperdiciado según factores EMEP/EEA.

## Ejecución Rápida
```bash
python simulacion_smart_traffic.py
python -m unittest discover -s tests -v
```
