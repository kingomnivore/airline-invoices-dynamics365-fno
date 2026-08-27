"""Share of invoices flagged at each price tolerance."""

import matplotlib.pyplot as plt
import numpy as np

from style import INK, INK_2, clean, colour_for

FILENAME = "fig4_review_burden.png"


def render(names, frames, results, path=FILENAME):
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    tolerances = np.linspace(0.02, 1.0, 60)

    for i, name in enumerate(names):
        dev = frames[name]["dev_" + results[name]["best_benchmark"]].to_numpy(float)
        flagged = [100 * (dev > 1 + t).mean() for t in tolerances]
        ax.plot(tolerances * 100, flagged, linewidth=2.0,
                color=colour_for(results[name]["best_spread"]),
                linestyle="-" if i % 2 == 0 else (0, (4, 2)),
                label="%s  (variance %.2f)" % (name, results[name]["best_spread"]),
                zorder=3)

    ax.legend(loc="upper right", fontsize=8.5)
    ax.set_xlabel("Price Tolerance (%)")
    ax.set_ylabel("Invoices Flagged (%)")
    ax.set_title("Review Load vs. Price Tolerance",
                 loc="left", fontsize=11.5, color=INK, pad=16)
    clean(ax, "y")

    fig.text(0.0, -0.07,
             "Share of invoices falling outside each tolerance, measured against the benchmark\n"
             "that holds each charge's rate tightest.",
             fontsize=8.5, color=INK_2, ha="left")
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return path
