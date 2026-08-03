"""Sensor system (Module 4): Layer 3 hydrophone + Layer 6 DAS sensing."""
import numpy as np

from .layer_architecture import LayerArchitecture
from .pipeline_physics import PipelinePhysics


# ══════════════════════════════════════════════════════════════════════════════
# MODULE 4 — SENSOR SYSTEM  (Layer 3 Hydrophone + Layer 6 DAS)
# ══════════════════════════════════════════════════════════════════════════════
class SensorSystem:
    """
    Simulates the three sensing modalities of Layers 3, 4, and 6.

    Layer 3 — PMN-PT + Floating Ceramic Shock Mount:
      Broadband pressure / vibration transducer (d33 ~2000 pC/N).
      Monitors bulk wall pressure, water-hammer transients, and vibration.
      Floating mount provides ~20 dB structure-borne noise rejection.

    Layer 4 — Quartz + Hydrophone Hybrid:
      Time-domain acoustic signal at the pipe wall.
      Orifice vortex shedding tone: f = St·V_jet/d_pin  [Ref 8 Strouhal]
      Quartz element for frequency reference; hydrophone for sensitivity.
      Background: Wenz (1962) ocean ambient noise [Ref 5]

    Layer 6 — Dual Redundant Fiber Optics (DAS):
      Rayleigh backscatter vibration amplitude along the pipe [Ref 4].
      Gaussian spatial profile centred at leak (σ = 500 m).
      Primary fibre (A) + backup fibre (B) — instant failover.
    """

    def __init__(self, phys: PipelinePhysics, arch: LayerArchitecture):
        self.p  = phys
        self.arch = arch
        # Vortex frequency from Strouhal number [Ref 8]:
        # V_jet = √(2·ΔP/ρ) via Torricelli; St = 0.2 for sharp orifice
        # Strouhal parameter now resides in Layer 4 (Quartz+Hydrophone Hybrid)
        V_jet          = np.sqrt(2 * phys.dP_orifice / phys.rho_oil)
        self.f_orifice = arch.layers[4]["strouhal_St"] * V_jet / phys.d_pin

    # ── Layer 4: Quartz + Hydrophone Hybrid signal ───────────────────────────
    def hydrophone_signal(self, t: np.ndarray,
                          has_leak: bool, healed: bool,
                          seed: int = 7) -> np.ndarray:
        """
        Time-domain Quartz+Hydrophone Hybrid signal (Layer 4).
        Wenz (1962) ambient [Ref 5] + orifice tone when leak is active.
        Quartz element provides stable frequency reference; hydrophone detects
        far-field acoustic tone.  Intermittent burst models vortex intermittency.
        """
        rng    = np.random.default_rng(seed)
        ambient = (0.30 * rng.standard_normal(len(t))
                   + 0.15 * np.sin(2 * np.pi * 0.1 * t))  # tidal noise [Ref 5]
        if has_leak:
            amp   = 0.80 if not healed else 0.10
            burst = np.where(np.abs(np.sin(2 * np.pi * 0.3 * t)) > 0.6, 1.0, 0.0)
            ambient += amp * np.sin(2 * np.pi * self.f_orifice * t) * burst
        return ambient

    # ── Layer 6: Dual Redundant Fiber Optics DAS vibration along pipeline ──────
    def das_signal(self, x: np.ndarray,
                   has_leak: bool, healed: bool,
                   fiber: str = "primary") -> np.ndarray:
        """
        Distributed Acoustic Sensing vibration amplitude vs distance.
        Gaussian bump at leak; σ = 500 m spatial spread [Ref 4].
        fiber='primary' → Fiber A; 'backup' → Fiber B (slight noise variation).
        """
        seed_off = 0 if fiber == "primary" else 17
        rng      = np.random.default_rng(seed_off)
        bg       = 0.05 + 0.02 * rng.standard_normal(len(x))
        if has_leak:
            amp = 0.45 if not healed else 0.05
            bg += amp * np.exp(-0.5 * ((x - self.p.X_leak_m) / 500) ** 2)
        return np.clip(bg, 0, None)

    # ── Utility: SNR & FFT ────────────────────────────────────────────────────
    @staticmethod
    def snr_db(signal: np.ndarray, background: np.ndarray) -> float:
        Ps = np.mean(signal ** 2)
        Pb = np.mean(background ** 2)
        return 10 * np.log10(max(Ps, 1e-15) / max(Pb, 1e-15))

    @staticmethod
    def rfft_norm(signal: np.ndarray, dt: float) -> tuple:
        freqs = np.fft.rfftfreq(len(signal), d=dt)
        mag   = np.abs(np.fft.rfft(signal))
        return freqs, mag / max(mag.max(), 1e-12)

