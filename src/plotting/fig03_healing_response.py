"""Figure 3 - Healing Response over time after a leak is detected."""
import numpy as np
import matplotlib.pyplot as plt

from ..config import TXT_COL, C_NORMAL, C_LEAK, C_SENSOR, C_HEAL, LAYER_CLR
from ..domain.pipeline_physics import PipelinePhysics
from ..domain.leak_simulator import LeakSimulator
from ..domain.healing_system import HealingSystem
from .utils import _save, _save_split_panels


def fig3_healing_response(
    phys: PipelinePhysics,
    leak: LeakSimulator,
    heal: HealingSystem,
):
    print("[Fig 3] Layer 5 IPDI+FBE Self-Healing Response...")

    t = np.linspace(-30, 600, 1200)
    th = np.clip(t, 0, None)
    tm = t / 60

    cf = heal.crack_fraction(th)
    Ql = heal.leak_flow(th, phys) * 1000

    cfd = np.where(t < 0, 0.0, cf)
    Qld = np.where(t < 0, 0.0, Ql)

    m1 = (t >= 0) & (t <= heal.T_PH1_S)
    m2 = t > heal.T_PH1_S
    mcb = heal.T_PH1_S / 60

    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle(
        "FIG 3 - Layer 5 Hybrid Healing System (IPDI@SPUA + PTFE Vascular + SMP): Self-Healing Response\n"
        f"Three-mechanism: Chemical (IPDI@SPUA validated 150 bar [Ref 10]) + Vascular (PTFE [Ref 2]) + SMP closure\n"
        f"Hybrid efficiency eta = {heal.eta*100:.1f}% "
        f"(60-80% hybrid vs 55-75% IPDI-only; saline-corrected [Ref 13])",
        fontsize=10,
        fontweight="bold",
        color=C_NORMAL,
    )

    ax = axes[0, 0]
    ax.fill_between(tm, Qld, where=(t < 0), color=C_LEAK, alpha=0.30,
                    label="Pre-healing (uncontrolled)")
    ax.fill_between(tm, Qld, where=m1, color=LAYER_CLR[5], alpha=0.42,
                    label=f"Phase 1 - {heal.L5['phase1_name']}")
    ax.fill_between(tm, Qld, where=m2, color=C_HEAL, alpha=0.28,
                    label=f"Phase 2 - {heal.L5['phase2_name']}")
    ax.plot(tm, Qld, color="white", lw=1.8)
    ax.axvline(0, color=C_LEAK, lw=1.2, ls=":", alpha=0.8)
    ax.axvline(mcb, color=LAYER_CLR[5], lw=1.2, ls=":", alpha=0.8)
    ax.text(mcb + 0.05, max(Qld) * 0.55, "PTFE vascular\ntakes over",
            fontsize=7, color=LAYER_CLR[5])
    ax.set_xlabel("Time (min)")
    ax.set_ylabel("Leak flow (L/s)")
    ax.set_title(
        f"(a) Leak Flow vs Time\neta_Hybrid = {heal.eta*100:.1f}% (60-80% range: IPDI+PTFE+SMP) [Refs 10, 13]"
    )
    ax.legend(fontsize=7)
    ax.grid(True)

    ax = axes[0, 1]
    ax.fill_between(tm, cfd * 100, color=C_LEAK, alpha=0.15)
    ax.plot(tm, cfd * 100, color=C_LEAK, lw=2.0, label="Crack open (%)")
    ax.plot(tm, (1 - cfd) * 100, color=LAYER_CLR[5], lw=2.0, ls="--",
            label="Healed by IPDI+PTFE (%)")
    ax.axvline(mcb, color=LAYER_CLR[5], lw=1.2, ls=":", alpha=0.8)
    ax.set_xlabel("Time (min)")
    ax.set_ylabel("Fraction (%)")
    ax.set_title(
        "(b) Crack Open Area & Hybrid Healing Progress\n"
        "IPDI+PTFE+SMP [Toohey 2007, Ref 2 | Zeng 2025, Ref 10 | Hamilton, Ref 15]"
    )
    ax.legend(fontsize=7.5)
    ax.grid(True)
    ax.set_ylim(0, 108)

    ax = axes[1, 0]
    x4 = np.linspace(0, phys.L, 400)
    x4k = x4 / 1000
    snaps = [
        (0, "t=0s (crack forms)", C_LEAK),
        (30, "t=30s (IPDI sealing)", LAYER_CLR[5]),
        (60, "t=1min (PTFE starts)", "#ffaa00"),
        (300, "t=5min (vascular)", C_HEAL),
        (600, "t=10min (sealed)", C_NORMAL),
    ]
    for ts, lbl, clr in snaps:
        cf_s = heal.crack_fraction(np.array([float(ts)]))[0]
        ax.plot(x4k, leak.pressure_with_leak(x4.copy(), cf_s) / 1e5,
                color=clr, lw=1.5, label=lbl)
    ax.plot(x4k, leak.pressure_baseline(x4) / 1e5,
            color=TXT_COL, lw=1.0, ls=":", alpha=0.35, label="Baseline")
    ax.axvline(20, color=C_LEAK, lw=1.0, ls="--", alpha=0.4)
    ax.set_xlabel("Distance (km)")
    ax.set_ylabel("Pressure (bar)")
    ax.set_title("(c) Pressure Recovery - L5 Healing Snapshots")
    ax.legend(fontsize=6.5, loc="upper right")
    ax.grid(True)

    ax = axes[1, 1]
    tp = t[t >= 0]
    tpm = tp / 60
    tot, ph1, ph2 = heal.healing_efficiency_pct(tp)
    ax.stackplot(
        tpm,
        ph1,
        ph2,
        labels=[
            f"IPDI Capsule (Phase 1, eta={heal.eta*100:.0f}%)",
            "PTFE Vascular (Phase 2)",
        ],
        colors=[LAYER_CLR[5], C_HEAL],
        alpha=0.75,
    )
    ax.plot(tpm, tot, color="white", lw=2.0, label="Total efficiency")
    ax.axhline(heal.eta * 100, color=LAYER_CLR[5], lw=1.0, ls="--", alpha=0.6)
    ax.text(0.25, heal.eta * 100 + 1.5,
            f"IPDI plateau ~= {heal.eta*100:.0f}%\n[Refs 10, 13 - realistic deep-sea]",
            fontsize=7.5, color=LAYER_CLR[5])
    ax.axhline(80, color=C_SENSOR, lw=0.8, ls=":", alpha=0.5)
    ax.text(0.1, 81.5, "White 2001 lab benchmark (80%)",
            fontsize=6.5, color=C_SENSOR, alpha=0.7)
    ax.set_xlabel("Time (min)")
    ax.set_ylabel("Healing efficiency (%)")
    ax.set_title(
        "(d) Efficiency Breakdown: IPDI+SMP Phase 1 + PTFE+SMP Phase 2\n"
        "Hybrid [Zeng 2025, Ref 10] + [Toohey 2007, Ref 2]"
    )
    ax.legend(fontsize=7, loc="lower right")
    ax.grid(True)
    ax.set_xlim(0, tpm[-1])
    ax.set_ylim(0, 108)

    fig.subplots_adjust(left=0.06, right=0.98, bottom=0.07, top=0.86,
                        wspace=0.11, hspace=0.36)
    _save_split_panels(fig, [
        ("Fig3_Leak_Flow_vs_Time.svg", [axes[0, 0]]),
        ("Fig3_Crack_and_Healing_Progress.svg", [axes[0, 1]]),
        ("Fig3_Pressure_Recovery_Snapshots.svg", [axes[1, 0]]),
        ("Fig3_Healing_Efficiency_Breakdown.svg", [axes[1, 1]]),
    ])
    _save(fig, "Fig3_Healing_Response.svg")
