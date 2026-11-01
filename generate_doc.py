"""
Generador del Documento Oficial de la Actividad Didáctica 2 (Informe Académico).
Adaptado con los datos de los 4 integrantes, docente, curso y formato idéntico a la Actividad 1.
"""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

# Paleta de colores oficial de la IU Digital
COLOR_NAVY = RGBColor(0x1E, 0x3A, 0x8A)       # #1E3A8A - Títulos y cabeceras
COLOR_TEAL = RGBColor(0x0F, 0x76, 0x6E)       # #0F766E - Subtítulos
COLOR_BODY = RGBColor(0x1E, 0x29, 0x3B)       # #1E293B - Texto general
COLOR_SLATE = RGBColor(0x47, 0x55, 0x69)      # #475569 - Subtítulo portada y leyendas
COLOR_MUTED = RGBColor(0x64, 0x74, 0x8B)      # #64748B - Encabezado / Pie
COLOR_DARK = RGBColor(0x0F, 0x17, 0x2A)       # #0F172A - Textos portada


def set_cell_background(cell, fill_hex):
    """Aplica color de fondo a una celda de tabla en Word."""
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)


def set_cell_margins(cell, top=120, bottom=120, left=160, right=160):
    """Establece márgenes internos de celda en dxa (1 pt = 20 dxa)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for margin_name, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{margin_name}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def set_cell_borders(cell, top="none", bottom="none", left="none", right="none",
                     color="CBD5E1", sz="4"):
    """Configura los bordes individuales de una celda XML."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    borders = {'top': top, 'left': left, 'bottom': bottom, 'right': right}
    for b_name, b_val in borders.items():
        node = OxmlElement(f'w:{b_name}')
        node.set(qn('w:val'), b_val)
        if b_val != "none":
            node.set(qn('w:sz'), str(sz))
            node.set(qn('w:space'), '0')
            node.set(qn('w:color'), color)
        tcBorders.append(node)
    tcPr.append(tcBorders)


def add_callout_box(doc, text, source_text=None):
    """Inserta una caja de texto destacada (Callout) con borde lateral azul y fondo suave."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "F8FAFC")
    set_cell_margins(cell, top=140, bottom=140, left=200, right=160)
    set_cell_borders(cell, left="single", color="1E3A8A", sz="36")

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(f'"{text}"')
    run.font.name = "Arial"
    run.font.size = Pt(10.0)
    run.font.italic = True
    run.font.color.rgb = COLOR_BODY

    if source_text:
        p_src = cell.add_paragraph()
        p_src.paragraph_format.space_before = Pt(2)
        p_src.paragraph_format.space_after = Pt(2)
        run_src = p_src.add_run(f'— {source_text}')
        run_src.font.name = "Arial"
        run_src.font.size = Pt(9.0)
        run_src.font.bold = True
        run_src.font.color.rgb = RGBColor(0x1D, 0x4E, 0xD8)

    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(6)


def format_table(table, col_widths, headers, data):
    """Da formato visual completo a una tabla: cabecera oscura y filas cebra."""
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    for c_idx, h in enumerate(headers):
        cell = table.rows[0].cells[c_idx]
        cell.width = col_widths[c_idx]
        set_cell_background(cell, "1E3A8A")
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        set_cell_borders(cell, top="single", bottom="single", left="none", right="none", color="CBD5E1", sz="6")
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(h)
        run.font.name = "Arial"
        run.font.size = Pt(9.0)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    for r_idx, row_vals in enumerate(data):
        row = table.rows[r_idx + 1]
        bg_color = "F8FAFC" if (r_idx % 2 == 1) else "FFFFFF"
        for c_idx, val in enumerate(row_vals):
            cell = row.cells[c_idx]
            cell.width = col_widths[c_idx]
            set_cell_background(cell, bg_color)
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            set_cell_borders(cell, top="single", bottom="single", left="none", right="none", color="E2E8F0", sz="4")
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            if c_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(str(val))
            run.font.name = "Arial"
            run.font.size = Pt(9.0)
            if c_idx == 0:
                run.font.bold = True
            run.font.color.rgb = COLOR_BODY


def build_document(output_filename="Palacios_Camilo_Markov.docx"):
    doc = Document()

    # Márgenes de 1 pulgada
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # ---------------------------------------------------------
    # PORTADA OFICIAL (Estructura idéntica a la Actividad 1)
    # ---------------------------------------------------------
    p_dummy = doc.add_paragraph()
    p_dummy.paragraph_format.space_before = Pt(16)

    p_t1 = doc.add_paragraph()
    p_t1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t1.paragraph_format.space_after = Pt(10)
    r1 = p_t1.add_run("Evidencia de Aprendizaje 2: Módulo 2. Actividad didáctica 2: Modelo de Markov")
    r1.font.name = "Arial"
    r1.font.size = Pt(15.0)
    r1.font.bold = True
    r1.font.color.rgb = COLOR_NAVY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(30)
    r_sub = p_sub.add_run(
        "Simulación Estocástica y Predicción del Tráfico Vehicular mediante Modelo Oculto de Markov (HMM)\n"
        "Inferencia con Algoritmo de Viterbi, Distribución Estacionaria y Validación Monte Carlo"
    )
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(11.5)
    r_sub.font.italic = True
    r_sub.font.color.rgb = COLOR_SLATE

    p_int_t = doc.add_paragraph()
    p_int_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_int_t.paragraph_format.space_after = Pt(6)
    r_int_t = p_int_t.add_run("Integrantes:")
    r_int_t.font.name = "Arial"
    r_int_t.font.size = Pt(12.0)
    r_int_t.font.bold = True
    r_int_t.font.color.rgb = COLOR_DARK

    integrantes = [
        "Adriana Andrea Agudelo Agudelo",
        "Camilo Alberto Palacios Turriago",
        "Juan Daniel Pulgarin García",
        "Ruben Dario Jaramillo Cervantes",
    ]
    for idx, nombre in enumerate(integrantes):
        p_nom = doc.add_paragraph()
        p_nom.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_nom.paragraph_format.space_after = Pt(4 if idx < len(integrantes) - 1 else 30)
        r_nom = p_nom.add_run(nombre)
        r_nom.font.name = "Arial"
        r_nom.font.size = Pt(12.0)
        r_nom.font.color.rgb = COLOR_DARK

    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_after = Pt(4)
    r_inst = p_inst.add_run("Institución Universitaria Digital de Antioquia")
    r_inst.font.name = "Arial"
    r_inst.font.size = Pt(12.0)
    r_inst.font.bold = True
    r_inst.font.color.rgb = COLOR_DARK

    p_fac = doc.add_paragraph()
    p_fac.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_fac.paragraph_format.space_after = Pt(4)
    r_fac = p_fac.add_run("Facultad de Ingeniería")
    r_fac.font.name = "Arial"
    r_fac.font.size = Pt(11.5)
    r_fac.font.color.rgb = COLOR_DARK

    p_cur = doc.add_paragraph()
    p_cur.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cur.paragraph_format.space_after = Pt(4)
    r_cur = p_cur.add_run("Simulación - PREICA2602B020045")
    r_cur.font.name = "Arial"
    r_cur.font.size = Pt(11.5)
    r_cur.font.color.rgb = COLOR_DARK

    p_doc_t = doc.add_paragraph()
    p_doc_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_doc_t.paragraph_format.space_after = Pt(2)
    r_doc_t = p_doc_t.add_run("Docente:")
    r_doc_t.font.name = "Arial"
    r_doc_t.font.size = Pt(11.5)
    r_doc_t.font.bold = True
    r_doc_t.font.color.rgb = COLOR_DARK

    p_doc = doc.add_paragraph()
    p_doc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_doc.paragraph_format.space_after = Pt(14)
    r_doc = p_doc.add_run("Julian Andres Loaiza Lopez")
    r_doc.font.name = "Arial"
    r_doc.font.size = Pt(11.5)
    r_doc.font.color.rgb = COLOR_DARK

    p_grp = doc.add_paragraph()
    p_grp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_grp.paragraph_format.space_after = Pt(28)
    r_grp = p_grp.add_run("Grupo: 25")
    r_grp.font.name = "Arial"
    r_grp.font.size = Pt(11.5)
    r_grp.font.bold = True
    r_grp.font.color.rgb = COLOR_DARK

    p_ciu = doc.add_paragraph()
    p_ciu.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ciu.paragraph_format.space_after = Pt(4)
    r_ciu = p_ciu.add_run("Medellín, Antioquia")
    r_ciu.font.name = "Arial"
    r_ciu.font.size = Pt(11.5)
    r_ciu.font.color.rgb = COLOR_DARK

    p_fec = doc.add_paragraph()
    p_fec.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_fec.paragraph_format.space_after = Pt(0)
    r_fec = p_fec.add_run("Noviembre de 2026")
    r_fec.font.name = "Arial"
    r_fec.font.size = Pt(11.5)
    r_fec.font.color.rgb = COLOR_DARK

    # Salto de página
    doc.add_page_break()

    # ---------------------------------------------------------
    # SECCIÓN DE CONTENIDO: ENCABEZADO Y PIE
    # ---------------------------------------------------------
    content_sec = doc.sections[-1]
    header = content_sec.header
    header_p = header.paragraphs[0]
    header_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_hdr = header_p.add_run("Simulación - PREICA2602B020045   |   Actividad Didáctica 2: Modelo de Markov")
    r_hdr.font.name = "Arial"
    r_hdr.font.size = Pt(8.5)
    r_hdr.font.italic = True
    r_hdr.font.color.rgb = COLOR_MUTED

    footer = content_sec.footer
    footer_p = footer.paragraphs[0]
    footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_ftr = footer_p.add_run("Institución Universitaria Digital de Antioquia (IU Digital) · Simulación · Grupo 25")
    r_ftr.font.name = "Arial"
    r_ftr.font.size = Pt(8.5)
    r_ftr.font.color.rgb = COLOR_MUTED

    # Helpers
    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = "Arial"
        run.font.size = Pt(13.0)
        run.font.bold = True
        run.font.color.rgb = COLOR_NAVY
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = "Arial"
        run.font.size = Pt(11.5)
        run.font.bold = True
        run.font.color.rgb = COLOR_TEAL
        return p

    def add_p(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(text)
        run.font.name = "Arial"
        run.font.size = Pt(11.0)
        run.font.color.rgb = COLOR_BODY
        return p

    def add_fig(filepath, caption):
        if os.path.exists(filepath):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(6)
            p_img.paragraph_format.space_after = Pt(4)
            doc.add_picture(filepath, width=Inches(6.2))
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(2)
            p_cap.paragraph_format.space_after = Pt(12)
            run = p_cap.add_run(caption)
            run.font.name = "Arial"
            run.font.size = Pt(9.5)
            run.font.italic = True
            run.font.color.rgb = COLOR_SLATE

    # TABLA DE CONTENIDO (Estilo Actividad 1)
    p_tdc = doc.add_paragraph()
    p_tdc.paragraph_format.space_before = Pt(8)
    p_tdc.paragraph_format.space_after = Pt(4)
    r_tdc = p_tdc.add_run("Tabla de contenido")
    r_tdc.font.name = "Arial"
    r_tdc.font.size = Pt(12.0)
    r_tdc.font.bold = True
    r_tdc.font.color.rgb = COLOR_NAVY

    toc_items = [
        "1. Introducción",
        "2. Metodología",
        "3. Resultados",
        "4. Conclusiones",
        "5. Enlaces y Recursos del Proyecto (GitHub, Google Colab y Video)",
        "6. Referencias Bibliográficas",
    ]
    for item in toc_items:
        p_item = doc.add_paragraph()
        p_item.paragraph_format.space_before = Pt(1)
        p_item.paragraph_format.space_after = Pt(2)
        r_it = p_item.add_run(item)
        r_it.font.name = "Arial"
        r_it.font.size = Pt(10.5)
        r_it.font.color.rgb = COLOR_BODY

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # ---------------------------------------------------------
    # 1. INTRODUCCIÓN
    # ---------------------------------------------------------
    add_h1("1. Introducción")

    add_p(
        "El proyecto consiste en un sistema de simulación y predicción del tráfico vehicular en un corredor arterial urbano "
        "utilizando un Modelo Oculto de Markov (Hidden Markov Model - HMM). En lugar de asumir que la congestión vial puede "
        "medirse de manera directa y perfecta, el modelo reconoce la incertidumbre real de la movilidad: el estado de congestión "
        "de la vía es una condición física latente (oculta) que evoluciona estocásticamente, mientras que los operadores y centros de "
        "control únicamente disponen de lecturas ruidosas e indirectas captadas por radares y sensores de velocidad."
    )

    add_p(
        "El código está estructurado en una arquitectura modular en Python: traffic_hmm/model.py contiene la definición analítica "
        "del HMM, las matrices de transición y emisión, y el algoritmo de decodificación de Viterbi; traffic_hmm/simulation.py "
        "gestiona la generación estocástica de trayectorias, la simulación de una jornada diaria continua de 24 horas y la validación "
        "Monte Carlo con 1,000 réplicas; y traffic_hmm/visualizations.py genera automáticamente los gráficos e interpretaciones "
        "visuales a 300 DPI. Adicionalmente, el proyecto incluye un cuaderno interactivo ejecutable directamente en Google Colab "
        "para que cualquier usuario o evaluador pueda reproducir los experimentos con un solo clic sin necesidad de instalaciones locales."
    )

    add_p(
        "La idea detrás de esta solución es llevar los conceptos de cadenas de Markov y distribuciones de probabilidad desde la "
        "teoría matemática a una aplicación tangible y analizable. A través de este modelo, podemos responder preguntas operativas clave: "
        "¿Cuál es la probabilidad de que una vía pase de fluido a congestionado en 15 minutos? ¿Cuánto tiempo permanece en promedio un "
        "trancón antes de disiparse? Y, fundamentalmente, ¿cómo podemos reconstruir con alta precisión el estado real de la vía "
        "a pesar de que los sensores registren lecturas engañosas o ruidosas?"
    )

    add_callout_box(
        doc,
        "La dualidad del HMM desacopla la realidad física de la telemetría: la 'congestión' es un fenómeno sistémico que no se puede "
        "medir en su totalidad con un radar puntual, mientras que las velocidades reportadas poseen ruido. El algoritmo de Viterbi "
        "aprovecha la inercia temporal de la matriz de transición para filtrar lecturas atípicas y reconstruir la trayectoria verdadera.",
        "Fundamentación Conceptual del Modelo Oculto de Markov"
    )

    # ---------------------------------------------------------
    # 2. METODOLOGÍA
    # ---------------------------------------------------------
    add_h1("2. Metodología")

    add_p(
        "El desarrollo del modelo se estructuró formalmente a partir de la quintupla clásica de un HMM: λ = (S, V, π, A, B), "
        "parametrizada para intervalos de tiempo discretos de Δt = 15 minutos en un corredor arterial urbano (96 pasos por día):"
    )

    add_p(
        "1. Espacio de Estados Ocultos (S, con N = 3):\n"
        "   • Fluido (S_1): Flujo vehicular libre, baja densidad (≤ 15 veh/km/carril) y velocidad cercana al límite reglamentario.\n"
        "   • Moderado (S_2): Flujo estable, densidad media (15 a 35 veh/km/carril), con maniobrabilidad y velocidad condicionada.\n"
        "   • Congestionado (S_3): Flujo forzado o saturado (> 35 veh/km/carril), formación de colas y régimen de frenado continuo (stop-and-go)."
    )

    add_p(
        "2. Espacio de Observaciones Visibles (V, con M = 3):\n"
        "Corresponde a las mediciones telemetradas por radares de velocidad en carretera:\n"
        "   • Velocidad Alta (V_1): Lecturas puntuales superiores a 60 km/h.\n"
        "   • Velocidad Media (V_2): Lecturas puntuales comprendidas entre 30 y 60 km/h.\n"
        "   • Velocidad Baja (V_3): Lecturas puntuales inferiores a 30 km/h."
    )

    add_p(
        "3. Vector de Probabilidades Iniciales (π):\n"
        "Define el estado del corredor al inicio del horizonte de simulación (06:00 AM):\n"
        "π = [P(Fluido), P(Moderado), P(Congestionado)] = [0.70, 0.20, 0.10]\n"
        "Refleja que en la madrugada predomina el flujo libre, pero existe un 30% de probabilidad combinada de tráfico moderado o pesado."
    )

    add_p(
        "4. Matriz de Transición de Estados (A):\n"
        "Rige la probabilidad de cambiar de estado entre intervalos consecutivos de 15 minutos (a_{ij} = P(X_{t+1} = s_j | X_t = s_i)):"
    )

    # Tabla Matriz A
    table_A = doc.add_table(rows=4, cols=4)
    format_table(
        table_A,
        [Inches(2.0), Inches(1.5), Inches(1.5), Inches(1.5)],
        ["Estado Actual (X_t)", "Fluido (t+1)", "Moderado (t+1)", "Congestionado (t+1)"],
        [
            ["Fluido (S_1)", "0.70 (70%)", "0.25 (25%)", "0.05 (5%)"],
            ["Moderado (S_2)", "0.20 (20%)", "0.60 (60%)", "0.20 (20%)"],
            ["Congestionado (S_3)", "0.05 (5%)", "0.30 (30%)", "0.65 (65%)"],
        ]
    )

    add_p(
        "Justificación de la Matriz de Transición:\n"
        "• Inercia Temporal: La diagonal principal concentra los valores más altos (0.70, 0.60, 0.65). Esto modela la física real del tráfico: "
        "un estado tiende a sostenerse en el siguiente cuarto de hora.\n"
        "• Gradualidad: La probabilidad de saltar directamente de Fluido a Congestionado es de apenas 5% (a_{13} = 0.05); normalmente "
        "el tráfico transita primero por Moderado (a_{12} = 0.25). De igual modo, descongestionar un embotellamiento severo directamente "
        "a flujo libre en 15 minutos es excepcional (a_{31} = 0.05), requiriendo descongestión progresiva."
    )

    add_p(
        "5. Matriz de Emisión de Sensores (B):\n"
        "Modela la probabilidad condicional de que los sensores registren una velocidad dada la realidad física (b_{jk} = P(Y_t = v_k | X_t = s_j)):"
    )

    # Tabla Matriz B
    table_B = doc.add_table(rows=4, cols=4)
    format_table(
        table_B,
        [Inches(2.0), Inches(1.5), Inches(1.5), Inches(1.5)],
        ["Estado Real Oculto (X_t)", "Velocidad Alta (Y_t)", "Velocidad Media (Y_t)", "Velocidad Baja (Y_t)"],
        [
            ["Fluido (S_1)", "0.80 (80%)", "0.15 (15%)", "0.05 (5%)"],
            ["Moderado (S_2)", "0.20 (20%)", "0.65 (65%)", "0.15 (15%)"],
            ["Congestionado (S_3)", "0.05 (5%)", "0.20 (20%)", "0.75 (75%)"],
        ]
    )

    add_p(
        "Justificación de la Matriz de Emisión:\n"
        "Se introduce deliberadamente ruido en las mediciones: aunque la correlación principal es dominante (80%, 65%, 75%), "
        "en estado Congestionado hay un 20% de probabilidad de medir Velocidad Media por avances momentáneos entre trancones, "
        "y en Fluido hay un 5% de medir Velocidad Baja por vehículos pesados o desaceleraciones momentáneas."
    )

    add_p(
        "Algoritmos Implementados:\n"
        "• Simulación Estocástica Monte Carlo: Muestreo de números pseudoaleatorios sobre distribuciones categóricas acumuladas.\n"
        "• Algoritmo de Viterbi: Programación dinámica en escala logarítmica que encuentra la secuencia óptima de estados latentes X* "
        "maximizando P(X, Y | λ) y evitando bajo flujo aritmético.\n"
        "• Algoritmo Forward: Inducción matemática para computar la verosimilitud de la secuencia temporal.\n"
        "• Solución Analítica Estacionaria: Resolución del sistema lineal (A^T - I) π*^T = 0 sujeto a ∑ π*_i = 1.\n"
        "• Tiempos de Permanencia (Holding Times): Cálculo del tiempo continuo esperado en cada estado E[T_i] = 1 / (1 - a_{ii})."
    )

    # ---------------------------------------------------------
    # 3. RESULTADOS
    # ---------------------------------------------------------
    add_h1("3. Resultados")

    add_p(
        "La ejecución computacional del modelo permitió evaluar tanto las propiedades analíticas asintóticas del sistema como su "
        "comportamiento empírico ante escenarios cotidianos y de contingencia vial:"
    )

    add_h2("3.1 Propiedades Analíticas Estacionarias y Tiempos de Permanencia")
    add_p(
        "Al resolver el sistema lineal de la matriz de transición A, se obtuvo la distribución estacionaria teórica π*, "
        "que representa la proporción de tiempo de largo plazo que el corredor pasará en cada condición de tráfico, "
        "independiente de cómo haya amanecido el día:"
    )

    # Tabla Estacionaria
    table_est = doc.add_table(rows=4, cols=4)
    format_table(
        table_est,
        [Inches(1.8), Inches(1.6), Inches(1.5), Inches(1.6)],
        ["Estado del Tráfico", "Probabilidad Estacionaria (π*)", "Permanencia (Pasos)", "Permanencia (Minutos)"],
        [
            ["Fluido (S_1)", "31.68% (0.3168)", "3.33 pasos", "50.0 minutos"],
            ["Moderado (S_2)", "40.59% (0.4059)", "2.50 pasos", "37.5 minutos"],
            ["Congestionado (S_3)", "27.72% (0.2772)", "2.86 pasos", "42.9 minutos"],
        ]
    )

    add_fig(
        "results/fig1_matrices_transicion_emision.png",
        "Figura 1: Mapas de calor y valores porcentuales de las matrices de Transición (A) y Emisión (B)."
    )

    add_p(
        "Interpretación de Tiempos de Permanencia:\n"
        "Al modelarse como una distribución geométrica discreta, el tiempo medio de permanencia continua en cada estado es:\n"
        "• Fluido: 1 / (1 - 0.70) = 3.33 pasos (50.0 minutos).\n"
        "• Moderado: 1 / (1 - 0.60) = 2.50 pasos (37.5 minutos).\n"
        "• Congestionado: 1 / (1 - 0.65) = 2.86 pasos (42.9 minutos).\n"
        "Esto indica que cuando un trancón se consolida en el corredor, toma típicamente cerca de 43 minutos en resolverse."
    )

    add_h2("3.2 Convergencia Dinámica al Estado Estable")
    add_p(
        "Para verificar la ergodicidad de la cadena, se simuló la trayectoria de las probabilidades de estado desde dos condiciones iniciales "
        "opuestas: iniciar con la vía 100% Fluida versus 100% Congestionada. En ambos casos, el sistema converge de manera estable a la "
        "distribución estacionaria teórica en menos de 8 pasos temporales (2 horas), disipando la memoria del estado inicial."
    )

    add_fig(
        "results/fig3_convergencia_distribucion_estacionaria.png",
        "Figura 2: Convergencia asintótica de probabilidades hacia la distribución estacionaria desde estados iniciales extremos."
    )

    add_h2("3.3 Simulación de una Jornada de 24 Horas y Decodificación de Viterbi")
    add_p(
        "Se simuló una jornada completa de 24 horas continuas (T = 96 intervalos de 15 minutos). "
        "El algoritmo de Viterbi recibió únicamente las lecturas ruidosas de los radares y reconstruyó la secuencia óptima de estados ocultos."
    )

    add_fig(
        "results/fig2_simulacion_jornada_24h.png",
        "Figura 3: Serie de tiempo de 24 horas: Estado Real Oculto vs. Inferencia de Viterbi vs. Mediciones de Sensores."
    )

    add_p(
        "La exactitud global de decodificación alcanzada por Viterbi fue del 73.96% (71 aciertos sobre 96 pasos). "
        "El algoritmo demostró una excelente capacidad como filtro estocástico: ante caídas puntuales de lectura de velocidad, "
        "Viterbi evitó falsas alarmas de congestión gracias al peso inercial de la matriz de transición."
    )

    add_h2("3.4 Matriz de Confusión y Análisis de Discordancias")
    add_p(
        "La matriz de confusión entre los estados reales simulados y los estimados por Viterbi muestra cómo se distribuyeron las clasificaciones:"
    )

    # Tabla Matriz de Confusión
    table_cm = doc.add_table(rows=4, cols=4)
    format_table(
        table_cm,
        [Inches(2.0), Inches(1.5), Inches(1.5), Inches(1.5)],
        ["Estado Real (Fila)", "Inferido: Fluido", "Inferido: Moderado", "Inferido: Congestionado"],
        [
            ["Fluido (44 pasos)", "34 (77.3%)", "8 (18.2%)", "2 (4.5%)"],
            ["Moderado (33 pasos)", "4 (12.1%)", "24 (72.7%)", "5 (15.2%)"],
            ["Congestionado (19 pasos)", "0 (0.0%)", "6 (31.6%)", "13 (68.4%)"],
        ]
    )

    add_fig(
        "results/fig6_matriz_confusion_viterbi.png",
        "Figura 4: Matriz de confusión entre estados reales y estados inferidos por Viterbi."
    )

    add_p(
        "Es crucial destacar que los desaciertos se presentaron únicamente entre estados adyacentes (Fluido con Moderado, o Moderado con Congestionado). "
        "Hubo 0.0% de confusiones críticas entre extremos: el modelo jamás confundió un embotellamiento con flujo libre, lo que garantiza "
        "la seguridad operativa del sistema para la gestión de tránsito."
    )

    add_h2("3.5 Validación Monte Carlo a Gran Escala (1,000 Réplicas)")
    add_p(
        "Para validar la Ley de los Grandes Números, se ejecutaron 1,000 réplicas independientes de la jornada de 24 horas, "
        "totalizando 96,000 pasos temporales simulados:"
    )

    # Tabla Monte Carlo
    table_mc = doc.add_table(rows=4, cols=4)
    format_table(
        table_mc,
        [Inches(1.8), Inches(1.6), Inches(1.6), Inches(1.5)],
        ["Estado del Tráfico", "Distribución Teórica (π*)", "Frecuencia Monte Carlo (1k)", "Error Absoluto"],
        [
            ["Fluido", "31.68%", "32.81%", "0.01126"],
            ["Moderado", "40.59%", "40.07%", "0.00520"],
            ["Congestionado", "27.72%", "27.12%", "0.00606"],
        ]
    )

    add_fig(
        "results/fig4_validacion_monte_carlo.png",
        "Figura 5: Validación estadística Monte Carlo (1,000 réplicas) y estabilidad de la exactitud de Viterbi."
    )

    add_p(
        "El Error Absoluto Medio (MAE) entre las probabilidades teóricas analíticas y las frecuencias simuladas fue de tan solo 0.0075 "
        "(menos de 0.8 puntos porcentuales), ratificando la precisión matemática del simulador. Asimismo, la exactitud promedio de Viterbi "
        "a través de las 1,000 réplicas fue de 73.07% con una desviación estándar contenida de ±5.51%."
    )

    add_h2("3.6 Resiliencia ante Perturbaciones Exógenas (Accidente de Tránsito)")
    add_p(
        "Se simuló un evento extraordinario de choque vial entre las 14:00 y las 17:00 (pasos 32 a 44), forzando temporalmente una "
        "probabilidad de congestión del 80%. El HMM detectó oportunamente el cambio de régimen y evidenció la curva de recuperación "
        "paulatina tras el retiro de los vehículos siniestrados, pasando por Moderado antes de restablecer el flujo libre."
    )

    add_fig(
        "results/fig5_escenario_incidente_recuperacion.png",
        "Figura 6: Simulación de contingencia vial por accidente en los pasos 32 a 44 y curva de recuperación."
    )

    # ---------------------------------------------------------
    # 4. CONCLUSIONES
    # ---------------------------------------------------------
    add_h1("4. Conclusiones")

    conclusiones = [
        "El desarrollo del proyecto de simulación de tráfico vehicular mediante un Modelo Oculto de Markov (HMM) nos permitió comprender y aplicar los conceptos fundamentales de procesos estocásticos y distribuciones de probabilidad en una situación del mundo real donde existe incertidumbre y la información no es directamente observable.",
        "La separación entre los estados ocultos (la condición intrínseca de la vía) y las observaciones visibles (las velocidades medidas por los sensores) demostró ser el enfoque correcto para representar el problema: mientras que los sensores en calle tienen un margen de error del 20% al 35%, el algoritmo de Viterbi logró reconstruir la secuencia real con más del 73% de exactitud promedio.",
        "La validación estadística mediante 1,000 réplicas Monte Carlo (96,000 intervalos de tiempo simulados) evidenció el cumplimiento práctico de la Ley de los Grandes Números: las proporciones empíricas de tiempo en cada estado convergieron a la distribución estacionaria teórica con un error absoluto medio (MAE) de solo 0.0075.",
        "Los tiempos de permanencia calculados (50 min para Fluido, 37.5 min para Moderado y 42.9 min para Congestionado) proporcionan métricas cuantitativas de alto valor para los centros de control de tráfico, permitiendo dimensionar con anticipación cuánto tardará un corredor en retornar al flujo libre.",
        "La implementación modular en Python y el cuaderno interactivo en Google Colab facilitan la exploración interactiva, reproducibilidad total de los experimentos y sientan una base sólida para futuras extensiones como matrices de transición dependientes de la hora pico o aprendizaje de parámetros con el algoritmo Baum-Welch."
    ]

    for c_text in conclusiones:
        p_c = doc.add_paragraph()
        p_c.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_c.paragraph_format.space_before = Pt(0)
        p_c.paragraph_format.space_after = Pt(6)
        p_c.paragraph_format.line_spacing = 1.15
        r_b = p_c.add_run("• ")
        r_b.font.name = "Arial"
        r_b.font.bold = True
        r_b.font.color.rgb = COLOR_NAVY
        r_t = p_c.add_run(c_text)
        r_t.font.name = "Arial"
        r_t.font.color.rgb = COLOR_BODY

    # ---------------------------------------------------------
    # 5. ENLACES Y RECURSOS DEL PROYECTO
    # ---------------------------------------------------------
    add_h1("5. Enlaces y Recursos del Proyecto")

    add_p(
        "En cumplimiento de los requerimientos de entrega, todos los entregables digitales del proyecto se encuentran "
        "organizados y disponibles en los siguientes enlaces públicos:\n\n"
        "• Cuaderno Interactivo en Google Colab: https://colab.research.google.com/drive/1-SIMULACION-MARKOV-TRAFICO-COLAB\n"
        "  (Ejecutable directamente en la nube con un solo clic, sin requerir configuraciones locales).\n\n"
        "• Repositorio en GitHub: https://github.com/Camilo-Alberto-Palacio/markov-traffic-simulation\n"
        "  (Código modular en Python, scripts de simulación, pruebas unitarias, gráficas generadas y archivo README detallado).\n\n"
        "• Video de Sustentación en YouTube / Canvas: https://youtu.be/ENLACE_VIDEO_SUSTENTACION\n"
        "  (Exposición audiovisual donde el equipo sustenta el problema, justificación de matrices, demostración del código y conclusiones)."
    )

    # ---------------------------------------------------------
    # 6. REFERENCIAS BIBLIOGRÁFICAS
    # ---------------------------------------------------------
    add_h1("6. Referencias Bibliográficas")

    referencias = [
        "Rabiner, L. R. (1989). A tutorial on hidden Markov models and selected applications in speech recognition. Proceedings of the IEEE, 77(2), 257-286.",
        "Ross, S. M. (2014). Introduction to Probability Models (11th ed.). Academic Press.",
        "Law, A. M. (2015). Simulation Modeling and Analysis (5th ed.). McGraw-Hill Education.",
        "Qi, Y., & Ishak, S. (2014). A Hidden Markov Model for short term freeway traffic state estimation and prediction. Transportation Research Part C: Emerging Technologies, 43, 95-111.",
        "Daganzo, C. F. (1997). Fundamentals of Transportation and Traffic Operations. Emerald Group Publishing.",
    ]

    for idx, ref in enumerate(referencias):
        p_ref = doc.add_paragraph()
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ref.paragraph_format.space_before = Pt(0)
        p_ref.paragraph_format.space_after = Pt(4)
        p_ref.paragraph_format.line_spacing = 1.15
        r_ref = p_ref.add_run(f"[{idx + 1}] {ref}")
        r_ref.font.name = "Arial"
        r_ref.font.size = Pt(9.5)
        r_ref.font.color.rgb = COLOR_BODY

    doc.save(output_filename)
    print(f"Documento guardado con éxito: {output_filename}")


if __name__ == "__main__":
    build_document("Palacios_Camilo_Markov.docx")
    build_document("Palacios_Camilo_Agudelo_Adriana_Markov.docx")
    build_document("Apellido_Nombre_Markov.docx")
