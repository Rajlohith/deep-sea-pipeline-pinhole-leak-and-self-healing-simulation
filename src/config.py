"""
Global configuration for the Deep-Sea 7-Layer Smart Pipeline simulation.

Holds everything that used to sit at module level in the original single-file
script: standard-library setup, output paths, the deep-ocean dark colour
theme, and the shared matplotlib rcParams. Every other module in this
package imports its constants from here instead of redefining them.
"""

# ── Standard library ──────────────────────────────────────────────────────────
import os
import sys
import warnings
from typing import Dict, Tuple, List, Optional

# ── Plotting ──────────────────────────────────────────────────────────────────
import matplotlib
matplotlib.use("Agg")                # headless — no display needed for saving
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════════════════════════════
#  OUTPUT DIRECTORY
# ══════════════════════════════════════════════════════════════════════════════
OUTPUT_DIR = os.path.join(os.getcwd(), "outputs")
PHMSA_PATH = os.path.join(os.getcwd(), "phmsa.csv")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ══════════════════════════════════════════════════════════════════════════════
#  GLOBAL VISUAL THEME  — deep-ocean dark palette, consistent across all figs
# ══════════════════════════════════════════════════════════════════════════════
DARK_BG  = "#0a0e1a"
MID_BG   = "#0f1629"
PANEL_BG = "#111827"
GRID_COL = "#1e2d45"
TXT_COL  = "#cdd6f4"

# Semantic colour assignments
C_NORMAL = "#00d4ff"   # cyan   — baseline / nominal signal
C_LEAK   = "#ff4d6d"   # red    — active leak / danger
C_SENSOR = "#ffd166"   # amber  — sensor / noise overlay
C_HEAL   = "#06d6a0"   # teal   — healing / recovery
C_EXTRA  = "#a29bfe"   # purple — supplementary metric
C_PHMSA  = "#f8961e"   # orange — real PHMSA data

# One stable colour per layer — used consistently in every figure
LAYER_CLR = {
    1: "#4a9eff",   # blue   — UE44/TMA Syntactic Foam + Basalt Fiber
    2: "#b0b8c8",   # silver — Inconel 625 Structural Shell
    3: "#ffd166",   # amber  — PMN-PT + Floating Ceramic Shock Mount
    4: "#a29bfe",   # purple — Quartz + Hydrophone Hybrid
    5: "#06d6a0",   # teal   — Hybrid Healing System
    6: "#f8961e",   # orange — Dual Redundant Fiber Optics
    7: "#ff4d6d",   # red    — Hybrid Power Layer
}

plt.rcParams.update({
    "figure.facecolor"  : DARK_BG,
    "axes.facecolor"    : PANEL_BG,
    "axes.edgecolor"    : GRID_COL,
    "axes.labelcolor"   : TXT_COL,
    "xtick.color"       : TXT_COL,
    "ytick.color"       : TXT_COL,
    "text.color"        : TXT_COL,
    "grid.color"        : GRID_COL,
    "grid.linewidth"    : 0.55,
    "legend.facecolor"  : MID_BG,
    "legend.edgecolor"  : GRID_COL,
    "legend.labelcolor" : TXT_COL,
    "font.family"       : "monospace",
    "axes.titlesize"    : 10,
    "axes.labelsize"    : 8.5,
    "xtick.labelsize"   : 7.5,
    "ytick.labelsize"   : 7.5,
})
