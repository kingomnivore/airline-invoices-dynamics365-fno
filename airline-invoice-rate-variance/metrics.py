"""Fit quality and rate dispersion."""

import numpy as np

from config import BENCHMARKS, ENTITY


def fit(amount, driver):
    """Least squares fit of amount on driver. Returns (slope, intercept, r2)."""
    slope, intercept = np.polyfit(driver, amount, 1)
    residual = amount - (intercept + slope * driver)
    r2 = 1.0 - (residual ** 2).sum() / ((amount - amount.mean()) ** 2).sum()
    return slope, intercept, r2


def r2_within_bands(amount, driver, n_bands=4, min_rows=30):
    """Mean R2 of fits within driver size quartiles.

    Pooled R2 is inflated because carrier size correlates with both variables
    independently of pricing. Refitting inside size bands removes most of it.
    """
    edges = np.percentile(driver, np.linspace(0, 100, n_bands + 1))
    edges[-1] += 1.0
    scores = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        band = (driver >= lo) & (driver < hi)
        if band.sum() >= min_rows:
            scores.append(fit(amount[band], driver[band])[2])
    return float(np.mean(scores)) if scores else float("nan")


def spread(dev):
    """Interquartile range over the median. 0.04 means the middle half sit
    within 4 percent of the benchmark."""
    p25, p50, p75 = np.percentile(dev, [25, 50, 75])
    return (p75 - p25) / p50


def rate_stats(d):
    """Rate percentiles and the spread against each benchmark."""
    rate = d["rate"].to_numpy(float)
    p10, p50, p90 = np.percentile(rate, [10, 50, 90])
    stats = {
        "n": int(rate.size),
        "entities": int(d.groupby(ENTITY).ngroups),
        "p10": p10,
        "median": p50,
        "p90": p90,
        "p90_over_p10": p90 / p10,
    }
    for name in BENCHMARKS:
        stats["spread_" + name] = spread(d["dev_" + name].to_numpy(float))
    return stats


def best_benchmark(stats):
    """The benchmark holding the rate tightest."""
    return min(BENCHMARKS, key=lambda b: stats["spread_" + b])
