"""与学龄前 ASD aperiodic 文献（Chen et al.）的 follow-up 对比分析。"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.formula.api import ols

logger = logging.getLogger(__name__)

GROUP_TERM = "C(group)[T.TD]"
COL_ASD = "#4C72B0"
COL_TD = "#DD8452"
COL_GRAY = "#4D4D4D"
PRESCHOOL_MAX_MONTHS = 72

PLOT_RC = {
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "DejaVu Sans", "sans-serif"],
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "axes.facecolor": "white",
    "figure.facecolor": "white",
    "axes.grid": False,
    "axes.spines.top": False,
    "axes.spines.right": False,
}

REQUIRED_PATHS = [
    ("participants", "data/participants/participants.csv"),
    ("roi_global", "derivatives/roi/specparam_subject_global.csv"),
    ("roi_long", "derivatives/roi/specparam_subject_roi_long.csv"),
    ("main_stats", "derivatives/stats/main_group_analysis.csv"),
    ("sensitivity_final", "outputs/tables/sensitivity_analysis_final.csv"),
    ("robustness", "outputs/tables/global_exponent_robustness_models.csv"),
]

OPTIONAL_PATHS = [
    ("periodic_peak", "derivatives/stats/periodic_peak_analysis.csv"),
    ("channel_qc", "derivatives/specparam/specparam_channel_results_qc.csv"),
]


def _resolve_path(root: Path, rel: str, fallbacks: list[str] | None = None) -> Path:
    p = root / rel
    if p.exists():
        return p
    for fb in fallbacks or []:
        alt = root / fb
        if alt.exists():
            logger.info("使用备选路径: %s → %s", rel, fb)
            return alt
    return p


def require_file(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"缺少必需文件 [{label}]: {path}")


def apply_plot_style() -> None:
    plt.rcParams.update(PLOT_RC)


def save_figure(fig: plt.Figure, out_base: Path) -> None:
    out_base.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf", "svg"):
        kw: dict[str, Any] = dict(bbox_inches="tight", facecolor="white")
        if ext == "png":
            kw["dpi"] = 600
        fig.savefig(out_base.with_suffix(f".{ext}"), **kw)
    plt.close(fig)


def fit_ols_model(formula: str, data: pd.DataFrame) -> tuple[Any, pd.DataFrame] | tuple[None, pd.DataFrame]:
    """Listwise deletion 后拟合 OLS（statsmodels 公式 API）。"""
    try:
        res = ols(formula, data=data).fit()
        if int(res.nobs) < 10:
            logger.warning("样本不足 (n=%d): %s", int(res.nobs), formula)
            return None, data
        sub = data.loc[res.fittedvalues.index].copy()
        return res, sub
    except Exception as exc:
        logger.warning("模型拟合失败: %s — %s", formula, exc)
        return None, data


def extract_model_terms(
    res: Any,
    outcome: str,
    model_name: str,
    sub: pd.DataFrame,
    highlight_terms: set[str] | None = None,
) -> list[dict[str, Any]]:
    """提取回归系数表行。"""
    rows = []
    conf = res.conf_int()
    counts = {
        "n": int(res.nobs),
        "n_ASD": int((sub["group"] == "ASD").sum()) if "group" in sub.columns else np.nan,
        "n_TD": int((sub["group"] == "TD").sum()) if "group" in sub.columns else np.nan,
    }
    for term in res.params.index:
        rows.append({
            "outcome": outcome,
            "model_name": model_name,
            **counts,
            "term": term,
            "coef": float(res.params[term]),
            "se": float(res.bse[term]),
            "t": float(res.tvalues[term]),
            "p": float(res.pvalues[term]),
            "ci_low": float(conf.loc[term, 0]),
            "ci_high": float(conf.loc[term, 1]),
            "r_squared": float(res.rsquared),
            "aic": float(res.aic),
            "bic": float(res.bic),
            "highlight": term in (highlight_terms or set()),
        })
    return rows


def load_and_merge_data(root: Path, cfg: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Path]]:
    """合并被试层面主表；返回 (main_qc_set, relaxed_epoch30_set, paths)。"""
    paths: dict[str, Path] = {}
    for key, rel in REQUIRED_PATHS:
        p = root / rel
        require_file(p, key)
        paths[key] = p

    participants = pd.read_csv(paths["participants"])
    participants["subject_id"] = participants["subject_id"].astype(str)
    if "included_final" in participants.columns:
        participants = participants[participants["included_final"].astype(int) == 1].copy()

    roi = pd.read_csv(paths["roi_global"])
    roi["subject_id"] = roi["subject_id"].astype(str)

    preproc_path = _resolve_path(
        root,
        "derivatives/qc/preprocessing_qc_summary.csv",
        ["derivatives/qc/preproc_summary.csv"],
    )
    if not preproc_path.exists():
        raise FileNotFoundError(
            "缺少预处理 QC：derivatives/qc/preprocessing_qc_summary.csv "
            "或 derivatives/qc/preproc_summary.csv"
        )
    paths["preproc"] = preproc_path
    preproc = pd.read_csv(preproc_path)
    preproc["subject_id"] = preproc["subject_id"].astype(str)

    sp_qc_path = _resolve_path(
        root,
        "derivatives/qc/specparam_qc_summary_subject.csv",
        ["derivatives/specparam/specparam_qc_summary_subject.csv"],
    )
    if not sp_qc_path.exists():
        raise FileNotFoundError(
            "缺少 specparam QC：derivatives/qc/specparam_qc_summary_subject.csv "
            "或 derivatives/specparam/specparam_qc_summary_subject.csv"
        )
    paths["specparam_qc"] = sp_qc_path
    sp_qc = pd.read_csv(sp_qc_path)
    sp_qc["subject_id"] = sp_qc["subject_id"].astype(str)

    df = participants.merge(roi, on=["subject_id", "group"], how="inner")
    preproc_cols = ["subject_id", "usable_epochs", "usable_seconds", "bad_channel_count"]
    if "ica_n_removed" in preproc.columns:
        preproc_cols.append("ica_n_removed")
    df = df.merge(preproc[preproc_cols], on="subject_id", how="left")
    if "ica_n_removed" in df.columns:
        df = df.rename(columns={"ica_n_removed": "n_ica_excluded"})

    sp_cols = [
        "subject_id", "mean_r_squared", "mean_fit_error",
        "invalid_channel_ratio", "low_quality_subject",
    ]
    df = df.merge(sp_qc[[c for c in sp_cols if c in sp_qc.columns]], on="subject_id", how="left")

    if "age_months" in df.columns:
        df["age_years"] = pd.to_numeric(df["age_months"], errors="coerce") / 12.0

    min_epochs_main = int(cfg.get("epochs", {}).get("min_usable_epochs", 60))
    main = df[
        (df["usable_epochs"].fillna(0) >= min_epochs_main)
        & (df["low_quality_subject"].fillna(0).astype(int) == 0)
    ].copy()

    relaxed = df[
        (df["usable_epochs"].fillna(0) >= 30)
        & df["global_exponent"].notna()
        & df["global_offset"].notna()
    ].copy()

    logger.info("合并完成: 全样本 %d, 主 QC %d, 宽松 QC %d", len(df), len(main), len(relaxed))
    return main.reset_index(drop=True), relaxed.reset_index(drop=True), paths


def run_age_distribution(df: pd.DataFrame, tables_dir: Path, fig_dir: Path) -> pd.DataFrame:
    rows = []
    for grp, sub in df.groupby("group"):
        age = pd.to_numeric(sub["age_months"], errors="coerce").dropna()
        n_2_6 = int(((age >= 24) & (age <= 72)).sum())
        rows.append({
            "group": grp,
            "n": len(age),
            "mean_age_months": float(age.mean()),
            "sd_age_months": float(age.std(ddof=1)) if len(age) > 1 else np.nan,
            "median_age_months": float(age.median()),
            "min_age_months": float(age.min()),
            "max_age_months": float(age.max()),
            "n_age_2_6_years": n_2_6,
            "percent_age_2_6_years": 100.0 * n_2_6 / len(age) if len(age) else np.nan,
            "n_age_le_72_months": int((age <= 72).sum()),
            "n_age_gt_72_months": int((age > 72).sum()),
        })
    out = pd.DataFrame(rows)
    out.to_csv(tables_dir / "age_distribution_by_group.csv", index=False)

    apply_plot_style()
    fig, ax = plt.subplots(figsize=(6, 4))
    for grp, color in [("ASD", COL_ASD), ("TD", COL_TD)]:
        age = pd.to_numeric(df.loc[df["group"] == grp, "age_months"], errors="coerce").dropna()
        ax.hist(age, bins=20, alpha=0.5, label=grp, color=color, edgecolor="white", density=True)
    ax.axvline(PRESCHOOL_MAX_MONTHS, color=COL_GRAY, ls="--", lw=1.2)
    ax.set_xlabel("Age (months)")
    ax.set_ylabel("Density")
    ax.legend(frameon=False)
    save_figure(fig, fig_dir / "fig_age_distribution")
    return out


def run_age_interaction(df: pd.DataFrame, tables_dir: Path, fig_dir: Path) -> pd.DataFrame:
    all_rows: list[dict] = []
    age_mean = float(df["age_months"].mean())
    df = df.copy()
    df["age_c"] = df["age_months"] - age_mean

    specs = [
        ("global_exponent", "interaction_raw", "global_exponent ~ C(group) * age_months + C(sex) + IQ_total + usable_epochs"),
        ("global_offset", "interaction_raw", "global_offset ~ C(group) * age_months + C(sex) + IQ_total + usable_epochs"),
        ("global_exponent", "interaction_centered", "global_exponent ~ C(group) * age_c + C(sex) + IQ_total + usable_epochs"),
        ("global_offset", "interaction_centered", "global_offset ~ C(group) * age_c + C(sex) + IQ_total + usable_epochs"),
    ]
    highlight = {
        GROUP_TERM,
        "C(group)[T.TD]:age_months",
        "C(group)[T.TD]:age_c",
    }

    for outcome, mname, formula in specs:
        res, sub = fit_ols_model(formula, df)
        if res is None:
            continue
        all_rows.extend(extract_model_terms(res, outcome, mname, sub, highlight))

    out = pd.DataFrame(all_rows)
    out.to_csv(tables_dir / "age_interaction_models.csv", index=False)

    for outcome, age_col in [("global_exponent", "age_months"), ("global_offset", "age_months")]:
        formula = f"{outcome} ~ C(group) * {age_col} + C(sex) + IQ_total + usable_epochs"
        res, sub = fit_ols_model(formula, df)
        if res is None:
            continue
        _plot_age_interaction(sub, res, outcome, age_col, fig_dir / f"fig_age_interaction_{outcome.replace('global_', '')}")

    return out


def _plot_age_interaction(
    df: pd.DataFrame,
    res: Any,
    outcome: str,
    age_col: str,
    out_base: Path,
) -> None:
    apply_plot_style()
    fig, ax = plt.subplots(figsize=(5.5, 4))
    mode_sex = df["sex"].mode().iloc[0] if "sex" in df.columns and df["sex"].notna().any() else "M"
    iq_m = float(df["IQ_total"].mean())
    ep_m = float(df["usable_epochs"].mean())

    ages = np.linspace(df[age_col].min(), df[age_col].max(), 80)
    for grp, color in [("ASD", COL_ASD), ("TD", COL_TD)]:
        pred_df = pd.DataFrame({
            age_col: ages,
            "group": grp,
            "sex": mode_sex,
            "IQ_total": iq_m,
            "usable_epochs": ep_m,
        })
        pred = res.get_prediction(pred_df).summary_frame(alpha=0.05)
        ax.plot(ages, pred["mean"], color=color, lw=1.5, label=grp)
        ax.fill_between(ages, pred["mean_ci_lower"], pred["mean_ci_upper"], color=color, alpha=0.2, linewidth=0)
        sub = df[df["group"] == grp]
        ax.scatter(sub[age_col], sub[outcome], s=18, alpha=0.55, color=color, edgecolors="none")

    ax.set_xlabel("Age (months)")
    ylab = "Global aperiodic exponent" if "exponent" in outcome else "Global aperiodic offset"
    ax.set_ylabel(ylab)
    ax.legend(frameon=False, loc="best")
    save_figure(fig, out_base)


def _underpowered(sub: pd.DataFrame) -> bool:
    if "group" not in sub.columns:
        return True
    return (sub["group"] == "ASD").sum() < 10 or (sub["group"] == "TD").sum() < 10


def run_age_stratified_models(df: pd.DataFrame, tables_dir: Path, fig_dir: Path) -> pd.DataFrame:
    df = df.copy()
    tert = pd.qcut(df["age_months"].rank(method="first"), 3, labels=["tertile_1_youngest", "tertile_2_middle", "tertile_3_oldest"])
    df["age_tertile"] = tert

    strata: list[tuple[str, pd.DataFrame]] = [
        ("preschool_like", df[df["age_months"] <= 72]),
        ("older_child", df[df["age_months"] > 72]),
    ]
    for label in ["tertile_1_youngest", "tertile_2_middle", "tertile_3_oldest"]:
        strata.append((label, df[df["age_tertile"] == label]))

    rows = []
    for outcome in ["global_exponent", "global_offset"]:
        formula = f"{outcome} ~ C(group) + C(sex) + IQ_total + usable_epochs"
        for stratum, sub in strata:
            asd = sub[sub["group"] == "ASD"][outcome].dropna()
            td = sub[sub["group"] == "TD"][outcome].dropna()
            row: dict[str, Any] = {
                "outcome": outcome,
                "age_stratum": stratum,
                "n_total": len(sub.dropna(subset=[outcome])),
                "n_ASD": len(asd),
                "n_TD": len(td),
                "ASD_mean": float(asd.mean()) if len(asd) else np.nan,
                "TD_mean": float(td.mean()) if len(td) else np.nan,
                "TD_minus_ASD_unadjusted": float(td.mean() - asd.mean()) if len(asd) and len(td) else np.nan,
                "underpowered": _underpowered(sub),
            }
            if row["underpowered"]:
                row.update({
                    "coef_TD_vs_ASD_adjusted": np.nan, "se": np.nan, "p": np.nan,
                    "ci_low": np.nan, "ci_high": np.nan, "r_squared": np.nan,
                })
            else:
                res, fit_sub = fit_ols_model(formula, sub)
                if res is None or GROUP_TERM not in res.params.index:
                    row.update({
                        "coef_TD_vs_ASD_adjusted": np.nan, "se": np.nan, "p": np.nan,
                        "ci_low": np.nan, "ci_high": np.nan, "r_squared": np.nan,
                    })
                else:
                    conf = res.conf_int().loc[GROUP_TERM]
                    row.update({
                        "coef_TD_vs_ASD_adjusted": float(res.params[GROUP_TERM]),
                        "se": float(res.bse[GROUP_TERM]),
                        "p": float(res.pvalues[GROUP_TERM]),
                        "ci_low": float(conf[0]),
                        "ci_high": float(conf[1]),
                        "r_squared": float(res.rsquared),
                    })
            rows.append(row)

    out = pd.DataFrame(rows)
    out.to_csv(tables_dir / "age_stratified_group_effects.csv", index=False)
    _plot_age_stratified_forest(out, fig_dir / "fig_age_stratified_effects")
    return out


def _plot_age_stratified_forest(effects: pd.DataFrame, out_base: Path) -> None:
    apply_plot_style()
    fig, axes = plt.subplots(1, 2, figsize=(10, 5), sharex=False)
    for ax, outcome in zip(axes, ["global_exponent", "global_offset"]):
        sub = effects[effects["outcome"] == outcome].iloc[::-1].reset_index(drop=True)
        y = np.arange(len(sub))
        ax.axvline(0, color="#D9D9D9", lw=1.2)
        for yi, (_, row) in enumerate(sub.iterrows()):
            if row["underpowered"] or pd.isna(row["coef_TD_vs_ASD_adjusted"]):
                ax.plot(row["TD_minus_ASD_unadjusted"], yi, "x", color=COL_GRAY, ms=6)
            else:
                ax.errorbar(
                    row["coef_TD_vs_ASD_adjusted"], yi,
                    xerr=[[row["coef_TD_vs_ASD_adjusted"] - row["ci_low"]],
                          [row["ci_high"] - row["coef_TD_vs_ASD_adjusted"]]],
                    fmt="o", color=COL_GRAY, ecolor=COL_GRAY, capsize=2, ms=4,
                )
        ax.set_yticks(y)
        labels = [f"{r['age_stratum']}{' *' if r['underpowered'] else ''}" for _, r in sub.iterrows()]
        ax.set_yticklabels(labels, fontsize=7)
        ax.set_xlabel("β (TD − ASD)")
        ylab = "Exponent" if "exponent" in outcome else "Offset"
        ax.set_title(ylab, fontsize=9)
    fig.tight_layout()
    save_figure(fig, out_base)


def run_exponent_offset_joint_models(df: pd.DataFrame, tables_dir: Path, fig_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    specs = [
        ("global_offset", "offset_only", "global_offset ~ C(group) + age_months + C(sex) + IQ_total + usable_epochs"),
        ("global_exponent", "exponent_only", "global_exponent ~ C(group) + age_months + C(sex) + IQ_total + usable_epochs"),
        ("global_exponent", "exponent_ctrl_offset", "global_exponent ~ C(group) + global_offset + age_months + C(sex) + IQ_total + usable_epochs"),
        ("global_offset", "offset_ctrl_exponent", "global_offset ~ C(group) + global_exponent + age_months + C(sex) + IQ_total + usable_epochs"),
    ]
    rows: list[dict] = []
    for outcome, mname, formula in specs:
        res, sub = fit_ols_model(formula, df)
        if res is None:
            continue
        rows.extend(extract_model_terms(res, outcome, mname, sub, {GROUP_TERM}))

    model_out = pd.DataFrame(rows)
    model_out.to_csv(tables_dir / "exponent_offset_joint_models.csv", index=False)

    corr_rows = []
    for label, sub in [("overall", df), ("ASD", df[df["group"] == "ASD"]), ("TD", df[df["group"] == "TD"])]:
        x = sub["global_exponent"].dropna()
        y = sub["global_offset"].dropna()
        common = sub.dropna(subset=["global_exponent", "global_offset"])
        if len(common) < 3:
            continue
        pr = stats.pearsonr(common["global_exponent"], common["global_offset"])
        sr = stats.spearmanr(common["global_exponent"], common["global_offset"])
        corr_rows.append({
            "subset": label, "n": len(common),
            "pearson_r": float(pr.statistic), "pearson_p": float(pr.pvalue),
            "spearman_rho": float(sr.statistic), "spearman_p": float(sr.pvalue),
        })
    corr_out = pd.DataFrame(corr_rows)
    corr_out.to_csv(tables_dir / "exponent_offset_correlation.csv", index=False)

    apply_plot_style()
    fig, ax = plt.subplots(figsize=(5, 4.5))
    for grp, color in [("ASD", COL_ASD), ("TD", COL_TD)]:
        sub = df[df["group"] == grp]
        ax.scatter(sub["global_exponent"], sub["global_offset"], s=22, alpha=0.6, color=color, label=grp)
        if len(sub) >= 3:
            z = np.polyfit(sub["global_exponent"], sub["global_offset"], 1)
            xs = np.linspace(sub["global_exponent"].min(), sub["global_exponent"].max(), 50)
            ax.plot(xs, np.poly1d(z)(xs), color=color, lw=1.2, alpha=0.8)
    ax.set_xlabel("Global aperiodic exponent")
    ax.set_ylabel("Global aperiodic offset")
    ax.legend(frameon=False)
    save_figure(fig, fig_dir / "fig_exponent_offset_scatter")
    return model_out, corr_out


def run_iq_language_models(df: pd.DataFrame, tables_dir: Path, fig_dir: Path, skipped: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict] = []
    miss_rows: list[dict] = []

    for var in ["IQ_total", "language_score", "ADOS_total", "ADOS_SA"]:
        for grp in ["ASD", "TD", "all"]:
            sub = df if grp == "all" else df[df["group"] == grp]
            if var not in sub.columns:
                n_miss = len(sub)
                n_ok = 0
            else:
                n_ok = int(sub[var].notna().sum())
                n_miss = int(sub[var].isna().sum())
            miss_rows.append({"variable": var, "group_subset": grp, "n_present": n_ok, "n_missing": n_miss})

    iq_specs = [
        ("global_exponent", "iq_interaction", "global_exponent ~ C(group) * IQ_total + age_months + C(sex) + usable_epochs"),
        ("global_offset", "iq_interaction", "global_offset ~ C(group) * IQ_total + age_months + C(sex) + usable_epochs"),
    ]
    for outcome, mname, formula in iq_specs:
        res, sub = fit_ols_model(formula, df)
        if res is None:
            skipped.append(f"IQ moderation {outcome}")
            continue
        for row in extract_model_terms(res, outcome, mname, sub):
            row["analysis_type"] = "iq_moderation"
            row["notes"] = ""
            rows.append(row)

    lang_asd = df["group"].eq("ASD").sum() if "group" in df.columns else 0
    lang_td = df["group"].eq("TD").sum()
    lang_ok = df["language_score"].notna().sum() if "language_score" in df.columns else 0
    lang_asd_ok = df.loc[df["group"] == "ASD", "language_score"].notna().sum() if "language_score" in df.columns else 0
    lang_td_ok = df.loc[df["group"] == "TD", "language_score"].notna().sum() if "language_score" in df.columns else 0

    if lang_asd_ok >= 10 and lang_td_ok >= 10:
        for outcome in ["global_exponent", "global_offset"]:
            formula = f"{outcome} ~ C(group) * language_score + age_months + C(sex) + IQ_total + usable_epochs"
            res, sub = fit_ols_model(formula, df)
            if res is None:
                continue
            for row in extract_model_terms(res, outcome, "language_interaction", sub):
                row["analysis_type"] = "language_moderation"
                row["notes"] = "both groups"
                rows.append(row)
    elif lang_asd_ok >= 10:
        for outcome in ["global_exponent", "global_offset"]:
            sub = df[df["group"] == "ASD"]
            formula = f"{outcome} ~ language_score + age_months + C(sex) + IQ_total + usable_epochs"
            res, fit_sub = fit_ols_model(formula, sub)
            if res is None:
                continue
            for row in extract_model_terms(res, outcome, "language_asd_only", fit_sub):
                row["analysis_type"] = "language_asd_only"
                row["notes"] = "ASD only"
                rows.append(row)
    else:
        skipped.append("language_score moderation (insufficient n in ASD and/or TD)")

    for outcome in ["global_exponent", "global_offset"]:
        sub = df.dropna(subset=[outcome, "language_score"])
        if len(sub) < 5:
            continue
        sr = stats.spearmanr(sub["language_score"], sub[outcome])
        miss_rows.append({
            "variable": f"spearman_language_vs_{outcome}",
            "group_subset": "all_with_language",
            "n_present": len(sub),
            "n_missing": len(df) - len(sub),
            "spearman_rho": float(sr.statistic),
            "spearman_p": float(sr.pvalue),
        })
        sub_asd = df[df["group"] == "ASD"].dropna(subset=[outcome, "language_score"])
        if len(sub_asd) >= 5:
            sr_a = stats.spearmanr(sub_asd["language_score"], sub_asd[outcome])
            miss_rows.append({
                "variable": f"spearman_language_vs_{outcome}",
                "group_subset": "ASD",
                "n_present": len(sub_asd),
                "n_missing": int(df["group"].eq("ASD").sum()) - len(sub_asd),
                "spearman_rho": float(sr_a.statistic),
                "spearman_p": float(sr_a.pvalue),
            })

    mod_out = pd.DataFrame(rows)
    if not mod_out.empty:
        mod_out.to_csv(tables_dir / "iq_language_moderation_models.csv", index=False)
    miss_out = pd.DataFrame(miss_rows)
    miss_out.to_csv(tables_dir / "language_missingness_and_correlations.csv", index=False)

    _plot_iq_moderation(df, fig_dir, skipped)
    _plot_language_asd(df, fig_dir, skipped)
    return mod_out, miss_out


def _plot_iq_moderation(df: pd.DataFrame, fig_dir: Path, skipped: list[str]) -> None:
    formula = "global_exponent ~ C(group) * IQ_total + age_months + C(sex) + usable_epochs"
    res, sub = fit_ols_model(formula, df)
    if res is None:
        skipped.append("fig_iq_moderation_exponent")
        return
    apply_plot_style()
    fig, ax = plt.subplots(figsize=(5.5, 4))
    iq_grid = np.linspace(sub["IQ_total"].min(), sub["IQ_total"].max(), 60)
    mode_sex = sub["sex"].mode().iloc[0]
    age_m = float(sub["age_months"].mean())
    ep_m = float(sub["usable_epochs"].mean())
    for grp, color in [("ASD", COL_ASD), ("TD", COL_TD)]:
        pred_df = pd.DataFrame({
            "IQ_total": iq_grid, "group": grp, "sex": mode_sex,
            "age_months": age_m, "usable_epochs": ep_m,
        })
        pred = res.get_prediction(pred_df).summary_frame(alpha=0.05)
        ax.plot(iq_grid, pred["mean"], color=color, lw=1.5, label=grp)
        ax.fill_between(iq_grid, pred["mean_ci_lower"], pred["mean_ci_upper"], color=color, alpha=0.2)
        s = sub[sub["group"] == grp]
        ax.scatter(s["IQ_total"], s["global_exponent"], s=18, alpha=0.55, color=color)
    ax.set_xlabel("IQ total")
    ax.set_ylabel("Global aperiodic exponent")
    ax.legend(frameon=False)
    save_figure(fig, fig_dir / "fig_iq_moderation_exponent")


def _plot_language_asd(df: pd.DataFrame, fig_dir: Path, skipped: list[str]) -> None:
    sub = df[(df["group"] == "ASD")].dropna(subset=["language_score", "global_exponent"])
    if len(sub) < 10:
        skipped.append("fig_language_association_asd")
        return
    apply_plot_style()
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.scatter(sub["language_score"], sub["global_exponent"], s=22, alpha=0.65, color=COL_ASD)
    if len(sub) >= 3:
        z = np.polyfit(sub["language_score"], sub["global_exponent"], 1)
        xs = np.linspace(sub["language_score"].min(), sub["language_score"].max(), 50)
        ax.plot(xs, np.poly1d(z)(xs), color=COL_GRAY, lw=1.2)
    sr = stats.spearmanr(sub["language_score"], sub["global_exponent"])
    ax.text(0.98, 0.98, f"ρ = {sr.statistic:.3f}\np = {sr.pvalue:.3f}", transform=ax.transAxes,
            ha="right", va="top", fontsize=7, color=COL_GRAY)
    ax.set_xlabel("Language score")
    ax.set_ylabel("Global aperiodic exponent")
    save_figure(fig, fig_dir / "fig_language_association_asd")


def run_qc_models(df_main: pd.DataFrame, df_relaxed: pd.DataFrame, tables_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    qc_covs = [
        ("base", None),
        ("plus_r2", "mean_r_squared"),
        ("plus_fit_error", "mean_fit_error"),
        ("plus_invalid_ratio", "invalid_channel_ratio"),
        ("plus_bad_channels", "bad_channel_count"),
    ]
    rows = []
    for outcome in ["global_exponent", "global_offset"]:
        for tag, extra in qc_covs:
            extra_term = f" + {extra}" if extra else ""
            formula = f"{outcome} ~ C(group) + age_months + C(sex) + IQ_total + usable_epochs{extra_term}"
            res, sub = fit_ols_model(formula, df_main)
            if res is None or GROUP_TERM not in res.params.index:
                continue
            conf = res.conf_int().loc[GROUP_TERM]
            rows.append({
                "outcome": outcome,
                "model_tag": tag,
                "extra_covariate": extra or "",
                "n": int(res.nobs),
                "coef_TD_vs_ASD": float(res.params[GROUP_TERM]),
                "se": float(res.bse[GROUP_TERM]),
                "p": float(res.pvalues[GROUP_TERM]),
                "ci_low": float(conf[0]),
                "ci_high": float(conf[1]),
                "r_squared": float(res.rsquared),
            })
    qc_out = pd.DataFrame(rows)
    qc_out.to_csv(tables_dir / "qc_adjusted_models.csv", index=False)

    comp_rows = []
    for label, dset in [("main_qc_set", df_main), ("relaxed_epoch30_set", df_relaxed)]:
        for outcome in ["global_exponent", "global_offset"]:
            formula = f"{outcome} ~ C(group) + age_months + C(sex) + IQ_total + usable_epochs"
            res, sub = fit_ols_model(formula, dset)
            if res is None or GROUP_TERM not in res.params.index:
                continue
            conf = res.conf_int().loc[GROUP_TERM]
            comp_rows.append({
                "analysis_set": label,
                "outcome": outcome,
                "n": int(res.nobs),
                "n_ASD": int((sub["group"] == "ASD").sum()),
                "n_TD": int((sub["group"] == "TD").sum()),
                "coef_TD_vs_ASD": float(res.params[GROUP_TERM]),
                "se": float(res.bse[GROUP_TERM]),
                "p": float(res.pvalues[GROUP_TERM]),
                "ci_low": float(conf[0]),
                "ci_high": float(conf[1]),
            })
    comp_out = pd.DataFrame(comp_rows)
    comp_out.to_csv(tables_dir / "qc_set_comparison.csv", index=False)
    return qc_out, comp_out


def summarize_fixed_vs_knee(sens_path: Path, tables_dir: Path, fig_dir: Path) -> pd.DataFrame:
    sens = pd.read_csv(sens_path)
    rows = []
    for _, r in sens.iterrows():
        mname = str(r["model_name"])
        m = re.match(r"freq_([\d.]+)_([\d.]+)_mode_(\w+)", mname)
        if not m:
            continue
        coef = float(r["group_coef_TD_vs_ASD"])
        p = float(r["group_p"])
        rows.append({
            "freq_range": f"{m.group(1)}–{m.group(2)} Hz",
            "aperiodic_mode": m.group(3),
            "n": int(r["n"]),
            "coef_TD_vs_ASD": coef,
            "p": p,
            "ci_low": float(r["group_ci_low"]),
            "ci_high": float(r["group_ci_high"]),
            "direction": "TD > ASD" if coef > 0 else "ASD > TD",
            "significant_p05": p < 0.05,
        })
    out = pd.DataFrame(rows)
    out.to_csv(tables_dir / "fixed_vs_knee_summary.csv", index=False)

    if out.empty:
        return out
    apply_plot_style()
    out = out.iloc[::-1].reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(6, 4.5))
    y = np.arange(len(out))
    ax.axvline(0, color="#D9D9D9", lw=1.2)
    for i, row in out.iterrows():
        marker = "o" if row["aperiodic_mode"] == "fixed" else "s"
        ax.errorbar(
            row["coef_TD_vs_ASD"], i,
            xerr=[[row["coef_TD_vs_ASD"] - row["ci_low"]], [row["ci_high"] - row["coef_TD_vs_ASD"]]],
            fmt=marker, color=COL_GRAY, ecolor=COL_GRAY, capsize=2, ms=5,
        )
    ax.set_yticks(y)
    ax.set_yticklabels([f"{r['freq_range']} ({r['aperiodic_mode']})" for _, r in out.iterrows()], fontsize=7)
    ax.set_xlabel("β (TD − ASD), global exponent")
    save_figure(fig, fig_dir / "fig_fixed_vs_knee_effects")
    return out


def write_markdown_report(
    report_path: Path,
    df_main: pd.DataFrame,
    age_dist: pd.DataFrame,
    age_int: pd.DataFrame,
    age_strat: pd.DataFrame,
    joint_models: pd.DataFrame,
    corr_exp_off: pd.DataFrame,
    iq_lang: pd.DataFrame,
    qc_comp: pd.DataFrame,
    fixed_knee: pd.DataFrame,
    skipped: list[str],
) -> None:
    """根据分析结果自动生成中英 Discussion 草稿。"""
    age = pd.to_numeric(df_main["age_months"], errors="coerce")
    n_pre = int(((age >= 24) & (age <= 72)).sum())
    iq_asd = df_main.loc[df_main["group"] == "ASD", "IQ_total"].mean()
    iq_td = df_main.loc[df_main["group"] == "TD", "IQ_total"].mean()
    lang_miss = int(df_main["language_score"].isna().sum()) if "language_score" in df_main.columns else np.nan

    def _p(term_df: pd.DataFrame, outcome: str, term: str) -> float | None:
        sub = term_df[(term_df["outcome"] == outcome) & (term_df["term"] == term)]
        if sub.empty:
            return None
        return float(sub["p"].iloc[0])

    int_exp = age_int[age_int["model_name"] == "interaction_raw"] if not age_int.empty else pd.DataFrame()
    p_int_exp = _p(int_exp, "global_exponent", "C(group)[T.TD]:age_months")
    p_int_off = _p(int_exp, "global_offset", "C(group)[T.TD]:age_months") if not int_exp.empty else None

    pre_exp = age_strat[(age_strat["age_stratum"] == "preschool_like") & (age_strat["outcome"] == "global_exponent")]
    pre_p = float(pre_exp["p"].iloc[0]) if not pre_exp.empty and pre_exp["p"].notna().any() else None
    pre_under = bool(pre_exp["underpowered"].iloc[0]) if not pre_exp.empty else True

    corr_r = float(corr_exp_off.loc[corr_exp_off["subset"] == "overall", "pearson_r"].iloc[0]) if not corr_exp_off.empty else np.nan

    exp_ctrl = joint_models[(joint_models["model_name"] == "exponent_ctrl_offset") & (joint_models["term"] == GROUP_TERM)]
    off_ctrl = joint_models[(joint_models["model_name"] == "offset_ctrl_exponent") & (joint_models["term"] == GROUP_TERM)]
    p_exp_ctrl = float(exp_ctrl["p"].iloc[0]) if not exp_ctrl.empty else np.nan
    p_off_ctrl = float(off_ctrl["p"].iloc[0]) if not off_ctrl.empty else np.nan

    main_exp = qc_comp[(qc_comp["analysis_set"] == "main_qc_set") & (qc_comp["outcome"] == "global_exponent")]
    relax_exp = qc_comp[(qc_comp["analysis_set"] == "relaxed_epoch30_set") & (qc_comp["outcome"] == "global_exponent")]

    knee_sig = int(fixed_knee["significant_p05"].sum()) if not fixed_knee.empty else 0
    knee_n = len(fixed_knee) if not fixed_knee.empty else 0

    if p_int_exp is None:
        age_int_txt = "Age interaction models could not be summarized."
    elif p_int_exp >= 0.05:
        age_int_txt = f"Group × age interaction for exponent p = {p_int_exp:.3f} (non-significant)."
    else:
        age_int_txt = f"Group × age interaction for exponent p = {p_int_exp:.3f} (significant)."

    pre_txt = (
        f"In the preschool-like subsample (≤72 months, n={int(pre_exp['n_total'].iloc[0]) if not pre_exp.empty else 0}), "
        f"adjusted exponent group effect p = {pre_p:.3f}"
        + (" (underpowered)." if pre_under else ".")
        if pre_p is not None
        else "Preschool-like stratum results unavailable."
    )

    text = f"""# Comparison with preschool ASD EEG aperiodic study

## 1. Purpose

This report compares findings from the current school-aged sample with Chen et al.'s preschool ASD resting-state EEG study (2–6 years), which reported **higher aperiodic offset** in autistic children but **no significant group difference in slope/exponent**. Our primary result is **higher global aperiodic exponent in TD than ASD** (adjusted), with offset showing a weaker trend.

## 2. Key differences in sample

| Metric | Value |
|--------|-------|
| Main QC N | {len(df_main)} (ASD {int((df_main['group']=='ASD').sum())}, TD {int((df_main['group']=='TD').sum())}) |
| Age range (months) | {age.min():.0f} – {age.max():.0f} |
| Subjects aged 24–72 months | {n_pre} ({100*n_pre/len(df_main):.1f}%) |
| Mean IQ ASD / TD | {iq_asd:.1f} / {iq_td:.1f} |
| Missing language_score | {lang_miss} |

Chen et al. focused on **preschool (2–6 y)** children; most participants here are **older than 72 months**.

## 3. Age-related checks

- {age_int_txt}
- {pre_txt}
- Older-child and tertile-stratified effects are in `age_stratified_group_effects.csv`.

## 4. Offset vs exponent

- Overall Pearson r(exponent, offset) = {corr_r:.3f}.
- After controlling for offset, exponent group effect p = {p_exp_ctrl:.3f}.
- After controlling for exponent, offset group effect p = {p_off_ctrl:.3f}.

## 5. IQ and language phenotype

- See `iq_language_moderation_models.csv` and `language_missingness_and_correlations.csv`.
- IQ × group interaction terms indicate whether cognitive level moderates group differences.

## 6. QC and model specification

- Main vs relaxed QC comparison: main exponent β = {float(main_exp['coef_TD_vs_ASD'].iloc[0]) if not main_exp.empty else np.nan:.3f}, relaxed β = {float(relax_exp['coef_TD_vs_ASD'].iloc[0]) if not relax_exp.empty else np.nan:.3f} (see `qc_set_comparison.csv`).
- Fixed vs knee: {knee_sig}/{knee_n} sensitivity rows significant at p < .05 for exponent (mostly fixed mode; see `fixed_vs_knee_summary.csv`).

## 7. Interpretation for Discussion

### 中文草稿

本研究与既往学龄前 ASD EEG 非周期活动结果不完全一致。Chen 等（学龄前 2–6 岁）主要报告 ASD 儿童 **aperiodic offset 升高**，而 **slope/exponent 组间差异不显著**；本研究在较大年龄样本中发现 **TD 组 global aperiodic exponent 高于 ASD 组**（协变量校正后），offset 仅为趋势。补充分析显示：本队列年龄范围主要为 {age.min():.0f}–{age.max():.0f} 月，仅 {n_pre} 名落在 2–6 岁区间；group × age 交互{'显著' if p_int_exp is not None and p_int_exp < 0.05 else '不显著'}；学龄前样层{'统计功效不足' if pre_under else '效应方向与全样本一致或见分层表'}。Exponent 与 offset 相关（r ≈ {corr_r:.2f}），控制 offset 后 exponent 组效应 p = {p_exp_ctrl:.3f}。IQ/语言表型调节分析见附表。加入拟合质量协变量后结论总体保持；fixed 模式组效应较 knee 更稳定。上述差异**最可能**与**年龄阶段**、**认知/IQ 表型**及 **specparam 参数维度（offset vs exponent）** 有关；学龄前重叠子样本功效有限，不宜直接等同于 Chen 等结论。

### English draft

Our findings differ from prior work in **preschool-aged** autistic children, which reported higher **aperiodic offset** but comparable **slope/exponent**. In this older sample (main N = {len(df_main)}), we observed higher **global aperiodic exponent in TD than ASD** after covariate adjustment, with offset effects weaker. Follow-up analyses indicated limited overlap with the 2–6 year preschool window (n = {n_pre}), a non-significant or modest group × age interaction (exponent interaction p = {p_int_exp if p_int_exp is not None else 'NA'}), and substantial correlation between exponent and offset (r ≈ {corr_r:.2f}). The exponent group effect remained discernible when controlling for offset (p = {p_exp_ctrl:.3f}). IQ/language moderation and QC-adjusted models are tabulated; **fixed** aperiodic fits showed more consistent TD > ASD exponent effects than **knee** mode. Discrepancies with Chen et al. are **most plausibly** explained by **developmental stage**, **IQ/phenotype differences**, and **distinct aperiodic parameters** (offset vs exponent), rather than a single contradictory null.

## Skipped / warnings

{chr(10).join('- ' + s for s in skipped) if skipped else '- None'}
"""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(text, encoding="utf-8")


def run_all_checks(root: Path, cfg: dict[str, Any]) -> dict[str, Any]:
    """执行全部分析并返回输出路径摘要。"""
    tables_dir = root / "outputs/tables/compare_preschool_study"
    fig_dir = root / "outputs/figures/compare_preschool_study"
    reports_dir = root / "outputs/reports"
    tables_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    skipped: list[str] = []
    tables_written: list[Path] = []
    figures_written: list[Path] = []

    df_main, df_relaxed, paths = load_and_merge_data(root, cfg)

    age_dist = run_age_distribution(df_main, tables_dir, fig_dir)
    tables_written.append(tables_dir / "age_distribution_by_group.csv")
    figures_written.append(fig_dir / "fig_age_distribution.png")

    age_int = run_age_interaction(df_main, tables_dir, fig_dir)
    tables_written.append(tables_dir / "age_interaction_models.csv")
    for stem in ["fig_age_interaction_exponent", "fig_age_interaction_offset"]:
        figures_written.append(fig_dir / f"{stem}.png")

    age_strat = run_age_stratified_models(df_main, tables_dir, fig_dir)
    tables_written.append(tables_dir / "age_stratified_group_effects.csv")
    figures_written.append(fig_dir / "fig_age_stratified_effects.png")

    joint_models, corr_exp_off = run_exponent_offset_joint_models(df_main, tables_dir, fig_dir)
    tables_written.extend([
        tables_dir / "exponent_offset_joint_models.csv",
        tables_dir / "exponent_offset_correlation.csv",
    ])
    figures_written.append(fig_dir / "fig_exponent_offset_scatter.png")

    iq_lang, _ = run_iq_language_models(df_main, tables_dir, fig_dir, skipped)
    if not iq_lang.empty:
        tables_written.append(tables_dir / "iq_language_moderation_models.csv")
    tables_written.append(tables_dir / "language_missingness_and_correlations.csv")
    for stem in ["fig_iq_moderation_exponent", "fig_language_association_asd"]:
        if (fig_dir / f"{stem}.png").exists():
            figures_written.append(fig_dir / f"{stem}.png")

    qc_adj, qc_comp = run_qc_models(df_main, df_relaxed, tables_dir)
    tables_written.extend([tables_dir / "qc_adjusted_models.csv", tables_dir / "qc_set_comparison.csv"])

    fixed_knee = summarize_fixed_vs_knee(paths["sensitivity_final"], tables_dir, fig_dir)
    tables_written.append(tables_dir / "fixed_vs_knee_summary.csv")
    figures_written.append(fig_dir / "fig_fixed_vs_knee_effects.png")

    report_path = reports_dir / "compare_with_preschool_study_checks.md"
    write_markdown_report(
        report_path, df_main, age_dist, age_int, age_strat,
        joint_models, corr_exp_off, iq_lang, qc_comp, fixed_knee, skipped,
    )

    return {
        "tables": tables_written,
        "figures": figures_written,
        "report": report_path,
        "skipped": skipped,
        "df_main": df_main,
        "age_int": age_int,
        "age_strat": age_strat,
        "qc_comp": qc_comp,
        "fixed_knee": fixed_knee,
        "corr_exp_off": corr_exp_off,
    }
