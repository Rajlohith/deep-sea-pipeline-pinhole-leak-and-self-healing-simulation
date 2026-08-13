"""Figure 5 - Intelligence Layer: sensing, communication and power overview."""
import numpy as np
import matplotlib.pyplot as plt

from ..config import TXT_COL, C_NORMAL, C_LEAK, C_SENSOR, C_HEAL, LAYER_CLR
from ..domain.layer_architecture import LayerArchitecture
from ..domain.pipeline_physics import PipelinePhysics
from ..domain.sensor_system import SensorSystem
from ..domain.power_system import PowerSystem
from .utils import _save, _save_split_panels


def fig5_intelligence_layer(
    phys: PipelinePhysics,
    arch: LayerArchitecture,
    sensors: SensorSystem,
    power: PowerSystem,
):
    print("[Fig 5] Step 4 Intelligence: DAS Redundancy + Power System...")

    x = np.linspace(0, phys.L, 500)
    xk = x / 1000

    fig, axes = plt.subplots(2, 2, figsize=(15, 9))
    fig.suptitle(
        "FIG 5 - STEP 4: Central Core & Intelligence\n"
        "Layer 6 Dual Redundant Fiber Optics DAS · "
        "Layer 7 Hybrid Power Layer (Piezo+TEG Harvest + Li-Thionyl Backup)",
        fontsize=11, fontweight="bold", color=C_NORMAL)

    ax = axes[0, 0]
    das_A = sensors.das_signal(x, True, False, "primary")
    das_B = sensors.das_signal(x, True, False, "backup")
    ax.plot(xk, das_A, color=LAYER_CLR[6], lw=2.0, label="Fiber A (primary - active)")
    ax.plot(xk, das_B, color=C_NORMAL, lw=1.2, ls="--", alpha=0.65,
            label="Fiber B (backup - standby)")
    ax.axvline(20, color=C_LEAK, lw=1.3, ls="--", label="Pinhole @20 km")
    ax.fill_between(xk, das_B, alpha=0.10, color=C_HEAL,
                    label="Failover region (B activates if A fails)")
    ax.set_xlabel("Distance (km)")
    ax.set_ylabel("DAS vibration (a.u.)")
    ax.set_title("(a) L6 Dual Redundant Fiber Optics - Instant Failover\n"
                 "Pressure cannot affect light propagation [Project images]")
    ax.legend(fontsize=7.5)
    ax.grid(True)
    ax.set_xlim(0, 50)

    ax = axes[0, 1]
    bg_d = sensors.das_signal(x, False, False, "primary")
    states_b = [("No Leak", False, False, C_NORMAL),
                ("Active Leak", True, False, C_LEAK),
                ("After Healing", True, True, C_HEAL)]
    snrs = [
        SensorSystem.snr_db(sensors.das_signal(x, hl, hd, "primary"), bg_d)
        for _, hl, hd, _ in states_b
    ]
    colors_b = [s[3] for s in states_b]
    bars = ax.bar(range(3), snrs, color=colors_b, alpha=0.82,
                  edgecolor="white", lw=0.5)
    for bar, v in zip(bars, snrs):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.3,
                f"{v:.1f} dB", ha="center", fontsize=9, color=TXT_COL)
    ax.axhline(6.0, color=C_SENSOR, lw=1.5, ls="--",
               label="Detection threshold (6 dB)")
    ax.set_xticks(range(3))
    ax.set_xticklabels([s[0] for s in states_b], fontsize=9)
    ax.set_ylabel("SNR (dB)")
    ax.set_title(
        f"(b) L6 Dual Redundant Fiber DAS SNR - Three States\n"
        f"Detection time < {arch.layers[6]['detection_time_s']} s [Bao & Chen 2012, Ref 4]"
    )
    ax.legend(fontsize=8)
    ax.grid(True, axis="y", alpha=0.4)

    ax = axes[1, 0]
    t_yr = np.linspace(0, 12, 300)
    for pw, clr, lbl in [
        (10, C_LEAK, "10 W (full active system)"),
        (5, LAYER_CLR[7], "5 W (standby mode)"),
        (2, C_HEAL, "2 W (minimal monitoring)"),
    ]:
        ax.plot(t_yr, power.soc_pct(t_yr, pw), color=clr, lw=2.0, label=lbl)
    ax.axhline(20, color=C_SENSOR, lw=1.2, ls="--", alpha=0.7,
               label="Low battery threshold (20%)")
    ax.axvline(arch.layers[7]["battery_life_yr"], color=TXT_COL,
               lw=1.0, ls=":", alpha=0.5,
               label=f"Rated life ({arch.layers[7]['battery_life_yr']} yr)")
    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Battery SOC (%)")
    ax.set_title(
        f"(c) L7 Hybrid Power - Battery SOC vs Time (w/ Harvesting)\n"
        f"{arch.layers[7]['battery_Wh']} Wh backup  |  ~{arch.layers[7]['total_harvest_mW']} mW harvested (Piezo+TEG offset)"
    )
    ax.legend(fontsize=7.5)
    ax.grid(True)
    ax.set_ylim(0, 105)

    ax = axes[1, 1]
    depths = np.linspace(0, 7000, 300)
    T_saph = power.transmittance(depths) * 100
    ax.plot(depths, T_saph, color=LAYER_CLR[7], lw=2.5,
            label="Sapphire window transmittance")
    ax.axvline(3000, color=C_LEAK, lw=1.5, ls="--", label="Study depth (3,000 m)")
    ax.axvline(6000, color=C_SENSOR, lw=1.5, ls=":", label="Sapphire depth rating (6,000 m)")
    T_3k = power.transmittance(np.array([3000.0]))[0] * 100
    ax.scatter([3000], [T_3k], color=C_LEAK, s=100, zorder=10)
    ax.text(3100, T_3k + 0.8, f"{T_3k:.1f}% @ 3,000 m", fontsize=8, color=C_LEAK)
    ax.fill_between(depths, T_saph,
                    where=(depths <= arch.layers[7]["sapphire_depth_m"]),
                    alpha=0.12, color=LAYER_CLR[7], label="Operational envelope")
    ax.set_xlabel("Depth (m)")
    ax.set_ylabel("Optical Transmittance (%)")
    ax.set_title("(d) L7 Hybrid Power - Sapphire Optical Port Transmittance vs Depth\n"
                 "Mohs 9 hardness | 6,000 m rated | Retained in Hybrid Power Layer")
    ax.legend(fontsize=7.5)
    ax.grid(True)
    ax.set_ylim(70, 92)

    fig.subplots_adjust(left=0.06, right=0.98, bottom=0.07, top=0.88,
                        wspace=0.15, hspace=0.34)
    _save_split_panels(fig, [
        ("Fig5_Dual_DAS_Failover.svg", [axes[0, 0]]),
        ("Fig5_DAS_SNR_Comparison.svg", [axes[0, 1]]),
        ("Fig5_Battery_SOC.svg", [axes[1, 0]]),
        ("Fig5_Sapphire_Transmittance.svg", [axes[1, 1]]),
    ])
    _save(fig, "Fig5_Intelligence_Layer.svg")
