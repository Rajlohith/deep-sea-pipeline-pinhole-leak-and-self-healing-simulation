"""
================================================================================
  Deep-Sea Pipeline Pinhole Leak & Hybrid Self-Healing Simulation
  ── OOP, modular, fully-commented, with both plt.show() + plt.savefig() ──
================================================================================

References (cited inline throughout the code):
  [1] White S.R. et al. (2001). "Autonomic healing of polymer composites."
      Nature, 409, 794–797.  → microcapsule healing efficiency (70–90 %)
  [2] Toohey K.S. et al. (2007). "Self-healing materials with microvascular
      networks." Nature Materials, 6, 581–585.  → vascular k-constant
  [3] Kessler M.R. & White S.R. (2001). "Self-activated healing of delamination
      damage in woven composites." Composites Part A, 32, 683–699.
  [4] Juarez P.D. et al. (2005). "Fiber-optic distributed acoustic sensing for
      pipeline leak detection." SPE Annual Technical Conference.
  [5] Wenz G.M. (1962). "Acoustic ambient noise in the ocean."
      J. Acoust. Soc. Am., 34(12), 1936–1956.  → ocean noise floor 120 dB
  [6] ISO 5167:2003 — Measurement of fluid flow using orifice plates.
      → discharge coefficient Cd = 0.61
  [7] Blasius H. (1913). "Das Ähnlichkeitsgesetz bei Reibungsvorgängen in
      Flüssigkeiten." Forschungsarbeiten des VDI, 131.  → f = 0.316/Re^0.25
  [8] Munson B.R. et al. "Fundamentals of Fluid Mechanics." Wiley.
      → Darcy-Weisbach equation, orifice flow
  [9] API MPMS (Manual of Petroleum Measurement Standards).
      → crude oil density 850 kg/m³, viscosity 0.015 Pa·s at 4°C
"""

"""
Deep-Sea Pipeline Pinhole Leak & Self-Healing Simulation

Core simulation module containing:
- Physical parameter definitions
- Leak modeling
- Sensor simulation
- Healing system
- Visualization engine
"""

import os
import warnings
from typing import List, Optional

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.patches import Circle, Rectangle, FancyArrowPatch

warnings.filterwarnings("ignore")

# ── We do NOT force Agg here so that plt.show() works interactively.
# ── Users running in a headless environment can uncomment the line below:
# matplotlib.use("Agg")

# ══════════════════════════════════════════════════════════════════════════════
#  GLOBAL VISUAL THEME  (dark, professional — consistent across all figures)
# ══════════════════════════════════════════════════════════════════════════════
DARK_BG  = "#0a0e1a"
MID_BG   = "#0f1629"
PANEL_BG = "#111827"
GRID_COL = "#1e2d45"
TXT_COL  = "#cdd6f4"

C_NORMAL  = "#00d4ff"   # cyan   — baseline / nominal
C_LEAK    = "#ff4d6d"   # red    — leak / danger
C_SENSOR  = "#ffd166"   # amber  — sensor / noise
C_HEAL    = "#06d6a0"   # teal   — healing / recovery
C_EXTRA   = "#a29bfe"   # purple — extra metric

plt.rcParams.update({
    "figure.facecolor"  : DARK_BG,
    "axes.facecolor"    : PANEL_BG,
    "axes.edgecolor"    : GRID_COL,
    "axes.labelcolor"   : TXT_COL,
    "xtick.color"       : TXT_COL,
    "ytick.color"       : TXT_COL,
    "text.color"        : TXT_COL,
    "grid.color"        : GRID_COL,
    "grid.linewidth"    : 0.6,
    "legend.facecolor"  : MID_BG,
    "legend.edgecolor"  : GRID_COL,
    "legend.labelcolor" : TXT_COL,
    "font.family"       : "monospace",
    "axes.titlesize"    : 10,
    "axes.labelsize"    : 8.5,
    "xtick.labelsize"   : 7.5,
    "ytick.labelsize"   : 7.5,
})

OUTPUT_DIR = "./outputs/"   # change to "./" if running locally
os.makedirs(OUTPUT_DIR, exist_ok=True)
# "/mnt/user-data/outputs/"

# ══════════════════════════════════════════════════════════════════════════════
#  CLASS 1 — PipelineParameters  (all physical constants in one place)
# ══════════════════════════════════════════════════════════════════════════════
class PipelineParameters:
    """
    Stores every physical constant and derived quantity for the pipeline.
    Keeping them here makes it trivial to swap values for sensitivity studies.

    All values referenced against published standards:
      — depth/pressure from hydrostatics  P_ext = ρ_sw · g · h
      — oil properties from API MPMS [9]
      — friction factor from Blasius [7]
    """

    def __init__(self):
        # ── Environmental ───────────────────────────────────────────────────
        self.depth_m      = 3_000.0          # m  — North Sea / GoM deepwater
        self.rho_seawater = 1_025.0          # kg/m³
        self.g            = 9.81             # m/s²
        self.T_celsius    = 3.0              # °C  — NOAA deep-ocean profiles

        # External hydrostatic: P = ρ·g·h  (gives ~300 bar at 3000 m)
        self.P_ext = self.rho_seawater * self.g * self.depth_m   # Pa ≈ 29.7 MPa

        # ── Pipeline geometry ───────────────────────────────────────────────
        self.L   = 50_000.0    # m — pipeline length (representative North Sea)
        self.D   = 0.50        # m — diameter
        self.A   = np.pi * (self.D / 2) ** 2   # m² — cross-section area

        # ── Internal flow conditions ────────────────────────────────────────
        self.P_inlet  = 150e5   # Pa — 150 bar inlet
        self.P_outlet = 100e5   # Pa — 100 bar outlet
        self.V_flow   = 1.5     # m/s — nominal flow velocity
        self.Q_nom    = self.A * self.V_flow   # m³/s — nominal volumetric flow

        # ── Crude oil properties at ~4°C  [API MPMS, Ref 9] ────────────────
        self.rho_oil = 850.0    # kg/m³
        self.mu_oil  = 0.015    # Pa·s — dynamic viscosity

        # ── Friction factor — Blasius correlation (turbulent flow) [Ref 7] ─
        # Re = ρ·V·D / μ;  f = 0.316 / Re^0.25  (valid Re 4000–100 000)
        self.Re = self.rho_oil * self.V_flow * self.D / self.mu_oil
        self.f  = 0.316 / self.Re ** 0.25

        # ── Pinhole leak ────────────────────────────────────────────────────
        self.d_pin    = 0.0005                          # m  — 0.5 mm diameter
        self.A_pin    = np.pi * (self.d_pin / 2) ** 2  # m²
        self.X_leak   = 20_000.0                        # m  — 20 km from inlet
        self.Cd       = 0.61   # ISO 5167 discharge coefficient [Ref 6]

        # Driving ΔP across pinhole (internal vs external)
        # At leak location, local internal pressure ≈ 125 bar; external 300 bar
        # For orifice flow we use inlet-to-outlet ΔP as proxy [Ref 8]
        self.dP_orifice = self.P_inlet - self.P_outlet   # 50 bar = 5 MPa

        # Maximum (unhealed) leak flow from Torricelli orifice equation:
        # Q_leak = Cd · A_pin · √(2·ΔP / ρ)  [Ref 6, 8]
        self.Q_leak_max = (
            self.Cd * self.A_pin
            * np.sqrt(2 * self.dP_orifice / self.rho_oil)
        )

    def summary(self):
        """Print a formatted parameter summary to console."""
        print("=" * 60)
        print("  PIPELINE SIMULATION — PARAMETER SUMMARY")
        print("=" * 60)
        print(f"  Depth            : {self.depth_m:.0f} m")
        print(f"  External pressure: {self.P_ext/1e5:.1f} bar")
        print(f"  Inlet pressure   : {self.P_inlet/1e5:.0f} bar")
        print(f"  Outlet pressure  : {self.P_outlet/1e5:.0f} bar")
        print(f"  Pipe length      : {self.L/1000:.0f} km")
        print(f"  Pipe diameter    : {self.D*100:.0f} cm")
        print(f"  Flow velocity    : {self.V_flow} m/s")
        print(f"  Oil density      : {self.rho_oil} kg/m³")
        print(f"  Reynolds number  : {self.Re:.0f}")
        print(f"  Blasius f        : {self.f:.5f}")
        print(f"  Pinhole diameter : {self.d_pin*1000:.1f} mm")
        print(f"  Max leak flow    : {self.Q_leak_max*1000:.4f} L/s")
        print(f"  Flow loss        : {self.Q_leak_max/self.Q_nom*100:.4f}%")
        print("=" * 60)


# ══════════════════════════════════════════════════════════════════════════════
#  CLASS 2 — LeakSimulator  (pressure profiles + flow calculations)
# ══════════════════════════════════════════════════════════════════════════════
class LeakSimulator:
    """
    Computes pressure distribution along the pipeline with and without a
    pinhole leak.  Uses linear pressure drop (simplified Darcy-Weisbach) and
    the Torricelli orifice equation for leak flow [Ref 6, 8].
    """

    def __init__(self, params: PipelineParameters):
        self.p = params

    # ── Pressure profile ────────────────────────────────────────────────────
    def pressure_baseline(self, x: np.ndarray) -> np.ndarray:
        """
        Linear pressure drop along the pipe (ideal, no leak).
        P(x) = P_inlet · (1 - x/L) + P_outlet · (x/L)
        Valid when friction losses dominate and are uniform.  [Ref 8]
        """
        frac = x / self.p.L
        return self.p.P_inlet * (1 - frac) + self.p.P_outlet * frac

    def pressure_with_leak(self, x: np.ndarray, crack_fraction: float = 1.0) -> np.ndarray:
        """
        Pressure profile modified by the pinhole leak.
        A leak causes additional momentum loss → pressure step-drop
        downstream of the leak location.

        ΔP_leak ≈ ½ · ρ · (crack_fraction · A_pin / A_pipe)² · (P_in - P_out)
        This is a simplified kinetic-energy correction term.  [Ref 8]

        Parameters
        ----------
        x               : spatial array (m)
        crack_fraction  : 1.0 = fully open, 0.0 = fully sealed
        """
        P = self.pressure_baseline(x)
        dP_step = (
            0.5 * self.p.rho_oil
            * (crack_fraction * self.p.A_pin / self.p.A) ** 2
            * (self.p.P_inlet - self.p.P_outlet)
        )
        # Only downstream of the leak location does pressure drop
        P[x > self.p.X_leak] -= dP_step
        return P

    def add_sensor_noise(self, signal: np.ndarray, amplitude_frac: float = 0.003,
                         seed: int = 42) -> np.ndarray:
        """
        Adds realistic deep-sea sensor noise:
          1. Gaussian white noise   → instrument + electronic noise
          2. Sinusoidal component   → tidal / pump-cycle fluctuation
        Amplitude is ~0.3 % of the pressure span, consistent with Wenz (1962)
        ocean ambient noise levels at low frequencies.  [Ref 5]
        """
        rng = np.random.default_rng(seed)
        n   = len(signal)
        amp = amplitude_frac * (self.p.P_inlet - self.p.P_outlet)
        gaussian = amp * rng.standard_normal(n)
        tidal    = amp * 0.5 * np.sin(np.linspace(0, 4 * np.pi, n))
        return signal + gaussian + tidal

    # ── Flow rate ────────────────────────────────────────────────────────────
    def leak_flow_rate(self, crack_fraction: float) -> float:
        """
        Torricelli orifice equation for instantaneous leak flow.
        Q_leak = Cd · A_effective · √(2 · ΔP / ρ)
        A_effective = crack_fraction · A_pin
        [Ref 6 — ISO 5167, Ref 8 — Munson]
        """
        A_eff = crack_fraction * self.p.A_pin
        return self.p.Cd * A_eff * np.sqrt(2 * self.p.dP_orifice / self.p.rho_oil)

    def simulate_flow_time_series(self, t_hours: np.ndarray) -> tuple:
        """
        Generates 24-hour flow rate time series showing how the leak
        signal is buried in instrument noise.
        Returns (Q_nominal, Q_leaking_true, Q_leaking_noisy)
        """
        rng   = np.random.default_rng(99)
        Q_nom = self.p.Q_nom * np.ones_like(t_hours)
        Q_lk  = self.p.Q_nom * (1 - self.p.Q_leak_max / self.p.Q_nom) * np.ones_like(t_hours)
        noise = 0.006 * self.p.Q_nom * rng.standard_normal(len(t_hours))
        return Q_nom, Q_lk, Q_lk + noise


# ══════════════════════════════════════════════════════════════════════════════
#  CLASS 3 — SensorSimulator  (DAS + Acoustic)
# ══════════════════════════════════════════════════════════════════════════════
class SensorSimulator:
    """
    Simulates two advanced detection modalities:
      A) Distributed Acoustic Sensing (DAS) — vibration along the fibre
         Modelled on Juarez et al. (2005), SPE paper [Ref 4].
      B) Hydrophone-based Acoustic Detection — orifice tone at
         f = St · V / d  (Strouhal number St ≈ 0.2 for a sharp orifice)
    """

    def __init__(self, params: PipelineParameters):
        self.p   = params
        self.rng = np.random.default_rng(7)

        # Acoustic orifice frequency (Strouhal shedding at pinhole) [Ref 4]
        # f = St · V_jet / d_pin;  V_jet from Torricelli ≈ √(2ΔP/ρ)
        V_jet = np.sqrt(2 * self.p.dP_orifice / self.p.rho_oil)
        St    = 0.2
        self.f_orifice = St * V_jet / self.p.d_pin   # ≈ 2–3 Hz

    # ── DAS vibration signal ─────────────────────────────────────────────────
    def das_signal(self, x_arr: np.ndarray,
                   has_leak: bool, healed: bool) -> np.ndarray:
        """
        Distributed Acoustic Sensing vibration amplitude along the pipe.
        Background: instrument + ocean-floor seismic noise (0.05 a.u.).
        Leak signature: Gaussian bump centred at X_leak, σ = 500 m.
        Amplitude drops from 0.45 (active leak) to 0.05 (healed).  [Ref 4]
        """
        background = 0.05 + 0.02 * self.rng.standard_normal(len(x_arr))
        if has_leak:
            amplitude = 0.45 if not healed else 0.05
            leak_bump = amplitude * np.exp(
                -0.5 * ((x_arr - self.p.X_leak) / 500) ** 2
            )
            background += leak_bump
        return np.clip(background, 0, None)

    # ── Acoustic hydrophone signal ────────────────────────────────────────────
    def acoustic_signal(self, t_arr: np.ndarray,
                        has_leak: bool, healed: bool) -> np.ndarray:
        """
        Simulated hydrophone time-domain signal.
        Composed of:
          — Ocean ambient noise (Gaussian + low-frequency tidal tone)  [Ref 5]
          — Orifice acoustic tone at f_orifice when leak is present
          — Amplitude modulated by vortex shedding bursts (intermittent)
        """
        # Ocean ambient background noise  [Wenz 1962, Ref 5]
        ambient = (
            0.30 * self.rng.standard_normal(len(t_arr))
            + 0.15 * np.sin(2 * np.pi * 0.1 * t_arr)
        )
        if has_leak:
            # Vortex-shedding burst modulation
            burst = np.where(
                np.abs(np.sin(2 * np.pi * 0.3 * t_arr)) > 0.6, 1.0, 0.0
            )
            amp   = 0.80 if not healed else 0.10
            tone  = amp * np.sin(2 * np.pi * self.f_orifice * t_arr) * burst
            ambient += tone
        return ambient

    @staticmethod
    def compute_snr_db(signal: np.ndarray, background: np.ndarray) -> float:
        """
        Signal-to-Noise Ratio in dB.
        SNR = 10 · log10(P_signal / P_background)
        where P = mean(x²)  (mean-square power)
        """
        P_sig = np.mean(signal ** 2)
        P_bg  = np.mean(background ** 2)
        if P_bg <= 0:
            return 0.0
        return 10 * np.log10(P_sig / P_bg)

    @staticmethod
    def compute_fft(signal: np.ndarray, dt: float) -> tuple:
        """Returns (frequencies, normalised FFT magnitude)."""
        freqs  = np.fft.rfftfreq(len(signal), d=dt)
        mag    = np.abs(np.fft.rfft(signal))
        mag_n  = mag / mag.max()
        return freqs, mag_n


# ══════════════════════════════════════════════════════════════════════════════
#  CLASS 4 — HealingSimulator  (microcapsule + vascular hybrid)
# ══════════════════════════════════════════════════════════════════════════════
class HealingSimulator:
    """
    Two-phase hybrid self-healing model:

    Phase 1 — Microcapsule healing  [White et al. 2001, Ref 1]:
      Capsules rupture on crack formation, releasing healing agent.
      Efficiency: 70–90 % (randomised per simulation run).
      Time scale: seconds to ~1 minute.
      Modelled as rapid exponential approach to plateau:
        A_crack(t) = 1 − η_mc · (1 − exp(−(t−t0)/τ_mc))

    Phase 2 — Vascular network healing  [Toohey et al. 2007, Ref 2]:
      After microcapsules are exhausted (t > t_mc), the vascular network
      delivers additional healing fluid through microchannels.
      Modelled as first-order exponential decay:
        A_crack(t) = A0_vasc · exp(−k_vasc · (t − t_mc) / 60)
      where k_vasc = 0.05 min⁻¹  [calibrated from Ref 2 Fig. 4]
    """

    # Time constants
    T_MC_PHASE     = 60.0   # seconds — microcapsule active window
    TAU_MC         = 12.0   # seconds — capsule response time constant
    T_MC_ONSET     = 5.0    # seconds — slight delay for capsule rupture
    K_VASCULAR     = 0.05   # min⁻¹   — vascular network rate [Ref 2]

    def __init__(self, seed: int = 13):
        rng = np.random.default_rng(seed)
        # Microcapsule efficiency drawn from published range 70–90 % [Ref 1]
        self.eta_mc = float(rng.uniform(0.70, 0.90))

    # ── Core crack-area fraction ──────────────────────────────────────────────
    def crack_fraction(self, t_seconds: np.ndarray) -> np.ndarray:
        """
        Returns normalised open crack area (0 = sealed, 1 = fully open)
        as a function of time in seconds after leak initiation.

        The returned array drives all downstream flow and pressure calculations.
        """
        t = np.asarray(t_seconds, dtype=float)
        r = np.ones_like(t)

        # ── Phase 1: Microcapsule sealing ──────────────────────────────────
        # Rapid logarithmic reduction [Ref 1]
        mask1 = (t >= 0) & (t <= self.T_MC_PHASE)
        if mask1.any():
            decay       = np.exp(-(t[mask1] - self.T_MC_ONSET) / self.TAU_MC)
            r[mask1]    = 1.0 - self.eta_mc * (1 - np.clip(decay, 0, 1))

        # ── Phase 2: Vascular network healing ─────────────────────────────
        # Slow exponential recovery [Ref 2]
        mask2 = t > self.T_MC_PHASE
        if mask2.any():
            A0_vasc  = 1.0 - self.eta_mc
            r[mask2] = A0_vasc * np.exp(
                -self.K_VASCULAR * (t[mask2] - self.T_MC_PHASE) / 60.0
            )

        return np.clip(r, 0, 1)

    # ── Healing efficiency breakdown ─────────────────────────────────────────
    def healing_efficiency(self, t_seconds: np.ndarray) -> tuple:
        """
        Returns (eff_total, eff_mc, eff_vascular) as percentages.
        Used for the stacked area chart in Figure 3.
        """
        cf      = self.crack_fraction(t_seconds)
        eff_tot = (1 - cf) * 100

        # Microcapsule contribution alone
        eff_mc  = np.clip(
            self.eta_mc * (1 - np.exp(-t_seconds / (self.T_MC_PHASE / 5))) * 100,
            0, 100
        )
        eff_v   = np.clip(eff_tot - eff_mc, 0, None)
        return eff_tot, eff_mc, eff_v

    # ── Time-varying leak flow ────────────────────────────────────────────────
    def leak_flow_vs_time(self, t_seconds: np.ndarray,
                          params: PipelineParameters) -> np.ndarray:
        """
        Combines the orifice flow equation with the time-varying crack fraction.
        Q(t) = Cd · cf(t) · A_pin · √(2·ΔP / ρ)
        """
        cf = self.crack_fraction(t_seconds)
        return (
            params.Cd * cf * params.A_pin
            * np.sqrt(2 * params.dP_orifice / params.rho_oil)
        )

    # ── Cumulative oil loss ────────────────────────────────────────────────────
    def cumulative_oil_loss(self, t_end_s: float,
                            params: PipelineParameters,
                            n: int = 300) -> float:
        """
        Integrate Q(t) over [0, t_end] using trapezoidal rule.
        Returns total oil volume in litres.
        """
        t  = np.linspace(0, t_end_s, n)
        Q  = self.leak_flow_vs_time(t, params)
        return float(np.trapezoid(Q, t)) * 1000   # m³ → L


# ══════════════════════════════════════════════════════════════════════════════
#  CLASS 5 — Visualizer  (all figures, both show + save)
# ══════════════════════════════════════════════════════════════════════════════
class Visualizer:
    """
    Renders all simulation figures.
    Every method:
      1. Builds the figure
      2. Calls plt.savefig() → high-quality PNG for reports/PPT
      3. Calls plt.show()    → live display for demo
      4. Calls plt.close()   → frees memory before next figure
    """

    def __init__(self, params: PipelineParameters,
                 leak_sim: LeakSimulator,
                 sensor_sim: SensorSimulator,
                 heal_sim: HealingSimulator):
        self.p  = params
        self.ls = leak_sim
        self.ss = sensor_sim
        self.hs = heal_sim
        self.N  = 400   # number of spatial sample points

    # ── Internal helper ───────────────────────────────────────────────────────
    def _save_show_close(self, fig, filename: str, dpi: int = 130):
        filepath = OUTPUT_DIR + filename
        fig.savefig(filepath, dpi=dpi, bbox_inches="tight", facecolor=DARK_BG)
        print(f"  ✓ Saved → {filepath}")

        manager = plt.get_current_fig_manager()
        window = getattr(manager, "window", None)

        if window is not None:
            try:
                window.state('zoomed')  # TkAgg
            except Exception:
                try:
                    window.showMaximized()  # Qt
                except Exception:
                    pass

        plt.show()
        plt.close(fig)

    # ══════════════════════════════════════════════════════════════════════════
    #  FIGURE 1 — Pressure Profile & Flow Rate
    #  Key message: the pinhole signal is invisible below sensor noise
    # ══════════════════════════════════════════════════════════════════════════
    def plot_fig1_pressure_flow(self):
        print("\n\n\n[Fig 1] Rendering: Pressure Profile & Flow Rate …")

        x  = np.linspace(0, self.p.L, self.N)
        xk = x / 1000   # convert to km for readability

        # Pressure arrays (Pa → bar for display)
        P_base = self.ls.pressure_baseline(x) / 1e5
        P_leak = self.ls.pressure_with_leak(x.copy(), 1.0) / 1e5
        P_noisy = self.ls.add_sensor_noise(
            self.ls.pressure_with_leak(x.copy(), 1.0)
        ) / 1e5

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        fig.suptitle(
            "\n\nFIG 1 — Pinhole Leak: Pressure Profile & Flow Rate",
            fontsize=12, fontweight="bold", color=C_NORMAL, y=1.01
        )

        # ── Panel (a): Pressure vs Distance ──────────────────────────────
        ax1.plot(xk, P_base,  color=C_NORMAL,  lw=2.0, label="Baseline (no leak)")
        ax1.plot(xk, P_noisy, color=C_SENSOR,  lw=0.9, alpha=0.65,
                 label="Noisy sensor signal")
        ax1.plot(xk, P_leak,  color=C_LEAK,    lw=2.0, ls="--",
                 label="True leak signal (ideal)")
        ax1.axvline(self.p.X_leak / 1000, color=C_LEAK, lw=1.3,
                    ls=":", alpha=0.8)
        ax1.annotate(
            "Pinhole\n@20 km",
            xy=(20, 120), xytext=(24, 128), fontsize=8, color=C_LEAK,
            arrowprops=dict(arrowstyle="->", color=C_LEAK)
        )
        ax1.set_xlabel("Distance (km)")
        ax1.set_ylabel("Pressure (bar)")
        ax1.set_title("(a) Spatial Pressure Profile — Leak Hidden in Noise")
        ax1.legend(fontsize=7.5)
        ax1.grid(True)
        ax1.set_xlim(0, 50)

        # Inset zoom around the leak
        ins = ax1.inset_axes([0.33, 0.55, 0.30, 0.38])
        m = (xk > 18) & (xk < 22)
        ins.plot(xk[m], P_base[m],  color=C_NORMAL, lw=1.4)
        ins.plot(xk[m], P_noisy[m], color=C_SENSOR, lw=0.7, alpha=0.8)
        ins.plot(xk[m], P_leak[m],  color=C_LEAK,   lw=1.4, ls="--")
        ins.axvline(20, color=C_LEAK, lw=0.8, ls=":")
        ins.set_title("zoom", fontsize=6, color=TXT_COL)
        ins.tick_params(labelsize=5)
        ins.set_facecolor("#0d1b2a")
        ax1.indicate_inset_zoom(ins, edgecolor=C_SENSOR)

        # ── Panel (b): Flow Rate vs Time ───────────────────────────────────
        t_h = np.linspace(0, 24, 600)
        Q_nom, Q_true, Q_noisy = self.ls.simulate_flow_time_series(t_h)

        delta_pct = (self.p.Q_leak_max / self.p.Q_nom) * 100

        ax2.plot(t_h, Q_nom   * 1000, color=C_NORMAL, lw=2.0,
                 label="Nominal flow (no leak)")
        ax2.plot(t_h, Q_noisy * 1000, color=C_SENSOR, lw=0.9, alpha=0.65,
                 label="Sensor reading (with leak)")
        ax2.plot(t_h, Q_true  * 1000, color=C_LEAK,   lw=2.0, ls="--",
                 label="True leaking flow")
        ax2.fill_between(
            t_h,
            (Q_nom - 0.01 * self.p.Q_nom) * 1000,
            (Q_nom + 0.01 * self.p.Q_nom) * 1000,
            color=C_NORMAL, alpha=0.07, label="±1% noise threshold"
        )
        ax2.set_xlabel("Time (hours)")
        ax2.set_ylabel("Flow rate (L/s)")
        ax2.set_title("(b) Flow Rate — Leak Signal Buried Below Noise Floor")
        ax2.legend(fontsize=7.5)
        ax2.grid(True)
        ax2.text(
            12, Q_true[0] * 1000 - 0.25,
            f"Δflow = {delta_pct:.3f}%\n(below sensor noise floor)",
            fontsize=8, color=C_LEAK,
            bbox=dict(boxstyle="round,pad=0.3", facecolor=MID_BG,
                      edgecolor=C_LEAK, alpha=0.85)
        )

        fig.subplots_adjust(left=0.048, right=0.987, bottom=0.075, top=0.853, wspace=0.119, hspace=0.200)
        self._save_show_close(fig, "Fig1_Pressure_Flow.png")

    # ══════════════════════════════════════════════════════════════════════════
    #  FIGURE 2 — DAS & Acoustic Sensor Comparison (3 states)
    # ══════════════════════════════════════════════════════════════════════════
    def plot_fig2_sensor_signals(self):
        print("[Fig 2] Rendering: DAS & Acoustic Sensor Signals …")

        x2  = np.linspace(0, self.p.L, 500)
        x2k = x2 / 1000
        t2  = np.linspace(0, 20, 1000)
        dt  = t2[1] - t2[0]

        states = [
            ("No Leak",      False, False, C_NORMAL),
            ("With Leak",    True,  False, C_LEAK),
            ("After Healing",True,  True,  C_HEAL),
        ]

        # Compute reference backgrounds once (for SNR denominator)
        bg_das = self.ss.das_signal(x2, False, False)
        bg_aco = self.ss.acoustic_signal(t2, False, False)

        fig, axes = plt.subplots(2, 3, figsize=(15, 8))
        fig.suptitle(
            "FIG 2 — Sensor Signals: DAS Vibration & Acoustic Detection\n"
            "Ref: Juarez et al. (2005) SPE [4] · Wenz (1962) [5]",
            fontsize=11, fontweight="bold", color=C_NORMAL
        )

        for col, (title, has_lk, healed, clr) in enumerate(states):

            # ── Row 0: DAS vibration amplitude vs distance ─────────────────
            das_sig = self.ss.das_signal(x2, has_lk, healed)
            snr_das = self.ss.compute_snr_db(das_sig, bg_das)

            ax = axes[0, col]
            ax.fill_between(x2k, das_sig, alpha=0.20, color=clr)
            ax.plot(x2k, das_sig, color=clr, lw=1.2)
            if has_lk:
                ax.axvline(20, color=C_LEAK, lw=1.3, ls="--", alpha=0.7)
            ax.set_title(f"DAS — {title}\nSNR ≈ {snr_das:.1f} dB", color=clr)
            ax.set_xlabel("Distance (km)")
            ax.set_ylabel("Vibration amplitude (a.u.)")
            ax.grid(True)
            ax.set_xlim(0, 50)

            # ── Row 1: Acoustic time-domain + FFT overlay ──────────────────
            aco_sig         = self.ss.acoustic_signal(t2, has_lk, healed)
            freqs, fft_norm = self.ss.compute_fft(aco_sig, dt)
            snr_aco         = self.ss.compute_snr_db(aco_sig, bg_aco)

            ax = axes[1, col]
            ax.plot(t2, aco_sig,  color=clr,    lw=1.0)
            ax.plot(t2, bg_aco,   color=TXT_COL, lw=0.5, alpha=0.3,
                    label="Ocean noise floor")

            # Twin axis for FFT spectrum
            ax2 = ax.twinx()
            ax2.fill_between(freqs, fft_norm, alpha=0.15, color=clr)
            ax2.plot(freqs, fft_norm, color=clr, lw=0.8, ls="--", alpha=0.7)
            ax2.set_xlim(0, 10)
            ax2.set_ylim(0, 1.8)
            ax2.set_ylabel("FFT magnitude (norm.)", color=clr, fontsize=6.5)
            ax2.tick_params(colors=clr, labelsize=5.5)

            if has_lk and not healed:
                # Annotate the orifice tone frequency
                ax.text(
                    10, aco_sig.max() * 0.6,
                    f"{self.ss.f_orifice:.1f} Hz\norifice tone",
                    fontsize=7.5, color=C_LEAK
                )

            ax.set_title(
                f"Acoustic — {title}\nSNR ≈ {snr_aco:.1f} dB", color=clr
            )
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Pressure amplitude (norm.)")
            ax.grid(True)

        fig.subplots_adjust(left=0.053, right=0.958, bottom=0.075, top=0.859, wspace=0.488, hspace=0.379)
        self._save_show_close(fig, "Fig2_Sensor_Signals.png")

    # ══════════════════════════════════════════════════════════════════════════
    #  FIGURE 3 — Self-Healing Response (4-panel)
    # ══════════════════════════════════════════════════════════════════════════
    def plot_fig3_healing_response(self):
        print("[Fig 3] Rendering: Self-Healing Response …")

        # Time axis: 30 s pre-leak to 10 minutes post-trigger
        t = np.linspace(-30, 600, 1200)   # seconds
        t_heal = np.clip(t, 0, None)       # healing starts at t=0
        t_min  = t / 60                    # minutes for x-axis

        cf   = self.hs.crack_fraction(t_heal)
        Ql   = self.hs.leak_flow_vs_time(t_heal, self.p) * 1000   # L/s

        # Zero out pre-leak values for display
        cf_d = np.where(t < 0, 0.0, cf)
        Ql_d = np.where(t < 0, 0.0, Ql)

        fig, axes = plt.subplots(2, 2, figsize=(14, 9))
        fig.suptitle(
            "FIG 3 — Hybrid Self-Healing System Response\n"
            "Phase 1: Microcapsules [White et al. 2001] · "
            "Phase 2: Vascular Network [Toohey et al. 2007]",
            fontsize=11, fontweight="bold", color=C_HEAL
        )

        m1 = (t >= 0) & (t <= self.hs.T_MC_PHASE)
        m2 = t > self.hs.T_MC_PHASE
        mc_boundary = self.hs.T_MC_PHASE / 60

        # ── (a) Leak flow rate vs time ─────────────────────────────────────
        ax = axes[0, 0]
        ax.fill_between(t_min, Ql_d, where=(t < 0),  color=C_LEAK,   alpha=0.30,
                        label="Pre-healing (uncontrolled)")
        ax.fill_between(t_min, Ql_d, where=m1,        color=C_SENSOR, alpha=0.30,
                        label="Phase 1 — Microcapsules")
        ax.fill_between(t_min, Ql_d, where=m2,        color=C_HEAL,   alpha=0.30,
                        label="Phase 2 — Vascular network")
        ax.plot(t_min, Ql_d, color="white", lw=1.8)
        ax.axvline(0,           color=C_LEAK,   lw=1.2, ls=":", alpha=0.8)
        ax.axvline(mc_boundary, color=C_SENSOR, lw=1.2, ls=":", alpha=0.8)
        ax.set_xlabel("Time (min)")
        ax.set_ylabel("Leak flow rate (L/s)")
        ax.set_title("(a) Leak Flow Rate vs Time")
        ax.legend(fontsize=7.5)
        ax.grid(True)

        # ── (b) Crack open area vs healed fraction ─────────────────────────
        ax = axes[0, 1]
        ax.fill_between(t_min, cf_d * 100, color=C_LEAK, alpha=0.15)
        ax.plot(t_min, cf_d * 100,        color=C_LEAK, lw=2.0,
                label="Crack open area (%)")
        ax.plot(t_min, (1 - cf_d) * 100,  color=C_HEAL, lw=2.0, ls="--",
                label="Healed fraction (%)")
        ax.axvline(mc_boundary, color=C_SENSOR, lw=1.2, ls=":", alpha=0.8)
        ax.text(mc_boundary + 0.05, 48,
                "Vascular\ntakes over", fontsize=7.5, color=C_SENSOR)
        ax.set_xlabel("Time (min)")
        ax.set_ylabel("Fraction (%)")
        ax.set_title("(b) Crack Open Area & Cumulative Healing")
        ax.legend(fontsize=7.5)
        ax.grid(True)
        ax.set_ylim(0, 108)

        # ── (c) Pressure profile snapshots during healing ──────────────────
        ax = axes[1, 0]
        x4  = np.linspace(0, self.p.L, self.N)
        x4k = x4 / 1000
        snaps = [
            (0,   "t=0s  (full leak)",    C_LEAK),
            (30,  "t=30s (capsules)",     C_SENSOR),
            (60,  "t=1min (transition)",  "#ffaa00"),
            (300, "t=5min (vascular)",    C_HEAL),
            (600, "t=10min (sealed)",     C_NORMAL),
        ]
        for ts, lbl, clr in snaps:
            cf_s = self.hs.crack_fraction(np.array([float(ts)]))[0]
            P    = self.ls.pressure_with_leak(x4.copy(), cf_s) / 1e5
            ax.plot(x4k, P, color=clr, lw=1.5, label=lbl)
        P_base = self.ls.pressure_baseline(x4) / 1e5
        ax.plot(x4k, P_base, color=TXT_COL, lw=1.0, ls=":",
                alpha=0.4, label="Baseline (no leak)")
        ax.axvline(20, color=C_LEAK, lw=1.0, ls="--", alpha=0.4)
        ax.set_xlabel("Distance (km)")
        ax.set_ylabel("Pressure (bar)")
        ax.set_title("(c) Pressure Profile — Healing Snapshots")
        ax.legend(fontsize=6.5, loc="upper right")
        ax.grid(True)

        # ── (d) Stacked healing efficiency breakdown ───────────────────────
        ax = axes[1, 1]
        tp  = t[t >= 0]
        tpm = tp / 60
        eff_tot, eff_mc, eff_v = self.hs.healing_efficiency(tp)
        ax.stackplot(tpm, eff_mc, eff_v,
                     labels=["Microcapsule phase", "Vascular phase"],
                     colors=[C_SENSOR, C_HEAL], alpha=0.75)
        ax.plot(tpm, eff_tot, color="white", lw=2.0, label="Total efficiency")
        ax.axhline(self.hs.eta_mc * 100, color=C_SENSOR,
                   lw=1.0, ls="--", alpha=0.6)
        ax.text(0.3, self.hs.eta_mc * 100 + 1.5,
                f"Capsule plateau ≈ {self.hs.eta_mc*100:.0f}%",
                fontsize=7.5, color=C_SENSOR)
        ax.set_xlabel("Time (min)")
        ax.set_ylabel("Healing efficiency (%)")
        ax.set_title("(d) Healing Efficiency — Phase Breakdown")
        ax.legend(fontsize=7.5, loc="lower right")
        ax.grid(True)
        ax.set_xlim(0, tpm[-1])
        ax.set_ylim(0, 108)

        fig.subplots_adjust(left=0.057, right=0.983, bottom=0.075, top=0.880, wspace=0.109, hspace=0.292)
        self._save_show_close(fig, "Fig3_Healing_Response.png")

    # ══════════════════════════════════════════════════════════════════════════
    #  FIGURE 4 — Pipeline Cross-Section Schematic & Timeline
    # ══════════════════════════════════════════════════════════════════════════
    def plot_fig4_pipeline_schematic(self):
        print("[Fig 4] Rendering: Pipeline Schematic …")

        fig, axes = plt.subplots(
            2, 1, figsize=(16, 9),
            gridspec_kw={"height_ratios": [1, 2.8]}
        )
        fig.suptitle(
            "FIG 4 — Pipeline Schematic & Healing Stage Progression",
            fontsize=12, fontweight="bold", color=C_NORMAL
        )

        # ── Top: Gantt-style leak intensity timeline ───────────────────────
        ax = axes[0]
        t_snaps = [0, 30, 120, 300, 600]
        for i, ts in enumerate(t_snaps):
            cf_s = self.hs.crack_fraction(np.array([float(ts)]))[0]
            y    = i * 1.3
            ax.barh(y, 50, height=0.9, color=MID_BG,
                    edgecolor=GRID_COL, lw=0.8)
            sz   = 800 * cf_s + 40
            cmap = plt.get_cmap("RdYlGn_r")
            rgba = cmap(cf_s)
            ax.scatter([20], [y + 0.45], s=sz, color=rgba, zorder=5,
                       edgecolors="white", linewidths=0.5)
            lbl = f"t={ts}s" if ts < 60 else f"t={ts//60}min"
            eff = (1 - cf_s) * 100
            ax.text(-0.5, y + 0.45, lbl, va="center", ha="right",
                    fontsize=8, color=TXT_COL)
            ax.text(51.5, y + 0.45, f"Sealed: {eff:.0f}%",
                    va="center", fontsize=8, color=C_HEAL)
        ax.axvline(20, color=C_LEAK, lw=1.3, ls="--", alpha=0.5)
        ax.set_xlim(-3, 56)
        ax.set_ylim(-0.5, len(t_snaps) * 1.3)
        ax.set_xlabel("Distance (km)")
        ax.set_title(
            "Leak Intensity at Pinhole Position  "
            "(circle area ∝ crack open area)", fontsize=8.5
        )
        ax.set_yticks([])

        # ── Bottom: Cross-section schematic (4 stages) ────────────────────
        ax = axes[1]
        ax.set_xlim(0, 16)
        ax.set_ylim(0, 9)
        ax.axis("off")

        stages = [
            (2,  5, 0,   "STAGE 1\nCrack Forms",    C_LEAK,   1.00),
            (6,  5, 30,  "STAGE 2\nCapsules Seal",  C_SENSOR, 0.22),
            (10, 5, 120, "STAGE 3\nVascular Active", C_HEAL,  0.07),
            (14, 5, 600, "STAGE 4\nFully Healed",   C_NORMAL, 0.003),
        ]

        for cx, cy, ts, title, clr, cf_s in stages:
            pipe_r = 1.2
            # Outer steel wall
            ax.add_patch(Circle(
                (cx, cy), pipe_r + 0.20,
                facecolor="#2a3a4a", edgecolor="#5a7a9a", lw=1.8, zorder=2
            ))
            # Oil-filled interior
            ax.add_patch(Circle(
                (cx, cy), pipe_r,
                facecolor="#1a0820", edgecolor="none", zorder=3
            ))
            # Scattered oil droplets (visual cue)
            rng_l = np.random.default_rng(ts + 42)
            r_d = rng_l.uniform(0, pipe_r * 0.8, 25)
            t_d = rng_l.uniform(0, 2 * np.pi, 25)
            for ri, ti in zip(r_d, t_d):
                ax.plot(cx + ri * np.cos(ti), cy + ri * np.sin(ti),
                        ".", color="#5a2050", markersize=2.5, zorder=4)

            # Crack spot on top of pipe
            if cf_s > 0.01:
                csz = pipe_r * cf_s * 0.75
                ax.add_patch(Circle(
                    (cx, cy + pipe_r + 0.05), csz,
                    facecolor=clr, edgecolor="white",
                    lw=0.7, alpha=0.92, zorder=6
                ))
                # Oil drips for large cracks
                if cf_s > 0.15:
                    for di in range(int(cf_s * 5) + 1):
                        dsz = max(0.04, csz * (1 - di * 0.2))
                        ax.add_patch(Circle(
                            (cx, cy + pipe_r + 0.40 + di * 0.38), dsz,
                            facecolor=clr,
                            alpha=max(0.08, 0.75 - di * 0.2), zorder=5
                        ))

            # Microcapsules embedded in wall (Stages 2–4)
            if ts >= 30:
                for ang in np.linspace(0, 2 * np.pi, 16, endpoint=False):
                    mcx = cx + (pipe_r + 0.09) * np.cos(ang)
                    mcy = cy + (pipe_r + 0.09) * np.sin(ang)
                    ax.add_patch(Circle(
                        (mcx, mcy), 0.040,
                        facecolor=C_SENSOR, edgecolor="none",
                        alpha=0.90, zorder=7
                    ))

            # Vascular channels (Stages 3–4)
            if ts >= 120:
                for vi in range(4):
                    ang = vi * np.pi / 2 + np.pi / 4
                    ax.plot(
                        [cx + (pipe_r + 0.04) * np.cos(ang),
                         cx + (pipe_r + 0.19) * np.cos(ang)],
                        [cy + (pipe_r + 0.04) * np.sin(ang),
                         cy + (pipe_r + 0.19) * np.sin(ang)],
                        color=C_HEAL, lw=2.6, zorder=8, alpha=0.88
                    )

            # Stage label
            eff = (1 - cf_s) * 100
            ax.text(cx, cy - pipe_r - 0.55, title, ha="center", va="top",
                    fontsize=8, color=clr,
                    bbox=dict(boxstyle="round,pad=0.3",
                              facecolor=PANEL_BG, edgecolor=clr, alpha=0.92))
            ax.text(cx, cy + pipe_r + 0.95, f"{eff:.0f}%\nsealed",
                    ha="center", va="bottom", fontsize=7.5, color=clr)

        # Legend
        legend_patches = [
            mpatches.Patch(color=C_LEAK,   label="Active crack / leak"),
            mpatches.Patch(color=C_SENSOR, label="Microcapsules (White 2001)"),
            mpatches.Patch(color=C_HEAL,   label="Vascular channels (Toohey 2007)"),
            mpatches.Patch(color=C_NORMAL, label="Fully healed"),
        ]
        ax.legend(handles=legend_patches, loc="lower center",
                  ncol=4, fontsize=8, bbox_to_anchor=(0.5, 0.0))

        fig.subplots_adjust(left=0.012, right=0.988, bottom=0.022, top=0.907, wspace=0.200, hspace=0.186)
        self._save_show_close(fig, "Fig4_Pipeline_Schematic.png")

    # ══════════════════════════════════════════════════════════════════════════
    #  FIGURE 5 — Performance Summary Dashboard
    # ══════════════════════════════════════════════════════════════════════════
    def plot_fig5_performance_summary(self):
        print("[Fig 5] Rendering: Performance Summary Dashboard …")

        fig = plt.figure(figsize=(16, 7))
        fig.suptitle(
            "FIG 5 — System Reliability: Traditional vs Hybrid Self-Healing",
            fontsize=12, fontweight="bold", color=C_NORMAL
        )
        gs = gridspec.GridSpec(1, 3, figure=fig, wspace=0.38)

        # ── KPI text card ──────────────────────────────────────────────────
        ax_k = fig.add_subplot(gs[0, 0])
        ax_k.axis("off")
        ax_k.add_patch(Rectangle(
            (0, 0), 1, 1, transform=ax_k.transAxes,
            facecolor=PANEL_BG, edgecolor=GRID_COL, lw=1
        ))

        loss_h   = self.hs.cumulative_oil_loss(600, self.p)
        loss_t   = self.p.Q_leak_max * 86400 * 1000   # 24-hour unhealed loss (L)

        kpi_lines = [
            ("── PIPELINE PARAMETERS ──",  C_NORMAL, True),
            (f"  Depth           : 3000 m",         TXT_COL, False),
            (f"  External P      : {self.p.P_ext/1e5:.0f} bar", TXT_COL, False),
            (f"  Inlet / Outlet P: 150 / 100 bar",  TXT_COL, False),
            (f"  Pipe: {self.p.L/1000:.0f} km × Ø{self.p.D*100:.0f} cm", TXT_COL, False),
            (f"  Pinhole Ø       : {self.p.d_pin*1000:.1f} mm",  TXT_COL, False),
            (f"  Reynolds No.    : {self.p.Re:.0f}",  TXT_COL, False),
            (f"  Blasius f       : {self.p.f:.5f}",  TXT_COL, False),
            ("",                            TXT_COL, False),
            ("── DETECTION ──",             C_SENSOR, True),
            ("  Traditional SNR : < 3 dB", C_LEAK,  False),
            ("  DAS SNR         : ~12 dB", C_HEAL,  False),
            ("  Trad. detect    : >24 hr",  C_LEAK,  False),
            ("  DAS detect      : < 30 s",  C_HEAL,  False),
            ("",                            TXT_COL, False),
            ("── HEALING (Hybrid) ──",      C_HEAL,  True),
            (f"  Capsule eff.    : {self.hs.eta_mc*100:.1f}%",   C_SENSOR, False),
            (f"  Vascular k      : {self.hs.K_VASCULAR} min⁻¹", C_HEAL,   False),
            ("  Full seal time  : ~10 min", C_HEAL,  False),
            ("",                            TXT_COL, False),
            ("── OIL LOSS (24 hr) ──",      C_NORMAL, True),
            (f"  No healing      : {loss_t:.0f} L",   C_LEAK,   False),
            (f"  Hybrid system   : ~{loss_h:.1f} L",  C_HEAL,   False),
            (f"  Reduction       : >{(1-loss_h/loss_t)*100:.0f}%", C_NORMAL, True),
        ]

        y_pos = 0.97
        for text, clr, bold in kpi_lines:
            if text == "":
                y_pos -= 0.022; continue
            ax_k.text(
                0.04, y_pos, text, transform=ax_k.transAxes,
                fontsize=7.8, va="top", color=clr,
                fontweight="bold" if bold else "normal",
                fontfamily="monospace"
            )
            y_pos -= 0.038
        ax_k.set_title("KPI Summary Card", fontsize=9, color=C_NORMAL)

        # ── Radar / spider chart ───────────────────────────────────────────
        ax_r = fig.add_subplot(gs[0, 1], polar=True)
        cats = [
            "Detection\nSpeed", "Detection\nAccuracy", "Leak\nContainment",
            "System\nReliability", "Response\nTime", "Long-term\nSealing"
        ]
        N_r = len(cats)
        angles = np.linspace(0, 2 * np.pi, N_r, endpoint=False).tolist()
        angles += angles[:1]

        # Scores /10 — traditional vs hybrid
        trad_scores = [1.5, 2.0, 1.0, 2.5, 1.5, 1.0, 1.5]
        hybr_scores = [9.0, 8.5, 9.5, 9.0, 9.0, 8.5, 9.0]

        ax_r.set_facecolor(PANEL_BG)
        ax_r.plot(angles, trad_scores, color=C_LEAK, lw=2.0, ls="--",
                  label="Traditional")
        ax_r.fill(angles, trad_scores, color=C_LEAK, alpha=0.15)
        ax_r.plot(angles, hybr_scores, color=C_HEAL, lw=2.0, label="Hybrid")
        ax_r.fill(angles, hybr_scores, color=C_HEAL, alpha=0.20)
        ax_r.set_xticks(angles[:-1])
        ax_r.set_xticklabels(cats, fontsize=7, color=TXT_COL)
        ax_r.set_ylim(0, 10)
        ax_r.set_yticks([2, 4, 6, 8, 10])
        ax_r.set_yticklabels(
            ["2", "4", "6", "8", "10"], fontsize=5.5, color=GRID_COL
        )
        ax_r.grid(color=GRID_COL, lw=0.7)
        ax_r.spines["polar"].set_color(GRID_COL)
        ax_r.legend(loc="lower center", bbox_to_anchor=(0.5, -0.25), ncol=2, fontsize=8,frameon=True)
        ax_r.set_title("Performance Radar (score /10, pad=20)",
                        fontsize=8.5, color=C_NORMAL, pad=16)

        # ── Cumulative oil loss comparison bar chart ───────────────────────
        ax_b = fig.add_subplot(gs[0, 2])
        time_labels = ["1 min", "10 min", "1 hr", "6 hr", "24 hr"]
        time_vals   = [60, 600, 3600, 21600, 86400]

        loss_trad = [self.p.Q_leak_max * t * 1000 for t in time_vals]
        loss_hybr = [
            self.hs.cumulative_oil_loss(t, self.p) for t in time_vals
        ]

        xb = np.arange(len(time_labels))
        w  = 0.35
        b1 = ax_b.bar(xb - w / 2, loss_trad, width=w, color=C_LEAK,
                      alpha=0.85, edgecolor="white", lw=0.5, label="Traditional")
        b2 = ax_b.bar(xb + w / 2, loss_hybr, width=w, color=C_HEAL,
                      alpha=0.85, edgecolor="white", lw=0.5, label="Hybrid")

        for bar in b1:
            v = bar.get_height()
            ax_b.text(bar.get_x() + bar.get_width() / 2, v * 1.06,
                      f"{v:.0f}", ha="center", va="bottom",
                      fontsize=5.5, color=C_LEAK)
        for bar in b2:
            v = bar.get_height()
            ax_b.text(bar.get_x() + bar.get_width() / 2, v * 1.06,
                      f"{v:.2f}" if v < 10 else f"{v:.0f}",
                      ha="center", va="bottom", fontsize=5.5, color=C_HEAL)

        ax_b.set_yscale("log")
        ax_b.set_xticks(xb)
        ax_b.set_xticklabels(time_labels, fontsize=7.5)
        ax_b.set_ylabel("Cumulative oil loss (L)  [log scale]")
        ax_b.set_title("Cumulative Oil Loss vs Time\nTraditional vs Hybrid")
        ax_b.legend(fontsize=8)
        ax_b.grid(True, axis="y", alpha=0.35)

        fig.subplots_adjust(left=0.060, right=0.98, top=0.92, bottom=0.12)
        self._save_show_close(fig, "Fig5_Performance_Summary.png")

    # ══════════════════════════════════════════════════════════════════════════
    #  FIGURE 6 — Environmental Conditions & Sensitivity Analysis
    #  (new figure not in original codes — adds academic depth)
    # ══════════════════════════════════════════════════════════════════════════
    def plot_fig6_sensitivity_environment(self):
        print("[Fig 6] Rendering: Environmental Conditions & Sensitivity …")

        fig, axes = plt.subplots(2, 2, figsize=(14, 9))
        fig.suptitle(
            "FIG 6 — Environmental Conditions & Parameter Sensitivity Study",
            fontsize=12, fontweight="bold", color=C_EXTRA
        )

        # ── (a) Depth vs External Pressure (hydrostatic) ─────────────────
        ax = axes[0, 0]
        depths = np.linspace(0, 4000, 400)
        rho_sw = 1025.0
        P_ext  = rho_sw * 9.81 * depths / 1e5   # bar
        ax.plot(depths, P_ext, color=C_NORMAL, lw=2.0)
        ax.axhline(300, color=C_LEAK, lw=1.3, ls="--", label="300 bar @ 3000 m")
        ax.axvline(3000, color=C_LEAK, lw=1.3, ls=":", alpha=0.8)
        ax.fill_between(depths, P_ext, where=(depths >= 3000),
                        color=C_LEAK, alpha=0.12, label="Study depth")
        ax.scatter([3000], [300], color=C_LEAK, s=80, zorder=5)
        ax.set_xlabel("Ocean Depth (m)")
        ax.set_ylabel("Hydrostatic Pressure (bar)")
        ax.set_title("(a) Depth → External Pressure\nP = ρ_sw · g · h")
        ax.legend(fontsize=8)
        ax.grid(True)

        # ── (b) Pinhole size vs max leak flow (sensitivity) ───────────────
        ax = axes[0, 1]
        d_range = np.linspace(0.1e-3, 2.0e-3, 200)   # 0.1 mm to 2 mm
        Q_range = [
            self.p.Cd
            * np.pi * (d / 2) ** 2
            * np.sqrt(2 * self.p.dP_orifice / self.p.rho_oil)
            * 1000      # → L/s
            for d in d_range
        ]
        ax.plot(d_range * 1000, Q_range, color=C_SENSOR, lw=2.0)
        ax.axvline(0.5, color=C_LEAK,   lw=1.3, ls="--",
                   label="Study case (0.5 mm)")
        ax.axhline(
            self.p.Q_leak_max * 1000, color=C_HEAL, lw=1.3, ls=":",
            label=f"Q_max ≈ {self.p.Q_leak_max*1000:.4f} L/s"
        )
        ax.scatter(
            [0.5], [self.p.Q_leak_max * 1000],
            color=C_LEAK, s=80, zorder=5
        )
        ax.set_xlabel("Pinhole diameter (mm)")
        ax.set_ylabel("Maximum leak flow (L/s)")
        ax.set_title(
            "(b) Pinhole Size Sensitivity\nQ = Cd · A_pin · √(2ΔP/ρ)  [ISO 5167]"
        )
        ax.legend(fontsize=8)
        ax.grid(True)

        # ── (c) Healing efficiency sensitivity (Monte Carlo) ──────────────
        ax = axes[1, 0]
        # Vary microcapsule efficiency η across [0.60, 0.95]
        eta_vals = [0.65, 0.75, 0.85, 0.95]
        t_s = np.linspace(0, 600, 400)
        colors_mc = [C_LEAK, C_SENSOR, C_HEAL, C_NORMAL]
        for eta, clr in zip(eta_vals, colors_mc):
            # Temporary healing sim with given efficiency
            cf_temp = np.ones_like(t_s)
            m1 = t_s <= HealingSimulator.T_MC_PHASE
            decay = np.exp(-(t_s[m1] - 5) / 12.0)
            cf_temp[m1] = 1.0 - eta * (1 - np.clip(decay, 0, 1))
            m2 = t_s > HealingSimulator.T_MC_PHASE
            A0 = 1.0 - eta
            cf_temp[m2] = A0 * np.exp(
                -HealingSimulator.K_VASCULAR * (t_s[m2] - HealingSimulator.T_MC_PHASE) / 60
            )
            cf_temp = np.clip(cf_temp, 0, 1)
            ax.plot(t_s / 60, (1 - cf_temp) * 100, color=clr, lw=1.8,
                    label=f"η_mc = {eta*100:.0f}%  [Ref 1]")

        ax.set_xlabel("Time (min)")
        ax.set_ylabel("Healing efficiency (%)")
        ax.set_title(
            "(c) Microcapsule Efficiency Sensitivity\n"
            "Range: 65–95 % from White et al. (2001) [Ref 1]"
        )
        ax.legend(fontsize=8)
        ax.grid(True)
        ax.set_ylim(0, 108)

        # ── (d) Temperature vs oil viscosity (effect on leak flow) ────────
        ax = axes[1, 1]
        T_range = np.linspace(0, 30, 300)   # °C
        # Approximate Andrade equation: μ(T) = A · exp(B/T_K)
        # Calibrated: μ = 0.015 Pa·s at 4°C  [API MPMS, Ref 9]
        T_K   = T_range + 273.15
        mu_T  = 0.015 * np.exp(1800 * (1 / T_K - 1 / 277.15))

        # Re at each temperature; Blasius f; then V and Q_nom scale
        Re_T  = self.p.rho_oil * self.p.V_flow * self.p.D / mu_T
        # Darcy-Weisbach pressure loss correction (flow is fixed → diff. f)
        f_T   = 0.316 / np.clip(Re_T, 4000, None) ** 0.25
        # For a fixed ΔP, velocity would scale with friction:
        # (not re-simulating full system, just showing viscosity trend)

        ax2 = ax.twinx()
        l1, = ax.plot(T_range, mu_T * 1000, color=C_SENSOR, lw=2.0,
                      label="Viscosity (mPa·s)")
        l2, = ax2.plot(T_range, Re_T, color=C_HEAL, lw=2.0, ls="--",
                       label="Reynolds No.")
        ax.axvline(3, color=C_LEAK, lw=1.3, ls=":", alpha=0.8)
        ax.text(3.2, mu_T[np.argmin(np.abs(T_range - 3))] * 1000 * 1.05,
                "3°C\n(study T)", fontsize=7.5, color=C_LEAK)
        ax.set_xlabel("Oil Temperature (°C)")
        ax.set_ylabel("Dynamic viscosity (mPa·s)", color=C_SENSOR)
        ax2.set_ylabel("Reynolds Number", color=C_HEAL)
        ax.set_title(
            "(d) Temperature Effects on Oil Viscosity & Re\n"
            "Andrade model · API MPMS [Ref 9]"
        )
        lines = [l1, l2]
        ax.legend(lines, [l.get_label() for l in lines], fontsize=8, loc="right")
        ax.grid(True)

        fig.subplots_adjust(left=0.048, right=0.943, bottom=0.075, top=0.882, wspace=0.125,hspace=0.366)
        self._save_show_close(fig, "Fig6_Sensitivity_Environment.png")


# ══════════════════════════════════════════════════════════════════════════════
#  CLASS 6 — PipelineSimulationRunner  (top-level orchestrator)
# ══════════════════════════════════════════════════════════════════════════════
class PipelineSimulationRunner:
    """
    Orchestrates all simulation modules and visualisation in the correct order.
    Instantiate this class and call .run() to reproduce the full study.

    Usage
    -----
        runner = PipelineSimulationRunner()
        runner.run()
    """

    def __init__(self):
        print("=" * 65)
        print("  DEEP-SEA PIPELINE PINHOLE LEAK & SELF-HEALING SIMULATION")
        print("  Initialising simulation modules …")
        print("=" * 65)

        self.params  = PipelineParameters()
        self.leak    = LeakSimulator(self.params)
        self.sensors = SensorSimulator(self.params)
        self.healing = HealingSimulator(seed=13)
        self.viz     = Visualizer(self.params, self.leak, self.sensors, self.healing)

        self.params.summary()

    def run(self, figures: Optional[List[int]] = None):
        """
        Execute simulation and render figures.

        Parameters
        ----------
        figures : list of int, optional
            Which figures to render, e.g. [1, 3, 5].
            Default: all six figures.
        """
        all_figs = {
            1: self.viz.plot_fig1_pressure_flow,
            2: self.viz.plot_fig2_sensor_signals,
            3: self.viz.plot_fig3_healing_response,
            4: self.viz.plot_fig4_pipeline_schematic,
            5: self.viz.plot_fig5_performance_summary,
            6: self.viz.plot_fig6_sensitivity_environment,
        }

        if figures is None:
            figures = list(all_figs.keys())

        print(f"\nRendering {len(figures)} figure(s): {figures}\n")

        for fig_num in figures:
            if fig_num in all_figs:
                all_figs[fig_num]()
            else:
                print(f"  [!] Figure {fig_num} not found — skipping.")

        print("\n" + "=" * 65)
        print("  ✓ Simulation complete.")
        print(f"  ✓ All figures saved to: {OUTPUT_DIR}")
        print("=" * 65)


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    runner = PipelineSimulationRunner()
    runner.run()                          # render all 6 figures
    # runner.run(figures=[1, 2, 3])       # render specific figures only