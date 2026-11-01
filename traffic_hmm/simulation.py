"""
Módulo de Simulación de Tráfico Vehicular con HMM.
Permite ejecutar simulaciones de escenarios individuales y múltiples réplicas Monte Carlo.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from .model import TrafficHMM


class TrafficSimulation:
    """
    Controlador de simulaciones y análisis experimental para el modelo HMM de tráfico.
    """

    def __init__(self, hmm: Optional[TrafficHMM] = None, step_duration_min: int = 15):
        self.hmm = hmm or TrafficHMM()
        self.step_duration_min = step_duration_min

    def run_single_day_simulation(
        self,
        num_steps: int = 96,
        seed: int = 42,
        start_hour: int = 6
    ) -> Dict[str, Any]:
        """
        Ejecuta una simulación completa de 24 horas (96 intervalos de 15 minutos).

        Parámetros
        ----------
        num_steps : int
            Cantidad de intervalos temporales (por defecto 96 para 24 horas a 15 min por intervalo).
        seed : int
            Semilla pseudoaleatoria para reproducibilidad.
        start_hour : int
            Hora de inicio de la simulación (ej. 6 = 06:00 AM).

        Retorna
        -------
        Dict[str, Any] con:
            - dataframe con la serie de tiempo (hora, estado real, observación, estado viterbi).
            - métricas de exactitud de decodificación.
            - matriz de confusión.
            - proporciones empíricas de estados.
        """
        # 1. Simular estados reales y observaciones de los sensores
        real_states, observations = self.hmm.simulate(T=num_steps, seed=seed)

        # 2. Inferencia con Algoritmo de Viterbi
        viterbi_states, log_prob = self.hmm.viterbi(observations)

        # 3. Construcción del DataFrame temporal
        timestamps = []
        for step in range(num_steps):
            total_minutes = start_hour * 60 + step * self.step_duration_min
            hour = (total_minutes // 60) % 24
            minute = total_minutes % 60
            timestamps.append(f"{hour:02d}:{minute:02d}")

        df = pd.DataFrame({
            "Paso": np.arange(num_steps),
            "Hora": timestamps,
            "Estado_Real_Id": real_states,
            "Estado_Real": [self.hmm.idx_to_state[s] for s in real_states],
            "Observacion_Id": observations,
            "Observacion": [self.hmm.idx_to_obs[o] for o in observations],
            "Estado_Viterbi_Id": viterbi_states,
            "Estado_Viterbi": [self.hmm.idx_to_state[s] for s in viterbi_states],
        })

        # Coincidencia exacta entre estado real y estado inferido
        df["Acierto"] = df["Estado_Real_Id"] == df["Estado_Viterbi_Id"]
        accuracy = float(np.mean(df["Acierto"]))

        # Matriz de confusión (Filas: Real, Columnas: Viterbi)
        N = self.hmm.N
        confusion_matrix = np.zeros((N, N), dtype=int)
        for r, v in zip(real_states, viterbi_states):
            confusion_matrix[r, v] += 1

        # Proporción de tiempo en cada estado
        state_counts = df["Estado_Real"].value_counts(normalize=True).to_dict()
        empirical_proportions = {s: float(state_counts.get(s, 0.0)) for s in self.hmm.states}

        return {
            "dataframe": df,
            "num_steps": num_steps,
            "accuracy": accuracy,
            "confusion_matrix": confusion_matrix,
            "empirical_proportions": empirical_proportions,
            "log_likelihood_viterbi": log_prob,
        }

    def run_monte_carlo_validation(
        self,
        num_replicas: int = 1000,
        steps_per_replica: int = 96,
        seed: int = 100
    ) -> Dict[str, Any]:
        """
        Ejecuta múltiples réplicas Monte Carlo para validar la convergencia asintótica
        hacia la distribución estacionaria y evaluar la robustez estadística de la inferencia.

        Retorna
        -------
        Dict[str, Any] con distribuciones empíricas vs. teóricas y estadísticas de exactitud.
        """
        rng = np.random.default_rng(seed)
        seeds = rng.integers(1, 10_000_000, size=num_replicas)

        state_occurrences = np.zeros(self.hmm.N, dtype=int)
        accuracies = np.zeros(num_replicas, dtype=float)

        for i, s in enumerate(seeds):
            real_states, observations = self.hmm.simulate(T=steps_per_replica, seed=int(s))
            viterbi_states, _ = self.hmm.viterbi(observations)

            # Acumular frecuencias de estados
            for st in real_states:
                state_occurrences[st] += 1

            # Exactitud de decodificación
            acc = np.mean(np.array(real_states) == np.array(viterbi_states))
            accuracies[i] = acc

        total_steps = num_replicas * steps_per_replica
        empirical_dist = state_occurrences / total_steps
        theoretical_dist = self.hmm.compute_stationary_distribution()

        # Error absoluto medio entre empírico y teórico
        mae = float(np.mean(np.abs(empirical_dist - theoretical_dist)))

        return {
            "num_replicas": num_replicas,
            "steps_per_replica": steps_per_replica,
            "total_steps_simulated": total_steps,
            "empirical_stationary": empirical_dist,
            "theoretical_stationary": theoretical_dist,
            "mae_stationary": mae,
            "mean_accuracy": float(np.mean(accuracies)),
            "std_accuracy": float(np.std(accuracies)),
            "min_accuracy": float(np.min(accuracies)),
            "max_accuracy": float(np.max(accuracies)),
        }

    def run_perturbation_scenario(
        self,
        num_steps: int = 96,
        incident_start: int = 32,  # aprox 14:00 si inicio es 06:00
        incident_end: int = 44,    # dura 3 horas = 12 intervalos
        seed: int = 77
    ) -> Dict[str, Any]:
        """
        Simula un escenario de contingencia (ej. accidente de tránsito o lluvia extrema)
        modificando temporalmente la matriz de transición para forzar congestión.
        Demuestra la adaptabilidad del HMM y el tiempo de recuperación de la vía.
        """
        rng = np.random.default_rng(seed)

        # Matriz modificada durante el incidente (alta probabilidad de saltar/permanecer en Congestionado)
        A_incident = np.array([
            [0.20, 0.40, 0.40],
            [0.05, 0.35, 0.60],
            [0.02, 0.18, 0.80],
        ])

        real_states = np.zeros(num_steps, dtype=int)
        observations = np.zeros(num_steps, dtype=int)

        # Estado inicial
        real_states[0] = rng.choice(self.hmm.N, p=self.hmm.pi)
        observations[0] = rng.choice(self.hmm.M, p=self.hmm.B[real_states[0]])

        for t in range(1, num_steps):
            prev = real_states[t - 1]
            if incident_start <= t <= incident_end:
                curr = rng.choice(self.hmm.N, p=A_incident[prev])
            else:
                curr = rng.choice(self.hmm.N, p=self.hmm.A[prev])
            obs = rng.choice(self.hmm.M, p=self.hmm.B[curr])

            real_states[t] = curr
            observations[t] = obs

        # Decodificación mediante Viterbi estándar (el sensor no sabe de antemano que hubo accidente)
        viterbi_states, _ = self.hmm.viterbi(observations.tolist())

        timestamps = [f"{(6*60 + s*15)//60 % 24:02d}:{(6*60 + s*15)%60:02d}" for s in range(num_steps)]

        df = pd.DataFrame({
            "Paso": np.arange(num_steps),
            "Hora": timestamps,
            "Estado_Real": [self.hmm.idx_to_state[s] for s in real_states],
            "Observacion": [self.hmm.idx_to_obs[o] for o in observations],
            "Estado_Viterbi": [self.hmm.idx_to_state[s] for s in viterbi_states],
            "Incidente_Activo": [incident_start <= s <= incident_end for s in range(num_steps)],
        })

        return {
            "dataframe": df,
            "incident_start": incident_start,
            "incident_end": incident_end,
            "accuracy": float(np.mean(real_states == np.array(viterbi_states))),
        }
