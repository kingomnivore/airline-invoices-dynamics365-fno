"""Figure styling.

Transparent backgrounds, recessive axes, two categorical hues in fixed order.
Blue is a rate tight enough to automate, orange is not. Colour follows meaning
rather than rank, so it means the same thing in every figure.
"""

import matplotlib as mpl

from config import USABLE

C_TIGHT = "#2a78d6"
C_LOOSE = "#eb6834"

INK = "#0b0b0b"
INK_2 = "#52514e"
RULE = "#c9c8c4"


def apply():
    mpl.rcParams.update({
        "figure.facecolor": "none",
        "axes.facecolor": "none",
        "savefig.facecolor": "none",
        "savefig.transparent": True,
        "font.size": 10,
        "text.color": INK,
        "axes.labelcolor": INK_2,
        "xtick.color": INK_2,
        "ytick.color": INK_2,
        "axes.edgecolor": RULE,
        "axes.linewidth": 0.8,
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
        "legend.frameon": False,
    })


def clean(ax, value_axis="x"):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(axis=value_axis, color=RULE, linewidth=0.6, alpha=0.7)
    ax.set_axisbelow(True)


def colour_for(spread, cutoff=USABLE):
    return C_TIGHT if spread < cutoff else C_LOOSE
