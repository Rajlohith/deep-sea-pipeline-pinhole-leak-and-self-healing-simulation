"""Shared plotting helpers used by every figure module."""
import os

import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox

from ..config import OUTPUT_DIR, DARK_BG


def _save(fig: plt.Figure, name: str, dpi: int = 120):
    path = os.path.join(OUTPUT_DIR, name)
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor=DARK_BG)
    plt.close(fig)
    print(f"  Saved {name}")


def _save_split_panels(
    fig: plt.Figure,
    panel_specs: list[tuple[str, list[plt.Axes]]],
    dpi: int = 120,
    pad_inches: float = 0.08,
):
    """Save individual subplot panels as standalone files."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()

    for name, axes in panel_specs:
        if not axes:
            continue

        bbox = Bbox.union(
            [ax.get_tightbbox(renderer) for ax in axes]
        ).transformed(fig.dpi_scale_trans.inverted())
        path = os.path.join(OUTPUT_DIR, name)
        fig.savefig(path, dpi=dpi, bbox_inches=bbox, pad_inches=pad_inches,
                    facecolor=DARK_BG)
        print(f"  Saved {name}")
