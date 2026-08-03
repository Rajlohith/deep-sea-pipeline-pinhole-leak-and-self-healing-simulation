"""Figure 11 — Machine Learning Sensor Fusion diagnostics (Module 7 results)."""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.metrics import confusion_matrix, roc_auc_score, roc_curve, f1_score, accuracy_score

from ..config import DARK_BG, PANEL_BG, TXT_COL, C_NORMAL, C_LEAK, C_HEAL, LAYER_CLR
from ..domain.layer_architecture import LayerArchitecture
from ..ml.sensor_fusion import MLSensorFusion
from .utils import _save


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 11 — Random Forest Sensor Fusion & Digital Twin Intelligence
# ══════════════════════════════════════════════════════════════════════════════

def fig11_ml_sensor_fusion(
    ml  : "MLSensorFusion",
    arch: "LayerArchitecture",
) -> None:
    """Figure 11 — Random Forest Sensor Fusion & Digital Twin Intelligence.

    Four-panel 2×2 GridSpec figure:
      Panel A — Confusion Matrix  (imshow + TP / TN / FP / FN annotations)
      Panel B — ROC Curve         (RF vs random classifier baseline + AUC)
      Panel C — Feature Importance (top-10 horizontal bars, layer-coloured)
      Panel D — Decision Timeline  (RF leak probability over incident lifecycle)

    Reuses DARK_BG, PANEL_BG, TXT_COL, C_NORMAL, C_LEAK, C_HEAL, LAYER_CLR
    from the global plotting constants.  No new colour constants introduced.

    Args:
        ml:   Trained MLSensorFusion instance (must have called
              train_digital_twin() first).
        arch: LayerArchitecture instance (for layer-colour access).
    """
    import matplotlib.patches as mpatches   # std-lib sub-module; no new dep

    fig = plt.figure(figsize=(16, 9), facecolor=DARK_BG)
    fig.suptitle(
        "FIG 11 — Random Forest Sensor Fusion & Digital Twin Intelligence\n"
        "Module 7: Hybrid Physics–AI  |  "
        "L3 PMN-PT  +  L4 Quartz/Hydrophone  +  L6 Dual Fiber DAS  →  RF  →  P(Leak)",
        fontsize=11, fontweight="bold", color=TXT_COL)

    gs = fig.add_gridspec(
        2, 2,
        hspace=0.44, wspace=0.38,
        left=0.07, right=0.97,
        top=0.88,  bottom=0.07)

    # ── Colour map: feature category → plot colour ─────────────────────────
    feat_clr: dict = {
        3      : LAYER_CLR[3],   # amber  — L3 PMN-PT pressure/vibration
        4      : LAYER_CLR[4],   # purple — L4 Quartz+Hydrophone acoustic
        6      : LAYER_CLR[6],   # orange — L6 Dual Fiber DAS
        "env"  : C_NORMAL,       # normal-state colour — environmental
        "state": C_HEAL,         # heal colour — state variables
    }

    # Helper: apply shared dark-theme styling to an axis
    def _style(ax: plt.Axes) -> None:
        ax.set_facecolor(PANEL_BG)
        ax.tick_params(colors=TXT_COL, labelsize=8)
        for sp in ax.spines.values():
            sp.set_edgecolor(TXT_COL)

    # ─────────────────────────────────────────────────────────────────────────
    # PANEL A — Confusion Matrix
    # ─────────────────────────────────────────────────────────────────────────
    ax_a = fig.add_subplot(gs[0, 0])
    _style(ax_a)

    cm     = confusion_matrix(ml.y_test, ml.y_pred)
    cm_pct = cm.astype(float) / cm.sum() * 100.0

    im = ax_a.imshow(cm, cmap="Blues", aspect="auto",
                     vmin=0, vmax=cm.max() * 1.35)

    # Cell annotations: label + count + percentage
    cell_lbl = [["TN", "FP"], ["FN", "TP"]]
    for r in range(2):
        for c in range(2):
            count  = cm[r, c]
            pct    = cm_pct[r, c]
            lbl    = cell_lbl[r][c]
            # White text on dark cells, dark text on light cells
            fg = "white" if count > cm.max() * 0.50 else TXT_COL
            ax_a.text(c, r,
                      f"{lbl}\n{count}\n({pct:.1f}%)",
                      ha="center", va="center",
                      fontsize=13, fontweight="bold", color=fg)

    acc_val = accuracy_score(ml.y_test, ml.y_pred)
    auc_val = roc_auc_score (ml.y_test, ml.y_prob)
    f1_val  = f1_score      (ml.y_test, ml.y_pred, zero_division=0)

    ax_a.set_xticks([0, 1])
    ax_a.set_yticks([0, 1])
    ax_a.set_xticklabels(["Predicted: Normal", "Predicted: Leak"],
                         color=TXT_COL, fontsize=8.5)
    ax_a.set_yticklabels(["Actual: Normal", "Actual: Leak"],
                         color=TXT_COL, fontsize=8.5,
                         rotation=90, va="center")
    ax_a.set_title(
        f"(A) Confusion Matrix\n"
        f"Accuracy={acc_val:.3f}  ·  F1={f1_val:.3f}  ·  AUC={auc_val:.3f}",
        color=TXT_COL, fontsize=9.5, pad=6)

    # ─────────────────────────────────────────────────────────────────────────
    # PANEL B — ROC Curve
    # ─────────────────────────────────────────────────────────────────────────
    ax_b = fig.add_subplot(gs[0, 1])
    _style(ax_b)

    fpr, tpr, _ = roc_curve(ml.y_test, ml.y_prob)

    ax_b.plot(fpr, tpr,
              color=LAYER_CLR[4], lw=2.5, zorder=5,
              label=f"RF Sensor Fusion  AUC = {auc_val:.4f}")
    ax_b.fill_between(fpr, tpr,
                      alpha=0.12, color=LAYER_CLR[4], zorder=4)
    ax_b.plot([0, 1], [0, 1],
              color=TXT_COL, lw=1.2, ls="--", alpha=0.55,
              label="Random Classifier  AUC = 0.500")

    ax_b.set_xlim(-0.01, 1.01)
    ax_b.set_ylim(-0.01, 1.01)
    ax_b.set_xlabel("False Positive Rate", color=TXT_COL, fontsize=9)
    ax_b.set_ylabel("True Positive Rate",  color=TXT_COL, fontsize=9)
    ax_b.legend(fontsize=8.5, facecolor=PANEL_BG,
                labelcolor=TXT_COL, edgecolor=TXT_COL, loc="lower right")
    ax_b.grid(True, alpha=0.20, color=TXT_COL)
    ax_b.set_title(
        "(B) ROC Curve\n"
        "L3 + L4 + L6 Sensor Fusion vs Random Classifier Baseline",
        color=TXT_COL, fontsize=9.5, pad=6)

    # ─────────────────────────────────────────────────────────────────────────
    # PANEL C — Feature Importance (top-10, coloured by sensor layer)
    # ─────────────────────────────────────────────────────────────────────────
    ax_c = fig.add_subplot(gs[1, 0])
    _style(ax_c)

    imp    = ml.model.feature_importances_
    order  = np.argsort(imp)[::-1][:10]            # top-10 only
    names  = [ml.feature_names[i]                  for i in order]
    vals   = [imp[i]                               for i in order]
    clrs   = [feat_clr[ml.FEATURE_LAYER_MAP[n]]   for n in names]
    y_pos  = np.arange(len(names))

    bars = ax_c.barh(y_pos, vals,
                     color=clrs, edgecolor=DARK_BG,
                     lw=0.6, height=0.72)

    # Value label to the right of each bar
    for yi, v in zip(y_pos, vals):
        ax_c.text(v + 0.0008, yi, f"{v:.3f}",
                  va="center", ha="left",
                  color=TXT_COL, fontsize=7.5)

    ax_c.set_yticks(y_pos)
    ax_c.set_yticklabels(names, color=TXT_COL, fontsize=8.0)
    ax_c.set_xlabel("Mean Impurity Decrease (Gini Importance)",
                    color=TXT_COL, fontsize=9)
    ax_c.invert_yaxis()
    ax_c.grid(True, axis="x", alpha=0.20, color=TXT_COL)

    # Legend — one entry per layer category
    legend_handles = [
        mpatches.Patch(facecolor=feat_clr[3],
                       label="Layer 3 — PMN-PT (pressure / vibration)"),
        mpatches.Patch(facecolor=feat_clr[4],
                       label="Layer 4 — Quartz + Hydrophone (acoustic)"),
        mpatches.Patch(facecolor=feat_clr[6],
                       label="Layer 6 — DAS (spatial vibration)"),
        mpatches.Patch(facecolor=feat_clr["env"],
                       label="Environmental (depth / temperature)"),
        mpatches.Patch(facecolor=feat_clr["state"],
                       label="State (crack fraction / healing η)"),
    ]
    ax_c.legend(handles=legend_handles, fontsize=7.0,
                facecolor=PANEL_BG, labelcolor=TXT_COL,
                edgecolor=TXT_COL, loc="lower right")
    ax_c.set_title(
        "(C) Feature Importance — Top 10 of 16\n"
        "Coloured by sensor layer  [L3 · L4 · L6 · Environmental · State]",
        color=TXT_COL, fontsize=9.5, pad=6)

    # ─────────────────────────────────────────────────────────────────────────
    # PANEL D — Decision Timeline
    # ─────────────────────────────────────────────────────────────────────────
    ax_d = fig.add_subplot(gs[1, 1])
    _style(ax_d)

    t_min, probs, t_hs, t_he = ml.decision_timeline(n_steps=80)

    # Light 3-point rolling average for visual smoothness (does not alter data)
    kernel  = np.ones(3) / 3.0
    prob_sm = np.convolve(probs, kernel, mode="same")
    prob_sm[0]  = probs[0]    # preserve endpoints
    prob_sm[-1] = probs[-1]

    # Leak probability trace
    ax_d.plot(t_min, prob_sm,
              color=LAYER_CLR[4], lw=2.5, zorder=5,
              label="RF Leak Probability P(Leak)")

    # Decision threshold
    ax_d.axhline(0.5,
                 color=C_LEAK, lw=1.3, ls="--", alpha=0.85, zorder=4,
                 label="Decision threshold  (0.50)")

    # Layer 5 healing interval — shaded with LAYER_CLR[5] at ~15% alpha
    ax_d.axvspan(t_hs, t_he,
                 alpha=0.15, color=LAYER_CLR[5], zorder=3,
                 label=f"L5 Hybrid Healing  ({t_hs:.0f}–{t_he:.0f} min)")

    # Vertical markers for key events
    ax_d.axvline(20.0, color=C_LEAK,   lw=1.0, ls=":", alpha=0.65, zorder=4)
    ax_d.axvline(28.0, color=C_NORMAL, lw=1.0, ls=":", alpha=0.65, zorder=4)

    # Phase text labels (using axis-fraction y so they sit just above the plot)
    phase_kw = dict(
        transform=ax_d.get_xaxis_transform(),
        fontsize=7.2, ha="center", va="bottom")
    ax_d.text( 9.0, 1.03, "Normal",        color=C_NORMAL,       **phase_kw)
    ax_d.text(24.0, 1.03, "Leak ↑",        color=C_LEAK,         **phase_kw)
    ax_d.text(41.0, 1.03, "Healing",       color=LAYER_CLR[5],   **phase_kw)
    ax_d.text(67.0, 1.03, "Recovery",      color=C_HEAL,         **phase_kw)

    ax_d.set_xlim(0.0, 80.0)
    ax_d.set_ylim(-0.06, 1.18)
    ax_d.set_xlabel("Time (minutes)", color=TXT_COL, fontsize=9)
    ax_d.set_ylabel("P(Leak)",        color=TXT_COL, fontsize=9)
    ax_d.legend(fontsize=7.5, facecolor=PANEL_BG,
                labelcolor=TXT_COL, edgecolor=TXT_COL, loc="upper right")
    ax_d.grid(True, alpha=0.20, color=TXT_COL)
    ax_d.set_title(
        "(D) Decision Timeline — Full Incident Lifecycle\n"
        "Normal → Leak Onset → RF Detection → L5 Hybrid Healing → Recovery",
        color=TXT_COL, fontsize=9.5, pad=6)

    _save(fig, "Fig11_ML_Sensor_Fusion.png")
