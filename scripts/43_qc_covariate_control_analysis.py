#!/usr/bin/env python
"""
43_qc_covariate_control_analysis.py
-----------------------------------
第三条道路：在宽松样本上加入 QC 协变量控制。

输出：
1) outputs/tables/qc_covariate_control_models.csv
2) outputs/tables/qc_covariate_control_event_fdr.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import spearmanr
from statsmodels.stats.multitest import multipletests


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="QC covariate control on relaxed cohorts")
    parser.add_argument("--project_root", type=str, default=".", help="项目根目录")
    parser.add_argument(
        "--resting_features_csv",
        type=str,
        default="outputs/tables/resting_features_locked.csv",
        help="resting 特征表（当前为宽松版）",
    )
    parser.add_argument(
        "--participants_csv",
        type=str,
        default="data/participants/participants.csv",
        help="resting participants 表（含 CARS）",
    )
    parser.add_argument(
        "--resting_qc_csv",
        type=str,
        default="derivatives/specparam/specparam_qc_summary_subject.csv",
        help="resting specparam 被试级 QC 表",
    )
    parser.add_argument(
        "--resting_preproc_csv",
        type=str,
        default="derivatives/qc/preproc_summary.csv",
        help="resting 预处理汇总表",
    )
    parser.add_argument(
        "--movie_isc_csv",
        type=str,
        default="derivatives_task_movie/stats/movie_isc_subject_values_with_neutral.csv",
        help="movie ISC 被试值（含 neutral）",
    )
    parser.add_argument(
        "--movie_participants_csv",
        type=str,
        default="data/participants/participants_task_movie.csv",
        help="movie participants 表",
    )
    parser.add_argument(
        "--movie_qc_csv",
        type=str,
        default="derivatives_task_movie/specparam/specparam_qc_summary_subject.csv",
        help="movie specparam 被试级 QC 表",
    )
    parser.add_argument(
        "--movie_preproc_csv",
        type=str,
        default="derivatives_task_movie/qc/preproc_summary.csv",
        help="movie 预处理汇总表",
    )
    parser.add_argument(
        "--out_models_csv",
        type=str,
        default="outputs/tables/qc_covariate_control_models.csv",
        help="模型结果输出 CSV",
    )
    parser.add_argument(
        "--out_fdr_csv",
        type=str,
        default="outputs/tables/qc_covariate_control_event_fdr.csv",
        help="event-level FDR 输出 CSV",
    )
    return parser.parse_args()


def _fit_ols(formula: str, data: pd.DataFrame):
    return smf.ols(formula=formula, data=data).fit()


def _extract_term_row(model, term: str, model_name: str, analysis: str, n_obs: int) -> dict[str, float | str]:
    params = model.params
    pvals = model.pvalues
    bse = model.bse
    return {
        "analysis": analysis,
        "model_name": model_name,
        "term": term,
        "coef": float(params.get(term, np.nan)),
        "std_err": float(bse.get(term, np.nan)),
        "p_value": float(pvals.get(term, np.nan)),
        "n_obs": int(n_obs),
        "r_squared": float(getattr(model, "rsquared", np.nan)),
        "formula": model.model.formula,
    }


def main() -> None:
    args = parse_args()
    root = Path(args.project_root).resolve()

    # -----------------------------
    # Resting: posterior -> CARS
    # -----------------------------
    resting = pd.read_csv(root / args.resting_features_csv)
    part = pd.read_csv(root / args.participants_csv)
    rq = pd.read_csv(root / args.resting_qc_csv)
    rp = pd.read_csv(root / args.resting_preproc_csv)

    resting["subject_id"] = resting["subject_id"].astype(str)
    resting["group"] = resting["group"].astype(str).str.upper()
    part["subject_id"] = part["subject_id"].astype(str)
    part["group"] = part["group"].astype(str).str.upper()
    part["included_final"] = pd.to_numeric(part.get("included_final", np.nan), errors="coerce")
    part["CARS_total"] = pd.to_numeric(part.get("CARS_total", np.nan), errors="coerce")
    part["age_months"] = pd.to_numeric(part.get("age_months", np.nan), errors="coerce")
    part["sex"] = part.get("sex", np.nan)

    rq["subject_id"] = rq["subject_id"].astype(str)
    rp["subject_id"] = rp["subject_id"].astype(str)
    rp["usable_epochs"] = pd.to_numeric(rp.get("usable_epochs", np.nan), errors="coerce")

    rest_df = (
        resting.merge(
            part[["subject_id", "group", "included_final", "CARS_total", "age_months", "sex"]],
            on=["subject_id", "group"],
            how="left",
        )
        .merge(
            rq[["subject_id", "mean_fit_error", "invalid_channel_ratio"]],
            on="subject_id",
            how="left",
        )
        .merge(rp[["subject_id", "usable_epochs"]], on="subject_id", how="left")
    )
    rest_df = rest_df[(rest_df["group"] == "ASD") & (rest_df["included_final"] == 1)].copy()
    rest_df["posterior_exponent"] = pd.to_numeric(rest_df["posterior_exponent"], errors="coerce")
    rest_df["mean_fit_error"] = pd.to_numeric(rest_df["mean_fit_error"], errors="coerce")
    rest_df["invalid_channel_ratio"] = pd.to_numeric(rest_df["invalid_channel_ratio"], errors="coerce")
    rest_df["usable_epochs"] = pd.to_numeric(rest_df["usable_epochs"], errors="coerce")

    models_rows: list[dict[str, float | str]] = []

    # 原始 Spearman（对照）
    spearman_df = rest_df.dropna(subset=["posterior_exponent", "CARS_total"])
    if len(spearman_df) >= 3:
        rho, p = spearmanr(spearman_df["posterior_exponent"], spearman_df["CARS_total"])
    else:
        rho, p = np.nan, np.nan
    models_rows.append(
        {
            "analysis": "posterior_cars",
            "model_name": "spearman_raw",
            "term": "posterior_exponent",
            "coef": float(rho) if pd.notna(rho) else np.nan,
            "std_err": np.nan,
            "p_value": float(p) if pd.notna(p) else np.nan,
            "n_obs": int(len(spearman_df)),
            "r_squared": np.nan,
            "formula": "Spearman(CARS_total, posterior_exponent)",
        }
    )

    # 基础回归（无 QC）
    base_df = rest_df.dropna(subset=["CARS_total", "posterior_exponent", "age_months", "sex"]).copy()
    if len(base_df) >= 20:
        m_base = _fit_ols("CARS_total ~ posterior_exponent + age_months + C(sex)", base_df)
        models_rows.append(
            _extract_term_row(
                m_base, "posterior_exponent", "ols_base", "posterior_cars", int(m_base.nobs)
            )
        )

    # QC 协变量控制回归
    qc_df = rest_df.dropna(
        subset=[
            "CARS_total",
            "posterior_exponent",
            "age_months",
            "sex",
            "mean_fit_error",
            "invalid_channel_ratio",
            "usable_epochs",
        ]
    ).copy()
    if len(qc_df) >= 20:
        m_qc = _fit_ols(
            "CARS_total ~ posterior_exponent + age_months + C(sex) + mean_fit_error + invalid_channel_ratio + usable_epochs",
            qc_df,
        )
        models_rows.append(
            _extract_term_row(
                m_qc, "posterior_exponent", "ols_qc_adjusted", "posterior_cars", int(m_qc.nobs)
            )
        )

    # -----------------------------
    # Movie: ISC group effect with/without QC covariates
    # -----------------------------
    isc = pd.read_csv(root / args.movie_isc_csv)
    mp = pd.read_csv(root / args.movie_participants_csv)
    mq = pd.read_csv(root / args.movie_qc_csv)
    mpre = pd.read_csv(root / args.movie_preproc_csv)

    isc["subject_id"] = isc["subject_id"].astype(str)
    isc["group"] = isc["group"].astype(str).str.upper()
    isc["event_type"] = isc["event_type"].astype(str).str.lower()
    isc["isc_z"] = pd.to_numeric(isc["isc_z"], errors="coerce")

    mp["subject_id"] = mp["subject_id"].astype(str)
    mp["group"] = mp["group"].astype(str).str.upper()
    mp["age_months"] = pd.to_numeric(mp.get("age_months", np.nan), errors="coerce")
    mp["IQ_total"] = pd.to_numeric(mp.get("IQ_total", np.nan), errors="coerce")
    mp["sex"] = mp.get("sex", np.nan)
    mp["included_final"] = pd.to_numeric(mp.get("included_final", np.nan), errors="coerce")

    mq["subject_id"] = mq["subject_id"].astype(str)
    mpre["subject_id"] = mpre["subject_id"].astype(str)
    mpre["usable_epochs"] = pd.to_numeric(mpre.get("usable_epochs", np.nan), errors="coerce")

    movie_df = (
        isc.merge(
            mp[["subject_id", "group", "age_months", "IQ_total", "sex", "included_final"]],
            on=["subject_id", "group"],
            how="left",
        )
        .merge(
            mq[["subject_id", "mean_fit_error", "invalid_channel_ratio"]],
            on="subject_id",
            how="left",
        )
        .merge(mpre[["subject_id", "usable_epochs"]], on="subject_id", how="left")
    )
    movie_df = movie_df[movie_df["included_final"] == 1].copy()
    movie_df = movie_df[movie_df["event_type"].isin(["mental", "pain", "neutral"])].copy()

    fdr_rows = []
    for ev in ["mental", "pain", "neutral"]:
        sub = movie_df[movie_df["event_type"] == ev].copy()

        base_sub = sub.dropna(subset=["isc_z", "group", "age_months", "sex", "IQ_total", "usable_epochs"]).copy()
        if len(base_sub) >= 30 and base_sub["group"].nunique() == 2:
            m_base = _fit_ols("isc_z ~ C(group) + age_months + C(sex) + IQ_total + usable_epochs", base_sub)
            term = "C(group)[T.TD]"
            row = _extract_term_row(m_base, term, f"isc_base_{ev}", "isc_group", int(m_base.nobs))
            row["event_type"] = ev
            models_rows.append(row)

        qc_sub = sub.dropna(
            subset=[
                "isc_z",
                "group",
                "age_months",
                "sex",
                "IQ_total",
                "usable_epochs",
                "mean_fit_error",
                "invalid_channel_ratio",
            ]
        ).copy()
        if len(qc_sub) >= 30 and qc_sub["group"].nunique() == 2:
            m_qc = _fit_ols(
                "isc_z ~ C(group) + age_months + C(sex) + IQ_total + usable_epochs + mean_fit_error + invalid_channel_ratio",
                qc_sub,
            )
            term = "C(group)[T.TD]"
            row = _extract_term_row(m_qc, term, f"isc_qc_adjusted_{ev}", "isc_group", int(m_qc.nobs))
            row["event_type"] = ev
            models_rows.append(row)
            fdr_rows.append({"event_type": ev, "raw_p": row["p_value"], "n_obs": row["n_obs"]})

    models_out = pd.DataFrame(models_rows)

    fdr_df = pd.DataFrame(fdr_rows)
    if not fdr_df.empty:
        p = pd.to_numeric(fdr_df["raw_p"], errors="coerce").to_numpy(dtype=float)
        valid = np.isfinite(p)
        fdr_p = np.full_like(p, np.nan, dtype=float)
        sig = np.full_like(p, False, dtype=bool)
        if valid.sum() > 0:
            rej, p_adj, *_ = multipletests(p[valid], alpha=0.05, method="fdr_bh")
            fdr_p[valid] = p_adj
            sig[valid] = rej
        fdr_df["fdr_p"] = fdr_p
        fdr_df["significant_fdr"] = sig

    out_models = root / args.out_models_csv
    out_fdr = root / args.out_fdr_csv
    out_models.parent.mkdir(parents=True, exist_ok=True)
    out_fdr.parent.mkdir(parents=True, exist_ok=True)
    models_out.to_csv(out_models, index=False)
    fdr_df.to_csv(out_fdr, index=False)

    print(f"Saved: {out_models}")
    print(f"Saved: {out_fdr}")
    if not models_out.empty:
        print(models_out.to_string(index=False))
    if not fdr_df.empty:
        print("\nISC QC-adjusted event FDR:")
        print(fdr_df.to_string(index=False))


if __name__ == "__main__":
    main()

