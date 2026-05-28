#!/usr/bin/env python
"""
15_make_figures.py
------------------
生成论文用图（PDF + PNG）。

输入: derivatives/, outputs/
输出: outputs/figures/*.png, *.pdf
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config, setup_logging  # noqa: E402
from src.io_utils import load_analysis_participants  # noqa: E402
from src.plotting_utils import (  # noqa: E402
    plot_band_power_comparison,
    plot_box_scatter,
    plot_clinical_scatter,
    plot_exponent_topomap,
    plot_roi_exponent,
    plot_specparam_example,
)
from src.psd_utils import plot_group_mean_psd  # noqa: E402
from src.specparam_utils import fit_specparam_channel  # noqa: E402


def main() -> None:
    cfg = load_config()
    log = setup_logging(cfg, name="make_figures")

    deriv = Path(cfg["paths"]["derivatives_root"])
    fig_dir = Path(cfg["paths"]["outputs_root"]) / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    participants = load_analysis_participants(cfg)
    psd_dir = deriv / "psd"

    # 1. 组平均 PSD
    plot_group_mean_psd(psd_dir, participants, cfg, fig_dir / "fig01_group_mean_psd")

    # 2. specparam 拟合示例
    example_sid = participants["subject_id"].iloc[0]
    psd_path = psd_dir / f"{example_sid}_psd.csv"
    if psd_path.exists():
        psd_df = pd.read_csv(psd_path)
        ch = psd_df["channel"].iloc[0]
        sub = psd_df[psd_df["channel"] == ch].sort_values("frequency")
        freqs = sub["frequency"].values
        power = sub["power"].values
        try:
            fit = fit_specparam_channel(freqs, power, cfg["specparam"])
            from specparam import SpectralModel
            model = SpectralModel(aperiodic_mode=cfg["specparam"].get("aperiodic_mode", "fixed"))
            model.fit(freqs, power, cfg["specparam"].get("freq_range", [1, 40]))
            model_fit = model.fitted_spectrum_
            plot_specparam_example(
                freqs, power, model_fit,
                fig_dir / "fig02_specparam_example",
                title=f"{example_sid} {ch}",
            )
        except Exception as exc:
            log.warning("specparam 示例图失败: %s", exc)

    # 3-4. global exponent / offset
    roi_path = deriv / "roi" / "specparam_subject_global.csv"
    if roi_path.exists():
        roi_df = pd.read_csv(roi_path)
        plot_box_scatter(roi_df, "group", "global_exponent", fig_dir / "fig03_global_exponent",
                         title="Global aperiodic exponent", ylabel="Exponent")
        plot_box_scatter(roi_df, "group", "global_offset", fig_dir / "fig04_global_offset",
                         title="Global aperiodic offset", ylabel="Offset")

    # 5. ROI exponent
    roi_long_path = deriv / "roi" / "specparam_subject_roi_long.csv"
    if roi_long_path.exists():
        plot_roi_exponent(pd.read_csv(roi_long_path), fig_dir / "fig05_roi_exponent")

    # 6. 临床相关散点（ASD）
    if roi_path.exists():
        parts = load_analysis_participants(cfg)
        roi_df = pd.read_csv(roi_path)
        asd = parts[parts["group"] == cfg["groups"]["asd_label"]].merge(roi_df, on="subject_id", how="inner")
        if "ADOS_total" in asd.columns:
            plot_clinical_scatter(
                asd.dropna(subset=["ADOS_total", "global_exponent"]),
                "global_exponent", "ADOS_total",
                fig_dir / "fig06_clinical_ADOS_exponent",
                title="ADOS vs global exponent (ASD)",
            )

    # 7. 通道 topomap
    ch_path = deriv / "stats" / "channel_level_analysis.csv"
    ch_results = deriv / "specparam" / "specparam_channel_results_qc.csv"
    if ch_path.exists() and ch_results.exists():
        effects = pd.read_csv(ch_path).merge(
            pd.read_csv(ch_results)[["channel", "aperiodic_exponent"]].drop_duplicates("channel"),
            on="channel", how="left",
        )
        effects = effects.rename(columns={"coef": "group_effect"})
        if "group_effect" not in effects.columns:
            effects["group_effect"] = pd.read_csv(ch_path)["coef"]
        plot_exponent_topomap(
            pd.read_csv(ch_results).groupby("channel")["aperiodic_exponent"].mean().reset_index(),
            "aperiodic_exponent",
            fig_dir / "fig07_channel_exponent_topomap",
        )

    # 8. 传统 alpha vs specparam alpha peak
    trad_path = deriv / "stats" / "band_power_comparison.csv"
    if trad_path.exists():
        comp = pd.read_csv(trad_path)
        alpha = comp[comp["band"] == "alpha"]
        if not alpha.empty:
            fig_data_trad = alpha.rename(columns={"traditional_power": "band_power"})
            fig_data_trad["band"] = "alpha"
            sp = pd.read_csv(deriv / "specparam" / "specparam_channel_results_qc.csv")
            plot_band_power_comparison(
                pd.DataFrame({
                    "subject_id": alpha["subject_id"],
                    "band": "alpha",
                    "band_power": alpha["traditional_power"],
                }),
                sp,
                "alpha",
                fig_dir / "fig08_alpha_trad_vs_specparam",
            )

    log.info("所有图形已保存至 %s", fig_dir)


if __name__ == "__main__":
    main()
