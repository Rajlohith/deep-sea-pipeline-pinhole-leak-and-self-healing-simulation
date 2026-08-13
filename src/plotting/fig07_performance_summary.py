"""Figure 7 - Overall Performance Summary dashboard."""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Rectangle

from ..config import PANEL_BG, GRID_COL, TXT_COL, C_NORMAL, C_LEAK, C_HEAL, LAYER_CLR
from ..domain.layer_architecture import LayerArchitecture
from ..domain.pipeline_physics import PipelinePhysics
from ..domain.healing_system import HealingSystem
from .utils import _save, _save_split_panels


def fig7_performance_summary(
    phys: PipelinePhysics,
    arch: LayerArchitecture,
    heal: HealingSystem,
):
    print("[Fig 7] Performance Summary Dashboard...")

    fig = plt.figure(figsize=(16, 7))
    fig.suptitle(
        "FIG 7 - 7-Layer Smart Pipeline: System Reliability vs Traditional Approach\n"
        f"Hybrid Healing System (eta = {heal.eta*100:.1f}%) vs traditional detection (>24 hr lag)",
        fontsize=11, fontweight="bold", color=C_NORMAL)
    gs = gridspec.GridSpec(1, 3, figure=fig, wspace=0.38)

    loss_h = heal.cumulative_loss_L(600, phys)
    loss_t = phys.Q_leak_max * 86400 * 1000

    axk = fig.add_subplot(gs[0, 0])
    axk.axis("off")
    axk.add_patch(Rectangle((0, 0), 1, 1, transform=axk.transAxes,
                            facecolor=PANEL_BG, edgecolor=GRID_COL, lw=1))

    lines = [
        ("-- 7-LAYER PARAMS --", C_NORMAL, True),
        (f"  Depth       : {phys.depth_m:.0f} m", TXT_COL, False),
        (f"  Ext. P      : {phys.P_ext/1e5:.0f} bar", TXT_COL, False),
        (f"  L1 rated    : {arch.layers[1]['pressure_rating_bar']} bar", C_HEAL, False),
        (f"  L2 corr.    : {arch.layers[2]['corrosion_mm_yr']} mm/yr", TXT_COL, False),
        (f"  Pinhole D   : {phys.d_pin*1000:.1f} mm", TXT_COL, False),
        (f"  Reynolds    : {phys.Re:.0f}", TXT_COL, False),
        ("", TXT_COL, False),
        ("-- L3+L4+L6 DETECTION --", LAYER_CLR[3], True),
        ("  Trad. SNR   : < 3 dB", C_LEAK, False),
        ("  L4+L6 SNR   : ~12 dB", C_HEAL, False),
        ("  Trad. detect: >24 hours", C_LEAK, False),
        ("  L3+L4+L6 < 30 s", C_HEAL, False),
        ("", TXT_COL, False),
        ("-- LAYER 5 HYBRID HEAL --", LAYER_CLR[5], True),
        ("  IPDI@SPUA+PTFE+SMP", LAYER_CLR[5], False),
        ("  NOT DCPD: fails at 3C/", TXT_COL, False),
        ("  300bar/saltwater [Ref 12]", TXT_COL, False),
        (f"  eta hybrid : {heal.eta*100:.1f}% [Refs 10,13]", LAYER_CLR[5], False),
        (f"  k_PTFE : {heal.K_VASC} min^-1 [Ref 2]", C_HEAL, False),
        ("  Full seal  : ~10 min", C_HEAL, False),
        ("", TXT_COL, False),
        ("-- L6 DUAL REDUNDANT --", LAYER_CLR[6], True),
        ("  Dual fibers: instant B->A", LAYER_CLR[6], False),
        ("  Pressure immune (light)", C_HEAL, False),
        ("", TXT_COL, False),
        ("-- OIL LOSS (24 hr) --", C_NORMAL, True),
        (f"  No healing : {loss_t:.0f} L", C_LEAK, False),
        (f"  L5 system  : ~{loss_h:.1f} L", C_HEAL, False),
        (f"  Reduction  : >{(1 - loss_h/loss_t)*100:.0f}%", C_HEAL, True),
        ("", TXT_COL, False),
        ("-- SYSTEM SURVIVAL --", C_NORMAL, True),
        (f"  {arch.overall_survival():.2f}% (all 7 layers)", C_HEAL, True),
    ]
    y = 0.97
    for text, clr, bold in lines:
        if text == "":
            y -= 0.016
            continue
        axk.text(0.04, y, text, transform=axk.transAxes,
                 fontsize=7.0, va="top", color=clr,
                 fontweight="bold" if bold else "normal",
                 fontfamily="monospace")
        y -= 0.034
    axk.set_title("7-Layer KPI Summary", fontsize=9, color=C_NORMAL)

    axr = fig.add_subplot(gs[0, 1], polar=True)
    cats = ["Detection\nSpeed", "Detection\nAccuracy", "Leak\nContainment",
            "System\nReliability", "Response\nTime", "Long-term\nSealing"]
    ang = np.linspace(0, 2 * np.pi, len(cats), endpoint=False).tolist() + [0]
    trad = [1.5, 2.0, 1.0, 2.5, 1.5, 1.0, 1.5]
    smart = [9.5, 9.0, 9.5, 9.2, 9.3, 9.0, 9.5]
    axr.set_facecolor(PANEL_BG)
    axr.plot(ang, trad, color=C_LEAK, lw=2.0, ls="--", label="Traditional")
    axr.fill(ang, trad, color=C_LEAK, alpha=0.15)
    axr.plot(ang, smart, color=LAYER_CLR[5], lw=2.0, label="7-Layer Smart")
    axr.fill(ang, smart, color=LAYER_CLR[5], alpha=0.20)
    axr.set_xticks(ang[:-1])
    axr.set_xticklabels(cats, fontsize=7, color=TXT_COL)
    axr.set_ylim(0, 10)
    axr.set_yticks([2, 4, 6, 8, 10])
    axr.set_yticklabels(["2", "4", "6", "8", "10"], fontsize=5.5, color=GRID_COL)
    axr.grid(color=GRID_COL, lw=0.7)
    axr.spines["polar"].set_color(GRID_COL)
    axr.legend(loc="lower center", bbox_to_anchor=(0.5, -0.28), ncol=1, fontsize=8)
    axr.set_title("Performance Radar (score /10)", fontsize=8.5, color=C_NORMAL, pad=16)

    axb = fig.add_subplot(gs[0, 2])
    labels_b = ["1 min", "10 min", "1 hr", "6 hr", "24 hr"]
    times_b = [60, 600, 3600, 21600, 86400]
    loss_trad = [phys.Q_leak_max * tv * 1000 for tv in times_b]
    loss_smart = [heal.cumulative_loss_L(tv, phys) for tv in times_b]
    xb = np.arange(len(labels_b))
    w = 0.35
    b1 = axb.bar(xb - w / 2, loss_trad, width=w, color=C_LEAK, alpha=0.82,
                 edgecolor="white", lw=0.5, label="Traditional (no healing)")
    b2 = axb.bar(xb + w / 2, loss_smart, width=w, color=LAYER_CLR[5], alpha=0.82,
                 edgecolor="white", lw=0.5, label="7-Layer Hybrid Healing")
    for bar in b1:
        v = bar.get_height()
        axb.text(bar.get_x() + bar.get_width() / 2, v * 1.06, f"{v:.0f}",
                 ha="center", va="bottom", fontsize=5.5, color=C_LEAK)
    for bar in b2:
        v = bar.get_height()
        axb.text(bar.get_x() + bar.get_width() / 2, v * 1.06,
                 f"{v:.2f}" if v < 10 else f"{v:.0f}",
                 ha="center", va="bottom", fontsize=5.5, color=LAYER_CLR[5])
    axb.set_yscale("log")
    axb.set_xticks(xb)
    axb.set_xticklabels(labels_b, fontsize=7.5)
    axb.set_ylabel("Cumulative oil loss (L, log scale)")
    axb.set_title("Oil Loss: Traditional vs 7-Layer Hybrid Healing\n"
                  "L5 Hybrid (IPDI+PTFE+SMP) sealing performance [Ref 10]")
    axb.legend(fontsize=8)
    axb.grid(True, axis="y", alpha=0.35)

    fig.subplots_adjust(left=0.06, right=0.98, top=0.88, bottom=0.12)
    _save_split_panels(fig, [
        ("Fig7_KPI_Summary.svg", [axk]),
        ("Fig7_Performance_Radar.svg", [axr]),
        ("Fig7_Oil_Loss_Comparison.svg", [axb]),
    ])
    _save(fig, "Fig7_Performance_Summary.svg")
