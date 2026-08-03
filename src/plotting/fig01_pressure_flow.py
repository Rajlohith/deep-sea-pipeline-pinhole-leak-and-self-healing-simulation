"""Figure 1 — Pressure Profile & Flow Rate.

Purpose: demonstrate WHY Layer 3 hydrophone is necessary.
The 0.5 mm pinhole creates a 0.004% flow anomaly — invisible in +/-0.6% noise.
"""
import numpy as np
import matplotlib.pyplot as plt

from ..config import MID_BG, TXT_COL, C_NORMAL, C_LEAK, C_SENSOR
from ..domain.pipeline_physics import PipelinePhysics
from ..domain.leak_simulator import LeakSimulator
from .utils import _save


# ══════════════════════════════════════════════════════════════════════════════
# FIG 1 — Pressure Profile & Flow Rate
# Purpose: demonstrate WHY Layer 3 hydrophone is necessary.
# The 0.5 mm pinhole creates a 0.004% flow anomaly — invisible in ±0.6% noise.
# ══════════════════════════════════════════════════════════════════════════════
def fig1_pressure_flow(phys: PipelinePhysics, leak: LeakSimulator):
    print("[Fig 1] Pressure Profile & Flow Rate …")
    N  = 400
    x  = np.linspace(0, phys.L, N)
    xk = x / 1000

    Pb = leak.pressure_baseline(x) / 1e5
    Pl = leak.pressure_with_leak(x.copy(), 1.0) / 1e5
    Pn = leak.sensor_noise(leak.pressure_with_leak(x.copy(), 1.0)) / 1e5

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("FIG 1 — Pinhole Leak: Pressure Profile & Flow Rate\n"
                 "Key insight: 0.004% signal buried in 0.6% sensor noise "
                 "→ Layer 4 Quartz+Hydrophone Hybrid is mandatory",
                 fontsize=11, fontweight="bold", color=C_NORMAL, y=1.02)

    # (a) Pressure vs distance
    ax1.plot(xk, Pb, color=C_NORMAL, lw=2.0, label="Baseline (no leak)")
    ax1.plot(xk, Pn, color=C_SENSOR, lw=0.85, alpha=0.65, label="Sensor signal (noisy)")
    ax1.plot(xk, Pl, color=C_LEAK,   lw=2.0, ls="--", label="True leak signal")
    ax1.axvline(20, color=C_LEAK, lw=1.2, ls=":", alpha=0.8)
    ax1.annotate("Pinhole @ 20 km\n(L4→detect, L5→heal)",
                 xy=(20, 120), xytext=(25, 130), fontsize=7.5, color=C_LEAK,
                 arrowprops=dict(arrowstyle="->", color=C_LEAK))
    ax1.set_xlabel("Distance (km)"); ax1.set_ylabel("Pressure (bar)")
    ax1.set_title("(a) Spatial Pressure Profile — Leak Hidden in Noise\n"
                  "Δp = 0.005 bar (buried in ±1.5 bar noise)")
    ax1.legend(fontsize=7.5); ax1.grid(True); ax1.set_xlim(0, 50)

    # Inset zoom around leak
    ins = ax1.inset_axes([0.33, 0.55, 0.30, 0.38])
    m   = (xk > 18) & (xk < 22)
    ins.plot(xk[m], Pb[m], color=C_NORMAL, lw=1.3)
    ins.plot(xk[m], Pn[m], color=C_SENSOR, lw=0.7, alpha=0.8)
    ins.plot(xk[m], Pl[m], color=C_LEAK,   lw=1.3, ls="--")
    ins.axvline(20, color=C_LEAK, lw=0.8, ls=":")
    ins.set_title("zoom @20 km", fontsize=6, color=TXT_COL)
    ins.tick_params(labelsize=5); ins.set_facecolor("#0d1b2a")
    ax1.indicate_inset_zoom(ins, edgecolor=C_SENSOR)

    # (b) Flow rate vs time
    t_h  = np.linspace(0, 24, 600)
    Qn, Ql, Qnoisy = leak.flow_time_series(t_h)
    dpct = phys.Q_leak_max / phys.Q_nom * 100

    ax2.plot(t_h, Qn    * 1000, color=C_NORMAL, lw=2.0, label="Nominal (no leak)")
    ax2.plot(t_h, Qnoisy* 1000, color=C_SENSOR, lw=0.85, alpha=0.65, label="Sensor reading")
    ax2.plot(t_h, Ql    * 1000, color=C_LEAK,   lw=2.0, ls="--", label="True leaking flow")
    ax2.fill_between(t_h,
                     (Qn - 0.01*phys.Q_nom)*1000,
                     (Qn + 0.01*phys.Q_nom)*1000,
                     color=C_NORMAL, alpha=0.07, label="±1% noise threshold")
    ax2.text(12, Ql[0]*1000 - 0.24,
             f"Δflow = {dpct:.4f}%\n(below ±1% noise)\nL3+L6 SNR: ~12 dB",
             fontsize=8, color=C_LEAK,
             bbox=dict(boxstyle="round,pad=0.3", facecolor=MID_BG,
                       edgecolor=C_LEAK, alpha=0.88))
    ax2.set_xlabel("Time (hours)"); ax2.set_ylabel("Flow rate (L/s)")
    ax2.set_title("(b) Outlet Flow Rate — Pinhole Signal Below Noise Floor\n"
                  "→ Mandates Layer 4 (Quartz+Hydrophone) + Layer 6 (Dual Fiber DAS)")
    ax2.legend(fontsize=7.5); ax2.grid(True)
    fig.tight_layout()
    _save(fig, "Fig1_Pressure_Flow.png")

