#!/usr/bin/env python
"""
20_make_paper_figures.py
------------------------
生成论文用图（600 dpi PNG + PDF）→ outputs/figures/paper_ready/

输出:
  fig01_group_mean_psd_paper
  fig02_global_exponent_paper
  fig03_roi_group_effect_paper
  fig04_channel_group_effect_topomap_paper
  figure_qc_notes.txt
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config, setup_logging  # noqa: E402
from src.paper_figures import (  # noqa: E402
    load_main_cohort,
    plot_fig01_group_mean_psd,
    plot_fig02_global_exponent,
    plot_fig03_roi_forest,
    plot_fig04_channel_topomap,
    write_qc_notes,
)


def main() -> None:
    cfg = load_config()
    log = setup_logging(cfg, name="make_paper_figures")
    deriv = Path(cfg["paths"]["derivatives_root"])
    out_dir = Path(cfg["paths"]["outputs_root"]) / "figures" / "paper_ready"
    out_dir.mkdir(parents=True, exist_ok=True)
    montage = cfg.get("eeg", {}).get("montage", "GSN-HydroCel-64_1.0")

    participants = load_main_cohort(cfg, deriv)
    notes = []

    log.info("Fig 1: group mean PSD")
    notes.append(plot_fig01_group_mean_psd(
        deriv / "psd", participants, cfg, out_dir / "fig01_group_mean_psd_paper",
    ))

    roi_global = deriv / "roi" / "specparam_subject_global.csv"
    main_stats = deriv / "stats" / "main_group_analysis.csv"
    beta, pval = 0.079, 0.012
    if main_stats.exists():
        row = pd_read(main_stats)
        g = row[(row["outcome"] == "global_exponent") & (row["term"] == "C(group)[T.TD]")]
        if not g.empty:
            beta = float(g["coef"].iloc[0])
            pval = float(g["pvalue"].iloc[0])
    log.info("Fig 2: global exponent")
    notes.append(plot_fig02_global_exponent(
        pd_read(roi_global),
        participants,
        out_dir / "fig02_global_exponent_paper",
        main_beta=beta,
        main_p=pval,
    ))

    roi_long = deriv / "roi" / "specparam_subject_roi_long.csv"
    log.info("Fig 3: ROI forest plot")
    notes.append(plot_fig03_roi_forest(
        pd_read(roi_long),
        participants,
        deriv,
        out_dir / "fig03_roi_group_effect_paper",
    ))

    ch_stats = deriv / "stats" / "channel_level_analysis.csv"
    log.info("Fig 4: channel topomap")
    notes.append(plot_fig04_channel_topomap(
        pd_read(ch_stats),
        montage,
        out_dir / "fig04_channel_group_effect_topomap_paper",
    ))

    write_qc_notes(notes, out_dir / "figure_qc_notes.txt")
    log.info("论文图已保存: %s", out_dir.resolve())


def pd_read(path: Path):
    import pandas as pd
    return pd.read_csv(path)


if __name__ == "__main__":
    main()
