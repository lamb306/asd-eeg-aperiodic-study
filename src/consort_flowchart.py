"""CONSORT-style participant flow diagram from sample_inclusion_flow.csv."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from src.paper_figures_v2 import PAPER_V2_RC, mm_figsize, save_v2_figure

BOX_FACE = "#F7F7F7"
BOX_EDGE = "#4D4D4D"
EXCL_FACE = "#FFF8F0"
EXCL_EDGE = "#C44E52"


def _load_flow_stages(flow_path: Path) -> list[dict[str, Any]]:
    """Parse inclusion CSV into ordered stages for plotting."""
    df = pd.read_csv(flow_path)
    key = {
        "participants_total": "enrolled",
        "preprocessing_success": "preprocessed",
        "min_usable_epochs_pass": "epochs",
        "specparam_subject_qc_pass": "specparam_qc",
        "main_analysis_complete_case": "primary",
    }
    stages: list[dict[str, Any]] = []
    prev_n: int | None = None
    for _, row in df.iterrows():
        stage_id = str(row["stage"])
        if stage_id not in key:
            continue
        n = int(row["n_total"])
        n_asd = int(row["n_ASD"])
        n_td = int(row["n_TD"])
        excluded = row.get("excluded_total")
        excl_n = int(excluded) if pd.notna(excluded) and float(excluded) > 0 else 0
        reason = str(row.get("exclusion_reason") or "").strip()
        stages.append(
            {
                "id": key[stage_id],
                "n": n,
                "n_asd": n_asd,
                "n_td": n_td,
                "excluded": excl_n,
                "reason": reason,
                "delta_from_prev": (prev_n - n) if prev_n is not None and prev_n > n else excl_n,
            }
        )
        prev_n = n
    return stages


def _box(
    ax: plt.Axes,
    cx: float,
    cy: float,
    w: float,
    h: float,
    text: str,
    *,
    facecolor: str = BOX_FACE,
    edgecolor: str = BOX_EDGE,
) -> FancyBboxPatch:
    patch = FancyBboxPatch(
        (cx - w / 2, cy - h / 2),
        w,
        h,
        boxstyle="round,rounding_size=0.02",
        linewidth=0.9,
        edgecolor=edgecolor,
        facecolor=facecolor,
        transform=ax.transAxes,
        zorder=2,
    )
    ax.add_patch(patch)
    ax.text(
        cx,
        cy,
        text,
        ha="center",
        va="center",
        fontsize=7.5,
        linespacing=1.25,
        transform=ax.transAxes,
        zorder=3,
    )
    return patch


def _arrow(
    ax: plt.Axes,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    *,
    style: str = "-|>",
    color: str = BOX_EDGE,
    linestyle: str = "solid",
) -> None:
    ax.add_patch(
        FancyArrowPatch(
            (x0, y0),
            (x1, y1),
            arrowstyle=style,
            mutation_scale=10,
            linewidth=0.9,
            color=color,
            linestyle=linestyle,
            transform=ax.transAxes,
            zorder=1,
            shrinkA=2,
            shrinkB=2,
        )
    )


def _stage_labels(stage: dict[str, Any]) -> tuple[str, str | None]:
    """Main box text and optional exclusion text (English, journal-ready)."""
    grp = f"N = {stage['n']} (ASD {stage['n_asd']}, TD {stage['n_td']})"
    sid = stage["id"]
    if sid == "enrolled":
        if stage.get("preproc_ok"):
            main = (
                "Resting-state EEG available;\n"
                f"preprocessing completed\n{grp}"
            )
        else:
            main = f"Resting-state EEG and metadata available\n{grp}"
        return main, None
    if sid == "preprocessed":
        main = f"Preprocessing completed\n{grp}"
        excl = None
        if stage["excluded"] > 0:
            excl = f"Excluded n = {stage['excluded']}\n{stage['reason']}"
        return main, excl
    if sid == "epochs":
        main = f"≥ 60 usable epochs (2 s each)\n{grp}"
        excl = f"Excluded n = {stage['excluded']}\nusable epochs < 60"
        return main, excl
    if sid == "specparam_qc":
        main = f"Specparam subject-level QC passed\n{grp}"
        excl = (
            f"Excluded n = {stage['excluded']}\n"
            "invalid channel ratio > 20%"
        )
        return main, excl
    # primary：与 specparam QC 同 N 时仍保留上一阶段的排除说明
    main = f"Primary analysis cohort\n{grp}"
    excl = None
    if stage["excluded"] > 0:
        excl = (
            f"Excluded n = {stage['excluded']}\n"
            "invalid channel ratio > 20%"
        )
    return main, excl


def plot_consort_flowchart(
    flow_path: Path,
    out_base: Path,
    *,
    language: str = "en",
) -> dict[str, Any]:
    """
    Draw vertical CONSORT flow from sample_inclusion_flow.csv.

    Parameters
    ----------
    language : 'en' only for on-figure labels; Chinese caption written separately.
    """
    if language != "en":
        raise ValueError("On-figure labels are English only; use caption file for 中文.")

    plt.rcParams.update(PAPER_V2_RC)
    stages = _load_flow_stages(flow_path)
    plot_stages: list[dict[str, Any]] = []
    for s in stages:
        if (
            s["id"] == "preprocessed"
            and plot_stages
            and plot_stages[-1]["id"] == "enrolled"
            and plot_stages[-1]["n"] == s["n"]
        ):
            plot_stages[-1]["preproc_ok"] = True
            continue
        if s["id"] == "primary" and plot_stages and plot_stages[-1]["n"] == s["n"]:
            plot_stages[-1]["id"] = "primary"
            continue
        plot_stages.append(s)

    n_boxes = len(plot_stages)
    fig_h = 55 + 22 * n_boxes
    fig, ax = plt.subplots(figsize=mm_figsize(180, fig_h))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    cx_main = 0.38
    cx_excl = 0.78
    bw_main = 0.52
    bw_excl = 0.36
    bh_main = 0.11
    bh_excl = 0.09
    y_top = 0.94
    y_step = 0.19

    meta_boxes: list[dict[str, Any]] = []
    ys: list[float] = []

    for i, stage in enumerate(plot_stages):
        cy = y_top - i * y_step
        ys.append(cy)
        main_txt, excl_txt = _stage_labels(stage)
        _box(ax, cx_main, cy, bw_main, bh_main, main_txt)
        meta_boxes.append({"stage": stage["id"], "y": cy, "exclusion": excl_txt})
        if excl_txt and stage["excluded"] > 0:
            _box(
                ax,
                cx_excl,
                cy,
                bw_excl,
                bh_excl,
                excl_txt,
                facecolor=EXCL_FACE,
                edgecolor=EXCL_EDGE,
            )
            _arrow(ax, cx_main + bw_main / 2 - 0.02, cy, cx_excl - bw_excl / 2 + 0.02, cy)

    for i in range(len(ys) - 1):
        _arrow(ax, cx_main, ys[i] - bh_main / 2 - 0.01, cx_main, ys[i + 1] + bh_main / 2 + 0.01)

    ax.text(
        0.5,
        0.02,
        "CONSORT-style flow for resting-state EEG aperiodic analysis (specparam).",
        ha="center",
        fontsize=7,
        color="#666666",
        transform=ax.transAxes,
    )

    out_base = Path(out_base)
    save_v2_figure(fig, out_base)
    plt.close(fig)

    return {
        "figure": str(out_base),
        "n_stages": len(plot_stages),
        "stages": [s["id"] for s in plot_stages],
        "final_n": plot_stages[-1]["n"],
    }
