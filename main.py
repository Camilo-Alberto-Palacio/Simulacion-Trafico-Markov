"""
Script Principal de Ejecución: Simulación y Predicción de Tráfico Vehicular con HMM.
Actividad Didáctica 2 - Módulo 2: Simulación de Procesos Estocásticos.
Institución Universitaria Digital de Antioquia (IU Digital) - Grupo 25.

Ejecución:
    python main.py
"""

import os
import sys
import numpy as np
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from traffic_hmm.model import TrafficHMM
from traffic_hmm.simulation import TrafficSimulation
from traffic_hmm.visualizations import TrafficVisualizer


def print_banner():
    print("=" * 80)
    print("  SIMULACIÓN ESTOCÁSTICA DE TRÁFICO VEHICULAR MEDIANTE MODELO OCULTO DE MARKOV  ")
    print("  Actividad Didáctica 2 - Módulo 2 | IU Digital de Antioquia - Grupo 25")
    print("=" * 80)


def main():
    print_banner()

    # 1. Instanciación del Modelo HMM
    print("\n[1/5] Inicializando el Modelo Oculto de Markov (HMM)...")
    hmm = TrafficHMM()

    print(f"  • Estados Ocultos (S):        {hmm.states}")
    print(f"  • Observaciones Visibles (V): {hmm.observations}")
    print(f"  • Vector Inicial (pi):        {hmm.pi}")
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
    recurrence_times = hmm.mean_recurrence_times()

    print("  • Distribución Estacionaria Teórica (pi*):")
    for state, p in zip(hmm.states, pi_star):
        print(f"      - {state:14s}: {p*100:6.2f}% ({p:.4f})")

    print("  • Tiempo Promedio de Permanencia Continua (Holding Time):")
    for state, steps in holding_times.items():
        print(f"      - {state:14s}: {steps:.2f} pasos (~{steps*15:.1f} minutos)")

    print("  • Tiempo Medio de Recurrencia (Retorno de Kac 1/pi*):")
    for state, steps in recurrence_times.items():
        print(f"      - {state:14s}: {steps:.2f} pasos (~{steps*15:.1f} minutos)")

    # 3. Simulación de una Jornada Completa (24 Horas)
    print("\n[3/5] Simulando Jornada de 24 Horas (96 Intervalos de 15 Minutos)...")
    sim = TrafficSimulation(hmm=hmm, step_duration_min=15)
    res_24h = sim.run_single_day_simulation(num_steps=96, seed=42, start_hour=6)

    df_24h = res_24h["dataframe"]
    cm = res_24h["confusion_matrix"]

    print(f"  • Exactitud Sensor Crudo (Sin Memoria):     {res_24h['accuracy_naive']*100:6.2f}%")
    print(f"  • Exactitud Algoritmo de Viterbi (HMM):     {res_24h['accuracy']*100:6.2f}%")
    print(f"  • Exactitud Suavizado Forward-Backward:     {res_24h['accuracy_posterior']*100:6.2f}%")
    print(f"  • Cambios de Estado (Real / Sensor / HMM):  {res_24h['transitions_real']} / {res_24h['transitions_naive']} / {res_24h['transitions_viterbi']}")

    print("\n  • Matriz de Confusión Viterbi (Filas: Real, Columnas: Inferido):")
    print("      " + " ".join([f"{s:>14s}" for s in hmm.states]))
    for i, row in enumerate(cm):
        print(f"      {hmm.states[i]:14s} " + " ".join([f"{val:14d}" for val in row]))

    os.makedirs("results", exist_ok=True)
    csv_path_24h = os.path.join("results", "simulacion_jornada_24h.csv")
    df_24h.to_csv(csv_path_24h, index=False, encoding="utf-8-sig")
    print(f"  [+] Serie temporal completa exportada a: {csv_path_24h}")

    # 4. Validación Monte Carlo (1,000 Réplicas)
    print("\n[4/5] Ejecutando Validación Monte Carlo (1,000 Réplicas = 96,000 Intervalos)...")
    mc_res = sim.run_monte_carlo_validation(num_replicas=1000, steps_per_replica=96, seed=100)

    print("  • Convergencia a la Distribución Estacionaria (Ley de los Grandes Números):")
    for s_idx, state in enumerate(hmm.states):
        theo_p = mc_res["theoretical_stationary"][s_idx]
        emp_p = mc_res["empirical_stationary"][s_idx]
        diff = abs(theo_p - emp_p)
        print(f"      - {state:14s} | Teórico: {theo_p*100:5.2f}% | Empírico: {emp_p*100:5.2f}% | Error Abs: {diff:.5f}")

    print(f"  • Error Absoluto Medio (MAE) Estacionario:  {mc_res['mae_stationary']:.6f}")
    print(f"  • Exactitud Media Sensor Crudo (Baseline):  {mc_res['mean_accuracy_naive']*100:.2f}% (±{mc_res['std_accuracy_naive']*100:.2f}%)")
    print(f"  • Exactitud Media Viterbi (Secuencia MAP):  {mc_res['mean_accuracy']*100:.2f}% (±{mc_res['std_accuracy']*100:.2f}%)")
    print(f"  • Exactitud Media Forward-Backward (Gamma): {mc_res['mean_accuracy_posterior']*100:.2f}% (±{mc_res['std_accuracy_posterior']*100:.2f}%)")
    print(f"  • Conmutaciones medias por día (Real / Sensor / Viterbi): "
          f"{mc_res['mean_switches_real']:.1f} / {mc_res['mean_switches_naive']:.1f} / {mc_res['mean_switches_viterbi']:.1f}")

    print("\n  • Simulando Escenario con Incidente Vial (Perturbación 14:00 - 17:00)...")
    incident_res = sim.run_perturbation_scenario(num_steps=96, incident_start=32, incident_end=44, seed=77)
    print(f"      - Exactitud de Inferencia durante contingencia: {incident_res['accuracy']*100:.2f}%")

    # 5. Generación de Gráficos de Alta Resolución
    print("\n[5/5] Generando 7 Figuras Científicas en Alta Resolución (300 DPI)...")
    viz = TrafficVisualizer(output_dir="results")

    figs = [
        viz.plot_hmm_architecture(hmm, filename="fig0_diagrama_estructura_hmm.png"),
        viz.plot_matrices(hmm, filename="fig1_matrices_transicion_emision.png"),
        viz.plot_single_day_timeline(res_24h, filename="fig2_simulacion_jornada_24h.png"),
        viz.plot_stationary_convergence(hmm, steps=15, filename="fig3_convergencia_distribucion_estacionaria.png"),
        viz.plot_monte_carlo_comparison(mc_res, hmm.states, filename="fig4_validacion_monte_carlo.png"),
        viz.plot_incident_scenario(incident_res, filename="fig5_escenario_incidente_recuperacion.png"),
        viz.plot_confusion_matrix(cm, hmm.states, filename="fig6_matriz_confusion_viterbi.png"),
    ]
    for fp in figs:
        print(f"  [OK] Guardada: {fp}")

    summary_df = pd.DataFrame({
        "Estado": hmm.states,
        "Prob_Inicial": hmm.pi,
        "Distribucion_Estacionaria_Teorica": np.round(mc_res["theoretical_stationary"], 5),
        "Distribucion_Empirica_MonteCarlo": np.round(mc_res["empirical_stationary"], 5),
        "Tiempo_Permanencia_Pasos": [round(holding_times[s], 3) for s in hmm.states],
        "Tiempo_Permanencia_Minutos": [round(holding_times[s] * 15, 2) for s in hmm.states],
        "Tiempo_Recurrencia_Minutos": [round(recurrence_times[s] * 15, 2) for s in hmm.states],
    })
    summary_csv = os.path.join("results", "resumen_modelo_markov.csv")
    summary_df.to_csv(summary_csv, index=False, encoding="utf-8-sig")
    print(f"  [+] Resumen estadístico exportado a: {summary_csv}")

    print("\n" + "=" * 80)
    print("  SIMULACIÓN COMPLETADA CON ÉXITO (0 ADVERTENCIAS, 7 FIGURAS GENERADAS)")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
