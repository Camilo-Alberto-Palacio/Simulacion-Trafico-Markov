"""
Módulo de Visualizaciones Científicas para el HMM de Tráfico Vehicular.
Genera figuras en alta resolución (300 DPI) para el informe técnico y el repositorio.
"""

from typing import Dict, Any, List, Optional
import os
import numpy as np
import matplotlib.pyplot as plt
from .model import TrafficHMM


class TrafficVisualizer:
    """
    Generador de gráficos e ilustraciones visuales del comportamiento del HMM.
    """

    def __init__(self, output_dir: str = "results"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        # Paleta de colores consistente
        self.colors = {
            "Fluido": "#2ecc71",        # Verde esmeralda
            "Moderado": "#f39c12",      # Naranja ambar
            "Congestionado": "#e74c3c",  # Rojo carmesí
            "Alta": "#3498db",          # Azul
            "Media": "#9b59b6",         # Púrpura
            "Baja": "#34495e",          # Gris oscuro / grafito
        }

    def plot_matrices(self, hmm: TrafficHMM, filename: str = "fig1_matrices_transicion_emision.png") -> str:
        """
        Grafica las matrices estocásticas de Transición (A) y Emisión (B) con anotaciones numéricas.
        """
        fig, axes = plt.subplots(1, 2, figsize=(13, 5), dpi=300)

        # 1. Matriz de Transición A
        im1 = axes[0].imshow(hmm.A, cmap="Blues", vmin=0, vmax=1)
        axes[0].set_title("Matriz de Transición de Estados ($A$)", fontsize=13, fontweight="bold", pad=12)
        axes[0].set_xticks(range(hmm.N))
        axes[0].set_yticks(range(hmm.N))
        axes[0].set_xticklabels(hmm.states, fontsize=10)
        axes[0].set_yticklabels(hmm.states, fontsize=10)
        axes[0].set_xlabel("Estado Siguiente ($X_{t+1}$)", fontsize=11, fontweight="semibold")
        axes[0].set_ylabel("Estado Actual ($X_t$)", fontsize=11, fontweight="semibold")

        for i in range(hmm.N):
            for j in range(hmm.N):
                val = hmm.A[i, j]
                text_color = "white" if val > 0.5 else "black"
                axes[0].text(j, i, f"{val:.2f}\n({val*100:.0f}%)", ha="center", va="center",
                             color=text_color, fontsize=11, fontweight="bold")

        fig.colorbar(im1, ax=axes[0], fraction=0.046, pad=0.04)

        # 2. Matriz de Emisión B
        im2 = axes[1].imshow(hmm.B, cmap="Oranges", vmin=0, vmax=1)
        axes[1].set_title("Matriz de Emisión de Sensores ($B$)", fontsize=13, fontweight="bold", pad=12)
        axes[1].set_xticks(range(hmm.M))
        axes[1].set_yticks(range(hmm.N))
        axes[1].set_xticklabels(hmm.observations, fontsize=9)
        axes[1].set_yticklabels(hmm.states, fontsize=10)
        axes[1].set_xlabel("Lectura Sensor / Velocidad ($Y_t$)", fontsize=11, fontweight="semibold")
        axes[1].set_ylabel("Estado Real Oculto ($X_t$)", fontsize=11, fontweight="semibold")

        for i in range(hmm.N):
            for j in range(hmm.M):
                val = hmm.B[i, j]
                text_color = "white" if val > 0.5 else "black"
                axes[1].text(j, i, f"{val:.2f}\n({val*100:.0f}%)", ha="center", va="center",
                             color=text_color, fontsize=11, fontweight="bold")

        fig.colorbar(im2, ax=axes[1], fraction=0.046, pad=0.04)

        plt.tight_layout()
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, bbox_inches="tight")
        plt.close()
        return filepath

    def plot_single_day_timeline(
        self,
        sim_result: Dict[str, Any],
        filename: str = "fig2_simulacion_jornada_24h.png"
    ) -> str:
        """
        Visualiza la trayectoria de 24 horas comparando el estado real, las observaciones
        captadas por los sensores y la estimación del estado óptimo mediante Viterbi.
        """
        df = sim_result["dataframe"]
        accuracy = sim_result["accuracy"]

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), dpi=300, sharex=True)

        steps = df["Paso"].values
        real_ids = df["Estado_Real_Id"].values
        viterbi_ids = df["Estado_Viterbi_Id"].values
        obs_ids = df["Observacion_Id"].values

        # Subplot 1: Estado Oculto Real vs Estimado por Viterbi
        ax1.plot(steps, real_ids, label="Estado Oculto Real ($X_t$)", color="#2c3e50",
                 linewidth=2.5, marker="o", markersize=4, alpha=0.9)
        ax1.plot(steps, viterbi_ids, label="Inferencia Viterbi ($X^*_t$)", color="#e74c3c",
                 linewidth=2.0, linestyle="--", marker="x", markersize=6, alpha=0.85)

        # Resaltar discordancias (errores de inferencia del sensor)
        mismatch_mask = df["Acierto"] == False
        if np.any(mismatch_mask):
            ax1.scatter(steps[mismatch_mask], real_ids[mismatch_mask], color="#c0392b",
                        s=90, zorder=5, facecolors="none", edgecolors="red", linewidths=2,
                        label="Desacuerdo de Inferencia")

        ax1.set_yticks([0, 1, 2])
        ax1.set_yticklabels(["Fluido (0)", "Moderado (1)", "Congestionado (2)"], fontsize=10, fontweight="bold")
        ax1.set_title(f"Simulación 24 Horas: Estado Real vs. Inferencia de Viterbi (Exactitud: {accuracy*100:.1f}%)",
                      fontsize=12, fontweight="bold", pad=10)
        ax1.grid(True, linestyle=":", alpha=0.6)
        ax1.legend(loc="upper right", framealpha=0.9)

        # Subplot 2: Mediciones de Sensores (Observaciones Visibles)
        # 0: Vel Alta, 1: Vel Media, 2: Vel Baja
        colors_obs = ["#27ae60" if o == 0 else "#f39c12" if o == 1 else "#8e44ad" for o in obs_ids]
        ax2.scatter(steps, obs_ids, c=colors_obs, s=40, alpha=0.8, edgecolors="black", linewidths=0.5)
        ax2.plot(steps, obs_ids, color="#7f8c8d", linestyle=":", alpha=0.5, linewidth=1)

        ax2.set_yticks([0, 1, 2])
        ax2.set_yticklabels(["Velocidad Alta (0)", "Velocidad Media (1)", "Velocidad Baja (2)"],
                            fontsize=10, fontweight="bold")
        ax2.set_title("Señal Visible Registrada por Sensores de Velocidad ($Y_t$)",
                      fontsize=12, fontweight="bold", pad=10)
        ax2.set_xlabel("Hora del Día (Intervalos de 15 minutos)", fontsize=11, fontweight="semibold")
        ax2.grid(True, linestyle=":", alpha=0.6)

        # Eje X con marcas de hora cada 2 horas (cada 8 pasos)
        tick_locs = steps[::8]
        tick_labels = df["Hora"].values[::8]
        ax2.set_xticks(tick_locs)
        ax2.set_xticklabels(tick_labels, rotation=45, ha="right", fontsize=9)

        plt.tight_layout()
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, bbox_inches="tight")
        plt.close()
        return filepath

    def plot_stationary_convergence(
        self,
        hmm: TrafficHMM,
        steps: int = 15,
        filename: str = "fig3_convergencia_distribucion_estacionaria.png"
    ) -> str:
        """
        Demuestra la evolución de las probabilidades de estado en el tiempo (pi_t = pi_0 * A^t)
        mostrando cómo converge asintóticamente a la distribución estacionaria teórica.
        """
        stationary = hmm.compute_stationary_distribution()

        # Probar con dos estados iniciales contrastantes:
        # 1. Inicio 100% Fluido
        # 2. Inicio 100% Congestionado
        initial_conditions = [
            ("Inicio 100% Fluido", np.array([1.0, 0.0, 0.0])),
            ("Inicio 100% Congestionado", np.array([0.0, 0.0, 1.0])),
        ]

        fig, axes = plt.subplots(1, 2, figsize=(14, 5), dpi=300, sharey=True)

        t_range = np.arange(steps + 1)

        for ax_idx, (title, pi_0) in enumerate(initial_conditions):
            history = np.zeros((steps + 1, hmm.N))
            history[0, :] = pi_0

            for t in range(1, steps + 1):
                history[t, :] = hmm.predict_future_distribution(pi_0, t)

            for s_idx, state_name in enumerate(hmm.states):
                color = self.colors[state_name]
                axes[ax_idx].plot(t_range, history[:, s_idx], label=f"P({state_name})",
                                  color=color, linewidth=2.2, marker="s", markersize=4)
                # Línea punteada de asíntota estacionaria
                axes[ax_idx].axhline(stationary[s_idx], color=color, linestyle="--", alpha=0.6,
                                     label=rf"$\pi^*_{{{state_name}}}$ = {stationary[s_idx]:.3f}" if ax_idx == 0 else "")

            axes[ax_idx].set_title(f"Convergencia desde: {title}", fontsize=12, fontweight="bold")
            axes[ax_idx].set_xlabel("Paso de tiempo $k$ (Intervalos de 15 min)", fontsize=10, fontweight="semibold")
            if ax_idx == 0:
                axes[ax_idx].set_ylabel("Probabilidad de Estado $P(X_k = s)$", fontsize=10, fontweight="semibold")
            axes[ax_idx].set_ylim(0, 1.05)
            axes[ax_idx].grid(True, linestyle=":", alpha=0.6)
            axes[ax_idx].legend(loc="best", fontsize=9, framealpha=0.9)

        fig.suptitle(rf"Convergencia Asintótica a la Distribución Estacionaria $\pi^* = [{stationary[0]:.2f}, {stationary[1]:.2f}, {stationary[2]:.2f}]$",
                     fontsize=13, fontweight="bold", y=1.02)
        plt.tight_layout()
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, bbox_inches="tight")
        plt.close()
        return filepath

    def plot_monte_carlo_comparison(
        self,
        mc_result: Dict[str, Any],
        states: List[str],
        filename: str = "fig4_validacion_monte_carlo.png"
    ) -> str:
        """
        Compara las frecuencias empíricas de 1000 réplicas Monte Carlo contra la distribución
        estacionaria teórica, junto con el histograma de exactitud del algoritmo de Viterbi.
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), dpi=300)

        # 1. Comparativa de Barras: Teórico vs Empírico
        x = np.arange(len(states))
        width = 0.35

        theo = mc_result["theoretical_stationary"]
        emp = mc_result["empirical_stationary"]

        ax1.bar(x - width/2, theo * 100, width, label=r"Distribución Teórica ($\pi^*$)",
                color="#2980b9", edgecolor="black", alpha=0.85)
        ax1.bar(x + width/2, emp * 100, width, label=f"Simulación Monte Carlo ($N={mc_result['num_replicas']}$)",
                color="#27ae60", edgecolor="black", alpha=0.85)

        for i in range(len(states)):
            ax1.text(x[i] - width/2, theo[i]*100 + 1, f"{theo[i]*100:.1f}%", ha="center", fontsize=9, fontweight="bold")
            ax1.text(x[i] + width/2, emp[i]*100 + 1, f"{emp[i]*100:.1f}%", ha="center", fontsize=9, fontweight="bold")

        ax1.set_xticks(x)
        ax1.set_xticklabels(states, fontsize=10, fontweight="bold")
        ax1.set_ylabel("Porcentaje de Tiempo (%)", fontsize=11, fontweight="semibold")
        ax1.set_title(f"Distribución Estacionaria Teórica vs. Empírica (MAE = {mc_result['mae_stationary']:.4f})",
                      fontsize=11, fontweight="bold")
        ax1.set_ylim(0, max(np.max(theo), np.max(emp)) * 125)
        ax1.grid(axis="y", linestyle=":", alpha=0.6)
        ax1.legend(loc="upper right", framealpha=0.9)

        # 2. Histograma de Exactitud de Decodificación de Viterbi
        # Re-simular exactitudes si es necesario o graficar métricas
        mean_acc = mc_result["mean_accuracy"] * 100
        std_acc = mc_result["std_accuracy"] * 100

        ax2.axvline(mean_acc, color="#e74c3c", linestyle="--", linewidth=2.5,
                    label=f"Media: {mean_acc:.1f}% (±{std_acc:.1f}%)")
        ax2.set_title("Eficacia de Decodificación del Algoritmo de Viterbi", fontsize=11, fontweight="bold")
        ax2.set_xlabel("Exactitud de Inferencia del Estado Oculto (%)", fontsize=11, fontweight="semibold")
        ax2.set_ylabel("Frecuencia", fontsize=11, fontweight="semibold")

        # Representación tipo caja o resumen
        ax2.text(0.5, 0.6, f"Resumen Estadístico ({mc_result['num_replicas']} Réplicas):\n"
                           f"• Pasos totales simulados: {mc_result['total_steps_simulated']:,}\n"
                           f"• Exactitud Promedio: {mean_acc:.2f}%\n"
                           f"• Desviación Estándar: {std_acc:.2f}%\n"
                           f"• Rango: [{mc_result['min_accuracy']*100:.1f}% - {mc_result['max_accuracy']*100:.1f}%]\n"
                           f"• Error Absoluto Medio (MAE): {mc_result['mae_stationary']:.5f}",
                 transform=ax2.transAxes, ha="center", va="center",
                 bbox=dict(boxstyle="round,pad=0.8", facecolor="#ecf0f1", edgecolor="#bdc3c7", alpha=0.95),
                 fontsize=11)
        ax2.set_xticks(np.arange(60, 105, 5))
        ax2.set_xlim(60, 100)
        ax2.legend(loc="upper left")
        ax2.grid(True, linestyle=":", alpha=0.6)

        plt.tight_layout()
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, bbox_inches="tight")
        plt.close()
        return filepath

    def plot_incident_scenario(
        self,
        incident_result: Dict[str, Any],
        filename: str = "fig5_escenario_incidente_recuperacion.png"
    ) -> str:
        """
        Visualiza el impacto y resiliencia del corredor ante un incidente de tránsito (congestión forzada)
        y su posterior proceso de disipación y normalización.
        """
        df = incident_result["dataframe"]
        start = incident_result["incident_start"]
        end = incident_result["incident_end"]

        fig, ax = plt.subplots(figsize=(14, 5), dpi=300)

        steps = df["Paso"].values
        state_map = {"Fluido": 0, "Moderado": 1, "Congestionado": 2}
        real_ids = [state_map[s] for s in df["Estado_Real"]]
        viterbi_ids = [state_map[s] for s in df["Estado_Viterbi"]]

        # Sombreado del período del incidente
        ax.axvspan(start, end, color="#e74c3c", alpha=0.2, label=f"Período del Incidente (Pasos {start}-{end})")

        ax.plot(steps, real_ids, label="Estado Oculto Real", color="#2c3e50", linewidth=2.2, marker="o", markersize=4)
        ax.plot(steps, viterbi_ids, label="Inferencia Viterbi", color="#e67e22", linestyle="--",
                linewidth=1.8, marker="^", markersize=5)

        ax.set_yticks([0, 1, 2])
        ax.set_yticklabels(["Fluido", "Moderado", "Congestionado"], fontsize=10, fontweight="bold")
        ax.set_title("Respuesta del Sistema ante Perturbación Exógena (Accidente Vial y Disipación)",
                     fontsize=12, fontweight="bold", pad=12)
        ax.set_xlabel("Hora del Día (Intervalos de 15 min)", fontsize=11, fontweight="semibold")
        ax.set_ylabel("Estado del Tráfico", fontsize=11, fontweight="semibold")

        tick_locs = steps[::8]
        tick_labels = df["Hora"].values[::8]
        ax.set_xticks(tick_locs)
        ax.set_xticklabels(tick_labels, rotation=45, ha="right", fontsize=9)

        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(loc="upper right", framealpha=0.95)

        plt.tight_layout()
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, bbox_inches="tight")
        plt.close()
        return filepath

    def plot_confusion_matrix(
        self,
        cm: np.ndarray,
        states: List[str],
        filename: str = "fig6_matriz_confusion_viterbi.png"
    ) -> str:
        """
        Grafica la matriz de confusión entre los estados reales simulados y los estimados por Viterbi.
        """
        fig, ax = plt.subplots(figsize=(6, 5), dpi=300)

        im = ax.imshow(cm, cmap="Blues")
        ax.set_title("Matriz de Confusión: Real vs. Viterbi", fontsize=12, fontweight="bold", pad=12)
        ax.set_xticks(range(len(states)))
        ax.set_yticks(range(len(states)))
        ax.set_xticklabels(states, fontsize=10)
        ax.set_yticklabels(states, fontsize=10)
        ax.set_xlabel("Estado Inferido por Viterbi ($X^*$)", fontsize=10, fontweight="semibold")
        ax.set_ylabel("Estado Oculto Real ($X$)", fontsize=10, fontweight="semibold")

        total = np.sum(cm)
        for i in range(len(states)):
            for j in range(len(states)):
                count = cm[i, j]
                pct = (count / total) * 100 if total > 0 else 0
                color = "white" if count > np.max(cm)/2 else "black"
                ax.text(j, i, f"{count}\n({pct:.1f}%)", ha="center", va="center",
                        color=color, fontsize=10, fontweight="bold")

        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        plt.tight_layout()
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, bbox_inches="tight")
        plt.close()
        return filepath
