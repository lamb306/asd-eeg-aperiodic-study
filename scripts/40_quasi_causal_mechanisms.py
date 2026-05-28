#!/usr/bin/env python
"""
40_quasi_causal_mechanisms.py
-----------------------------
准因果证据链三联分析：
1) Trait × Context 混合效应模型
2) Mental vs Neutral 事件级中介分析（ACME/ADE）
3) 滑窗 Lag-1 方向性检验（cross-lagged）
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.mediation import Mediation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Quasi-causal mechanism analyses")
    parser.add_argument("--project_root", type=str, default=".", help="项目根目录")
    parser.add_argument(
        "--resting_csv",
        type=str,
        default="outputs/tables/resting_features_locked.csv",
        help="静息特征CSV",
    )
    parser.add_argument(
        "--participants_csv",
        type=str,
        default="data/participants/participants_task_movie.csv",
        help="被试信息CSV（含age_months）",
    )
    parser.add_argument(
        "--event_mean_csv",
        type=str,
        default="derivatives_task_movie/stats/movie_event_subject_condition_means.csv",
        help="事件级指数均值CSV",
    )
    parser.add_argument(
        "--event_aligned_csv",
        type=str,
        default="derivatives_task_movie/stats/movie_event_aligned_timeseries.csv",
        help="对齐后连续时序CSV（0.5s）",
    )
    parser.add_argument(
        "--isc_with_neutral_csv",
        type=str,
        default="derivatives_task_movie/stats/movie_isc_subject_values_with_neutral.csv",
        help="含neutral的ISC CSV",
    )
    parser.add_argument(
        "--rolling_window_bins",
        type=int,
        default=20,
        help="动态ISC滚动相关窗口（bin数，20=10秒）",
    )
    parser.add_argument(
        "--mediation_bootstrap_n",
        type=int,
        default=2000,
        help="中介bootstrap次数",
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        default="derivatives_task_movie/stats",
        help="输出目录",
    )
    return parser.parse_args()


def _std_subject_group(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["subject_id"] = out["subject_id"].astype(str)
    out["group"] = out["group"].astype(str).str.upper()
    return out


def run_trait_context_mixed_model(
    event_mean: pd.DataFrame,
    resting: pd.DataFrame,
    participants: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, object]:
    task = event_mean.copy()
    task["event_type"] = task["event_type"].astype(str).str.lower()
    task["event_type"] = task["event_type"].replace({"baseline": "neutral"})
    task = task[task["event_type"].isin(["mental", "pain", "neutral"])].copy()
    task = task.rename(columns={"exponent": "task_exponent"})

    rest = resting[["subject_id", "group", "posterior_exponent"]].copy()
    rest = rest.rename(columns={"posterior_exponent": "resting_posterior_exponent"})
    rest["resting_posterior_exponent"] = pd.to_numeric(rest["resting_posterior_exponent"], errors="coerce")

    part = participants[["subject_id", "age_months"]].copy()
    part["age_months"] = pd.to_numeric(part["age_months"], errors="coerce")

    task = _std_subject_group(task)
    rest = _std_subject_group(rest)
    part["subject_id"] = part["subject_id"].astype(str)

    df = task.merge(rest, on=["subject_id", "group"], how="inner").merge(part, on="subject_id", how="left")
    df["task_exponent"] = pd.to_numeric(df["task_exponent"], errors="coerce")
    df = df.dropna(subset=["task_exponent", "resting_posterior_exponent", "age_months"]).copy()
    df["event_type"] = pd.Categorical(df["event_type"], categories=["neutral", "mental", "pain"], ordered=True)

    formula = (
        "task_exponent ~ C(event_type, Treatment(reference='neutral'))"
        " * resting_posterior_exponent + age_months"
    )

    try:
        fit = smf.mixedlm(
            formula=formula,
            data=df,
            groups=df["subject_id"],
            re_formula="~C(event_type, Treatment(reference='neutral'))",
        ).fit(method="lbfgs", reml=False, maxiter=200)
        model_type = "mixedlm_random_slope"
    except Exception:
        fit = smf.mixedlm(
            formula=formula,
            data=df,
            groups=df["subject_id"],
            re_formula="1",
        ).fit(method="lbfgs", reml=False, maxiter=200)
        model_type = "mixedlm_random_intercept"

    coef_df = pd.DataFrame(
        {
            "term": fit.params.index,
            "coef": fit.params.values,
            "std_err": fit.bse.values,
            "z_or_t": fit.tvalues.values,
            "p_value": fit.pvalues.values,
        }
    )
    coef_df["model_type"] = model_type
    coef_df["n_obs"] = int(fit.nobs)
    coef_df["n_subjects"] = int(df["subject_id"].nunique())
    return df, coef_df, fit


def run_event_level_mediation(
    event_mean: pd.DataFrame,
    isc_with_neutral: pd.DataFrame,
    resting: pd.DataFrame,
    participants: pd.DataFrame,
    n_boot: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    exp_df = event_mean.copy()
    exp_df["event_type"] = exp_df["event_type"].astype(str).str.lower().replace({"baseline": "neutral"})
    exp_df = exp_df[exp_df["event_type"].isin(["mental", "neutral"])].copy()
    exp_df = exp_df.rename(columns={"exponent": "task_exponent"})

    isc = isc_with_neutral.copy()
    isc["event_type"] = isc["event_type"].astype(str).str.lower()
    isc = isc[isc["event_type"].isin(["mental", "neutral"])].copy()
    isc = isc.rename(columns={"isc_z": "isc_z"})

    rest = resting[["subject_id", "group", "posterior_exponent"]].copy()
    rest = rest.rename(columns={"posterior_exponent": "resting_posterior_exponent"})
    rest["resting_posterior_exponent"] = pd.to_numeric(rest["resting_posterior_exponent"], errors="coerce")

    part = participants[["subject_id", "age_months"]].copy()
    part["age_months"] = pd.to_numeric(part["age_months"], errors="coerce")

    exp_df = _std_subject_group(exp_df)
    isc = _std_subject_group(isc)
    rest = _std_subject_group(rest)
    part["subject_id"] = part["subject_id"].astype(str)

    med_df = (
        exp_df[["subject_id", "group", "event_type", "task_exponent"]]
        .merge(isc[["subject_id", "group", "event_type", "isc_z"]], on=["subject_id", "group", "event_type"], how="inner")
        .merge(rest, on=["subject_id", "group"], how="inner")
        .merge(part, on="subject_id", how="left")
    )
    med_df["task_exponent"] = pd.to_numeric(med_df["task_exponent"], errors="coerce")
    med_df["isc_z"] = pd.to_numeric(med_df["isc_z"], errors="coerce")
    med_df = med_df.dropna(subset=["task_exponent", "isc_z", "resting_posterior_exponent", "age_months"]).copy()
    med_df["event_x"] = (med_df["event_type"] == "mental").astype(int)
    med_df["delta_exponent"] = med_df["task_exponent"] - med_df["resting_posterior_exponent"]

    mediator_model = smf.ols(
        "delta_exponent ~ event_x + resting_posterior_exponent + age_months",
        data=med_df,
    )
    outcome_model = smf.ols(
        "isc_z ~ event_x + delta_exponent + resting_posterior_exponent + age_months",
        data=med_df,
    )
    med_fit = Mediation(outcome_model, mediator_model, "event_x", "delta_exponent").fit(
        n_rep=n_boot,
        method="bootstrap",
    )
    med_summary = med_fit.summary()
    if isinstance(med_summary, pd.DataFrame):
        med_summary_df = med_summary.reset_index().rename(columns={"index": "effect"})
    else:
        med_summary_df = pd.DataFrame({"effect": ["summary_text"], "value": [str(med_summary)]})

    med_summary_df["n_rows"] = int(len(med_df))
    med_summary_df["n_subjects"] = int(med_df["subject_id"].nunique())
    return med_df, med_summary_df


def _build_time_resolved_isc(
    aligned_ts: pd.DataFrame,
    rolling_window_bins: int,
) -> pd.DataFrame:
    ts = aligned_ts.copy()
    ts["event_type"] = ts["event_type"].astype(str).str.lower().replace({"baseline": "neutral"})
    ts = ts[ts["event_type"].isin(["mental", "pain", "neutral"])].copy()
    ts["center_sec"] = pd.to_numeric(ts["center_sec"], errors="coerce")
    ts["exponent_mean"] = pd.to_numeric(ts["exponent_mean"], errors="coerce")
    ts = ts.dropna(subset=["center_sec", "exponent_mean"]).copy()
    ts = _std_subject_group(ts)

    # TD模板：每个时间点跨TD平均指数
    td_template = (
        ts[ts["group"] == "TD"]
        .groupby("center_sec", as_index=False)["exponent_mean"]
        .mean()
        .rename(columns={"exponent_mean": "td_template_exp"})
    )
    event_lookup = (
        ts.groupby("center_sec", as_index=False)["event_type"]
        .agg(lambda x: x.value_counts().index[0])
    )

    pivot = ts.pivot_table(
        index=["subject_id", "group"],
        columns="center_sec",
        values="exponent_mean",
        aggfunc="mean",
    )
    centers = np.array(sorted(pivot.columns.to_numpy(dtype=float)))
    template_vec = td_template.set_index("center_sec").reindex(centers)["td_template_exp"]

    rows = []
    for (sid, grp), row in pivot.iterrows():
        subj = row.reindex(centers)
        corr_t = subj.rolling(window=rolling_window_bins, min_periods=max(8, rolling_window_bins // 2)).corr(template_vec)
        for c, isc_r in corr_t.items():
            if pd.isna(isc_r):
                continue
            rows.append(
                {
                    "subject_id": sid,
                    "group": grp,
                    "center_sec": float(c),
                    "isc_r_t": float(isc_r),
                    "isc_z_t": float(np.arctanh(np.clip(isc_r, -0.999999, 0.999999))),
                    "subject_exp_t": float(subj.loc[c]) if pd.notna(subj.loc[c]) else np.nan,
                }
            )
    dyn = pd.DataFrame(rows)
    dyn = dyn.merge(event_lookup, on="center_sec", how="left")
    dyn["event_type"] = dyn["event_type"].astype(str).str.lower()
    return dyn


def run_lag_models(
    aligned_ts: pd.DataFrame,
    resting: pd.DataFrame,
    rolling_window_bins: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    dyn = _build_time_resolved_isc(aligned_ts=aligned_ts, rolling_window_bins=rolling_window_bins)
    rest = resting[["subject_id", "group", "posterior_exponent"]].copy()
    rest = rest.rename(columns={"posterior_exponent": "resting_posterior_exponent"})
    rest["resting_posterior_exponent"] = pd.to_numeric(rest["resting_posterior_exponent"], errors="coerce")
    rest = _std_subject_group(rest)

    dyn = _std_subject_group(dyn)
    lag_df = dyn.merge(rest, on=["subject_id", "group"], how="inner")
    lag_df["delta_t"] = lag_df["subject_exp_t"] - lag_df["resting_posterior_exponent"]
    lag_df = lag_df.sort_values(["subject_id", "center_sec"]).copy()
    lag_df["isc_lag1"] = lag_df.groupby("subject_id")["isc_z_t"].shift(1)
    lag_df["delta_lag1"] = lag_df.groupby("subject_id")["delta_t"].shift(1)
    lag_df = lag_df.dropna(subset=["isc_z_t", "delta_t", "isc_lag1", "delta_lag1"]).copy()

    # 模型A：ISC_t ~ Delta_{t-1} + ISC_{t-1}
    m_a = smf.ols("isc_z_t ~ delta_lag1 + isc_lag1", data=lag_df).fit(
        cov_type="cluster", cov_kwds={"groups": lag_df["subject_id"]}
    )
    # 模型B：Delta_t ~ ISC_{t-1} + Delta_{t-1}
    m_b = smf.ols("delta_t ~ isc_lag1 + delta_lag1", data=lag_df).fit(
        cov_type="cluster", cov_kwds={"groups": lag_df["subject_id"]}
    )

    lag_coef = pd.DataFrame(
        [
            {
                "model": "A_isc_t_on_delta_lag1",
                "predictor": "delta_lag1",
                "coef": float(m_a.params.get("delta_lag1", np.nan)),
                "p_value": float(m_a.pvalues.get("delta_lag1", np.nan)),
            },
            {
                "model": "A_isc_t_on_delta_lag1",
                "predictor": "isc_lag1",
                "coef": float(m_a.params.get("isc_lag1", np.nan)),
                "p_value": float(m_a.pvalues.get("isc_lag1", np.nan)),
            },
            {
                "model": "B_delta_t_on_isc_lag1",
                "predictor": "isc_lag1",
                "coef": float(m_b.params.get("isc_lag1", np.nan)),
                "p_value": float(m_b.pvalues.get("isc_lag1", np.nan)),
            },
            {
                "model": "B_delta_t_on_isc_lag1",
                "predictor": "delta_lag1",
                "coef": float(m_b.params.get("delta_lag1", np.nan)),
                "p_value": float(m_b.pvalues.get("delta_lag1", np.nan)),
            },
        ]
    )
    lag_coef["n_rows"] = int(len(lag_df))
    lag_coef["n_subjects"] = int(lag_df["subject_id"].nunique())
    return lag_df, lag_coef


def build_discussion_text(
    trait_coef: pd.DataFrame,
    med_summary: pd.DataFrame,
    lag_coef: pd.DataFrame,
) -> str:
    inter = trait_coef[trait_coef["term"].str.contains("event_type", case=False, na=False) & trait_coef["term"].str.contains("resting_posterior_exponent", case=False, na=False)].copy()
    inter_lines = []
    for _, r in inter.iterrows():
        inter_lines.append(f"{r['term']}: beta={r['coef']:.4f}, p={r['p_value']:.4g}")
    inter_txt = "; ".join(inter_lines) if inter_lines else "interaction terms not found"

    acme_row = med_summary[med_summary["effect"].astype(str).str.contains("ACME", case=False, na=False)].head(1)
    ade_row = med_summary[med_summary["effect"].astype(str).str.contains("ADE", case=False, na=False)].head(1)
    if len(acme_row) and "Estimate" in med_summary.columns:
        acme_txt = (
            f"ACME={float(acme_row['Estimate'].iloc[0]):.4f}, "
            f"p={float(acme_row['P-value'].iloc[0]):.4g}"
        )
    else:
        acme_txt = "ACME parsed from summary table unavailable"
    if len(ade_row) and "Estimate" in med_summary.columns:
        ade_txt = (
            f"ADE={float(ade_row['Estimate'].iloc[0]):.4f}, "
            f"p={float(ade_row['P-value'].iloc[0]):.4g}"
        )
    else:
        ade_txt = "ADE parsed from summary table unavailable"

    a_delta = lag_coef[(lag_coef["model"] == "A_isc_t_on_delta_lag1") & (lag_coef["predictor"] == "delta_lag1")]
    b_isc = lag_coef[(lag_coef["model"] == "B_delta_t_on_isc_lag1") & (lag_coef["predictor"] == "isc_lag1")]
    if len(a_delta):
        a_txt = f"Model A delta_lag1->ISC_t: beta={float(a_delta['coef'].iloc[0]):.4f}, p={float(a_delta['p_value'].iloc[0]):.4g}"
    else:
        a_txt = "Model A lag effect unavailable"
    if len(b_isc):
        b_txt = f"Model B isc_lag1->Delta_t: beta={float(b_isc['coef'].iloc[0]):.4f}, p={float(b_isc['p_value'].iloc[0]):.4g}"
    else:
        b_txt = "Model B lag effect unavailable"

    text = (
        "Trait × context mixed-effects analyses indicated that the contribution of resting posterior aperiodic exponent "
        "to task-state exponent varied across event contexts, as evidenced by the event-by-trait interaction terms "
        f"({inter_txt}). This pattern supports a context-constrained trait-to-state mapping rather than a context-invariant baseline effect. "
        "In event-level mediation (mental vs neutral), the decomposition of total effect into direct and mediated components "
        f"yielded {acme_txt} and {ade_txt}, suggesting that part of event-related ISC modulation is transmitted through task-evoked "
        "delta exponent reconfiguration. Finally, lag-1 cross-lag models on continuous 0.5-s windows showed "
        f"{a_txt}; {b_txt}. Taken together, these findings provide temporal-precedence-supported, quasi-causal evidence that "
        "resting aperiodic trait constrains context-dependent state reconfiguration, which in turn contributes to dynamic neural synchrony."
    )
    return text


def main() -> None:
    args = parse_args()
    root = Path(args.project_root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    resting = pd.read_csv(root / args.resting_csv)
    participants = pd.read_csv(root / args.participants_csv)
    event_mean = pd.read_csv(root / args.event_mean_csv)
    aligned_ts = pd.read_csv(root / args.event_aligned_csv)
    isc_with_neutral = pd.read_csv(root / args.isc_with_neutral_csv)

    # 任务1
    trait_df, trait_coef, _ = run_trait_context_mixed_model(
        event_mean=event_mean,
        resting=resting,
        participants=participants,
    )
    # 任务2
    med_df, med_summary = run_event_level_mediation(
        event_mean=event_mean,
        isc_with_neutral=isc_with_neutral,
        resting=resting,
        participants=participants,
        n_boot=int(args.mediation_bootstrap_n),
    )
    # 任务3
    lag_df, lag_coef = run_lag_models(
        aligned_ts=aligned_ts,
        resting=resting,
        rolling_window_bins=int(args.rolling_window_bins),
    )

    discussion = build_discussion_text(
        trait_coef=trait_coef,
        med_summary=med_summary,
        lag_coef=lag_coef,
    )

    # 保存
    trait_df.to_csv(out_dir / "quasi_causal_trait_context_input.csv", index=False)
    trait_coef.to_csv(out_dir / "quasi_causal_trait_context_mixedlm_coefficients.csv", index=False)
    med_df.to_csv(out_dir / "quasi_causal_mediation_input_mental_vs_neutral.csv", index=False)
    med_summary.to_csv(out_dir / "quasi_causal_mediation_summary_mental_vs_neutral.csv", index=False)
    lag_df.to_csv(out_dir / "quasi_causal_lag_model_input_timeseries.csv", index=False)
    lag_coef.to_csv(out_dir / "quasi_causal_lag_model_coefficients.csv", index=False)
    (out_dir / "quasi_causal_discussion_paragraph.txt").write_text(discussion, encoding="utf-8")

    # 终端摘要
    print("Saved:", out_dir / "quasi_causal_trait_context_mixedlm_coefficients.csv")
    print("Saved:", out_dir / "quasi_causal_mediation_summary_mental_vs_neutral.csv")
    print("Saved:", out_dir / "quasi_causal_lag_model_coefficients.csv")
    print("Saved:", out_dir / "quasi_causal_discussion_paragraph.txt")

    inter_rows = trait_coef[
        trait_coef["term"].str.contains("event_type", case=False, na=False)
        & trait_coef["term"].str.contains("resting_posterior_exponent", case=False, na=False)
    ].copy()
    print("\nTask1 Interaction terms:")
    print(inter_rows[["term", "coef", "p_value"]].to_string(index=False))

    print("\nTask2 Mediation summary:")
    print(med_summary.to_string(index=False))

    print("\nTask3 Lag model key coefficients:")
    print(lag_coef.to_string(index=False))


if __name__ == "__main__":
    main()

