"""Figure 8 - PHMSA Incident Landscape (real-world context)."""
import numpy as np
import pandas as pd
from scipy import stats as sp_stats
import matplotlib.pyplot as plt

from ..config import TXT_COL, C_NORMAL, C_LEAK, C_SENSOR, C_HEAL, C_EXTRA, C_PHMSA
from .utils import _save, _save_split_panels


def fig8_phmsa_landscape(df: pd.DataFrame):
    print("[Fig 8] PHMSA Incident Landscape...")

    df_crude = df[df["COMMODITY_RELEASED_TYPE"] == "CRUDE OIL"]
    df_pc = df[(df["LEAK_TYPE"] == "PINHOLE") &
               (df["COMMODITY_RELEASED_TYPE"] == "CRUDE OIL")]
    all_leaks = df[df["RELEASE_TYPE"] == "LEAK"]
    pin_frac = len(df[(df["RELEASE_TYPE"] == "LEAK") &
                      (df["LEAK_TYPE"] == "PINHOLE")]) / max(len(all_leaks), 1)

    yr_min = int(df["IYEAR"].min())
    yr_max = int(df["IYEAR"].max())
    yr_full_max = yr_max - 1

    fig, axes = plt.subplots(2, 2, figsize=(15, 9))
    fig.suptitle(
        f"FIG 8 - PHMSA Real-World Validation: Incident Landscape ({yr_min}-{yr_max})\n"
        f"Source: U.S. PHMSA Hazardous Liquid Incident Database [Ref 14] | N = {len(df):,} incidents",
        fontsize=11, fontweight="bold", color=C_NORMAL)

    ax = axes[0, 0]
    ann = {y: c for y, c in df[df["IYEAR"] <= yr_full_max].groupby("IYEAR").size().items()}
    years = sorted(ann.keys())
    counts = [ann[y] for y in years]
    ax.bar(years, counts, color=C_PHMSA, alpha=0.65, edgecolor=C_PHMSA, lw=0.5)
    slope, intercept, r, *_ = sp_stats.linregress(years, counts)
    ax.plot(years, [slope * y + intercept for y in years],
            color=C_LEAK, lw=2.0, ls="--",
            label=f"Trend (slope={slope:.1f}/yr, R^2={r**2:.2f})")
    ax.annotate("COVID-19\noperational dip", xy=(2020, ann.get(2020, 332)),
                xytext=(2016, 285), fontsize=7.5, color=TXT_COL,
                arrowprops=dict(arrowstyle="->", color=TXT_COL, lw=0.8))
    ax.set_xlabel("Year")
    ax.set_ylabel("Reported incidents")
    ax.set_title("(a) Annual Hazardous Liquid Pipeline Incidents\n"
                 "Justifies 7-Layer autonomous monitoring design")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.4)
    ax.set_xlim(2009, 2026)

    ax = axes[0, 1]
    causes = df_crude["CAUSE"].value_counts()
    short = [c[:28] for c in causes.index]
    clrs_c = [C_LEAK if "CORROS" in c else C_SENSOR if "EQUIP" in c else C_EXTRA
              for c in causes.index]
    bars = ax.barh(range(len(causes)), causes.values, color=clrs_c,
                   alpha=0.80, edgecolor="white", lw=0.4)
    ax.set_yticks(range(len(causes)))
    ax.set_yticklabels(short, fontsize=6.5)
    for bar, val in zip(bars, causes.values):
        ax.text(val + 3, bar.get_y() + bar.get_height() / 2,
                f"{val:,}", va="center", fontsize=7, color=TXT_COL)
    ax.set_xlabel("Crude oil incidents")
    ax.set_title("(b) Incident Cause - Crude Oil Only\n"
                 "Corrosion -> pinhole; L2 Inconel 625 addresses this")
    ax.grid(True, axis="x", alpha=0.3)

    ax = axes[1, 0]
    ltype = all_leaks["LEAK_TYPE"].value_counts().head(6)
    lclrs = [C_LEAK if l == "PINHOLE" else C_SENSOR for l in ltype.index]
    bars = ax.bar(range(len(ltype)), ltype.values, color=lclrs,
                  alpha=0.82, edgecolor="white", lw=0.5)
    ax.set_xticks(range(len(ltype)))
    ax.set_xticklabels([l[:15] for l in ltype.index], fontsize=7.5)
    for bar, val in zip(bars, ltype.values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 8,
                f"{val:,}\n({val/len(all_leaks)*100:.0f}%)",
                ha="center", va="bottom", fontsize=6.5, color=TXT_COL)
    ax.set_ylabel("Incident count")
    ax.set_title(
        f"(c) Leak Type Distribution\nPinhole = {pin_frac*100:.0f}% of all leaks - "
        "MOST COMMON TYPE -> validates L3+L5 design"
    )
    ax.grid(True, axis="y", alpha=0.3)
    ax.annotate("This study\n(0.5 mm pinhole)", xy=(0, ltype.iloc[0]),
                xytext=(1.5, ltype.iloc[0] * 0.83), fontsize=8,
                color=C_LEAK, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C_LEAK, lw=1.2))

    ax = axes[1, 1]
    ann_pc = {y: c for y, c in df_pc[df_pc["IYEAR"] <= 2025].groupby("IYEAR").size().items()}
    p_years = sorted(ann_pc.keys())
    p_cnts = [ann_pc.get(y, 0) for y in p_years]
    ax.fill_between(p_years, p_cnts, alpha=0.18, color=C_PHMSA)
    ax.plot(p_years, p_cnts, color=C_PHMSA, lw=2.0, marker="o", markersize=4,
            label="PHMSA crude pinhole/yr")
    rolling = pd.Series(p_cnts, index=p_years).rolling(3, center=True).mean()
    ax.plot(p_years, rolling.values, color=C_SENSOR, lw=1.5, ls="--",
            label="3-year rolling mean")
    ax.axhline(np.mean(p_cnts), color=C_HEAL, lw=1.5, ls=":",
               label=f"Mean = {np.mean(p_cnts):.0f}/yr")
    ax.set_xlabel("Year")
    ax.set_ylabel("Crude oil pinhole incidents/yr")
    ax.set_title("(d) Annual Crude Oil Pinhole Incidents\n"
                 "Each dot = real case matching our simulation scenario")
    ax.legend(fontsize=7.5)
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    _save_split_panels(fig, [
        ("Fig8_Annual_Incident_Count.svg", [axes[0, 0]]),
        ("Fig8_Cause_Breakdown.svg", [axes[0, 1]]),
        ("Fig8_Leak_Type_Distribution.svg", [axes[1, 0]]),
        ("Fig8_Annual_Crude_Pinhole_Incidents.svg", [axes[1, 1]]),
    ])
    _save(fig, "Fig8_PHMSA_Landscape.svg")
