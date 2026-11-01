# GUION Y GUÍA COMPLETA PARA EL VIDEO DE SUSTENTACIÓN
## Actividad Didáctica 2 - Módulo 2: Simulación de Procesos Estocásticos
### Tema: Modelo Oculto de Markov (HMM) para Predicción del Tráfico Vehicular

---

## 📌 1. Ficha Técnica del Video
* **Duración recomendada:** Entre **5 y 8 minutos** (tiempo óptimo para no perder puntos por exceso o escasez).
* **Plataforma de grabación recomendada:** Zoom, Microsoft Teams, Google Meet, Loom o grabación de pantalla con OBS Studio.
* **Formato de entrega:** Enlace público en YouTube (en modo *Oculto/Unlisted* o *Público*) o Microsoft Stream / Google Drive con permisos abiertos.
* **Requisito visual:** Se recomienda que los expositores tengan su cámara web encendida en una esquina y compartan pantalla con las diapositivas y el código en ejecución.

---

## 👥 2. Asignación de Roles por Integrante

### Si el grupo es de 4 personas:
* **Integrante 1:** Introducción, contextualización del problema e idoneidad del Modelo Oculto de Markov.
* **Integrante 2:** Fundamentación matemática: vector inicial $\pi$, matriz de transición $A$ y matriz de emisión $B$.
* **Integrante 3:** Demostración en vivo del código en Python (`main.py` o Jupyter Notebook) y algoritmo de Viterbi.
* **Integrante 4:** Análisis de resultados (gráficas 24h, convergencia estacionaria, contingencia) y conclusiones finales.

### Si el grupo es de 3 personas:
* **Integrante 1:** Introducción, contextualización y justificación del HMM (problema + dualidad estados/observaciones).
* **Integrante 2:** Matrices del modelo ($\pi$, $A$, $B$) y demostración en vivo del código (`main.py`).
* **Integrante 3:** Análisis de resultados gráficos (Viterbi, Monte Carlo, incidente) y conclusiones.

### Si el grupo es de 2 personas:
* **Integrante 1:** Introducción, pertinencia del problema, justificación de HMM y explicación de matrices ($\pi, A, B$).
* **Integrante 2:** Demostración práctica del código, análisis de las 6 gráficas de resultados y conclusiones.

---

## 🎬 3. Estructura Minuto a Minuto y Guion Palabra por Palabra

```text
TIEMPO TOTAL: ~6:30 minutos
├── [0:00 - 1:15] Bloque 1: Saludo, Introducción y Justificación del HMM
├── [1:15 - 2:30] Bloque 2: Significado de las Matrices (π, A, B)
├── [2:30 - 4:00] Bloque 3: Demostración en Vivo del Código en Python
├── [4:00 - 5:30] Bloque 4: Análisis de Resultados y Visualizaciones
└── [5:30 - 6:30] Bloque 5: Conclusiones y Cierre
```

---

### 🕒 [0:00 - 1:15] Bloque 1: Saludo, Introducción y Justificación del HMM
**Quién expone:** Integrante 1  
**Qué mostrar en pantalla:** Diapositiva 1 (Título, integrantes, logo de IU Digital) y Diapositiva 2 (Diagrama conceptual del HMM: Estados Ocultos vs Observaciones).

> **Guion sugerido:**
> *"Cordial saludo profesor y companeros. Somos el equipo conformado por [Nombres completos de los integrantes] para la asignatura de Simulación de la IU Digital de Antioquia.
> 
> En esta segunda actividad didáctica, nos propusimos modelar y simular un proceso estocástico del mundo real: **la predicción y estimación del tráfico vehicular en un corredor urbano arterial**.
> 
> Elegimos abordar este problema mediante un **Modelo Oculto de Markov (HMM)** debido a una razón técnica fundamental: en el tráfico existen dos capas bien diferenciadas.
> 
> Primero, tenemos el **Estado Oculto o Latente**, que representa la verdadera condición macroscópica de la vía: si está en estado **Fluido**, **Moderado** o **Congestionado**. Ningún sensor en el asfalto puede 'ver' este estado sistémico de forma absoluta.
> 
> Segundo, tenemos las **Observaciones Visibles**, que son las lecturas puntuales reportadas por radares y cámaras de velocidad: lecturas de **Velocidad Alta**, **Media** o **Baja**. Estas lecturas tienen ruido e incertidumbre: un camión frenando en una vía fluida puede registrar velocidad baja momentáneamente, sin que la vía esté colapsada. El HMM nos permite filtrar ese ruido y reconstruir la realidad."*

---

### 🕒 [1:15 - 2:30] Bloque 2: Significado de las Matrices del Modelo
**Quién expone:** Integrante 2  
**Qué mostrar en pantalla:** Diapositiva 3 (Figura 1: Mapas de calor de las matrices $A$ y $B$, y vector $\pi$).

> **Guion sugerido:**
> *"Para formalizar matemáticamente nuestro modelo en intervalos de 15 minutos, definimos tres componentes clave:
> 
> 1. **Vector de Probabilidades Iniciales ($\pi$):** Fijado en $[0.70, 0.20, 0.10]$ a las 06:00 de la manana, reflejando que el día usualmente inicia con flujo libre.
> 
> 2. **Matriz de Transición de Estados ($A$):** Gobierna cómo cambia el tráfico de un intervalo de 15 minutos al siguiente. Noten que la diagonal principal concentra los valores más altos: $0.70$ para Fluido, $0.60$ para Moderado y $0.65$ para Congestionado. Esto modela la **inercia física del tráfico**: un estado tiende a persistir. Además, la transición directa de Fluido a Congestionado es de apenas el $5\%$, porque físicamente el tráfico casi siempre se degrada pasando primero por un estado Moderado.
> 
> 3. **Matriz de Emisión ($B$):** Cuantifica la probabilidad de que los radares reporten cierta velocidad según el estado real. Si el tráfico es Fluido, el sensor reporta Velocidad Alta con un $80\%$ de probabilidad, pero dejamos un $15\%$ para Media y un $5\%$ para Baja, representando el ruido instrumental y situaciones puntuales de la vía."*

---

### 🕒 [2:30 - 4:00] Bloque 3: Demostración en Vivo del Código en Python
**Quién expone:** Integrante 3  
**Qué mostrar en pantalla:** Terminal de comandos (PowerShell / CMD) ejecutando `python main.py` o las celdas del Jupyter Notebook `simulacion_trafico.ipynb`.

> **Guion sugerido:**
> *(El estudiante comparte pantalla mostrando la terminal y escribe `python main.py`)*
> 
> *"Ahora pasamos a la demostración práctica del código fuente. Desarrollamos una librería modular en Python organizada en una clase principal `TrafficHMM`, un controlador de simulación y un módulo de visualizaciones.
> 
> Al ejecutar `python main.py`:
> 
> - En el **Paso 1 y 2**, el programa inicializa las matrices y calcula analíticamente la **Distribución Estacionaria**, que resulta ser: $31.68\%$ para Fluido, $40.59\%$ para Moderado y $27.72\%$ para Congestionado. También calcula los **tiempos de permanencia**: el tráfico permanece en promedio 50 minutos en Fluido, 37.5 minutos en Moderado y 42.9 minutos en Congestionado.
> 
> - En el **Paso 3**, simulamos una jornada de 24 horas equivalente a 96 pasos temporales. Aquí entra en acción el **Algoritmo de Viterbi**, que a partir únicamente de las observaciones ruidosas de los radares infiere la secuencia oculta con una **exactitud del 73.96%**.
> 
> - En el **Paso 4**, ejecutamos una validación Monte Carlo con **1,000 réplicas completas** (96,000 pasos de tiempo). Con esto comprobamos la Ley de los Grandes Números: el error absoluto medio entre las frecuencias simuladas y la distribución teórica fue de apenas $0.0075$."*

---

### 🕒 [4:00 - 5:30] Bloque 4: Análisis de Resultados y Visualizaciones
**Quién expone:** Integrante 4 (o Integrante 1/2 si son menos de 4)  
**Qué mostrar en pantalla:** Mostrar las figuras generadas en la carpeta `results/` (`fig2_simulacion_jornada_24h.png`, `fig3_convergencia...png`, `fig5_escenario_incidente...png`, `fig6_matriz_confusion...png`).

> **Guion sugerido:**
> *"Revisemos los resultados gráficos más relevantes:
> 
> En la **Figura de la Jornada de 24 Horas**, la línea negra representa el estado real y la línea punteada roja la inferencia de Viterbi. Observen cómo Viterbi filtra eficazmente las caídas bruscas de los sensores, evitando falsas alarmas de congestión.
> 
> En la **Matriz de Confusión**, vemos que los pocos desaciertos ocurren únicamente entre estados vecinos (Fluido con Moderado, o Moderado con Congestionado). El modelo **nunca confundió Congestionado con Fluido (0%)**, lo cual es vital para la seguridad vial.
> 
> En la **Gráfica de Convergencia**, probamos iniciar el sistema bajo dos extremos: un día 100% Fluido versus un día 100% Congestionado. En menos de 2 horas (8 pasos), ambas curvas convergen exactamente a la distribución estacionaria calculada analíticamente, demostrando la ergodicidad de la cadena.
> 
> Por último, simulamos un **escenario de perturbación** por accidente vial entre las 14:00 y las 17:00. El modelo detecta inmediatamente el colapso vial y muestra cómo la vía tarda cerca de 1 hora en disipar la congestión tras retirar el siniestro."*

---

### 🕒 [5:30 - 6:30] Bloque 5: Conclusiones y Cierre
**Quién expone:** Todos o el Integrante designado  
**Qué mostrar en pantalla:** Diapositiva final con conclusiones, enlace al repositorio en GitHub y agradecimiento.

> **Guion sugerido:**
> *"Como conclusiones principales de nuestro proyecto destacamos:
> 
> 1. El Modelo Oculto de Markov demostró ser la herramienta idónea para este fenómeno, logrando más del 73% de precisión aún con sensores imperfectos.
> 2. Se comprobó la convergencia estocástica mediante la validación Monte Carlo a gran escala.
> 3. Todo el código fuente, el notebook interactivo, los datos generados y el documento oficial en Word se encuentran organizados y disponibles en nuestro repositorio público de GitHub.
> 
> Agradecemos su atención y quedamos atentos a sus preguntas y retroalimentación. ¡Muchas gracias!"*

---

## 💡 4. Consejos Clave para Obtener 10/10 en el Criterio de Sustentación

1. **Puntualidad en los tiempos:** Mantengan la grabación entre 5 y 7 minutos. Ensayen una vez con cronómetro antes de grabar la versión definitiva.
2. **Claridad de audio:** Utilicen auriculares o micrófono cercano para evitar eco ambiental.
3. **Fluidez:** No lean las diapositivas de corrido; usen el guion como guía para expresarlo con sus propias palabras.
4. **Prueba de ejecución en vivo:** Asegúrense de que se vea claramente la terminal corriendo `python main.py` o las celdas de Jupyter ejecutándose; esto evidencia ante el profesor que la simulación es 100% real y funcional.
5. **Enlace público:** Antes de enviar el enlace en la entrega, ábranlo en una ventana de incógnito para verificar que no pida permisos de acceso especiales.
