#!/usr/bin/env python
"""
68_knot_to_ados_mapping.py
--------------------------
将阈值分段模型的 knot（posterior_exponent）映射为 ADOS_total 的可解释数值：
1) 拐点处模型预测 ADOS（未校正 / 协变量校正）
2) 拐点附近真实观测 ADOS 分布（多个带宽）

输出（按 cohort 分别保存）：
- <outputs_root>/tables/knot_to_ados_mapping.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config, setup_logging  # noqa: E402
from src.io_utils import (  # noqa: E402
    attach_usable_epochs,
    exclude_specparam_low_quality,
    load_analysis_participants,
    save_csv,
)


def build_asd_df(cfg_path: Path) -> tuple[pd.DataFrame, Path]:
    cfg = load_config(cfg_path)
    deriv = Path(cfg["paths"]["derivatives_root"])
    out_root = Path(cfg["paths"]["outputs_root"])

    participants = load_analysis_participants(cfg)
    roi = pd.read_csv(deriv / "roi" / "specparam_subject_global.csv")
    df = participants.merge(roi, on=["subject_id", "group"], how="inner")
    df = attach_usable_epochs(df, deriv)
    df = exclude_specparam_low_quality(df, deriv)
    df = df[df["group"].astype(str).str.upper() == "ASD"].copy()

    if "posterior_exponent" not in df.columns:
        need = ["parietal_exponent", "occipital_exponent"]
        miss = [c for c in need if c not in df.columns]
        if miss:
            raise ValueError(f"无法构造 posterior_exponent，缺少: {miss}")
        df["posterior_exponent"] = df[need].mean(axis=1)
    return df, out_root


def map_knot_to_ados(df: pd.DataFrame, knot: float, model_set: str) -> list[dict[str, float | int | str]]:
    rows: list[dict[str, float | int | str]] = []
    bands = [0.03, 0.05, 0.08]

    # Unadjusted
    if model_set == "unadjusted_threshold":
        sub = df.dropna(subset=["ADOS_total", "posterior_exponent"]).copy()
        sub["hinge"] = np.maximum(sub["posterior_exponent"] - knot, 0.0)
        m = smf.ols("ADOS_total ~ posterior_exponent + hinge", data=sub).fit()
        pred = float(m.predict(pd.DataFrame({"posterior_exponent": [knot], "hinge": [0.0]}))[0])
        rows.append(
            {
                "model_set": model_set,
                "prediction_scenario": "unadjusted",
                "knot_posterior_exponent": float(knot),
                "predicted_ados_at_knot": pred,
                "n_model": int(len(sub)),
                "mean_age_months": np.nan,
                "mean_iq_total": np.nan,
                "mean_usable_epochs": np.nan,
                "sex_for_prediction": "",
                "near_band_width": np.nan,
                "n_near": np.nan,
                "ados_mean_near": np.nan,
                "ados_median_near": np.nan,
                "ados_min_near": np.nan,
                "ados_max_near": np.nan,
            },
        )
        for bw in bands:
            near = sub[np.abs(sub["posterior_exponent"] - knot) <= bw]["ADOS_total"]
            rows.append(
                {
                    "model_set": model_set,
                    "prediction_scenario": f"observed_near_knot_bw_{bw:.2f}",
                    "knot_posterior_exponent": float(knot),
                    "predicted_ados_at_knot": np.nan,
                    "n_model": int(len(sub)),
                    "mean_age_months": np.nan,
                    "mean_iq_total": np.nan,
                    "mean_usable_epochs": np.nan,
                    "sex_for_prediction": "",
                    "near_band_width": float(bw),
                    "n_near": int(len(near)),
                    "ados_mean_near": float(near.mean()) if len(near) else np.nan,
                    "ados_median_near": float(near.median()) if len(near) else np.nan,
                    "ados_min_near": float(near.min()) if len(near) else np.nan,
                    "ados_max_near": float(near.max()) if len(near) else np.nan,
                },
            )

    # Adjusted
    if model_set == "adjusted_threshold":
        sub = df.dropna(
            subset=["ADOS_total", "posterior_exponent", "age_months", "sex", "IQ_total", "usable_epochs"],
        ).copy()
        sub["hinge"] = np.maximum(sub["posterior_exponent"] - knot, 0.0)
        m = smf.ols(
            "ADOS_total ~ posterior_exponent + hinge + age_months + C(sex) + IQ_total + usable_epochs",
            data=sub,
        ).fit()
        mean_age = float(sub["age_months"].mean())
        mean_iq = float(sub["IQ_total"].mean())
        mean_ep = float(sub["usable_epochs"].mean())
        for sx in ["F", "M"]:
            pred = float(
                m.predict(
                    pd.DataFrame(
                        {
                            "posterior_exponent": [knot],
                            "hinge": [0.0],
                            "age_months": [mean_age],
                            "sex": [sx],
                            "IQ_total": [mean_iq],
                            "usable_epochs": [mean_ep],
                        },
                    ),
                )[0],
            )
            rows.append(
                {
                    "model_set": model_set,
                    "prediction_scenario": "adjusted_cov_means",
                    "knot_posterior_exponent": float(knot),
                    "predicted_ados_at_knot": pred,
                    "n_model": int(len(sub)),
                    "mean_age_months": mean_age,
                    "mean_iq_total": mean_iq,
                    "mean_usable_epochs": mean_ep,
                    "sex_for_prediction": sx,
                    "near_band_width": np.nan,
                    "n_near": np.nan,
                    "ados_mean_near": np.nan,
                    "ados_median_near": np.nan,
                    "ados_min_near": np.nan,
                    "ados_max_near": np.nan,
                },
            )
    return rows


def run_for_cohort(cohort: str, cfg_path: Path, log) -> None:
    if not cfg_path.exists():
        return
    df, out_root = build_asd_df(cfg_path)
    nl_path = out_root / "tables" / "ados_posterior_nonlinear_spline_threshold.csv"
    if not nl_path.exists():
        log.warning("cohort=%s 缺少非线性结果文件: %s", cohort, nl_path)
        return

    nl = pd.read_csv(nl_path)
    nl = nl[nl["cohort"] == cohort].copy() if "cohort" in nl.columns else nl.copy()
    if nl.empty:
        log.warning("cohort=%s 在非线性表中无记录", cohort)
        return

    out_rows: list[dict[str, float | int | str]] = []
    for ms in ["unadjusted_threshold", "adjusted_threshold"]:
        sub = nl[nl["model_set"] == ms]
        if sub.empty:
            continue
        knot = float(pd.to_numeric(sub.iloc[0]["best_knot_posterior_exponent"], errors="coerce"))
        out_rows.extend(map_knot_to_ados(df, knot, ms))

    if not out_rows:
        log.warning("cohort=%s 未生成 knot 映射结果", cohort)
        return

    out_df = pd.DataFrame(out_rows)
    out_df.insert(0, "cohort", cohort)
    out_path = out_root / "tables" / "knot_to_ados_mapping.csv"
    save_csv(out_df, out_path)
    log.info("cohort=%s 输出: %s", cohort, out_path)


def main() -> None:
    log = setup_logging(load_config(), name="knot_to_ados_mapping")
    cohorts = {
        "matched": PROJECT_ROOT / "config" / "config_resting_matched.yaml",
        "matched_postqc": PROJECT_ROOT / "config" / "config_resting_matched_postqc.yaml",
    }
    for cohort, cfg_path in cohorts.items():
        run_for_cohort(cohort, cfg_path, log)


if __name__ == "__main__":
    main()
