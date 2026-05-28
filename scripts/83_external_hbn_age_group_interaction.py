#!/usr/bin/env python
"""
83_external_hbn_age_group_interaction.py
----------------------------------------
HBN 外部验证：复现主研究 Group × Age（月龄）交互效应。

模型（与主研究 extension 一致）:
  outcome ~ C(group) * age_months + C(sex) + IQ_total + usable_epochs

支持闭眼 / 睁眼分段；输出系数表与交互图。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.formula.api import ols

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config, setup_logging  # noqa: E402
from src.extension_analysis import load_main_qc_cohort  # noqa: E402
from src.io_utils import save_csv  # noqa: E402

MAIN_SIG_POSTERIOR_CHANNELS = ("E33", "E36", "E37", "E38")
COVARIATES = "C(sex) + IQ_total + usable_epochs"
INTERACTION_TERM = "C(group)[T.TD]:age_months"
COL_ASD = "#4C72B0"
COL_TD = "#DD8452"

OUTCOMES = (
    "global_exponent",
    "global_offset",
    "posterior_exponent",
    "occipital_exponent",
    "parietal_exponent",
    "main_sig_posterior_exponent",
)


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="HBN 外部验证 Group×Age 交互")
    p.add_argument(
        "--config",
        action="append",
        default=None,
        help="可重复传入多个 config（如闭眼、睁眼）",
    )
    p.add_argument(
        "--segment-label",
        action="append",
        default=None,
        help="与 --config 一一对应的标签（如 eyes_closed, eyes_open）",
    )
    return p.parse_args()


def _add_derived_outcomes(df: pd.DataFrame, deriv: Path) -> pd.DataFrame:
    out = df.copy()
    if "parietal_exponent" in out.columns and "occipital_exponent" in out.columns:
        out["posterior_exponent"] = out[["parietal_exponent", "occipital_exponent"]].mean(axis=1)

    ch_path = deriv / "specparam" / "specparam_channel_results_qc.csv"
    if ch_path.exists():
        ch = pd.read_csv(ch_path)
        if "fit_valid" in ch.columns:
            ch = ch[ch["fit_valid"]]
        ch = ch[ch["channel"].isin(MAIN_SIG_POSTERIOR_CHANNELS)]
        if not ch.empty:
            cluster = (
                ch.groupby(["subject_id", "group"], as_index=False)["aperiodic_exponent"]
                .mean()
                .rename(columns={"aperiodic_exponent": "main_sig_posterior_exponent"})
            )
            out = out.merge(cluster, on=["subject_id", "group"], how="left")
    return out


def fit_age_interaction_models(df: pd.DataFrame, segment: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for outcome in OUTCOMES:
        if outcome not in df.columns:
            continue
        formula = f"{outcome} ~ C(group) * age_months + {COVARIATES}"
        sub = df.dropna(subset=[outcome, "group", "age_months", "sex", "IQ_total", "usable_epochs"])
        if len(sub) < 12:
            continue
        res = ols(formula, data=sub).fit()
        conf = res.conf_int()
        counts = {
            "segment": segment,
            "n": int(res.nobs),
            "n_ASD": int((sub["group"] == "ASD").sum()),
            "n_TD": int((sub["group"] == "TD").sum()),
        }
        for term in res.params.index:
            rows.append(
                {
                    "segment": segment,
                    "outcome": outcome,
                    "model": formula,
                    **counts,
                    "term": term,
                    "coef": float(res.params[term]),
                    "se": float(res.bse[term]),
                    "t": float(res.tvalues[term]),
                    "p": float(res.pvalues[term]),
                    "ci_low": float(conf.loc[term, 0]),
                    "ci_high": float(conf.loc[term, 1]),
                    "r_squared": float(res.rsquared),
                }
            )
    return pd.DataFrame(rows)


def plot_interaction(
    df: pd.DataFrame,
    outcome: str,
    segment: str,
    fig_dir: Path,
) -> None:
    formula = f"{outcome} ~ C(group) * age_months + {COVARIATES}"
    sub = df.dropna(subset=[outcome, "group", "age_months", "sex", "IQ_total", "usable_epochs"])
    if len(sub) < 12:
        return
    res = ols(formula, data=sub).fit()

    fig, ax = plt.subplots(figsize=(5.5, 4))
    mode_sex = sub["sex"].mode().iloc[0]
    iq_m = float(sub["IQ_total"].mean())
    ep_m = float(sub["usable_epochs"].mean())
    ages = np.linspace(sub["age_months"].min(), sub["age_months"].max(), 80)

    for grp, color in [("ASD", COL_ASD), ("TD", COL_TD)]:
        pred_df = pd.DataFrame(
            {
                "age_months": ages,
                "group": grp,
                "sex": mode_sex,
                "IQ_total": iq_m,
                "usable_epochs": ep_m,
            }
        )
        pred = res.get_prediction(pred_df).summary_frame(alpha=0.05)
        ax.plot(ages, pred["mean"], color=color, lw=1.5, label=grp)
        ax.fill_between(ages, pred["mean_ci_lower"], pred["mean_ci_upper"], color=color, alpha=0.2, linewidth=0)
        gsub = sub[sub["group"] == grp]
        ax.scatter(gsub["age_months"], gsub[outcome], s=18, alpha=0.55, color=color, edgecolors="none")

    inter = res.params.get(INTERACTION_TERM, np.nan)
    p_inter = res.pvalues.get(INTERACTION_TERM, np.nan)
    ax.set_xlabel("Age (months)")
    ax.set_ylabel(outcome.replace("_", " "))
    ax.set_title(f"{segment}: Group × Age (interaction p={p_inter:.3f})")
    ax.legend(frameon=False, loc="best")
    fig_dir.mkdir(parents=True, exist_ok=True)
    out = fig_dir / f"fig_age_group_interaction_{segment}_{outcome}.png"
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def run_one_config(config_path: Path, segment: str) -> pd.DataFrame:
    cfg = load_config(config_path)
    log = setup_logging(cfg, name=f"age_interaction_{segment}")
    deriv = Path(cfg["paths"]["derivatives_root"])
    fig_dir = Path(cfg["paths"]["outputs_root"]) / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    roi_path = deriv / "roi" / "specparam_subject_global.csv"
    if not roi_path.exists():
        log.error("缺少 ROI 结果 %s，请先运行 03–06 分析流程", roi_path)
        return pd.DataFrame()

    roi = pd.read_csv(roi_path)
    df = load_main_qc_cohort(cfg, deriv)
    add_cols = [c for c in roi.columns if c not in df.columns and c != "subject_id"]
    if add_cols:
        df = df.merge(roi[["subject_id"] + add_cols], on="subject_id", how="inner")
    df = _add_derived_outcomes(df, deriv)

    models = fit_age_interaction_models(df, segment)
    stats_dir = deriv / "stats"
    stats_dir.mkdir(parents=True, exist_ok=True)
    save_csv(models, stats_dir / "age_group_interaction_models.csv")

    for outcome in ("global_exponent", "global_offset", "posterior_exponent", "main_sig_posterior_exponent"):
        if outcome in df.columns:
            plot_interaction(df, outcome, segment, fig_dir)

    if not models.empty:
        inter = models.loc[models["term"] == INTERACTION_TERM].copy()
        log.info("segment=%s 交互项结果:\n%s", segment, inter[["outcome", "coef", "p", "n"]].to_string(index=False))
    return models


def main() -> int:
    args = _parse_args()
    default_configs = [
        (PROJECT_ROOT / "config/config_external_hbn_resting_60x60_eyes_closed.yaml", "eyes_closed"),
        (PROJECT_ROOT / "config/config_external_hbn_resting_60x60_eyes_open.yaml", "eyes_open"),
    ]
    if args.config:
        configs = [(Path(c), args.segment_label[i] if args.segment_label else f"seg{i+1}") for i, c in enumerate(args.config)]
    else:
        configs = default_configs

    all_models: list[pd.DataFrame] = []
    for cfg_path, label in configs:
        if not cfg_path.exists():
            print(f"[SKIP] config not found: {cfg_path}")
            continue
        print(f"\n=== {label} ({cfg_path.name}) ===")
        m = run_one_config(cfg_path, label)
        if not m.empty:
            all_models.append(m)

    if all_models:
        merged = pd.concat(all_models, ignore_index=True)
        out = PROJECT_ROOT / "outputs_external_hbn/age_group_interaction_all_segments.csv"
        out.parent.mkdir(parents=True, exist_ok=True)
        save_csv(merged, out)

        summary = merged.loc[merged["term"] == INTERACTION_TERM, ["segment", "outcome", "coef", "p", "n", "n_ASD", "n_TD"]]
        print("\n=== Group × Age interaction summary ===")
        print(summary.sort_values(["segment", "outcome"]).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
