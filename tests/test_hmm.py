"""
Suite de Pruebas Unitarias y Verificación Matemática del Modelo Oculto de Markov (HMM).
Valida propiedades estocásticas, distribución estacionaria, algoritmos de inferencia
(Viterbi y Forward-Backward) y reproducibilidad de Monte Carlo.
"""

import unittest
import numpy as np
from traffic_hmm import TrafficHMM, TrafficSimulation


class TestTrafficHMM(unittest.TestCase):
    """Pruebas rigurosas de las propiedades algebraicas y probabilísticas del HMM."""

    def setUp(self) -> None:
        self.hmm = TrafficHMM()

    def test_stochastic_constraints(self) -> None:
        """Verifica no-negatividad y suma unitaria en pi, A y B."""
        self.assertTrue(np.all(self.hmm.pi >= 0.0))
        self.assertTrue(np.all(self.hmm.A >= 0.0))
        self.assertTrue(np.all(self.hmm.B >= 0.0))

        self.assertAlmostEqual(float(np.sum(self.hmm.pi)), 1.0, places=10)
        np.testing.assert_allclose(np.sum(self.hmm.A, axis=1), np.ones(self.hmm.N), atol=1e-10)
        np.testing.assert_allclose(np.sum(self.hmm.B, axis=1), np.ones(self.hmm.N), atol=1e-10)

    def test_invalid_matrix_raises_error(self) -> None:
        """Comprueba que matrices cuyas filas no suman 1 lancen ValueError."""
        bad_A = np.array([
            [0.80, 0.25, 0.05],  # Suma 1.10
            [0.20, 0.60, 0.20],
            [0.05, 0.30, 0.65],
        ])
        with self.assertRaises(ValueError):
            TrafficHMM(transition_matrix=bad_A)

    def test_stationary_distribution_invariance(self) -> None:
        """Comprueba analíticamente que pi* * A = pi* y sum(pi*) = 1."""
        pi_star = self.hmm.compute_stationary_distribution()
        self.assertAlmostEqual(float(np.sum(pi_star)), 1.0, places=10)
        np.testing.assert_allclose(pi_star @ self.hmm.A, pi_star, atol=1e-10)

        # Fracciones exactas esperadas: [32/101, 41/101, 28/101]
        expected_exact = np.array([32.0 / 101.0, 41.0 / 101.0, 28.0 / 101.0])
        np.testing.assert_allclose(pi_star, expected_exact, atol=1e-10)

    def test_chapman_kolmogorov_convergence(self) -> None:
        """Comprueba que pi_0 * A^k converge a pi* desde cualquier estado inicial."""
        pi_star = self.hmm.compute_stationary_distribution()
        for idx in range(self.hmm.N):
            e_i = np.zeros(self.hmm.N)
            e_i[idx] = 1.0
            pi_50 = self.hmm.predict_future_distribution(e_i, steps=50)
            np.testing.assert_allclose(pi_50, pi_star, atol=1e-8)

    def test_holding_and_recurrence_times(self) -> None:
        """Verifica tiempos medios de permanencia 1/(1 - a_ii) y recurrencia 1/pi*_i."""
        holding = self.hmm.expected_holding_times()
        self.assertAlmostEqual(holding["Fluido"], 1.0 / 0.30, places=8)
        self.assertAlmostEqual(holding["Moderado"], 1.0 / 0.40, places=8)
        self.assertAlmostEqual(holding["Congestionado"], 1.0 / 0.35, places=8)

        recurrence = self.hmm.mean_recurrence_times()
        pi_star = self.hmm.compute_stationary_distribution()
        for i, state in enumerate(self.hmm.states):
            self.assertAlmostEqual(recurrence[state], 1.0 / pi_star[i], places=8)

    def test_viterbi_and_forward_backward_consistency(self) -> None:
        """Verifica coherencia dimensional y normalización de Viterbi y Forward-Backward."""
        states_idx, obs_idx = self.hmm.simulate(T=96, seed=42)
        self.assertEqual(len(states_idx), 96)
        self.assertEqual(len(obs_idx), 96)

        viterbi_path, log_prob = self.hmm.viterbi(obs_idx)
        self.assertEqual(len(viterbi_path), 96)
        self.assertLess(log_prob, 0.0)
        self.assertTrue(np.all((np.array(viterbi_path) >= 0) & (np.array(viterbi_path) < self.hmm.N)))

        gamma, posterior_states, log_likelihood = self.hmm.forward_backward(obs_idx)
        self.assertEqual(gamma.shape, (96, self.hmm.N))
        self.assertEqual(len(posterior_states), 96)
        np.testing.assert_allclose(np.sum(gamma, axis=1), np.ones(96), atol=1e-8)
        # La verosimilitud marginal log P(Y) siempre es >= log P(X*, Y) de una sola ruta
        self.assertGreaterEqual(log_likelihood, log_prob - 1e-8)

    def test_monte_carlo_ergodic_convergence(self) -> None:
        """Verifica que la simulación Monte Carlo converge empíricamente a pi* (MAE < 0.015)."""
        sim = TrafficSimulation(self.hmm)
        mc = sim.run_monte_carlo_validation(num_replicas=500, steps_per_replica=96, seed=100)
        self.assertLess(mc["mae_stationary"], 0.015)
        self.assertGreater(mc["mean_accuracy"], 0.70)
        # Verifica que Viterbi suprime más del 50% de las oscilaciones ruidosas del sensor crudo
        self.assertLess(mc["mean_switches_viterbi"], 0.55 * mc["mean_switches_naive"])


if __name__ == "__main__":
    unittest.main()
