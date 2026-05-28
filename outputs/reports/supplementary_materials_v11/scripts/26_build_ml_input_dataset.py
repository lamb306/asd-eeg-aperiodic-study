"""
Build subject-level ML input table for ASD vs TD EEG classification.

Output columns are designed to match `25_nested_cv_aperiodic_classifier.py`:
- group
- global_exponent, global_offset
- posterior_exponent (E33/E36/E37/E38 mean)
- frontal_exponent, central_exponent, temporal_exponent, parietal_exponent, occipital_exponent
- alpha_pw, alpha_cf, theta_pw, beta_pw
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build merged subject-level EEG ML dataset.")
    parser.add_argument(
        "--channel_csv",
        type=str,
        default="derivatives/specparam/specparam_channel_results_qc.csv",
        help="Channel-level specparam CSV path.",
    )
    parser.add_argument(
        "--roi_csv",
        type=str,
        default="derivatives/roi/specparam_subject_global.csv",
        help="Subject-level ROI/global CSV path.",
    )
    parser.add_argument(
        "--output_csv",
        type=str,
        default="outputs/tables/resting_features_locked.csv",
        help="Output merged CSV path.",
    )
    parser.add_argument(
        "--participants_csv",
        type=str,
        default="data/participants/participants.csv",
        help="Participants CSV path (for included_final filter).",
    )
    parser.add_argument(
        "--analysis_participants_csv",
        type=str,
        default="derivatives/participants_analysis.csv",
        help="Analysis cohort CSV path from preprocessing.",
    )
    parser.add_argument(
        "--specparam_subject_qc_csv",
        type=str,
        default="derivatives/specparam/specparam_qc_summary_subject.csv",
        help="Subject-level specparam QC summary CSV path.",
    )
    parser.add_argument(
        "--posterior_channels",
        type=str,
        default="E33,E36,E37,E38",
        help="Comma-separated posterior channels for posterior_exponent.",
    )
    parser.add_argument(
        "--periodic_scope",
        type=str,
        choices=["global", "posterior"],
        default="global",
        help="Aggregate periodic features over all channels or posterior channels only.",
    )
    return parser.parse_args()


def _require_columns(df: pd.DataFrame, required: List[str], name: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")


def main() -> None:
    args = parse_args()
    posterior_channels = [c.strip() for c in args.posterior_channels.split(",") if c.strip()]

    channel_path = Path(args.channel_csv)
    roi_path = Path(args.roi_csv)
    out_path = Path(args.output_csv)
    participants_path = Path(args.participants_csv)
    analysis_participants_path = Path(args.analysis_participants_csv)
    specparam_subject_qc_path = Path(args.specparam_subject_qc_csv)
    if not channel_path.exists():
        raise FileNotFoundError(f"channel_csv not found: {channel_path}")
    if not roi_path.exists():
        raise FileNotFoundError(f"roi_csv not found: {roi_path}")
    if not participants_path.exists():
        raise FileNotFoundError(f"participants_csv not found: {participants_path}")

    df_ch = pd.read_csv(channel_path)
    df_roi = pd.read_csv(roi_path)
    df_participants = pd.read_csv(participants_path)

    _require_columns(
        df_ch,
        [
            "subject_id",
            "group",
            "channel",
            "aperiodic_exponent",
            "alpha_pw",
            "alpha_cf",
            "theta_pw",
            "beta_pw",
        ],
        "channel_csv",
    )
    _require_columns(
        df_participants,
        ["subject_id", "group"],
        "participants_csv",
    )
    _require_columns(
        df_roi,
        [
            "subject_id",
            "group",
            "global_exponent",
            "global_offset",
            "frontal_exponent",
            "central_exponent",
            "temporal_exponent",
            "parietal_exponent",
            "occipital_exponent",
        ],
        "roi_csv",
    )

    df_ch["subject_id"] = df_ch["subject_id"].astype(str)
    df_ch["group"] = df_ch["group"].astype(str).str.upper()
    df_roi["subject_id"] = df_roi["subject_id"].astype(str)
    df_roi["group"] = df_roi["group"].astype(str).str.upper()
    df_participants["subject_id"] = df_participants["subject_id"].astype(str)
    df_participants["group"] = df_participants["group"].astype(str).str.upper()

    if "fit_valid" in df_ch.columns:
        df_ch = df_ch[df_ch["fit_valid"] == True].copy()  # noqa: E712

    cohort = df_participants[["subject_id", "group"]].drop_duplicates().copy()
    if "included_final" in df_participants.columns:
        inc = pd.to_numeric(df_participants["included_final"], errors="coerce")
        cohort = df_participants.loc[inc == 1, ["subject_id", "group"]].drop_duplicates().copy()

    if analysis_participants_path.exists():
        df_analysis = pd.read_csv(analysis_participants_path)
        _require_columns(df_analysis, ["subject_id", "group"], "analysis_participants_csv")
        df_analysis["subject_id"] = df_analysis["subject_id"].astype(str)
        df_analysis["group"] = df_analysis["group"].astype(str).str.upper()
        cohort = cohort.merge(
            df_analysis[["subject_id", "group"]].drop_duplicates(),
            on=["subject_id", "group"],
            how="inner",
        )

    if specparam_subject_qc_path.exists():
        df_qc = pd.read_csv(specparam_subject_qc_path)
        _require_columns(df_qc, ["subject_id", "low_quality_subject"], "specparam_subject_qc_csv")
        df_qc["subject_id"] = df_qc["subject_id"].astype(str)
        bad_ids = set(
            df_qc.loc[pd.to_numeric(df_qc["low_quality_subject"], errors="coerce") == 1, "subject_id"].tolist()
        )
        if bad_ids:
            cohort = cohort[~cohort["subject_id"].isin(bad_ids)].copy()

    # posterior_exponent: mean over user-defined posterior channels.
    df_post = (
        df_ch.loc[df_ch["channel"].isin(posterior_channels), ["subject_id", "group", "aperiodic_exponent"]]
        .groupby(["subject_id", "group"], as_index=False)
        .agg(posterior_exponent=("aperiodic_exponent", "mean"))
    )

    # periodic features: mean across channels (global or posterior-only).
    periodic_cols = ["alpha_pw", "alpha_cf", "theta_pw", "beta_pw"]
    if args.periodic_scope == "posterior":
        periodic_base = df_ch.loc[df_ch["channel"].isin(posterior_channels)].copy()
    else:
        periodic_base = df_ch.copy()

    df_periodic = (
        periodic_base[["subject_id", "group"] + periodic_cols]
        .groupby(["subject_id", "group"], as_index=False)
        .mean(numeric_only=True)
    )

    # Merge all subject-level features.
    merged = df_roi.merge(df_post, on=["subject_id", "group"], how="inner")
    merged = merged.merge(df_periodic, on=["subject_id", "group"], how="left")
    merged = merged.merge(cohort, on=["subject_id", "group"], how="inner")

    desired_cols = [
        "subject_id",
        "group",
        "global_exponent",
        "global_offset",
        "posterior_exponent",
        "frontal_exponent",
        "central_exponent",
        "temporal_exponent",
        "parietal_exponent",
        "occipital_exponent",
        "alpha_pw",
        "alpha_cf",
        "theta_pw",
        "beta_pw",
    ]
    merged = merged[desired_cols].copy()

    # Remove rows with missing required aperiodic features.
    aperiodic_required = [
        "global_exponent",
        "global_offset",
        "posterior_exponent",
        "frontal_exponent",
        "central_exponent",
        "temporal_exponent",
        "parietal_exponent",
        "occipital_exponent",
    ]
    before = len(merged)
    merged = merged.dropna(subset=aperiodic_required).reset_index(drop=True)
    dropped = before - len(merged)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(out_path, index=False)

    n_asd = int((merged["group"].astype(str).str.upper() == "ASD").sum())
    n_td = int((merged["group"].astype(str).str.upper() == "TD").sum())

    print("========== ML dataset built ==========")
    print(f"Saved: {out_path}")
    print(f"Rows: {len(merged)} | ASD: {n_asd} | TD: {n_td}")
    print(f"Dropped due to missing required aperiodic features: {dropped}")
    print(f"Periodic aggregation scope: {args.periodic_scope}")
    print("Missing count per periodic feature:")
    for c in periodic_cols:
        print(f"- {c}: {int(merged[c].isna().sum())}")


if __name__ == "__main__":
    main()
