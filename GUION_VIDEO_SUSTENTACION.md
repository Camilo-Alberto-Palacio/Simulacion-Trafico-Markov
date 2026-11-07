# GUION OFICIAL DEL VIDEO PITCH (ELEVATOR PITCH DE INVESTIGACIÓN)
## Actividad Didáctica 2 — Módulo 2: Simulación de Procesos Estocásticos (Modelo Oculto de Markov - HMM)

* **Institución:** Institución Universitaria Digital de Antioquia (IU Digital) — Facultad de Ingeniería
* **Asignatura:** Simulación (`PREICA2602B020045`) — Grupo 25
* **Docente Catedrático:** Julian Andres Loaiza Lopez
* **Modalidad:** 1 Solo Presentador / Portavoz (a nombre del Grupo 25)
* **Integrantes del Equipo:** Adriana Agudelo, Camilo Palacios, Juan Daniel Pulgarin y Ruben Jaramillo
* **Duración Total:** **2 minutos y 30 segundos (Límite estricto: Máximo 3:00 minutos)**
* **Formato:** Video horizontal (16:9), 1080p, audio nítido sin música de fondo
* **Enlace Oficial YouTube:** [https://youtu.be/IdrZkVlJzT8](https://youtu.be/IdrZkVlJzT8)
* **Duración Grabada:** **02:57** (177.1 segundos — Cumple límite estricto de 2:00 a 3:00 minutos)
* **Recurso Visual:** Presentador en cámara web (esquina) + pantalla compartida mostrando las gráficas de `results/` o el Google Colab

---

### ESTRUCTURA OBLIGATORIA DEL PITCH (Página 6 de la Guía Oficial)

```
[0:00 - 0:15]  1. Gancho: El problema del tráfico y los sensores ruidosos
[0:15 - 0:40]  2. Motivación e Impacto: Costos de la congestión e inestabilidad en ITS
[0:40 - 1:10]  3. Solución Propuesta: El Modelo Oculto de Markov (HMM)
[1:10 - 1:25]  4. Metodología en 1 frase: Discretización, Viterbi y Monte Carlo
[1:25 - 1:55]  5. Resultados Clave: 74% de exactitud, -60% de ruido y 0% falsos negativos
[1:55 - 2:15]  6. Aporte (¿Por qué merece publicarse en Q1?): Rigor y reproducibilidad
[2:15 - 2:30]  7. Cierre: Repositorio GitHub, Google Colab y despedida
```

---

## 🎬 GUION COMPLETO PASO A PASO (TEXTO EXACTO PARA LEER)

> **[0:00 – 0:15] FASE 1: EL GANCHO (15 segundos)**  
> *(En pantalla: Cámara encendida del presentador + imagen de congestión o Autopista Norte)*  
>  
> *"¿Sabían que los sensores de velocidad en nuestras ciudades se equivocan hasta en un 35% de sus lecturas debido al ruido del tráfico? Un solo camión frenando en vía libre puede hacer que el sistema crea que hay un trancón gigante donde no lo hay."*

---

> **[0:15 – 0:40] FASE 2: MOTIVACIÓN E IMPACTO (25 segundos)**  
> *(En pantalla: Diagrama de arquitectura `results/fig0_diagrama_estructura_hmm.png`)*  
>  
> *"Un cordial saludo, profesor Julian Loaiza. A nombre del **Grupo 25**, conformado por Adriana Agudelo, Juan Daniel Pulgarin, Ruben Jaramillo y quien les habla, Camilo Palacios, abordamos este grave problema. En arterias como la Autopista Norte en Medellín, las falsas alarmas de los radares provocan que los semáforos inteligentes cambien de plan caóticamente cada 15 minutos, disparando las emisiones y los tiempos de viaje."*

---

> **[0:40 – 1:10] FASE 3: SOLUCIÓN PROPUESTA (30 segundos)**  
> *(En pantalla: Mapas de calor de matrices `results/fig1_matrices_transicion_emision.png`)*  
>  
> *"Nuestra solución es formular e implementar un **Modelo Oculto de Markov (HMM)**. En lugar de confiar ciegamente en la lectura aislada del sensor, el modelo separa la realidad física de la vía en tres estados latentes: Fluido, Moderado y Congestionado, y los acopla probabilísticamente con las lecturas ruidosas mediante una matriz de transición que captura la inercia real del flujo vehicular."*

---

> **[1:10 – 1:25] FASE 4: METODOLOGÍA EN UNA FRASE (15 segundos)**  
> *(En pantalla: Gráfica de 24 horas `results/fig2_simulacion_jornada_24h.png`)*  
>  
> *"Modelamos jornadas completas en intervalos de 15 minutos utilizando el **Algoritmo de Viterbi** para reconstruir la ruta óptima del tráfico y validamos el sistema con **1,000 réplicas Monte Carlo** en Python."*

---

> **[1:25 – 1:55] FASE 5: RESULTADOS CLAVE (30 segundos)**  
> *(En pantalla: Matriz de confusión `results/fig6_matriz_confusion_viterbi.png` y Monte Carlo `results/fig4_validacion_monte_carlo.png`)*  
>  
> *"Los resultados son contundentes: nuestro HMM alcanza un **74% de exactitud**, pero lo más importante: **reduce en un 60.4% las conmutaciones erráticas del radar**, bajando de 53 falsos cambios a solo 21 por día. Además, en la matriz de confusión logramos **cero por ciento de falsos negativos críticos**: ningún embotellamiento real fue clasificado como vía libre, garantizando total seguridad operativa."*

---

> **[1:55 – 2:15] FASE 6: APORTE (¿POR QUÉ MERECE PUBLICARSE EN Q1?) (20 segundos)**  
> *(En pantalla: Gráfica de incidente vial `results/fig5_escenario_incidente_recuperacion.png`)*  
>  
> *"Este trabajo aporta rigor de estándar Q1 porque no es una caja negra: derivamos algebraicamente la distribución estacionaria exacta, comprobamos la Ley de los Grandes Números con un error menor al 1% y demostramos que ante un choque real, el modelo detecta la contingencia con más del 90% de certidumbre y reproduce su tiempo de recuperación."*

---

> **[2:15 – 2:30] FASE 7: CIERRE (15 segundos)**  
> *(En pantalla: Vista del repositorio GitHub y cuaderno Google Colab abierto)*  
>  
> *"Entregamos nuestro artículo científico, el repositorio en GitHub y un cuaderno de Google Colab 100% autocontenido y ejecutable en la nube. ¡Muchas gracias por su atención y quedamos atentos a sus comentarios!"*

---

### ⏱️ CONSEJOS CLAVE PARA CLAVAR EL TIEMPO:
1. **Ritmo de voz:** Habla con entusiasmo y seguridad, sin correr pero sin hacer pausas largas.
2. **Cronómetro:** Pon un cronómetro en el celular al lado de la pantalla. A los **1:10** debes estar terminando la solución, a los **1:55** terminando los resultados y a los **2:25** diciendo *"Muchas gracias"*.
3. **Grabación rápida:** Puedes usar Microsoft Teams, OBS o Zoom, compartiendo la pantalla con las gráficas de fondo y tu cámara en la esquina superior derecha.
