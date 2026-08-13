"""Figure 4 - 7-Layer Cross-Section illustration of the pipeline wall."""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Circle, FancyBboxPatch

from ..config import DARK_BG, MID_BG, TXT_COL, C_NORMAL, C_LEAK, C_HEAL, LAYER_CLR
from ..domain.layer_architecture import LayerArchitecture
from ..domain.pipeline_physics import PipelinePhysics
from .utils import _save, _save_split_panels


def fig4_cross_section(phys: PipelinePhysics, arch: LayerArchitecture):
    print("[Fig 4] 7-Layer Cross-Section Schematic...")

    fig = plt.figure(figsize=(18, 10))
    fig.suptitle(
        "FIG 4 - 7-Layer Smart Pipeline: Cross-Section & Architecture\n"
        f"System Survival: {arch.overall_survival():.2f}% - "
        f"Depth: {phys.depth_m:.0f} m - "
        f"External P: {phys.P_ext/1e5:.0f} bar",
        fontsize=12, fontweight="bold", color=C_NORMAL)
    gs = gridspec.GridSpec(1, 2, figure=fig, wspace=0.05,
                           width_ratios=[1.05, 0.95])

    axc = fig.add_subplot(gs[0, 0])
    axc.set_xlim(-1.08, 1.08)
    axc.set_ylim(-1.10, 1.38)
    axc.set_aspect("equal")
    axc.axis("off")

    disp = arch.display_radii(r_total=0.97)
    for i in range(1, 8):
        r_in, r_out = disp[i]
        clr = LAYER_CLR[i]
        axc.add_patch(Circle((0, 0), r_out, color=clr, alpha=0.72, zorder=3 + i))
        axc.add_patch(Circle((0, 0), r_in, color=DARK_BG, zorder=4 + i))

    oil_r = disp[7][0]
    axc.add_patch(Circle((0, 0), oil_r, color="#1a0820", zorder=12))
    axc.text(0, 0, "CRUDE\nOIL\nFLOW", ha="center", va="center",
             fontsize=6.5, color="#cc88cc", fontweight="bold", zorder=13)

    label_ang = {1: 62, 2: 82, 3: 102, 4: 122, 5: 143, 6: 163, 7: 175}
    for i in range(1, 8):
        r_in, r_out = disp[i]
        r_mid = (r_in + r_out) / 2
        ang = np.deg2rad(label_ang[i])
        clr = LAYER_CLR[i]
        layer = arch.layers[i]
        xd = r_mid * np.cos(ang)
        yd = r_mid * np.sin(ang)
        axc.plot(xd, yd, "o", color=clr, ms=3.5, zorder=20)
        x_lbl = 1.14 if np.cos(ang) > 0 else -1.14
        axc.annotate(
            f"L{i}: {layer['material']}\n({layer['survival_pct']:.0f}%)",
            xy=(xd, yd),
            xytext=(x_lbl, yd + 0.02),
            fontsize=5.8,
            color=clr,
            ha="left" if np.cos(ang) > 0 else "right",
            arrowprops=dict(arrowstyle="-", color=clr, lw=0.7, alpha=0.7),
            zorder=25,
            bbox=dict(boxstyle="round,pad=0.13", facecolor=MID_BG,
                      edgecolor=clr, alpha=0.92),
        )

    axc.annotate(
        "0.5 mm PINHOLE\n(L3 detects -> L5 seals)",
        xy=(0.97 * np.cos(np.deg2rad(22)), 0.97 * np.sin(np.deg2rad(22))),
        xytext=(0.50, 1.22),
        fontsize=7,
        color=C_LEAK,
        fontweight="bold",
        arrowprops=dict(arrowstyle="->", color=C_LEAK, lw=1.4),
        bbox=dict(boxstyle="round,pad=0.2", facecolor=MID_BG,
                  edgecolor=C_LEAK, alpha=0.92),
        zorder=30,
    )

    axc.text(0, -1.06,
             f"SEAWATER | {phys.depth_m:.0f} m | {phys.P_ext/1e5:.0f} bar external",
             ha="center", fontsize=7.5, color=C_NORMAL,
             bbox=dict(boxstyle="round,pad=0.3", facecolor=MID_BG,
                       edgecolor=C_NORMAL, alpha=0.8))
    axc.text(0, 1.33, f"System Survival: {arch.overall_survival():.2f}%",
             ha="center", fontsize=9, color=C_HEAL, fontweight="bold")
    axc.set_title("Pipeline Cross-Section (proportional thickness)\n"
                  "Oil bore = centre; Layer 1 = outermost",
                  fontsize=9, color=C_NORMAL)

    axt = fig.add_subplot(gs[0, 1])
    axt.axis("off")
    axt.set_title("Step-by-Step Architecture (from project design document)",
                  fontsize=9.5, color=C_NORMAL)

    step_hdr_clr = {
        "STEP 1": LAYER_CLR[1],
        "STEP 2": LAYER_CLR[2],
        "STEP 3": LAYER_CLR[5],
        "STEP 4": LAYER_CLR[7],
    }
    y = 0.97
    for step_name, nums in arch.steps.items():
        sk = step_name.split(" - ")[0]
        hclr = step_hdr_clr.get(sk, C_NORMAL)
        axt.text(0.02, y, step_name, transform=axt.transAxes,
                 fontsize=9, fontweight="bold", color=hclr, va="top")
        y -= 0.042
        for n in nums:
            layer = arch.layers[n]
            lclr = LAYER_CLR[n]
            axt.add_patch(FancyBboxPatch(
                (0.02, y - 0.085), 0.95, 0.082,
                transform=axt.transAxes,
                boxstyle="round,pad=0.01",
                facecolor=MID_BG, edgecolor=lclr, lw=1.5, alpha=0.92))
            axt.text(0.05, y - 0.008, f"L{n}  {layer['material']}",
                     transform=axt.transAxes, fontsize=8,
                     fontweight="bold", color=lclr, va="top")
            axt.text(0.05, y - 0.032, f"Role : {layer['role']}",
                     transform=axt.transAxes, fontsize=7, color=TXT_COL, va="top")
            extra = ""
            if n == 5:
                extra = "  <- IPDI water-reactive (improved [Ref 10, 13])"
            axt.text(
                0.05,
                y - 0.055,
                f"t = {layer['thickness_mm']:.0f} mm  |  Survival: {layer['survival_pct']:.0f}%{extra}",
                transform=axt.transAxes,
                fontsize=6.5,
                color=lclr,
                va="top",
                alpha=0.85,
            )
            y -= 0.098
        y -= 0.018

    axt.text(0.50, 0.018,
             f"Overall System Survival: {arch.overall_survival():.2f}%",
             transform=axt.transAxes,
             fontsize=9.5, fontweight="bold", color=C_HEAL,
             ha="center", va="bottom",
             bbox=dict(boxstyle="round,pad=0.3", facecolor=MID_BG,
                       edgecolor=C_HEAL, alpha=0.92))

    fig.subplots_adjust(left=0.01, right=0.99, bottom=0.04, top=0.90)
    _save_split_panels(fig, [
        ("Fig4_Pipeline_Cross_Section.svg", [axc]),
        ("Fig4_Architecture_Table.svg", [axt]),
    ])
    _save(fig, "Fig4_7Layer_CrossSection.svg")
