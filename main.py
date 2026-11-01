"""
Script Principal de Ejecución: Simulación y Predicción de Tráfico Vehicular con HMM.
Actividad Didáctica 2 - Módulo 2: Simulación de Procesos Estocásticos.

Ejecución:
    python main.py
"""

import os
import sys
import numpy as np
import pandas as pd

# Configurar stdout para evitar errores de codificación en consolas Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from traffic_hmm.model import TrafficHMM
from traffic_hmm.simulation import TrafficSimulation
from traffic_hmm.visualizations import TrafficVisualizer


def print_banner():
    print("=" * 78)
    print("  SIMULACIÓN ESTOCÁSTICA DE TRÁFICO VEHICULAR MEDIANTE MODELO OCULTO DE MARKOV  ")
    print("  Actividad Didáctica 2 - Módulo 2 | Modelo Oculto de Markov (HMM)")
    print("=" * 78)


def main():
    print_banner()

    # 1. Instanciación del Modelo HMM
    print("\n[1/5] Inicializando el Modelo Oculto de Markov (HMM)...")
    hmm = TrafficHMM()

    print(f"  • Estados Ocultos (S): {hmm.states}")
    print(f"  • Observaciones Visibles (V): {hmm.observations}")
    print(f"  • Vector Inicial (pi): {hmm.pi}")
    print("\n  • Matriz de Transición de Estados (A):")
    for i, row in enumerate(hmm.A):
        print(f"      {hmm.states[i]:14s} -> {row}")

    print("\n  • Matriz de Emisión de Sensores (B):")
    for i, row in enumerate(hmm.B):
        print(f"      {hmm.states[i]:14s} -> {row}")

    # 2. Análisis Analítico del Proceso de Markov
    print("\n[2/5] Calculando Propiedades Analíticas Estacionarias...")
    pi_star = hmm.compute_stationary_distribution()
    holding_times = hmm.expected_holding_times()

    print("  • Distribución Estacionaria Teórica (pi*):")
    for state, p in zip(hmm.states, pi_star):
        print(f"      - {state:14s}: {p*100:6.2f}% ({p:.4f})")

    print("  • Tiempo Promedio de Permanencia por Estado (Holding Time):")
    for state, steps in holding_times.items():
        minutes = steps * 15
        print(f"      - {state:14s}: {steps:.2f} pasos (~{minutes:.1f} minutos)")

    # 3. Simulación de una Jornada Completa (24 Horas)
    print("\n[3/5] Simulando Jornada de 24 Horas (96 Intervalos de 15 Minutos)...")
    sim = TrafficSimulation(hmm=hmm, step_duration_min=15)
    res_24h = sim.run_single_day_simulation(num_steps=96, seed=42, start_hour=6)

    df_24h = res_24h["dataframe"]
    accuracy = res_24h["accuracy"]
    cm = res_24h["confusion_matrix"]

    print(f"  • Exactitud de Decodificación (Viterbi vs. Real): {accuracy * 100:.2f}%")
    print(f"  • Distribución Empírica de la Jornada:")
    for state, prop in res_24h["empirical_proportions"].items():
        print(f"      - {state:14s}: {prop*100:6.2f}%")

    print("\n  • Matriz de Confusión (Filas: Real, Columnas: Viterbi):")
    print("      " + " ".join([f"{s:>12s}" for s in hmm.states]))
    for i, row in enumerate(cm):
        print(f"      {hmm.states[i]:12s} " + " ".join([f"{val:12d}" for val in row]))

    # Exportar datos a CSV
    os.makedirs("results", exist_ok=True)
    csv_path_24h = os.path.join("results", "simulacion_jornada_24h.csv")
    df_24h.to_csv(csv_path_24h, index=False, encoding="utf-8-sig")
    print(f"  [+] Datos de la jornada exportados a: {csv_path_24h}")

    # 4. Validación Monte Carlo (1,000 Réplicas)
    print("\n[4/5] Ejecutando Validación Monte Carlo (1,000 Réplicas = 96,000 Intervalos)...")
    mc_res = sim.run_monte_carlo_validation(num_replicas=1000, steps_per_replica=96, seed=100)

    print("  • Comparación Teórica vs. Empírica (Ley de los Grandes Números):")
    for s_idx, state in enumerate(hmm.states):
        theo_p = mc_res["theoretical_stationary"][s_idx]
        emp_p = mc_res["empirical_stationary"][s_idx]
        diff = abs(theo_p - emp_p)
        print(f"      - {state:14s} | Teórico: {theo_p*100:5.2f}% | Empírico: {emp_p*100:5.2f}% | Error Absoluto: {diff:.5f}")

    print(f"  • Error Absoluto Medio (MAE) Global: {mc_res['mae_stationary']:.6f}")
    print(f"  • Desempeño Promedio de Viterbi: {mc_res['mean_accuracy']*100:.2f}% (±{mc_res['std_accuracy']*100:.2f}%)")

    # Escenario de Incidente
    print("\n  • Simulando Escenario con Incidente Vial (Perturbación)...")
    incident_res = sim.run_perturbation_scenario(num_steps=96, incident_start=32, incident_end=44, seed=77)
    print(f"      - Exactitud de Inferencia durante contingencia: {incident_res['accuracy']*100:.2f}%")

    # 5. Generación de Gráficos de Alta Resolución
    print("\n[5/5] Generando Figuras Científicas en Alta Resolución (300 DPI)...")
    viz = TrafficVisualizer(output_dir="results")

    f1 = viz.plot_matrices(hmm, filename="fig1_matrices_transicion_emision.png")
    print(f"  [OK] Guardada: {f1}")

    f2 = viz.plot_single_day_timeline(res_24h, filename="fig2_simulacion_jornada_24h.png")
    print(f"  [OK] Guardada: {f2}")

    f3 = viz.plot_stationary_convergence(hmm, steps=15, filename="fig3_convergencia_distribucion_estacionaria.png")
    print(f"  [OK] Guardada: {f3}")

    f4 = viz.plot_monte_carlo_comparison(mc_res, hmm.states, filename="fig4_validacion_monte_carlo.png")
    print(f"  [OK] Guardada: {f4}")

    f5 = viz.plot_incident_scenario(incident_res, filename="fig5_escenario_incidente_recuperacion.png")
    print(f"  [OK] Guardada: {f5}")

    f6 = viz.plot_confusion_matrix(cm, hmm.states, filename="fig6_matriz_confusion_viterbi.png")
    print(f"  [OK] Guardada: {f6}")

    # Guardar resumen en CSV
    summary_df = pd.DataFrame({
        "Estado": hmm.states,
        "Prob_Inicial": hmm.pi,
        "Distribucion_Estacionaria_Teorica": mc_res["theoretical_stationary"],
        "Distribucion_Empirica_MonteCarlo": mc_res["empirical_stationary"],
        "Tiempo_Permanencia_Pasos": [holding_times[s] for s in hmm.states],
        "Tiempo_Permanencia_Minutos": [holding_times[s] * 15 for s in hmm.states],
    })
    summary_csv = os.path.join("results", "resumen_modelo_markov.csv")
    summary_df.to_csv(summary_csv, index=False, encoding="utf-8-sig")
    print(f"  [+] Resumen estadístico exportado a: {summary_csv}")

    print("\n" + "=" * 78)
    print("  SIMULACIÓN COMPLETADA CON ÉXITO")
    print("  Todos los gráficos y datos se encuentran en el directorio: ./results/")
    print("=" * 78 + "\n")


if __name__ == "__main__":
    main()
