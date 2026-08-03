"""Shared plotting helper used by every figure module: save-and-close-figure."""
import os

import matplotlib.pyplot as plt

from ..config import OUTPUT_DIR, DARK_BG


# ══════════════════════════════════════════════════════════════════════════════
# HELPER — save figure
# ══════════════════════════════════════════════════════════════════════════════
def _save(fig: plt.Figure, name: str, dpi: int = 120):
    path = os.path.join(OUTPUT_DIR, name)
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor=DARK_BG)
    plt.close(fig)
    print(f"  ✓ {name}")

