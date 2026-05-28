"""主研究 GSN-64 与 HBN GSN-128 空间通道匹配。"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import mne
import numpy as np
import pandas as pd

MAIN_MONTAGE = "GSN-HydroCel-64_1.0"
HBN_MONTAGE_FULL = "GSN-HydroCel-128"


def positions_dict(montage: mne.channels.DigMontage) -> dict[str, np.ndarray]:
    return {k: np.asarray(v, dtype=float) for k, v in montage.get_positions()["ch_pos"].items()}


def load_main_positions() -> dict[str, np.ndarray]:
    return positions_dict(mne.channels.make_standard_montage(MAIN_MONTAGE))


def load_hbn128_positions() -> dict[str, np.ndarray]:
    pos = positions_dict(mne.channels.make_standard_montage(HBN_MONTAGE_FULL))
    return {k: v for k, v in pos.items() if k.upper().startswith("E")}


def load_hbn_e64_subset_positions() -> dict[str, np.ndarray]:
    pos = load_hbn128_positions()
    return {k: v for k, v in pos.items() if 1 <= int(k[1:]) <= 64}


def nearest_in_pool(
    target_pos: np.ndarray,
    pool: dict[str, np.ndarray],
) -> tuple[str, float]:
    best_ch, best_d = None, np.inf
    for ch, p in pool.items():
        d = float(np.linalg.norm(target_pos - p))
        if d < best_d:
            best_d, best_ch = d, ch
    return best_ch, best_d * 1000.0


def nearest_to_main_channel(
    main_ch: str,
    main_pos: dict[str, np.ndarray],
    pool: dict[str, np.ndarray],
) -> tuple[str, float]:
    if main_ch not in main_pos:
        raise KeyError(f"主研究通道不在 montage: {main_ch}")
    return nearest_in_pool(np.asarray(main_pos[main_ch], dtype=float), pool)


def channel_num(label: str) -> int:
    return int(label[1:])


def in_e1_e64(label: str) -> bool:
    return label.upper().startswith("E") and 1 <= channel_num(label) <= 64


def build_comprehensive_mapping_table(
    main_pos: dict[str, np.ndarray],
    channels: Iterable[str],
    hbn_full: dict[str, np.ndarray] | None = None,
    hbn_e64: dict[str, np.ndarray] | None = None,
) -> pd.DataFrame:
    """主研究通道 → 128 全网格 / E64 子集 / E64 对 128 目标的 relay。"""
    hbn_full = hbn_full or load_hbn128_positions()
    hbn_e64 = hbn_e64 or load_hbn_e64_subset_positions()

    rows = []
    for ch in channels:
        mx, my, mz = main_pos[ch]
        g128, d128 = nearest_to_main_channel(ch, main_pos, hbn_full)
        g64, d64 = nearest_to_main_channel(ch, main_pos, hbn_e64)
        p128 = np.asarray(hbn_full[g128], dtype=float)
        g_relay, d_relay = nearest_in_pool(p128, hbn_e64)
        same128 = (
            float(np.linalg.norm(np.asarray(main_pos[ch]) - hbn_full[ch]) * 1000)
            if ch in hbn_full
            else np.nan
        )
        hx, hy, hz = hbn_full[g128]
        rows.append(
            {
                "main_channel": ch,
                "main_x_m": mx,
                "main_y_m": my,
                "main_z_m": mz,
                "hbn_nearest_128": g128,
                "hbn_128_x_m": hx,
                "hbn_128_y_m": hy,
                "hbn_128_z_m": hz,
                "dist_main_to_128_mm": d128,
                "same_label_on_128_mm": same128,
                "in_e1_e64_analysis": in_e1_e64(g128),
                "hbn_nearest_e64_subset": g64,
                "dist_main_to_e64_subset_mm": d64,
                "hbn_e64_relay_to_128_target": g_relay,
                "dist_128_target_to_e64_relay_mm": d_relay,
                "hbn_montage": HBN_MONTAGE_FULL,
            }
        )
    return pd.DataFrame(rows)


def supplemental_channels_from_mapping(mapping: pd.DataFrame) -> list[str]:
    """128 匹配通道中不在 E1–E64 分析子集、需补提 specparam 的电极。"""
    chans = mapping["hbn_nearest_128"].astype(str).unique().tolist()
    return sorted([c for c in chans if not in_e1_e64(c)], key=channel_num)


def main_to_hbn128_map(mapping: pd.DataFrame) -> dict[str, str]:
    return dict(zip(mapping["main_channel"], mapping["hbn_nearest_128"], strict=True))
