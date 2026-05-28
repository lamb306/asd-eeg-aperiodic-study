#!/usr/bin/env python
"""
89_time_resolved_exponent_variability.py
----------------------------------------
滑窗 specparam → exponent 时间序列 → 波动率指标（方差 / 多尺度熵）。

默认：主研究静息 matched_postqc 队列，从 .mff 连续数据计算（2 s 窗，1 s 步长，后部 ROI E33–E38）。

也可 `--from-timeseries` 从已有动态 specparam 表直接汇总（如电影任务）。

输出（derivatives_root/specparam/）：
  - exponent_timeseries_posterior_sliding.csv
  - exponent_variability_subject_metrics.csv
  - exponent_variability_group_tests.csv
  - exponent_variability_group_models.csv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import pearsonr, spearmanr, ttest_ind

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config, load_roi_config, setup_logging  # noqa: E402
from src.eeg_preprocessing import (  # noqa: E402
    apply_filters,
    drop_reference_and_non_scalp_channels,
    read_raw_eeg,
    resample_if_needed,
    set_montage,
    set_reference,
)
from src.io_utils import attach_usable_epochs, load_analysis_participants, save_csv  # noqa: E402
from src.psd_utils import compute_psd_matrix_from_epochs, psd_windows_to_wide_df  # noqa: E402
from src.specparam_utils import fit_subject_specparam_dynamic  # noqa: E402
from src.time_series_metrics import exponent_variability_metrics  # noqa: E402

POSTERIOR_CHANNELS = ("E33", "E36", "E37", "E38")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="滑窗 exponent 波动率分析")
    p.add_argument(
        "--config",
        default=str(PROJECT_ROOT / "config/config_resting_matched_postqc_sliding.yaml"),
    )
    p.add_argument(
        "--from-timeseries",
        type=Path,
        default=None,
        help="跳过滑窗拟合，直接从已有时间序列 CSV 汇总（需含 subject_id, group, aperiodic_exponent 或 exponent_mean）",
    )
    p.add_argument("--channel-col", default="ROI_TARGET", help="动态 specparam 通道列名")
    p.add_argument("--min-r-squared", type=float, default=0.8, help="纳入波动率计算的最小窗口 r²")
    p.add_argument("--limit-subjects", type=int, default=None)
    p.add_argument("--overwrite", action="store_true")
    return p.parse_args()


def _resolve_raw_path(cfg: dict, row: pd.Series) -> Path | None:
    rel = str(row.get("raw_EEG_file") or "").strip()
    if not rel:
        return None
    p = Path(rel)
    if not p.is_absolute():
        p = PROJECT_ROOT / p
    return p if p.exists() else None


def preprocess_continuous_raw(raw_path: Path, cfg: dict) -> Any:
    """轻量预处理：读入 → 剔通道 → montage → 滤波 → 重采样 → 平均参考。"""
    eeg_cfg = cfg.get("eeg", {})
    filt = cfg.get("filter", {})
    raw = read_raw_eeg(raw_path, preload=True)
    raw, _ = drop_reference_and_non_scalp_channels(raw, eeg_cfg)
    raw = set_montage(raw, eeg_cfg.get("montage", "GSN-HydroCel-64_1.0"))
    raw = apply_filters(
        raw,
        l_freq=float(filt.get("highpass_hz", 0.5)),
        h_freq=float(filt.get("lowpass_hz", 45.0)),
        notch_freq=float(filt.get("notch_hz", 50.0)),
        notch_enabled=bool(filt.get("notch_enabled", True)),
    )
    raw = resample_if_needed(raw, float(eeg_cfg.get("sampling_rate_target", 250)))
    raw = set_reference(raw, cfg.get("reference", {}).get("method", "average"))
    return raw


def compute_sliding_exponent_series(
    subject_id: str,
    group: str,
    raw_path: Path,
    cfg: dict,
) -> pd.DataFrame:
    """单被试：滑窗 PSD + 后部 ROI 动态 specparam。"""
    import mne

    psd_cfg = cfg["psd"]
    sw = psd_cfg.get("sliding_window", {})
    window_sec = float(sw.get("window_sec", 2.0))
    step_sec = float(sw.get("step_sec", 1.0))
    welch_cfg = psd_cfg.get("welch", {})
    fmin = float(psd_cfg.get("freq_min_hz", 1.0))
    fmax = float(psd_cfg.get("freq_max_hz", 40.0))

    raw = preprocess_continuous_raw(raw_path, cfg)
    overlap = max(0.0, window_sec - step_sec)
    epochs = mne.make_fixed_length_epochs(
        raw,
        duration=window_sec,
        overlap=overlap,
        preload=True,
        reject_by_annotation=True,
        verbose=False,
    )
    if len(epochs) == 0:
        raise RuntimeError(f"{subject_id}: 无有效滑窗 epoch")

    freqs, psd_windows, ch_names = compute_psd_matrix_from_epochs(epochs, fmin, fmax, welch_cfg)
    sfreq = raw.info["sfreq"]
    starts = (epochs.events[:, 0] - raw.first_samp) / sfreq
    ends = starts + window_sec

    psd_wide = psd_windows_to_wide_df(
        subject_id=subject_id,
        group=group,
        freqs=freqs,
        psd_windows=psd_windows,
        ch_names=ch_names,
        window_starts=starts,
        window_ends=ends,
    )

    sp_cfg = dict(cfg.get("specparam", {}))
    sp_cfg.setdefault("dynamic", {})
    sp_cfg["dynamic"]["fit_mode"] = "roi_mean"
    sp_cfg["dynamic"]["target_channels"] = list(POSTERIOR_CHANNELS)

    fit_df = fit_subject_specparam_dynamic(psd_wide, sp_cfg)
    fit_df = fit_df.rename(columns={"aperiodic_exponent": "exponent_posterior"})
    fit_df["window_center_sec"] = (
        fit_df["window_start_sec"].astype(float) + fit_df["window_end_sec"].astype(float)
    ) / 2.0
    return fit_df


def load_timeseries_for_variability(path: Path, channel_col: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "exponent_mean" in df.columns and "aperiodic_exponent" not in df.columns:
        df["aperiodic_exponent"] = df["exponent_mean"]
    if channel_col and "channel" in df.columns:
        df = df[df["channel"].astype(str) == channel_col].copy()
    need = {"subject_id", "group", "aperiodic_exponent"}
    miss = need - set(df.columns)
    if miss:
        raise ValueError(f"时间序列文件缺少列: {miss}")
    if "window_index" not in df.columns:
        df = df.sort_values(["subject_id", "window_start_sec"] if "window_start_sec" in df.columns else ["subject_id"])
        df["window_index"] = df.groupby("subject_id").cumcount()
    return df


def subject_level_variability(
    ts_df: pd.DataFrame,
    min_r_squared: float,
    static_posterior: pd.DataFrame | None,
) -> pd.DataFrame:
    """被试级波动率 + 与静态 exponent 对照。"""
    value_col = "exponent_posterior" if "exponent_posterior" in ts_df.columns else "aperiodic_exponent"
    rows = []
    for sid, sub in ts_df.groupby("subject_id"):
        grp = str(sub["group"].iloc[0])
        w = sub.copy()
        if "r_squared" in w.columns:
            w = w[pd.to_numeric(w["r_squared"], errors="coerce") >= min_r_squared]
        elif "r_squared_mean" in w.columns:
            w = w[pd.to_numeric(w["r_squared_mean"], errors="coerce") >= min_r_squared]
        series = pd.to_numeric(w[value_col], errors="coerce").dropna().to_numpy()
        metrics = exponent_variability_metrics(series)
        row = {
            "subject_id": str(sid),
            "group": grp,
            **metrics,
            "static_posterior_exponent": np.nan,
        }
        if static_posterior is not None:
            hit = static_posterior[static_posterior["subject_id"] == str(sid)]
            if not hit.empty:
                row["static_posterior_exponent"] = float(hit.iloc[0]["posterior_exponent"])
        rows.append(row)
    return pd.DataFrame(rows)


def group_welch_tests(metrics_df: pd.DataFrame, metric_cols: list[str]) -> pd.DataFrame:
    rows = []
    for col in metric_cols:
        asd = metrics_df.loc[metrics_df["group"] == "ASD", col].dropna().to_numpy(dtype=float)
        td = metrics_df.loc[metrics_df["group"] == "TD", col].dropna().to_numpy(dtype=float)
        if len(asd) < 2 or len(td) < 2:
            t_stat, p_val = np.nan, np.nan
        else:
            res = ttest_ind(asd, td, equal_var=False)
            t_stat, p_val = float(res.statistic), float(res.pvalue)
        rows.append(
            {
                "metric": col,
                "n_asd": int(len(asd)),
                "n_td": int(len(td)),
                "asd_mean": float(np.nanmean(asd)) if len(asd) else np.nan,
                "td_mean": float(np.nanmean(td)) if len(td) else np.nan,
                "mean_diff_td_minus_asd": float(np.nanmean(td) - np.nanmean(asd)) if len(asd) and len(td) else np.nan,
                "t_welch": t_stat,
                "p_welch": p_val,
            }
        )
    return pd.DataFrame(rows)


def group_regression_models(
    metrics_df: pd.DataFrame,
    participants: pd.DataFrame,
    outcomes: list[str],
) -> pd.DataFrame:
    pcols = ["subject_id", "age_months", "sex", "IQ_total"]
    if "usable_epochs" in participants.columns:
        pcols.append("usable_epochs")
    merged = metrics_df.merge(participants[pcols], on="subject_id", how="left")
    merged["group"] = merged["group"].astype(str).str.upper()
    rows = []
    for outcome in outcomes:
        need = [outcome, "group", "age_months"]
        if "usable_epochs" in merged.columns:
            need.append("usable_epochs")
        sub = merged.dropna(subset=need).copy()
        if "IQ_total" in sub.columns:
            sub = sub.dropna(subset=["IQ_total"])
        if len(sub) < 12:
            continue
        formula = f"{outcome} ~ C(group) + age_months"
        if "usable_epochs" in sub.columns:
            formula += " + usable_epochs"
        if "IQ_total" in sub.columns:
            formula += " + IQ_total"
        if "sex" in sub.columns and sub["sex"].notna().any():
            formula += " + C(sex)"
        ols = smf.ols(formula, data=sub).fit()
        tab = ols.summary2().tables[1].reset_index().rename(columns={"index": "term"})
        for _, r in tab.iterrows():
            rows.append(
                {
                    "outcome": outcome,
                    "estimator": "OLS",
                    "term": r["term"],
                    "coef": r["Coef."],
                    "pvalue": r.get("P>|t|", np.nan),
                    "n_obs": int(ols.nobs),
                    "formula": formula,
                }
            )
    return pd.DataFrame(rows)


def static_posterior_from_roi(deriv: Path) -> pd.DataFrame:
    roi = pd.read_csv(deriv / "roi/specparam_subject_roi_long.csv")
    post = roi[roi["roi"].isin(["parietal", "occipital"])].copy()
    out = (
        post.groupby(["subject_id", "group"], as_index=False)["exponent"]
        .mean()
        .rename(columns={"exponent": "posterior_exponent"})
    )
    out["subject_id"] = out["subject_id"].astype(str)
    return out


def run_compute_pipeline(cfg: dict, args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame]:
    log = setup_logging(cfg, name="exponent_variability")
    deriv = Path(cfg["paths"]["derivatives_root"])
    out_dir = deriv / "specparam"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts_path = out_dir / "exponent_timeseries_posterior_sliding.csv"

    if ts_path.exists() and not args.overwrite and args.from_timeseries is None:
        log.info("加载已有时间序列: %s", ts_path)
        ts_all = pd.read_csv(ts_path)
        return ts_all, static_posterior_from_roi(deriv)

    participants = load_analysis_participants(cfg)
    if args.limit_subjects:
        participants = participants.head(args.limit_subjects).copy()

    all_ts: list[pd.DataFrame] = []
    failures: list[str] = []
    for _, row in participants.iterrows():
        sid = str(row["subject_id"])
        grp = str(row["group"])
        raw_path = _resolve_raw_path(cfg, row)
        if raw_path is None:
            failures.append(sid)
            log.warning("%s: 未找到 raw_EEG_file", sid)
            continue
        try:
            fit_df = compute_sliding_exponent_series(sid, grp, raw_path, cfg)
            all_ts.append(fit_df)
            log.info("%s: %d windows", sid, len(fit_df))
        except Exception as exc:
            failures.append(sid)
            log.warning("%s 失败: %s", sid, exc)

    if not all_ts:
        raise RuntimeError("无成功被试；请检查 data/raw 下 .mff 是否存在")

    ts_all = pd.concat(all_ts, ignore_index=True)
    save_csv(ts_all, ts_path)
    if failures:
        pd.DataFrame({"subject_id": failures}).to_csv(out_dir / "exponent_variability_failures.csv", index=False)
    return ts_all, static_posterior_from_roi(deriv)


def main() -> None:
    args = parse_args()
    cfg = load_config(Path(args.config))
    deriv = Path(cfg["paths"]["derivatives_root"])
    stats_dir = deriv / "stats"
    stats_dir.mkdir(parents=True, exist_ok=True)

    if args.from_timeseries is not None:
        ts_all = load_timeseries_for_variability(args.from_timeseries, args.channel_col)
        static_post = static_posterior_from_roi(deriv) if (deriv / "roi").exists() else None
    else:
        ts_all, static_post = run_compute_pipeline(cfg, args)

    subj_metrics = subject_level_variability(ts_all, args.min_r_squared, static_post)
    participants = load_analysis_participants(cfg)
    participants = attach_usable_epochs(participants, deriv)

    metric_cols = [
        "exponent_var",
        "exponent_std",
        "exponent_cv",
        "exponent_range",
        "exponent_mse_mean",
    ]
    tests = group_welch_tests(subj_metrics, metric_cols)
    models = group_regression_models(subj_metrics, participants, metric_cols)

    save_csv(subj_metrics, stats_dir / "exponent_variability_subject_metrics.csv")
    save_csv(tests, stats_dir / "exponent_variability_group_tests.csv")
    save_csv(models, stats_dir / "exponent_variability_group_models.csv")

    # 静态均值 vs 时间波动率
    comp_rows = []
    if "static_posterior_exponent" in subj_metrics.columns:
        for xcol, ycol in (
            ("static_posterior_exponent", "exponent_var"),
            ("static_posterior_exponent", "exponent_mse_mean"),
            ("exponent_mean_ts", "exponent_var"),
        ):
            tmp = subj_metrics[[xcol, ycol]].dropna()
            if len(tmp) >= 5:
                r, p = pearsonr(tmp[xcol], tmp[ycol])
                rho, ps = spearmanr(tmp[xcol], tmp[ycol])
                comp_rows.append(
                    {
                        "x": xcol,
                        "y": ycol,
                        "pearson_r": float(r),
                        "pearson_p": float(p),
                        "spearman_rho": float(rho),
                        "spearman_p": float(ps),
                        "n": int(len(tmp)),
                    }
                )
    if comp_rows:
        save_csv(pd.DataFrame(comp_rows), stats_dir / "exponent_variability_static_vs_dynamic.csv")

    print(f"\n=== 队列 n={len(subj_metrics)} (ASD={(subj_metrics['group']=='ASD').sum()}, TD={(subj_metrics['group']=='TD').sum()}) ===")
    print("\n=== Welch 组间检验 (TD - ASD) ===")
    print(tests.to_string(index=False))
    if not models.empty:
        g = models[models["term"].str.contains("group", na=False)]
        print("\n=== OLS 组效应 ===")
        print(g[["outcome", "coef", "pvalue", "n_obs"]].to_string(index=False))


if __name__ == "__main__":
    main()
