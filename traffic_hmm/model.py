"""
Modelo Oculto de Markov (Hidden Markov Model - HMM) para Tráfico Vehicular.
Actividad Didáctica 2 - Módulo 2: Simulación de Procesos Estocásticos.
Institución Universitaria Digital de Antioquia (IU Digital) - Grupo 25.
"""

from typing import List, Tuple, Dict, Optional, Any
import numpy as np


class TrafficHMM:
    """
    Implementación rigurosa de un Modelo Oculto de Markov (HMM) de tiempo discreto
    aplicado a la dinámica estocástica, inferencia y predicción del tráfico vehicular.

    Definido por la quintupla canónica lambda = (S, V, pi, A, B):
      - S  : Espacio de estados ocultos (Fluido, Moderado, Congestionado).
      - V  : Espacio de observaciones visibles en sensores (Velocidad Alta, Media, Baja).
      - pi : Vector de probabilidades iniciales P(X_0 = s_i).
      - A  : Matriz estocástica de transición A[i, j] = P(X_{t+1} = s_j | X_t = s_i).
      - B  : Matriz estocástica de emisión B[j, k] = P(Y_t = v_k | X_t = s_j).
    """

    def __init__(
        self,
        states: Optional[List[str]] = None,
        observations: Optional[List[str]] = None,
        initial_probs: Optional[np.ndarray] = None,
        transition_matrix: Optional[np.ndarray] = None,
        emission_matrix: Optional[np.ndarray] = None,
        preset: str = "default",
    ):
        if preset == "prompt":
            self.states = states or ["Tráfico Fluido", "Tráfico Moderado", "Tráfico Congestionado"]
            self.observations = observations or ["Velocidad Alta", "Velocidad Media", "Velocidad Baja"]
            if initial_probs is not None:
                self.pi = np.array(initial_probs, dtype=float)
            else:
                self.pi = np.array([0.50, 0.30, 0.20], dtype=float)

            if transition_matrix is not None:
                self.A = np.array(transition_matrix, dtype=float)
            else:
                self.A = np.array([
                    [0.70, 0.25, 0.05],  # Fluido -> [0.7, 0.25, 0.05]
                    [0.30, 0.50, 0.20],  # Moderado -> [0.3, 0.5, 0.2]
                    [0.10, 0.40, 0.50],  # Congestionado -> [0.1, 0.4, 0.5]
                ], dtype=float)

            if emission_matrix is not None:
                self.B = np.array(emission_matrix, dtype=float)
            else:
                self.B = np.array([
                    [0.80, 0.15, 0.05],  # Fluido -> [Alta: 0.8, Media: 0.15, Baja: 0.05]
                    [0.20, 0.60, 0.20],  # Moderado -> [Alta: 0.2, Media: 0.6, Baja: 0.2]
                    [0.05, 0.25, 0.70],  # Congestionado -> [Alta: 0.05, Media: 0.25, Baja: 0.7]
                ], dtype=float)
        else:
            self.states = states or ["Fluido", "Moderado", "Congestionado"]
            self.observations = observations or ["Velocidad Alta", "Velocidad Media", "Velocidad Baja"]

            if initial_probs is not None:
                self.pi = np.array(initial_probs, dtype=float)
            else:
                self.pi = np.array([0.70, 0.20, 0.10], dtype=float)

            if transition_matrix is not None:
                self.A = np.array(transition_matrix, dtype=float)
            else:
                self.A = np.array([
                    [0.70, 0.25, 0.05],  # Desde Fluido
                    [0.20, 0.60, 0.20],  # Desde Moderado
                    [0.05, 0.30, 0.65],  # Desde Congestionado
                ], dtype=float)

            if emission_matrix is not None:
                self.B = np.array(emission_matrix, dtype=float)
            else:
                self.B = np.array([
                    [0.80, 0.15, 0.05],  # Estado real Fluido
                    [0.20, 0.65, 0.15],  # Estado real Moderado
                    [0.05, 0.20, 0.75],  # Estado real Congestionado
                ], dtype=float)

        self.N = len(self.states)
        self.M = len(self.observations)

        self.state_to_idx = {name: i for i, name in enumerate(self.states)}
        self.idx_to_state = {i: name for i, name in enumerate(self.states)}
        self.obs_to_idx = {name: i for i, name in enumerate(self.observations)}
        self.idx_to_obs = {i: name for i, name in enumerate(self.observations)}

        self._validate_matrices()

    @classmethod
    def create_prompt_model(cls) -> "TrafficHMM":
        """Crea una instancia con las especificaciones exactas del prompt de actividad didáctica."""
        return cls(preset="prompt")

    def _validate_matrices(self) -> None:
        """Verifica dimensiones, no negatividad y axiomas estocásticos de Kolmogorov."""
        if len(self.pi) != self.N:
            raise ValueError(f"Vector pi debe tener dimensión {self.N}, recibido {len(self.pi)}")
        if np.any(self.pi < 0) or not np.isclose(np.sum(self.pi), 1.0, atol=1e-4):
            raise ValueError(f"Vector pi debe ser no negativo y sumar 1.0 (suma={np.sum(self.pi)})")

        if self.A.shape != (self.N, self.N):
            raise ValueError(f"Matriz A debe tener forma ({self.N}, {self.N})")
        if np.any(self.A < 0) or not np.allclose(np.sum(self.A, axis=1), 1.0, atol=1e-4):
            raise ValueError("Cada fila de la matriz de transición A debe ser no negativa y sumar 1.0")

        if self.B.shape != (self.N, self.M):
            raise ValueError(f"Matriz B debe tener forma ({self.N}, {self.M})")
        if np.any(self.B < 0) or not np.allclose(np.sum(self.B, axis=1), 1.0, atol=1e-4):
            raise ValueError("Cada fila de la matriz de emisión B debe ser no negativa y sumar 1.0")

    def simulate(self, T: int, seed: Optional[int] = None) -> Tuple[List[int], List[int]]:
        """
        Genera una trayectoria sintética de longitud T mediante simulación Monte Carlo.

        Retorna
        -------
        Tuple[List[int], List[int]]
            (secuencia_estados_ocultos, secuencia_observaciones)
        """
        if T <= 0:
            return [], []

        rng = np.random.default_rng(seed)
        hidden_states = np.zeros(T, dtype=int)
        observations = np.zeros(T, dtype=int)

        hidden_states[0] = rng.choice(self.N, p=self.pi)
        observations[0] = rng.choice(self.M, p=self.B[hidden_states[0]])

        for t in range(1, T):
            prev_state = hidden_states[t - 1]
            curr_state = rng.choice(self.N, p=self.A[prev_state])
            curr_obs = rng.choice(self.M, p=self.B[curr_state])

            hidden_states[t] = curr_state
            observations[t] = curr_obs

        return hidden_states.tolist(), observations.tolist()

    def naive_sensor_decode(self, observations_seq: List[int]) -> List[int]:
        """
        Clasificador puntual sin memoria markoviana (Máxima Verosimilitud por Emisión):
            X_hat_t = argmax_i P(Y_t | X_t = s_i) = argmax_i B[i, Y_t]
        Sirve como línea base (baseline) para cuantificar la ganancia del HMM.
        """
        return [int(np.argmax(self.B[:, obs])) for obs in observations_seq]

    def viterbi(self, observations_seq: List[int]) -> Tuple[List[int], float]:
        """
        Algoritmo de Viterbi en escala logarítmica para hallar la secuencia conjunta
        más probable de estados ocultos X* = argmax_X P(X, Y | lambda).
        """
        T = len(observations_seq)
        if T == 0:
            return [], 0.0

        eps = 1e-12
        log_pi = np.log(np.maximum(self.pi, eps))
        log_A = np.log(np.maximum(self.A, eps))
        log_B = np.log(np.maximum(self.B, eps))

        V = np.zeros((T, self.N))
        backpointer = np.zeros((T, self.N), dtype=int)

        V[0, :] = log_pi + log_B[:, observations_seq[0]]

        for t in range(1, T):
            obs = observations_seq[t]
            for j in range(self.N):
                prob_transitions = V[t - 1, :] + log_A[:, j]
                best_prev = int(np.argmax(prob_transitions))
                V[t, j] = prob_transitions[best_prev] + log_B[j, obs]
                backpointer[t, j] = best_prev

        best_last_state = int(np.argmax(V[T - 1, :]))
        best_log_prob = float(V[T - 1, best_last_state])

        best_path = [0] * T
        best_path[T - 1] = best_last_state
        for t in range(T - 2, -1, -1):
            best_path[t] = int(backpointer[t + 1, best_path[t + 1]])

        return best_path, best_log_prob

    def forward(self, observations_seq: List[int]) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Algoritmo Forward escalado para calcular alpha_hat[t, i] = P(X_t = s_i | Y_{0:t}, lambda)
        y la log-verosimilitud marginal log P(Y | lambda).
        """
        T = len(observations_seq)
        if T == 0:
            return np.empty((0, self.N)), np.empty(0), 0.0

        alpha = np.zeros((T, self.N))
        scales = np.zeros(T)

        alpha[0, :] = self.pi * self.B[:, observations_seq[0]]
        scales[0] = max(float(np.sum(alpha[0, :])), 1e-15)
        alpha[0, :] /= scales[0]

        for t in range(1, T):
            obs = observations_seq[t]
            alpha[t, :] = (alpha[t - 1, :] @ self.A) * self.B[:, obs]
            scales[t] = max(float(np.sum(alpha[t, :])), 1e-15)
            alpha[t, :] /= scales[t]

        log_likelihood = float(np.sum(np.log(scales)))
        return alpha, scales, log_likelihood

    def forward_backward(self, observations_seq: List[int]) -> Tuple[np.ndarray, List[int], float]:
        """
        Algoritmo Forward-Backward (Suavizado Bayesiano) para obtener la distribución
        marginal a posteriori en cada instante:
            gamma[t, i] = P(X_t = s_i | Y_{0:T-1}, lambda)
        y la secuencia que maximiza la probabilidad marginal paso a paso (Posterior Decoding).
        """
        T = len(observations_seq)
        if T == 0:
            return np.empty((0, self.N)), [], 0.0

        alpha, scales, log_likelihood = self.forward(observations_seq)
        beta = np.zeros((T, self.N))
        beta[T - 1, :] = 1.0

        for t in range(T - 2, -1, -1):
            next_obs = observations_seq[t + 1]
            beta[t, :] = self.A @ (self.B[:, next_obs] * beta[t + 1, :])
            beta[t, :] /= scales[t + 1]

        gamma = alpha * beta
        row_sums = np.maximum(np.sum(gamma, axis=1, keepdims=True), 1e-15)
        gamma /= row_sums

        posterior_states = np.argmax(gamma, axis=1).tolist()
        return gamma, posterior_states, log_likelihood

    def compute_stationary_distribution(self) -> np.ndarray:
        """
        Calcula la distribución estacionaria exacta pi* resolviendo:
            (A^T - I) pi*^T = 0, sujeto a sum(pi*) = 1.
        """
        Q = self.A.T - np.eye(self.N)
        Q[-1, :] = 1.0
        b = np.zeros(self.N)
        b[-1] = 1.0

        try:
            stationary = np.linalg.solve(Q, b)
            stationary = np.clip(stationary, 0.0, 1.0)
            stationary /= np.sum(stationary)
            return stationary
        except np.linalg.LinAlgError:
            A_k = np.linalg.matrix_power(self.A, 1000)
            return A_k[0, :]

    def expected_holding_times(self) -> Dict[str, float]:
        """
        Tiempo esperado de permanencia continua (distribución geométrica):
            E[T_i] = 1 / (1 - a_{ii}) pasos de tiempo.
        """
        holding_times = {}
        for i, state in enumerate(self.states):
            p_exit = 1.0 - self.A[i, i]
            holding_times[state] = 1.0 / p_exit if p_exit > 1e-9 else float("inf")
        return holding_times

    def mean_recurrence_times(self) -> Dict[str, float]:
        """
        Tiempo medio de retorno (recurrencia de Kac) a cada estado en régimen estacionario:
            mu_i = 1 / pi*_i pasos de tiempo.
        """
        pi_star = self.compute_stationary_distribution()
        return {
            state: (1.0 / float(pi_star[i]) if pi_star[i] > 1e-9 else float("inf"))
            for i, state in enumerate(self.states)
        }

    def predict_future_distribution(self, initial_dist: np.ndarray, steps: int) -> np.ndarray:
        """Calcula pi_{t+k} = pi_t * A^k (Ecuación de Chapman-Kolmogorov)."""
        A_power = np.linalg.matrix_power(self.A, steps)
        return np.dot(initial_dist, A_power)

    def simulate_with_speeds(
        self,
        T: int = 48,
        seed: Optional[int] = None,
        step_duration_min: int = 30,
        start_hour: int = 0,
    ) -> Tuple[List[int], List[int], List[float], List[str]]:
        """
        Simula T mediciones estocásticas con velocidades continuas en km/h:
          - Alta: 80 - 100 km/h (mu=90, sigma=4)
          - Media: 40 - 80 km/h (mu=60, sigma=7)
          - Baja: 0 - 40 km/h (mu=25, sigma=6)
        Retorna (estados_idx, observaciones_idx, velocidades_kmh, timestamps).
        """
        rng = np.random.default_rng(seed)
        states_idx, obs_idx = self.simulate(T=T, seed=seed)

        speeds = []
        timestamps = []
        for t, obs in enumerate(obs_idx):
            if obs == 0:  # Velocidad Alta (80 - 100 km/h)
                speed = float(np.clip(rng.normal(90.0, 4.0), 80.0, 100.0))
            elif obs == 1:  # Velocidad Media (40 - 80 km/h)
                speed = float(np.clip(rng.normal(60.0, 7.0), 40.0, 79.9))
            else:  # Velocidad Baja (0 - 40 km/h)
                speed = float(np.clip(rng.normal(25.0, 6.0), 5.0, 39.9))
            speeds.append(round(speed, 2))

            total_min = start_hour * 60 + t * step_duration_min
            h = (total_min // 60) % 24
            m = total_min % 60
            timestamps.append(f"{h:02d}:{m:02d}")

        return states_idx, obs_idx, speeds, timestamps

    def predict_next_hours(
        self,
        current_state_idx: int,
        hours: float,
        step_duration_min: int = 30,
    ) -> Dict[str, Any]:
        """
        Predice la distribución de probabilidad y estado más probable para las próximas h horas.
        """
        steps = max(1, int(round(hours * 60.0 / step_duration_min)))
        e_current = np.zeros(self.N, dtype=float)
        e_current[current_state_idx] = 1.0
        prob_dist = self.predict_future_distribution(e_current, steps=steps)
        most_likely_idx = int(np.argmax(prob_dist))
        return {
            "hours_ahead": hours,
            "steps_ahead": steps,
            "probability_distribution": prob_dist,
            "most_likely_state_idx": most_likely_idx,
            "most_likely_state": self.idx_to_state[most_likely_idx],
            "state_probabilities": {
                self.idx_to_state[i]: float(prob_dist[i]) for i in range(self.N)
            },
        }
