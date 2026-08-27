"""Spend against driver quantity, for the tightest and loosest charge."""

import matplotlib.pyplot as plt
import numpy as np

from config import CHARGES
from data import arrays
from style import INK, INK_2, clean, colour_for

FILENAME = "fig2_two_fits.png"


def render(names, frames, fits, results, path=FILENAME):
    pair = [names[0], names[-1]]
    fig, axes = plt.subplots(1, 2, figsize=(7.8, 3.6))

    for ax, name in zip(axes, pair):
        amount, driver = arrays(frames[name])
        slope, intercept, r2, within = fits[name]
        colour = colour_for(results[name]["best_spread"])
        hi_x, hi_y = np.percentile(driver, 99), np.percentile(amount, 99)

        ax.scatter(driver, amount, s=6, color=colour, alpha=0.28,
                   linewidths=0, zorder=2)
        xs = np.linspace(0, hi_x, 50)
        ax.plot(xs, intercept + slope * xs, color=INK, linewidth=1.4, zorder=3)
        ax.set_xlim(0, hi_x)
        ax.set_ylim(0, hi_y)
        ax.set_xlabel(CHARGES[name]["driver_label"], fontsize=8.5)
        ax.set_ylabel(CHARGES[name]["amount_label"], fontsize=8.5)
        ax.set_title("%s\nR2 %.2f, %.2f Size-Adjusted" % (name, r2, within),
                     loc="left", fontsize=9.5, color=INK, pad=10)
        clean(ax, "y")

    fig.suptitle("Spend vs. Driver Quantity", x=0.0, ha="left",
                 fontsize=11.5, color=INK, y=1.12)
    fig.text(0.0, -0.07,
             "Each point is one carrier, one aircraft type, one quarter. The line is a least squares fit.\n"
             "Points along the bottom of the fuel panel are carriers whose fuel a partner pays for.\n"
             "Both axes are clipped at the 99th percentile.",
             fontsize=8.5, color=INK_2, ha="left")
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return path
