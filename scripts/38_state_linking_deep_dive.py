#!/usr/bin/env python
"""
38_state_linking_deep_dive.py
-----------------------------
补充分析合集：
1) 解释 n56 / n62 / n73 的样本口径差异（样本量审计）
2) 补充 Neutral 片段 ISC（与 mental / pain 同口径）
3) 检验 ISC ~ CARS 的非线性（倒U二次项 + 阈值模型）
4) 路径/中介闭环（X=resting posterior, M1=Delta exponent, M2=ISC, Y=CARS）
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import ttest_ind
from statsmodels.stats.anova import anova_lm


EVENT_TYPES = ("mental", "pain", "neutral")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="State-linking deep-dive analyses")
    parser.add_argument("--project_root", type=str, default=".", help="项目根目录")
    parser.add_argument(
        "--resting_csv",
        type=str,
        default="outputs/tables/resting_features_locked.csv",
        help="静息特征CSV",
    )
    parser.add_argument(
        "--movie_event_means_csv",
        type=str,
        default="derivatives_task_movie/stats/movie_event_subject_condition_means.csv",
        help="电影事件条件均值CSV（exponent）",
    )
    parser.add_argument(
        "--movie_events_csv",
        type=str,
        default="data/movie_events.csv",
        help="电影事件标签CSV（mental/pain）",
    )
    parser.add_argument(
        "--timeseries_csv",
        type=str,
        default="derivatives_task_movie/specparam/specparam_exponent_timeseries_global.csv",
        help="动态exponent时序CSV",
    )
    parser.add_argument(
        "--isc_csv",
        type=str,
        default="derivatives_task_movie/stats/movie_isc_subject_values.csv",
        help="现有ISC结果（mental/pain）",
    )
    parser.add_argument(
        "--participants_clinical_csv",
        type=str,
        default="data/participants/participants.csv",
        help="临床量表CSV（含CARS）",
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        default="derivatives_task_movie/stats",
        help="输出目录",
    )
    parser.add_argument(
        "--min_overlap_points",
        type=int,
        default=10,
        help="ISC相关最小重叠点",
    )
    parser.add_argument(
        "--bootstrap_n",
        type=int,
        default=2000,
        help="路径分析bootstrap重采样次数",
    )
    parser.add_argument(
        "--random_seed",
        type=int,
        default=42,
        help="随机种子",
    )
    return parser.parse_args()


def fisher_z(r: float) -> float:
    if pd.isna(r):
        return np.nan
    r = float(np.clip(r, -0.999999, 0.999999))
    return float(np.arctanh(r))


def safe_corr(x: np.ndarray, y: np.ndarray, min_points: int) -> tuple[float, int]:
    mask = np.isfinite(x) & np.isfinite(y)
    n = int(mask.sum())
    if n < min_points:
        return np.nan, n
    xv = x[mask]
    yv = y[mask]
    if np.std(xv) < 1e-12 or np.std(yv) < 1e-12:
        return np.nan, n
    return float(np.corrcoef(xv, yv)[0, 1]), n


def label_bins_with_neutral(ts_bins: np.ndarray, events: pd.DataFrame) -> pd.DataFrame:
    events = events.copy()
    events["event_type"] = events["event_type"].astype(str).str.lower().str.strip()
    events = events[events["event_type"].isin(["mental", "pain"])].copy()
    events["start"] = pd.to_numeric(events["onset_sec"], errors="coerce")
    events["end"] = pd.to_numeric(events["onset_sec"], errors="coerce") + pd.to_numeric(
        events["duration_sec"], errors="coerce"
    )
    events = events.dropna(subset=["start", "end"]).sort_values("start").reset_index(drop=True)

    rows: list[dict[str, float | int | str]] = []
    for b in np.sort(np.unique(np.round(ts_bins, 6))):
        labels = []
        for _, ev in events.iterrows():
            if float(ev["start"]) <= float(b) < float(ev["end"]):
                labels.append(str(ev["event_type"]))
        if "mental" in labels:
            event_type = "mental"
        elif "pain" in labels:
            event_type = "pain"
        else:
            event_type = "neutral"
        rows.append({"center_sec": float(b), "event_type": event_type})

    key_df = pd.DataFrame(rows)
    for ev in EVENT_TYPES:
        sub_idx = key_df.index[key_df["event_type"] == ev].to_numpy()
        key_df.loc[key_df["event_type"] == ev, "concat_index"] = np.arange(len(sub_idx), dtype=int)
    key_df["concat_index"] = key_df["concat_index"].astype(int)
    return key_df


def compute_isc_for_event(subject_concat: pd.DataFrame, event_type: str, min_overlap_points: int) -> pd.DataFrame:
    sub_ev = subject_concat[subject_concat["event_type"] == event_type].copy()
    mat = sub_ev.pivot_table(
        index=["subject_id", "group"],
        columns="concat_index",
        values="exponent_mean",
        aggfunc="mean",
    )
    mat = mat.sort_index(axis=1)
    idx_df = mat.index.to_frame(index=False)
    idx_df.columns = ["subject_id", "group"]
    idx_df["group"] = idx_df["group"].astype(str).str.upper()

    td_mask = idx_df["group"] == "TD"
    asd_mask = idx_df["group"] == "ASD"
    td_vals = mat[td_mask.to_numpy()]
    asd_vals = mat[asd_mask.to_numpy()]

    if td_vals.shape[0] < 2:
        raise RuntimeError(f"{event_type}: TD样本不足，无法进行留一模板ISC")

    rows = []
    td_subjects = idx_df.loc[td_mask, "subject_id"].tolist()
    for i, sid in enumerate(td_subjects):
        x = td_vals.iloc[i].to_numpy(dtype=float)
        tmpl = td_vals.drop(td_vals.index[i]).mean(axis=0, skipna=True).to_numpy(dtype=float)
        r, n_overlap = safe_corr(x, tmpl, min_points=min_overlap_points)
        rows.append(
            {
                "subject_id": sid,
                "group": "TD",
                "event_type": event_type,
                "isc_r": r,
                "isc_z": fisher_z(r),
                "n_overlap_points": n_overlap,
                "template_type": "TD_LOO",
            }
        )

    td_template = td_vals.mean(axis=0, skipna=True).to_numpy(dtype=float)
    asd_subjects = idx_df.loc[asd_mask, "subject_id"].tolist()
    for i, sid in enumerate(asd_subjects):
        x = asd_vals.iloc[i].to_numpy(dtype=float)
        r, n_overlap = safe_corr(x, td_template, min_points=min_overlap_points)
        rows.append(
            {
                "subject_id": sid,
                "group": "ASD",
                "event_type": event_type,
                "isc_r": r,
                "isc_z": fisher_z(r),
                "n_overlap_points": n_overlap,
                "template_type": "TD_FULL",
            }
        )
    return pd.DataFrame(rows)


def run_nonlinear_models(df: pd.DataFrame, y_col: str) -> pd.DataFrame:
    tmp = df[[y_col, "CARS_total"]].dropna().copy()
    if len(tmp) < 12:
        return pd.DataFrame(
            [
                {
                    "isc_metric": y_col,
                    "n": len(tmp),
                    "linear_aic": np.nan,
                    "quadratic_aic": np.nan,
                    "quadratic_term_p": np.nan,
                    "linear_vs_quadratic_p": np.nan,
                    "best_threshold": np.nan,
                    "threshold_aic": np.nan,
                    "threshold_hinge_p": np.nan,
                    "linear_vs_threshold_p": np.nan,
                }
            ]
        )

    tmp["x"] = pd.to_numeric(tmp["CARS_total"], errors="coerce")
    tmp["x_c"] = tmp["x"] - tmp["x"].mean()
    tmp["x_c2"] = tmp["x_c"] ** 2

    linear = smf.ols(f"{y_col} ~ x_c", data=tmp).fit()
    quadratic = smf.ols(f"{y_col} ~ x_c + x_c2", data=tmp).fit()
    anova_quad = anova_lm(linear, quadratic)
    p_l_vs_q = float(anova_quad["Pr(>F)"].iloc[1]) if len(anova_quad) > 1 else np.nan

    quantiles = np.linspace(0.2, 0.8, 25)
    taus = sorted({float(tmp["x"].quantile(q)) for q in quantiles})
    thresh_models = []
    for tau in taus:
        tdf = tmp.copy()
        tdf["hinge"] = np.maximum(0.0, tdf["x"] - tau)
        model = smf.ols(f"{y_col} ~ x + hinge", data=tdf).fit()
        thresh_models.append((tau, model))
    best_tau, best_model = min(thresh_models, key=lambda z: z[1].aic)
    anova_thr = anova_lm(linear, best_model)
    p_l_vs_t = float(anova_thr["Pr(>F)"].iloc[1]) if len(anova_thr) > 1 else np.nan

    row = {
        "isc_metric": y_col,
        "n": int(len(tmp)),
        "linear_aic": float(linear.aic),
        "quadratic_aic": float(quadratic.aic),
        "quadratic_term_p": float(quadratic.pvalues.get("x_c2", np.nan)),
        "linear_vs_quadratic_p": p_l_vs_q,
        "best_threshold": float(best_tau),
        "threshold_aic": float(best_model.aic),
        "threshold_hinge_p": float(best_model.pvalues.get("hinge", np.nan)),
        "linear_vs_threshold_p": p_l_vs_t,
    }
    return pd.DataFrame([row])


def serial_path_bootstrap(
    df: pd.DataFrame,
    x_col: str,
    m1_col: str,
    m2_col: str,
    y_col: str,
    n_boot: int,
    seed: int,
) -> pd.DataFrame:
    d = df[[x_col, m1_col, m2_col, y_col]].dropna().copy()
    if len(d) < 20:
        return pd.DataFrame(
            [
                {
                    "n": len(d),
                    "a1_x_to_m1": np.nan,
                    "d_m1_to_m2": np.nan,
                    "a2_x_to_m2": np.nan,
                    "b1_m1_to_y": np.nan,
                    "b2_m2_to_y": np.nan,
                    "cprime_x_to_y": np.nan,
                    "ind_x_m1_y": np.nan,
                    "ind_x_m2_y": np.nan,
                    "ind_x_m1_m2_y": np.nan,
                    "ind_total": np.nan,
                    "ind_x_m1_m2_y_ci_low": np.nan,
                    "ind_x_m1_m2_y_ci_high": np.nan,
                }
            ]
        )

    m1_fit = smf.ols(f"{m1_col} ~ {x_col}", data=d).fit()
    m2_fit = smf.ols(f"{m2_col} ~ {x_col} + {m1_col}", data=d).fit()
    y_fit = smf.ols(f"{y_col} ~ {x_col} + {m1_col} + {m2_col}", data=d).fit()

    a1 = float(m1_fit.params.get(x_col, np.nan))
    d21 = float(m2_fit.params.get(m1_col, np.nan))
    a2 = float(m2_fit.params.get(x_col, np.nan))
    b1 = float(y_fit.params.get(m1_col, np.nan))
    b2 = float(y_fit.params.get(m2_col, np.nan))
    cprime = float(y_fit.params.get(x_col, np.nan))

    ind_x_m1_y = a1 * b1
    ind_x_m2_y = a2 * b2
    ind_x_m1_m2_y = a1 * d21 * b2
    ind_total = ind_x_m1_y + ind_x_m2_y + ind_x_m1_m2_y

    rng = np.random.default_rng(seed)
    serial_samples = []
    n = len(d)
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        b = d.iloc[idx].copy()
        try:
            b_m1 = smf.ols(f"{m1_col} ~ {x_col}", data=b).fit()
            b_m2 = smf.ols(f"{m2_col} ~ {x_col} + {m1_col}", data=b).fit()
            b_y = smf.ols(f"{y_col} ~ {x_col} + {m1_col} + {m2_col}", data=b).fit()
            ba1 = float(b_m1.params.get(x_col, np.nan))
            bd = float(b_m2.params.get(m1_col, np.nan))
            bb2 = float(b_y.params.get(m2_col, np.nan))
            serial_samples.append(ba1 * bd * bb2)
        except Exception:
            serial_samples.append(np.nan)
    serial_arr = np.array(serial_samples, dtype=float)
    serial_arr = serial_arr[np.isfinite(serial_arr)]
    if len(serial_arr) > 0:
        ci_low, ci_high = np.quantile(serial_arr, [0.025, 0.975])
    else:
        ci_low, ci_high = np.nan, np.nan

    return pd.DataFrame(
        [
            {
                "n": int(len(d)),
                "a1_x_to_m1": a1,
                "d_m1_to_m2": d21,
                "a2_x_to_m2": a2,
                "b1_m1_to_y": b1,
                "b2_m2_to_y": b2,
                "cprime_x_to_y": cprime,
                "ind_x_m1_y": ind_x_m1_y,
                "ind_x_m2_y": ind_x_m2_y,
                "ind_x_m1_m2_y": ind_x_m1_m2_y,
                "ind_total": ind_total,
                "ind_x_m1_m2_y_ci_low": float(ci_low),
                "ind_x_m1_m2_y_ci_high": float(ci_high),
            }
        ]
    )


def main() -> None:
    args = parse_args()
    root = Path(args.project_root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    resting = pd.read_csv(root / args.resting_csv)
    resting = resting[["subject_id", "group", "posterior_exponent"]].copy()
    resting["subject_id"] = resting["subject_id"].astype(str)
    resting["group"] = resting["group"].astype(str).str.upper()
    resting["posterior_exponent"] = pd.to_numeric(resting["posterior_exponent"], errors="coerce")
    resting = resting.rename(columns={"posterior_exponent": "resting_posterior_exponent"})

    event_means = pd.read_csv(root / args.movie_event_means_csv)
    event_means["subject_id"] = event_means["subject_id"].astype(str)
    event_means["group"] = event_means["group"].astype(str).str.upper()
    event_means["event_type"] = event_means["event_type"].astype(str).str.lower()
    event_means["exponent"] = pd.to_numeric(event_means["exponent"], errors="coerce")
    event_means = event_means[event_means["event_type"].isin(["mental", "pain"])].copy()
    exp_wide = event_means.pivot_table(
        index=["subject_id", "group"],
        columns="event_type",
        values="exponent",
        aggfunc="mean",
    ).reset_index()
    exp_wide.columns.name = None
    exp_wide = exp_wide.rename(columns={"mental": "mental_exponent", "pain": "pain_exponent"})

    delta_df = exp_wide.merge(resting, on=["subject_id", "group"], how="inner")
    delta_df["Delta_Exponent_mental"] = delta_df["mental_exponent"] - delta_df["resting_posterior_exponent"]
    delta_df["Delta_Exponent_pain"] = delta_df["pain_exponent"] - delta_df["resting_posterior_exponent"]

    t_rows = []
    for metric in ["Delta_Exponent_mental", "Delta_Exponent_pain"]:
        asd = delta_df.loc[delta_df["group"] == "ASD", metric].dropna().to_numpy()
        td = delta_df.loc[delta_df["group"] == "TD", metric].dropna().to_numpy()
        tt = ttest_ind(asd, td, equal_var=False, nan_policy="omit")
        s_p = np.sqrt(
            ((len(asd) - 1) * np.var(asd, ddof=1) + (len(td) - 1) * np.var(td, ddof=1))
            / max(len(asd) + len(td) - 2, 1)
        )
        d_eff = (np.mean(asd) - np.mean(td)) / s_p if s_p > 0 else np.nan
        t_rows.append(
            {
                "metric": metric,
                "n_asd": int(len(asd)),
                "n_td": int(len(td)),
                "asd_mean": float(np.mean(asd)),
                "asd_sd": float(np.std(asd, ddof=1)),
                "td_mean": float(np.mean(td)),
                "td_sd": float(np.std(td, ddof=1)),
                "mean_diff_asd_minus_td": float(np.mean(asd) - np.mean(td)),
                "cohen_d": float(d_eff),
                "t_stat_welch": float(tt.statistic),
                "p_value_welch": float(tt.pvalue),
            }
        )
    delta_t_df = pd.DataFrame(t_rows)

    ts = pd.read_csv(root / args.timeseries_csv)
    ts = ts[["subject_id", "group", "window_start_sec", "window_end_sec", "exponent_mean"]].copy()
    ts["subject_id"] = ts["subject_id"].astype(str)
    ts["group"] = ts["group"].astype(str).str.upper()
    ts["exponent_mean"] = pd.to_numeric(ts["exponent_mean"], errors="coerce")
    ts["center_sec"] = np.round((ts["window_start_sec"] + ts["window_end_sec"]) / 2.0, 6)

    events = pd.read_csv(root / args.movie_events_csv)
    keys = label_bins_with_neutral(ts_bins=ts["center_sec"].to_numpy(dtype=float), events=events)
    subject_concat = ts[["subject_id", "group", "center_sec", "exponent_mean"]].merge(
        keys, on="center_sec", how="left"
    )
    subject_concat = subject_concat.dropna(subset=["event_type", "concat_index"]).copy()
    subject_concat["concat_index"] = subject_concat["concat_index"].astype(int)

    isc_parts = []
    for ev in EVENT_TYPES:
        isc_parts.append(
            compute_isc_for_event(
                subject_concat=subject_concat,
                event_type=ev,
                min_overlap_points=int(args.min_overlap_points),
            )
        )
    isc_with_neutral = pd.concat(isc_parts, ignore_index=True)

    isc_stats_rows = []
    for ev in EVENT_TYPES:
        sub = isc_with_neutral[isc_with_neutral["event_type"] == ev]
        asd = sub.loc[sub["group"] == "ASD", "isc_z"].dropna().to_numpy()
        td = sub.loc[sub["group"] == "TD", "isc_z"].dropna().to_numpy()
        if len(asd) >= 2 and len(td) >= 2:
            t_res = ttest_ind(asd, td, equal_var=False, nan_policy="omit")
            t_stat = float(t_res.statistic)
            p_val = float(t_res.pvalue)
        else:
            t_stat = np.nan
            p_val = np.nan
        isc_stats_rows.append(
            {
                "event_type": ev,
                "n_asd": int(len(asd)),
                "n_td": int(len(td)),
                "asd_mean_z": float(np.mean(asd)) if len(asd) else np.nan,
                "td_mean_z": float(np.mean(td)) if len(td) else np.nan,
                "t_stat_welch": t_stat,
                "p_value_welch": p_val,
            }
        )
    isc_stats_df = pd.DataFrame(isc_stats_rows)

    isc_wide = isc_with_neutral.pivot_table(
        index=["subject_id", "group"],
        columns="event_type",
        values="isc_z",
        aggfunc="mean",
    ).reset_index()
    isc_wide.columns.name = None
    isc_wide = isc_wide.rename(
        columns={"mental": "mental_isc_z", "pain": "pain_isc_z", "neutral": "neutral_isc_z"}
    )

    part = pd.read_csv(root / args.participants_clinical_csv)
    part["subject_id"] = part["subject_id"].astype(str)
    part["group"] = part["group"].astype(str).str.upper()
    if "included_final" in part.columns:
        part["included_final"] = pd.to_numeric(part["included_final"], errors="coerce")
    else:
        part["included_final"] = np.nan
    part["CARS_total"] = pd.to_numeric(part["CARS_total"], errors="coerce")
    part = part[["subject_id", "group", "CARS_total", "included_final"]]

    asd_isc = isc_wide[(isc_wide["group"] == "ASD")].copy()
    n73_ids = set(
        asd_isc.dropna(subset=["mental_isc_z", "pain_isc_z"])["subject_id"].astype(str).tolist()
    )
    asd_delta = delta_df[delta_df["group"] == "ASD"].copy()
    n62_ids = set(
        asd_delta.dropna(subset=["Delta_Exponent_mental", "Delta_Exponent_pain"])["subject_id"].astype(str).tolist()
    )
    asd_clin = asd_isc.merge(part, on=["subject_id", "group"], how="left")
    n56_ids = set(
        asd_clin[
            (asd_clin["subject_id"].isin(n62_ids))
            & (asd_clin["included_final"] == 1)
            & asd_clin["CARS_total"].notna()
            & asd_clin["mental_isc_z"].notna()
            & asd_clin["pain_isc_z"].notna()
        ]["subject_id"].astype(str).tolist()
    )

    audit_rows = [
        {
            "sample_label": "ASD_n73_task_isc_only",
            "definition": "ASD with both mental_isc_z and pain_isc_z available",
            "n": len(n73_ids),
        },
        {
            "sample_label": "ASD_n62_resting_task_delta",
            "definition": "ASD with resting posterior + mental/pain exponent delta complete",
            "n": len(n62_ids),
        },
        {
            "sample_label": "ASD_n56_with_cars",
            "definition": "ASD n62 intersection with CARS_total + included_final=1 + mental/pain ISC",
            "n": len(n56_ids),
        },
        {
            "sample_label": "drop_n73_to_n62",
            "definition": "Missing resting-task delta information",
            "n": len(n73_ids - n62_ids),
        },
        {
            "sample_label": "drop_n62_to_n56",
            "definition": "Missing CARS/included_final or ISC for closed-loop model",
            "n": len(n62_ids - n56_ids),
        },
    ]
    audit_df = pd.DataFrame(audit_rows)

    closed_df = (
        delta_df.merge(isc_wide, on=["subject_id", "group"], how="inner")
        .merge(part, on=["subject_id", "group"], how="left")
        .copy()
    )
    closed_df = closed_df[
        (closed_df["group"] == "ASD")
        & (closed_df["subject_id"].astype(str).isin(n56_ids))
    ].copy()

    nonlin_parts = []
    for metric in ["mental_isc_z", "pain_isc_z", "neutral_isc_z"]:
        nonlin_parts.append(run_nonlinear_models(closed_df, y_col=metric))
    nonlin_df = pd.concat(nonlin_parts, ignore_index=True)

    path_mental = serial_path_bootstrap(
        closed_df,
        x_col="resting_posterior_exponent",
        m1_col="Delta_Exponent_mental",
        m2_col="mental_isc_z",
        y_col="CARS_total",
        n_boot=int(args.bootstrap_n),
        seed=int(args.random_seed),
    )
    path_mental["condition"] = "mental"

    path_pain = serial_path_bootstrap(
        closed_df,
        x_col="resting_posterior_exponent",
        m1_col="Delta_Exponent_pain",
        m2_col="pain_isc_z",
        y_col="CARS_total",
        n_boot=int(args.bootstrap_n),
        seed=int(args.random_seed) + 1,
    )
    path_pain["condition"] = "pain"
    path_df = pd.concat([path_mental, path_pain], ignore_index=True)

    # 输出
    delta_df.to_csv(out_dir / "delta_exponent_subject_values.csv", index=False)
    delta_t_df.to_csv(out_dir / "delta_exponent_group_ttests.csv", index=False)
    keys.to_csv(out_dir / "movie_isc_concat_keys_with_neutral.csv", index=False)
    subject_concat.to_csv(out_dir / "movie_isc_subject_concat_timeseries_with_neutral.csv", index=False)
    isc_with_neutral.to_csv(out_dir / "movie_isc_subject_values_with_neutral.csv", index=False)
    isc_stats_df.to_csv(out_dir / "movie_isc_group_stats_with_neutral.csv", index=False)
    audit_df.to_csv(out_dir / "sample_size_audit_state_linking.csv", index=False)
    closed_df.to_csv(out_dir / "state_linking_closed_loop_asd_subject_values.csv", index=False)
    nonlin_df.to_csv(out_dir / "cars_isc_nonlinear_models.csv", index=False)
    path_df.to_csv(out_dir / "state_linking_serial_path_models.csv", index=False)

    print("Saved:", out_dir / "movie_isc_subject_values_with_neutral.csv")
    print("Saved:", out_dir / "movie_isc_group_stats_with_neutral.csv")
    print("Saved:", out_dir / "sample_size_audit_state_linking.csv")
    print("Saved:", out_dir / "cars_isc_nonlinear_models.csv")
    print("Saved:", out_dir / "state_linking_serial_path_models.csv")
    print("\nSample-size audit:")
    print(audit_df.to_string(index=False))
    print("\nNeutral ISC group stats:")
    print(isc_stats_df.to_string(index=False))
    print("\nNonlinear model summary:")
    print(nonlin_df.to_string(index=False))
    print("\nPath model summary:")
    print(path_df.to_string(index=False))


if __name__ == "__main__":
    main()
