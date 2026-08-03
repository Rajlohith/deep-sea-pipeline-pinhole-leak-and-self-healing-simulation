"""Healing system (Module 5): Layer 5 hybrid self-healing model."""
import numpy as np

from .layer_architecture import LayerArchitecture
from .pipeline_physics import PipelinePhysics


# ══════════════════════════════════════════════════════════════════════════════
# MODULE 5 — LAYER 5 HEALING SYSTEM
# Critical improvement: IPDI water-reactive model instead of DCPD+Grubbs
# ══════════════════════════════════════════════════════════════════════════════
class HealingSystem:
    """
    Layer 5: Hybrid Healing System — IPDI@SPUA + PTFE vascular + SMP matrix.

    Architecture upgrade from single-agent to three-mechanism hybrid:
    ──────────────────────────────────────────────────────────────────
    Previous single-agent code used DCPD + Grubbs (White 2001 lab system),
    which fails at deep-sea conditions [Refs 12, 13].  The Hybrid Healing
    System stacks three complementary mechanisms:

      Mechanism A — IPDI@SPUA Chemical Capsules:
        - IPDI reacts WITH seawater → no catalyst needed [Ref 10]
        - 300 bar PROMOTES capsule rupture → faster activation [Ref 10]
        - Validated at 15 MPa (150 bar) seawater, 1008 h [Ref 10]
        - Contribution: chemical sealing, 55–75% efficiency [Refs 10, 13]

      Mechanism B — PTFE Vascular Network:
        - Pressurised PTFE microchannels deliver sealing fluid [Ref 2, 15]
        - Rate constant k = 0.05 min⁻¹ [Ref 2, Fig. 4]
        - Contribution: long-duration sealing, consolidation

      Mechanism C — Shape Memory Polymer (SMP) Matrix:
        - Elastic recovery from crude/seawater ΔT closes micro-cracks
        - Additional +5–10% efficiency [literature estimate]
        - Contribution: mechanical crack closure complement

    Combined efficiency: 60–80% (hybrid total, improved vs IPDI-only 55–75%).

    Two-Phase Simulation Model:
    ───────────────────────────
    Phase 1 — IPDI@SPUA + SMP sealing  (0–60 s):
      cf(t) = 1 − η·(1 − exp(−(t − t_onset)/τ_fill))
      η = 60–80% (hybrid efficiency)

    Phase 2 — PTFE vascular + SMP recovery  (60 s – 10 min):
      cf(t) = A₀·exp(−k·(t − 60)/60),  k = 0.05 min⁻¹ [Ref 2 Fig. 4]
    """

    T_PH1_S  = 60.0     # seconds — Phase 1 window (IPDI seal time)
    TAU_S    = 12.0     # seconds — capsule exponential time constant
    T_ONSET  = 5.0      # seconds — pressure-wave trigger delay [Ref 10]
    K_VASC   = 0.05     # min⁻¹  — PTFE vascular rate [Ref 2, Fig. 4]

    def __init__(self, arch: LayerArchitecture, seed: int = 13):
        L5  = arch.layers[5]
        rng = np.random.default_rng(seed)
        lo, hi = L5["efficiency_range"]
        # Draw IPDI sealing efficiency from realistic deep-sea range [Ref 10, 13]
        self.eta = float(rng.uniform(lo, hi))
        self.L5  = L5

    def crack_fraction(self, t_s: np.ndarray) -> np.ndarray:
        """
        Normalised open crack area (0 = fully sealed, 1 = fully open).
        t_s : time in seconds since crack formation (t < 0 → crack not yet formed)
        """
        t = np.asarray(t_s, dtype=float)
        r = np.ones_like(t)

        # Phase 1: IPDI capsule rupture & polyurea formation (0 to T_PH1_S)
        # Rapid sigmoid reduction — pressure-promoted rupture [Ref 10]
        m1 = (t >= 0) & (t <= self.T_PH1_S)
        if m1.any():
            decay   = np.exp(-(t[m1] - self.T_ONSET) / self.TAU_S)
            r[m1]   = 1.0 - self.eta * (1 - np.clip(decay, 0, 1))

        # Phase 2: PTFE vascular consolidation (t > T_PH1_S)
        # Slow exponential decay from residual open area [Ref 2, 15]
        m2 = t > self.T_PH1_S
        if m2.any():
            A0     = 1.0 - self.eta
            r[m2]  = A0 * np.exp(-self.K_VASC * (t[m2] - self.T_PH1_S) / 60.0)

        return np.clip(r, 0, 1)

    def healing_efficiency_pct(self, t_s: np.ndarray) -> tuple:
        """
        Returns (total%, phase1%, phase2%) healing efficiency.
        Used for stacked area chart.
        """
        cf      = self.crack_fraction(t_s)
        tot     = (1 - cf) * 100
        ph1     = np.clip(
            self.eta * (1 - np.exp(-t_s / (self.T_PH1_S / 5))) * 100,
            0, 100)
        ph2     = np.clip(tot - ph1, 0, None)
        return tot, ph1, ph2

    def leak_flow(self, t_s: np.ndarray, phys: PipelinePhysics) -> np.ndarray:
        """Q(t) = Cd·cf(t)·A_pin·√(2ΔP/ρ)  [ISO 5167, Ref 6]"""
        cf = self.crack_fraction(t_s)
        return phys.Cd * cf * phys.A_pin * np.sqrt(2 * phys.dP_orifice / phys.rho_oil)

    def cumulative_loss_L(self, t_end_s: float,
                          phys: PipelinePhysics, n: int = 300) -> float:
        """Integrate Q(t) by trapezoid rule → litres."""
        t = np.linspace(0, t_end_s, n)
        return float(np.trapezoid(self.leak_flow(t, phys), t)) * 1000
