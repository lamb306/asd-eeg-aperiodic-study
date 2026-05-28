#!/usr/bin/env python
"""
67_compile_postqc_analysis_tables.py
------------------------------------
汇总 postQC 重匹配后的关键分析结果，输出统一结果表。

输出：
- outputs_matched_resting_postqc/tables/postqc_analysis_results_long.csv
- outputs_matched_resting_postqc/tables/postqc_analysis_results_overview.csv
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def _sig_mark(p: float | int | None) -> str:
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
    tables_dir = root / "outputs_matched_resting_postqc" / "tables"
    stats_dir = root / "derivatives_matched_postqc" / "stats"
    tables_dir.mkdir(parents=True, exist_ok=True)

    long_rows: list[dict[str, object]] = []
    overview_rows: list[dict[str, object]] = []

    # 1) demographics
    demo_path = tables_dir / "table1_demographics_comparison.csv"
    if demo_path.exists():
        demo = pd.read_csv(demo_path)
        for var in ["age_months", "IQ_total", "language_score"]:
            sub = demo[demo["variable"] == var]
            if sub.empty:
                continue
            r = sub.iloc[0]
            p = pd.to_numeric(r.get("t_pvalue", np.nan), errors="coerce")
            long_rows.append(
                {
                    "analysis": "demographics_comparison",
                    "outcome": var,
                    "term": "ASD_vs_TD",
                    "estimate": pd.to_numeric(r.get("cohens_d", np.nan), errors="coerce"),
                    "pvalue": p,
                    "significance": _sig_mark(float(p)) if pd.notna(p) else "",
                    "n_asd": pd.to_numeric(r.get("n_a", np.nan), errors="coerce"),
                    "n_td": pd.to_numeric(r.get("n_b", np.nan), errors="coerce"),
                    "source_file": str(demo_path.relative_to(root)),
                },
            )
        overview_rows.append(
            {
                "analysis": "demographics_comparison",
                "key_result": "Age matched; IQ trend; language group difference",
                "source_file": str(demo_path.relative_to(root)),
            },
        )

    # 2) main group analysis
    main_path = stats_dir / "main_group_analysis.csv"
    if main_path.exists():
        main_df = pd.read_csv(main_path)
        for outcome in ["global_exponent", "global_offset"]:
            sub = main_df[(main_df["outcome"] == outcome) & (main_df["term"] == "C(group)[T.TD]")]
            if sub.empty:
                continue
            r = sub.iloc[0]
            p = pd.to_numeric(r.get("pvalue", np.nan), errors="coerce")
            long_rows.append(
                {
                    "analysis": "main_group_analysis",
                    "outcome": outcome,
                    "term": "C(group)[T.TD]",
                    "estimate": pd.to_numeric(r.get("coef", np.nan), errors="coerce"),
                    "pvalue": p,
                    "significance": _sig_mark(float(p)) if pd.notna(p) else "",
                    "n_asd": np.nan,
                    "n_td": np.nan,
                    "source_file": str(main_path.relative_to(root)),
                },
            )
        overview_rows.append(
            {
                "analysis": "main_group_analysis",
                "key_result": "Global exponent group effect significant",
                "source_file": str(main_path.relative_to(root)),
            },
        )

    # 3) ROI mixed model (group and interactions)
    roi_path = stats_dir / "roi_mixed_model.csv"
    if roi_path.exists():
        roi = pd.read_csv(roi_path)
        keep_terms = [
            "C(group)[T.TD]",
            "C(group)[T.TD]:C(roi)[T.frontal]",
            "C(group)[T.TD]:C(roi)[T.occipital]",
            "C(group)[T.TD]:C(roi)[T.parietal]",
            "C(group)[T.TD]:C(roi)[T.temporal]",
        ]
        sub = roi[(roi["outcome"] == "exponent") & (roi["term"].isin(keep_terms))].copy()
        for _, r in sub.iterrows():
            p = pd.to_numeric(r.get("pvalue", np.nan), errors="coerce")
            long_rows.append(
                {
                    "analysis": "roi_mixed_model",
                    "outcome": "exponent",
                    "term": r["term"],
                    "estimate": pd.to_numeric(r.get("coef", np.nan), errors="coerce"),
                    "pvalue": p,
                    "significance": _sig_mark(float(p)) if pd.notna(p) else "",
                    "n_asd": np.nan,
                    "n_td": np.nan,
                    "source_file": str(roi_path.relative_to(root)),
                },
            )
        overview_rows.append(
            {
                "analysis": "roi_mixed_model",
                "key_result": "Frontal/occipital group-by-ROI interactions significant",
                "source_file": str(roi_path.relative_to(root)),
            },
        )

    # 4) channel-level analysis summary
    ch_path = stats_dir / "channel_level_analysis.csv"
    if ch_path.exists():
        ch = pd.read_csv(ch_path)
        n_sig = int(pd.to_numeric(ch.get("significant_fdr"), errors="coerce").fillna(False).astype(bool).sum())
        min_fdr = pd.to_numeric(ch.get("pvalue_fdr"), errors="coerce").min()
        best = ch.loc[pd.to_numeric(ch["pvalue_fdr"], errors="coerce").idxmin()] if len(ch) else None
        long_rows.append(
            {
                "analysis": "channel_level_analysis",
                "outcome": "exponent",
                "term": "n_significant_channels_fdr",
                "estimate": n_sig,
                "pvalue": np.nan,
                "significance": "",
                "n_asd": np.nan,
                "n_td": np.nan,
                "source_file": str(ch_path.relative_to(root)),
            },
        )
        if best is not None:
            long_rows.append(
                {
                    "analysis": "channel_level_analysis",
                    "outcome": "exponent",
                    "term": f"best_channel_{best['channel']}",
                    "estimate": pd.to_numeric(best.get("coef", np.nan), errors="coerce"),
                    "pvalue": pd.to_numeric(best.get("pvalue_fdr", np.nan), errors="coerce"),
                    "significance": _sig_mark(float(min_fdr)) if pd.notna(min_fdr) else "",
                    "n_asd": np.nan,
                    "n_td": np.nan,
                    "source_file": str(ch_path.relative_to(root)),
                },
            )
        overview_rows.append(
            {
                "analysis": "channel_level_analysis",
                "key_result": f"FDR-significant channels: {n_sig}",
                "source_file": str(ch_path.relative_to(root)),
            },
        )

    # 5) ADOS nonlinear / threshold
    nonlin_path = tables_dir / "ados_posterior_nonlinear_spline_threshold.csv"
    if nonlin_path.exists():
        nl = pd.read_csv(nonlin_path)
        for model_set in ["unadjusted", "adjusted"]:
            sub = nl[nl["model_set"] == model_set]
            if sub.empty:
                continue
            r = sub.iloc[0]
            p = pd.to_numeric(r.get("spline_vs_linear_p", np.nan), errors="coerce")
            long_rows.append(
                {
                    "analysis": "ados_nonlinear_spline",
                    "outcome": "ADOS_total",
                    "term": model_set,
                    "estimate": pd.to_numeric(r.get("delta_aic_spline_minus_linear", np.nan), errors="coerce"),
                    "pvalue": p,
                    "significance": _sig_mark(float(p)) if pd.notna(p) else "",
                    "n_asd": pd.to_numeric(r.get("n", np.nan), errors="coerce"),
                    "n_td": 0,
                    "source_file": str(nonlin_path.relative_to(root)),
                },
            )
        for model_set in ["unadjusted_threshold", "adjusted_threshold"]:
            sub = nl[nl["model_set"] == model_set]
            if sub.empty:
                continue
            r = sub.iloc[0]
            p = pd.to_numeric(r.get("hinge_pvalue", np.nan), errors="coerce")
            long_rows.append(
                {
                    "analysis": "ados_threshold_piecewise",
                    "outcome": "ADOS_total",
                    "term": model_set,
                    "estimate": pd.to_numeric(r.get("best_knot_posterior_exponent", np.nan), errors="coerce"),
                    "pvalue": p,
                    "significance": _sig_mark(float(p)) if pd.notna(p) else "",
                    "n_asd": pd.to_numeric(r.get("n", np.nan), errors="coerce"),
                    "n_td": 0,
                    "source_file": str(nonlin_path.relative_to(root)),
                },
            )
        overview_rows.append(
            {
                "analysis": "ados_nonlinear_threshold",
                "key_result": "Threshold model supports nonlinear association",
                "source_file": str(nonlin_path.relative_to(root)),
            },
        )

    # 6) ADOS latent class
    lc_path = tables_dir / "ados_posterior_latent_class_tests.csv"
    if lc_path.exists():
        lc = pd.read_csv(lc_path)
        if len(lc):
            r = lc.iloc[0]
            for term, pcol in [
                ("anova_ados_by_class", "anova_p_ados_by_class"),
                ("kruskal_ados_by_class", "kruskal_p_ados_by_class"),
                ("spearman_class_order_vs_ados", "spearman_p_class_order_vs_ados"),
                ("adjusted_anova_ados_by_class", "adjusted_anova_p_ados_by_class"),
            ]:
                p = pd.to_numeric(r.get(pcol, np.nan), errors="coerce")
                long_rows.append(
                    {
                        "analysis": "ados_latent_class",
                        "outcome": "ADOS_total",
                        "term": term,
                        "estimate": np.nan,
                        "pvalue": p,
                        "significance": _sig_mark(float(p)) if pd.notna(p) else "",
                        "n_asd": pd.to_numeric(r.get("n_asd_with_ados_posterior", np.nan), errors="coerce"),
                        "n_td": 0,
                        "source_file": str(lc_path.relative_to(root)),
                    },
                )
            overview_rows.append(
                {
                    "analysis": "ados_latent_class",
                    "key_result": "Monotonic trend present; omnibus tests non-significant",
                    "source_file": str(lc_path.relative_to(root)),
                },
            )

    long_df = pd.DataFrame(long_rows)
    overview_df = pd.DataFrame(overview_rows)

    long_out = tables_dir / "postqc_analysis_results_long.csv"
    overview_out = tables_dir / "postqc_analysis_results_overview.csv"
    long_df.to_csv(long_out, index=False)
    overview_df.to_csv(overview_out, index=False)

    print(f"Saved: {long_out}")
    print(f"Saved: {overview_out}")
    print(f"Rows (long): {len(long_df)}")
    print(f"Rows (overview): {len(overview_df)}")


if __name__ == "__main__":
    main()
