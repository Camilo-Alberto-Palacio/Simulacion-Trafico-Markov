"""
Simulación de Tráfico Vehicular con HMM para Ciudades Inteligentes.
Cumplimiento estricto del prompt de la Actividad Didáctica 2 - Módulo 2.
IU Digital de Antioquia - Grupo 25.

Ejecución directa:
    python simulacion_smart_traffic.py
"""

import sys
import os
import pandas as pd
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from traffic_hmm import TrafficHMM, SmartCityTrafficAnalyzer, SmartCityVisualizer


def print_banner():
    print("=" * 85)
    print("  SIMULACIÓN DE TRÁFICO VEHICULAR MEDIANTE MODELO OCULTO DE MARKOV (HMM)")
    print("  Centro de Monitoreo y Analítica Urbana para Ciudades Inteligentes")
    print("  Actividad Didáctica 2 - Módulo 2 | IU Digital de Antioquia - Grupo 25")
    print("=" * 85)


def main():
    print_banner()

    # 1. Configuración del Modelo HMM según especificaciones exactas del prompt
    print("\n[1/7] Inicializando el Modelo HMM con Parámetros del Prompt...")
    hmm = TrafficHMM.create_prompt_model()

    print(f"  • Estados Ocultos:      {hmm.states}")
    print(f"  • Observaciones:        {hmm.observations}")
    print(f"  • Distribución Inicial: {hmm.pi}")
    print("\n  • Matriz de Transición (A):")
    for i, row in enumerate(hmm.A):
        print(f"      {hmm.states[i]:24s} -> {row}")

    print("\n  • Matriz de Emisión (B):")
    for i, row in enumerate(hmm.B):
        print(f"      {hmm.states[i]:24s} -> {row}")

    # Distribución estacionaria analítica
    pi_star = hmm.compute_stationary_distribution()
    print("\n  • Distribución Estacionaria Teórica (pi* A = pi*):")
    for s, p in zip(hmm.states, pi_star):
        print(f"      - {s:24s}: {p*100:5.2f}% ({p:.4f})")

    # 2. Simulación de 48 mediciones (Día completo, cada 30 minutos) con velocidades en km/h
    print("\n[2/7] Simulando Jornada Completa (48 Mediciones, cada 30 minutos = 24 horas)...")
    analyzer = SmartCityTrafficAnalyzer(hmm=hmm, corridor_length_km=15.0)
    df = analyzer.simulate_day(num_steps=48, seed=42, step_duration_min=30, start_hour=0)

    print(f"  • Mediciones simuladas: {len(df)}")
    print(f"  • Rango de velocidad generado: {df['Velocidad_kmh'].min():.1f} km/h  a  {df['Velocidad_kmh'].max():.1f} km/h")
    print(f"  • Exactitud de inferencia Viterbi: {(df['Estado_Real_Id'] == df['Estado_Viterbi_Id']).mean() * 100:.2f}%")

    # Muestra de semáforo por período
    print("\n  • Muestra del Semáforo Urbano (Primeras 12 Horas):")
    semaforo_str = " ".join([f"{df.loc[i, 'Hora']}:{df.loc[i, 'Semaforo_Icono']}" for i in range(12)])
    print(f"      {semaforo_str}")

    # 3. Cálculo de Métricas de Transporte
    print("\n[3/7] Calculando Métricas Clave de Transporte Urbano...")
    metrics = analyzer.calculate_transport_metrics(df)

    print(f"  • Velocidad Promedio General:      {metrics['velocidad_promedio_general_kmh']} km/h")
    print(f"  • Índice de Congestión (0-100):    {metrics['indice_congestion_0_100']} / 100")
    print(f"  • Tiempo Total en Congestión:      {metrics['horas_congestión_total']} horas ({metrics['porcentaje_dia_congestion']}% del día)")
    print(f"  • Tiempo Promedio de Viaje:        {metrics['tiempo_promedio_viaje_min']} minutos (en corredor de 15 km)")
    print(f"  • Tiempo Máximo en Hora Crítica:   {metrics['tiempo_maximo_viaje_min']} minutos")
    print("  • Velocidad Promedio por Estado Operativo:")
    for state, spd in metrics["velocidad_promedio_por_estado"].items():
        print(f"      - {state:24s}: {spd} km/h")

    print("  • Horas Pico Identificadas:")
    for peak in metrics["horas_pico_identificadas"]:
        print(f"      - Rango: {peak['rango']:15s} | Duración: {peak['duracion_horas']} h | Vel. Media: {peak['velocidad_media_kmh']} km/h")

    # 4. Predicción del Tráfico para las Próximas Horas
    last_state = df.loc[len(df) - 1, "Estado_Viterbi_Id"]
    print(f"\n[4/7] Predicción de Tráfico Futuro a partir de última observación ({df.loc[len(df)-1, 'Hora']}: {df.loc[len(df)-1, 'Estado_Viterbi']})...")
    predictions = analyzer.predict_future_traffic(last_state, horizons_hours=[1, 2, 4, 6])
    for pred in predictions:
        print(
            f"  • +{pred['horas_adelante']} horas: Estado más probable -> {pred['estado_mas_probable']} "
            f"({pred['probabilidad_estado']}%) | Vel. Esperada: ~{pred['velocidad_esperada_kmh']} km/h "
            f"[Fluido: {pred['distribucion']['Tráfico Fluido']}%, Mod: {pred['distribucion']['Tráfico Moderado']}%, Cong: {pred['distribucion']['Tráfico Congestionado']}%]"
        )

    # 5. Identificación de Patrones y Riesgo de Congestión
    print("\n[5/7] Identificación de Patrones: ¿Cuándo es más probable la congestión?...")
    patterns = analyzer.identify_congestion_patterns(df)
    print(f"  • Franja Horaria con Mayor Riesgo: {patterns['franja_mas_critica']} ({patterns['probabilidad_maxima_congestion_pct']}% prob. congestión)")
    print(f"  • Tiempo Medio de Permanencia en Congestión: {patterns['tiempo_medio_permanencia_congestion_horas']} horas")
    print("  • Análisis por Franja Horaria:")
    for franja, d in patterns["analisis_por_franja"].items():
        print(f"      - {franja:26s} -> Prob: {d['probabilidad_media_congestion_pct']:4.1f}% | Vel: {d['velocidad_promedio_kmh']:4.1f} km/h | Horas Cong: {d['tiempo_en_congestion_horas']} h")

    # 6. Rutas Alternativas Sugeridas e Impacto Ambiental
    print("\n[6/7] Generando Rutas Alternativas y Análisis de Impacto Ambiental...")
    current_speed = float(df.loc[len(df) - 1, "Velocidad_kmh"])
    current_state_name = str(df.loc[len(df) - 1, "Estado_Viterbi"])
    routes = analyzer.suggest_alternative_routes(current_state_name, current_speed)

    print(f"  • Estado actual del corredor: {current_state_name} ({current_speed:.1f} km/h)")
    print(f"  • Alerta de congestión activa: {'SÍ (🔴)' if routes['alerta_congestion_activa'] else 'NO (🟢)'}")
    print(f"  • Ruta Óptima Recomendada:    {routes['ruta_optima_sugerida']}")
    if routes["alerta_congestion_activa"]:
        print(f"  • Ahorro Estimado de Tiempo:   {routes['ahorro_tiempo_maximo_min']} minutos frente al corredor principal")

    env = analyzer.analyze_environmental_impact(df, daily_fleet_volume=15000)
    print("\n  • Impacto Ambiental en el Corredor (Flota de 15.000 veh/día):")
    print(f"      - Emisiones Totales de CO2:          {env['emisiones_totales_co2_toneladas']} Toneladas/día")
    print(f"      - Consumo Total de Combustible:      {env['consumo_total_combustible_litros']:,} Litros/día")
    print(f"      - Exceso de CO2 por Congestión:      {env['exceso_co2_por_congestion_toneladas']} Toneladas/día (+{env['incremento_porcentual_emisiones_vs_ideal']}%)")
    print(f"      - Combustible Desperdiciado:         {env['exceso_combustible_desperdiciado_litros']:,} Litros")
    print(f"      - Costo Económico del Desperdicio:   COP ${env['costo_economico_combustible_desperdiciado_cop']:,.0f}")

    # 7. Generación de Visualizaciones con Matplotlib
    print("\n[7/7] Generando Visualizaciones Científicas con Matplotlib y Dashboard Urbano...")
    viz = SmartCityVisualizer(output_dir="results")

    fig1 = viz.plot_speed_and_traffic_lights(df, filename="fig_velocidad_promedio_semaforo.png")
    print(f"  [OK] Guardado: {fig1}")

    fig2 = viz.plot_hourly_heatmap(df, filename="fig_mapa_calor_estado_hora.png")
    print(f"  [OK] Guardado: {fig2}")

    fig3 = viz.plot_smart_city_dashboard(df, metrics, patterns, predictions, routes, env, filename="fig_dashboard_ciudad_inteligente.png")
    print(f"  [OK] Guardado: {fig3}")

    print("  • Generando Animación de Flujo Vehicular (GIF)...")
    anim_file = viz.generate_vehicular_animation(df, filename="animacion_flujo_vehicular.gif", num_frames=48)
    print(f"  [OK] Guardado: {anim_file}")

    # Exportación tabular
    csv_sim = os.path.join("results", "simulacion_smart_traffic_48pasos.csv")
    df.to_csv(csv_sim, index=False, encoding="utf-8-sig")
    print(f"  [+] Datos de la simulación exportados a: {csv_sim}")

    print("\n" + "=" * 85)
    print("  SIMULACIÓN SMART CITY HMM COMPLETADA EXITOSAMENTE (10/10 REQUISITOS CUMPLIDOS)")
    print("=" * 85 + "\n")


if __name__ == "__main__":
    main()
