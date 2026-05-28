#!/usr/bin/env python
"""
62_nonlinear_ados_posterior_spline.py
-------------------------------------
检验 ASD 组 ADOS_total 与 posterior_exponent 的非线性关系：
1) 线性模型 vs 样条模型（bs basis）
2) 阈值分段模型（grid-search knot 的 hinge regression）

输出：
- outputs/tables/ados_posterior_nonlinear_spline_threshold.csv
- outputs_matched_resting/tables/ados_posterior_nonlinear_spline_threshold.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from patsy import bs

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config, setup_logging  # noqa: E402
from src.io_utils import (  # noqa: E402
    attach_usable_epochs,
    exclude_specparam_low_quality,
    load_analysis_participants,
    save_csv,
)


def build_asd_dataset(cfg_path: Path) -> tuple[pd.DataFrame, Path]:
    """读取指定 config 的 ASD 数据，并构造 posterior_exponent。"""
    cfg = load_config(cfg_path)
    deriv = Path(cfg["paths"]["derivatives_root"])
    out_root = Path(cfg["paths"]["outputs_root"])
    roi_path = deriv / "roi" / "specparam_subject_global.csv"
    if not roi_path.exists():
        raise FileNotFoundError(f"未找到 ROI 文件: {roi_path}")

    participants = load_analysis_participants(cfg)
    roi = pd.read_csv(roi_path)
    df = participants.merge(roi, on=["subject_id", "group"], how="inner")
    df = attach_usable_epochs(df, deriv)
    df = exclude_specparam_low_quality(df, deriv)
    df = df[df["group"].astype(str).str.upper() == "ASD"].copy()

    if "posterior_exponent" not in df.columns:
        required = ["parietal_exponent", "occipital_exponent"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"无法构造 posterior_exponent，缺少列: {missing}")
        # 采用后部 ROI（顶叶+枕叶）均值作为 posterior_exponent。
        df["posterior_exponent"] = df[required].mean(axis=1)

    return df, out_root


def fit_nonlinear_models(df: pd.DataFrame) -> list[dict[str, float | int | str]]:
    """拟合线性 / 样条 / 阈值模型，返回汇总行。"""
    base_cols = ["ADOS_total", "posterior_exponent"]
    covars = ["age_months", "sex", "IQ_total", "usable_epochs"]
    results: list[dict[str, float | int | str]] = []

    # Unadjusted
    sub_u = df.dropna(subset=base_cols).copy()
    if len(sub_u) >= 15 and sub_u["posterior_exponent"].nunique() >= 8:
        lin_u = smf.ols("ADOS_total ~ posterior_exponent", data=sub_u).fit()
        spl_u = smf.ols(
            "ADOS_total ~ bs(posterior_exponent, df=4, include_intercept=False)",
            data=sub_u,
        ).fit()
        f_u, p_u, _ = spl_u.compare_f_test(lin_u)
        results.append(
            {
                "model_set": "unadjusted",
                "n": int(len(sub_u)),
                "linear_r2": float(lin_u.rsquared),
                "linear_aic": float(lin_u.aic),
                "spline_r2": float(spl_u.rsquared),
                "spline_aic": float(spl_u.aic),
                "delta_aic_spline_minus_linear": float(spl_u.aic - lin_u.aic),
                "spline_vs_linear_F": float(f_u),
                "spline_vs_linear_p": float(p_u),
            }
        )

        # 阈值模型：hinge with grid-searched knot（探索性）。
        ks = np.quantile(sub_u["posterior_exponent"].to_numpy(), np.linspace(0.20, 0.80, 41))
        best = None
        for k in np.unique(np.round(ks, 6)):
            tmp = sub_u.copy()
            tmp["hinge"] = np.maximum(tmp["posterior_exponent"] - k, 0.0)
            m = smf.ols("ADOS_total ~ posterior_exponent + hinge", data=tmp).fit()
            if best is None or m.aic < best[0]:
                best = (m.aic, float(k), m)
        assert best is not None
        _, knot_u, pw_u = best
        results.append(
            {
                "model_set": "unadjusted_threshold",
                "n": int(len(sub_u)),
                "best_knot_posterior_exponent": float(knot_u),
                "piecewise_aic": float(pw_u.aic),
                "piecewise_r2": float(pw_u.rsquared),
                "delta_aic_piecewise_minus_linear": float(pw_u.aic - lin_u.aic),
                "slope_before_knot": float(pw_u.params.get("posterior_exponent", np.nan)),
                "slope_change_after_knot": float(pw_u.params.get("hinge", np.nan)),
                "slope_after_knot": float(
                    pw_u.params.get("posterior_exponent", np.nan)
                    + pw_u.params.get("hinge", np.nan)
                ),
                "hinge_pvalue": float(pw_u.pvalues.get("hinge", np.nan)),
            }
        )

    # Adjusted sensitivity
    sub_a = df.dropna(subset=base_cols + covars).copy()
    if len(sub_a) >= 20 and sub_a["posterior_exponent"].nunique() >= 8:
        lin_a = smf.ols(
            "ADOS_total ~ posterior_exponent + age_months + C(sex) + IQ_total + usable_epochs",
            data=sub_a,
        ).fit()
        spl_a = smf.ols(
            "ADOS_total ~ bs(posterior_exponent, df=4, include_intercept=False) + age_months + C(sex) + IQ_total + usable_epochs",
            data=sub_a,
        ).fit()
        f_a, p_a, _ = spl_a.compare_f_test(lin_a)
        results.append(
            {
                "model_set": "adjusted",
                "n": int(len(sub_a)),
                "linear_r2": float(lin_a.rsquared),
                "linear_aic": float(lin_a.aic),
                "spline_r2": float(spl_a.rsquared),
                "spline_aic": float(spl_a.aic),
                "delta_aic_spline_minus_linear": float(spl_a.aic - lin_a.aic),
                "spline_vs_linear_F": float(f_a),
                "spline_vs_linear_p": float(p_a),
            }
        )

        ks = np.quantile(sub_a["posterior_exponent"].to_numpy(), np.linspace(0.20, 0.80, 41))
        best = None
        for k in np.unique(np.round(ks, 6)):
            tmp = sub_a.copy()
            tmp["hinge"] = np.maximum(tmp["posterior_exponent"] - k, 0.0)
            m = smf.ols(
                "ADOS_total ~ posterior_exponent + hinge + age_months + C(sex) + IQ_total + usable_epochs",
                data=tmp,
            ).fit()
            if best is None or m.aic < best[0]:
                best = (m.aic, float(k), m)
        assert best is not None
        _, knot_a, pw_a = best
        results.append(
            {
                "model_set": "adjusted_threshold",
                "n": int(len(sub_a)),
                "best_knot_posterior_exponent": float(knot_a),
                "piecewise_aic": float(pw_a.aic),
                "piecewise_r2": float(pw_a.rsquared),
                "delta_aic_piecewise_minus_linear": float(pw_a.aic - lin_a.aic),
                "slope_before_knot": float(pw_a.params.get("posterior_exponent", np.nan)),
                "slope_change_after_knot": float(pw_a.params.get("hinge", np.nan)),
                "slope_after_knot": float(
                    pw_a.params.get("posterior_exponent", np.nan)
                    + pw_a.params.get("hinge", np.nan)
                ),
                "hinge_pvalue": float(pw_a.pvalues.get("hinge", np.nan)),
            }
        )

    return results


def main() -> None:
    log = setup_logging(load_config(), name="ados_posterior_nonlinear")
    config_map = {
        "main": PROJECT_ROOT / "config" / "config.yaml",
        "matched": PROJECT_ROOT / "config" / "config_resting_matched.yaml",
    }
    postqc_cfg = PROJECT_ROOT / "config" / "config_resting_matched_postqc.yaml"
    if postqc_cfg.exists():
        config_map["matched_postqc"] = postqc_cfg

    for cohort, cfg_path in config_map.items():
        df, out_root = build_asd_dataset(cfg_path)
        rows = fit_nonlinear_models(df)
        if not rows:
            log.warning("cohort=%s 无法拟合（样本不足或变量缺失）", cohort)
            continue

        out_df = pd.DataFrame(rows)
        out_df.insert(0, "cohort", cohort)
        out_path = out_root / "tables" / "ados_posterior_nonlinear_spline_threshold.csv"
        save_csv(out_df, out_path)
        log.info("cohort=%s 输出: %s", cohort, out_path)


if __name__ == "__main__":
    main()
