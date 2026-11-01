# GUION Y GUÍA OFICIAL PARA EL VIDEO DE SUSTENTACIÓN
## Actividad Didáctica 2 — Módulo 2: Simulación de Procesos Estocásticos
### Tema: Modelo Oculto de Markov (HMM) para Estimación y Predicción del Tráfico Vehicular Urbano

---

## 1. Ficha Técnica de Grabación
* **Duración objetivo:** **6:00 a 7:00 minutos** (cumple con holgura todos los criterios de la rúbrica sin exceder el tiempo).
* **Herramienta sugerida:** Microsoft Teams, Google Meet, Zoom o OBS Studio.
* **Formato de entrega:** Enlace público o *No listado (Unlisted)* en YouTube / Google Drive (con permiso *"Cualquier persona con el enlace puede ver"*), incluido en la entrega de Canvas.
* **Recomendación visual:** Cámara encendida de los integrantes y pantalla compartida alternando entre las figuras de `results/`, la terminal ejecutando `python main.py` y el cuaderno interactivo `Simulacion_Markov_Trafico_Colab.ipynb`.

---

## 2. Distribución Equitativa de Roles (Grupo 25)

| Bloque | Tiempo | Integrante Responsable | Ejes de la Rúbrica Cubiertos |
| :--- | :---: | :--- | :--- |
| **Bloque 1** | `0:00 – 1:25` | **Adriana Andrea Agudelo Agudelo** | Formulación del problema, fenómeno vial y distinción Estado Oculto vs. Observación Visible. |
| **Bloque 2** | `1:25 – 2:50` | **Camilo Alberto Palacios Turriago** | Construcción, axiomas estocásticos y justificación física de $\pi$, $A$ y $B$. |
| **Bloque 3** | `2:50 – 4:25` | **Juan Daniel Pulgarin García** | Demostración en vivo en Python / Google Colab, Viterbi, Forward-Backward y Monte Carlo. |
| **Bloque 4** | `4:25 – 6:15` | **Ruben Dario Jaramillo Cervantes** | Análisis de resultados gráficos, matriz de confusión, contingencia vial y conclusiones. |

---

## 3. Guion Paso a Paso por Bloques

### [0:00 – 1:25] Bloque 1: Problema Planteado y Justificación del Modelo Oculto de Markov
**Expone:** Adriana Andrea Agudelo Agudelo  
**Mostrar en pantalla:** Portada de `Palacios_Camilo_Markov.docx` y luego `results/fig0_diagrama_estructura_hmm.png`.

> *"Cordial saludo profesor Julian Andres Loaiza. Somos el Grupo 25 de la asignatura Simulación en la IU Digital de Antioquia, conformado por Adriana Agudelo, Camilo Palacios, Juan Daniel Pulgarin y Ruben Dario Jaramillo.*
>
> *En esta actividad implementamos un **Modelo Oculto de Markov (HMM)** para simular e inferir el tráfico vehicular en un corredor arterial urbano como la Autopista Norte en Medellín, discretizado en intervalos de 15 minutos (96 pasos por día).*
>
> *¿Por qué un Modelo Oculto de Markov y no una cadena simple? Como vemos en nuestro diagrama de arquitectura (`fig0`), en la movilidad urbana existen dos capas distintas:*
> *1. Una **Capa Oculta o Latente ($X_t$)**, que es el estado macroscópico real de todo el corredor: **Fluido**, **Moderado** o **Congestionado**, el cual no puede observarse directamente desde un solo punto.*
> *2. Una **Capa Observable ($Y_t$)**, compuesta por las lecturas puntuales de radares Doppler: **Velocidad Alta**, **Media** o **Baja**. Estas mediciones contienen ruido: por ejemplo, un camión pesado frenando en vía libre genera una lectura baja sin que exista trancón. El HMM desacopla ese ruido instrumental de la dinámica física real."*

---

### [1:25 – 2:50] Bloque 2: Significado y Justificación de $\pi$, Matriz $A$ y Matriz $B$
**Expone:** Camilo Alberto Palacios Turriago  
**Mostrar en pantalla:** `results/fig1_matrices_transicion_emision.png`.

> *"Para parametrizar formalmente la quíntupla $\lambda = (\mathcal{S}, \mathcal{V}, \pi, A, B)$, verificamos que todas las distribuciones cumplan los axiomas estocásticos de Kolmogorov (no negatividad y suma por fila igual a 1):*
>
> *Primero, el **Vector Inicial $\pi = [0.70, 0.20, 0.10]$** representa el arranque operativo a las 06:00 de la mañana, donde predomina el flujo libre con un 70%.*
>
> *Segundo, la **Matriz de Transición $A$** modela la evolución entre cuartos de hora consecutivos. Su diagonal principal concentra las mayores probabilidades ($0.70$, $0.60$ y $0.65$), capturando la **inercia hidrodinámica del tráfico**. Además, los saltos extremos directos entre Fluido y Congestionado tienen apenas un $5\%$ de probabilidad ($a_{13} = a_{31} = 0.05$), pues físicamente la congestión se forma y se disipa de manera gradual pasando por el estado Moderado.*
>
> *Tercero, la **Matriz de Emisión $B$** cuantifica la confiabilidad del radar: acierta el $80\%$ en estado Fluido, $65\%$ en Moderado y $75\%$ en Congestionado, dejando entre un $20\%$ y un $35\%$ de emisiones cruzadas que modelan el ruido real de telemetría."*

---

### [2:50 – 4:25] Bloque 3: Demostración en Vivo en Python y Google Colab
**Expone:** Juan Daniel Pulgarin García  
**Mostrar en pantalla:** Terminal ejecutando `python main.py` (y `python -m unittest discover -s tests -v`) + vista rápida de `Simulacion_Markov_Trafico_Colab.ipynb`.

> *"Pasamos a la demostración computacional. Estructuramos el paquete modular `traffic_hmm` en Python con pruebas unitarias automatizadas y un cuaderno interactivo en Google Colab.*
>
> *Al ejecutar `python main.py` en vivo observamos cinco etapas:*
> *- Primero, resuelve algebraicamente el sistema lineal estacionario $\pi^* A = \pi^*$, hallando el equilibrio exacto: **31.68% Fluido**, **40.59% Moderado** y **27.72% Congestionado**, con tiempos continuos esperados de permanencia de **50.0 minutos en Fluido**, **37.5 en Moderado** y **42.9 minutos continuos cuando se instala una congestión**.*
> *- Segundo, simula una jornada completa de 24 horas (96 intervalos) y aplica tanto el **Algoritmo de Viterbi** en escala logarítmica como el suavizado bayesiano **Forward-Backward**, alcanzando un **73.96% de exactitud** y reduciendo las oscilaciones ruidosas del sensor de **53 a solo 21 cambios** en el día.*
> *- Tercero, ejecuta **1,000 réplicas Monte Carlo** (96,000 intervalos), comprobando la Ley de los Grandes Números con un **Error Absoluto Medio de apenas 0.0075** y confirmando que los decodificadores bayesianos superan sistemáticamente al sensor crudo sin memoria."*

---

### [4:25 – 6:15] Bloque 4: Análisis de Resultados Gráficos y Conclusiones
**Expone:** Ruben Dario Jaramillo Cervantes  
**Mostrar en pantalla:** `fig2_simulacion_jornada_24h.png`, `fig6_matriz_confusion_viterbi.png`, `fig3_convergencia_distribucion_estacionaria.png` y `fig5_escenario_incidente_recuperacion.png`.

> *"Al analizar nuestras visualizaciones científicas destacamos cuatro hallazgos clave:*
>
> *1. En la **Serie de 24 Horas (`fig2`)**, vemos cómo Viterbi y las probabilidades posteriores $\gamma_t$ actúan como un filtro estocástico robusto, suprimiendo casi el 60% del parpadeo errático de los radares.*
> *2. En la **Matriz de Confusión (`fig6`)**, el **92% de las discrepancias ocurren entre estados vecinos** y tenemos **0.0% de falsos negativos críticos en congestión** (0 de 19 trancones reales fueron clasificados como vía fluida), garantizando seguridad operativa.*
> *3. En la **Gráfica de Convergencia (`fig3`)**, comprobamos la ergodicidad: sea que el corredor amanezca 100% Fluido o 100% Congestionado, converge al equilibrio estacionario $\pi^*$ en menos de 2 horas (6 a 8 pasos).*
> *4. Finalmente, en el **Escenario de Accidente Vial entre las 14:00 y 17:00 (`fig5`)**, el modelo alcanza un **80.21% de exactitud**, dispara la probabilidad posterior de alerta ITS por encima del 90% y reproduce la cola de recuperación de 30 a 45 minutos tras despejar la vía.*
>
> *En conclusión, el HMM implementado transforma telemetría ruidosa en inteligencia operativa accionable para planes semafóricos adaptativos. Todo nuestro código, pruebas, informe y notebook en Google Colab están disponibles en nuestro repositorio público de GitHub. ¡Muchas gracias!"*
