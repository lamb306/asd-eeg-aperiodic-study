#!/usr/bin/env python
"""
37_delta_exponent_and_isc_cars.py
---------------------------------
补充分析：
1) Delta Exponent（movie mental/pain - resting posterior_exponent）组间 Welch t 检验
2) ASD 组中 ISC（mental/pain）与 CARS_total 的 Pearson / Spearman 相关
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr, ttest_ind
from statsmodels.stats.multitest import multipletests


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Delta exponent + ISC-CARS supplemental analyses")
    parser.add_argument(
        "--project_root",
        type=str,
        default=".",
        help="项目根目录",
    )
    parser.add_argument(
        "--resting_csv",
        type=str,
        default="outputs/tables/resting_features_locked.csv",
        help="静息态特征文件（含 posterior_exponent）",
    )
    parser.add_argument(
        "--movie_exponent_csv",
        type=str,
        default="derivatives_task_movie/stats/movie_event_subject_condition_means.csv",
        help="电影事件条件均值（含 mental/pain exponent）",
    )
    parser.add_argument(
        "--movie_isc_csv",
        type=str,
        default="derivatives_task_movie/stats/movie_isc_subject_values.csv",
        help="电影 ISC 被试值",
    )
    parser.add_argument(
        "--participants_csv",
        type=str,
        default="data/participants/participants_task_movie.csv",
        help="movie 被试信息（用于 included_final 与样本口径）",
    )
    parser.add_argument(
        "--clinical_participants_csv",
        type=str,
        default="data/participants/participants.csv",
        help="临床被试信息（用于 CARS_total）",
    )
    parser.add_argument(
        "--movie_analysis_csv",
        type=str,
        default="derivatives_task_movie/participants_analysis.csv",
        help="movie 分析队列 CSV（统一样本口径）",
    )
    parser.add_argument(
        "--movie_specparam_qc_csv",
        type=str,
        default="derivatives_task_movie/specparam/specparam_qc_summary_subject.csv",
        help="movie 被试级 specparam QC（剔除 low_quality_subject）",
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        default="derivatives_task_movie/stats",
        help="输出目录",
    )
    return parser.parse_args()


def cohen_d_independent(x: np.ndarray, y: np.ndarray) -> float:
    nx = len(x)
    ny = len(y)
    if nx < 2 or ny < 2:
        return np.nan
    vx = np.var(x, ddof=1)
    vy = np.var(y, ddof=1)
    pooled = ((nx - 1) * vx + (ny - 1) * vy) / (nx + ny - 2)
    if pooled <= 0:
        return np.nan
    return float((np.mean(x) - np.mean(y)) / np.sqrt(pooled))


def safe_pearson(x: pd.Series, y: pd.Series) -> tuple[float, float, int]:
    tmp = pd.DataFrame({"x": x, "y": y}).dropna()
    n = len(tmp)
    if n < 3:
        return np.nan, np.nan, n
    if tmp["x"].std() < 1e-12 or tmp["y"].std() < 1e-12:
        return np.nan, np.nan, n
    r, p = pearsonr(tmp["x"], tmp["y"])
    return float(r), float(p), n


def safe_spearman(x: pd.Series, y: pd.Series) -> tuple[float, float, int]:
    tmp = pd.DataFrame({"x": x, "y": y}).dropna()
    n = len(tmp)
    if n < 3:
        return np.nan, np.nan, n
    r, p = spearmanr(tmp["x"], tmp["y"])
    return float(r), float(p), n


def main() -> None:
    args = parse_args()
    root = Path(args.project_root).resolve()
    resting_path = root / args.resting_csv
    movie_exp_path = root / args.movie_exponent_csv
    movie_isc_path = root / args.movie_isc_csv
    participants_path = root / args.participants_csv
    clinical_participants_path = root / args.clinical_participants_csv
    movie_analysis_path = root / args.movie_analysis_csv
    movie_qc_path = root / args.movie_specparam_qc_csv
    out_dir = root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    rest = pd.read_csv(resting_path)
    rest = rest[["subject_id", "group", "posterior_exponent"]].copy()
    rest = rest.rename(columns={"posterior_exponent": "resting_posterior_exponent"})
    rest["subject_id"] = rest["subject_id"].astype(str)
    rest["group"] = rest["group"].astype(str).str.upper()
    rest["resting_posterior_exponent"] = pd.to_numeric(rest["resting_posterior_exponent"], errors="coerce")

    movie_exp = pd.read_csv(movie_exp_path)
    movie_exp = movie_exp[
        movie_exp["event_type"].astype(str).str.lower().isin(["mental", "pain", "neutral"])
    ].copy()
    movie_exp["subject_id"] = movie_exp["subject_id"].astype(str)
    movie_exp["group"] = movie_exp["group"].astype(str).str.upper()
    movie_exp["exponent"] = pd.to_numeric(movie_exp["exponent"], errors="coerce")
    exp_wide = movie_exp.pivot_table(
        index=["subject_id", "group"],
        columns="event_type",
        values="exponent",
        aggfunc="mean",
    ).reset_index()
    exp_wide.columns.name = None
    exp_wide = exp_wide.rename(
        columns={
            "mental": "movie_mental_exponent",
            "pain": "movie_pain_exponent",
            "neutral": "movie_neutral_exponent",
        },
    )

    movie_part = pd.read_csv(participants_path)
    movie_part = movie_part[["subject_id", "group"] + ([ "included_final"] if "included_final" in movie_part.columns else [])].copy()
    movie_part["subject_id"] = movie_part["subject_id"].astype(str)
    movie_part["group"] = movie_part["group"].astype(str).str.upper()
    if "included_final" in movie_part.columns:
        movie_part["included_final"] = pd.to_numeric(movie_part["included_final"], errors="coerce")
        movie_part = movie_part[movie_part["included_final"] == 1].copy()
    allowed_pairs = movie_part[["subject_id", "group"]].drop_duplicates()

    if movie_analysis_path.exists():
        movie_analysis = pd.read_csv(movie_analysis_path)
        movie_analysis = movie_analysis[["subject_id", "group"]].copy()
        movie_analysis["subject_id"] = movie_analysis["subject_id"].astype(str)
        movie_analysis["group"] = movie_analysis["group"].astype(str).str.upper()
        allowed_pairs = allowed_pairs.merge(movie_analysis.drop_duplicates(), on=["subject_id", "group"], how="inner")

    if movie_qc_path.exists():
        movie_qc = pd.read_csv(movie_qc_path)
        movie_qc["subject_id"] = movie_qc["subject_id"].astype(str)
        bad_ids = set(
            movie_qc.loc[pd.to_numeric(movie_qc["low_quality_subject"], errors="coerce") == 1, "subject_id"].tolist()
        )
        if bad_ids:
            allowed_pairs = allowed_pairs[~allowed_pairs["subject_id"].isin(bad_ids)].copy()

    delta_df = exp_wide.merge(rest, on=["subject_id", "group"], how="inner")
    delta_df = delta_df.merge(allowed_pairs, on=["subject_id", "group"], how="inner")
    delta_df["Delta_Exponent_mental"] = delta_df["movie_mental_exponent"] - delta_df["resting_posterior_exponent"]
    delta_df["Delta_Exponent_pain"] = delta_df["movie_pain_exponent"] - delta_df["resting_posterior_exponent"]
    if "movie_neutral_exponent" in delta_df.columns:
        delta_df["Delta_Exponent_neutral"] = (
            delta_df["movie_neutral_exponent"] - delta_df["resting_posterior_exponent"]
        )

    t_rows: list[dict[str, float | int | str]] = []
    metric_list = ["Delta_Exponent_mental", "Delta_Exponent_pain"]
    if "Delta_Exponent_neutral" in delta_df.columns:
        metric_list.append("Delta_Exponent_neutral")
    for metric in metric_list:
        asd = delta_df.loc[delta_df["group"] == "ASD", metric].dropna().to_numpy(dtype=float)
        td = delta_df.loc[delta_df["group"] == "TD", metric].dropna().to_numpy(dtype=float)
        if len(asd) >= 2 and len(td) >= 2:
            res = ttest_ind(asd, td, equal_var=False, nan_policy="omit")
            t_stat = float(res.statistic)
            p_val = float(res.pvalue)
        else:
            t_stat = np.nan
            p_val = np.nan
        t_rows.append(
            {
                "metric": metric,
                "n_asd": int(len(asd)),
                "n_td": int(len(td)),
                "asd_mean": float(np.mean(asd)) if len(asd) else np.nan,
                "asd_sd": float(np.std(asd, ddof=1)) if len(asd) > 1 else np.nan,
                "td_mean": float(np.mean(td)) if len(td) else np.nan,
                "td_sd": float(np.std(td, ddof=1)) if len(td) > 1 else np.nan,
                "mean_diff_asd_minus_td": float(np.mean(asd) - np.mean(td)) if len(asd) and len(td) else np.nan,
                "cohen_d": cohen_d_independent(asd, td),
                "t_stat_welch": t_stat,
                "p_value_welch": p_val,
            }
        )
    ttest_df = pd.DataFrame(t_rows)
    if not ttest_df.empty:
        raw_p = pd.to_numeric(ttest_df["p_value_welch"], errors="coerce").to_numpy(dtype=float)
        valid = np.isfinite(raw_p)
        fdr_p = np.full_like(raw_p, np.nan, dtype=float)
        fdr_sig = np.full_like(raw_p, False, dtype=bool)
        if valid.sum() > 0:
            rej, p_adj, *_ = multipletests(raw_p[valid], alpha=0.05, method="fdr_bh")
            fdr_p[valid] = p_adj
            fdr_sig[valid] = rej
        ttest_df["p_value_fdr_bh"] = fdr_p
        ttest_df["significant_fdr_bh"] = fdr_sig

    isc = pd.read_csv(movie_isc_path)
    isc = isc[isc["event_type"].astype(str).str.lower().isin(["mental", "pain"])].copy()
    isc["subject_id"] = isc["subject_id"].astype(str)
    isc["group"] = isc["group"].astype(str).str.upper()
    isc["isc_z"] = pd.to_numeric(isc["isc_z"], errors="coerce")
    isc_wide = isc.pivot_table(
        index=["subject_id", "group"],
        columns="event_type",
        values="isc_z",
        aggfunc="mean",
    ).reset_index()
    isc_wide.columns.name = None
    isc_wide = isc_wide.rename(columns={"mental": "mental_isc_z", "pain": "pain_isc_z"})

    part = pd.read_csv(clinical_participants_path)
    part = part[["subject_id", "group", "CARS_total"]].copy()
    part["subject_id"] = part["subject_id"].astype(str)
    part["group"] = part["group"].astype(str).str.upper()
    part["CARS_total"] = pd.to_numeric(part["CARS_total"], errors="coerce")

    asd_corr_df = isc_wide.merge(part, on=["subject_id", "group"], how="left")
    asd_corr_df = asd_corr_df[asd_corr_df["group"] == "ASD"].copy()
    asd_corr_df = asd_corr_df.merge(
        allowed_pairs[allowed_pairs["group"] == "ASD"][["subject_id", "group"]],
        on=["subject_id", "group"],
        how="inner",
    )
    # 与 Delta 指标保持同一 ASD 样本（当前为 n=62）
    asd_ref_ids = set(delta_df.loc[delta_df["group"] == "ASD", "subject_id"].astype(str))
    asd_corr_df = asd_corr_df[asd_corr_df["subject_id"].astype(str).isin(asd_ref_ids)].copy()

    corr_rows = []
    for metric in ["mental_isc_z", "pain_isc_z"]:
        r_p, p_p, n_p = safe_pearson(asd_corr_df[metric], asd_corr_df["CARS_total"])
        r_s, p_s, n_s = safe_spearman(asd_corr_df[metric], asd_corr_df["CARS_total"])
        corr_rows.append(
            {
                "group": "ASD",
                "isc_metric": metric,
                "corr_type": "pearson",
                "n": int(n_p),
                "r": r_p,
                "p_value": p_p,
            }
        )
        corr_rows.append(
            {
                "group": "ASD",
                "isc_metric": metric,
                "corr_type": "spearman",
                "n": int(n_s),
                "r": r_s,
                "p_value": p_s,
            }
        )
    corr_df = pd.DataFrame(corr_rows)

    delta_df.to_csv(out_dir / "delta_exponent_subject_values.csv", index=False)
    ttest_df.to_csv(out_dir / "delta_exponent_group_ttests.csv", index=False)
    asd_corr_df.to_csv(out_dir / "asd_isc_cars_subject_values.csv", index=False)
    corr_df.to_csv(out_dir / "asd_isc_cars_correlations.csv", index=False)

    print(f"Saved: {out_dir / 'delta_exponent_subject_values.csv'}")
    print(f"Saved: {out_dir / 'delta_exponent_group_ttests.csv'}")
    print(f"Saved: {out_dir / 'asd_isc_cars_subject_values.csv'}")
    print(f"Saved: {out_dir / 'asd_isc_cars_correlations.csv'}")


if __name__ == "__main__":
    main()
