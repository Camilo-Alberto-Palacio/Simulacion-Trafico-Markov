"""
Modelo Oculto de Markov (Hidden Markov Model - HMM) para Tráfico Vehicular.
Actividad Didáctica 2 - Módulo 2: Simulación de Procesos Estocásticos.
"""

from typing import List, Tuple, Dict, Optional
import numpy as np


class TrafficHMM:
    """
    Implementación del Modelo Oculto de Markov (HMM) aplicado a la
    dinámica estocástica y predicción del tráfico vehicular.

    Parámetros
    ----------
    states : List[str]
        Nombres de los estados ocultos (e.g., ['Fluido', 'Moderado', 'Congestionado']).
    observations : List[str]
        Nombres de las observaciones observables (e.g., ['Velocidad Alta', 'Velocidad Media', 'Velocidad Baja']).
    initial_probs : np.ndarray
        Vector pi de probabilidades iniciales (dimension N).
    transition_matrix : np.ndarray
        Matriz A de transición de estados de tamano (N x N), donde A[i, j] = P(X_{t+1} = s_j | X_t = s_i).
    emission_matrix : np.ndarray
        Matriz B de emisión de observaciones de tamano (N x M), donde B[j, k] = P(Y_t = v_k | X_t = s_j).
    """

    def __init__(
        self,
        states: Optional[List[str]] = None,
        observations: Optional[List[str]] = None,
        initial_probs: Optional[np.ndarray] = None,
        transition_matrix: Optional[np.ndarray] = None,
        emission_matrix: Optional[np.ndarray] = None,
    ):
        # 1. Definición de espacios por defecto orientados a Tráfico Vehicular
        self.states = states or ["Fluido", "Moderado", "Congestionado"]
        self.observations = observations or ["Velocidad Alta", "Velocidad Media", "Velocidad Baja"]

        self.N = len(self.states)        # Número de estados ocultos
        self.M = len(self.observations)  # Número de tipos de observaciones

        # Mapeos de nombres a índices para acceso rápido
        self.state_to_idx = {name: i for i, name in enumerate(self.states)}
        self.idx_to_state = {i: name for i, name in enumerate(self.states)}
        self.obs_to_idx = {name: i for i, name in enumerate(self.observations)}
        self.idx_to_obs = {i: name for i, name in enumerate(self.observations)}

        # 2. Probabilidades iniciales pi
        # Representa el estado inicial del corredor vial (ej. inicio de jornada 06:00 AM)
        if initial_probs is not None:
            self.pi = np.array(initial_probs, dtype=float)
        else:
            self.pi = np.array([0.70, 0.20, 0.10], dtype=float)

        # 3. Matriz de Transición de Estados A (N x N)
        # Fila i: estado actual, Columna j: estado siguiente
        if transition_matrix is not None:
            self.A = np.array(transition_matrix, dtype=float)
        else:
            self.A = np.array([
                [0.70, 0.25, 0.05],  # Desde Fluido
                [0.20, 0.60, 0.20],  # Desde Moderado
                [0.05, 0.30, 0.65],  # Desde Congestionado
            ], dtype=float)

        # 4. Matriz de Emisión B (N x M)
        # Fila j: estado real del tráfico, Columna k: medición del sensor
        if emission_matrix is not None:
            self.B = np.array(emission_matrix, dtype=float)
        else:
            self.B = np.array([
                [0.80, 0.15, 0.05],  # Si el tráfico es Fluido
                [0.20, 0.65, 0.15],  # Si el tráfico es Moderado
                [0.05, 0.20, 0.75],  # Si el tráfico es Congestionado
            ], dtype=float)

        self._validate_matrices()

    def _validate_matrices(self) -> None:
        """Verifica que las dimensiones y propiedades de probabilidad estocástica sean válidas."""
        if len(self.pi) != self.N:
            raise ValueError(f"Vector pi debe tener dimensión {self.N}, tiene {len(self.pi)}")
        if not np.isclose(np.sum(self.pi), 1.0, atol=1e-4):
            raise ValueError(f"Vector pi debe sumar 1.0 (suma={np.sum(self.pi)})")

        if self.A.shape != (self.N, self.N):
            raise ValueError(f"Matriz A debe ser de forma ({self.N}, {self.N})")
        if not np.allclose(np.sum(self.A, axis=1), 1.0, atol=1e-4):
            raise ValueError("Cada fila de la matriz de transición A debe sumar 1.0")

        if self.B.shape != (self.N, self.M):
            raise ValueError(f"Matriz B debe ser de forma ({self.N}, {self.M})")
        if not np.allclose(np.sum(self.B, axis=1), 1.0, atol=1e-4):
            raise ValueError("Cada fila de la matriz de emisión B debe sumar 1.0")

    def simulate(self, T: int, seed: Optional[int] = None) -> Tuple[List[int], List[int]]:
        """
        Simula una trayectoria de T pasos de tiempo para el HMM usando el método Monte Carlo.

        Parámetros
        ----------
        T : int
            Número de pasos de tiempo a simular (ej. 96 pasos de 15 min = 24 horas).
        seed : int, opcional
            Semilla para reproducibilidad estocástica.

        Retorna
        -------
        Tuple[List[int], List[int]]
            (secuencia_estados_ocultos, secuencia_observaciones) con índices enteros.
        """
        rng = np.random.default_rng(seed)
        hidden_states = np.zeros(T, dtype=int)
        observations = np.zeros(T, dtype=int)

        # 1. Generar estado inicial X_0 según pi
        hidden_states[0] = rng.choice(self.N, p=self.pi)
        # Generar observación inicial Y_0 según B[X_0]
        observations[0] = rng.choice(self.M, p=self.B[hidden_states[0]])

        # 2. Generar pasos sucesivos t = 1, ..., T-1
        for t in range(1, T):
            prev_state = hidden_states[t - 1]
            curr_state = rng.choice(self.N, p=self.A[prev_state])
            curr_obs = rng.choice(self.M, p=self.B[curr_state])

            hidden_states[t] = curr_state
            observations[t] = curr_obs

        return hidden_states.tolist(), observations.tolist()

    def viterbi(self, observations_seq: List[int]) -> Tuple[List[int], float]:
        """
        Algoritmo de Viterbi para decodificación del estado más probable.
        Dada una secuencia observada de mediciones de sensores Y_1...Y_T,
        calcula la trayectoria óptima de estados ocultos X*_1...X*_T que maximiza P(X, Y | lambda).

        Implementado en escala logarítmica para evitar underflow numérico.

        Parámetros
        ----------
        observations_seq : List[int]
            Lista de índices de observaciones.

        Retorna
        -------
        Tuple[List[int], float]
            (mejor_secuencia_estados, log_probabilidad_maxima)
        """
        T = len(observations_seq)
        if T == 0:
            return [], 0.0

        # Evitar log(0) con epsilon
        eps = 1e-12
        log_pi = np.log(np.maximum(self.pi, eps))
        log_A = np.log(np.maximum(self.A, eps))
        log_B = np.log(np.maximum(self.B, eps))

        # Matrices de programación dinámica:
        # V[t, i] almacena la mayor log-probabilidad de una trayectoria que termina en estado i en tiempo t
        V = np.zeros((T, self.N))
        # backpointer[t, i] guarda el estado del tiempo t-1 que maximizó V[t, i]
        backpointer = np.zeros((T, self.N), dtype=int)

        # Inicialización t = 0
        first_obs = observations_seq[0]
        V[0, :] = log_pi + log_B[:, first_obs]

        # Inducción hacia adelante t = 1 ... T-1
        for t in range(1, T):
            obs = observations_seq[t]
            for j in range(self.N):
                # V[t-1, i] + log(A[i, j]) para todos los posibles estados previos i
                prob_transitions = V[t - 1, :] + log_A[:, j]
                best_prev = np.argmax(prob_transitions)
                V[t, j] = prob_transitions[best_prev] + log_B[j, obs]
                backpointer[t, j] = best_prev

        # Terminación: encontrar el estado final con mayor probabilidad
        best_last_state = int(np.argmax(V[T - 1, :]))
        best_log_prob = float(V[T - 1, best_last_state])

        # Reconstrucción de la trayectoria (Backtracking)
        best_path = [0] * T
        best_path[T - 1] = best_last_state
        for t in range(T - 2, -1, -1):
            best_path[t] = int(backpointer[t + 1, best_path[t + 1]])

        return best_path, best_log_prob

    def forward(self, observations_seq: List[int]) -> Tuple[np.ndarray, float]:
        """
        Algoritmo Forward (Adelante) para calcular la verosimilitud P(Y | lambda)
        y la matriz de probabilidades hacia adelante alpha[t, i] = P(Y_1...Y_t, X_t = s_i | lambda).

        Retorna
        -------
        Tuple[np.ndarray, float]
            (alpha_matrix escalada, log_verosimilitud_total)
        """
        T = len(observations_seq)
        alpha = np.zeros((T, self.N))
        scales = np.zeros(T)

        # Inicialización t = 0
        alpha[0, :] = self.pi * self.B[:, observations_seq[0]]
        scales[0] = np.sum(alpha[0, :])
        alpha[0, :] /= scales[0]

        # Inducción
        for t in range(1, T):
            obs = observations_seq[t]
            for j in range(self.N):
                alpha[t, j] = np.sum(alpha[t - 1, :] * self.A[:, j]) * self.B[j, obs]
            scales[t] = np.sum(alpha[t, :])
            if scales[t] > 0:
                alpha[t, :] /= scales[t]

        log_likelihood = float(np.sum(np.log(scales)))
        return alpha, log_likelihood

    def compute_stationary_distribution(self) -> np.ndarray:
        """
        Calcula la distribución estacionaria pi* de la cadena de Markov subyacente.
        Resuelve el sistema lineal:
            pi* A = pi*
            sum(pi*) = 1
        Equivalente a (A.T - I) * pi*.T = 0 con la restricción de suma unitaria.

        Retorna
        -------
        np.ndarray
            Vector de probabilidades en estado estable [pi*_F, pi*_M, pi*_C].
        """
        # Matriz del sistema lineal: (A.T - I)
        Q = self.A.T - np.eye(self.N)
        # Reemplazamos la última fila por la condición sum(pi*) = 1
        Q[-1, :] = 1.0
        b = np.zeros(self.N)
        b[-1] = 1.0

        try:
            stationary = np.linalg.solve(Q, b)
            # Asegurar que no haya valores negativos por redondeo numérico
            stationary = np.clip(stationary, 0, 1)
            stationary /= np.sum(stationary)
            return stationary
        except np.linalg.LinAlgError:
            # En caso excepcional, recurrir a potencias de matriz A^k para k grande
            A_k = np.linalg.matrix_power(self.A, 1000)
            return A_k[0, :]

    def expected_holding_times(self) -> Dict[str, float]:
        """
        Calcula el tiempo promedio de permanencia continua en cada estado (Holding Time).
        Dado que el tiempo en un estado sigue una distribución geométrica:
            E[T_i] = 1 / (1 - a_{ii}) pasos de tiempo.
        """
        holding_times = {}
        for i, state in enumerate(self.states):
            p_exit = 1.0 - self.A[i, i]
            # Si p_exit es muy pequeño, evitamos división por cero
            e_steps = 1.0 / p_exit if p_exit > 1e-9 else float("inf")
            holding_times[state] = e_steps
        return holding_times

    def predict_future_distribution(self, initial_dist: np.ndarray, steps: int) -> np.ndarray:
        """
        Calcula la distribución de probabilidad de los estados después de k pasos de tiempo:
            pi_{t+k} = pi_t * A^k
        """
        A_power = np.linalg.matrix_power(self.A, steps)
        return np.dot(initial_dist, A_power)
