#!/usr/bin/env python
"""构建 HBN 外部验证 movie（ThePresent）预处理 participants 表。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.external_hbn import build_participants_external_hbn_movie  # noqa: E402
from src.io_utils import save_csv  # noqa: E402


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="构建 HBN 外部 movie participants")
    p.add_argument(
        "--subjects-csv",
        type=Path,
        default=PROJECT_ROOT / "data/participants/external_validation_subjects_hbn_eeg_balanced_100x2.csv",
    )
    p.add_argument(
        "--external-eeg-root",
        type=Path,
        default=PROJECT_ROOT / "data/external_hbn_eeg",
    )
    p.add_argument(
        "--out-csv",
        type=Path,
        default=PROJECT_ROOT / "data/participants/participants_external_hbn_100x2_movie.csv",
    )
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    df = build_participants_external_hbn_movie(
        subjects_csv=args.subjects_csv,
        external_eeg_root=args.external_eeg_root,
        project_root=PROJECT_ROOT,
    )
    save_csv(df, args.out_csv)
    n_movie = int(df["has_movie"].sum()) if "has_movie" in df.columns else len(df)
    print(f"Wrote {args.out_csv} ({len(df)} rows, has_movie={n_movie})")


if __name__ == "__main__":
    main()
