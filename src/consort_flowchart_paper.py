"""Publication-quality CONSORT-style flow diagram (fixed layout, matplotlib)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch

COL_EDGE = "#4D4D4D"
COL_MAIN_FACE = "#FFFFFF"
COL_EXCL_FACE = "#F2F2F2"
FONT_MAIN = 9.5
FONT_EXCL = 8.5

# Layout in axes coordinates [0, 1]
MAIN_CX = 0.5
MAIN_W = 0.42
MAIN_H = 0.16
MAIN_Y = (0.78, 0.48, 0.18)

EXCL_CX = 0.78
EXCL_W = 0.28
EXCL_H = 0.12
EXCL_Y = (0.63, 0.33)


@dataclass(frozen=True)
class FlowBox:
    """One main-stage box."""

    lines: tuple[str, ...]


@dataclass(frozen=True)
class ExclusionBox:
    """Side exclusion between two main stages."""

    lines: tuple[str, ...]
    branch_y: float


@dataclass(frozen=True)
class ConsortFlowData:
    top: FlowBox
    middle: FlowBox
    bottom: FlowBox
    exclusions: tuple[ExclusionBox, ExclusionBox]


def _default_flow_data() -> ConsortFlowData:
    return ConsortFlowData(
        top=FlowBox(
            (
                "Resting-state EEG available",
                "and preprocessing completed",
                "N = 168 (ASD 80, TD 88)",
            )
        ),
        middle=FlowBox(
            (
                "Met usable epoch criterion",
                ">= 60 usable epochs (2 s each)",
                "N = 145 (ASD 65, TD 80)",
            )
        ),
        bottom=FlowBox(
            (
                "Primary analysis cohort",
                "N = 138 (ASD 61, TD 77)",
            )
        ),
        exclusions=(
            ExclusionBox(
                ("Excluded n = 23", "usable epochs < 60"),
                branch_y=EXCL_Y[0],
            ),
            ExclusionBox(
                ("Excluded n = 7", "invalid channel ratio > 20%"),
                branch_y=EXCL_Y[1],
            ),
        ),
    )


def load_flow_data(flow_csv: Path | None) -> ConsortFlowData:
    """Load counts from sample_inclusion_flow.csv or use fixed defaults."""
    if flow_csv is None or not flow_csv.exists():
        return _default_flow_data()

    df = pd.read_csv(flow_csv)

    def _row(stage: str) -> pd.Series:
        sub = df.loc[df["stage"] == stage]
        if sub.empty:
            raise ValueError(f"Missing stage {stage!r} in {flow_csv}")
        return sub.iloc[0]

    r0 = _row("participants_total")
    r1 = _row("min_usable_epochs_pass")
    r2 = _row("specparam_subject_qc_pass")

    excl1 = int(float(r1["excluded_total"])) if pd.notna(r1["excluded_total"]) else 23
    excl2 = int(float(r2["excluded_total"])) if pd.notna(r2["excluded_total"]) else 7

    return ConsortFlowData(
        top=FlowBox(
            (
                "Resting-state EEG available",
                "and preprocessing completed",
                f"N = {int(r0['n_total'])} (ASD {int(r0['n_ASD'])}, TD {int(r0['n_TD'])})",
            )
        ),
        middle=FlowBox(
            (
                "Met usable epoch criterion",
                ">= 60 usable epochs (2 s each)",
                f"N = {int(r1['n_total'])} (ASD {int(r1['n_ASD'])}, TD {int(r1['n_TD'])})",
            )
        ),
        bottom=FlowBox(
            (
                "Primary analysis cohort",
                f"N = {int(r2['n_total'])} (ASD {int(r2['n_ASD'])}, TD {int(r2['n_TD'])})",
            )
        ),
        exclusions=(
            ExclusionBox(
                (f"Excluded n = {excl1}", "usable epochs < 60"),
                branch_y=EXCL_Y[0],
            ),
            ExclusionBox(
                (f"Excluded n = {excl2}", "invalid channel ratio > 20%"),
                branch_y=EXCL_Y[1],
            ),
        ),
    )


def _apply_rc() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans", "sans-serif"],
            "font.size": FONT_MAIN,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def _rounded_box(
    ax: plt.Axes,
    cx: float,
    cy: float,
    w: float,
    h: float,
    *,
    facecolor: str,
    linewidth: float = 0.9,
) -> tuple[float, float, float, float]:
    """Draw rounded rectangle; return (left, bottom, right, top) in axes coords."""
    left, bottom = cx - w / 2, cy - h / 2
    patch = FancyBboxPatch(
        (left, bottom),
        w,
        h,
        boxstyle="round,pad=0.008,rounding_size=0.015",
        linewidth=linewidth,
        edgecolor=COL_EDGE,
        facecolor=facecolor,
        transform=ax.transAxes,
        clip_on=False,
        zorder=2,
    )
    ax.add_patch(patch)
    return left, bottom, left + w, bottom + h


def _centered_text(
    ax: plt.Axes,
    cx: float,
    cy: float,
    lines: tuple[str, ...],
    *,
    fontsize: float,
) -> None:
    text = "\n".join(lines)
    ax.text(
        cx,
        cy,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        color=COL_EDGE,
        linespacing=1.22,
        transform=ax.transAxes,
        zorder=3,
        clip_on=False,
    )


def _arrow(
    ax: plt.Axes,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    *,
    linewidth: float = 0.85,
) -> None:
    ax.annotate(
        "",
        xy=(x1, y1),
        xytext=(x0, y0),
        xycoords="axes fraction",
        textcoords="axes fraction",
        arrowprops=dict(
            arrowstyle="-|>",
            color=COL_EDGE,
            lw=linewidth,
            shrinkA=0,
            shrinkB=0,
            mutation_scale=9,
        ),
        zorder=1,
    )


def plot_consort_flow_paper(
    data: ConsortFlowData,
    out_base: Path,
    *,
    figsize: tuple[float, float] = (7.0, 5.0),
    dpi: int = 600,
) -> list[Path]:
    """
    Draw vertical CONSORT flow with two side exclusions.

    Returns list of saved file paths (png, pdf, svg).
    """
    _apply_rc()
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    mains = (data.top, data.middle, data.bottom)
    main_bounds: list[tuple[float, float, float, float]] = []

    for box, cy in zip(mains, MAIN_Y, strict=True):
        bounds = _rounded_box(
            ax, MAIN_CX, cy, MAIN_W, MAIN_H, facecolor=COL_MAIN_FACE
        )
        _centered_text(ax, MAIN_CX, cy, box.lines, fontsize=FONT_MAIN)
        main_bounds.append(bounds)

    for excl in data.exclusions:
        _rounded_box(
            ax, EXCL_CX, excl.branch_y, EXCL_W, EXCL_H, facecolor=COL_EXCL_FACE
        )
        _centered_text(
            ax, EXCL_CX, excl.branch_y, excl.lines, fontsize=FONT_EXCL
        )

    # Vertical arrows: bottom center -> top center
    for i in range(len(main_bounds) - 1):
        _, bottom0, _, top0 = main_bounds[i]
        _, bottom1, _, top1 = main_bounds[i + 1]
        _arrow(ax, MAIN_CX, bottom0, MAIN_CX, top1)

    # Horizontal branches to exclusion boxes (midpoint of each vertical segment)
    excl_left = EXCL_CX - EXCL_W / 2
    for i, excl in enumerate(data.exclusions):
        _, bottom0, _, _ = main_bounds[i]
        _, _, _, top1 = main_bounds[i + 1]
        mid_y = (bottom0 + top1) / 2.0
        _arrow(ax, MAIN_CX, mid_y, excl_left, excl.branch_y)

    saved: list[Path] = []
    out_base = Path(out_base)
    out_base.parent.mkdir(parents=True, exist_ok=True)
    save_kw: dict[str, Any] = dict(
        bbox_inches="tight",
        pad_inches=0.15,
        facecolor="white",
        edgecolor="none",
    )
    for ext in ("png", "pdf", "svg"):
        path = out_base.with_suffix(f".{ext}")
        kw = dict(save_kw)
        if ext == "png":
            kw["dpi"] = dpi
        fig.savefig(path, **kw)
        saved.append(path)

    plt.close(fig)
    return saved
