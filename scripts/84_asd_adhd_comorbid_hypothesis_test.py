#!/usr/bin/env python
"""检验共病驱动假说：ASD+仅 ADHD 子集 vs TD（后部 ROI / global / E38）。"""

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

DX1 = "Diagnosis_ClinicianConsensus,DX_01"
DX2 = "Diagnosis_ClinicianConsensus,DX_02"
ASD_LABEL = "Autism Spectrum Disorder"
ADHD_LABELS = {
    "ADHD-Combined Type",
    "ADHD-Inattentive Type",
    "ADHD-Hyperactive/Impulsive Type",
    "Other Specified Attention-Deficit/Hyperactivity Disorder",
}
COVARIATE_FORMULA = " + age_months + C(sex) + IQ_total + usable_epochs"
MAIN_SIG_POSTERIOR_CHANNELS = ("E33", "E36", "E37", "E38")


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="ASD+仅 ADHD vs TD 共病驱动假说检验")
    p.add_argument(
        "--config",
        default=str(PROJECT_ROOT / "config/config_external_hbn_resting_100x2_eyes_closed.yaml"),
    )
    return p.parse_args()


def _dx_list(row: pd.Series) -> list[str]:
    vals = [str(row.get(DX1, "")).strip(), str(row.get(DX2, "")).strip()]
    return [v for v in vals if v and v.lower() != "nan"]


def assign_asd_subtype(subjects_csv: Path) -> pd.DataFrame:
    meta = pd.read_csv(subjects_csv)
    meta = meta[meta["group_std"] == "ASD"].copy()
    meta["dx"] = meta.apply(_dx_list, axis=1)
    meta["has_asd_dx"] = meta["dx"].apply(lambda x: ASD_LABEL in x)
    meta["has_adhd"] = meta["dx"].apply(lambda x: any(d in ADHD_LABELS for d in x))
    meta["non_core"] = meta["dx"].apply(
        lambda x: [d for d in x if d not in {ASD_LABEL, *ADHD_LABELS}]
    )

    def _subtype(row: pd.Series) -> str:
        if row["has_asd_dx"] and row["has_adhd"] and len(row["non_core"]) == 0:
            return "asd_adhd_only"
        if row["has_asd_dx"] and not row["has_adhd"]:
            return "asd_no_adhd"
        if row["has_asd_dx"] and row["has_adhd"] and len(row["non_core"]) > 0:
            return "asd_adhd_other"
        if row["has_adhd"] and not row["has_asd_dx"]:
            return "asd_group_adhd_primary"
        return "asd_other"

    meta["asd_subtype"] = meta.apply(_subtype, axis=1)
    return meta[["subject_id", "asd_subtype", "dx"]]


def _prepare_df(
    cfg: dict,
    subtype: str,
    participants: pd.DataFrame,
    roi: pd.DataFrame,
    deriv: Path,
) -> pd.DataFrame:
    sub = participants[participants["asd_subtype"] == subtype].copy()
    sub = sub.drop(columns=["group"], errors="ignore")
    sub["group"] = "ASD"
    td = participants[participants["group"] == "TD"].copy()
    df = pd.concat([sub, td], ignore_index=True)
    df = df.merge(roi, on=["subject_id", "group"], how="inner")
    df["posterior_exponent"] = df[["parietal_exponent", "occipital_exponent"]].mean(axis=1)
    post_off = (
        pd.read_csv(deriv / "roi/specparam_subject_roi_long.csv")
        .query("roi in ['parietal', 'occipital']")
        .groupby(["subject_id", "group"])["offset"]
        .mean()
        .reset_index(name="posterior_offset")
    )
    df = df.merge(post_off, on=["subject_id", "group"], how="left")
    return df


def _run_outcomes(df: pd.DataFrame, label: str) -> list[dict]:
    rows = []
    for outcome in (
        "global_exponent",
        "posterior_exponent",
        "parietal_exponent",
        "occipital_exponent",
        "posterior_offset",
    ):
        formula = f"{outcome} ~ C(group){COVARIATE_FORMULA}"
        sub = df.dropna(subset=[outcome, "group", "age_months", "sex", "IQ_total", "usable_epochs"])
        if len(sub) < 10 or sub["group"].nunique() < 2:
            continue
        rows.extend(model_results_to_row(run_ols(formula, sub), label, outcome))
    return rows


def _run_e38(participants: pd.DataFrame, deriv: Path, label: str) -> list[dict]:
    ch = pd.read_csv(deriv / "specparam/specparam_channel_results_qc.csv")
    if "fit_valid" in ch.columns:
        ch = ch[ch["fit_valid"]]
    ch = ch[ch["channel"] == "E38"]
    rows = []
    for sid, sub_ch in ch.groupby("subject_id"):
        _ = sid
    m = participants.merge(ch, on=["subject_id", "group"], how="inner")
    m = m.dropna(subset=["aperiodic_exponent", "group", "age_months", "sex", "IQ_total", "usable_epochs"])
    if len(m) < 10 or m["group"].nunique() < 2:
        return rows
    formula = f"aperiodic_exponent ~ C(group){COVARIATE_FORMULA}"
    rows.extend(model_results_to_row(run_ols(formula, m), label, "E38_exponent"))
    return rows


def _run_posterior_channels(participants: pd.DataFrame, deriv: Path) -> pd.DataFrame:
    roi_cfg = load_roi_config()
    post_ch = set(roi_cfg["channels_egi64"]["parietal"] + roi_cfg["channels_egi64"]["occipital"])
    ch = pd.read_csv(deriv / "specparam/specparam_channel_results_qc.csv")
    if "fit_valid" in ch.columns:
        ch = ch[ch["fit_valid"]]
    ch = ch[ch["channel"].isin(post_ch)]
    rows = []
    for ch_name, sub_ch in ch.groupby("channel"):
        m = participants.merge(sub_ch, on=["subject_id", "group"], how="inner")
        m = m.dropna(subset=["aperiodic_exponent", "group", "age_months", "sex", "IQ_total", "usable_epochs"])
        if len(m) < 10 or m["group"].nunique() < 2:
            continue
        res = run_ols(f"aperiodic_exponent ~ C(group){COVARIATE_FORMULA}", m)
        term = [t for t in res.params.index if t.startswith("C(group)")][0]
        rows.append(
            {
                "channel": ch_name,
                "coef": res.params[term],
                "pvalue": res.pvalues[term],
                "n_obs": len(m),
            }
        )
    out = pd.DataFrame(rows)
    if not out.empty:
        _, p_adj = fdr_correction(out["pvalue"].values)
        out["pvalue_fdr"] = p_adj
        out["significant_fdr"] = out["pvalue_fdr"] < 0.05
    return out


def main() -> None:
    args = _parse_args()
    cfg = load_config(Path(args.config))
    deriv = Path(cfg["paths"]["derivatives_root"])
    stats_dir = deriv / "stats"
    stats_dir.mkdir(parents=True, exist_ok=True)

    subjects_csv = PROJECT_ROOT / "data/participants/external_validation_subjects_hbn_eeg_balanced_100x2.csv"
    subtype_meta = assign_asd_subtype(subjects_csv)

    participants = load_analysis_participants(cfg)
    participants = attach_usable_epochs(participants, deriv)
    participants = exclude_specparam_low_quality(participants, deriv)
    participants = participants.merge(subtype_meta, on="subject_id", how="left")
    participants.loc[participants["group"] == "TD", "asd_subtype"] = "td"

    roi = pd.read_csv(deriv / "roi/specparam_subject_global.csv")

    all_rows: list[dict] = []
    cohort_sizes = []

    comparisons = [
        ("asd_adhd_only_vs_td", "asd_adhd_only"),
        ("full_asd_vs_td", None),
        ("asd_no_adhd_vs_td", "asd_no_adhd"),
    ]

    for label, subtype in comparisons:
        if subtype is None:
            asd_ids = participants.loc[participants["group"] == "ASD", "subject_id"]
            df = participants[participants["subject_id"].isin(asd_ids) | (participants["group"] == "TD")].copy()
            df = df.merge(roi, on=["subject_id", "group"], how="inner")
            df["posterior_exponent"] = df[["parietal_exponent", "occipital_exponent"]].mean(axis=1)
            post_off = (
                pd.read_csv(deriv / "roi/specparam_subject_roi_long.csv")
                .query("roi in ['parietal', 'occipital']")
                .groupby(["subject_id", "group"])["offset"]
                .mean()
                .reset_index(name="posterior_offset")
            )
            df = df.merge(post_off, on=["subject_id", "group"], how="left")
            subset_part = participants[participants["subject_id"].isin(asd_ids) | (participants["group"] == "TD")]
        else:
            df = _prepare_df(cfg, subtype, participants, roi, deriv)
            subset_part = participants[
                participants["subject_id"].isin(
                    participants.loc[participants["asd_subtype"] == subtype, "subject_id"]
                )
                | (participants["group"] == "TD")
            ]

        n_asd = int((df["group"] == "ASD").sum())
        n_td = int((df["group"] == "TD").sum())
        cohort_sizes.append({"comparison": label, "n_asd": n_asd, "n_td": n_td, "n_model": len(df)})

        all_rows.extend(_run_outcomes(df, label))
        all_rows.extend(_run_e38(subset_part, deriv, label))

        if label == "asd_adhd_only_vs_td":
            ch_df = _run_posterior_channels(subset_part, deriv)
            save_csv(ch_df.sort_values("pvalue"), stats_dir / "asd_adhd_only_posterior_channels.csv")

    res_df = pd.DataFrame(all_rows)
    save_csv(res_df, stats_dir / "asd_adhd_comorbid_hypothesis_test.csv")
    save_csv(pd.DataFrame(cohort_sizes), stats_dir / "asd_adhd_comorbid_cohort_sizes.csv")

    print("=== Cohort sizes ===")
    print(pd.DataFrame(cohort_sizes).to_string(index=False))
    print("\n=== Key results (group term) ===")
    key = res_df[res_df["term"].str.contains("group", na=False)].copy()
    for comp in key["model"].unique():
        print(f"\n--- {comp} ---")
        sub = key[key["model"] == comp]
        for outcome in ["global_exponent", "posterior_exponent", "occipital_exponent", "E38_exponent"]:
            r = sub[sub["outcome"] == outcome]
            if len(r):
                rr = r.iloc[0]
                print(
                    f"  {outcome}: beta={rr['coef']:.4f}, p={rr['pvalue']:.4f}, n={int(rr['n_obs'])}"
                )
    ch_path = stats_dir / "asd_adhd_only_posterior_channels.csv"
    if ch_path.exists():
        ch_df = pd.read_csv(ch_path)
        sig = int(ch_df["significant_fdr"].sum()) if "significant_fdr" in ch_df.columns else 0
        print(f"\n=== ASD+ADHD only: posterior FDR sig {sig}/{len(ch_df)} ===")
        print(ch_df.nsmallest(5, "pvalue")[["channel", "coef", "pvalue", "pvalue_fdr"]].to_string(index=False))


if __name__ == "__main__":
    main()
