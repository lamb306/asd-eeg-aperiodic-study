#!/usr/bin/env python
"""
88_variational_free_energy_coupling_both_postqc.py
--------------------------------------------------
变分/预测编码框架下的跨状态耦合分析（严格 both_postqc 队列，34 ASD vs 34 TD）。

数据来源：
  - 队列：data/participants/participants_resting_movie_matched_postqc.csv
  - 电影：derivatives_task_movie_both_postqc
  - 静息：derivatives_matched_postqc（与 69 脚本 both 交集一致）

三个模块（均输出 OLS + RLM/Winsor）：
  1) Primary state coupling: ISC ~ resting_posterior_exponent * group + covariates
     （neutral 为主，mental/pain 为对照）
  2) Cost of transition: neutral_isc ~ delta_exp * group + covariates
     delta_exp = movie_posterior_mean - resting_posterior_exponent
  3) Path / mediation: resting_exp -> delta_exp -> neutral_isc（路径系数 + bootstrap 间接效应）
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import pearsonr, spearmanr

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config, setup_logging  # noqa: E402
from src.io_utils import save_csv  # noqa: E402

COHORT_FILE = PROJECT_ROOT / "data/participants/participants_resting_movie_matched_postqc.csv"
RESTING_DERIV = PROJECT_ROOT / "derivatives_matched_postqc"
MOVIE_CONFIG = PROJECT_ROOT / "config/config_task_movie_both_postqc.yaml"

COVARIATES_NUM = ("age_months", "IQ_total", "usable_epochs")
COVARIATES_CAT = ("sex",)
EVENTS_PRIMARY = ("neutral",)
EVENTS_SECONDARY = ("mental", "pain")
GROUP_TERM_SUFFIX = "C(group)[T.TD]"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="VFE coupling analysis on both_postqc cohort")
    p.add_argument("--config", default=str(MOVIE_CONFIG))
    p.add_argument("--n-bootstrap", type=int, default=2000)
    p.add_argument("--random-seed", type=int, default=42)
    return p.parse_args()


def winsorize_series(s: pd.Series, lo: float = 0.05, hi: float = 0.95) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce")
    finite = x.dropna()
    if finite.empty:
        return x
    return x.clip(lower=float(finite.quantile(lo)), upper=float(finite.quantile(hi)))


def _covariate_terms(df: pd.DataFrame) -> list[str]:
    terms = list(COVARIATES_NUM)
    if "sex" in df.columns and df["sex"].notna().any():
        terms.append("C(sex)")
    return [t for t in terms if t in df.columns or t.startswith("C(")]


def build_formula(
    outcome: str,
    core_terms: list[str],
    df: pd.DataFrame,
) -> str:
    parts = list(core_terms) + _covariate_terms(df)
    return f"{outcome} ~ " + " + ".join(parts)


def fit_ols(formula: str, df: pd.DataFrame) -> tuple[Any, pd.DataFrame]:
    model = smf.ols(formula, data=df).fit()
    tab = model.summary2().tables[1].reset_index().rename(columns={"index": "term"})
    tab["n_obs"] = int(model.nobs)
    tab["r_squared"] = float(model.rsquared)
    tab["adj_r_squared"] = float(model.rsquared_adj)
    tab["formula"] = formula
    return model, tab


def fit_rlm_winsor(formula: str, df: pd.DataFrame) -> tuple[Any, pd.DataFrame, str]:
    """将公式中的非 C() 变量名做 winsorize（带 _w 后缀）。"""
    import re

    resp, rhs = formula.split("~", 1)
    resp = resp.strip()
    w_df = df.copy()
    w_formula_parts: list[str] = []
    for raw in rhs.split("+"):
        term = raw.strip()
        if term.startswith("C("):
            w_formula_parts.append(term)
            continue
        if ":" in term:
            left, right = term.split(":", 1)
            for side in (left.strip(), right.strip()):
                if side not in w_df.columns:
                    wname = f"{side}_w"
                    if wname not in w_df.columns and side in w_df.columns:
                        w_df[wname] = winsorize_series(w_df[side])
            w_formula_parts.append(
                term.replace(left.strip(), f"{left.strip()}_w").replace(
                    right.strip(), f"{right.strip()}_w"
                )
            )
        else:
            base = re.sub(r"\[.*\]", "", term).strip()
            if base in w_df.columns:
                wname = f"{base}_w"
                if wname not in w_df.columns:
                    w_df[wname] = winsorize_series(w_df[base])
                w_formula_parts.append(term.replace(base, wname))
            else:
                w_formula_parts.append(term)
    w_formula = f"{resp}_w ~ " + " + ".join(w_formula_parts)
    if f"{resp}_w" not in w_df.columns and resp in w_df.columns:
        w_df[f"{resp}_w"] = winsorize_series(w_df[resp])
    model = smf.rlm(w_formula, w_df, M=sm.robust.norms.HuberT()).fit()
    tab = pd.DataFrame(
        {
            "term": model.params.index,
            "coef": model.params.values,
            "std_err": model.bse.values,
            "z": model.tvalues.values,
            "pvalue": model.pvalues.values,
        }
    )
    tab["n_obs"] = int(len(w_df))
    tab["formula"] = w_formula
    return model, tab, w_formula


def _interaction_row(tab: pd.DataFrame, pattern: str) -> dict[str, Any]:
    hit = tab[tab["term"].astype(str).str.contains(pattern, regex=False)]
    if hit.empty:
        return {"term": pattern, "coef": np.nan, "pvalue": np.nan}
    row = hit.iloc[0]
    pcol = "pvalue" if "pvalue" in row else ("P>|t|" if "P>|t|" in row else "P>|z|")
    return {
        "term": str(row["term"]),
        "coef": float(row.get("coef", row.get("Coef.", np.nan))),
        "pvalue": float(row[pcol]) if pcol in row.index else np.nan,
    }


def run_coupling_models(
    df: pd.DataFrame,
    outcome_col: str,
    predictor_col: str,
    module: str,
    event_type: str,
    analysis_tier: str,
) -> list[dict[str, Any]]:
    """ISC ~ predictor * group + covariates。"""
    sub = df.dropna(
        subset=[outcome_col, predictor_col, "group", "age_months", "usable_epochs"]
        + (["IQ_total"] if "IQ_total" in df.columns else [])
        + (["sex"] if "sex" in df.columns else [])
    ).copy()
    if "IQ_total" in sub.columns:
        sub = sub.dropna(subset=["IQ_total"])
    if len(sub) < 12 or sub["group"].nunique() < 2:
        return []

    core = [f"{predictor_col} * C(group)"]
    formula = build_formula(outcome_col, core, sub)
    rows: list[dict[str, Any]] = []

    _, ols_tab = fit_ols(formula, sub)
    inter = _interaction_row(ols_tab, f"{predictor_col}:{GROUP_TERM_SUFFIX}")
    rows.append(
        {
            "module": module,
            "analysis_tier": analysis_tier,
            "event_type": event_type,
            "estimator": "OLS",
            "outcome": outcome_col,
            "predictor": predictor_col,
            "n_obs": int(ols_tab["n_obs"].iloc[0]),
            "r_squared": float(ols_tab["r_squared"].iloc[0]),
            "interaction_term": inter["term"],
            "beta_interaction_TD_minus_ASD_slope_mod": inter["coef"],
            "p_interaction": inter["pvalue"],
            "formula": formula,
        }
    )

    _, rlm_tab, rlm_formula = fit_rlm_winsor(formula, sub)
    pat = f"{predictor_col}_w:{GROUP_TERM_SUFFIX}"
    if not (rlm_tab["term"].astype(str) == pat).any():
        pat = f"{predictor_col}_w:C(group)[T.TD]"
    inter_r = _interaction_row(rlm_tab, pat.replace("_w", "").split(":")[0] + "_w:")
    if np.isnan(inter_r["coef"]):
        inter_r = _interaction_row(rlm_tab, "C(group)[T.TD]")
    rows.append(
        {
            "module": module,
            "analysis_tier": analysis_tier,
            "event_type": event_type,
            "estimator": "RLM_Winsor",
            "outcome": outcome_col,
            "predictor": predictor_col,
            "n_obs": int(rlm_tab["n_obs"].iloc[0]),
            "r_squared": np.nan,
            "interaction_term": inter_r["term"],
            "beta_interaction_TD_minus_ASD_slope_mod": inter_r["coef"],
            "p_interaction": inter_r["pvalue"],
            "formula": rlm_formula,
        }
    )
    return rows


def run_path_regressions(df: pd.DataFrame) -> pd.DataFrame:
    """路径 a/b/c/c' + 组别交互（探索组别在哪一步偏离）。"""
    need = [
        "neutral_isc_z",
        "resting_posterior_exponent",
        "delta_exp",
        "group",
        "age_months",
        "usable_epochs",
    ]
    if "IQ_total" in df.columns:
        need.append("IQ_total")
    sub = df.dropna(subset=[c for c in need if c in df.columns]).copy()
    if "sex" in sub.columns:
        sub = sub.dropna(subset=["sex"])

    cov = " + ".join(_covariate_terms(sub))
    specs = [
        ("path_a", "delta_exp", f"resting_posterior_exponent * C(group) + {cov}"),
        ("path_a_total", "delta_exp", f"resting_posterior_exponent + C(group) + {cov}"),
        ("path_b", "neutral_isc_z", f"delta_exp * C(group) + resting_posterior_exponent + {cov}"),
        ("path_c_total", "neutral_isc_z", f"resting_posterior_exponent * C(group) + {cov}"),
        ("path_c_prime", "neutral_isc_z", f"delta_exp + resting_posterior_exponent + C(group) + {cov}"),
    ]
    rows = []
    for path_id, outcome, rhs in specs:
        formula = f"{outcome} ~ {rhs}"
        for est_name, fitter in (("OLS", fit_ols),):
            try:
                _, tab = fitter(formula, sub)
            except Exception as exc:
                rows.append(
                    {
                        "path_id": path_id,
                        "estimator": est_name,
                        "error": str(exc),
                    }
                )
                continue
            for _, r in tab.iterrows():
                rows.append(
                    {
                        "path_id": path_id,
                        "estimator": est_name,
                        "outcome": outcome,
                        "term": r["term"],
                        "coef": r.get("Coef.", r.get("coef", np.nan)),
                        "std_err": r.get("Std.Err.", r.get("std_err", np.nan)),
                        "pvalue": r.get("P>|t|", r.get("pvalue", np.nan)),
                        "n_obs": int(r["n_obs"]),
                        "r_squared": r.get("r_squared", np.nan),
                        "formula": formula,
                    }
                )
        try:
            _, rlm_tab, rlm_formula = fit_rlm_winsor(formula, sub)
            for _, r in rlm_tab.iterrows():
                rows.append(
                    {
                        "path_id": path_id,
                        "estimator": "RLM_Winsor",
                        "outcome": outcome,
                        "term": r["term"],
                        "coef": r["coef"],
                        "std_err": r["std_err"],
                        "pvalue": r["pvalue"],
                        "n_obs": int(r["n_obs"]),
                        "r_squared": np.nan,
                        "formula": rlm_formula,
                    }
                )
        except Exception as exc:
            rows.append({"path_id": path_id, "estimator": "RLM_Winsor", "error": str(exc)})
    return pd.DataFrame(rows)


def bootstrap_indirect_effect(
    df: pd.DataFrame,
    n_boot: int,
    seed: int,
) -> pd.DataFrame:
    """间接效应 ab：resting -> delta_exp -> neutral_isc（控制协变量，不含量化交互）。"""
    cov = _covariate_terms(df)
    cov_rhs = " + ".join(cov) if cov else "1"
    sub = df.dropna(
        subset=["neutral_isc_z", "resting_posterior_exponent", "delta_exp", "group"]
        + list(COVARIATES_NUM)
        + (["sex"] if "sex" in df.columns else [])
    ).copy()

    rng = np.random.default_rng(seed)
    boots: list[float] = []
    n = len(sub)
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        samp = sub.iloc[idx].copy()
        if samp["group"].nunique() < 2:
            continue
        try:
            ma = smf.ols(f"delta_exp ~ resting_posterior_exponent + C(group) + {cov_rhs}", samp).fit()
            mb = smf.ols(
                f"neutral_isc_z ~ delta_exp + resting_posterior_exponent + C(group) + {cov_rhs}",
                samp,
            ).fit()
            a = float(ma.params.get("resting_posterior_exponent", np.nan))
            b = float(mb.params.get("delta_exp", np.nan))
            if np.isfinite(a) and np.isfinite(b):
                boots.append(a * b)
        except Exception:
            continue
    valid = np.asarray(boots, dtype=float)
    if len(valid) == 0:
        return pd.DataFrame(
            [
                {
                    "n_bootstrap": n_boot,
                    "n_valid": 0,
                    "indirect_ab_mean": np.nan,
                    "ci95_low": np.nan,
                    "ci95_high": np.nan,
                    "p_two_sided": np.nan,
                }
            ]
        )
    ci_low, ci_high = np.quantile(valid, [0.025, 0.975])
    p_two = 2.0 * min(np.mean(valid <= 0), np.mean(valid >= 0))
    return pd.DataFrame(
        [
            {
                "n_bootstrap": n_boot,
                "n_valid": int(len(valid)),
                "indirect_ab_mean": float(np.mean(valid)),
                "indirect_ab_median": float(np.median(valid)),
                "ci95_low": float(ci_low),
                "ci95_high": float(ci_high),
                "p_two_sided": float(min(1.0, p_two)),
            }
        ]
    )


def partial_correlation_table(df: pd.DataFrame) -> pd.DataFrame:
    """偏相关探索：控制 age_months, IQ, sex（残差化）。"""
    from numpy.linalg import lstsq

    sub = df.dropna(
        subset=[
            "neutral_isc_z",
            "resting_posterior_exponent",
            "delta_exp",
            "age_months",
            "IQ_total",
            "usable_epochs",
            "group",
        ]
    ).copy()
    if sub.empty:
        return pd.DataFrame()

    def residualize(y: pd.Series, x_cov: pd.DataFrame) -> np.ndarray:
        x = sm.add_constant(x_cov.astype(float), has_constant="add")
        yv = pd.to_numeric(y, errors="coerce").to_numpy(dtype=float)
        beta, _, _, _ = lstsq(x.to_numpy(dtype=float), yv, rcond=None)
        return yv - x.to_numpy(dtype=float) @ beta

    x_cov = pd.get_dummies(
        sub[["age_months", "IQ_total", "usable_epochs", "sex", "group"]].astype(
            {"sex": "category", "group": "category"}
        ),
        drop_first=True,
    )
    rows = []
    pairs = [
        ("resting_posterior_exponent", "delta_exp", "path_a_partial"),
        ("delta_exp", "neutral_isc_z", "path_b_partial"),
        ("resting_posterior_exponent", "neutral_isc_z", "path_c_partial"),
    ]
    for xname, yname, label in pairs:
        rx = residualize(sub[xname], x_cov)
        ry = residualize(sub[yname], x_cov)
        r, p = pearsonr(rx, ry)
        rho, p_s = spearmanr(rx, ry)
        rows.append(
            {
                "contrast": label,
                "x": xname,
                "y": yname,
                "pearson_r": float(r),
                "pearson_p": float(p),
                "spearman_rho": float(rho),
                "spearman_p": float(p_s),
                "n": int(len(sub)),
            }
        )
    # 控制 resting 后 delta -> neutral
    rx = residualize(sub["delta_exp"], x_cov.assign(rest=sub["resting_posterior_exponent"]))
    ry = residualize(
        sub["neutral_isc_z"],
        x_cov.assign(rest=sub["resting_posterior_exponent"]),
    )
    r, p = pearsonr(rx, ry)
    rho, p_s = spearmanr(rx, ry)
    rows.append(
        {
            "contrast": "path_b_given_resting_partial",
            "x": "delta_exp",
            "y": "neutral_isc_z",
            "pearson_r": float(r),
            "pearson_p": float(p),
            "spearman_rho": float(rho),
            "spearman_p": float(p_s),
            "n": int(len(sub)),
        }
    )
    return pd.DataFrame(rows)


def load_both_postqc_merged() -> tuple[pd.DataFrame, pd.DataFrame]:
    """构建分析宽表 + 队列清单。"""
    cohort = pd.read_csv(COHORT_FILE)
    cohort["subject_id"] = cohort["subject_id"].astype(str)
    cohort["group"] = cohort["group"].astype(str).str.upper()
    cohort_ids = cohort[["subject_id", "group"]].drop_duplicates()

    # 静息后部 exponent（matched_postqc ROI）
    roi = pd.read_csv(RESTING_DERIV / "roi/specparam_subject_roi_long.csv")
    roi = roi[roi["roi"].isin(["parietal", "occipital"])].copy()
    rest = (
        roi.groupby(["subject_id", "group"], as_index=False)["exponent"]
        .mean()
        .rename(columns={"exponent": "resting_posterior_exponent"})
    )
    rest["subject_id"] = rest["subject_id"].astype(str)
    rest["group"] = rest["group"].astype(str).str.upper()

    cfg = load_config(MOVIE_CONFIG)
    mov_deriv = Path(cfg["paths"]["derivatives_root"])

    # 电影事件 exponent
    mov_exp = pd.read_csv(mov_deriv / "stats/movie_event_subject_condition_means.csv")
    mov_exp = mov_exp[mov_exp["event_type"].isin(["mental", "pain", "neutral"])].copy()
    mov_exp["subject_id"] = mov_exp["subject_id"].astype(str)
    mov_exp["group"] = mov_exp["group"].astype(str).str.upper()
    exp_wide = mov_exp.pivot_table(
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
        }
    )
    exp_wide["movie_posterior_mean"] = exp_wide[
        ["movie_mental_exponent", "movie_pain_exponent", "movie_neutral_exponent"]
    ].mean(axis=1)

    # ISC
    isc = pd.read_csv(mov_deriv / "stats/movie_isc_subject_values_with_neutral.csv")
    isc = isc[["subject_id", "group", "event_type", "isc_z", "isc_r"]].copy()
    isc["subject_id"] = isc["subject_id"].astype(str)
    isc["group"] = isc["group"].astype(str).str.upper()
    isc["event_type"] = isc["event_type"].astype(str).str.lower()
    isc_wide = isc.pivot_table(
        index=["subject_id", "group"],
        columns="event_type",
        values="isc_z",
        aggfunc="mean",
    ).reset_index()
    isc_wide.columns.name = None
    isc_wide = isc_wide.rename(
        columns={
            "mental": "mental_isc_z",
            "pain": "pain_isc_z",
            "neutral": "neutral_isc_z",
        }
    )

    # 电影 QC / epoch
    pre = pd.read_csv(mov_deriv / "qc/preproc_summary.csv")[["subject_id", "usable_epochs"]]
    pre["subject_id"] = pre["subject_id"].astype(str)
    mq_path = mov_deriv / "specparam/specparam_qc_summary_subject.csv"
    bad: set[str] = set()
    if mq_path.exists():
        mq = pd.read_csv(mq_path)
        mq["subject_id"] = mq["subject_id"].astype(str)
        bad = set(
            mq.loc[pd.to_numeric(mq["low_quality_subject"], errors="coerce") == 1, "subject_id"]
        )

    merged = cohort[
        ["subject_id", "group", "sex", "age_months", "IQ_total", "matched_pair_id"]
    ].drop_duplicates()
    merged = merged.merge(cohort_ids, on=["subject_id", "group"], how="inner")
    merged = merged.merge(rest, on=["subject_id", "group"], how="inner")
    merged = merged.merge(exp_wide, on=["subject_id", "group"], how="inner")
    merged = merged.merge(isc_wide, on=["subject_id", "group"], how="inner")
    merged = merged.merge(pre, on="subject_id", how="left")
    merged["delta_exp"] = merged["movie_posterior_mean"] - merged["resting_posterior_exponent"]
    merged["delta_exp_neutral"] = merged["movie_neutral_exponent"] - merged["resting_posterior_exponent"]
    if bad:
        merged = merged[~merged["subject_id"].isin(bad)].copy()

    for col in (
        "resting_posterior_exponent",
        "movie_posterior_mean",
        "movie_neutral_exponent",
        "delta_exp",
        "neutral_isc_z",
        "mental_isc_z",
        "pain_isc_z",
        "age_months",
        "IQ_total",
        "usable_epochs",
    ):
        if col in merged.columns:
            merged[col] = pd.to_numeric(merged[col], errors="coerce")
    if "sex" in merged.columns:
        merged["sex"] = merged["sex"].astype(str).str.upper().replace({"NAN": np.nan, "": np.nan})

    manifest = pd.DataFrame(
        [
            {
                "cohort_file": str(COHORT_FILE),
                "n_cohort_list": int(len(cohort)),
                "n_asd_list": int((cohort["group"] == "ASD").sum()),
                "n_td_list": int((cohort["group"] == "TD").sum()),
                "n_merged_analysis": int(len(merged)),
                "n_asd_analysis": int((merged["group"] == "ASD").sum()),
                "n_td_analysis": int((merged["group"] == "TD").sum()),
                "n_excluded_movie_specparam_qc": int(len(bad & set(cohort["subject_id"]))),
                "resting_derivatives": str(RESTING_DERIV),
                "movie_derivatives": str(mov_deriv),
            }
        ]
    )
    return merged, manifest


def main() -> None:
    args = parse_args()
    cfg = load_config(Path(args.config))
    log = setup_logging(cfg, name="vfe_coupling_both_postqc")
    stats_dir = Path(cfg["paths"]["derivatives_root"]) / "stats"
    stats_dir.mkdir(parents=True, exist_ok=True)

    merged, manifest = load_both_postqc_merged()
    save_csv(manifest, stats_dir / "vfe88_cohort_manifest.csv")
    save_csv(merged, stats_dir / "vfe88_subject_merged.csv")

    if len(merged) != 68 or (merged["group"] == "ASD").sum() != 34:
        log.warning(
            "队列 n=%d (ASD=%d, TD=%d)，预期 68 (34/34)",
            len(merged),
            (merged["group"] == "ASD").sum(),
            (merged["group"] == "TD").sum(),
        )

    # 回填 resting 到 merged（merge 顺序问题：delta 需要 resting）
    if "resting_posterior_exponent" not in merged.columns or merged["resting_posterior_exponent"].isna().all():
        raise RuntimeError("resting_posterior_exponent 缺失")

    merged["delta_exp"] = merged["movie_posterior_mean"] - merged["resting_posterior_exponent"]
    merged["delta_exp_neutral"] = merged["movie_neutral_exponent"] - merged["resting_posterior_exponent"]

    module1_rows: list[dict[str, Any]] = []
    for ev in EVENTS_PRIMARY:
        module1_rows.extend(
            run_coupling_models(
                merged,
                outcome_col=f"{ev}_isc_z",
                predictor_col="resting_posterior_exponent",
                module="module1_state_coupling",
                event_type=ev,
                analysis_tier="primary",
            )
        )
    for ev in EVENTS_SECONDARY:
        outcome = f"{ev}_isc_z"
        module1_rows.extend(
            run_coupling_models(
                merged,
                outcome_col=outcome,
                predictor_col="resting_posterior_exponent",
                module="module1_state_coupling",
                event_type=ev,
                analysis_tier="secondary",
            )
        )
    mod1 = pd.DataFrame(module1_rows)
    save_csv(mod1, stats_dir / "vfe88_module1_state_coupling.csv")

    module2_rows: list[dict[str, Any]] = []
    module2_rows.extend(
        run_coupling_models(
            merged,
            outcome_col="neutral_isc_z",
            predictor_col="delta_exp",
            module="module2_delta_transition",
            event_type="neutral",
            analysis_tier="primary",
        )
    )
    module2_rows.extend(
        run_coupling_models(
            merged,
            outcome_col="neutral_isc_z",
            predictor_col="delta_exp_neutral",
            module="module2_delta_transition",
            event_type="neutral_event_specific_delta",
            analysis_tier="sensitivity",
        )
    )
    mod2 = pd.DataFrame(module2_rows)
    save_csv(mod2, stats_dir / "vfe88_module2_delta_transition.csv")

    path_reg = run_path_regressions(merged)
    save_csv(path_reg, stats_dir / "vfe88_module3_path_regressions.csv")

    boot = bootstrap_indirect_effect(merged, n_boot=args.n_bootstrap, seed=args.random_seed)
    save_csv(boot, stats_dir / "vfe88_module3_indirect_effect_bootstrap.csv")

    pcorr = partial_correlation_table(merged)
    save_csv(pcorr, stats_dir / "vfe88_module3_partial_correlations.csv")

    summary_rows = []
    for label, frame in (
        ("module1_state_coupling", mod1),
        ("module2_delta_transition", mod2),
    ):
        if frame.empty:
            continue
        for _, r in frame.iterrows():
            summary_rows.append(
                {
                    "module_block": label,
                    **r.to_dict(),
                }
            )
    if not boot.empty:
        summary_rows.append({"module_block": "module3_indirect_bootstrap", **boot.iloc[0].to_dict()})
    save_csv(pd.DataFrame(summary_rows), stats_dir / "vfe88_results_summary.csv")

    # 完整 OLS/RLM 系数表（模块1 neutral）
    formula = build_formula(
        "neutral_isc_z",
        ["resting_posterior_exponent * C(group)"],
        merged,
    )
    _, ols_full = fit_ols(formula, merged.dropna(subset=["neutral_isc_z", "resting_posterior_exponent", "group"]))
    ols_full["module"] = "module1_state_coupling"
    ols_full["event_type"] = "neutral"
    ols_full["estimator"] = "OLS_full_coefficients"
    save_csv(ols_full, stats_dir / "vfe88_module1_neutral_ols_full.csv")

    log.info("Cohort manifest: %s", stats_dir / "vfe88_cohort_manifest.csv")
    log.info("Merged n=%d → %s", len(merged), stats_dir / "vfe88_subject_merged.csv")
    log.info("Module1: %s", stats_dir / "vfe88_module1_state_coupling.csv")
    log.info("Module2: %s", stats_dir / "vfe88_module2_delta_transition.csv")
    log.info("Module3 paths: %s", stats_dir / "vfe88_module3_path_regressions.csv")

    print("\n=== VFE both_postqc cohort ===")
    print(manifest.to_string(index=False))
    if not mod1.empty:
        print("\n=== Module 1 (state coupling) ===")
        print(mod1[["analysis_tier", "event_type", "estimator", "beta_interaction_TD_minus_ASD_slope_mod", "p_interaction", "n_obs"]].to_string(index=False))
    if not mod2.empty:
        print("\n=== Module 2 (delta transition) ===")
        print(mod2[["event_type", "estimator", "predictor", "beta_interaction_TD_minus_ASD_slope_mod", "p_interaction", "n_obs"]].to_string(index=False))
    if not boot.empty:
        print("\n=== Module 3 indirect effect (bootstrap) ===")
        print(boot.to_string(index=False))


if __name__ == "__main__":
    main()
