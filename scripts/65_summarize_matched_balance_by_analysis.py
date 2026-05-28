#!/usr/bin/env python
"""
65_summarize_matched_balance_by_analysis.py
------------------------------------------
汇总 matched 队列在关键分析数据集中的组间平衡情况（ASD vs TD）。

输出：
- outputs_matched_resting/tables/matched_qc_balance_by_analysis.csv
"""

from __future__ import annotations

import sys
import argparse
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config, setup_logging  # noqa: E402
from src.io_utils import (  # noqa: E402
    attach_usable_epochs,
    exclude_specparam_low_quality,
    load_analysis_participants,
    save_csv,
)


def _pooled_sd(x: pd.Series, y: pd.Series) -> float:
    x = pd.to_numeric(x, errors="coerce").dropna()
    y = pd.to_numeric(y, errors="coerce").dropna()
    if len(x) < 2 or len(y) < 2:
        return float("nan")
    vx = x.var(ddof=1)
    vy = y.var(ddof=1)
    return float(np.sqrt((vx + vy) / 2.0))


def _smd_cont(x: pd.Series, y: pd.Series) -> float:
    sd = _pooled_sd(x, y)
    if np.isnan(sd) or sd == 0:
        return float("nan")
    return float((pd.to_numeric(x, errors="coerce").mean() - pd.to_numeric(y, errors="coerce").mean()) / sd)


def _smd_binary(x: pd.Series, y: pd.Series) -> float:
    # x/y: 0-1 binary
    px = pd.to_numeric(x, errors="coerce").mean()
    py = pd.to_numeric(y, errors="coerce").mean()
    pbar = (px + py) / 2.0
    den = np.sqrt(pbar * (1.0 - pbar))
    if den == 0 or np.isnan(den):
        return float("nan")
    return float((px - py) / den)


def _summarize_balance(df: pd.DataFrame, analysis_name: str, note: str = "") -> dict[str, Any]:
    out: dict[str, Any] = {"analysis": analysis_name, "note": note}
    g = df.copy()
    g["group"] = g["group"].astype(str).str.upper()
    asd = g[g["group"] == "ASD"].copy()
    td = g[g["group"] == "TD"].copy()

    out["n_total"] = int(len(g))
    out["n_asd"] = int(len(asd))
    out["n_td"] = int(len(td))
    out["n_diff_asd_minus_td"] = int(len(asd) - len(td))

    for v in ["age_months", "IQ_total", "usable_epochs"]:
        out[f"{v}_mean_asd"] = float(pd.to_numeric(asd[v], errors="coerce").mean()) if v in asd.columns else np.nan
        out[f"{v}_mean_td"] = float(pd.to_numeric(td[v], errors="coerce").mean()) if v in td.columns else np.nan
        out[f"{v}_smd_asd_minus_td"] = _smd_cont(asd[v], td[v]) if v in asd.columns and v in td.columns else np.nan

    if "sex" in g.columns:
        asd_m = (asd["sex"].astype(str).str.upper() == "M").astype(float)
        td_m = (td["sex"].astype(str).str.upper() == "M").astype(float)
        out["male_prop_asd"] = float(asd_m.mean()) if len(asd_m) else np.nan
        out["male_prop_td"] = float(td_m.mean()) if len(td_m) else np.nan
        out["male_prop_diff_asd_minus_td"] = (
            float(out["male_prop_asd"] - out["male_prop_td"])
            if not (np.isnan(out["male_prop_asd"]) or np.isnan(out["male_prop_td"]))
            else np.nan
        )
        out["sex_smd_asd_minus_td"] = _smd_binary(asd_m, td_m) if len(asd_m) and len(td_m) else np.nan
    else:
        out["male_prop_asd"] = np.nan
        out["male_prop_td"] = np.nan
        out["male_prop_diff_asd_minus_td"] = np.nan
        out["sex_smd_asd_minus_td"] = np.nan

    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize matched balance across analysis datasets.")
    parser.add_argument(
        "--config",
        type=str,
        default=str(PROJECT_ROOT / "config" / "config_resting_matched.yaml"),
        help="Path to config yaml.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_config(Path(args.config))
    log = setup_logging(cfg, name="matched_balance_summary")
    deriv = Path(cfg["paths"]["derivatives_root"])
    out_root = Path(cfg["paths"]["outputs_root"])
    out_path = out_root / "tables" / "matched_qc_balance_by_analysis.csv"

    part = load_analysis_participants(cfg)
    roi = pd.read_csv(deriv / "roi" / "specparam_subject_global.csv")

    rows: list[dict[str, Any]] = []

    rows.append(_summarize_balance(part, "01_initial_matched_analysis_participants"))

    step2 = part.merge(roi, on=["subject_id", "group"], how="inner")
    rows.append(_summarize_balance(step2, "02_after_roi_merge"))

    step3 = attach_usable_epochs(step2, deriv)
    rows.append(_summarize_balance(step3, "03_after_attach_usable_epochs"))

    step4 = exclude_specparam_low_quality(step3, deriv)
    rows.append(_summarize_balance(step4, "04_after_specparam_low_quality_exclusion"))

    step5 = step4.dropna(subset=["global_exponent", "age_months", "sex", "IQ_total", "usable_epochs"]).copy()
    rows.append(_summarize_balance(step5, "05_group_model_complete_qcstrict"))

    ml_path = out_root / "tables" / "ml_asd_td_auc_posterior_ageIQ_dataset_used.csv"
    if ml_path.exists():
        ml_df = pd.read_csv(ml_path)
        rows.append(_summarize_balance(ml_df, "06_ml_dataset_used_posterior_ageIQ"))
    else:
        rows.append(
            {
                "analysis": "06_ml_dataset_used_posterior_ageIQ",
                "note": f"missing file: {ml_path}",
            },
        )

    out_df = pd.DataFrame(rows)
    save_csv(out_df, out_path)
    log.info("输出: %s", out_path)


if __name__ == "__main__":
    main()
