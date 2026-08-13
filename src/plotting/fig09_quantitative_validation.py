"""Figure 9 - Quantitative Validation of the simulation against PHMSA data."""
import numpy as np
import pandas as pd
from scipy import stats as sp_stats
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from ..config import MID_BG, C_NORMAL, C_LEAK, C_SENSOR, C_HEAL, C_PHMSA, LAYER_CLR
from ..domain.pipeline_physics import PipelinePhysics
from ..domain.healing_system import HealingSystem
from .utils import _save, _save_split_panels


def fig9_quantitative_validation(
    df: pd.DataFrame,
    phys: PipelinePhysics,
    heal: HealingSystem,
):
    print("[Fig 9] Quantitative Validation...")

    df_pc = df[(df["LEAK_TYPE"] == "PINHOLE") &
               (df["COMMODITY_RELEASED_TYPE"] == "CRUDE OIL")]
    vols = df_pc["RELEASE_L"].dropna()
    vols = vols[vols > 0]
    psig_all = df["ACCIDENT_PSIG"].dropna()
    psig_all = psig_all[psig_all > 0]
    diam_all = df["PIPE_DIAMETER"].dropna()
    diam_all = diam_all[(diam_all > 0) & (diam_all <= 48)]

    sim_psig_psi = 125.0 * 14.5038
    sim_in = phys.D * 39.3701
    vol_healed = heal.cumulative_loss_L(600, phys)
    vol_unhealed = phys.Q_leak_max * 86400 * 1000

    fig, axes = plt.subplots(2, 2, figsize=(15, 9))
    fig.suptitle(
        "FIG 9 - Quantitative Validation: 7-Layer Simulation vs PHMSA Empirical Data\n"
        "IEEE-Style Cross-Validation | Simulated: D0.5mm pinhole, 150 bar, 50km crude line, Hybrid Healing System",
        fontsize=10.5, fontweight="bold", color=C_NORMAL)

    ax = axes[0, 0]
    psig_plot = psig_all[psig_all <= 2000]
    ax.hist(psig_plot, bins=50, color=C_PHMSA, alpha=0.65, edgecolor="none",
            density=True, label="PHMSA reported PSIG")
    kde_x = np.linspace(0, 2000, 500)
    kde = sp_stats.gaussian_kde(psig_plot, bw_method=0.15)
    ax.plot(kde_x, kde(kde_x), color=C_SENSOR, lw=1.8, label="KDE density")
    ax.axvline(sim_psig_psi, color=C_LEAK, lw=2.5, ls="--",
               label=f"Simulation: {sim_psig_psi:.0f} PSI (125 bar midpoint)")
    p25p = float(np.percentile(psig_plot, 25))
    p75p = float(np.percentile(psig_plot, 75))
    ax.axvspan(p25p, p75p, color=C_HEAL, alpha=0.10,
               label=f"PHMSA IQR ({p25p:.0f}-{p75p:.0f} PSI)")
    pct_psig = float(sp_stats.percentileofscore(psig_all, sim_psig_psi))
    ax.set_xlabel("Operating Pressure at Incident (PSIG)")
    ax.set_ylabel("Probability density")
    ax.set_title(f"(a) Operating Pressure Validation\n"
                 f"Simulation P{pct_psig:.0f} of PHMSA - L1 rated "
                 f"{phys.arch.layers[1]['pressure_rating_bar']} bar")
    ax.legend(fontsize=7.5)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 2000)

    ax = axes[0, 1]
    vsort = np.sort(vols)
    cdf = np.arange(1, len(vsort) + 1) / len(vsort)
    ax.semilogx(vsort, cdf * 100, color=C_PHMSA, lw=2.0, label="PHMSA crude pinhole CDF")
    for pct, val, lbl in [
        (25, float(np.percentile(vols, 25)), "P25"),
        (50, float(np.percentile(vols, 50)), "P50"),
        (75, float(np.percentile(vols, 75)), "P75"),
    ]:
        ax.axvline(val, color=C_SENSOR, lw=0.9, ls=":", alpha=0.7)
        ax.text(val * 1.15, pct + 2, f"{lbl}\n{val:.0f} L", fontsize=6.5, color=C_SENSOR)
    ax.axvline(vol_healed, color=LAYER_CLR[5], lw=2.5, ls="--",
               label=f"L5 Hybrid Healed (10 min): {vol_healed:.2f} L")
    ax.axvline(vol_unhealed, color=C_LEAK, lw=2.0, ls="-.",
               label=f"Unhealed (24 hr): {vol_unhealed:.0f} L")
    pct_h = float(sp_stats.percentileofscore(vols, vol_healed))
    pct_u = float(sp_stats.percentileofscore(vols, vol_unhealed))
    ax.text(0.97, 0.28,
            f"L5 healed -> P{pct_h:.0f} PHMSA\n"
            f"Unhealed -> P{pct_u:.0f} PHMSA\n"
            f"Hybrid saves {(1 - vol_healed/vol_unhealed)*100:.0f}%\n"
            f"[Zeng 2025 Ref 10 + SMP]",
            transform=ax.transAxes, ha="right", va="top", fontsize=8,
            color=LAYER_CLR[5],
            bbox=dict(boxstyle="round,pad=0.4", facecolor=MID_BG,
                      edgecolor=LAYER_CLR[5], alpha=0.92))
    ax.set_xlabel("Volume Released (L, log scale)")
    ax.set_ylabel("Cumulative Probability (%)")
    ax.set_title("(b) Volume Loss Validation\n"
                 "L5 Hybrid Healing pushes sim. loss below P50 of PHMSA")
    ax.legend(fontsize=7.5, loc="upper left")
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 102)

    ax = axes[1, 0]
    ax.hist(diam_all, bins=30, color=C_PHMSA, alpha=0.65, edgecolor="none",
            density=True, label="PHMSA pipe diameters")
    kde_d = np.linspace(0, 50, 300)
    kdev = sp_stats.gaussian_kde(diam_all, bw_method=0.2)
    ax.plot(kde_d, kdev(kde_d), color=C_SENSOR, lw=1.8, label="KDE")
    ax.axvline(sim_in, color=C_NORMAL, lw=2.5, ls="--",
               label=f"Simulation: {phys.D*100:.0f} cm = {sim_in:.1f} in.")
    pct_d = float(sp_stats.percentileofscore(diam_all, sim_in))
    p25_d = float(np.percentile(diam_all, 25))
    p75_d = float(np.percentile(diam_all, 75))
    ax.axvspan(p25_d, p75_d, color=C_HEAL, alpha=0.10,
               label=f"PHMSA IQR ({p25_d:.0f}-{p75_d:.0f} in.)")
    ax.text(0.97, 0.95, f"Sim. at P{pct_d:.0f} PHMSA",
            transform=ax.transAxes, ha="right", va="top", fontsize=8,
            color=C_NORMAL,
            bbox=dict(boxstyle="round,pad=0.4", facecolor=MID_BG,
                      edgecolor=C_NORMAL, alpha=0.92))
    ax.set_xlabel("Pipe Diameter (inches)")
    ax.set_ylabel("Probability density")
    ax.set_title(f"(c) Pipe Diameter Validation\n"
                 f"Sim. {sim_in:.0f} in. at P{pct_d:.0f} of PHMSA range")
    ax.legend(fontsize=7.5)
    ax.grid(True, alpha=0.3)

    ax = axes[1, 1]
    env_c = df_pc["EST_COST_ENVIRONMENTAL"].dropna()
    env_c = env_c[env_c > 0]
    prop_c = df_pc["EST_COST_PROP_DAMAGE"].dropna()
    prop_c = prop_c[prop_c > 0]
    bplot = ax.boxplot(
        [np.log10(env_c + 1), np.log10(prop_c + 1)],
        tick_labels=["Environmental\nCost", "Property\nDamage"],
        patch_artist=True,
        medianprops=dict(color="white", lw=2.0),
        whiskerprops=dict(color=C_NORMAL),
        capprops=dict(color=C_NORMAL),
        flierprops=dict(marker=".", color=C_PHMSA, markersize=2, alpha=0.3),
    )
    bplot["boxes"][0].set_facecolor(C_LEAK)
    bplot["boxes"][0].set_alpha(0.5)
    bplot["boxes"][1].set_facecolor(C_SENSOR)
    bplot["boxes"][1].set_alpha(0.5)
    for i, data in enumerate([env_c, prop_c], 1):
        med = float(data.median())
        ax.text(i, np.log10(med + 1) + 0.15, f"Median\n${med:,.0f}",
                ha="center", fontsize=7.5, color=C_NORMAL)
    savings = float(env_c.median()) * (1 - vol_healed / vol_unhealed)
    ax.axhline(np.log10(savings + 1), color=LAYER_CLR[5], lw=2.0, ls="--",
               label=f"Proj. savings via L5 Hybrid Heal: ${savings:,.0f}")
    ax.set_ylabel("Cost (log10 USD + 1)")
    ax.set_title("(d) Economic Impact Validation\n"
                 "PHMSA crude pinhole costs + L5 Hybrid Healing savings [Ref 10]")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _: f"$10^{{{v:.0f}}}" if v > 0 else "$0")
    )

    fig.tight_layout()
    _save_split_panels(fig, [
        ("Fig9_Operating_Pressure_Validation.svg", [axes[0, 0]]),
        ("Fig9_Volume_Loss_Validation.svg", [axes[0, 1]]),
        ("Fig9_Pipe_Diameter_Validation.svg", [axes[1, 0]]),
        ("Fig9_Economic_Impact_Validation.svg", [axes[1, 1]]),
    ])
    _save(fig, "Fig9_Quantitative_Validation.svg")
