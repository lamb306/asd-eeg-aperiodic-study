#!/usr/bin/env python
"""
63_latent_class_posterior_ados.py
---------------------------------
按 posterior_exponent 在 ASD 组做三分层（low/medium/high），比较 ADOS_total。

输出：
- outputs/tables/ados_posterior_latent_class_tests.csv
- outputs/tables/ados_posterior_latent_class_membership.csv
- outputs_matched_resting/tables/ados_posterior_latent_class_tests.csv
- outputs_matched_resting/tables/ados_posterior_latent_class_membership.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import kruskal, spearmanr
from statsmodels.stats.anova import anova_lm

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
        df["posterior_exponent"] = df[required].mean(axis=1)
    return df, out_root


def assign_three_classes(sub: pd.DataFrame) -> tuple[pd.DataFrame, float, float]:
    """按 posterior_exponent 三分位切 low / medium / high。"""
    q1 = float(sub["posterior_exponent"].quantile(1 / 3))
    q2 = float(sub["posterior_exponent"].quantile(2 / 3))

    # 用阈值规则而非 qcut，确保标签始终是 low/medium/high。
    cls = np.where(
        sub["posterior_exponent"] <= q1,
        "low",
        np.where(sub["posterior_exponent"] <= q2, "medium", "high"),
    )
    out = sub.copy()
    out["latent_class"] = pd.Categorical(cls, categories=["low", "medium", "high"], ordered=True)
    out["latent_class_code"] = out["latent_class"].cat.codes + 1
    return out, q1, q2


def run_class_tests(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    sub = df.dropna(subset=["ADOS_total", "posterior_exponent"]).copy()
    if len(sub) < 15 or sub["posterior_exponent"].nunique() < 9:
        raise ValueError("样本过少或 posterior_exponent 离散度不足，无法稳定三分层。")

    sub, q1, q2 = assign_three_classes(sub)

    # 组间检验
    m = smf.ols("ADOS_total ~ C(latent_class)", data=sub).fit()
    anova_tbl = anova_lm(m, typ=2)
    anova_p = float(anova_tbl.loc["C(latent_class)", "PR(>F)"])

    groups = [g["ADOS_total"].to_numpy() for _, g in sub.groupby("latent_class", observed=True)]
    kruskal_p = float(kruskal(*groups).pvalue)

    # 有序趋势：low<medium<high 与 ADOS 的 Spearman
    rho, rho_p = spearmanr(sub["latent_class_code"], sub["ADOS_total"])

    # adjusted（敏感性）
    cov_cols = ["age_months", "sex", "IQ_total", "usable_epochs"]
    adj_sub = sub.dropna(subset=["ADOS_total", "latent_class", *cov_cols]).copy()
    adj_p = np.nan
    if len(adj_sub) >= 20:
        m_adj = smf.ols(
            "ADOS_total ~ C(latent_class) + age_months + C(sex) + IQ_total + usable_epochs",
            data=adj_sub,
        ).fit()
        adj_tbl = anova_lm(m_adj, typ=2)
        adj_p = float(adj_tbl.loc["C(latent_class)", "PR(>F)"])

    desc = (
        sub.groupby("latent_class", observed=True)["ADOS_total"]
        .agg(["count", "mean", "median", "std"])
        .reset_index()
    )

    summary = pd.DataFrame(
        [
            {
                "n_asd_with_ados_posterior": int(len(sub)),
                "q1_posterior_exponent": q1,
                "q2_posterior_exponent": q2,
                "class_definition": f"low<=q1({q1:.6f}), medium(q1,q2], high>q2({q2:.6f})",
                "n_low": int((sub["latent_class"] == "low").sum()),
                "n_medium": int((sub["latent_class"] == "medium").sum()),
                "n_high": int((sub["latent_class"] == "high").sum()),
                "ados_mean_low": float(
                    desc.loc[desc["latent_class"] == "low", "mean"].iloc[0]
                ),
                "ados_mean_medium": float(
                    desc.loc[desc["latent_class"] == "medium", "mean"].iloc[0]
                ),
                "ados_mean_high": float(
                    desc.loc[desc["latent_class"] == "high", "mean"].iloc[0]
                ),
                "anova_p_ados_by_class": anova_p,
                "kruskal_p_ados_by_class": kruskal_p,
                "spearman_rho_class_order_vs_ados": float(rho),
                "spearman_p_class_order_vs_ados": float(rho_p),
                "adjusted_anova_p_ados_by_class": float(adj_p) if not np.isnan(adj_p) else np.nan,
            },
        ]
    )

    membership = sub[
        ["subject_id", "group", "posterior_exponent", "ADOS_total", "latent_class", "latent_class_code"]
    ].sort_values(["latent_class_code", "posterior_exponent", "subject_id"])
    return summary, membership


def main() -> None:
    log = setup_logging(load_config(), name="ados_posterior_latent_class")
    config_map = {
        "main": PROJECT_ROOT / "config" / "config.yaml",
        "matched": PROJECT_ROOT / "config" / "config_resting_matched.yaml",
    }
    postqc_cfg = PROJECT_ROOT / "config" / "config_resting_matched_postqc.yaml"
    if postqc_cfg.exists():
        config_map["matched_postqc"] = postqc_cfg

    for cohort, cfg_path in config_map.items():
        try:
            df, out_root = build_asd_dataset(cfg_path)
            summary, membership = run_class_tests(df)
        except Exception as exc:
            log.warning("cohort=%s 失败: %s", cohort, exc)
            continue

        summary.insert(0, "cohort", cohort)
        membership.insert(0, "cohort", cohort)
        out_tests = out_root / "tables" / "ados_posterior_latent_class_tests.csv"
        out_membership = out_root / "tables" / "ados_posterior_latent_class_membership.csv"
        save_csv(summary, out_tests)
        save_csv(membership, out_membership)
        log.info("cohort=%s 输出: %s ; %s", cohort, out_tests, out_membership)


if __name__ == "__main__":
    main()
