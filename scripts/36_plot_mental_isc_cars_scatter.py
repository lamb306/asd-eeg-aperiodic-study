#!/usr/bin/env python
"""
Plot mental ISC vs CARS_total (ASD).
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy.stats import spearmanr


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    isc = pd.read_csv(root / "derivatives_task_movie" / "stats" / "movie_isc_subject_values.csv")
    part = pd.read_csv(root / "data" / "participants" / "participants.csv")

    isc = isc[isc["event_type"].astype(str).str.lower() == "mental"].copy()
    isc["subject_id"] = isc["subject_id"].astype(str)
    isc["group"] = isc["group"].astype(str).str.upper()

    part["subject_id"] = part["subject_id"].astype(str)
    part["group"] = part["group"].astype(str).str.upper()
    part["CARS_total"] = pd.to_numeric(part["CARS_total"], errors="coerce")
    part["included_final"] = pd.to_numeric(part["included_final"], errors="coerce")

    df = isc.merge(
        part[["subject_id", "group", "CARS_total", "included_final"]],
        on=["subject_id", "group"],
        how="left",
    )
    df = df[(df["group"] == "ASD") & (df["included_final"] == 1)].copy()
    df["isc_z"] = pd.to_numeric(df["isc_z"], errors="coerce")
    df["CARS_total"] = pd.to_numeric(df["CARS_total"], errors="coerce")
    df = df.dropna(subset=["isc_z", "CARS_total"]).copy()

    rho, pval = spearmanr(df["isc_z"], df["CARS_total"])

    out_dir = root / "outputs" / "figures" / "clinical"
    out_dir.mkdir(parents=True, exist_ok=True)

    sns.set_style("white")
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Arial", "Helvetica", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=(6.2, 4.8))
    sns.regplot(
        data=df,
        x="isc_z",
        y="CARS_total",
        ci=95,
        scatter_kws={
            "s": 40,
            "alpha": 0.70,
            "color": "#2a6fbb",
            "edgecolor": "none",
        },
        line_kws={
            "color": "#1b1b1b",
            "linewidth": 2.0,
        },
        ax=ax,
    )
    sns.despine(ax=ax, top=True, right=True)
    ax.set_xlabel("Mental ISC (Fisher z)", fontsize=12)
    ax.set_ylabel("CARS Total", fontsize=12)
    ax.tick_params(axis="both", labelsize=10)
    ax.text(
        0.98,
        0.98,
        f"Spearman's rho = {rho:.2f}, p = {pval:.3f}",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=10.5,
        bbox={"facecolor": "white", "alpha": 0.85, "edgecolor": "none"},
    )
    fig.tight_layout()

    out_png = out_dir / "mental_isc_vs_cars_scatter.png"
    out_pdf = out_dir / "mental_isc_vs_cars_scatter.pdf"
    fig.savefig(out_png, dpi=400, bbox_inches="tight")
    fig.savefig(out_pdf, bbox_inches="tight")
    plt.close(fig)

    print(f"n={len(df)}")
    print(f"rho={rho:.6f}, p={pval:.6f}")
    print(f"Saved: {out_png}")
    print(f"Saved: {out_pdf}")


if __name__ == "__main__":
    main()
