"""Figure 2 - Sensor Signals across the pipeline's sensing layers."""
import numpy as np
import matplotlib.pyplot as plt

from ..config import MID_BG, TXT_COL, C_NORMAL, C_LEAK, C_HEAL, LAYER_CLR
from ..domain.layer_architecture import LayerArchitecture
from ..domain.pipeline_physics import PipelinePhysics
from ..domain.sensor_system import SensorSystem
from .utils import _save, _save_split_panels


def fig2_sensor_signals(
    phys: PipelinePhysics,
    arch: LayerArchitecture,
    sensors: SensorSystem,
):
    print("[Fig 2] Layer 3 Hydrophone + Layer 6 DAS Sensor Comparison...")
    x2 = np.linspace(0, phys.L, 500)
    x2k = x2 / 1000
    t2 = np.linspace(0, 20, 1000)
    dt2 = t2[1] - t2[0]

    states = [
        ("No Leak", False, False, C_NORMAL),
        ("Active Leak", True, False, C_LEAK),
        ("After L5 Hybrid Healing", True, True, C_HEAL),
    ]

    bg_das = sensors.das_signal(x2, False, False, "primary")
    bg_hyd = sensors.hydrophone_signal(t2, False, False)

    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    fig.suptitle(
        "FIG 2 - Multi-Sensor Fusion: L3 (PMN-PT Pressure) + "
        "L4 (Quartz+Hydrophone Acoustic) + L6 (Dual Redundant Fiber DAS)\n"
        "Refs: Bao & Chen (2012) [Ref 4] · Wenz (1962) ocean noise [Ref 5] · "
        "Strouhal orifice tone [Ref 8]",
        fontsize=10.5,
        fontweight="bold",
        color=C_NORMAL,
    )

    panel_specs = []

    for col, (title, hl, hd, clr) in enumerate(states):
        das_A = sensors.das_signal(x2, hl, hd, "primary")
        das_B = sensors.das_signal(x2, hl, hd, "backup")
        snr_d = SensorSystem.snr_db(das_A, bg_das)

        ax = axes[0, col]
        ax.fill_between(x2k, das_A, alpha=0.18, color=clr)
        ax.plot(x2k, das_A, color=clr, lw=1.4, label="Fiber A (primary)")
        ax.plot(
            x2k,
            das_B,
            color=clr,
            lw=0.65,
            ls="--",
            alpha=0.5,
            label="Fiber B (backup)",
        )
        if hl:
            ax.axvline(20, color=C_LEAK, lw=1.3, ls="--", alpha=0.7,
                       label="Pinhole @20 km")
        ax.set_title(
            f"L6 Dual Redundant Fiber DAS - {title}\nSNR ~= {snr_d:.1f} dB",
            color=clr,
            fontsize=9,
        )
        ax.set_xlabel("Distance (km)")
        ax.set_ylabel("Vibration (a.u.)")
        ax.legend(fontsize=6)
        ax.grid(True)
        ax.set_xlim(0, 50)
        ax.text(
            0.02,
            0.97,
            "Layer 6 · Dual Redundant Fiber",
            transform=ax.transAxes,
            fontsize=6.5,
            color=LAYER_CLR[6],
            va="top",
            bbox=dict(
                boxstyle="round,pad=0.2",
                facecolor=MID_BG,
                edgecolor=LAYER_CLR[6],
                alpha=0.8,
            ),
        )

        hyd_s = sensors.hydrophone_signal(t2, hl, hd)
        freqs, fft_norm = SensorSystem.rfft_norm(hyd_s, dt2)
        snr_h = SensorSystem.snr_db(hyd_s, bg_hyd)

        ax = axes[1, col]
        ax.plot(t2, hyd_s, color=clr, lw=1.0, label="L4 Quartz+Hydrophone")
        ax.plot(
            t2,
            bg_hyd,
            color=TXT_COL,
            lw=0.5,
            alpha=0.3,
            label="Ocean ambient [Wenz 1962]",
        )

        ax_t = ax.twinx()
        ax_t.fill_between(freqs, fft_norm, alpha=0.15, color=clr)
        ax_t.plot(freqs, fft_norm, color=clr, lw=0.8, ls="--", alpha=0.7)
        ax_t.set_xlim(0, 10)
        ax_t.set_ylim(0, 1.8)
        ax_t.set_ylabel("FFT (norm.)", color=clr, fontsize=6.5)
        ax_t.tick_params(colors=clr, labelsize=5.5)

        if hl and not hd:
            ax.text(
                0.97,
                0.97,
                f"f_orifice\n~= {sensors.f_orifice:.0f} Hz\n(Strouhal [Ref 8])",
                transform=ax.transAxes,
                ha="right",
                va="top",
                fontsize=7.5,
                color=C_LEAK,
                bbox=dict(
                    boxstyle="round,pad=0.2",
                    facecolor=MID_BG,
                    edgecolor=C_LEAK,
                    alpha=0.88,
                ),
            )
        ax.set_title(
            f"L4 Quartz+Hydrophone Hybrid - {title}\nSNR ~= {snr_h:.1f} dB",
            color=clr,
            fontsize=9,
        )
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Pressure (norm.)")
        ax.legend(fontsize=6)
        ax.grid(True)
        ax.text(
            0.02,
            0.97,
            "Layer 4 · Quartz + Hydrophone",
            transform=ax.transAxes,
            fontsize=6.5,
            color=LAYER_CLR[4],
            va="top",
            bbox=dict(
                boxstyle="round,pad=0.2",
                facecolor=MID_BG,
                edgecolor=LAYER_CLR[4],
                alpha=0.8,
            ),
        )

        slug = title.lower().replace(" ", "_").replace("-", "_")
        panel_specs.extend([
            (f"Fig2_L6_DAS_{slug}.svg", [axes[0, col]]),
            (f"Fig2_L4_Hydrophone_{slug}.svg", [axes[1, col], ax_t]),
        ])

    fig.subplots_adjust(left=0.05, right=0.96, bottom=0.07, top=0.86,
                        wspace=0.47, hspace=0.38)
    _save_split_panels(fig, panel_specs)
    _save(fig, "Fig2_Sensor_Signals.svg")
