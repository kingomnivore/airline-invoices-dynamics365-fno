"""Entry point. Writes outputs.txt and four figures.

    python run.py
"""

import matplotlib
matplotlib.use("Agg")

import config
import data
import detection
import metrics
import report
import style
from figures import deviation, fits, rate_spread, review_burden

OUTPUTS = "outputs.txt"


def analyse(df, names):
    """Frames, fit statistics, rate statistics and detection results per charge."""
    frames = {n: data.frame(df, n) for n in names}
    stats = {n: metrics.rate_stats(frames[n]) for n in names}

    results = {}
    for name in names:
        benchmark = metrics.best_benchmark(stats[name])
        dev = frames[name]["dev_" + benchmark].to_numpy(float)
        tol = detection.tolerance_for_burden(dev, config.BURDEN)
        results[name] = dict(detection.detect(dev, tol),
                             best_benchmark=benchmark,
                             best_spread=stats[name]["spread_" + benchmark])
    return frames, stats, results


def main():
    names = list(config.CHARGES)
    df = data.load()
    frames, stats, results = analyse(df, names)

    out = report.Report()
    report.source(out, df)
    report.charges(out, names, frames)
    fit_stats = report.explanatory_power(out, names, frames)
    report.rate_and_benchmarks(out, names, stats)
    report.mixed_population(out, frames)
    report.detection(out, names, frames, results)
    report.tolerance_sweep(out, names, frames, results)
    out.save(OUTPUTS)

    style.apply()
    written = [
        rate_spread.render(names, stats),
        fits.render(names, frames, fit_stats, results),
        deviation.render(names, frames, results),
        review_burden.render(names, frames, results),
    ]

    print("\n\nwrote %s and %s" % (OUTPUTS, ", ".join(written)))


if __name__ == "__main__":
    main()
