#!/usr/bin/env python3
"""
timeline.py

Create a timeline image showing the number of days between a start date and an end date,
and clearly mark today's date if it falls within the range.

Usage:
    python timeline.py 2025-01-01 2025-03-15 --output timeline.png
"""
from datetime import datetime, date, timedelta
import argparse
# import math
import sys

# Use a non-interactive backend for environments without a display
import matplotlib
matplotlib.use("Agg")
from matplotlib import transforms as mtransforms
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def parse_date(s: str) -> date:
    formats = ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%m/%d/%Y", "%Y.%m.%d")
    for fmt in formats:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    # Last resort: try ISO parse
    try:
        return date.fromisoformat(s)
    except Exception:
        pass
    raise argparse.ArgumentTypeError(f"Unrecognized date format: {s!r}. Use YYYY-MM-DD or common variants.")


def choose_tick_interval(days: int) -> int:
    if days <= 14:
        return 1
    if days <= 60:
        return 7
    if days <= 365:
        return 30
    # for multi-year ranges, show ticks roughly every 90-365 days
    return max(90, int(days / 8))


def build_timeline(start: date, end: date, out_path: str) -> None:
    if end < start:
        raise ValueError("End date must be on or after start date.")
    # number of days between start and end (0 if same day)
    raw_span = (end - start).days
    total_span_days = max(1, raw_span)  # avoid zero-length for plotting

    today = date.today()
    days_from_start_to_today = (today - start).days

    # Layout: variable width based on days, and ensure bar is 100 pixels high.
    dpi = 100
    # Default max width for reasonable images; will be capped to display max below.
    max_width_px = 1600
    px_per_day = max(3.0, min(12.0, max_width_px / max(1, total_span_days)))
    padding_px = 200
    width_px = int(px_per_day * total_span_days + padding_px)
    width_in = max(6.0, width_px / dpi)

    # Reserve some vertical padding around the 100px bar
    bar_px = 100
    vert_padding_px = 80
    height_px = bar_px + vert_padding_px
    height_in = max(1.2, height_px / dpi)

    # Ensure the final image will fit on an Apple Pro Display XDR (6016x3384 px).
    # If image is larger, cap the width/height so it fits. Keep bar height at 100px if possible.
    display_max_width_px = 6016
    display_max_height_px = 3384

    if width_px > display_max_width_px:
        # reduce width in pixels to fit the display; keep vertical size unchanged so bar stays 100px
        width_px = display_max_width_px
    if height_px > display_max_height_px:
        # very unlikely, but cap height while attempting to keep the bar at 100px
        # if display_max_height_px is smaller than the bar height, force bar to that height
        if display_max_height_px >= bar_px + 20:
            height_px = display_max_height_px
        else:
            # fallback: ensure at least a tiny padding
            height_px = bar_px + 8

    # Recompute figure size in inches from possibly-adjusted pixel dims
    width_in = max(3.0, width_px / dpi)
    height_in = max(0.8, height_px / dpi)

    fig, ax = plt.subplots(figsize=(width_in, height_in), dpi=dpi)
    ax.set_xlim(0, total_span_days)
    ax.set_ylim(0, 1)
    ax.axis("off")
    # Compute bar height as fraction of axes height (for use with blended transform)
    bar_frac = bar_px / height_px
    trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)

    # Draw blue horizontal bar (spanning the date range in data coordinates, 100px tall in screen space)
    bar = Rectangle((0, 0.5 - bar_frac / 2), total_span_days, bar_frac, transform=trans,
                    facecolor="#1f77b4", edgecolor=None, zorder=1)
    ax.add_patch(bar)

    # Draw black vertical markers for 10 equidistant dates across the range (including start and end)
    n_markers = 10
    if total_span_days == 0:
        positions = [0.0]
    else:
        # positions include both endpoints
        positions = [i * total_span_days / (n_markers - 1) for i in range(n_markers)]
    for pos in positions:
        ax.vlines(pos,
                  0.5 - bar_frac / 2 - 0.02,
                  0.5 + bar_frac / 2 + 0.02,
                  transform=trans,
                  colors="black",
                  linewidth=1.4,
                  zorder=3,
                  alpha=0.9)

    # Label each equidistant date under the bar (skip explicit duplicates for start/end since they are labeled separately)
    label_y = 0.5 - bar_frac / 2 - 0.08
    for i, pos in enumerate(positions):
        # skip endpoints; start/end are labeled later to keep alignment/justification consistent
        if i == 0 or i == len(positions) - 1:
            continue
        days_offset = int(round(pos))
        label_date = (start + timedelta(days=days_offset)).isoformat()
        ax.text(pos, label_y, label_date, transform=trans, ha="center", va="top", fontsize=9, color="black", zorder=5)

    # Draw red line for today if within range
    if 0 <= days_from_start_to_today <= total_span_days:
        x = float(days_from_start_to_today)
        ax.vlines(x,
                  0.5 - bar_frac / 2 - 0.04,
                  0.5 + bar_frac / 2 + 0.04,
                  transform=trans,
                  colors="#d32f2f",
                  linewidth=2.0,
                  zorder=4)
        ax.text(x, 0.5 + bar_frac / 2 + 0.08, f"Today\n{today.isoformat()}",
                transform=trans, ha="center", va="bottom", fontsize=9, color="#d32f2f", zorder=5)

    # Optional: show start/end labels near the ends
    ax.text(0, label_y, start.isoformat(), transform=trans, ha="left", va="top", fontsize=9)
    ax.text(total_span_days, label_y, end.isoformat(), transform=trans, ha="right", va="top", fontsize=9)

    # Save image
    plt.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate a timeline image for a date range and mark today if inside it.")
    parser.add_argument("start", type=parse_date, help="Start date (e.g. 2025-01-01)")
    parser.add_argument("end", type=parse_date, help="End date (e.g. 2025-03-15)")
    parser.add_argument("--output", "-o", default="timeline.png", help="Output image file (PNG). Default: timeline.png")
    args = parser.parse_args(argv)

    try:
        build_timeline(args.start, args.end, args.output)
        print(f"Saved timeline image to {args.output}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()