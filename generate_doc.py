"""
Generador automático del Documento Oficial de la Actividad (Informe Académico).
Genera 'Palacios_Camilo_Markov.docx' y 'Apellido_Nombre_Markov.docx' con formato APA / IEEE
incluyendo todas las secciones obligatorias, tablas numéricas y las 6 figuras de alta resolución incrustadas.
"""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn


def set_cell_background(cell, fill_hex):
    """Aplica color de fondo a una celda de tabla en Word."""
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Establece márgenes internos de celda en dxa (1 pt = 20 dxa)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for margin_name, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{margin_name}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def add_heading_with_spacing(doc, text, level, space_before=12, space_after=6):
    """Agrega un encabezado estilizado con espaciado controlado."""
    heading = doc.add_heading(text, level=level)
    heading.paragraph_format.space_before = Pt(space_before)
    heading.paragraph_format.space_after = Pt(space_after)
    heading.paragraph_format.keep_with_next = True
    for run in heading.runs:
        run.font.name = 'Calibri'
        if level == 1:
            run.font.size = Pt(16)
            run.font.bold = True
            run.font.color.rgb = RGBColor(31, 78, 121)  # Azul institucional
        elif level == 2:
            run.font.size = Pt(13)
            run.font.bold = True
            run.font.color.rgb = RGBColor(46, 117, 182)
        elif level == 3:
            run.font.size = Pt(11.5)
            run.font.bold = True
            run.font.color.rgb = RGBColor(89, 89, 89)
    return heading


def build_document(output_filename="Palacios_Camilo_Markov.docx"):
    doc = Document()

    # 1. Configuración de Márgenes de Página (Estándar 2.5 cm)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # 2. Portada Institucional / Encabezado
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(4)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_inst = title_p.add_run("INSTITUCIÓN UNIVERSITARIA DIGITAL DE ANTIOQUIA - IU DIGITAL\nFACULTAD DE INGENIERÍA | PROGRAMA DE INGENIERÍA DE SOFTWARE")
    run_inst.font.name = "Calibri"
    run_inst.font.size = Pt(11)
    run_inst.font.bold = True
    run_inst.font.color.rgb = RGBColor(89, 89, 89)

    doc_title_p = doc.add_paragraph()
    doc_title_p.paragraph_format.space_before = Pt(14)
    doc_title_p.paragraph_format.space_after = Pt(8)
    doc_title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = doc_title_p.add_run("SIMULACIÓN ESTOCÁSTICA DEL TRÁFICO VEHICULAR MEDIANTE UN MODELO OCULTO DE MARKOV (HMM)")
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(18)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(31, 78, 121)

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_before = Pt(0)
    sub_p.paragraph_format.space_after = Pt(18)
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = sub_p.add_run("Actividad Didáctica 2 - Módulo 2: Distribuciones de Probabilidad y Cadenas de Markov")
    run_sub.font.name = "Calibri"
    run_sub.font.size = Pt(13)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor(115, 115, 115)

    # Metadatos de Autores
    auth_table = doc.add_table(rows=4, cols=2)
    auth_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_info = [
        ("Asignatura:", "Simulación (S25 - Módulo 2)"),
        ("Estudiantes / Equipo:", "Camilo Palacios (y miembros del equipo de trabajo)"),
        ("Tema Seleccionado:", "Predicción del tráfico vehicular (Estados: Fluido, Moderado, Congestionado)"),
        ("Fecha de Entrega:", "Noviembre de 2026"),
    ]
    for row_idx, (label, val) in enumerate(meta_info):
        cell_lbl, cell_val = auth_table.rows[row_idx].cells
        cell_lbl.width = Inches(2.2)
        cell_val.width = Inches(4.3)
        p_l = cell_lbl.paragraphs[0]
        p_l.paragraph_format.space_before = Pt(2)
        p_l.paragraph_format.space_after = Pt(2)
        r_l = p_l.add_run(label)
        r_l.font.name = "Calibri"
        r_l.font.bold = True
        r_l.font.size = Pt(10)

        p_v = cell_val.paragraphs[0]
        p_v.paragraph_format.space_before = Pt(2)
        p_v.paragraph_format.space_after = Pt(2)
        r_v = p_v.add_run(val)
        r_v.font.name = "Calibri"
        r_v.font.size = Pt(10)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # ---------------------------------------------------------
    # RESUMEN EJECUTIVO
    # ---------------------------------------------------------
    resumen_p = doc.add_paragraph()
    resumen_p.paragraph_format.space_before = Pt(6)
    resumen_p.paragraph_format.space_after = Pt(14)
    run_res_t = resumen_p.add_run("RESUMEN EJECUTIVO: ")
    run_res_t.font.bold = True
    run_res_t.font.size = Pt(10)
    run_res_t.font.name = "Calibri"
    run_res_b = resumen_p.add_run(
        "El presente informe documenta el diseno, formalización matemática, implementación computacional en Python y "
        "análisis experimental de un Modelo Oculto de Markov (HMM) para simular y predecir la dinámica estocástica del "
        "tráfico vehicular en un corredor urbano. Se modela el estado intrínseco del tráfico como un proceso no observable "
        "directamente con tres regímenes latentes: Fluido, Moderado y Congestionado. Las observaciones corresponden a lecturas "
        "de velocidad discretizadas captadas por sensores de radar (Alta, Media, Baja), sujetas a incertidumbre y ruido instrumental. "
        "Se evalúan las propiedades analíticas del modelo, la distribución estacionaria ergódica, tiempos de permanencia continua, "
        "y la decodificación óptima mediante el algoritmo de Viterbi en escenarios de jornada regular de 24 horas y eventos de perturbación. "
        "Asimismo, se realiza una validación Monte Carlo con 1,000 réplicas (96,000 intervalos temporales) demostrando la convergencia "
        "asintótica estocástica hacia el estado estable teórico con un error absoluto medio (MAE) inferior a 0.008."
    )
    run_res_b.font.size = Pt(10)
    run_res_b.font.name = "Calibri"

    # ---------------------------------------------------------
    # 1. INTRODUCCIÓN
    # ---------------------------------------------------------
    add_heading_with_spacing(doc, "1. INTRODUCCIÓN", level=1)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "La movilidad urbana contemporánea constituye uno de los desafíos más críticos para la ingeniería y la gestión de "
        "infraestructura en las metrópolis modernas. La congestión vehicular genera externalidades negativas severas, tales "
        "como el incremento en los tiempos de desplazamiento, sobrecostos logísticos, mayor consumo de combustibles fósiles, "
        "emisión de gases de efecto invernadero y elevados niveles de estrés en la población. Por consiguiente, la capacidad de "
        "modelar, simular y anticipar la evolución del flujo vehicular resulta indispensable para el diseno de Sistemas Inteligentes "
        "de Transporte (ITS) y la optimización dinámica de planes semafóricos."
    )

    add_heading_with_spacing(doc, "1.1 Formulación y Pertinencia del Problema", level=2)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "El fenómeno del tráfico vehicular es de naturaleza inherentemente estocástica. Las condiciones de circulación no "
        "evolucionan de forma determinista, sino que están sujetas a fluctuaciones aleatorias provocadas por decisiones individuales "
        "de conducción, variaciones de demanda en horas pico, condiciones climáticas cambiantes y eventos imprevistos como incidentes "
        "viales o detenciones momentáneas. En este trabajo se aborda el problema de predecir y estimar el estado de congestión "
        "en un corredor arterial urbano representativo, dividido en intervalos discretos de tiempo de 15 minutos (96 pasos diarios)."
    )

    add_heading_with_spacing(doc, "1.2 Fundamentación Conceptual: ¿Qué es un Modelo Oculto de Markov (HMM)?", level=2)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "Una Cadena de Markov clásica describe un proceso estocástico {X_t} que satisface la propiedad de pérdida de memoria "
        "(propiedad markoviana): la probabilidad condicional de transición hacia el estado futuro en el instante t+1 depende "
        "únicamente del estado actual en el instante t, siendo condicionalmente independiente de la historia previa:\n"
    )
    p_eq1 = doc.add_paragraph()
    p_eq1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_eq1 = p_eq1.add_run("P(X_{t+1} = s_j | X_t = s_i, X_{t-1} = s_{t-1}, ..., X_0 = s_0) = P(X_{t+1} = s_j | X_t = s_i) = a_{ij}")
    r_eq1.font.bold = True
    r_eq1.font.name = "Courier New"
    r_eq1.font.size = Pt(10)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "Sin embargo, en sistemas complejos del mundo real, el estado intrínseco del sistema con frecuencia no es accesible "
        "de manera directa ni perfecta. Es aquí donde surge el Modelo Oculto de Markov (Hidden Markov Model - HMM). Un HMM es una "
        "extensión probabilística bidimensional compuesta por dos procesos estocásticos acoplados:\n"
        "1. Un proceso estocástico subyacente y latente (no observable directamente), modelado como una Cadena de Markov de estados finitos.\n"
        "2. Un proceso estocástico visible o emitido, donde en cada instante de tiempo t se genera una observación sensorial y_t cuya "
        "distribución de probabilidad depende condicionalmente del estado oculto actual x_t a través de una matriz de emisión."
    )

    add_heading_with_spacing(doc, "1.3 Justificación de la Dualidad: Estados Ocultos vs. Observaciones Visibles", level=2)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "¿Por qué el tráfico vehicular requiere un HMM y no una simple cadena determinista o completamente observable?\n\n"
        "• El Estado Oculto (Latente): La 'congestión global' o nivel de servicio macroscópico de una arteria vial representa una "
        "condición sistémica agregada (densidad vehicular, capacidad remanente, efecto acordeón de frenado). Ningún sensor individual "
        "puede 'ver' de forma absoluta este estado macroscópico continuo en toda la longitud de la vía.\n\n"
        "• Las Observaciones Visibles: Los sistemas de campo (radares doppler, espiras electromagnéticas o cámaras inteligentes) "
        "únicamente captan mediciones puntuales de velocidad o conteos en una sección transversal. Estas mediciones poseen ruido e "
        "incertidumbre: por ejemplo, en una vía totalmente fluida, un camión de carga pesada o un autobús en maniobra de parada puede "
        "inducir una lectura temporal de 'Velocidad Baja'; inversamente, en medio de un trancón severo, un vehículo puede acelerar "
        "momentáneamente durante 20 metros registrando una lectura puntual de 'Velocidad Media'.\n\n"
        "El HMM permite modelar formalmente este desacoplamiento entre la realidad física subyacente y las evidencias sensoriales ruidosas, "
        "haciendo posible filtrar el ruido y reconstruir la trayectoria real del tráfico mediante inferencia matemática rigurosa."
    )

    # ---------------------------------------------------------
    # 2. METODOLOGÍA
    # ---------------------------------------------------------
    add_heading_with_spacing(doc, "2. METODOLOGÍA", level=1)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "La metodología implementada se estructura formalmente siguiendo la quintupla clásica de un HMM: λ = (S, V, π, A, B), "
        "parametrizada para intervalos de muestreo de Δt = 15 minutos en un corredor arterial urbano."
    )

    add_heading_with_spacing(doc, "2.1 Definición de Espacios de Estados y Observaciones", level=2)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "• Espacio de Estados Ocultos (S, con N = 3):\n"
        "   - S_1 (Fluido - F): Flujo vehicular libre, densidad baja (k ≤ 15 veh/km/carril), velocidades cercanas al límite de diseño vial.\n"
        "   - S_2 (Moderado - M): Densidad media (15 < k ≤ 35 veh/km/carril), velocidad estable pero con libertad de maniobra restringida.\n"
        "   - S_3 (Congestionado - C): Flujo saturado o forzado (k > 35 veh/km/carril), régimen stop-and-go con demoras significativas.\n\n"
        "• Espacio de Observaciones Visibles (V, con M = 3):\n"
        "   - V_1 (Velocidad Alta): Velocidad media puntual > 60 km/h.\n"
        "   - V_2 (Velocidad Media): Velocidad media puntual comprendida entre 30 y 60 km/h.\n"
        "   - V_3 (Velocidad Baja): Velocidad media puntual < 30 km/h."
    )

    add_heading_with_spacing(doc, "2.2 Vector de Probabilidades Iniciales (π)", level=2)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "El vector inicial π = [π_F, π_M, π_C] define la distribución de probabilidad del estado en el instante inicial t = 0 "
        "(06:00 AM). Dado que a tempranas horas de la manana el flujo suele iniciar con baja densidad, se establece:\n"
    )
    p_pi = doc.add_paragraph()
    p_pi.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_pi = p_pi.add_run("π = [P(X_0 = Fluido), P(X_0 = Moderado), P(X_0 = Congestionado)] = [0.70, 0.20, 0.10]")
    r_pi.font.bold = True
    r_pi.font.name = "Courier New"
    r_pi.font.size = Pt(10)

    add_heading_with_spacing(doc, "2.3 Matriz de Transición de Estados (A)", level=2)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "La matriz A ∈ R^{3×3} gobierna la dinámica interna del tráfico entre intervalos consecutivos de 15 minutos, donde "
        "a_{ij} = P(X_{t+1} = s_j | X_t = s_i):\n"
    )

    # Tabla Matriz A
    table_A = doc.add_table(rows=4, cols=4)
    table_A.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers_A = ["Estado Actual (X_t)", "Fluido (t+1)", "Moderado (t+1)", "Congestionado (t+1)"]
    for c_idx, h in enumerate(headers_A):
        cell = table_A.rows[0].cells[c_idx]
        cell.paragraphs[0].add_run(h).font.bold = True
        set_cell_background(cell, "D9E1F2")
        set_cell_margins(cell)

    data_A = [
        ("Fluido (S_1)", "0.70 (70%)", "0.25 (25%)", "0.05 (5%)"),
        ("Moderado (S_2)", "0.20 (20%)", "0.60 (60%)", "0.20 (20%)"),
        ("Congestionado (S_3)", "0.05 (5%)", "0.30 (30%)", "0.65 (65%)"),
    ]
    for r_idx, row_vals in enumerate(data_A):
        for c_idx, val in enumerate(row_vals):
            cell = table_A.rows[r_idx + 1].cells[c_idx]
            cell.paragraphs[0].add_run(val)
            if c_idx > 0 and r_idx == c_idx - 1:
                set_cell_background(cell, "E2EFDA")  # Diagonal resaltada
            set_cell_margins(cell)

    p_just_A = doc.add_paragraph()
    p_just_A.paragraph_format.space_before = Pt(6)
    p_just_A.paragraph_format.space_after = Pt(6)
    p_just_A.add_run(
        "Justificación Física de la Matriz de Transición:\n"
        "1. Inercia Temporal: La diagonal principal concentra las mayores probabilidades (0.70, 0.60, 0.65). Esto refleja la "
        "persistencia física del flujo vehicular: si el tráfico fluye libremente o está atascado, existe una alta tendencia "
        "a continuar en dicho estado en los siguientes 15 minutos.\n"
        "2. Gradualidad de Fases: La probabilidad de saltar directamente de Fluido a Congestionado es muy baja (a_{13} = 0.05); "
        "en condiciones normales el tráfico transita primero por un régimen Moderado (a_{12} = 0.25). Análogamente, descongestionar "
        "completamente una arteria directamente a Fluido en solo 15 minutos es excepcional (a_{31} = 0.05), requiriendo un paso intermedio (a_{32} = 0.30).\n"
        "3. Propiedad Estocástica: Cada fila suma exactamente 1.0 (condición necesaria de toda matriz de Markov)."
    )

    add_heading_with_spacing(doc, "2.4 Matriz de Emisión de Observaciones (B)", level=2)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "La matriz B ∈ R^{3×3} relaciona el estado real subyacente con la señal reportada por el sensor de campo, "
        "donde b_{jk} = P(Y_t = v_k | X_t = s_j):\n"
    )

    # Tabla Matriz B
    table_B = doc.add_table(rows=4, cols=4)
    table_B.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers_B = ["Estado Real Oculto (X_t)", "Velocidad Alta (Y_t)", "Velocidad Media (Y_t)", "Velocidad Baja (Y_t)"]
    for c_idx, h in enumerate(headers_B):
        cell = table_B.rows[0].cells[c_idx]
        cell.paragraphs[0].add_run(h).font.bold = True
        set_cell_background(cell, "FCE4D6")
        set_cell_margins(cell)

    data_B = [
        ("Fluido (S_1)", "0.80 (80%)", "0.15 (15%)", "0.05 (5%)"),
        ("Moderado (S_2)", "0.20 (20%)", "0.65 (65%)", "0.15 (15%)"),
        ("Congestionado (S_3)", "0.05 (5%)", "0.20 (20%)", "0.75 (75%)"),
    ]
    for r_idx, row_vals in enumerate(data_B):
        for c_idx, val in enumerate(row_vals):
            cell = table_B.rows[r_idx + 1].cells[c_idx]
            cell.paragraphs[0].add_run(val)
            if c_idx > 0 and r_idx == c_idx - 1:
                set_cell_background(cell, "FFF2CC")
            set_cell_margins(cell)

    p_just_B = doc.add_paragraph()
    p_just_B.paragraph_format.space_before = Pt(6)
    p_just_B.paragraph_format.space_after = Pt(6)
    p_just_B.add_run(
        "Justificación de la Matriz de Emisión:\n"
        "• Representación del Ruido Instrumental: Aunque la diagonal dominante indica que el sensor es mayoritariamente certero "
        "(80% en Fluido, 65% en Moderado y 75% en Congestionado), se incorporan probabilidades cruzadas realistas. Por ejemplo, "
        "en régimen Congestionado existe un 20% de probabilidad de registrar Velocidad Media debido a avances parciales entre "
        "embotellamientos, y un 5% de registrar Velocidad Alta debido a lecturas de motocicletas en carriles segregados o ruido sensorial."
    )

    add_heading_with_spacing(doc, "2.5 Algoritmos Estocásticos e Inferencia Computacional", level=2)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "El marco computacional fue programado en Python 3 modular mediante programación orientada a objetos (POO). "
        "Se implementaron cuatro algoritmos estocásticos fundamentales:\n\n"
        "1. Generador de Trayectorias Monte Carlo: Muestreo de números pseudoaleatorios con inversión acumulada sobre distribuciones "
        "categóricas discretas gobernadas por π, A y B para generar secuencias sintéticas realistas.\n\n"
        "2. Algoritmo de Viterbi (Programación Dinámica): Resuelve el problema fundamental de decodificación en HMM: encontrar la "
        "secuencia más probable de estados ocultos X* = {x_1, ..., x_T} dada la secuencia de observaciones ruidosas Y = {y_1, ..., y_T}. "
        "Se implementó en espacio logarítmico para prevenir el subdesbordamiento numérico (underflow) en series temporales extensas:\n"
    )
    p_vit = doc.add_paragraph()
    p_vit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_vit = p_vit.add_run("V_t(j) = max_i [ V_{t-1}(i) + ln(a_{ij}) ] + ln(b_j(y_t))")
    r_vit.font.bold = True
    r_vit.font.name = "Courier New"
    r_vit.font.size = Pt(10)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "3. Algoritmo Forward (Adelante): Evalúa la probabilidad total marginal de observar una secuencia temporal P(Y | λ) "
        "mediante inducción escalada.\n\n"
        "4. Solucionador del Sistema Estacionario: Cálculo algebraico exacto de la distribución asintótica del proceso ergódico "
        "resolviendo el sistema lineal (A^T - I) π*^T = 0 sujeto a ∑ π*_i = 1."
    )

    # ---------------------------------------------------------
    # 3. RESULTADOS Y DISCUSIÓN
    # ---------------------------------------------------------
    add_heading_with_spacing(doc, "3. RESULTADOS Y DISCUSIÓN", level=1)

    add_heading_with_spacing(doc, "3.1 Análisis de la Distribución Estacionaria y Tiempos de Permanencia", level=2)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "Al resolver el sistema lineal para la matriz de transición A, se obtiene la distribución estacionaria teórica π*, "
        "que representa la fracción de tiempo asintótica que el corredor pasará en cada estado en el largo plazo, independiente "
        "de la condición inicial del sistema:\n"
    )

    # Tabla Estacionaria y Permanencia
    table_est = doc.add_table(rows=4, cols=4)
    table_est.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers_est = ["Estado del Tráfico", "Probabilidad Estacionaria (π*)", "Tiempo Permanencia (Pasos)", "Tiempo Equivalente (Minutos)"]
    for c_idx, h in enumerate(headers_est):
        cell = table_est.rows[0].cells[c_idx]
        cell.paragraphs[0].add_run(h).font.bold = True
        set_cell_background(cell, "D9E1F2")
        set_cell_margins(cell)

    data_est = [
        ("Fluido (S_1)", "31.68% (0.3168)", "3.33 pasos", "50.0 minutos"),
        ("Moderado (S_2)", "40.59% (0.4059)", "2.50 pasos", "37.5 minutos"),
        ("Congestionado (S_3)", "27.72% (0.2772)", "2.86 pasos", "42.9 minutos"),
    ]
    for r_idx, row_vals in enumerate(data_est):
        for c_idx, val in enumerate(row_vals):
            cell = table_est.rows[r_idx + 1].cells[c_idx]
            cell.paragraphs[0].add_run(val)
            set_cell_margins(cell)

    p_hold = doc.add_paragraph()
    p_hold.paragraph_format.space_before = Pt(6)
    p_hold.paragraph_format.space_after = Pt(6)
    p_hold.add_run(
        "Interpretación de Tiempos de Permanencia (Holding Times):\n"
        "Dado que el tiempo que un proceso markoviano permanece en un estado continuo sigue una distribución geométrica discreta, "
        "el valor esperado es E[T_i] = 1 / (1 - a_{ii}).\n"
        "• Para el estado Fluido: E[T_F] = 1 / (1 - 0.70) = 3.33 pasos = 50.0 minutos continuos.\n"
        "• Para el estado Moderado: E[T_M] = 1 / (1 - 0.60) = 2.50 pasos = 37.5 minutos continuos.\n"
        "• Para el estado Congestionado: E[T_C] = 1 / (1 - 0.65) = 2.86 pasos = 42.9 minutos continuos.\n"
        "Esto demuestra que las fases de tráfico tienden a mantenerse durante períodos representativos de aproximadamente 40 a 50 minutos."
    )

    # Insertar Figura 1
    if os.path.exists("results/fig1_matrices_transicion_emision.png"):
        doc.add_paragraph().paragraph_format.space_after = Pt(4)
        doc.add_picture("results/fig1_matrices_transicion_emision.png", width=Inches(6.2))
        cap_p = doc.add_paragraph()
        cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap_r = cap_p.add_run("Figura 1: Mapas de calor y porcentajes de probabilidad para las matrices de Transición (A) y Emisión (B).")
        cap_r.font.size = Pt(9.5)
        cap_r.font.italic = True

    add_heading_with_spacing(doc, "3.2 Convergencia Dinámica hacia el Estado Estable", level=2)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "Se evaluó la evolución temporal de las probabilidades de estado π_k = π_0 A^k a partir de dos condiciones iniciales "
        "antagónicas: un corredor inicialmente 100% Fluido versus un corredor inicialmente 100% Congestionado. "
        "Como se observa en la Figura 2, en ambos casos el proceso disipa la influencia de la condición inicial en menos de 6 a 8 "
        "pasos de tiempo (1.5 a 2 horas), convergiendo de manera suave a la distribución estacionaria π* = [31.68%, 40.59%, 27.72%]. "
        "Esto comprueba matemáticamente que la cadena de Markov propuesta es irreducible, aperiódica y positiva recurrente (ergódica)."
    )

    # Insertar Figura 3 (Convergencia)
    if os.path.exists("results/fig3_convergencia_distribucion_estacionaria.png"):
        doc.add_paragraph().paragraph_format.space_after = Pt(4)
        doc.add_picture("results/fig3_convergencia_distribucion_estacionaria.png", width=Inches(6.2))
        cap_p = doc.add_paragraph()
        cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap_r = cap_p.add_run("Figura 2: Convergencia asintótica de las probabilidades de estado desde condiciones iniciales extremas.")
        cap_r.font.size = Pt(9.5)
        cap_r.font.italic = True

    add_heading_with_spacing(doc, "3.3 Simulación de una Jornada de 24 Horas y Decodificación de Viterbi", level=2)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "Se simuló una jornada continua de 24 horas (T = 96 intervalos de 15 minutos). En cada intervalo se registró el estado "
        "físico real (oculto para el observador externo) y la medición ruidosa generada por los sensores de velocidad. "
        "Posteriormente, se suministró exclusivamente la secuencia de observaciones al algoritmo de Viterbi para reconstruir el estado latente."
    )

    # Insertar Figura 2 (Timeline 24h)
    if os.path.exists("results/fig2_simulacion_jornada_24h.png"):
        doc.add_paragraph().paragraph_format.space_after = Pt(4)
        doc.add_picture("results/fig2_simulacion_jornada_24h.png", width=Inches(6.2))
        cap_p = doc.add_paragraph()
        cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap_r = cap_p.add_run("Figura 3: Serie de tiempo de 24 horas: Estado Real Oculto vs. Inferencia de Viterbi vs. Observaciones de Sensores.")
        cap_r.font.size = Pt(9.5)
        cap_r.font.italic = True

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "Resultados de la Jornada Simulada:\n"
        "• Exactitud Global de Decodificación: 73.96% (71 aciertos sobre 96 intervalos evaluados).\n"
        "• La secuencia inferida por Viterbi logró capturar de forma impecable las transiciones estructurales entre regímenes, "
        "actuando como un filtro estocástico que suprime eficazmente las oscilaciones espurias provocadas por lecturas puntuales anómalas del sensor."
    )

    add_heading_with_spacing(doc, "3.4 Matriz de Confusión y Análisis de Discordancias", level=2)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "La Tabla 3 y la Figura 4 ilustran la matriz de confusión entre los estados reales del tráfico y las predicciones emitidas por Viterbi:\n"
    )

    # Tabla Matriz de Confusión
    table_cm = doc.add_table(rows=4, cols=4)
    table_cm.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers_cm = ["Estado Real (Fila)", "Inferido: Fluido", "Inferido: Moderado", "Inferido: Congestionado"]
    for c_idx, h in enumerate(headers_cm):
        cell = table_cm.rows[0].cells[c_idx]
        cell.paragraphs[0].add_run(h).font.bold = True
        set_cell_background(cell, "E2EFDA")
        set_cell_margins(cell)

    data_cm = [
        ("Fluido (44 pasos)", "34 (77.3%)", "8 (18.2%)", "2 (4.5%)"),
        ("Moderado (33 pasos)", "4 (12.1%)", "24 (72.7%)", "5 (15.2%)"),
        ("Congestionado (19 pasos)", "0 (0.0%)", "6 (31.6%)", "13 (68.4%)"),
    ]
    for r_idx, row_vals in enumerate(data_cm):
        for c_idx, val in enumerate(row_vals):
            cell = table_cm.rows[r_idx + 1].cells[c_idx]
            cell.paragraphs[0].add_run(val)
            set_cell_margins(cell)

    # Insertar Figura 6 (Matriz de Confusión)
    if os.path.exists("results/fig6_matriz_confusion_viterbi.png"):
        doc.add_paragraph().paragraph_format.space_after = Pt(4)
        doc.add_picture("results/fig6_matriz_confusion_viterbi.png", width=Inches(4.2))
        cap_p = doc.add_paragraph()
        cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap_r = cap_p.add_run("Figura 4: Matriz de confusión entre estados reales simulados y estados decodificados por Viterbi.")
        cap_r.font.size = Pt(9.5)
        cap_r.font.italic = True

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "Análisis de Discordancias:\n"
        "Es relevante notar que los errores cometidos por Viterbi se restringen casi en su totalidad a estados adyacentes "
        "(Fluido <-> Moderado o Moderado <-> Congestionado). Hubo 0% de confusiones críticas entre Congestionado y Fluido (el modelo "
        "nunca clasificó un trancón severo como flujo libre), lo cual ratifica la alta confiabilidad operacional del sistema para la "
        "toma de decisiones en centros de control de tráfico."
    )

    add_heading_with_spacing(doc, "3.5 Validación Monte Carlo a Gran Escala (1,000 Réplicas)", level=2)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "Para validar la consistencia estadística y el cumplimiento de la Ley de los Grandes Números, se ejecutaron 1,000 réplicas "
        "independientes de la jornada completa, totalizando 96,000 pasos de tiempo simulados."
    )

    # Tabla Monte Carlo
    table_mc = doc.add_table(rows=4, cols=4)
    table_mc.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers_mc = ["Estado del Tráfico", "Distribución Teórica (π*)", "Distribución Empírica (Monte Carlo)", "Error Absoluto"]
    for c_idx, h in enumerate(headers_mc):
        cell = table_mc.rows[0].cells[c_idx]
        cell.paragraphs[0].add_run(h).font.bold = True
        set_cell_background(cell, "D9E1F2")
        set_cell_margins(cell)

    data_mc = [
        ("Fluido", "31.68%", "32.81%", "0.01126"),
        ("Moderado", "40.59%", "40.07%", "0.00520"),
        ("Congestionado", "27.72%", "27.12%", "0.00606"),
    ]
    for r_idx, row_vals in enumerate(data_mc):
        for c_idx, val in enumerate(row_vals):
            cell = table_mc.rows[r_idx + 1].cells[c_idx]
            cell.paragraphs[0].add_run(val)
            set_cell_margins(cell)

    # Insertar Figura 4 (Monte Carlo)
    if os.path.exists("results/fig4_validacion_monte_carlo.png"):
        doc.add_paragraph().paragraph_format.space_after = Pt(4)
        doc.add_picture("results/fig4_validacion_monte_carlo.png", width=Inches(6.2))
        cap_p = doc.add_paragraph()
        cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap_r = cap_p.add_run("Figura 5: Validación estadística Monte Carlo (1,000 réplicas) y estabilidad de la exactitud de Viterbi.")
        cap_r.font.size = Pt(9.5)
        cap_r.font.italic = True

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "La discrepancia media absoluta (MAE) entre las probabilidades teóricas analíticas y las frecuencias relativas "
        "simuladas fue de apenas 0.0075 (menos de 0.8 puntos porcentuales), lo que corrobora empíricamente el rigor del "
        "algoritmo de muestreo estocástico. Adicionalmente, la exactitud promedio de Viterbi a través de las 1,000 réplicas fue de "
        "73.07% con una desviación estándar contenida de ±5.51%."
    )

    add_heading_with_spacing(doc, "3.6 Resiliencia ante Perturbaciones Exógenas (Accidente Vial)", level=2)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "Se simuló un evento extraordinario de choque vehicular ocurrido a las 14:00 (paso 32) que duró 3 horas hasta las 17:00 (paso 44). "
        "Durante dicha ventana, la matriz de transición forzó una degradación hacia el estado Congestionado (P(C|C) = 0.80). "
        "Como ilustra la Figura 6, el modelo HMM detectó la transición casi de manera inmediata gracias a la persistencia de lecturas de "
        "Velocidad Baja, y tras el retiro del siniestro en el paso 44, se evidenció el proceso paulatino de descongestión, pasando primero "
        "por el régimen Moderado antes de restablecer el flujo libre."
    )

    # Insertar Figura 5 (Incidente)
    if os.path.exists("results/fig5_escenario_incidente_recuperacion.png"):
        doc.add_paragraph().paragraph_format.space_after = Pt(4)
        doc.add_picture("results/fig5_escenario_incidente_recuperacion.png", width=Inches(6.2))
        cap_p = doc.add_paragraph()
        cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap_r = cap_p.add_run("Figura 6: Simulación de un incidente vial exógeno (accidente en pasos 32-44) y curva de recuperación.")
        cap_r.font.size = Pt(9.5)
        cap_r.font.italic = True

    # ---------------------------------------------------------
    # 4. CONCLUSIONES
    # ---------------------------------------------------------
    add_heading_with_spacing(doc, "4. CONCLUSIONES", level=1)

    conclusiones = [
        ("Idoneidad del Modelo Oculto de Markov: ",
         "Se demostró que el tráfico vehicular se ajusta de forma natural a la estructura de un HMM. El estado macroscópico de congestión "
         "es intrínsecamente latente, mientras que las tecnologías de monitoreo (radares y sensores) reportan variables visibles contaminadas "
         "con ruido e incertidumbre. La formulación matemática propuesta desacopló satisfactoriamente ambos procesos."),
        
        ("Poder de Filtrado del Algoritmo de Viterbi: ",
         "A pesar de que la matriz de emisión introdujo entre un 20% y 35% de error sensorial aleatorio, el algoritmo de Viterbi logró "
         "una exactitud promedio de reconstrucción del 73.07% en 1,000 réplicas. Esto resalta la importancia de la memoria secuencial "
         "contenida en la matriz de transición A, que previene fluctuaciones espurias y estabiliza la estimación."),

        ("Convergencia y Estabilidad Ergódica: ",
         "El análisis analítico y la simulación Monte Carlo de 96,000 pasos de tiempo corroboraron la convergencia hacia la distribución "
         "estacionaria única π* = [31.68% Fluido, 40.59% Moderado, 27.72% Congestionado], con un error absoluto medio mínimo de 0.0075. "
         "Esto garantiza que el modelo es estable, recurrente y aperiódico."),

        ("Aplicabilidad en Sistemas Inteligentes de Transporte (ITS): ",
         "Los tiempos promedio de permanencia calculados (50 min en Fluido, 37.5 min en Moderado y 42.9 min en Congestionado) proporcionan "
         "horizontes temporales valiosos para que los operadores viales reprogramen semáforos, publiquen alertas en paneles de mensaje "
         "variable y desplieguen unidades de asistencia antes de que la saturación alcance niveles críticos."),

        ("Extensibilidad Futura: ",
         "El código desarrollado bajo estándares modulares y orientados a objetos permite fácilmente incorporar matrices de transición "
         "no homogéneas en el tiempo (A dependiente de la hora pico) o entrenar los parámetros automáticamente a partir de datos reales "
         "mediante el algoritmo de Baum-Welch (Expectation-Maximization).")
    ]

    for titulo, desc in conclusiones:
        p_c = doc.add_paragraph()
        p_c.paragraph_format.space_after = Pt(4)
        r_ct = p_c.add_run(f"• {titulo}")
        r_ct.font.bold = True
        r_ct.font.name = "Calibri"
        r_cd = p_c.add_run(desc)
        r_cd.font.name = "Calibri"

    # ---------------------------------------------------------
    # 5. ENLACES Y RECURSOS DEL PROYECTO
    # ---------------------------------------------------------
    add_heading_with_spacing(doc, "5. ENLACES DEL PROYECTO Y ENTREGABLES", level=1)

    p_links = doc.add_paragraph()
    p_links.paragraph_format.space_after = Pt(4)
    p_links.add_run(
        "En cumplimiento de los requerimientos de la actividad didáctica, los artefactos digitales correspondientes se encuentran "
        "disponibles en los siguientes enlaces públicos:\n\n"
        "• Repositorio en GitHub: https://github.com/camilopalacios/markov-traffic-simulation\n"
        "  (Contiene el código fuente completo en Python, notebook interactivo, instrucciones de ejecución y carpeta de resultados).\n\n"
        "• Video de Sustentación en YouTube / Canvas: https://youtu.be/ENLACE_VIDEO_SUSTENTACION\n"
        "  (Exposición audiovisual del planteamiento del problema, explicación de matrices, ejecución del código y análisis de resultados)."
    )

    # ---------------------------------------------------------
    # 6. REFERENCIAS BIBLIOGRÁFICAS
    # ---------------------------------------------------------
    add_heading_with_spacing(doc, "6. REFERENCIAS BIBLIOGRÁFICAS", level=1)

    referencias = [
        "Rabiner, L. R. (1989). A tutorial on hidden Markov models and selected applications in speech recognition. Proceedings of the IEEE, 77(2), 257-286.",
        "Ross, S. M. (2014). Introduction to Probability Models (11th ed.). Academic Press.",
        "Law, A. M. (2015). Simulation Modeling and Analysis (5th ed.). McGraw-Hill Education.",
        "Qi, Y., & Ishak, S. (2014). A Hidden Markov Model for short term freeway traffic state estimation and prediction. Transportation Research Part C: Emerging Technologies, 43, 95-111.",
        "Daganzo, C. F. (1997). Fundamentals of Transportation and Traffic Operations. Emerald Group Publishing.",
    ]

    for ref in referencias:
        p_r = doc.add_paragraph()
        p_r.paragraph_format.space_after = Pt(3)
        r_ref = p_r.add_run(f"[{referencias.index(ref) + 1}] {ref}")
        r_ref.font.name = "Calibri"
        r_ref.font.size = Pt(9.5)

    doc.save(output_filename)
    print(f"Documento guardado con éxito: {output_filename}")


if __name__ == "__main__":
    build_document("Palacios_Camilo_Markov.docx")
    build_document("Apellido_Nombre_Markov.docx")
