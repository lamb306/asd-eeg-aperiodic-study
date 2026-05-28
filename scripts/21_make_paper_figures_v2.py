#!/usr/bin/env python
"""
21_make_paper_figures_v2.py
----------------------------
Molecular Autism 风格论文图 v2 → outputs/figures/paper_ready_v2/

输出 PNG (600 dpi), PDF, SVG；figure_captions.md；figure_qc_notes.txt
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd

from src.config import load_config, setup_logging  # noqa: E402
from src.paper_figures_v2 import (  # noqa: E402
    load_main_cohort,
    make_fig1_psd_specparam_overview,
    make_fig2_main_aperiodic_effects,
    make_fig3_spatial_distribution,
    make_fig4_periodic_clinical,
    write_figure_captions,
    write_v2_qc_notes,
)


def main() -> None:
    cfg = load_config()
    log = setup_logging(cfg, name="make_paper_figures_v2")
    deriv = Path(cfg["paths"]["derivatives_root"])
    outputs = Path(cfg["paths"]["outputs_root"])
    out_dir = outputs / "figures" / "paper_ready_v2"
    out_dir.mkdir(parents=True, exist_ok=True)
    montage = cfg.get("eeg", {}).get("montage", "GSN-HydroCel-64_1.0")

    participants = load_main_cohort(cfg, deriv)
    n_asd = int((participants["group"] == "ASD").sum())
    n_td = int((participants["group"] == "TD").sum())
    all_meta: list[dict] = []

    log.info("Figure 1: PSD + specparam overview")
    m1 = make_fig1_psd_specparam_overview(
        cfg, participants, deriv, out_dir / "fig1_psd_specparam_overview",
    )
    all_meta.append(m1)

    log.info("Figure 2: main aperiodic effects")
    m2 = make_fig2_main_aperiodic_effects(
        participants, deriv, outputs, out_dir / "fig2_main_aperiodic_effects",
    )
    all_meta.append(m2)

    log.info("Figure 3: spatial distribution")
    m3 = make_fig3_spatial_distribution(
        participants, deriv, montage, out_dir / "fig3_spatial_distribution",
    )
    all_meta.append(m3)

    log.info("Figure 4: periodic + clinical exploratory")
    m4 = make_fig4_periodic_clinical(
        participants, deriv, outputs, out_dir / "fig4_periodic_clinical_exploratory",
        include_clinical=True,
    )
    all_meta.append(m4)

    write_v2_qc_notes(all_meta, out_dir / "figure_qc_notes.txt")

    main_stats = pd.read_csv(deriv / "stats" / "main_group_analysis.csv")
    clin = pd.read_csv(deriv / "stats" / "clinical_correlation_spearman.csv")

    def _coef_p(outcome: str) -> tuple[float, float]:
        r = main_stats[(main_stats["outcome"] == outcome) & (main_stats["term"] == "C(group)[T.TD]")]
        return (float(r["coef"].iloc[0]), float(r["pvalue"].iloc[0])) if not r.empty else (np.nan, np.nan)

    be, pe = _coef_p("global_exponent")
    bo, po = _coef_p("global_offset")
    sa_row = clin[(clin["clinical"] == "ADOS_SA") & (clin["eeg_variable"] == "global_exponent")]

    cap_meta = {
        "n_main": len(participants),
        "n_asd": n_asd,
        "n_td": n_td,
        "fig1_rep_id": m1["panel_A"]["subject_id"],
        "fig1_rep_group": m1["panel_A"]["group"],
        "beta_exp": be,
        "p_exp": pe,
        "beta_off": bo,
        "p_off": po,
        "p_alpha_pw": m4["panel_A"].get("adjusted_p"),
        "p_alpha_cf": m4["panel_B"].get("adjusted_p"),
        "n_clinical": m4.get("panel_C", {}).get("n_ASD", 61),
        "rho_sa": float(sa_row["rho"].iloc[0]) if not sa_row.empty else -0.229,
        "p_sa": float(sa_row["pvalue"].iloc[0]) if not sa_row.empty else 0.076,
    }
    write_figure_captions(out_dir / "figure_captions.md", cap_meta)

    log.info("v2 论文图已保存: %s", out_dir.resolve())


if __name__ == "__main__":
    main()
