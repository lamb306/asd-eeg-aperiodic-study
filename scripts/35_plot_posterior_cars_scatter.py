#!/usr/bin/env python
"""
35_plot_posterior_cars_scatter.py
---------------------------------
绘制 ASD 组 posterior_exponent 与 CARS_total 的散点回归图（Nature Comm 风格）。
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy.stats import spearmanr


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    feature_csv = root / "outputs" / "tables" / "resting_features_locked.csv"
    part_csv = root / "data" / "participants" / "participants.csv"
    out_dir = root / "outputs" / "figures" / "clinical"
    out_dir.mkdir(parents=True, exist_ok=True)

    feat = pd.read_csv(feature_csv)
    part = pd.read_csv(part_csv)
    part["subject_id"] = part["subject_id"].astype(str)
    feat["subject_id"] = feat["subject_id"].astype(str)

    df = feat.merge(
        part[["subject_id", "group", "CARS_total"]],
        on=["subject_id", "group"],
        how="left",
    )
    df["CARS_total"] = pd.to_numeric(df["CARS_total"], errors="coerce")
    df = df[df["group"].astype(str).str.upper() == "ASD"].copy()
    df = df.dropna(subset=["posterior_exponent", "CARS_total"]).copy()

    rho, pval = spearmanr(df["posterior_exponent"], df["CARS_total"])

    sns.set_style("white")
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Arial", "Helvetica", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=(6.2, 4.8))
    sns.regplot(
        data=df,
        x="posterior_exponent",
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
    ax.set_xlabel("Posterior Exponent", fontsize=12)
    ax.set_ylabel("CARS Total", fontsize=12)
    ax.tick_params(axis="both", labelsize=10)

    stat_txt = f"Spearman's ρ = {rho:.2f}, p = {pval:.3f}"
    ax.text(
        0.98,
        0.98,
        stat_txt,
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=10.5,
        bbox={"facecolor": "white", "alpha": 0.85, "edgecolor": "none"},
    )

    fig.tight_layout()
    out_png = out_dir / "posterior_exponent_vs_cars_scatter.png"
    out_pdf = out_dir / "posterior_exponent_vs_cars_scatter.pdf"
    fig.savefig(out_png, dpi=400, bbox_inches="tight")
    fig.savefig(out_pdf, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out_png}")
    print(f"Saved: {out_pdf}")


if __name__ == "__main__":
    main()
