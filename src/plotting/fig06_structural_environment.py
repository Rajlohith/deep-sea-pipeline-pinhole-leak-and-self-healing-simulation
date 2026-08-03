"""Figure 6 — Structural & Environmental summary of the pipeline system."""
import numpy as np
import matplotlib.pyplot as plt

from ..config import C_NORMAL, C_LEAK, C_SENSOR, C_HEAL, LAYER_CLR
from ..domain.layer_architecture import LayerArchitecture
from ..domain.pipeline_physics import PipelinePhysics
from ..domain.healing_system import HealingSystem
from .utils import _save


# ══════════════════════════════════════════════════════════════════════════════
# FIG 6 — Structural & Environmental Properties (Layers 1, 2, 4 + sensitivity)
# ══════════════════════════════════════════════════════════════════════════════
def fig6_structural_environment(phys: PipelinePhysics, arch: LayerArchitecture,
                                 heal: HealingSystem):
    print("[Fig 6] Structural & Environmental Properties …")

    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle(
        "FIG 6 — Steps 1–3: Structural, Environmental & Acoustic Layer Properties\n"
        "L1 (UE44/TMA+Basalt) · L2 (Inconel 625) · L4 (Quartz+Hydrophone) · Pinhole Sensitivity",
        fontsize=11, fontweight="bold", color=C_NORMAL)

    # (a) Depth vs external pressure — Layer 1 rating
    ax = axes[0, 0]
    d  = np.linspace(0, 4200, 400)
    Pe = 1025 * 9.81 * d / 1e5       # bar
    ax.plot(d, Pe, color=LAYER_CLR[1], lw=2.0, label="Hydrostatic P = ρ·g·h")
    ax.axhline(arch.layers[1]["pressure_rating_bar"], color=C_HEAL, lw=1.5,
               ls="--", label=f"L1 rating: {arch.layers[1]['pressure_rating_bar']} bar ✓")
    ax.axvline(3000, color=C_LEAK, lw=1.3, ls=":", alpha=0.8)
    ax.scatter([3000], [phys.P_ext/1e5], color=C_LEAK, s=90, zorder=5)
    ax.text(3100, phys.P_ext/1e5 + 3,
            f"Study: {phys.P_ext/1e5:.0f} bar\n@ 3,000 m", fontsize=7.5, color=C_LEAK)
    ax.fill_between(d, Pe, where=(d <= 3000), color=LAYER_CLR[1], alpha=0.07)
    ax.set_xlabel("Ocean Depth (m)"); ax.set_ylabel("Hydrostatic Pressure (bar)")
    ax.set_title("(a) L1 (UE44/TMA Syntactic Foam + Basalt Fiber) — Pressure vs Depth\n"
                 "UE44/TMA rated 350 bar | Basalt fiber: 4,800 MPa tensile strength")
    ax.legend(fontsize=8); ax.grid(True)

    # (b) Inconel 625 corrosion vs carbon steel vs 316L
    ax = axes[0, 1]
    yr = np.linspace(0, 25, 200)
    ax.plot(yr, 0.15 * yr, color=C_LEAK,       lw=2.0, label="Carbon steel (0.15 mm/yr)")
    ax.plot(yr, 0.05 * yr, color=C_SENSOR,     lw=2.0, label="Stainless 316L (0.05 mm/yr)")
    ax.plot(yr, arch.layers[2]["corrosion_mm_yr"] * yr,
            color=LAYER_CLR[2], lw=2.5,
            label=f"L2 Inconel 625 ({arch.layers[2]['corrosion_mm_yr']} mm/yr ≈ 0)")
    ax.fill_between(yr, arch.layers[2]["corrosion_mm_yr"]*yr, alpha=0.25, color=LAYER_CLR[2])
    ax.set_xlabel("Service Life (years)"); ax.set_ylabel("Cumulative Corrosion (mm)")
    ax.set_title("(b) L2 Inconel 625 — Corrosion Resistance in Seawater\n"
                 "Near-zero corrosion — used in deep-sea wellheads for decades")
    ax.legend(fontsize=8); ax.grid(True)

    # (c) Pinhole size sensitivity — Q vs d_pin  [ISO 5167, Ref 6]
    ax = axes[1, 0]
    d_range = np.linspace(0.1e-3, 2.0e-3, 200)
    Q_range = [phys.Cd * np.pi*(d/2)**2
               * np.sqrt(2*phys.dP_orifice/phys.rho_oil)*1000
               for d in d_range]
    ax.plot(d_range*1000, Q_range, color=C_SENSOR, lw=2.0,
            label="Q = Cd·A·√(2ΔP/ρ)  [ISO 5167, Ref 6]")
    ax.axvline(0.5, color=C_LEAK, lw=1.5, ls="--", label="Study: 0.5 mm pinhole")
    ax.axhline(phys.Q_leak_max*1000, color=LAYER_CLR[5], lw=1.3, ls=":",
               label=f"Q_max = {phys.Q_leak_max*1000:.4f} L/s")
    ax.scatter([0.5], [phys.Q_leak_max*1000], color=C_LEAK, s=100, zorder=6)
    ax.set_xlabel("Pinhole diameter (mm)"); ax.set_ylabel("Max leak flow (L/s)")
    ax.set_title("(c) Pinhole Size Sensitivity\n"
                 "L4 Quartz+Hydrophone: <0.01% flow loss detectable")
    ax.legend(fontsize=7.5); ax.grid(True)

    # (d) L4 Quartz+Hydrophone — Acoustic SNR vs Frequency
    # Shows SNR advantage of the hybrid detector vs single-element quartz
    ax = axes[1, 1]
    freq  = np.logspace(0, 5, 500)          # 1 Hz – 100 kHz
    # Single quartz SNR: baseline roll-off above resonance
    snr_q = 20 * np.log10(np.clip(1 / (1 + (freq / 10000)**2), 1e-4, 1)) + 15
    # Hydrophone SNR: broader band, peaks near orifice frequency
    snr_h = 20 * np.log10(np.clip(1 / (1 + (freq / 50000)**2), 1e-4, 1)) + 20
    # Hybrid (matched-filter combination): SNR gain of hybrid_snr_gain_dB
    snr_hybrid = snr_q + arch.layers[4]["hybrid_snr_gain_dB"]

    ax.semilogx(freq, snr_q,      color=C_SENSOR,     lw=1.5, ls="--",
                label="Quartz only (ref element)")
    ax.semilogx(freq, snr_h,      color=LAYER_CLR[4], lw=1.5, ls=":",
                label="Hydrophone only")
    ax.semilogx(freq, snr_hybrid, color=C_HEAL,       lw=2.5,
                label=f"L4 Hybrid (+{arch.layers[4]['hybrid_snr_gain_dB']:.0f} dB matched-filter)")
    # Mark Strouhal orifice tone frequency
    ax.axvline(heal.L5["phase1_time_s"], color=C_LEAK, lw=1.2, ls=":", alpha=0.5)
    # Mark detection threshold
    ax.axhline(6.0, color=C_LEAK, lw=1.3, ls="--", alpha=0.8,
               label="Detection threshold (6 dB)")
    ax.set_xlabel("Frequency (Hz)"); ax.set_ylabel("Relative SNR (dB)")
    ax.set_title("(d) L4 Quartz+Hydrophone Hybrid — Acoustic SNR vs Frequency\n"
                 "Hybrid matched-filter gains +6 dB over single-element  [Ref 4, 8]")
    ax.legend(fontsize=7.5); ax.grid(True, alpha=0.4)
    ax.set_ylim(-5, 30)

    fig.subplots_adjust(left=0.05, right=0.94, bottom=0.07, top=0.88,
                        wspace=0.16, hspace=0.38)
    _save(fig, "Fig6_Structural_Environment.png")

