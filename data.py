"""Loading and filtering of BTS Schedule P-5.2 filings."""

import pandas as pd

from config import CHARGES, DATA_DIR, ENTITY, MIN_AMOUNT, MIN_QUARTERS, ROOT


def load():
    """Concatenate every P-5.2 CSV under DATA_DIR."""
    files = sorted(DATA_DIR.glob("**/T_F41SCHEDULE_P52.csv"))
    if not files:
        raise FileNotFoundError(
            "No P-5.2 CSVs found under %s. Download from transtats.bts.gov, "
            "Air Carrier Financial, Schedule P-5.2." % DATA_DIR
        )
    df = pd.concat([pd.read_csv(f, low_memory=False) for f in files],
                   ignore_index=True)
    df["PERIOD"] = df.YEAR.astype(str) + "Q" + df.QUARTER.astype(str)
    df.attrs["files"] = [str(f.relative_to(ROOT)) for f in files]
    return df


def frame(df, charge, require_history=True):
    """Rows for one charge, with the unit rate and its deviation from each benchmark.

    Amounts are in $000 and drivers in thousands, so amount / driver is dollars
    per unit. Deviation columns are named dev_<benchmark>; 1.0 sits exactly on
    the benchmark.
    """
    c = CHARGES[charge]
    d = df[ENTITY + ["PERIOD", c["amount"], c["driver"]]].dropna()
    d = d[(d[c["amount"]] > MIN_AMOUNT) & (d[c["driver"]] > 0)].copy()
    d["rate"] = d[c["amount"]] / d[c["driver"]]

    d["dev_industry"] = d["rate"] / d["rate"].median()
    d["dev_indexed"] = d["rate"] / d.groupby("PERIOD")["rate"].transform("median")

    if require_history:
        d = d[d.groupby(ENTITY)["rate"].transform("size") >= MIN_QUARTERS].copy()

    own = d.groupby(ENTITY)["dev_indexed"].transform("median")
    d["dev_contract"] = d["dev_indexed"] / own

    d.attrs["amount_col"] = c["amount"]
    d.attrs["driver_col"] = c["driver"]
    return d


def arrays(d):
    """Amount and driver as float arrays."""
    return (d[d.attrs["amount_col"]].to_numpy(float),
            d[d.attrs["driver_col"]].to_numpy(float))
