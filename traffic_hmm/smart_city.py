"""
Módulo de Ciudad Inteligente y Analítica de Transporte Urbano con HMM.
Actividad Didáctica 2 - Módulo 2: Simulación de Procesos Estocásticos.
Institución Universitaria Digital de Antioquia (IU Digital).
"""

from typing import Dict, List, Any, Tuple, Optional
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.animation import FuncAnimation
import os

from .model import TrafficHMM


class SmartCityTrafficAnalyzer:
    """
    Motor de análisis de transporte, métricas de congestión, rutas alternativas
    e impacto ambiental para centros de control de tráfico y ciudades inteligentes.
    """

    def __init__(self, hmm: Optional[TrafficHMM] = None, corridor_length_km: float = 15.0):
        self.hmm = hmm or TrafficHMM.create_prompt_model()
        self.corridor_length_km = corridor_length_km
        self.free_flow_speed_kmh = 90.0  # Velocidad de referencia para flujo libre

    def simulate_day(
        self,
        num_steps: int = 48,
        seed: int = 42,
        step_duration_min: int = 30,
        start_hour: int = 0,
    ) -> pd.DataFrame:
        """
        Simula una jornada completa de 48 mediciones (cada 30 minutos = 24 horas),
        generando estados ocultos, observaciones discretas y velocidades continuas en km/h.
        """
        states_idx, obs_idx, speeds, timestamps = self.hmm.simulate_with_speeds(
            T=num_steps, seed=seed, step_duration_min=step_duration_min, start_hour=start_hour
        )

        # Inferencia mediante algoritmo de Viterbi
        viterbi_states, _ = self.hmm.viterbi(obs_idx)
        gamma, posterior_states, _ = self.hmm.forward_backward(obs_idx)

        # Asignación de semáforo urbano
        # 0: Fluido -> Verde 🟢, 1: Moderado -> Amarillo 🟡, 2: Congestionado -> Rojo 🔴
        semaforo_icons = {0: "🟢", 1: "🟡", 2: "🔴"}
        semaforo_names = {0: "Verde", 1: "Amarillo", 2: "Rojo"}

        df = pd.DataFrame({
            "Paso": np.arange(num_steps),
            "Hora": timestamps,
            "Estado_Real_Id": states_idx,
            "Estado_Real": [self.hmm.idx_to_state[s] for s in states_idx],
            "Observacion_Id": obs_idx,
            "Observacion": [self.hmm.idx_to_obs[o] for o in obs_idx],
            "Velocidad_kmh": speeds,
            "Estado_Viterbi_Id": viterbi_states,
            "Estado_Viterbi": [self.hmm.idx_to_state[s] for s in viterbi_states],
            "Estado_Posterior_Id": posterior_states,
            "Estado_Posterior": [self.hmm.idx_to_state[s] for s in posterior_states],
            "Prob_Fluido": np.round(gamma[:, 0], 4),
            "Prob_Moderado": np.round(gamma[:, 1], 4),
            "Prob_Congestionado": np.round(gamma[:, 2], 4),
            "Semaforo_Icono": [semaforo_icons[s] for s in viterbi_states],
            "Semaforo_Color": [semaforo_names[s] for s in viterbi_states],
        })

        # Tiempo de viaje estimado en el corredor (minutos)
        df["Tiempo_Viaje_Min"] = np.round((self.corridor_length_km / np.maximum(df["Velocidad_kmh"], 1.0)) * 60.0, 1)

        return df

    def calculate_transport_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcula las 4 métricas clave de transporte urbano requeridas:
          1. Horas pico identificadas
          2. Tiempo promedio en congestión
          3. Velocidad promedio por estado
          4. Índice de congestión (0-100)
        """
        step_min = 30.0

        # 1. Identificación de horas pico (intervalos donde el estado inferido es Congestionado o velocidad < 40 km/h)
        congested_mask = (df["Estado_Viterbi_Id"] == 2) | (df["Velocidad_kmh"] < 40.0)
        congested_steps = df[congested_mask]

        peak_hours_ranges = []
        if not congested_steps.empty:
            indices = congested_steps.index.tolist()
            groups = []
            current_group = [indices[0]]
            for idx in indices[1:]:
                if idx == current_group[-1] + 1:
                    current_group.append(idx)
                else:
                    groups.append(current_group)
                    current_group = [idx]
            groups.append(current_group)

            for g in groups:
                h_start = df.loc[g[0], "Hora"]
                end_idx = min(len(df) - 1, g[-1] + 1)
                h_end = df.loc[end_idx, "Hora"]
                duration_h = len(g) * 0.5
                avg_speed = float(df.loc[g, "Velocidad_kmh"].mean())
                peak_hours_ranges.append({
                    "rango": f"{h_start} - {h_end}",
                    "duracion_horas": duration_h,
                    "velocidad_media_kmh": round(avg_speed, 1),
                })

        # 2. Tiempo total y porcentaje en congestión
        num_congested_steps = int(congested_mask.sum())
        total_congestion_hours = (num_congested_steps * step_min) / 60.0
        pct_congestion_day = (total_congestion_hours / 24.0) * 100.0

        # 3. Velocidad promedio por estado operacional
        speed_by_state = {}
        for s_idx, s_name in self.hmm.idx_to_state.items():
            subset = df[df["Estado_Viterbi_Id"] == s_idx]
            if not subset.empty:
                speed_by_state[s_name] = round(float(subset["Velocidad_kmh"].mean()), 2)
            else:
                speed_by_state[s_name] = 0.0

        # 4. Índice de congestión (0 - 100)
        # Ic = 100 * (1 - v_media / v_libre)
        mean_operating_speed = float(df["Velocidad_kmh"].mean())
        congestion_index = max(0.0, min(100.0, 100.0 * (1.0 - mean_operating_speed / self.free_flow_speed_kmh)))

        return {
            "velocidad_promedio_general_kmh": round(mean_operating_speed, 2),
            "velocidad_promedio_por_estado": speed_by_state,
            "horas_congestión_total": round(total_congestion_hours, 1),
            "porcentaje_dia_congestion": round(pct_congestion_day, 1),
            "horas_pico_identificadas": peak_hours_ranges,
            "indice_congestion_0_100": round(congestion_index, 2),
            "tiempo_promedio_viaje_min": round(float(df["Tiempo_Viaje_Min"].mean()), 1),
            "tiempo_maximo_viaje_min": round(float(df["Tiempo_Viaje_Min"].max()), 1),
        }

    def predict_future_traffic(
        self,
        current_state_idx: int,
        horizons_hours: Optional[List[int]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Predice el estado del tráfico para horizontes futuros (ej. 1h, 2h, 4h, 6h).
        """
        if horizons_hours is None:
            horizons_hours = [1, 2, 3, 4, 6]

        predictions = []
        for h in horizons_hours:
            pred = self.hmm.predict_next_hours(current_state_idx, hours=h, step_duration_min=30)
            # Velocidad esperada ponderada
            # Fluido: ~90 km/h, Moderado: ~60 km/h, Congestionado: ~25 km/h
            speeds_ref = [90.0, 60.0, 25.0]
            expected_speed = float(np.dot(pred["probability_distribution"], speeds_ref))
            predictions.append({
                "horas_adelante": h,
                "pasos_adelante": pred["steps_ahead"],
                "estado_mas_probable": pred["most_likely_state"],
                "probabilidad_estado": round(float(np.max(pred["probability_distribution"])) * 100.0, 1),
                "distribucion": {
                    s: round(float(p) * 100.0, 1) for s, p in pred["state_probabilities"].items()
                },
                "velocidad_esperada_kmh": round(expected_speed, 1),
            })
        return predictions

    def identify_congestion_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Identifica patrones temporales: ¿cuándo es más probable la congestión?
        """
        # Franjas horarias
        # Madrugada: 00:00 - 06:00 (pasos 0 a 11)
        # Mañana: 06:00 - 12:00 (pasos 12 a 23)
        # Tarde: 12:00 - 18:00 (pasos 24 a 35)
        # Noche: 18:00 - 24:00 (pasos 36 a 47)
        periods = {
            "Madrugada (00:00 - 06:00)": df.iloc[0:12],
            "Mañana (06:00 - 12:00)": df.iloc[12:24],
            "Tarde (12:00 - 18:00)": df.iloc[24:36],
            "Noche (18:00 - 24:00)": df.iloc[36:48],
        }

        period_analysis = {}
        max_period = ""
        max_prob = -1.0

        for name, sub_df in periods.items():
            if not sub_df.empty:
                prob_cong = float(sub_df["Prob_Congestionado"].mean()) * 100.0
                avg_spd = float(sub_df["Velocidad_kmh"].mean())
                cong_count = int((sub_df["Estado_Viterbi_Id"] == 2).sum())
                period_analysis[name] = {
                    "probabilidad_media_congestion_pct": round(prob_cong, 1),
                    "velocidad_promedio_kmh": round(avg_spd, 1),
                    "intervalos_congestionados": cong_count,
                    "tiempo_en_congestion_horas": round(cong_count * 0.5, 1),
                }
                if prob_cong > max_prob:
                    max_prob = prob_cong
                    max_period = name

        # Tiempos de permanencia analíticos (Holding Times)
        holding_times = self.hmm.expected_holding_times()

        return {
            "franja_mas_critica": max_period,
            "probabilidad_maxima_congestion_pct": round(max_prob, 1),
            "analisis_por_franja": period_analysis,
            "tiempo_medio_permanencia_congestion_horas": round(holding_times.get("Tráfico Congestionado", 2.0) * 0.5, 2),
            "probabilidad_transicion_a_congestion_desde_moderado_pct": round(self.hmm.A[1, 2] * 100.0, 1),
            "probabilidad_transicion_a_congestion_desde_fluido_pct": round(self.hmm.A[0, 2] * 100.0, 1),
        }

    def suggest_alternative_routes(
        self,
        current_state_str: str,
        current_speed_kmh: float,
    ) -> Dict[str, Any]:
        """
        Genera rutas alternativas sugeridas cuando se detecta o predice congestión.
        """
        is_congested = "Congestionado" in current_state_str or current_speed_kmh < 40.0
        corridor_time = (self.corridor_length_km / max(current_speed_kmh, 5.0)) * 60.0

        routes = [
            {
                "nombre": "Ruta Principal (Corredor Actual)",
                "distancia_km": self.corridor_length_km,
                "velocidad_estimada_kmh": round(current_speed_kmh, 1),
                "tiempo_estimado_min": round(corridor_time, 1),
                "recomendada": not is_congested,
                "motivo": "Flujo adecuado" if not is_congested else "Vía saturada con demoras críticas",
            },
            {
                "nombre": "Ruta Alterna 1 (Vía Perimetral / Av. Regional)",
                "distancia_km": 18.5,
                "velocidad_estimada_kmh": 65.0,
                "tiempo_estimado_min": round((18.5 / 65.0) * 60.0, 1),
                "recomendada": is_congested,
                "ahorro_minutos": round(max(0.0, corridor_time - (18.5 / 65.0) * 60.0), 1),
                "motivo": "Mayor capacidad y flujo continuo de velocidad media",
            },
            {
                "nombre": "Ruta Alterna 2 (Corredor Multimodal / Transporte Masivo)",
                "distancia_km": 14.0,
                "velocidad_estimada_kmh": 38.0,
                "tiempo_estimado_min": 22.0,  # Tiempo comercial programado
                "recomendada": is_congested and corridor_time > 25.0,
                "ahorro_minutos": round(max(0.0, corridor_time - 22.0), 1),
                "motivo": "Carril exclusivo segregado, inmune a la congestión de superficie",
            },
        ]

        best_alternative = None
        if is_congested:
            alternatives = [r for r in routes if r["nombre"] != "Ruta Principal (Corredor Actual)"]
            best_alternative = min(alternatives, key=lambda x: x["tiempo_estimado_min"])

        return {
            "alerta_congestion_activa": is_congested,
            "tiempo_ruta_principal_min": round(corridor_time, 1),
            "ruta_optima_sugerida": best_alternative["nombre"] if best_alternative else "Ruta Principal",
            "ahorro_tiempo_maximo_min": best_alternative["ahorro_minutos"] if best_alternative else 0.0,
            "catalogo_rutas": routes,
        }

    def analyze_environmental_impact(
        self,
        df: pd.DataFrame,
        daily_fleet_volume: int = 15000,
    ) -> Dict[str, Any]:
        """
        Análisis de impacto ambiental: cálculo de emisiones de CO2 y consumo de combustible.
        Factores de emisión según EMEP/EEA e IPCC para tráfico urbano:
          - Fluido (90 km/h): 110 g CO2/km | Consumo: 5.5 L / 100 km
          - Moderado (60 km/h): 155 g CO2/km | Consumo: 7.8 L / 100 km
          - Congestionado (25 km/h): 275 g CO2/km | Consumo: 13.8 L / 100 km (+150% emisiones por ralentí)
        """
        factors_co2_g_per_km = {0: 110.0, 1: 155.0, 2: 275.0}
        factors_fuel_l_per_100km = {0: 5.5, 1: 7.8, 2: 13.8}

        df["Factor_CO2_g_km"] = df["Estado_Viterbi_Id"].map(factors_co2_g_per_km)
        df["Factor_Combustible_L_100km"] = df["Estado_Viterbi_Id"].map(factors_fuel_l_per_100km)

        # Emisión media ponderada por paso de tiempo para 1 vehículo en el corredor (15 km)
        emission_per_veh_kg = (df["Factor_CO2_g_km"] * self.corridor_length_km) / 1000.0
        fuel_per_veh_l = (df["Factor_Combustible_L_100km"] * self.corridor_length_km) / 100.0

        # Para toda la flota diaria (distribuida en los 48 intervalos)
        veh_per_step = daily_fleet_volume / len(df)
        total_co2_kg = float(np.sum(emission_per_veh_kg * veh_per_step))
        total_fuel_liters = float(np.sum(fuel_per_veh_l * veh_per_step))

        # Escenario de referencia ideal (si el 100% del día hubiese sido fluido)
        ideal_co2_kg = float(len(df) * (110.0 * self.corridor_length_km / 1000.0) * veh_per_step)
        ideal_fuel_liters = float(len(df) * (5.5 * self.corridor_length_km / 100.0) * veh_per_step)

        excess_co2_kg = max(0.0, total_co2_kg - ideal_co2_kg)
        excess_fuel_liters = max(0.0, total_fuel_liters - ideal_fuel_liters)

        return {
            "volumen_flota_vehiculos_dia": daily_fleet_volume,
            "emisiones_totales_co2_toneladas": round(total_co2_kg / 1000.0, 2),
            "consumo_total_combustible_litros": round(total_fuel_liters, 1),
            "exceso_co2_por_congestion_toneladas": round(excess_co2_kg / 1000.0, 2),
            "exceso_combustible_desperdiciado_litros": round(excess_fuel_liters, 1),
            "incremento_porcentual_emisiones_vs_ideal": round((excess_co2_kg / ideal_co2_kg) * 100.0, 1),
            "costo_economico_combustible_desperdiciado_cop": round(excess_fuel_liters * 16000.0, 0),  # COP ~16.000 / galón o litro equivalente
        }


class SmartCityVisualizer:
    """
    Generador de gráficos de ciudad inteligente: velocidad con semáforo, mapa de calor,
    dashboard consolidado y animación opcional del tráfico vehicular.
    """

    def __init__(self, output_dir: str = "results"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def plot_speed_and_traffic_lights(self, df: pd.DataFrame, filename: str = "fig_velocidad_semaforo.png") -> str:
        """
        Gráfico 1: Curva de velocidad a lo largo del día con bandas operativas y semáforo por período.
        """
        fig, (ax_speed, ax_lights) = plt.subplots(
            nrows=2, ncols=1, figsize=(14, 7), sharex=True, gridspec_kw={"height_ratios": [3.5, 1]}
        )

        x = np.arange(len(df))
        speeds = df["Velocidad_kmh"].values

        # Bandas de velocidad de referencia
        ax_speed.axhspan(80, 105, color="#DCFCE7", alpha=0.5, label="Velocidad Alta (80-100 km/h) - Fluido")
        ax_speed.axhspan(40, 80, color="#FEF3C7", alpha=0.5, label="Velocidad Media (40-80 km/h) - Moderado")
        ax_speed.axhspan(0, 40, color="#FEE2E2", alpha=0.5, label="Velocidad Baja (0-40 km/h) - Congestionado")

        # Línea de velocidad continua
        ax_speed.plot(x, speeds, color="#1E3A8A", linewidth=2.2, marker="o", markersize=4, label="Velocidad Observada en Sensor")
        v_mean = float(np.mean(speeds))
        ax_speed.axhline(v_mean, color="#B91C1C", linestyle="--", linewidth=1.5, label=f"Velocidad Promedio ({v_mean:.1f} km/h)")

        ax_speed.set_title("Velocidad Promedio a lo Largo del Día (48 Intervalos de 30 Minutos)", fontsize=13, fontweight="bold", pad=10)
        ax_speed.set_ylabel("Velocidad (km/h)", fontsize=11)
        ax_speed.set_ylim(0, 105)
        ax_speed.legend(loc="upper right", framealpha=0.9, fontsize=9)
        ax_speed.grid(True, linestyle=":", alpha=0.6)

        # Semáforo urbano cronológico
        color_map = {0: "#16A34A", 1: "#EAB308", 2: "#DC2626"}
        for i, s_idx in enumerate(df["Estado_Viterbi_Id"].values):
            ax_lights.bar(i, 1, width=0.85, color=color_map[s_idx], edgecolor="none", alpha=0.85)

        ax_lights.set_title("Semáforo Urbano por Período (Verde: Fluido  |  Amarillo: Moderado  |  Rojo: Congestionado)", fontsize=11, fontweight="bold", pad=6)
        ax_lights.set_yticks([])
        ax_lights.set_ylabel("Semáforo", fontsize=10)
        ax_lights.set_xlim(-0.5, len(df) - 0.5)

        # Eje X con marcas cada 4 pasos (cada 2 horas)
        tick_steps = np.arange(0, len(df), 4)
        ax_lights.set_xticks(tick_steps)
        ax_lights.set_xticklabels([df.loc[t, "Hora"] for t in tick_steps], rotation=45, ha="right", fontsize=9)
        ax_lights.set_xlabel("Hora del Día (Formato 24h)", fontsize=11)

        plt.tight_layout()
        out_path = os.path.join(self.output_dir, filename)
        plt.savefig(out_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        return out_path

    def plot_hourly_heatmap(self, df: pd.DataFrame, filename: str = "fig_mapa_calor_estado_hora.png") -> str:
        """
        Gráfico 2: Mapa de calor del estado y probabilidades del tráfico por hora.
        """
        # Matriz 3 filas (Estados) x 48 columnas (Intervalos)
        heatmap_data = np.vstack([
            df["Prob_Fluido"].values,
            df["Prob_Moderado"].values,
            df["Prob_Congestionado"].values,
        ])

        fig, ax = plt.subplots(figsize=(15, 4.5))
        cax = ax.imshow(heatmap_data, cmap="YlOrRd", aspect="auto", vmin=0.0, vmax=1.0)

        cbar = fig.colorbar(cax, orientation="horizontal", pad=0.25, shrink=0.5)
        cbar.set_label(r"Probabilidad a Posteriori Forward-Backward $\gamma_t(i)$", fontsize=10)

        ax.set_yticks([0, 1, 2])
        ax.set_yticklabels(["Tráfico Fluido", "Tráfico Moderado", "Tráfico Congestionado"], fontsize=10, fontweight="bold")

        tick_steps = np.arange(0, len(df), 4)
        ax.set_xticks(tick_steps)
        ax.set_xticklabels([df.loc[t, "Hora"] for t in tick_steps], rotation=45, ha="right", fontsize=9)
        ax.set_xlabel("Hora del Día (30 min / intervalo)", fontsize=11)
        ax.set_title("Mapa de Calor: Dinámica Temporal del Estado del Tráfico por Hora", fontsize=13, fontweight="bold", pad=12)

        plt.tight_layout()
        out_path = os.path.join(self.output_dir, filename)
        plt.savefig(out_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        return out_path

    def plot_smart_city_dashboard(
        self,
        df: pd.DataFrame,
        metrics: Dict[str, Any],
        patterns: Dict[str, Any],
        predictions: List[Dict[str, Any]],
        routes: Dict[str, Any],
        env: Dict[str, Any],
        filename: str = "fig_dashboard_ciudad_inteligente.png",
    ) -> str:
        """
        Gráfico 3: Dashboard Integrado de Ciudad Inteligente con múltiples métricas, semáforo,
        panel de KPIs, pronóstico horario y recomendación de rutas.
        """
        fig = plt.figure(figsize=(18, 12), constrained_layout=True)
        gs = fig.add_gridspec(nrows=3, ncols=3, height_ratios=[1.2, 1.0, 1.0])

        # --- Subplot 1: Curva de Velocidad y Semáforo (Ocupa 2 columnas superiores) ---
        ax1 = fig.add_subplot(gs[0, :2])
        x = np.arange(len(df))
        speeds = df["Velocidad_kmh"].values
        ax1.axhspan(80, 105, color="#DCFCE7", alpha=0.5)
        ax1.axhspan(40, 80, color="#FEF3C7", alpha=0.5)
        ax1.axhspan(0, 40, color="#FEE2E2", alpha=0.5)
        ax1.plot(x, speeds, color="#1E3A8A", linewidth=2.0, marker="o", markersize=3.5, label="Velocidad (km/h)")
        ax1.axhline(metrics["velocidad_promedio_general_kmh"], color="#B91C1C", linestyle="--",
                    label=f"Promedio: {metrics['velocidad_promedio_general_kmh']} km/h")
        ax1.set_ylabel("Velocidad (km/h)", fontsize=10, fontweight="bold")
        ax1.set_ylim(0, 105)
        ax1.set_title("1. Velocidad Continua del Corredor y Régimen Operativo", fontsize=11, fontweight="bold", color="#1E3A8A")
        ax1.grid(True, linestyle=":", alpha=0.6)
        ax1.legend(loc="upper right", fontsize=8)

        # Semáforo en la base de ax1
        color_map = {0: "#16A34A", 1: "#EAB308", 2: "#DC2626"}
        for i, s_idx in enumerate(df["Estado_Viterbi_Id"].values):
            ax1.scatter(i, 5, color=color_map[s_idx], s=35, zorder=5)
        ax1.set_xticks(np.arange(0, len(df), 4))
        ax1.set_xticklabels([df.loc[t, "Hora"] for t in np.arange(0, len(df), 4)], fontsize=8)

        # --- Subplot 2: Tarjetas de KPI Urbanos (Columna superior derecha) ---
        ax_kpi = fig.add_subplot(gs[0, 2])
        ax_kpi.axis("off")
        ax_kpi.set_title("2. Indicadores Clave de Transporte (KPI)", fontsize=11, fontweight="bold", color="#1E3A8A")

        kpi_text = (
            f"• Índice de Congestión (0-100):  {metrics['indice_congestion_0_100']} / 100\n"
            f"• Velocidad Media General:       {metrics['velocidad_promedio_general_kmh']} km/h\n"
            f"• Tiempo Total en Congestión:    {metrics['horas_congestión_total']} h ({metrics['porcentaje_dia_congestion']}% del día)\n"
            f"• Tiempo Medio de Viaje:         {metrics['tiempo_promedio_viaje_min']} min (Pico: {metrics['tiempo_maximo_viaje_min']} min)\n\n"
            f"• Velocidad por Estado:\n"
            f"    - Fluido:         {metrics['velocidad_promedio_por_estado'].get('Tráfico Fluido', 0)} km/h\n"
            f"    - Moderado:       {metrics['velocidad_promedio_por_estado'].get('Tráfico Moderado', 0)} km/h\n"
            f"    - Congestionado:  {metrics['velocidad_promedio_por_estado'].get('Tráfico Congestionado', 0)} km/h\n\n"
            f"• Horas Pico Detectadas:\n"
        )
        for p in metrics["horas_pico_identificadas"][:2]:
            kpi_text += f"    - {p['rango']} ({p['duracion_horas']} h, ~{p['velocidad_media_kmh']} km/h)\n"

        bbox_props = dict(boxstyle="round,pad=0.8", facecolor="#F8FAFC", edgecolor="#CBD5E1", linewidth=1.5)
        ax_kpi.text(0.02, 0.95, kpi_text, fontsize=9.2, verticalalignment="top", fontfamily="monospace", bbox=bbox_props)

        # --- Subplot 3: Mapa de Calor de Probabilidades por Hora (Fila 2, Col 0 y 1) ---
        ax3 = fig.add_subplot(gs[1, :2])
        heat_data = np.vstack([df["Prob_Fluido"], df["Prob_Moderado"], df["Prob_Congestionado"]])
        im = ax3.imshow(heat_data, cmap="YlOrRd", aspect="auto", vmin=0, vmax=1)
        ax3.set_yticks([0, 1, 2])
        ax3.set_yticklabels(["Fluido", "Moderado", "Congestionado"], fontsize=9, fontweight="bold")
        ax3.set_xticks(np.arange(0, len(df), 4))
        ax3.set_xticklabels([df.loc[t, "Hora"] for t in np.arange(0, len(df), 4)], fontsize=8)
        ax3.set_title("3. Mapa de Calor Horario de Probabilidad de Congestión", fontsize=11, fontweight="bold", color="#1E3A8A")
        fig.colorbar(im, ax=ax3, orientation="vertical", shrink=0.8, pad=0.02)

        # --- Subplot 4: Análisis de Impacto Ambiental (Fila 2, Col 2) ---
        ax_env = fig.add_subplot(gs[1, 2])
        ax_env.axis("off")
        ax_env.set_title("4. Impacto Ambiental y Huella de Carbono", fontsize=11, fontweight="bold", color="#1E3A8A")

        env_text = (
            f"• Flota Diaria Estimada:      {env['volumen_flota_vehiculos_dia']:,} veh/día\n"
            f"• Emisiones Totales CO2:      {env['emisiones_totales_co2_toneladas']} Toneladas/día\n"
            f"• Consumo Total Combustible:  {env['consumo_total_combustible_litros']:,} Litros\n\n"
            f"• EXCESO POR CONGESTIÓN:\n"
            f"    - CO2 Innecesario:         {env['exceso_co2_por_congestion_toneladas']} Toneladas (+{env['incremento_porcentual_emisiones_vs_ideal']}%)\n"
            f"    - Combustible Desperdiciado: {env['exceso_combustible_desperdiciado_litros']:,} Litros\n"
            f"    - Costo Económico Estimado: COP ${env['costo_economico_combustible_desperdiciado_cop']:,.0f}\n"
        )
        bbox_env = dict(boxstyle="round,pad=0.8", facecolor="#F0FDF4", edgecolor="#86EFAC", linewidth=1.5)
        ax_env.text(0.02, 0.95, env_text, fontsize=9.2, verticalalignment="top", fontfamily="monospace", bbox=bbox_env)

        # --- Subplot 5: Predicción Próximas Horas (Fila 3, Col 0 y 1) ---
        ax_pred = fig.add_subplot(gs[2, :2])
        h_labels = [f"+{p['horas_adelante']}h" for p in predictions]
        p_fluido = [p["distribucion"]["Tráfico Fluido"] for p in predictions]
        p_mod = [p["distribucion"]["Tráfico Moderado"] for p in predictions]
        p_cong = [p["distribucion"]["Tráfico Congestionado"] for p in predictions]

        bar_x = np.arange(len(h_labels))
        width = 0.25
        ax_pred.bar(bar_x - width, p_fluido, width, label="Fluido (%)", color="#16A34A", alpha=0.85)
        ax_pred.bar(bar_x, p_mod, width, label="Moderado (%)", color="#EAB308", alpha=0.85)
        ax_pred.bar(bar_x + width, p_cong, width, label="Congestionado (%)", color="#DC2626", alpha=0.85)

        ax_pred.set_xticks(bar_x)
        ax_pred.set_xticklabels(h_labels, fontsize=9, fontweight="bold")
        ax_pred.set_ylabel("Probabilidad Estimada (%)", fontsize=9)
        ax_pred.set_ylim(0, 100)
        ax_pred.set_title("5. Pronóstico del Tráfico para las Próximas Horas (Cadena de Markov)", fontsize=11, fontweight="bold", color="#1E3A8A")
        ax_pred.grid(True, linestyle=":", alpha=0.6)
        ax_pred.legend(loc="upper right", fontsize=8)

        # --- Subplot 6: Rutas Alternativas Sugeridas (Fila 3, Col 2) ---
        ax_route = fig.add_subplot(gs[2, 2])
        ax_route.axis("off")
        ax_route.set_title("6. Rutas Alternativas y Navegación Inteligente", fontsize=11, fontweight="bold", color="#1E3A8A")

        alert_color = "#FEF2F2" if routes["alerta_congestion_activa"] else "#F0FDF4"
        edge_color = "#F87171" if routes["alerta_congestion_activa"] else "#86EFAC"

        route_text = (
            f"• Estado Alerta: {'[ALERTA] CONGESTION ACTIVA' if routes['alerta_congestion_activa'] else '[OK] FLUJO NORMAL'}\n"
            f"• Ruta Óptima Sugerida: {routes['ruta_optima_sugerida']}\n"
            f"• Ahorro Máximo Estimado: {routes['ahorro_tiempo_maximo_min']} minutos\n\n"
            f"• Comparativa de Tiempos de Viaje:\n"
        )
        for r in routes["catalogo_rutas"]:
            flag = "★ " if r["recomendada"] else "  "
            route_text += f"{flag}{r['nombre'][:24]}: {r['tiempo_estimado_min']} min (~{r['velocidad_estimada_kmh']} km/h)\n"

        bbox_route = dict(boxstyle="round,pad=0.8", facecolor=alert_color, edgecolor=edge_color, linewidth=1.5)
        ax_route.text(0.02, 0.95, route_text, fontsize=9.2, verticalalignment="top", fontfamily="monospace", bbox=bbox_route)

        fig.suptitle(
            "CENTRO INTEGRADO DE CIUDAD INTELIGENTE — MODELO OCULTO DE MARKOV (HMM)\n"
            "Monitoreo, Predicción de Velocidades, Semáforos e Impacto Ambiental en Corredor Vial Urbano",
            fontsize=13, fontweight="bold", color="#0F172A", y=0.99
        )

        out_path = os.path.join(self.output_dir, filename)
        plt.savefig(out_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        return out_path

    def generate_vehicular_animation(
        self,
        df: pd.DataFrame,
        filename: str = "animacion_flujo_trafico.gif",
        num_frames: int = 48,
    ) -> str:
        """
        Gráfico 4: Animación opcional del flujo vehicular en el corredor según el semáforo y velocidad.
        """
        fig, ax = plt.subplots(figsize=(12, 3))
        corridor_len = 15.0  # km

        # Generar posiciones iniciales de 20 vehículos distribuidos
        num_vehicles = 20
        veh_positions = np.linspace(0.5, corridor_len - 0.5, num_vehicles)

        color_map = {0: "#16A34A", 1: "#EAB308", 2: "#DC2626"}

        def update(frame):
            ax.clear()
            row = df.iloc[frame]
            state_id = row["Estado_Viterbi_Id"]
            speed = row["Velocidad_kmh"]
            hora = row["Hora"]
            color = color_map[state_id]

            # Actualizar posiciones de vehículos según velocidad del intervalo
            # Desplazamiento proporcional a velocidad
            step_shift = (speed / 100.0) * 0.4
            nonlocal veh_positions
            veh_positions = (veh_positions + step_shift) % corridor_len

            # Dibujar carretera (2 carriles)
            ax.fill_between([0, corridor_len], -1.0, 1.0, color="#334155", alpha=0.9)
            ax.axhline(0, color="#F8FAFC", linestyle="--", linewidth=1.5, alpha=0.7)

            # Dibujar vehículos
            for p in veh_positions:
                ax.plot(p, 0.4, marker="s", markersize=10, color=color, markeredgecolor="white")
                ax.plot((p + 1.2) % corridor_len, -0.4, marker="s", markersize=10, color=color, markeredgecolor="white")

            ax.set_xlim(0, corridor_len)
            ax.set_ylim(-1.5, 1.5)
            ax.set_yticks([])
            ax.set_xlabel("Distancia a lo largo del Corredor Vial (0 a 15 km)", fontsize=10, fontweight="bold")
            ax.set_title(
                f"Animación de Flujo Vehicular en Corredor Urbano | Hora: {hora} | "
                f"Estado: {row['Estado_Viterbi']} ({row['Semaforo_Color']}) | Velocidad: {speed:.1f} km/h",
                fontsize=11, fontweight="bold", color="#1E3A8A"
            )

        anim = FuncAnimation(fig, update, frames=num_frames, interval=250, repeat=True)
        out_path = os.path.join(self.output_dir, filename)
        anim.save(out_path, writer="pillow", fps=4)
        plt.close(fig)
        return out_path
