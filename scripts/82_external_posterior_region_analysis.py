#!/usr/bin/env python
"""HBN 外部验证：后部 ROI（顶叶+枕叶）组间分析。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config, load_roi_config  # noqa: E402
from src.io_utils import (  # noqa: E402
    attach_usable_epochs,
    exclude_specparam_low_quality,
    load_analysis_participants,
    save_csv,
)
from src.stats_utils import fdr_correction, model_results_to_row, run_ols  # noqa: E402

COVARIATE_FORMULA = " + age_months + C(sex) + IQ_total + usable_epochs"
CHANNEL_FORMULA = "aperiodic_exponent ~ C(group) + age_months + C(sex) + IQ_total + usable_epochs"
# 主研究 channel-level FDR 显著后部电极（matched post-QC）
MAIN_SIG_POSTERIOR_CHANNELS = ("E33", "E36", "E37", "E38")


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="外部验证后部脑区分析")
    p.add_argument(
        "--config",
        default=str(PROJECT_ROOT / "config/config_external_hbn_resting_60x60.yaml"),
    )
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    cfg = load_config(Path(args.config))
    deriv = Path(cfg["paths"]["derivatives_root"])
    roi_cfg = load_roi_config()
    post_ch = set(roi_cfg["channels_egi64"]["parietal"] + roi_cfg["channels_egi64"]["occipital"])

    roi = pd.read_csv(deriv / "roi/specparam_subject_global.csv")
    participants = load_analysis_participants(cfg)
    participants = attach_usable_epochs(participants, deriv)
    participants = exclude_specparam_low_quality(participants, deriv)
    df = participants.merge(roi, on=["subject_id", "group"], how="inner")

    long = pd.read_csv(deriv / "roi/specparam_subject_roi_long.csv")
    post_long = long[long["roi"].isin(["parietal", "occipital"])].copy()
    post_off = post_long.groupby(["subject_id", "group"])["offset"].mean().reset_index(name="posterior_offset")
    df = df.merge(post_off, on=["subject_id", "group"], how="left")
    df["posterior_exponent"] = df[["parietal_exponent", "occipital_exponent"]].mean(axis=1)

    rows = []
    for outcome in ("posterior_exponent", "parietal_exponent", "occipital_exponent", "posterior_offset"):
        formula = f"{outcome} ~ C(group){COVARIATE_FORMULA}"
        sub = df.dropna(subset=[outcome, "group", "age_months", "sex", "IQ_total", "usable_epochs"])
        rows.extend(model_results_to_row(run_ols(formula, sub), "posterior_roi", outcome))

    desc_rows = []
    for outcome in ("posterior_exponent", "parietal_exponent", "occipital_exponent", "posterior_offset"):
        sub = df.dropna(subset=[outcome])
        a = sub.loc[sub["group"] == "ASD", outcome]
        t = sub.loc[sub["group"] == "TD", outcome]
        d = (a.mean() - t.mean()) / np.sqrt((a.var(ddof=1) + t.var(ddof=1)) / 2) if len(a) > 1 and len(t) > 1 else np.nan
        desc_rows.append(
            {
                "outcome": outcome,
                "ASD_mean": a.mean(),
                "TD_mean": t.mean(),
                "ASD_n": len(a),
                "TD_n": len(t),
                "cohens_d_ASD_minus_TD": d,
            }
        )

    ch = pd.read_csv(deriv / "specparam/specparam_channel_results_qc.csv")
    if "fit_valid" in ch.columns:
        ch = ch[ch["fit_valid"]]
    ch = ch[ch["channel"].isin(post_ch)]

    ch_rows = []
    for ch_name, sub_ch in ch.groupby("channel"):
        m = participants.merge(sub_ch, on=["subject_id", "group"], how="inner")
        m = m.dropna(subset=["aperiodic_exponent", "group", "age_months", "sex", "IQ_total", "usable_epochs"])
        if len(m) < 10:
            continue
        res = run_ols(CHANNEL_FORMULA, m)
        term = [t for t in res.params.index if t.startswith("C(group)")][0]
        ch_rows.append(
            {
                "channel": ch_name,
                "term": term,
                "coef": res.params[term],
                "pvalue": res.pvalues[term],
                "n_obs": len(m),
            }
        )

    ch_df = pd.DataFrame(ch_rows)
    if not ch_df.empty:
        _, p_adj = fdr_correction(ch_df["pvalue"].values)
        ch_df["pvalue_fdr"] = p_adj
        ch_df["significant_fdr"] = ch_df["pvalue_fdr"] < 0.05

    stats_dir = deriv / "stats"
    stats_dir.mkdir(parents=True, exist_ok=True)
    save_csv(pd.DataFrame(rows), stats_dir / "posterior_region_group_analysis.csv")
    save_csv(pd.DataFrame(desc_rows), stats_dir / "posterior_region_descriptives.csv")
    if not ch_df.empty:
        save_csv(ch_df.sort_values("pvalue"), stats_dir / "posterior_channel_level_analysis.csv")

    # 主研究显著 4 通道：单通道 + 四通道均值
    main_ch = pd.read_csv(deriv / "specparam/specparam_channel_results_qc.csv")
    if "fit_valid" in main_ch.columns:
        main_ch = main_ch[main_ch["fit_valid"]]
    main_ch = main_ch[main_ch["channel"].isin(MAIN_SIG_POSTERIOR_CHANNELS)]

    sig_rows = []
    subj_cluster = []
    for ch_name, sub_ch in main_ch.groupby("channel"):
        m = participants.merge(sub_ch, on=["subject_id", "group"], how="inner")
        m = m.dropna(subset=["aperiodic_exponent", "group", "age_months", "sex", "IQ_total", "usable_epochs"])
        if len(m) < 10:
            continue
        res = run_ols(CHANNEL_FORMULA, m)
        term = [t for t in res.params.index if t.startswith("C(group)")][0]
        sig_rows.append(
            {
                "channel": ch_name,
                "term": term,
                "coef": res.params[term],
                "pvalue": res.pvalues[term],
                "n_obs": len(m),
            }
        )
        subj_cluster.append(m[["subject_id", "group", "channel", "aperiodic_exponent"]])

    sig_df = pd.DataFrame(sig_rows)
    cluster_rows = []
    cluster_desc = []
    if subj_cluster:
        long_ch = pd.concat(subj_cluster, ignore_index=True)
        cluster_mean = (
            long_ch.groupby(["subject_id", "group"], as_index=False)["aperiodic_exponent"]
            .mean()
            .rename(columns={"aperiodic_exponent": "main_sig_posterior_exponent"})
        )
        cluster_df = participants.merge(cluster_mean, on=["subject_id", "group"], how="inner")
        cluster_df = attach_usable_epochs(cluster_df, deriv)
        cluster_df = cluster_df.dropna(
            subset=["main_sig_posterior_exponent", "group", "age_months", "sex", "IQ_total", "usable_epochs"]
        )
        formula = f"main_sig_posterior_exponent ~ C(group){COVARIATE_FORMULA}"
        cluster_rows.extend(
            model_results_to_row(run_ols(formula, cluster_df), "main_sig_posterior_4ch", "main_sig_posterior_exponent")
        )
        a = cluster_df.loc[cluster_df["group"] == "ASD", "main_sig_posterior_exponent"]
        t = cluster_df.loc[cluster_df["group"] == "TD", "main_sig_posterior_exponent"]
        d = (a.mean() - t.mean()) / np.sqrt((a.var(ddof=1) + t.var(ddof=1)) / 2) if len(a) > 1 and len(t) > 1 else np.nan
        cluster_desc.append(
            {
                "outcome": "main_sig_posterior_exponent",
                "channels": "|".join(MAIN_SIG_POSTERIOR_CHANNELS),
                "ASD_mean": a.mean(),
                "TD_mean": t.mean(),
                "ASD_n": len(a),
                "TD_n": len(t),
                "cohens_d_ASD_minus_TD": d,
            }
        )

    if not sig_df.empty:
        save_csv(sig_df.sort_values("pvalue"), stats_dir / "main_sig_posterior_channels_analysis.csv")
    if cluster_rows:
        save_csv(pd.DataFrame(cluster_rows), stats_dir / "main_sig_posterior_cluster_group_analysis.csv")
    if cluster_desc:
        save_csv(pd.DataFrame(cluster_desc), stats_dir / "main_sig_posterior_cluster_descriptives.csv")

    res_df = pd.DataFrame(rows)
    print("=== ROI-level (TD vs ASD, adjusted) ===")
    for outcome in ("posterior_exponent", "parietal_exponent", "occipital_exponent", "posterior_offset"):
        r = res_df[(res_df["outcome"] == outcome) & (res_df["term"].str.contains("group"))]
        if len(r):
            print(f"{outcome}: beta={r.iloc[0]['coef']:.4f}, p={r.iloc[0]['pvalue']:.4f}, n={int(r.iloc[0]['n_obs'])}")
    print("=== Descriptives ===")
    for r in desc_rows:
        print(
            f"{r['outcome']}: ASD={r['ASD_mean']:.3f}, TD={r['TD_mean']:.3f}, "
            f"d={r['cohens_d_ASD_minus_TD']:.3f}"
        )
    if not ch_df.empty:
        print(f"=== Posterior channels FDR sig: {int(ch_df['significant_fdr'].sum())} / {len(ch_df)} ===")
        print(ch_df.nsmallest(5, "pvalue")[["channel", "coef", "pvalue", "pvalue_fdr"]].to_string(index=False))
    if not sig_df.empty:
        print(f"=== Main-study sig channels {list(MAIN_SIG_POSTERIOR_CHANNELS)} ===")
        print(sig_df.sort_values("pvalue")[["channel", "coef", "pvalue", "n_obs"]].to_string(index=False))
    if cluster_rows:
        cr = pd.DataFrame(cluster_rows)
        r = cr[(cr["outcome"] == "main_sig_posterior_exponent") & (cr["term"].str.contains("group"))]
        if len(r):
            print(
                f"4-ch mean exponent: beta={r.iloc[0]['coef']:.4f}, "
                f"p={r.iloc[0]['pvalue']:.4f}, n={int(r.iloc[0]['n_obs'])}"
            )
    if cluster_desc:
        c = cluster_desc[0]
        print(
            f"4-ch descriptives: ASD={c['ASD_mean']:.3f}, TD={c['TD_mean']:.3f}, "
            f"d={c['cohens_d_ASD_minus_TD']:.3f}"
        )


if __name__ == "__main__":
    main()
