#!/usr/bin/env python
"""
79_build_external_hbn_participants.py
-------------------------------------
从 60x60 名单 + 下载审计表生成外部验证 participants 表，并映射本地 .set 路径。

输出:
  data/participants/participants_external_hbn_60x60.csv
  data/participants/participants_external_hbn_60x60_resting.csv  # 仅 has_resting，供静息预处理
  data/participants/external_hbn_60x60_availability_summary.csv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.external_hbn import build_participants_external_hbn  # noqa: E402
from src.io_utils import save_csv  # noqa: E402


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="构建 HBN 外部验证 participants 表")
    p.add_argument(
        "--subjects-csv",
        type=Path,
        default=PROJECT_ROOT / "data/participants/external_validation_subjects_hbn_eeg_balanced_60x60.csv",
    )
    p.add_argument(
        "--audit-csv",
        type=Path,
        default=PROJECT_ROOT / "data/participants/external_hbn_eeg_download_audit_60x60.csv",
    )
    p.add_argument(
        "--external-eeg-root",
        type=Path,
        default=PROJECT_ROOT / "data/external_hbn_eeg",
    )
    p.add_argument(
        "--out-all",
        type=Path,
        default=PROJECT_ROOT / "data/participants/participants_external_hbn_60x60.csv",
    )
    p.add_argument(
        "--out-resting",
        type=Path,
        default=PROJECT_ROOT / "data/participants/participants_external_hbn_60x60_resting.csv",
    )
    return p.parse_args()


def availability_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = [
        {
            "metric": "n_subjects",
            "ASD": int((df["group"] == "ASD").sum()),
            "TD": int((df["group"] == "TD").sum()),
            "total": len(df),
        },
        {
            "metric": "has_resting",
            "ASD": int(df.loc[df["group"] == "ASD", "has_resting"].sum()),
            "TD": int(df.loc[df["group"] == "TD", "has_resting"].sum()),
            "total": int(df["has_resting"].sum()),
        },
        {
            "metric": "has_movie_thepresent",
            "ASD": int(df.loc[df["group"] == "ASD", "has_movie"].sum()),
            "TD": int(df.loc[df["group"] == "TD", "has_movie"].sum()),
            "total": int(df["has_movie"].sum()),
        },
        {
            "metric": "has_both_resting_and_movie",
            "ASD": int(df.loc[df["group"] == "ASD", ["has_resting", "has_movie"]].all(axis=1).sum()),
            "TD": int(df.loc[df["group"] == "TD", ["has_resting", "has_movie"]].all(axis=1).sum()),
            "total": int((df["has_resting"] & df["has_movie"]).sum()),
        },
        {
            "metric": "resting_only_no_movie",
            "ASD": int(df.loc[(df["group"] == "ASD") & (df["has_resting"] == 1) & (df["has_movie"] == 0)].shape[0]),
            "TD": int(df.loc[(df["group"] == "TD") & (df["has_resting"] == 1) & (df["has_movie"] == 0)].shape[0]),
            "total": int(((df["has_resting"] == 1) & (df["has_movie"] == 0)).sum()),
        },
    ]
    return pd.DataFrame(rows)


def main() -> None:
    args = _parse_args()
    df = build_participants_external_hbn(
        subjects_csv=args.subjects_csv,
        audit_csv=args.audit_csv,
        external_eeg_root=args.external_eeg_root,
        project_root=PROJECT_ROOT,
    )

    save_csv(df, args.out_all)

    resting_df = df[df["has_resting"].astype(int) == 1].copy()
    resting_df["included_final"] = 1
    resting_df["raw_EEG_file"] = resting_df["raw_EEG_file_resting"]
    save_csv(resting_df, args.out_resting)

    summ_path = args.out_all.parent / "external_hbn_60x60_availability_summary.csv"
    save_csv(availability_summary(df), summ_path)

    missing_rest = df.loc[df["has_resting"] == 0, "subject_id"].tolist()
    print(f"Wrote {args.out_all} ({len(df)} subjects)")
    print(f"Wrote {args.out_resting} ({len(resting_df)} with resting .set)")
    print(f"Wrote {summ_path}")
    if missing_rest:
        print(f"Missing RestingState .set: {missing_rest}")


if __name__ == "__main__":
    main()
