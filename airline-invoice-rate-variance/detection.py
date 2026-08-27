"""Synthetic overcharge detection.

Not used to support any claim in the article. It measures detection against a
population benchmark, whereas F&O matching compares an invoice to its own
purchase order. Retained because the result is informative; see README.
"""

import numpy as np

from config import OVERCHARGE, SEED, SHARE


def tolerance_for_burden(dev, burden=0.05):
    """Tolerance that flags the given share of invoices."""
    return float(np.percentile(dev, 100 * (1 - burden)) - 1.0)


def inject(dev, pct=OVERCHARGE, share=SHARE, seed=SEED):
    """Apply a known overcharge to a random share of rows."""
    rng = np.random.default_rng(seed)
    mask = rng.random(dev.size) < share
    out = dev.copy()
    out[mask] *= (1.0 + pct)
    return out, mask


def detect(dev, tol, pct=OVERCHARGE, share=SHARE, seed=SEED):
    """Flag rates above tolerance before and after injection.

    A row already over tolerance was not caught by the injection, so only rows
    that newly cross it are counted.
    """
    before = dev > (1.0 + tol)
    dirty, tampered = inject(dev, pct, share, seed)
    after = dirty > (1.0 + tol)

    caught = int(((after & ~before) & tampered).sum())
    n_tampered = int(tampered.sum())
    clean_flagged = int((after & ~tampered).sum())
    n_clean = int((~tampered).sum())

    return {
        "tolerance": tol,
        "n_overcharged": n_tampered,
        "caught": caught,
        "catch_rate": caught / n_tampered if n_tampered else float("nan"),
        "review_burden": clean_flagged / n_clean if n_clean else float("nan"),
        "n_reviewed": clean_flagged,
    }
