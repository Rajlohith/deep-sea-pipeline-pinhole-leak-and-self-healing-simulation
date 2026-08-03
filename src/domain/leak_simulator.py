"""Leak simulator (Module 3): pressure and flow-rate physics for the pinhole leak."""
import numpy as np

from .pipeline_physics import PipelinePhysics


# ══════════════════════════════════════════════════════════════════════════════
# MODULE 3 — LEAK SIMULATOR  (pressure & flow physics)
# ══════════════════════════════════════════════════════════════════════════════
class LeakSimulator:
    """
    Computes pressure distribution and flow rates.

    Key equations:
      Pressure baseline  : P(x) = P_in·(1−x/L) + P_out·(x/L)    [Ref 8]
      Leak pressure drop : ΔP ≈ ½·ρ·(cf·A_pin/A_pipe)²·ΔP_total  [Ref 8]
      Leak flow rate     : Q = Cd·A_eff·√(2·ΔP/ρ)                [Ref 6]
      Sensor noise       : Gaussian + tidal sinusoid, ~0.3% span  [Ref 5]

    Layer relevance:
      Layer 3 (PMN-PT) monitors bulk wall pressure; Layer 4 (Quartz+Hydrophone)
      detects the orifice acoustic tone — both needed because pressure noise
      >> leak signal (<0.01%); Layer 6 DAS detects distributed vibration.
    """

    def __init__(self, phys: PipelinePhysics):
        self.p = phys

    def pressure_baseline(self, x: np.ndarray) -> np.ndarray:
        """Linear pressure drop — ideal pipe, no leak.  [Ref 8]"""
        frac = x / self.p.L
        return self.p.P_inlet * (1 - frac) + self.p.P_outlet * frac

    def pressure_with_leak(self, x: np.ndarray,
                           crack_fraction: float = 1.0) -> np.ndarray:
        """
        Pressure profile modified by pinhole.
        crack_fraction : 1.0 = fully open crack, 0.0 = Layer 5 fully healed
        """
        P       = self.pressure_baseline(x)
        dP_step = (0.5 * self.p.rho_oil
                   * (crack_fraction * self.p.A_pin / self.p.A_pipe) ** 2
                   * (self.p.P_inlet - self.p.P_outlet))
        P[x > self.p.X_leak_m] -= dP_step
        return P

    def sensor_noise(self, signal: np.ndarray,
                     amp_frac: float = 0.003, seed: int = 42) -> np.ndarray:
        """
        Deep-sea sensor noise superimposed on pressure signal:
          — Gaussian white noise  : instrument + electronic drift
          — Sinusoidal tidal term : 0.1 Hz tidal / pump-cycle fluctuation
        Amplitude ~ 0.3% of ΔP, consistent with Wenz (1962) noise model [Ref 5].
        This is what makes Layer 4 (Quartz+Hydrophone Hybrid) necessary —
        pressure sensors alone cannot resolve a 0.004% anomaly through 0.3%
        noise.  Layer 3 (PMN-PT) handles the bulk pressure and vibration tracking.
        """
        rng = np.random.default_rng(seed)
        amp = amp_frac * (self.p.P_inlet - self.p.P_outlet)
        n   = len(signal)
        return signal + amp * rng.standard_normal(n) + \
               amp * 0.5 * np.sin(np.linspace(0, 4 * np.pi, n))

    def flow_time_series(self, t_hours: np.ndarray) -> tuple:
        """24-hour flow at outlet: nominal, true-leak, noisy-sensor."""
        rng   = np.random.default_rng(99)
        Q_nom = self.p.Q_nom * np.ones_like(t_hours)
        Q_lk  = self.p.Q_nom * (1 - self.p.Q_leak_max / self.p.Q_nom) * np.ones_like(t_hours)
        noise = 0.006 * self.p.Q_nom * rng.standard_normal(len(t_hours))
        return Q_nom, Q_lk, Q_lk + noise

