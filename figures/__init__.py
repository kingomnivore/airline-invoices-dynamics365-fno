"""One module per figure. Each exposes render(...) and writes a PNG."""

from figures import deviation, fits, rate_spread, review_burden

__all__ = ["rate_spread", "fits", "deviation", "review_burden"]
