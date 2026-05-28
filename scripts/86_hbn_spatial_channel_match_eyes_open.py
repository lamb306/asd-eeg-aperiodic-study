#!/usr/bin/env python
"""
HBN eyes_open：主研究后部通道 → HBN 空间最近邻（GSN-128 全网格），并重算组间统计。

- 128 全网格：真实空间最近邻（如 E33→E67）
- E1–E64 子集：展示覆盖不足导致的塌缩（如 E33→E62）
- 指标：优先用 87 脚本补提的 128 通道 specparam
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config, load_roi_config  # noqa: E402
from src.io_utils import attach_usable_epochs, load_analysis_participants, save_csv  # noqa: E402
from src.qc_utils import flag_invalid_fits, summarize_subject_qc  # noqa: E402
from src.spatial_channel_match import (  # noqa: E402
    MAIN_MONTAGE,
    build_comprehensive_mapping_table,
    load_hbn_e64_subset_positions,
    load_hbn128_positions,
    load_main_positions,
    main_to_hbn128_map,
)
from src.stats_utils import model_results_to_row, run_ols  # noqa: E402

MAIN_SIG_CHANNELS = ("E33", "E36", "E37", "E38")
COVARIATE_FORMULA = " + age_months + C(sex) + IQ_total + usable_epochs"
GROUP_TERM = "C(group)[T.TD]"
STRICT_QC = {
    "min_r_squared": 0.9,
    "exponent_min": 0.0,
    "exponent_max": 5.0,
    "fit_error_top_percentile": 5.0,
    "subject_invalid_channel_ratio_max": 0.2,
}


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="HBN eyes_open 空间通道匹配分析（128 网格）")
    p.add_argument(
        "--config",
        default=str(PROJECT_ROOT / "config/config_external_hbn_resting_100x2_eyes_open.yaml"),
    )
    p.add_argument("--min-epochs", type=int, default=60, help="目标 epoch 阈值（若不可达则降级为 30）")
    p.add_argument(
        "--skip-supplemental",
        action="store_true",
        help="不加载 128 补提 specparam（仅输出映射表与 E64 子集分析）",
    )
    return p.parse_args()


def apply_strict_cohort(
    cfg: dict,
    deriv: Path,
    min_epochs_target: int,
) -> tuple[pd.DataFrame, pd.DataFrame, int]:
    ch_raw = pd.read_csv(deriv / "specparam/specparam_channel_results.csv")
    ch_qc = flag_invalid_fits(ch_raw, STRICT_QC)
    subj_qc = summarize_subject_qc(
        ch_qc,
        max_invalid_ratio=STRICT_QC["subject_invalid_channel_ratio_max"],
    )

    pre = pd.read_csv(deriv / "qc/preproc_summary.csv")
    pre["subject_id"] = pre["subject_id"].astype(str)
    max_epochs = int(pre.loc[pre["status"] == "ok", "usable_epochs"].max()) if len(pre) else 0

    min_epochs = min_epochs_target
    if max_epochs < min_epochs_target:
        print(
            f"[WARN] eyes_open 最大可用 epoch={max_epochs}，无法达到 min_epochs={min_epochs_target}；"
            "严格 QC 分析回退 min_epochs=30"
        )
        min_epochs = 30

    participants = load_analysis_participants(cfg, min_epochs=min_epochs)
    participants = attach_usable_epochs(participants, deriv)
    bad = subj_qc.loc[subj_qc["low_quality_subject"] == 1, "subject_id"].astype(str)
    participants = participants[~participants["subject_id"].isin(bad)].copy()
    return participants, ch_qc, min_epochs


def load_supplemental_qc(deriv: Path) -> pd.DataFrame | None:
    path = deriv / "specparam/specparam_channel_results_supplemental_128grid_qc.csv"
    if not path.exists():
        path = deriv / "specparam/specparam_channel_results_supplemental_128grid.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path)
    if "fit_valid" not in df.columns:
        df = flag_invalid_fits(df, STRICT_QC)
    return df


def _mean_exponent(
    sid: str,
    channels: list[str],
    ch_qc: pd.DataFrame,
    supp_qc: pd.DataFrame | None,
) -> float:
    """从 E64 主结果和/或 128 补提结果取通道均值。"""
    vals: list[float] = []
    ch_valid = ch_qc[ch_qc["fit_valid"]]
    for ch in channels:
        hit = ch_valid[(ch_valid["subject_id"] == sid) & (ch_valid["channel"] == ch)]
        if not hit.empty:
            vals.append(float(hit.iloc[0]["aperiodic_exponent"]))
            continue
        if supp_qc is not None:
            supp_valid = supp_qc[supp_qc["fit_valid"]] if "fit_valid" in supp_qc.columns else supp_qc
            hit2 = supp_valid[(supp_valid["subject_id"] == sid) & (supp_valid["channel"] == ch)]
            if not hit2.empty:
                vals.append(float(hit2.iloc[0]["aperiodic_exponent"]))
    return float(np.mean(vals)) if vals else np.nan


def subject_metrics_from_channels(
    participants: pd.DataFrame,
    ch_qc: pd.DataFrame,
    map128: dict[str, str],
    map_e64: dict[str, str],
    occipital_main: list[str],
    parietal_main: list[str],
    supp_qc: pd.DataFrame | None,
) -> pd.DataFrame:
    ch = ch_qc[ch_qc["fit_valid"]].copy()
    rows = []
    ch128 = [map128[c] for c in MAIN_SIG_CHANNELS]
    ch64 = [map_e64[c] for c in MAIN_SIG_CHANNELS]
    occ128 = list({map128[c] for c in occipital_main})
    par128 = list({map128[c] for c in parietal_main})
    post128 = list(set(occ128) | set(par128))
    occ64 = list({map_e64[c] for c in occipital_main})
    par64 = list({map_e64[c] for c in parietal_main})
    post64 = list(set(occ64) | set(par64))

    for _, part in participants.iterrows():
        sid = str(part["subject_id"])
        if ch[ch["subject_id"] == sid].empty and (supp_qc is None or supp_qc[supp_qc["subject_id"] == sid].empty):
            continue
        row = {
            "subject_id": sid,
            "group": part["group"],
            "age_months": part.get("age_months"),
            "sex": part.get("sex"),
            "IQ_total": part.get("IQ_total"),
            "usable_epochs": part.get("usable_epochs"),
        }

        def set_mean(chans: list[str], key: str, use_supp: bool) -> None:
            row[key] = _mean_exponent(sid, chans, ch_qc, supp_qc if use_supp else None)

        set_mean(list(MAIN_SIG_CHANNELS), "original_post4_exponent", False)
        set_mean(["E38"], "original_E38_exponent", False)
        set_mean(occipital_main, "original_occipital_exponent", False)
        set_mean(occipital_main + parietal_main, "original_posterior_all_exponent", False)

        set_mean(ch64, "matched_e64subset_post4_exponent", False)
        set_mean([map_e64["E38"]], "matched_e64subset_E38_exponent", False)
        set_mean(occ64, "matched_e64subset_occipital_exponent", False)
        set_mean(post64, "matched_e64subset_posterior_exponent", False)

        set_mean(ch128, "matched128_post4_exponent", True)
        set_mean([map128["E38"]], "matched128_E38_exponent", True)
        set_mean(occ128, "matched128_occipital_exponent", True)
        set_mean(post128, "matched128_posterior_exponent", True)

        sub = ch[ch["subject_id"] == sid]
        row["global_exponent"] = float(sub["aperiodic_exponent"].mean()) if not sub.empty else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def run_models(df: pd.DataFrame, label: str) -> pd.DataFrame:
    outcomes = [
        "global_exponent",
        "original_E38_exponent",
        "matched_e64subset_E38_exponent",
        "matched128_E38_exponent",
        "original_post4_exponent",
        "matched_e64subset_post4_exponent",
        "matched128_post4_exponent",
        "original_occipital_exponent",
        "matched_e64subset_occipital_exponent",
        "matched128_occipital_exponent",
        "original_posterior_all_exponent",
        "matched_e64subset_posterior_exponent",
        "matched128_posterior_exponent",
    ]
    all_rows = []
    for outcome in outcomes:
        if outcome not in df.columns:
            continue
        formula = f"{outcome} ~ C(group){COVARIATE_FORMULA}"
        sub = df.dropna(subset=[outcome, "group", "age_months", "sex", "IQ_total", "usable_epochs"])
        if len(sub) < 10 or sub["group"].nunique() < 2:
            continue
        all_rows.extend(model_results_to_row(run_ols(formula, sub), label, outcome))
    return pd.DataFrame(all_rows)


def main() -> None:
    args = _parse_args()
    cfg = load_config(Path(args.config))
    deriv = Path(cfg["paths"]["derivatives_root"])
    stats_dir = deriv / "stats"
    stats_dir.mkdir(parents=True, exist_ok=True)

    main_pos = load_main_positions()
    roi_cfg = load_roi_config()
    parietal_ch = roi_cfg["channels_egi64"]["parietal"]
    occipital_ch = roi_cfg["channels_egi64"]["occipital"]
    map_channels = sorted(set(MAIN_SIG_CHANNELS) | set(parietal_ch) | set(occipital_ch))

    mapping = build_comprehensive_mapping_table(main_pos, map_channels)
    save_csv(mapping, stats_dir / "spatial_channel_mapping_main_to_hbn_128grid.csv")

    # 兼容旧文件名：E64 子集列
    legacy = mapping.rename(
        columns={
            "hbn_nearest_e64_subset": "hbn_matched_channel",
            "dist_main_to_e64_subset_mm": "euclidean_distance_mm",
        }
    )
    save_csv(legacy, stats_dir / "spatial_channel_mapping_main_to_hbn.csv")

    map128 = main_to_hbn128_map(mapping)
    map_e64 = dict(zip(mapping["main_channel"], mapping["hbn_nearest_e64_subset"], strict=True))

    supp_qc = None if args.skip_supplemental else load_supplemental_qc(deriv)
    if supp_qc is None and not args.skip_supplemental:
        print(
            "[WARN] 未找到 128 补提 specparam；请先运行 scripts/87_hbn_extract_supplemental_128_channels_eyes_open.py"
        )

    participants, ch_qc, min_epochs_used = apply_strict_cohort(cfg, deriv, args.min_epochs)
    save_csv(ch_qc, deriv / "specparam/specparam_channel_results_qc_strict_r09.csv")

    subj_metrics = subject_metrics_from_channels(
        participants, ch_qc, map128, map_e64, occipital_ch, parietal_ch, supp_qc
    )
    save_csv(subj_metrics, stats_dir / "spatial_match_subject_metrics_eyes_open.csv")

    models = run_models(subj_metrics, "spatial_match_eyes_open_strict")
    save_csv(models, stats_dir / "spatial_match_group_models_eyes_open.csv")

    OUTCOME_LABELS = {
        "global_exponent": "global",
        "original_E38_exponent": "original_HBN_E38",
        "matched_e64subset_E38_exponent": "matched_E64subset_E38_equiv_collapsed",
        "matched128_E38_exponent": "matched_GSN128_E38_equiv",
        "original_post4_exponent": "original_E33_E36_E37_E38_mean",
        "matched_e64subset_post4_exponent": "matched_E64subset_4ch_mean_collapsed",
        "matched128_post4_exponent": "matched_GSN128_4ch_mean",
        "original_occipital_exponent": "original_occipital_ROI",
        "matched_e64subset_occipital_exponent": "matched_E64subset_occipital",
        "matched128_occipital_exponent": "matched_GSN128_occipital",
        "original_posterior_all_exponent": "original_posterior_ROI",
        "matched_e64subset_posterior_exponent": "matched_E64subset_posterior",
        "matched128_posterior_exponent": "matched_GSN128_posterior",
    }

    if models.empty:
        print("[ERROR] 无有效回归结果")
        summary = pd.DataFrame()
    else:
        key = models.loc[models["term"] == GROUP_TERM].copy()
        summary = key[["outcome", "coef", "pvalue", "n_obs"]].rename(
            columns={"coef": "beta_TD_minus_ASD", "pvalue": "p_value"}
        )
        summary["analysis_label"] = summary["outcome"].map(OUTCOME_LABELS)
        summary["epoch_threshold_used"] = min_epochs_used
        summary["hbn_montage"] = "GSN-HydroCel-128"
        summary["has_supplemental_128_specparam"] = supp_qc is not None
    save_csv(summary, stats_dir / "spatial_match_results_summary_eyes_open.csv")

    hbn128 = load_hbn128_positions()
    print(f"Analysis n={len(subj_metrics)} (ASD={(subj_metrics['group']=='ASD').sum()}, TD={(subj_metrics['group']=='TD').sum()})")
    print(f"Epoch threshold: >={min_epochs_used}")
    print("\n=== 主研究显著通道：128 全网格 vs E1–E64 子集 ===")
    sig = mapping[mapping["main_channel"].isin(MAIN_SIG_CHANNELS)][
        [
            "main_channel",
            "hbn_nearest_128",
            "dist_main_to_128_mm",
            "in_e1_e64_analysis",
            "hbn_nearest_e64_subset",
            "dist_main_to_e64_subset_mm",
            "same_label_on_128_mm",
        ]
    ]
    print(sig.to_string(index=False))

    if not summary.empty:
        print("\n=== Group models (beta = TD - ASD) ===")
        print(summary[["analysis_label", "beta_TD_minus_ASD", "p_value", "n_obs"]].to_string(index=False))

    e38_row = sig[sig["main_channel"] == "E38"].iloc[0]
    print(
        f"\nE38: 128→{e38_row['hbn_nearest_128']} ({e38_row['dist_main_to_128_mm']:.1f} mm); "
        f"同名 E38 偏差 {e38_row['same_label_on_128_mm']:.1f} mm; "
        f"E64子集→{e38_row['hbn_nearest_e64_subset']} ({e38_row['dist_main_to_e64_subset_mm']:.1f} mm)"
    )


if __name__ == "__main__":
    main()
