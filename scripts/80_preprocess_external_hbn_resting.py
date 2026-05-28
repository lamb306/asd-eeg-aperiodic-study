#!/usr/bin/env python
"""
80_preprocess_external_hbn_resting.py
-------------------------------------
HBN 外部验证 — 静息（RestingState）预处理入口。

复用 src.eeg_preprocessing.batch_preprocess；输出写入 derivatives_external_hbn/，
不覆盖主分析 derivatives_*。

输入:
  config/config_external_hbn_resting_60x60.yaml
  data/participants/participants_external_hbn_60x60_resting.csv

输出:
  derivatives_external_hbn/resting/preprocessed/{subject_id}-raw.fif
  derivatives_external_hbn/resting/epochs/{subject_id}-epo.fif
  derivatives_external_hbn/resting/qc/*
  derivatives_external_hbn/resting/participants_analysis.csv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config, setup_logging  # noqa: E402
from src.eeg_preprocessing import batch_preprocess  # noqa: E402
from src.external_hbn import build_attrition_report  # noqa: E402
from src.io_utils import load_participants, save_csv  # noqa: E402


def build_preproc_summary(
    qc_df: pd.DataFrame,
    participants: pd.DataFrame,
    min_epochs: int,
) -> pd.DataFrame:
    if qc_df.empty:
        return qc_df
    merge_cols = ["subject_id", "group", "age_months", "sex", "IQ_total", "has_movie"]
    merge_cols = [c for c in merge_cols if c in participants.columns]
    base = participants[merge_cols].drop_duplicates("subject_id")
    summary = qc_df.merge(base, on=["subject_id", "group"], how="left", suffixes=("", "_meta"))
    if "group_meta" in summary.columns:
        summary["group"] = summary["group"].fillna(summary["group_meta"])
        summary = summary.drop(columns=["group_meta"])
    summary["min_epochs_required"] = min_epochs
    summary["meets_epoch_criterion"] = summary["usable_epochs"] >= min_epochs
    summary["ica_n_removed"] = summary["ica_removed_components"].apply(
        lambda x: len(x) if isinstance(x, list) else 0
    )
    summary["dropped_ref_n"] = summary["dropped_reference_channels"].apply(
        lambda x: len(x) if isinstance(x, list) else 0
    )
    col_order = [
        "subject_id", "group", "age_months", "sex", "IQ_total", "has_movie", "status",
        "usable_epochs", "usable_seconds", "meets_epoch_criterion",
        "min_epochs_required", "n_channels", "sampling_rate",
        "bad_channel_count", "ica_n_removed", "dropped_ref_n",
        "bad_channels", "ica_removed_components", "raw_file",
        "eeg_system", "resting_condition",
    ]
    cols = [c for c in col_order if c in summary.columns]
    extra = [c for c in summary.columns if c not in cols]
    return summary[cols + extra]


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="HBN 外部验证 RestingState 预处理")
    p.add_argument(
        "--config",
        type=str,
        default=str(PROJECT_ROOT / "config/config_external_hbn_resting_60x60.yaml"),
    )
    p.add_argument("--limit-subjects", type=int, default=None)
    p.add_argument(
        "--segment-mode",
        type=str,
        default=None,
        help="覆盖 eeg.hbn_resting_segment_mode: eyes_closed|eyes_open|continuous|none",
    )
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    cfg = load_config(Path(args.config))
    if args.segment_mode is not None:
        cfg.setdefault("eeg", {})["hbn_resting_segment_mode"] = args.segment_mode

    log = setup_logging(cfg, name="preprocess_external_hbn_resting")
    deriv = Path(cfg["paths"]["derivatives_root"])
    qc_dir = deriv / "qc"
    qc_dir.mkdir(parents=True, exist_ok=True)

    part_path = Path(cfg["paths"]["participants_file"])
    if not part_path.exists():
        log.error(
            "未找到 %s，请先运行 scripts/79_build_external_hbn_participants.py",
            part_path,
        )
        sys.exit(1)

    participants = load_participants(part_path, included_only=True)
    if args.limit_subjects is not None:
        participants = participants.head(max(0, args.limit_subjects)).copy()
        log.info("--limit-subjects=%d → %d 名", args.limit_subjects, len(participants))

    min_epochs = int(cfg.get("epochs", {}).get("min_usable_epochs", 60))
    log.info(
        "HBN 静息预处理: n=%d, min_epochs=%d, segment_mode=%s, notch=%s Hz",
        len(participants),
        min_epochs,
        cfg.get("eeg", {}).get("hbn_resting_segment_mode"),
        cfg.get("filter", {}).get("notch_hz"),
    )

    summary_raw, failures = batch_preprocess(participants, cfg)

    cohort_path = Path(
        cfg.get("paths", {}).get("selection_file", cfg["paths"]["participants_file"])
    )
    if not cohort_path.is_absolute():
        cohort_path = PROJECT_ROOT / cohort_path
    task_label = "movie" if "movie" in str(cfg.get("eeg", {}).get("task_condition", "")).lower() else "resting"
    cohort_label = cohort_path.stem.replace("external_validation_subjects_hbn_eeg_balanced_", "").replace(
        "participants_external_hbn_", ""
    )
    if cohort_path.exists():
        all_participants = pd.read_csv(cohort_path)
        if task_label == "movie" and part_path.exists():
            all_participants = pd.read_csv(part_path)
        if not all_participants.empty:
            attrition = build_attrition_report(
                all_participants,
                summary_raw,
                failures,
                min_epochs,
                cohort_label=cohort_label or "cohort",
                task_label=task_label,
            )
            save_csv(attrition, qc_dir / "attrition_summary.csv")
            log.info("流失报告: %s", qc_dir / "attrition_summary.csv")

    if not failures.empty:
        save_csv(failures, qc_dir / "preproc_failures.csv")

    if summary_raw.empty:
        log.error("预处理未成功任何被试。")
        sys.exit(1)

    summary = build_preproc_summary(summary_raw, participants, min_epochs)
    save_csv(summary, qc_dir / "preproc_summary.csv")

    low_epoch = summary[~summary["meets_epoch_criterion"]]
    if not low_epoch.empty:
        save_csv(low_epoch, qc_dir / "preproc_low_epoch_subjects.csv")
        save_csv(low_epoch, qc_dir / "participants_excluded_epochs.csv")

    passed_ids = summary.loc[summary["meets_epoch_criterion"], "subject_id"]
    analysis_df = participants[participants["subject_id"].isin(passed_ids)].copy()
    analysis_df = analysis_df.merge(
        summary[["subject_id", "usable_epochs", "usable_seconds", "meets_epoch_criterion"]],
        on="subject_id",
        how="left",
    )
    save_csv(analysis_df, deriv / "participants_analysis.csv")

    n_ok = int(summary["meets_epoch_criterion"].sum())
    log.info(
        "完成: 预处理成功 %d，epoch 达标 %d，失败 %d → %s",
        len(summary),
        n_ok,
        len(failures),
        qc_dir / "preproc_summary.csv",
    )


if __name__ == "__main__":
    main()
