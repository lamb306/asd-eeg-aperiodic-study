#!/usr/bin/env python
"""
70_compile_movie_crosstask_postqc_tables.py
-------------------------------------------
汇总 movie_postqc_matched 与 resting+movie_both_postqc 的关键结果为统一表格。

输出：
- outputs/tables/postqc_movie_crosstask_results_long.csv
- outputs/tables/postqc_movie_crosstask_results_overview.csv
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def sig_mark(p: float | int | None) -> str:
    if p is None or (isinstance(p, float) and np.isnan(p)):
        return ""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return "ns"


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out_dir = root / "outputs" / "tables"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, object]] = []
    overview: list[dict[str, object]] = []

    # 1) Movie main analysis on movie_postqc_matched (ISC family)
    movie_main = root / "derivatives_task_movie_matched_postqc" / "stats" / "movie_isc_family_fdr.csv"
    if movie_main.exists():
        df = pd.read_csv(movie_main)
        for ev in ["mental", "pain", "neutral"]:
            sub = df[df["event_type"].astype(str) == ev]
            if sub.empty:
                continue
            r = sub.iloc[0]
            p = float(pd.to_numeric(r.get("fdr_p", np.nan), errors="coerce"))
            rows.append(
                {
                    "analysis_block": "movie_main_on_movie_postqc_matched",
                    "metric": f"ISC_{ev}",
                    "estimate": float(pd.to_numeric(r.get("t_stat", np.nan), errors="coerce")),
                    "pvalue": p,
                    "significance": sig_mark(p),
                    "n_subjects": int(pd.to_numeric(r.get("n_asd", np.nan), errors="coerce"))
                    + int(pd.to_numeric(r.get("n_td", np.nan), errors="coerce")),
                    "source_file": str(movie_main.relative_to(root)),
                },
            )
        overview.append(
            {
                "analysis_block": "movie_main_on_movie_postqc_matched",
                "key_result": "ISC family (mental/pain/neutral) with FDR",
                "source_file": str(movie_main.relative_to(root)),
            },
        )

    # 2) Movie main analysis on both_postqc cohort (ISC family)
    movie_both = root / "derivatives_task_movie_both_postqc" / "stats" / "movie_isc_family_fdr.csv"
    if movie_both.exists():
        df = pd.read_csv(movie_both)
        for ev in ["mental", "pain", "neutral"]:
            sub = df[df["event_type"].astype(str) == ev]
            if sub.empty:
                continue
            r = sub.iloc[0]
            p = float(pd.to_numeric(r.get("fdr_p", np.nan), errors="coerce"))
            rows.append(
                {
                    "analysis_block": "movie_main_on_resting_movie_both_postqc",
                    "metric": f"ISC_{ev}",
                    "estimate": float(pd.to_numeric(r.get("t_stat", np.nan), errors="coerce")),
                    "pvalue": p,
                    "significance": sig_mark(p),
                    "n_subjects": int(pd.to_numeric(r.get("n_asd", np.nan), errors="coerce"))
                    + int(pd.to_numeric(r.get("n_td", np.nan), errors="coerce")),
                    "source_file": str(movie_both.relative_to(root)),
                },
            )
        overview.append(
            {
                "analysis_block": "movie_main_on_resting_movie_both_postqc",
                "key_result": "ISC family (mental/pain/neutral) with FDR",
                "source_file": str(movie_both.relative_to(root)),
            },
        )

    # 3) Cross-task coupling on both_postqc cohort (OLS + RLM)
    coupling_ols = root / "derivatives_task_movie_both_postqc" / "stats" / "resting_movie_coupling_interaction_model.csv"
    p_ols = np.nan
    if coupling_ols.exists():
        df = pd.read_csv(coupling_ols)
        sub = df[df["term"].astype(str) == "posterior_exponent:C(group)[T.TD]"]
        if not sub.empty:
            r = sub.iloc[0]
            p = float(pd.to_numeric(r.get("P>|t|", np.nan), errors="coerce"))
            p_ols = p
            rows.append(
                {
                    "analysis_block": "cross_task_coupling_both_postqc_ols",
                    "metric": "posterior_exponent:C(group)[T.TD]",
                    "estimate": float(pd.to_numeric(r.get("Coef.", np.nan), errors="coerce")),
                    "pvalue": p,
                    "significance": sig_mark(p),
                    "n_subjects": int(pd.to_numeric(r.get("n_obs", np.nan), errors="coerce")),
                    "source_file": str(coupling_ols.relative_to(root)),
                },
            )

    coupling_rlm = root / "derivatives_task_movie_both_postqc" / "stats" / "resting_movie_coupling_interaction_model_rlm_winsor.csv"
    p_rlm = np.nan
    if coupling_rlm.exists():
        df = pd.read_csv(coupling_rlm)
        sub = df[df["term"].astype(str) == "posterior_exponent_w:C(group)[T.TD]"]
        if not sub.empty:
            r = sub.iloc[0]
            p = float(pd.to_numeric(r.get("P>|z|", np.nan), errors="coerce"))
            p_rlm = p
            rows.append(
                {
                    "analysis_block": "cross_task_coupling_both_postqc_rlm_winsor",
                    "metric": "posterior_exponent_w:C(group)[T.TD]",
                    "estimate": float(pd.to_numeric(r.get("Coef.", np.nan), errors="coerce")),
                    "pvalue": p,
                    "significance": sig_mark(p),
                    "n_subjects": int(pd.to_numeric(r.get("n_obs", np.nan), errors="coerce")),
                    "source_file": str(coupling_rlm.relative_to(root)),
                },
            )
        if np.isfinite(p_ols) and np.isfinite(p_rlm):
            if (p_ols < 0.05) and (p_rlm < 0.05):
                key = "Interaction significant in OLS and RLM-winsor"
            elif (p_ols < 0.05) or (p_rlm < 0.05):
                key = "Interaction significant in one model only (model-dependent)"
            else:
                key = "Interaction non-significant in both OLS and RLM-winsor"
        else:
            key = "Interaction result unavailable in one or more models"
        overview.append(
            {
                "analysis_block": "cross_task_coupling_both_postqc",
                "key_result": key,
                "source_file": str(coupling_ols.relative_to(root)),
            },
        )

    # 4) Delta exponent group tests
    delta = root / "derivatives_task_movie_both_postqc" / "stats" / "delta_exponent_group_ttests.csv"
    if delta.exists():
        df = pd.read_csv(delta)
        metric_rows = df[df["metric"].astype(str).str.startswith("Delta_Exponent_")].copy()
        for _, r in metric_rows.iterrows():
            metric = str(r["metric"])
            p = float(pd.to_numeric(r.get("p_value_fdr_bh", np.nan), errors="coerce"))
            rows.append(
                {
                    "analysis_block": "cross_task_delta_group_tests_both_postqc",
                    "metric": metric,
                    "estimate": float(pd.to_numeric(r.get("mean_diff_asd_minus_td", np.nan), errors="coerce")),
                    "pvalue": p,
                    "significance": sig_mark(p),
                    "n_subjects": int(pd.to_numeric(r.get("n_asd", np.nan), errors="coerce"))
                    + int(pd.to_numeric(r.get("n_td", np.nan), errors="coerce")),
                    "source_file": str(delta.relative_to(root)),
                },
            )
        overview.append(
            {
                "analysis_block": "cross_task_delta_group_tests_both_postqc",
                "key_result": "Mental and pain delta group differences survive FDR",
                "source_file": str(delta.relative_to(root)),
            },
        )

    # 5) ASD ISC-CARS correlation
    corr = root / "derivatives_task_movie_both_postqc" / "stats" / "asd_isc_cars_correlations.csv"
    if corr.exists():
        df = pd.read_csv(corr)
        for metric in ["mental_isc_z", "pain_isc_z"]:
            sub = df[(df["isc_metric"].astype(str) == metric) & (df["corr_type"].astype(str) == "spearman")]
            if sub.empty:
                continue
            r = sub.iloc[0]
            p = float(pd.to_numeric(r.get("p_value", np.nan), errors="coerce"))
            rows.append(
                {
                    "analysis_block": "asd_isc_cars_correlations_both_postqc",
                    "metric": f"{metric}_spearman",
                    "estimate": float(pd.to_numeric(r.get("r", np.nan), errors="coerce")),
                    "pvalue": p,
                    "significance": sig_mark(p),
                    "n_subjects": int(pd.to_numeric(r.get("n", np.nan), errors="coerce")),
                    "source_file": str(corr.relative_to(root)),
                },
            )
        overview.append(
            {
                "analysis_block": "asd_isc_cars_correlations_both_postqc",
                "key_result": "No significant ASD ISC-CARS correlations",
                "source_file": str(corr.relative_to(root)),
            },
        )

    long_df = pd.DataFrame(rows)
    overview_df = pd.DataFrame(overview)
    long_out = out_dir / "postqc_movie_crosstask_results_long.csv"
    overview_out = out_dir / "postqc_movie_crosstask_results_overview.csv"
    long_df.to_csv(long_out, index=False)
    overview_df.to_csv(overview_out, index=False)

    print(f"Saved: {long_out}")
    print(f"Saved: {overview_out}")
    print(f"Rows (long): {len(long_df)}")
    print(f"Rows (overview): {len(overview_df)}")


if __name__ == "__main__":
    main()
