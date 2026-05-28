#!/usr/bin/env python
"""
72_interaction_evidence_enhancement.py
--------------------------------------
Strengthen interaction evidence reporting for resting-to-movie coupling by adding:
1) OLS / RLM interaction estimates
2) Stratified bootstrap CI for interaction term
3) Permutation test p-value for interaction term
4) Simple slopes (ASD / TD) for OLS and RLM
5) Approximate Bayesian posterior probability for interaction direction
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
import statsmodels.formula.api as smf
from matplotlib import pyplot as plt
from scipy.stats import norm

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config, setup_logging  # noqa: E402
from src.io_utils import save_csv  # noqa: E402


@dataclass
class TargetSpec:
    key: str
    merged_csv: str
    y_col: str
    x_col: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Interaction evidence enhancement for coupling analysis.")
    parser.add_argument("--config", type=str, required=True, help="Config path.")
    parser.add_argument("--n_bootstrap", type=int, default=5000, help="Number of bootstrap resamples.")
    parser.add_argument("--n_permutation", type=int, default=5000, help="Number of permutation resamples.")
    parser.add_argument("--random_seed", type=int, default=42, help="Random seed.")
    parser.add_argument(
        "--bayes_prior_sd",
        type=float,
        default=1.0,
        help="Prior SD for approximate normal posterior on interaction beta.",
    )
    return parser.parse_args()


def winsorize_series(s: pd.Series, lower_q: float = 0.05, upper_q: float = 0.95) -> pd.Series:
    s2 = pd.to_numeric(s, errors="coerce")
    finite = s2.dropna()
    if finite.empty:
        return s2
    lo = float(finite.quantile(lower_q))
    hi = float(finite.quantile(upper_q))
    return s2.clip(lower=lo, upper=hi)


def build_formula(y_col: str, x_col: str, df: pd.DataFrame) -> str:
    formula = f"{y_col} ~ {x_col} * C(group) + age_months + usable_epochs"
    if "IQ_total" in df.columns:
        formula += " + IQ_total"
    if "sex" in df.columns:
        formula += " + C(sex)"
    return formula


def find_interaction_term(index_like) -> str | None:
    terms = [str(x) for x in index_like]
    candidates = [t for t in terms if (":C(group)" in t and ("posterior_exponent" in t))]
    return candidates[0] if candidates else None


def extract_simple_slopes(result, base_x_term: str, interaction_term: str | None) -> list[dict]:
    rows: list[dict] = []
    if base_x_term not in result.params.index:
        return rows

    beta_asd = float(result.params[base_x_term])
    p_asd = float(result.pvalues.get(base_x_term, np.nan))
    rows.append(
        {
            "group_slope": "ASD",
            "beta": beta_asd,
            "p_value": p_asd,
            "contrast": base_x_term,
        },
    )

    if interaction_term is None or interaction_term not in result.params.index:
        return rows

    beta_td = float(result.params[base_x_term] + result.params[interaction_term])
    p_td = np.nan
    try:
        test = result.t_test(f"{base_x_term} + {interaction_term} = 0")
        p_td = float(np.asarray(test.pvalue).reshape(-1)[0])
    except Exception:
        pass
    rows.append(
        {
            "group_slope": "TD",
            "beta": beta_td,
            "p_value": p_td,
            "contrast": f"{base_x_term} + {interaction_term}",
        },
    )
    return rows


def stratified_bootstrap_interaction(
    df: pd.DataFrame,
    formula: str,
    interaction_term: str,
    n_resamples: int,
    rng: np.random.Generator,
) -> pd.DataFrame:
    rows = []
    groups = sorted(df["group"].dropna().astype(str).unique().tolist())
    grouped = {g: df[df["group"].astype(str) == g].copy() for g in groups}

    for i in range(n_resamples):
        samples = []
        valid = True
        for g in groups:
            gdf = grouped[g]
            n_g = len(gdf)
            if n_g == 0:
                valid = False
                break
            idx = rng.integers(0, n_g, size=n_g)
            samples.append(gdf.iloc[idx].copy())
        if not valid:
            rows.append({"resample_id": i, "beta_interaction": np.nan})
            continue

        sample_df = pd.concat(samples, ignore_index=True)
        try:
            fit = smf.ols(formula=formula, data=sample_df).fit()
            beta = float(fit.params.get(interaction_term, np.nan))
        except Exception:
            beta = np.nan
        rows.append({"resample_id": i, "beta_interaction": beta})
    return pd.DataFrame(rows)


def permutation_test_interaction(
    df: pd.DataFrame,
    formula: str,
    interaction_term: str,
    n_resamples: int,
    rng: np.random.Generator,
) -> tuple[float, pd.DataFrame]:
    obs_fit = smf.ols(formula=formula, data=df).fit()
    obs_beta = float(obs_fit.params.get(interaction_term, np.nan))

    perm_betas = []
    for i in range(n_resamples):
        perm_df = df.copy()
        perm_df["group"] = rng.permutation(perm_df["group"].values)
        try:
            fit = smf.ols(formula=formula, data=perm_df).fit()
            beta = float(fit.params.get(interaction_term, np.nan))
        except Exception:
            beta = np.nan
        perm_betas.append({"resample_id": i, "beta_interaction_perm": beta})
    perm_df = pd.DataFrame(perm_betas)
    valid = perm_df["beta_interaction_perm"].dropna().to_numpy()
    if len(valid) == 0 or np.isnan(obs_beta):
        return np.nan, perm_df
    p_perm = float((np.sum(np.abs(valid) >= abs(obs_beta)) + 1) / (len(valid) + 1))
    return p_perm, perm_df


def approximate_bayes_direction(beta_hat: float, se_hat: float, prior_sd: float) -> dict[str, float]:
    if np.isnan(beta_hat) or np.isnan(se_hat) or se_hat <= 0 or prior_sd <= 0:
        return {
            "post_mean": np.nan,
            "post_sd": np.nan,
            "p_beta_lt_0": np.nan,
            "p_beta_gt_0": np.nan,
            "p_abs_beta_lt_0p1": np.nan,
        }

    prior_var = prior_sd ** 2
    like_var = se_hat ** 2
    post_var = 1.0 / (1.0 / prior_var + 1.0 / like_var)
    post_sd = float(np.sqrt(post_var))
    post_mean = float(post_var * (beta_hat / like_var))

    p_lt_0 = float(norm.cdf(0.0, loc=post_mean, scale=post_sd))
    p_gt_0 = 1.0 - p_lt_0
    p_rope = float(norm.cdf(0.1, loc=post_mean, scale=post_sd) - norm.cdf(-0.1, loc=post_mean, scale=post_sd))
    return {
        "post_mean": post_mean,
        "post_sd": post_sd,
        "p_beta_lt_0": p_lt_0,
        "p_beta_gt_0": p_gt_0,
        "p_abs_beta_lt_0p1": p_rope,
    }


def summarize_bootstrap(dist_df: pd.DataFrame) -> dict[str, float]:
    valid = dist_df["beta_interaction"].dropna().to_numpy()
    if len(valid) == 0:
        return {
            "bootstrap_n_valid": 0,
            "bootstrap_beta_mean": np.nan,
            "bootstrap_ci95_low": np.nan,
            "bootstrap_ci95_high": np.nan,
            "bootstrap_p_two_sided": np.nan,
        }
    ci_low, ci_high = np.quantile(valid, [0.025, 0.975])
    p_boot = 2.0 * min(np.mean(valid <= 0), np.mean(valid >= 0))
    return {
        "bootstrap_n_valid": int(len(valid)),
        "bootstrap_beta_mean": float(np.mean(valid)),
        "bootstrap_ci95_low": float(ci_low),
        "bootstrap_ci95_high": float(ci_high),
        "bootstrap_p_two_sided": float(min(1.0, p_boot)),
    }


def run_one_target(
    spec: TargetSpec,
    stats_dir: Path,
    n_bootstrap: int,
    n_permutation: int,
    rng: np.random.Generator,
    bayes_prior_sd: float,
) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(stats_dir / spec.merged_csv)
    for col in [spec.y_col, spec.x_col, "age_months", "usable_epochs", "IQ_total"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "group" in df.columns:
        df["group"] = df["group"].astype(str).str.upper()
    if "sex" in df.columns:
        df["sex"] = df["sex"].astype(str).str.upper().replace({"NAN": np.nan, "": np.nan})

    need = [spec.y_col, spec.x_col, "group", "age_months", "usable_epochs"]
    if "IQ_total" in df.columns:
        need.append("IQ_total")
    if "sex" in df.columns:
        need.append("sex")
    model_df = df.dropna(subset=need).copy()

    formula = build_formula(spec.y_col, spec.x_col, model_df)
    ols = smf.ols(formula=formula, data=model_df).fit()
    ols_inter = find_interaction_term(ols.params.index)
    beta_ols = float(ols.params.get(ols_inter, np.nan)) if ols_inter else np.nan
    p_ols = float(ols.pvalues.get(ols_inter, np.nan)) if ols_inter else np.nan
    se_ols = float(ols.bse.get(ols_inter, np.nan)) if ols_inter else np.nan

    x_w = f"{spec.x_col}_w"
    y_w = f"{spec.y_col}_w"
    robust_df = model_df.copy()
    robust_df[x_w] = winsorize_series(robust_df[spec.x_col])
    robust_df[y_w] = winsorize_series(robust_df[spec.y_col])
    r_formula = build_formula(y_w, x_w, robust_df)
    rlm = smf.rlm(formula=r_formula, data=robust_df, M=sm.robust.norms.HuberT()).fit()
    rlm_inter = find_interaction_term(rlm.params.index)
    beta_rlm = float(rlm.params.get(rlm_inter, np.nan)) if rlm_inter else np.nan
    p_rlm = float(rlm.pvalues.get(rlm_inter, np.nan)) if rlm_inter else np.nan

    boot_dist = pd.DataFrame(columns=["resample_id", "beta_interaction"])
    boot_summary = {
        "bootstrap_n_valid": np.nan,
        "bootstrap_beta_mean": np.nan,
        "bootstrap_ci95_low": np.nan,
        "bootstrap_ci95_high": np.nan,
        "bootstrap_p_two_sided": np.nan,
    }
    if ols_inter:
        boot_dist = stratified_bootstrap_interaction(
            df=model_df,
            formula=formula,
            interaction_term=ols_inter,
            n_resamples=n_bootstrap,
            rng=rng,
        )
        boot_summary = summarize_bootstrap(boot_dist)

    p_perm = np.nan
    perm_dist = pd.DataFrame(columns=["resample_id", "beta_interaction_perm"])
    if ols_inter:
        p_perm, perm_dist = permutation_test_interaction(
            df=model_df,
            formula=formula,
            interaction_term=ols_inter,
            n_resamples=n_permutation,
            rng=rng,
        )

    ols_slopes = extract_simple_slopes(ols, spec.x_col, ols_inter)
    rlm_slopes = extract_simple_slopes(rlm, x_w, rlm_inter)
    slopes_rows = []
    for row in ols_slopes:
        slopes_rows.append({"target": spec.key, "model": "OLS", **row})
    for row in rlm_slopes:
        slopes_rows.append({"target": spec.key, "model": "RLM_winsor", **row})
    slopes_df = pd.DataFrame(slopes_rows)

    bayes = approximate_bayes_direction(beta_ols, se_ols, bayes_prior_sd)

    summary_row = {
        "target": spec.key,
        "n_obs": int(ols.nobs),
        "interaction_beta_ols": beta_ols,
        "interaction_p_ols": p_ols,
        "interaction_beta_rlm": beta_rlm,
        "interaction_p_rlm": p_rlm,
        "permutation_p_two_sided": p_perm,
        "ols_interaction_term": ols_inter,
        "rlm_interaction_term": rlm_inter,
        "ols_formula": formula,
        "rlm_formula": r_formula,
        **boot_summary,
        **bayes,
    }
    return summary_row, slopes_df, boot_dist, perm_dist


def draw_interaction_forest(summary_df: pd.DataFrame, fig_path: Path) -> None:
    plot_df = summary_df.copy()
    plot_df["target"] = pd.Categorical(
        plot_df["target"],
        categories=["mental", "pain", "neutral", "overall_isc"],
        ordered=True,
    )
    plot_df = plot_df.sort_values("target")

    y_labels = plot_df["target"].astype(str).tolist()
    y_pos = np.arange(len(plot_df))

    plt.figure(figsize=(8.4, 5.4))
    plt.axvline(0.0, color="#888", linestyle="--", linewidth=1)

    plt.errorbar(
        x=plot_df["interaction_beta_ols"].to_numpy(),
        y=y_pos + 0.1,
        xerr=[
            plot_df["interaction_beta_ols"].to_numpy() - plot_df["bootstrap_ci95_low"].to_numpy(),
            plot_df["bootstrap_ci95_high"].to_numpy() - plot_df["interaction_beta_ols"].to_numpy(),
        ],
        fmt="o",
        color="#1f77b4",
        ecolor="#1f77b4",
        elinewidth=1.5,
        capsize=3,
        label="OLS beta (95% bootstrap CI)",
    )
    plt.scatter(
        plot_df["interaction_beta_rlm"].to_numpy(),
        y_pos - 0.1,
        color="#d62728",
        marker="s",
        s=46,
        label="RLM winsor beta",
    )

    plt.yticks(y_pos, y_labels)
    plt.xlabel("Interaction beta")
    plt.ylabel("Target")
    plt.title("Resting-to-Movie Interaction Evidence")
    plt.legend(loc="best", frameon=True)
    plt.tight_layout()
    plt.savefig(fig_path.with_suffix(".png"), dpi=200)
    plt.savefig(fig_path.with_suffix(".pdf"))
    plt.close()


def main() -> None:
    args = parse_args()
    cfg = load_config(PROJECT_ROOT / args.config)
    log = setup_logging(cfg, name="interaction_evidence_enhancement")

    deriv = Path(cfg["paths"]["derivatives_root"])
    out_root = Path(cfg["paths"]["outputs_root"])
    stats_dir = deriv / "stats"
    fig_dir = out_root / "figures"
    stats_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    specs = [
        TargetSpec("mental", "resting_movie_coupling_merged.csv", "mental_isc_z", "posterior_exponent"),
        TargetSpec("pain", "resting_movie_coupling_merged_pain.csv", "mental_isc_z", "posterior_exponent"),
        TargetSpec("neutral", "resting_movie_coupling_merged_neutral.csv", "mental_isc_z", "posterior_exponent"),
        TargetSpec("overall_isc", "resting_movie_coupling_overall_isc_merged.csv", "overall_movie_isc_z", "posterior_exponent"),
    ]

    rng = np.random.default_rng(args.random_seed)
    summary_rows = []
    slopes_all = []

    for spec in specs:
        merged_path = stats_dir / spec.merged_csv
        if not merged_path.exists():
            log.warning("Missing merged file for target=%s: %s", spec.key, merged_path)
            continue
        summary_row, slopes_df, boot_dist, perm_dist = run_one_target(
            spec=spec,
            stats_dir=stats_dir,
            n_bootstrap=args.n_bootstrap,
            n_permutation=args.n_permutation,
            rng=rng,
            bayes_prior_sd=args.bayes_prior_sd,
        )
        summary_rows.append(summary_row)
        slopes_all.append(slopes_df)
        save_csv(boot_dist, stats_dir / f"resting_movie_coupling_interaction_bootstrap_dist_{spec.key}.csv")
        save_csv(perm_dist, stats_dir / f"resting_movie_coupling_interaction_permutation_dist_{spec.key}.csv")

    summary_df = pd.DataFrame(summary_rows)
    if summary_df.empty:
        log.warning("No summary generated; no merged target files found.")
        return
    slopes_df = pd.concat(slopes_all, ignore_index=True) if slopes_all else pd.DataFrame()

    save_csv(summary_df, stats_dir / "resting_movie_coupling_interaction_evidence_summary.csv")
    save_csv(slopes_df, stats_dir / "resting_movie_coupling_interaction_simple_slopes_all.csv")

    draw_interaction_forest(
        summary_df=summary_df,
        fig_path=fig_dir / "resting_movie_coupling_interaction_evidence_forest",
    )

    log.info("Interaction evidence summary: %s", stats_dir / "resting_movie_coupling_interaction_evidence_summary.csv")
    log.info("Simple slopes: %s", stats_dir / "resting_movie_coupling_interaction_simple_slopes_all.csv")
    log.info("Forest figure: %s", fig_dir / "resting_movie_coupling_interaction_evidence_forest.png")


if __name__ == "__main__":
    main()
