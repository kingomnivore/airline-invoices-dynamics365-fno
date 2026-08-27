"""Text report written to outputs.txt."""

import io

import numpy as np

from config import (BENCHMARK_LABELS, BURDEN, CHARGES, ENTITY, MIN_AMOUNT,
                    MIN_QUARTERS, OVERCHARGE, SHARE, USABLE)
from data import arrays
from metrics import best_benchmark, fit, r2_within_bands, spread


class Report:
    """Accumulates lines, prints them, writes them to a file."""

    def __init__(self):
        self.lines = []

    def __call__(self, text=""):
        print(text)
        self.lines.append(str(text))

    def section(self, title):
        self("")
        self("=" * 76)
        self(title)
        self("=" * 76)

    def save(self, path):
        with io.open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(self.lines) + "\n")
        return path


def source(out, df):
    out.section("0. SOURCE")
    for f in df.attrs["files"]:
        out("    %s" % f)
    out("")
    out("Rows            %d" % len(df))
    out("Years           %s" % ", ".join(str(y) for y in sorted(df.YEAR.unique())))
    out("Quarters        %d" % df.PERIOD.nunique())
    out("Carriers        %d" % df.UNIQUE_CARRIER.nunique())
    out("Aircraft types  %d" % df.AIRCRAFT_TYPE.nunique())
    out("")
    out("One row is one carrier, one aircraft type, one quarter. Amounts are in")
    out("$000 and drivers in thousands, so amount / driver is dollars per unit.")


def charges(out, names, frames):
    out.section("1. CHARGES")
    out("%-18s %-9s %-20s %-22s %7s %8s" %
        ("Charge", "Account", "Amount", "Driver", "Rows", "Entities"))
    for name in names:
        c, d = CHARGES[name], frames[name]
        out("%-18s %-9s %-20s %-22s %7d %8d" %
            (name, c["account"], c["amount"], c["driver"], len(d),
             d.groupby(ENTITY).ngroups))
    out("")
    out("Fuel, engine repair and airframe repair are third-party spend. Pilot pay")
    out("is account 51230, salaries, and is a reference case only.")
    out("Rows under $%s of quarterly spend dropped. Minimum %d quarters per entity."
        % (format(int(MIN_AMOUNT * 1000), ","), MIN_QUARTERS))


def explanatory_power(out, names, frames):
    """Returns {name: (slope, intercept, r2, within_band)}."""
    out.section("2. DRIVER EXPLANATORY POWER")
    out("Pooled R2 is inflated by carrier size. The second column refits within")
    out("driver size quartiles.")
    out("")
    out("%-18s %11s %18s %16s" % ("Charge", "Pooled R2", "Within size band", "Slope"))
    fits = {}
    for name in names:
        amount, driver = arrays(frames[name])
        fits[name] = fit(amount, driver) + (r2_within_bands(amount, driver),)
        out("%-18s %11.3f %18.3f %16.2f"
            % (name, fits[name][2], fits[name][3], fits[name][0]))
    return fits


def rate_and_benchmarks(out, names, stats):
    out.section("3. UNIT RATE AND BENCHMARK CHOICE")
    out("%-18s %10s %10s %10s %10s %9s" %
        ("Charge", "Unit", "p10", "Median", "p90", "p90/p10"))
    for name in names:
        s = stats[name]
        out("%-18s %10s %10.2f %10.2f %10.2f %8.1fx"
            % (name, CHARGES[name]["rate_unit"], s["p10"], s["median"],
               s["p90"], s["p90_over_p10"]))
    out("")
    out("Check: the fuel median is the delivered jet fuel price for the period,")
    out("which sits above the Gulf Coast spot average of $2.227 for 2024-2025.")
    out("")
    out("Spread is the interquartile range over the median.")
    out("")
    out("%-18s %13s %15s %13s %8s   %s"
        % ("Charge", "vs industry", "vs same quarter", "vs own rate", "Best", "Verdict"))
    for name in names:
        s = stats[name]
        b = best_benchmark(s)
        verdict = "benchmark it" if s["spread_" + b] < USABLE else "do not automate"
        out("%-18s %13.2f %15.2f %13.2f %8s   %s"
            % (name, s["spread_industry"], s["spread_indexed"],
               s["spread_contract"], BENCHMARK_LABELS[b].replace("vs ", ""), verdict))


def mixed_population(out, frames):
    out.section("4. MIXED POPULATION IN THE FUEL DATA")
    fuel = frames["Aircraft fuel"]
    odd = fuel[fuel["rate"] < 1.0]
    out("%d of %d fuel rows (%.1f%%) imply a rate under $1.00 a gallon."
        % (len(odd), len(fuel), 100 * len(odd) / len(fuel)))
    out("Carriers: %s" % ", ".join(odd.groupby("UNIQUE_CARRIER").size()
                                   .sort_values(ascending=False).head(6).index))
    out("")
    out("Regional carriers on capacity purchase agreements and ACMI cargo")
    out("operators, whose fuel a partner pays for. A different commercial")
    out("arrangement rather than a reporting error. The rows are retained.")
    out("")
    out("%-30s %6s %12s %11s %13s %12s"
        % ("", "n", "Median rate", "Pooled R2", "Within band", "Spread"))
    for label, cut in [("As published", 0.0), ("Excluding under $1.00/gal", 1.0)]:
        d = fuel[fuel["rate"] >= cut]
        amount = d[fuel.attrs["amount_col"]].to_numpy(float)
        driver = d[fuel.attrs["driver_col"]].to_numpy(float)
        out("%-30s %6d %12.2f %11.3f %13.3f %12.3f"
            % (label, len(d), np.median(d["rate"]), fit(amount, driver)[2],
               r2_within_bands(amount, driver),
               spread(d["dev_contract"].to_numpy(float))))
    out("")
    out("R2 moves. The median rate and the spread do not. A measure built on")
    out("medians tolerates a mixed population; one built on squared deviations")
    out("does not.")


def detection(out, names, frames, results):
    out.section("5. SYNTHETIC OVERCHARGE DETECTION")
    out("NOT USED IN THE ARTICLE. This measures detection against a population")
    out("benchmark. F&O compares an invoice to its own purchase order, which is")
    out("a different comparison. Retained for completeness; see README.")
    out("")
    out("Tolerance set to flag %.0f%% of invoices. Overcharge of %.0f%% applied to"
        % (BURDEN * 100, OVERCHARGE * 100))
    out("a random %.0f%% of rows." % (SHARE * 100))
    out("")
    out("%-18s %12s %14s %10s %12s"
        % ("Charge", "Tolerance", "Overcharged", "Caught", "Catch rate"))
    for name in names:
        r = results[name]
        out("%-18s %11.0f%% %14d %10d %11.0f%%"
            % (name, r["tolerance"] * 100, r["n_overcharged"], r["caught"],
               r["catch_rate"] * 100))


def tolerance_sweep(out, names, frames, results):
    out.section("6. INVOICES FLAGGED BY TOLERANCE")
    grid = [0.05, 0.10, 0.15, 0.25, 0.50, 1.00]
    out("%-18s %s" % ("Charge", "".join("%10s" % ("%d%%" % (t * 100)) for t in grid)))
    for name in names:
        dev = frames[name]["dev_" + results[name]["best_benchmark"]].to_numpy(float)
        out("%-18s %s" % (name, "".join("%9.0f%%" % (100 * (dev > 1 + t).mean())
                                        for t in grid)))
