"""
Módulo de Visualizaciones Científicas para el HMM de Tráfico Vehicular.
Genera 7 figuras de calidad editorial (300 DPI) sin solapamientos ni advertencias tipográficas.
"""

from typing import Dict, Any, List
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
from .model import TrafficHMM


class TrafficVisualizer:
    """
    Generador de gráficos e ilustraciones visuales del comportamiento del HMM.
    """

    def __init__(self, output_dir: str = "results"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        self.colors = {
            "Fluido": "#27ae60",         # Verde esmeralda
            "Moderado": "#f39c12",       # Ámbar
            "Congestionado": "#e74c3c",  # Rojo carmesí
        }

    def plot_hmm_architecture(
        self,
        hmm: TrafficHMM,
        filename: str = "fig0_diagrama_estructura_hmm.png"
    ) -> str:
        """
        Dibuja el grafo dirigido completo de la arquitectura del Modelo Oculto de Markov:
        separa visualmente la Capa Oculta (estados y transiciones A, vector inicial pi)
        de la Capa Observable (sensores de velocidad y emisiones B).
        """
        fig, ax = plt.subplots(figsize=(13, 7.2), dpi=300)
        ax.set_xlim(0, 13)
        ax.set_ylim(0, 7.6)
        ax.axis("off")

        # Fondos de las dos capas
        hidden_bg = FancyBboxPatch(
            (0.4, 3.72), 12.2, 3.50,
            boxstyle="round,pad=0.15,rounding_size=0.25",
            facecolor="#EFF6FF", edgecolor="#93C5FD", linewidth=1.6, zorder=0
        )
        obs_bg = FancyBboxPatch(
            (0.4, 0.35), 12.2, 2.15,
            boxstyle="round,pad=0.15,rounding_size=0.25",
            facecolor="#FFF7ED", edgecolor="#FDBA74", linewidth=1.6, zorder=0
        )
        ax.add_patch(hidden_bg)
        ax.add_patch(obs_bg)

        ax.text(
            0.7, 7.00,
            "CAPA OCULTA / LATENTE — Cadena de Markov Subyacente ($X_t \\in \\mathcal{S}$: Condición Vial Real)",
            fontsize=10.8, fontweight="bold", color="#1E3A8A"
        )
        ax.text(
            0.7, 0.52,
            "CAPA OBSERVABLE / VISIBLE — Telemetría ($Y_t \\in \\mathcal{V}$)",
            fontsize=10.2, fontweight="bold", color="#9A3412"
        )
        ax.text(
            12.3, 0.52,
            "Flechas grises ($0.05 - 0.20$): Ruido instrumental del radar",
            ha="right", va="baseline", fontsize=9.0, color="#64748B", style="italic"
        )

        # Posiciones horizontales de los 3 nodos
        xs = [2.6, 6.5, 10.4]
        y_hidden = 5.15
        y_obs = 1.68
        state_colors = ["#27ae60", "#f39c12", "#e74c3c"]
        obs_labels = [
            "Velocidad Alta\n($v > 60$ km/h)",
            "Velocidad Media\n($30 - 60$ km/h)",
            "Velocidad Baja\n($v < 30$ km/h)",
        ]

        # Nodos de Estados Ocultos + Probabilidades iniciales + Bucles de inercia
        r_node = 0.72
        for i, (x, st_name, col) in enumerate(zip(xs, hmm.states, state_colors)):
            circle = Circle((x, y_hidden), r_node, facecolor=col, edgecolor="#1E293B", linewidth=2.0, alpha=0.92, zorder=4)
            ax.add_patch(circle)
            ax.text(x, y_hidden + 0.08, f"$S_{i+1}$\n{st_name}", ha="center", va="center",
                    color="white", fontsize=10.5, fontweight="bold", zorder=5)
            ax.text(x, y_hidden - 0.42, f"$\\pi_{i+1}={hmm.pi[i]:.2f}$", ha="center", va="center",
                    color="white", fontsize=8.5, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.15", facecolor="#0F172A", edgecolor="none", alpha=0.55), zorder=5)

            # Bucle de autotransición (inercia diagonal a_ii)
            loop = FancyArrowPatch(
                (x - 0.38, y_hidden + 0.62), (x + 0.38, y_hidden + 0.62),
                connectionstyle="arc3,rad=-1.45",
                arrowstyle="-|>,head_length=6,head_width=4",
                color="#1E3A8A", linewidth=2.0, zorder=3
            )
            ax.add_patch(loop)
            ax.text(x, y_hidden + 1.33, f"$a_{{{i+1}{i+1}}}={hmm.A[i, i]:.2f}$",
                    ha="center", va="center", fontsize=9.2, fontweight="bold", color="#1E3A8A",
                    bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="#BFDBFE", alpha=0.95), zorder=6)

        # Flechas de transición entre estados adyacentes
        adj_pairs = [
            (0, 1, 0.20, 0.22),   # Fluido -> Moderado (arriba)
            (1, 0, -0.20, -0.28), # Moderado -> Fluido (abajo)
            (1, 2, 0.20, 0.22),   # Moderado -> Congestionado (arriba)
            (2, 1, -0.20, -0.28), # Congestionado -> Moderado (abajo)
        ]
        for i, j, dy, rad in adj_pairs:
            x_start = xs[i] + (r_node if j > i else -r_node)
            x_end = xs[j] - (r_node if j > i else -r_node)
            arrow = FancyArrowPatch(
                (x_start, y_hidden + dy * 0.5), (x_end, y_hidden + dy * 0.5),
                connectionstyle=f"arc3,rad={ -0.18 if j > i else -0.18 }",
                arrowstyle="-|>,head_length=6,head_width=4",
                color="#334155", linewidth=1.7, zorder=3
            )
            ax.add_patch(arrow)
            xm = 0.5 * (xs[i] + xs[j])
            ym = y_hidden + (0.38 if j > i else -0.42)
            ax.text(xm, ym, f"$a_{{{i+1}{j+1}}}={hmm.A[i, j]:.2f}$",
                    ha="center", va="center", fontsize=8.8, fontweight="bold", color="#1E293B",
                    bbox=dict(boxstyle="round,pad=0.12", facecolor="white", edgecolor="#CBD5E1", alpha=0.92), zorder=6)

        # Transiciones extremas (Fluido <-> Congestionado = 0.05) por debajo de los nodos ocultos
        extreme_arrow_fc = FancyArrowPatch(
            (xs[0] + 0.45, y_hidden - 0.58), (xs[2] - 0.45, y_hidden - 0.58),
            connectionstyle="arc3,rad=0.18",
            arrowstyle="<->,head_length=5,head_width=3.5",
            color="#64748B", linestyle=":", linewidth=1.4, zorder=2
        )
        ax.add_patch(extreme_arrow_fc)
        ax.text(6.5, y_hidden - 1.12,
                f"Saltos extremos poco probables: $a_{{13}}={hmm.A[0,2]:.2f}$, $a_{{31}}={hmm.A[2,0]:.2f}$",
                ha="center", va="center", fontsize=8.5, color="#475569", style="italic",
                bbox=dict(boxstyle="round,pad=0.15", facecolor="#F8FAFC", edgecolor="#CBD5E1"), zorder=6)

        # Nodos de Observaciones Visibles (Sensores)
        obs_colors = ["#0284C7", "#7C3AED", "#475569"]
        box_w, box_h = 2.35, 0.90
        for k, (x, lbl, ocol) in enumerate(zip(xs, obs_labels, obs_colors)):
            rect = FancyBboxPatch(
                (x - box_w / 2, y_obs - box_h / 2), box_w, box_h,
                boxstyle="round,pad=0.08,rounding_size=0.15",
                facecolor=ocol, edgecolor="#0F172A", linewidth=1.7, alpha=0.92, zorder=4
            )
            ax.add_patch(rect)
            ax.text(x, y_obs, f"$V_{k+1}$: {lbl}", ha="center", va="center",
                    color="white", fontsize=9.5, fontweight="bold", zorder=5)

        # Flechas de emisión B (dominantes en diagonal + cruzadas ruidosas)
        for j in range(3):
            for k in range(3):
                prob = hmm.B[j, k]
                is_diag = (j == k)
                start_pt = (xs[j] + (k - j) * 0.18, y_hidden - r_node - 0.02)
                end_pt = (xs[k] + (j - k) * 0.18, y_obs + box_h / 2 + 0.05)
                em_arrow = FancyArrowPatch(
                    start_pt, end_pt,
                    arrowstyle="-|>,head_length=6,head_width=4" if is_diag else "-|>,head_length=4.5,head_width=3",
                    color="#C2410C" if is_diag else "#94A3B8",
                    linestyle="--",
                    linewidth=2.2 if is_diag else 1.1,
                    alpha=0.95 if is_diag else 0.65,
                    zorder=3 if is_diag else 1
                )
                ax.add_patch(em_arrow)
                if is_diag:
                    ax.text(
                        xs[j],
                        3.08,
                        f"$b_{{{j+1}{k+1}}}={prob:.2f}$",
                        ha="center", va="center", fontsize=9.2, fontweight="bold", color="#9A3412",
                        bbox=dict(boxstyle="round,pad=0.16", facecolor="#FFEDD5", edgecolor="#FB923C"), zorder=6
                    )

        ax.set_title(
            "Arquitectura del Modelo Oculto de Markov (HMM) Aplicado al Tráfico Vehicular Urbano",
            fontsize=13, fontweight="bold", color="#0F172A", pad=8
        )

        plt.tight_layout()
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, bbox_inches="tight")
        plt.close()
        return filepath

    def plot_matrices(self, hmm: TrafficHMM, filename: str = "fig1_matrices_transicion_emision.png") -> str:
        """
        Grafica las matrices estocásticas de Transición (A) y Emisión (B) con anotaciones numéricas.
        """
        fig, axes = plt.subplots(1, 2, figsize=(13, 5.2), dpi=300)

        im1 = axes[0].imshow(hmm.A, cmap="Blues", vmin=0, vmax=1)
        axes[0].set_title("Matriz de Transición de Estados ($A$)", fontsize=12.5, fontweight="bold", pad=12)
        axes[0].set_xticks(range(hmm.N))
        axes[0].set_yticks(range(hmm.N))
        axes[0].set_xticklabels(hmm.states, fontsize=10)
        axes[0].set_yticklabels(hmm.states, fontsize=10)
        axes[0].set_xlabel("Estado Siguiente ($X_{t+1}$)", fontsize=10.5, fontweight="bold")
        axes[0].set_ylabel("Estado Actual ($X_t$)", fontsize=10.5, fontweight="bold")

        for i in range(hmm.N):
            for j in range(hmm.N):
                val = hmm.A[i, j]
                text_color = "white" if val > 0.5 else "black"
                axes[0].text(j, i, f"{val:.2f}\n({val*100:.0f}%)", ha="center", va="center",
                             color=text_color, fontsize=10.5, fontweight="bold")

        fig.colorbar(im1, ax=axes[0], fraction=0.046, pad=0.04)

        im2 = axes[1].imshow(hmm.B, cmap="Oranges", vmin=0, vmax=1)
        axes[1].set_title("Matriz de Emisión de Sensores ($B$)", fontsize=12.5, fontweight="bold", pad=12)
        axes[1].set_xticks(hmm.M and range(hmm.M))
        axes[1].set_yticks(range(hmm.N))
        axes[1].set_xticklabels(hmm.observations, fontsize=9.5)
        axes[1].set_yticklabels(hmm.states, fontsize=10)
        axes[1].set_xlabel("Lectura Sensor / Velocidad ($Y_t$)", fontsize=10.5, fontweight="bold")
        axes[1].set_ylabel("Estado Real Oculto ($X_t$)", fontsize=10.5, fontweight="bold")

        for i in range(hmm.N):
            for j in range(hmm.M):
                val = hmm.B[i, j]
                text_color = "white" if val > 0.5 else "black"
                axes[1].text(j, i, f"{val:.2f}\n({val*100:.0f}%)", ha="center", va="center",
                             color=text_color, fontsize=10.5, fontweight="bold")

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
        Visualiza la jornada de 24 horas en 3 paneles sincronizados:
        1) Trayectoria oculta real vs decodificación de Viterbi (leyenda superior sin solapamiento).
        2) Distribución de probabilidad posterior suavizada P(X_t | Y_{1:T}) (Forward-Backward).
        3) Observaciones discretas captadas por los radares de velocidad.
        """
        df = sim_result["dataframe"]
        gamma = sim_result["gamma"]
        accuracy = sim_result["accuracy"]
        acc_naive = sim_result["accuracy_naive"]

        fig, (ax1, ax2, ax3) = plt.subplots(
            3, 1, figsize=(14, 9.6), dpi=300, sharex=True,
            gridspec_kw={"height_ratios": [1.25, 1.0, 0.95]}
        )

        steps = df["Paso"].values
        real_ids = df["Estado_Real_Id"].values
        viterbi_ids = df["Estado_Viterbi_Id"].values
        obs_ids = df["Observacion_Id"].values

        # Panel 1: Estado Real vs Inferencia Viterbi
        ax1.step(steps, real_ids, where="mid", label="Estado Oculto Real ($X_t$)",
                 color="#1E293B", linewidth=2.3, alpha=0.92)
        ax1.plot(steps, real_ids, "o", color="#1E293B", markersize=3.8, alpha=0.85)

        ax1.step(steps, viterbi_ids, where="mid", label="Inferencia Viterbi ($X^*_t$)",
                 color="#DC2626", linewidth=2.0, linestyle="--", alpha=0.9)
        ax1.plot(steps, viterbi_ids, "x", color="#DC2626", markersize=5.2, alpha=0.9)

        mismatch_mask = ~df["Acierto"].values
        if np.any(mismatch_mask):
            ax1.scatter(
                steps[mismatch_mask], real_ids[mismatch_mask],
                s=85, zorder=6, facecolors="none", edgecolors="#EF4444", linewidths=1.8,
                label=f"Desacuerdos ({int(np.sum(mismatch_mask))}/{len(steps)})"
            )

        switches_raw = int(np.sum(np.diff(obs_ids) != 0))
        switches_vit = int(np.sum(np.diff(viterbi_ids) != 0))
        jitter_red = (1.0 - switches_vit / max(switches_raw, 1)) * 100.0

        ax1.set_yticks([0, 1, 2])
        ax1.set_yticklabels(["Fluido (0)", "Moderado (1)", "Congestionado (2)"], fontsize=9.5, fontweight="bold")
        ax1.set_ylim(-0.32, 2.35)
        ax1.set_title(
            f"Simulación 24 Horas: Exactitud Viterbi ({accuracy*100:.2f}%) | Supresión de Oscilaciones Ruidosas: {switches_raw} → {switches_vit} (-{jitter_red:.1f}%)",
            fontsize=11.5, fontweight="bold", pad=28
        )
        ax1.grid(True, linestyle=":", alpha=0.6)
        ax1.legend(
            loc="lower center", bbox_to_anchor=(0.5, 1.01),
            ncol=3, frameon=True, framealpha=0.95, fontsize=9.5
        )

        # Panel 2: Probabilidades Posteriores (Forward-Backward)
        ax2.stackplot(
            steps,
            gamma[:, 0], gamma[:, 1], gamma[:, 2],
            labels=["$P(\\mathrm{Fluido} \\mid Y)$", "$P(\\mathrm{Moderado} \\mid Y)$", "$P(\\mathrm{Congestionado} \\mid Y)$"],
            colors=["#2ecc71", "#f39c12", "#e74c3c"],
            alpha=0.80
        )
        ax2.set_ylim(0, 1.0)
        ax2.set_ylabel("Probabilidad\nPosterior $\\gamma_t$", fontsize=9.5, fontweight="bold")
        ax2.set_title("Certidumbre Bayesiana a Posteriori por Intervalo ($\\gamma_t(i) = P(X_t = s_i \\mid Y_{1:T}, \\lambda)$)",
                      fontsize=11, fontweight="bold", pad=6)
        ax2.grid(True, linestyle=":", alpha=0.45)
        ax2.legend(loc="upper right", ncol=3, framealpha=0.92, fontsize=8.8)

        # Panel 3: Observaciones de Sensores
        colors_obs = ["#0284C7" if o == 0 else "#7C3AED" if o == 1 else "#334155" for o in obs_ids]
        ax3.plot(steps, obs_ids, color="#94A3B8", linestyle=":", linewidth=1.1, alpha=0.7)
        ax3.scatter(steps, obs_ids, c=colors_obs, s=36, alpha=0.9, edgecolors="black", linewidths=0.5, zorder=4)
        ax3.set_yticks([0, 1, 2])
        ax3.set_yticklabels(["Vel. Alta (0)", "Vel. Media (1)", "Vel. Baja (2)"], fontsize=9.5, fontweight="bold")
        ax3.set_ylim(-0.3, 2.3)
        ax3.set_title("Señal Visible Ruidosa Registrada por Radares de Velocidad ($Y_t$)",
                      fontsize=11, fontweight="bold", pad=6)
        ax3.set_xlabel("Hora del Día (96 intervalos discretos de 15 minutos)", fontsize=10.5, fontweight="bold")
        ax3.grid(True, linestyle=":", alpha=0.6)

        tick_locs = steps[::8]
        tick_labels = df["Hora"].values[::8]
        ax3.set_xticks(tick_locs)
        ax3.set_xticklabels(tick_labels, rotation=35, ha="right", fontsize=9)

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
        Demuestra la evolución de las probabilidades de estado (pi_k = pi_0 * A^k)
        convergiendo asintóticamente a la distribución estacionaria única pi*.
        """
        stationary = hmm.compute_stationary_distribution()
        initial_conditions = [
            ("Inicio 100% Fluido ($\\pi_0 = [1, 0, 0]$)", np.array([1.0, 0.0, 0.0])),
            ("Inicio 100% Congestionado ($\\pi_0 = [0, 0, 1]$)", np.array([0.0, 0.0, 1.0])),
        ]

        fig, axes = plt.subplots(1, 2, figsize=(14, 5.2), dpi=300, sharey=True)
        t_range = np.arange(steps + 1)

        for ax_idx, (title, pi_0) in enumerate(initial_conditions):
            history = np.zeros((steps + 1, hmm.N))
            history[0, :] = pi_0
            for t in range(1, steps + 1):
                history[t, :] = hmm.predict_future_distribution(pi_0, t)

            for s_idx, state_name in enumerate(hmm.states):
                color = self.colors[state_name]
                axes[ax_idx].plot(t_range, history[:, s_idx], label=f"$P(X_k = \\mathrm{{{state_name}}})$",
                                  color=color, linewidth=2.3, marker="s", markersize=4)
                axes[ax_idx].axhline(
                    stationary[s_idx], color=color, linestyle="--", alpha=0.65,
                    label=rf"$\pi^*_{{\mathrm{{{state_name}}}}} = {stationary[s_idx]:.3f}$" if ax_idx == 0 else ""
                )

            axes[ax_idx].set_title(title, fontsize=11.5, fontweight="bold")
            axes[ax_idx].set_xlabel("Paso de tiempo $k$ (Intervalos de 15 min)", fontsize=10, fontweight="bold")
            if ax_idx == 0:
                axes[ax_idx].set_ylabel("Probabilidad de Estado $P(X_k = s)$", fontsize=10, fontweight="bold")
            axes[ax_idx].set_ylim(0, 1.05)
            axes[ax_idx].grid(True, linestyle=":", alpha=0.6)
            axes[ax_idx].legend(loc="upper right", fontsize=8.8, framealpha=0.94)

        fig.suptitle(
            rf"Convergencia Ergódica a la Distribución Estacionaria $\pi^* = [{stationary[0]:.4f}, {stationary[1]:.4f}, {stationary[2]:.4f}]$",
            fontsize=12.5, fontweight="bold", y=1.02
        )
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
        Panel izquierdo: Frecuencias empíricas Monte Carlo (1,000 réplicas) vs Distribución Teórica pi*.
        Panel derecho: Histograma real comparativo de Exactitud de Viterbi vs Sensor Crudo sin memoria,
        con curva de densidad normal ajustada.
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.4), dpi=300)

        # 1. Barras Teórico vs Empírico
        x = np.arange(len(states))
        width = 0.35
        theo = mc_result["theoretical_stationary"]
        emp = mc_result["empirical_stationary"]

        ax1.bar(x - width / 2, theo * 100, width, label=r"Distribución Analítica ($\pi^*$)",
                color="#1E3A8A", edgecolor="black", alpha=0.88)
        ax1.bar(x + width / 2, emp * 100, width,
                label=f"Monte Carlo ($N={mc_result['num_replicas']}$ réplicas)",
                color="#10B981", edgecolor="black", alpha=0.88)

        for i in range(len(states)):
            ax1.text(x[i] - width / 2, theo[i] * 100 + 0.9, f"{theo[i]*100:.2f}%",
                     ha="center", fontsize=9, fontweight="bold", color="#1E3A8A")
            ax1.text(x[i] + width / 2, emp[i] * 100 + 0.9, f"{emp[i]*100:.2f}%",
                     ha="center", fontsize=9, fontweight="bold", color="#047857")

        ax1.set_xticks(x)
        ax1.set_xticklabels(states, fontsize=10, fontweight="bold")
        ax1.set_ylabel("Proporción de Tiempo (%)", fontsize=10.5, fontweight="bold")
        ax1.set_title(
            f"Ley de los Grandes Números: Teórico vs. Empírico (MAE = {mc_result['mae_stationary']:.4f})",
            fontsize=11, fontweight="bold"
        )
        ax1.set_ylim(0, max(np.max(theo), np.max(emp)) * 126)
        ax1.grid(axis="y", linestyle=":", alpha=0.6)
        ax1.legend(loc="upper right", framealpha=0.95, fontsize=9)

        # 2. Histograma Real de Exactitud en las 1,000 Réplicas
        acc_vit = mc_result["accuracies"] * 100.0
        acc_naive = mc_result["accuracies_naive"] * 100.0

        bins = np.linspace(52, 92, 21)
        ax2.hist(acc_naive, bins=bins, density=True, color="#94A3B8", edgecolor="#475569",
                 alpha=0.45, label=f"Sensor Crudo Sin Memoria ({np.mean(acc_naive):.1f}%)")
        ax2.hist(acc_vit, bins=bins, density=True, color="#2563EB", edgecolor="#1E3A8A",
                 alpha=0.68, label=f"Decodificación HMM Viterbi ({np.mean(acc_vit):.1f}%)")

        # Curva Gaussiana ajustada sobre Viterbi
        mu, sigma = float(np.mean(acc_vit)), float(np.std(acc_vit))
        x_grid = np.linspace(52, 92, 250)
        pdf = (1.0 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_grid - mu) / sigma) ** 2)
        ax2.plot(x_grid, pdf, color="#DC2626", linewidth=2.2, label=f"Ajuste Normal ($\\mu={mu:.1f}\\%, \\sigma={sigma:.1f}\\%$)")
        ax2.axvline(mu, color="#DC2626", linestyle="--", linewidth=1.8)
        ax2.axvline(float(np.mean(acc_naive)), color="#475569", linestyle=":", linewidth=1.8)

        ax2.set_title("Distribución de Exactitud en 1,000 Réplicas (96,000 Pasos)", fontsize=11, fontweight="bold")
        ax2.set_xlabel("Exactitud de Reconstrucción del Estado Oculto (%)", fontsize=10.5, fontweight="bold")
        ax2.set_ylabel("Densidad de Probabilidad", fontsize=10.5, fontweight="bold")
        ax2.set_xlim(52, 92)
        ax2.grid(True, linestyle=":", alpha=0.6)
        ax2.legend(loc="upper left", fontsize=8.5, framealpha=0.95)

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
        Visualiza el impacto y resiliencia del corredor ante un accidente vial (pasos 32-44)
        junto con la curva de probabilidad posterior de congestión.
        """
        df = incident_result["dataframe"]
        start = incident_result["incident_start"]
        end = incident_result["incident_end"]

        fig, (ax1, ax2) = plt.subplots(
            2, 1, figsize=(14, 6.8), dpi=300, sharex=True,
            gridspec_kw={"height_ratios": [1.25, 0.9]}
        )

        steps = df["Paso"].values
        real_ids = df["Estado_Real_Id"].values
        viterbi_ids = df["Estado_Viterbi_Id"].values
        prob_cong = df["Prob_Congestionado"].values

        ax1.axvspan(start, end, color="#EF4444", alpha=0.18, label=f"Siniestro Vial Activo (14:00 - 17:00 | Pasos {start}-{end})")
        ax1.step(steps, real_ids, where="mid", label="Estado Oculto Real", color="#1E293B", linewidth=2.2)
        ax1.plot(steps, real_ids, "o", color="#1E293B", markersize=3.8)
        ax1.step(steps, viterbi_ids, where="mid", label="Inferencia Viterbi", color="#EA580C", linestyle="--", linewidth=2.0)
        ax1.plot(steps, viterbi_ids, "^", color="#EA580C", markersize=4.8)

        ax1.set_yticks([0, 1, 2])
        ax1.set_yticklabels(["Fluido", "Moderado", "Congestionado"], fontsize=10, fontweight="bold")
        ax1.set_ylim(-0.3, 2.35)
        ax1.set_title("Respuesta ante Perturbación Exógena (Accidente Vial) y Disipación de Cola",
                      fontsize=12, fontweight="bold", pad=28)
        ax1.grid(True, linestyle=":", alpha=0.6)
        ax1.legend(loc="lower center", bbox_to_anchor=(0.5, 1.01), ncol=3, framealpha=0.95, fontsize=9.2)

        ax2.axvspan(start, end, color="#EF4444", alpha=0.18)
        ax2.fill_between(steps, 0, prob_cong * 100, color="#EF4444", alpha=0.35)
        ax2.plot(steps, prob_cong * 100, color="#B91C1C", linewidth=2.0, label="$P(X_t = \\mathrm{Congestionado} \\mid Y_{1:T})$")
        ax2.axhline(50, color="#64748B", linestyle=":", linewidth=1.2, label="Umbral de Alerta ITS (50%)")
        ax2.set_ylim(0, 114)
        ax2.set_ylabel("Prob. Congestión (%)", fontsize=9.5, fontweight="bold")
        ax2.set_xlabel("Hora del Día (Intervalos de 15 min)", fontsize=10.5, fontweight="bold")
        ax2.grid(True, linestyle=":", alpha=0.6)
        ax2.legend(loc="upper left", ncol=2, fontsize=9, framealpha=0.95)

        tick_locs = steps[::8]
        tick_labels = df["Hora"].values[::8]
        ax2.set_xticks(tick_locs)
        ax2.set_xticklabels(tick_labels, rotation=35, ha="right", fontsize=9)

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
        Grafica la matriz de confusión normalizada por fila (Sensibilidad / Recall por estado real),
        mostrando conteo exacto y porcentaje de fila en total coherencia con las tablas del informe.
        """
        fig, ax = plt.subplots(figsize=(6.6, 5.4), dpi=300)

        row_sums = np.maximum(cm.sum(axis=1, keepdims=True), 1)
        cm_row_pct = (cm / row_sums) * 100.0

        im = ax.imshow(cm_row_pct, cmap="Blues", vmin=0, vmax=100)
        ax.set_title("Matriz de Confusión: Real vs. Viterbi\n(Conteo y % Sensibilidad por Fila)",
                     fontsize=11.5, fontweight="bold", pad=12)
        ax.set_xticks(range(len(states)))
        ax.set_yticks(range(len(states)))
        ax.set_xticklabels(states, fontsize=10, fontweight="bold")
        ax.set_yticklabels([f"{s}\n(n={int(row_sums[i,0])})" for i, s in enumerate(states)], fontsize=9.5, fontweight="bold")
        ax.set_xlabel("Estado Inferido por Viterbi ($X^*_t$)", fontsize=10.5, fontweight="bold")
        ax.set_ylabel("Estado Oculto Real ($X_t$)", fontsize=10.5, fontweight="bold")

        for i in range(len(states)):
            for j in range(len(states)):
                count = int(cm[i, j])
                pct = cm_row_pct[i, j]
                color = "white" if pct > 50.0 else "black"
                ax.text(j, i, f"{count}\n({pct:.1f}%)", ha="center", va="center",
                        color=color, fontsize=10.5, fontweight="bold")

        cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label("Sensibilidad por Estado Real (%)", fontsize=9.5)

        plt.tight_layout()
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, bbox_inches="tight")
        plt.close()
        return filepath
