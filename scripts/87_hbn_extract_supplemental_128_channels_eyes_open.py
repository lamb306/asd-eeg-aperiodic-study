#!/usr/bin/env python
"""
从 HBN 原始 .set 为 GSN-128 空间匹配通道补提 PSD + specparam（eyes_open）。

主流程仅保留 E1–E64；当 128 全网格最近邻为 E67/E72/… 时需本脚本补数据。
预处理与主流程一致：睁眼拼接、滤波、重采样、分 epoch；**不重复 ICA**（补通道分析）。
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import mne
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config, setup_logging  # noqa: E402
from src.eeg_preprocessing import apply_filters, make_epochs, resample_if_needed  # noqa: E402
from src.external_hbn import crop_hbn_resting_segments, resting_set_path  # noqa: E402
from src.io_utils import load_analysis_participants, save_csv  # noqa: E402
from src.psd_utils import compute_psd_from_epochs, psd_to_long_df  # noqa: E402
from src.qc_utils import flag_invalid_fits  # noqa: E402
from src.spatial_channel_match import (  # noqa: E402
    build_comprehensive_mapping_table,
    load_main_positions,
    supplemental_channels_from_mapping,
)
from src.specparam_utils import fit_subject_specparam  # noqa: E402

logger = logging.getLogger(__name__)

STRICT_QC = {
    "min_r_squared": 0.9,
    "exponent_min": 0.0,
    "exponent_max": 5.0,
    "fit_error_top_percentile": 5.0,
    "subject_invalid_channel_ratio_max": 0.2,
}


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="HBN eyes_open 补提 128 网格通道 specparam")
    p.add_argument(
        "--config",
        default=str(PROJECT_ROOT / "config/config_external_hbn_resting_100x2_eyes_open.yaml"),
    )
    p.add_argument(
        "--mapping-csv",
        type=Path,
        default=None,
        help="spatial_channel_mapping_main_to_hbn_128grid.csv（默认由本脚本生成）",
    )
    p.add_argument("--limit-subjects", type=int, default=None)
    p.add_argument("--channels", nargs="*", default=None, help="覆盖自动补提通道列表")
    p.add_argument("--overwrite", action="store_true")
    return p.parse_args()


def _raw_path_for_subject(cfg: dict, row: pd.Series) -> Path | None:
    for key in ("raw_EEG_file_resting", "raw_EEG_file"):
        rel = str(row.get(key) or "").strip()
        if not rel:
            continue
        p = Path(rel)
        if not p.is_absolute():
            p = PROJECT_ROOT / p
        if p.exists():
            return p
    root = Path(cfg["paths"]["raw_data"])
    release = str(row.get("release", "")).strip()
    sid = str(row["subject_id"])
    found = resting_set_path(root, release, sid)
    return found


def extract_supplemental_subject(
    raw_path: Path,
    cfg: dict,
    channels: list[str],
    group: str,
    subject_id: str,
) -> pd.DataFrame | None:
    """返回 specparam 长表行（每通道一行）。"""
    eeg_cfg = cfg.get("eeg", {})
    filt = cfg.get("filter", {})
    epoch_cfg = cfg.get("epochs", {})
    psd_cfg = cfg.get("psd", {})
    sp_cfg = cfg.get("specparam", {})

    raw = mne.io.read_raw_eeglab(raw_path, preload=False, verbose=False)
    available = [c for c in channels if c in raw.ch_names]
    missing = sorted(set(channels) - set(available))
    if missing:
        logger.warning("%s 缺少通道: %s", subject_id, missing)
    if not available:
        return None
    raw.pick(available)
    raw.load_data(verbose=False)

    seg_mode = eeg_cfg.get("hbn_resting_segment_mode", "eyes_open")
    raw = crop_hbn_resting_segments(raw, raw_path, mode=str(seg_mode))

    raw = apply_filters(
        raw,
        l_freq=float(filt.get("highpass_hz", 0.5)),
        h_freq=float(filt.get("lowpass_hz", 45.0)),
        notch_freq=float(filt.get("notch_hz", 60.0)),
        notch_enabled=bool(filt.get("notch_enabled", True)),
    )
    raw = resample_if_needed(raw, float(eeg_cfg.get("sampling_rate_target", 250)))

    epochs = make_epochs(
        raw,
        duration=float(epoch_cfg.get("duration_sec", 2.0)),
        overlap=float(epoch_cfg.get("overlap_sec", 0.0)),
        reject_uv=float(epoch_cfg.get("reject_amplitude_uv", 500.0)),
    )
    if len(epochs) < 1:
        return None

    welch = psd_cfg.get("welch", {})
    freqs, psd, ch_names = compute_psd_from_epochs(
        epochs,
        fmin=float(welch.get("fmin", 1.0)),
        fmax=float(welch.get("fmax", 40.0)),
        welch_cfg=welch,
    )
    psd_df = psd_to_long_df(subject_id, group, freqs, psd, ch_names)
    return fit_subject_specparam(psd_df, sp_cfg)


def main() -> None:
    args = _parse_args()
    cfg = load_config(Path(args.config))
    setup_logging(cfg, name="supplemental_128_channels")
    deriv = Path(cfg["paths"]["derivatives_root"])
    stats_dir = deriv / "stats"
    stats_dir.mkdir(parents=True, exist_ok=True)

    main_pos = load_main_positions()
    from src.config import load_roi_config

    roi = load_roi_config()
    map_ch = sorted(
        set(roi["channels_egi64"]["occipital"])
        | set(roi["channels_egi64"]["parietal"])
        | {"E33", "E36", "E37", "E38"}
    )
    mapping = build_comprehensive_mapping_table(main_pos, map_ch)
    mapping_path = stats_dir / "spatial_channel_mapping_main_to_hbn_128grid.csv"
    save_csv(mapping, mapping_path)

    if args.channels:
        channels = sorted(args.channels, key=lambda x: int(x[1:]))
    else:
        channels = supplemental_channels_from_mapping(mapping)
    print(f"补提通道 ({len(channels)}): {', '.join(channels)}")

    out_csv = deriv / "specparam" / "specparam_channel_results_supplemental_128grid.csv"
    if out_csv.exists() and not args.overwrite:
        print(f"已存在 {out_csv}，跳过（使用 --overwrite 重跑）")
        return

    min_epochs = 30
    pre = pd.read_csv(deriv / "qc/preproc_summary.csv")
    max_ep = int(pre.loc[pre["status"] == "ok", "usable_epochs"].max()) if len(pre) else 0
    if max_ep < int(cfg.get("epochs", {}).get("min_usable_epochs", 60)):
        min_epochs = 30

    participants = load_analysis_participants(cfg, min_epochs=min_epochs)
    if args.limit_subjects:
        participants = participants.head(args.limit_subjects).copy()

    all_rows: list[pd.DataFrame] = []
    n_fail = 0
    for _, row in participants.iterrows():
        sid = str(row["subject_id"])
        raw_path = _raw_path_for_subject(cfg, row)
        if raw_path is None or not raw_path.exists():
            logger.warning("%s: 无 raw .set", sid)
            n_fail += 1
            continue
        try:
            fit_df = extract_supplemental_subject(
                raw_path, cfg, channels, str(row["group"]), sid
            )
        except Exception as exc:
            logger.warning("%s 补提失败: %s", sid, exc)
            n_fail += 1
            continue
        if fit_df is None or fit_df.empty:
            n_fail += 1
            continue
        all_rows.append(fit_df)

    if not all_rows:
        print("[ERROR] 无成功补提结果")
        sys.exit(1)

    out = pd.concat(all_rows, ignore_index=True)
    save_csv(out, out_csv)
    qc = flag_invalid_fits(out, STRICT_QC)
    save_csv(qc, deriv / "specparam" / "specparam_channel_results_supplemental_128grid_qc.csv")
    print(f"完成: {out['subject_id'].nunique()} 被试, {len(out)} 通道行 → {out_csv}")
    print(f"失败/跳过: {n_fail}")


if __name__ == "__main__":
    main()
