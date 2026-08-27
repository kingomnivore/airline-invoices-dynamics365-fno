"""Rate variance against each benchmark, one row per charge."""

import matplotlib.pyplot as plt
import numpy as np

from config import BENCHMARK_LABELS, BENCHMARKS, USABLE
from style import INK, INK_2, clean, colour_for

FILENAME = "fig1_rate_spread.png"


def render(names, stats, path=FILENAME):
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    y = np.arange(len(names))[::-1]
    bar_h = 0.24

    for i, benchmark in enumerate(BENCHMARKS):
        values = [stats[n]["spread_" + benchmark] for n in names]
        colours = [colour_for(v) for v in values]
        offset = y + (1 - i) * bar_h
        ax.barh(offset, values, height=bar_h * 0.88, color=colours,
                alpha=0.35 + 0.32 * i, linewidth=0, zorder=3)
        for yy, v in zip(offset, values):
            # Short bars end left of the threshold line; keep labels clear of it.
            ax.text(max(v, USABLE) + 0.03, yy,
                    "%.2f  %s" % (v, BENCHMARK_LABELS[benchmark]),
                    va="center", fontsize=7.6, color=INK_2, zorder=4)

    ax.axvline(USABLE, color=INK_2, linewidth=1.0, linestyle=(0, (5, 3)), zorder=2)
    transform = ax.get_xaxis_transform()
    ax.annotate("", xy=(0.004, 1.055), xytext=(USABLE, 1.055),
                xycoords=transform, textcoords=transform,
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.5,
                                shrinkA=0, shrinkB=0))
    ax.text(USABLE + 0.025, 1.055, "AUTOMATE", transform=transform,
            fontsize=9.5, color=INK, ha="left", va="center")

    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=9.5)
    ax.set_xlim(0, max(stats[n]["spread_industry"] for n in names) * 1.35)
    ax.set_xlabel("Cost Variance (IQR / Median)")
    ax.set_title("Cost Variance vs. Automation Threshold",
                 loc="left", fontsize=11.5, color=INK, pad=36)
    clean(ax, "x")

    fig.text(0.0, -0.07,
             "Each charge measured against three benchmarks: the industry, the same quarter,\n"
             "and the carrier's own past rate. Bars are the interquartile range over the median.",
             fontsize=8.5, color=INK_2, ha="left")
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return path
