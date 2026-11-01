"""
Módulo de Simulación de Tráfico Vehicular con HMM.
Permite ejecutar simulaciones de escenarios individuales, validación Monte Carlo
y evaluación comparativa frente a sensores sin memoria markoviana.
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from .model import TrafficHMM


def _count_transitions(seq: list) -> int:
    """Cuenta el número de cambios de estado entre pasos consecutivos."""
    if len(seq) < 2:
        return 0
    return int(np.sum(np.array(seq[1:]) != np.array(seq[:-1])))


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
        Ejecuta una simulación completa de 24 horas (96 intervalos de 15 minutos),
        comparando el clasificador puntual del sensor, Viterbi y Forward-Backward.
        """
        real_states, observations = self.hmm.simulate(T=num_steps, seed=seed)

        naive_states = self.hmm.naive_sensor_decode(observations)
        viterbi_states, log_prob_viterbi = self.hmm.viterbi(observations)
        gamma, posterior_states, log_likelihood = self.hmm.forward_backward(observations)

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
            "Sensor_Crudo_Id": naive_states,
            "Sensor_Crudo": [self.hmm.idx_to_state[s] for s in naive_states],
            "Estado_Viterbi_Id": viterbi_states,
            "Estado_Viterbi": [self.hmm.idx_to_state[s] for s in viterbi_states],
            "Estado_Posterior_Id": posterior_states,
            "Estado_Posterior": [self.hmm.idx_to_state[s] for s in posterior_states],
            "Prob_Fluido": np.round(gamma[:, 0], 4),
            "Prob_Moderado": np.round(gamma[:, 1], 4),
            "Prob_Congestionado": np.round(gamma[:, 2], 4),
        })

        df["Acierto_Sensor_Crudo"] = df["Estado_Real_Id"] == df["Sensor_Crudo_Id"]
        df["Acierto"] = df["Estado_Real_Id"] == df["Estado_Viterbi_Id"]
        df["Acierto_Posterior"] = df["Estado_Real_Id"] == df["Estado_Posterior_Id"]

        accuracy_naive = float(np.mean(df["Acierto_Sensor_Crudo"]))
        accuracy_viterbi = float(np.mean(df["Acierto"]))
        accuracy_posterior = float(np.mean(df["Acierto_Posterior"]))

        N = self.hmm.N
        confusion_matrix = np.zeros((N, N), dtype=int)
        for r, v in zip(real_states, viterbi_states):
            confusion_matrix[r, v] += 1

        state_counts = df["Estado_Real"].value_counts(normalize=True).to_dict()
        empirical_proportions = {s: float(state_counts.get(s, 0.0)) for s in self.hmm.states}

        return {
            "dataframe": df,
            "gamma": gamma,
            "num_steps": num_steps,
            "accuracy_naive": accuracy_naive,
            "accuracy": accuracy_viterbi,
            "accuracy_posterior": accuracy_posterior,
            "transitions_real": _count_transitions(real_states),
            "transitions_naive": _count_transitions(naive_states),
            "transitions_viterbi": _count_transitions(viterbi_states),
            "confusion_matrix": confusion_matrix,
            "empirical_proportions": empirical_proportions,
            "log_likelihood_viterbi": log_prob_viterbi,
            "log_likelihood_marginal": log_likelihood,
        }

    def run_monte_carlo_validation(
        self,
        num_replicas: int = 1000,
        steps_per_replica: int = 96,
        seed: int = 100
    ) -> Dict[str, Any]:
        """
        Ejecuta múltiples réplicas Monte Carlo para validar la convergencia asintótica
        hacia la distribución estacionaria y cuantificar la superioridad del HMM frente
        a la lectura puntual sin memoria.
        """
        rng = np.random.default_rng(seed)
        seeds = rng.integers(1, 10_000_000, size=num_replicas)

        state_occurrences = np.zeros(self.hmm.N, dtype=int)
        accuracies_viterbi = np.zeros(num_replicas, dtype=float)
        accuracies_naive = np.zeros(num_replicas, dtype=float)
        accuracies_posterior = np.zeros(num_replicas, dtype=float)
        switches_real = np.zeros(num_replicas, dtype=int)
        switches_naive = np.zeros(num_replicas, dtype=int)
        switches_viterbi = np.zeros(num_replicas, dtype=int)

        for i, s in enumerate(seeds):
            real_states, observations = self.hmm.simulate(T=steps_per_replica, seed=int(s))
            naive_states = self.hmm.naive_sensor_decode(observations)
            viterbi_states, _ = self.hmm.viterbi(observations)
            _, posterior_states, _ = self.hmm.forward_backward(observations)

            real_arr = np.array(real_states)
            for st in range(self.hmm.N):
                state_occurrences[st] += int(np.sum(real_arr == st))

            accuracies_naive[i] = float(np.mean(real_arr == np.array(naive_states)))
            accuracies_viterbi[i] = float(np.mean(real_arr == np.array(viterbi_states)))
            accuracies_posterior[i] = float(np.mean(real_arr == np.array(posterior_states)))

            switches_real[i] = _count_transitions(real_states)
            switches_naive[i] = _count_transitions(naive_states)
            switches_viterbi[i] = _count_transitions(viterbi_states)

        total_steps = num_replicas * steps_per_replica
        empirical_dist = state_occurrences / total_steps
        theoretical_dist = self.hmm.compute_stationary_distribution()
        mae = float(np.mean(np.abs(empirical_dist - theoretical_dist)))

        return {
            "num_replicas": num_replicas,
            "steps_per_replica": steps_per_replica,
            "total_steps_simulated": total_steps,
            "empirical_stationary": empirical_dist,
            "theoretical_stationary": theoretical_dist,
            "mae_stationary": mae,
            "accuracies": accuracies_viterbi,
            "accuracies_naive": accuracies_naive,
            "accuracies_posterior": accuracies_posterior,
            "mean_accuracy": float(np.mean(accuracies_viterbi)),
            "std_accuracy": float(np.std(accuracies_viterbi)),
            "min_accuracy": float(np.min(accuracies_viterbi)),
            "max_accuracy": float(np.max(accuracies_viterbi)),
            "mean_accuracy_naive": float(np.mean(accuracies_naive)),
            "std_accuracy_naive": float(np.std(accuracies_naive)),
            "mean_accuracy_posterior": float(np.mean(accuracies_posterior)),
            "std_accuracy_posterior": float(np.std(accuracies_posterior)),
            "mean_switches_real": float(np.mean(switches_real)),
            "mean_switches_naive": float(np.mean(switches_naive)),
            "mean_switches_viterbi": float(np.mean(switches_viterbi)),
        }

    def run_perturbation_scenario(
        self,
        num_steps: int = 96,
        incident_start: int = 32,
        incident_end: int = 44,
        seed: int = 77
    ) -> Dict[str, Any]:
        """
        Simula un escenario de contingencia (accidente vial o lluvia torrencial entre 14:00 y 17:00)
        modificando temporalmente la matriz de transición para forzar congestión severa.
        """
        rng = np.random.default_rng(seed)

        A_incident = np.array([
            [0.20, 0.40, 0.40],
            [0.05, 0.35, 0.60],
            [0.02, 0.18, 0.80],
        ])

        real_states = np.zeros(num_steps, dtype=int)
        observations = np.zeros(num_steps, dtype=int)

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

        viterbi_states, _ = self.hmm.viterbi(observations.tolist())
        gamma, _, _ = self.hmm.forward_backward(observations.tolist())

        timestamps = [f"{(6*60 + s*15)//60 % 24:02d}:{(6*60 + s*15)%60:02d}" for s in range(num_steps)]

        df = pd.DataFrame({
            "Paso": np.arange(num_steps),
            "Hora": timestamps,
            "Estado_Real_Id": real_states,
            "Estado_Real": [self.hmm.idx_to_state[s] for s in real_states],
            "Observacion_Id": observations,
            "Observacion": [self.hmm.idx_to_obs[o] for o in observations],
            "Estado_Viterbi_Id": viterbi_states,
            "Estado_Viterbi": [self.hmm.idx_to_state[s] for s in viterbi_states],
            "Prob_Congestionado": np.round(gamma[:, 2], 4),
            "Incidente_Activo": [incident_start <= s <= incident_end for s in range(num_steps)],
        })

        return {
            "dataframe": df,
            "gamma": gamma,
            "incident_start": incident_start,
            "incident_end": incident_end,
            "accuracy": float(np.mean(real_states == np.array(viterbi_states))),
        }
