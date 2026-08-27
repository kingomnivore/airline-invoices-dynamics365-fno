"""Distribution of each invoice against its own best benchmark."""

import matplotlib.pyplot as plt
import numpy as np

from style import INK, INK_2, clean, colour_for

FILENAME = "fig3_deviation.png"


def render(names, frames, results, path=FILENAME):
    fig, axes = plt.subplots(1, len(names), figsize=(9.6, 2.9), sharey=True)

    for ax, name in zip(axes, names):
        dev = frames[name]["dev_" + results[name]["best_benchmark"]].to_numpy(float)
        colour = colour_for(results[name]["best_spread"])
        ax.hist(np.clip(dev, 0, 2.5), bins=45, color=colour, alpha=0.75, linewidth=0)
        ax.axvline(1.0, color=INK, linewidth=1.0, zorder=4)
        ax.set_xlim(0, 2.5)
        ax.set_xlabel("Invoice / Benchmark", fontsize=8.5)
        ax.set_title("%s\nVariance %.2f" % (name, results[name]["best_spread"]),
                     loc="left", fontsize=9, color=INK, pad=8)
        clean(ax, "y")

    axes[0].set_ylabel("Carrier-quarters", fontsize=8.5)
    fig.text(0.0, -0.10,
             "Each invoice divided by its own benchmark, so 1.0 sits exactly on benchmark.\n"
             "Every charge uses whichever of the three benchmarks holds its rate tightest.",
             fontsize=8.5, color=INK_2, ha="left")
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return path
