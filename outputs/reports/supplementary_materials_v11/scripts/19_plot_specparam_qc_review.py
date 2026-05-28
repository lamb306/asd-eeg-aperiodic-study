#!/usr/bin/env python
"""
19_plot_specparam_qc_review.py
------------------------------
生成单被试 specparam 拟合 QC 图（肉眼检查用）。

输出: outputs/figures/qc_specparam_review/{subject_id}_fit.png
      outputs/figures/qc_specparam_review/qc_review_index.csv

用法（项目根目录）:
  python scripts/19_plot_specparam_qc_review.py
  python scripts/19_plot_specparam_qc_review.py --subjects S001 S016 T004
  python scripts/19_plot_specparam_qc_review.py --preset review_batch
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config, setup_logging  # noqa: E402
from src.io_utils import save_csv  # noqa: E402
from src.specparam_utils import fit_specparam_channel  # noqa: E402


def _mean_psd(psd_df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """被试全通道平均 PSD。"""
    g = psd_df.groupby("frequency", as_index=False)["power"].mean().sort_values("frequency")
    return g["frequency"].values, g["power"].values


def _model_linear_power(
    freqs: np.ndarray,
    offset: float,
    exponent: float,
    peak_params: np.ndarray | None,
) -> np.ndarray:
    """由 aperiodic + 峰参数重建线性功率（用于 log-log 叠加）。"""
    log_p = offset - exponent * np.log10(freqs)
    if peak_params is not None and len(peak_params) > 0:
        for cf, pw, bw in peak_params:
            # 高斯峰（log10 功率域，与 specparam 一致）
            log_p = log_p + pw * np.exp(-0.5 * ((freqs - cf) / max(bw, 1e-6)) ** 2)
    return np.power(10.0, log_p)


def plot_subject_fit(
    subject_id: str,
    group: str,
    freqs: np.ndarray,
    power: np.ndarray,
    sp_cfg: dict,
    out_path: Path,
    qc_row: pd.Series | None = None,
) -> dict:
    """单被试平均通道拟合图。"""
    fit = fit_specparam_channel(freqs, power, sp_cfg)
    peak_raw = None
    try:
        from specparam import SpectralModel

        m = SpectralModel(
            aperiodic_mode=sp_cfg.get("aperiodic_mode", "fixed"),
            verbose=False,
            peak_width_limits=tuple(sp_cfg.get("peak_width_limits", [1, 8])),
            max_n_peaks=sp_cfg.get("max_n_peaks", 6),
        )
        m.fit(freqs, power, sp_cfg.get("freq_range", [1.0, 40.0]))
        peak_raw = m.get_params("peak")
        if peak_raw is not None and len(np.asarray(peak_raw)) == 0:
            peak_raw = None
        ap = m.get_params("aperiodic")
        offset, exponent = float(ap[0]), float(ap[1])
    except Exception:
        offset = float(fit["aperiodic_offset"])
        exponent = float(fit["aperiodic_exponent"])

    model_power = _model_linear_power(freqs, offset, exponent, peak_raw)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.loglog(freqs, power, color="0.35", lw=1.5, alpha=0.85, label="PSD (channel mean)")
    ax.loglog(freqs, model_power, "r--", lw=2, label="specparam model")
    ax.axvline(1, color="0.7", ls=":", lw=0.8)
    ax.axvline(40, color="0.7", ls=":", lw=0.8)
    ax.set_xlim(freqs.min(), freqs.max())
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Power (linear)")
    title = f"{subject_id} ({group})  exp={fit['aperiodic_exponent']:.2f}  R²={fit['r_squared']:.3f}"
    if qc_row is not None:
        title += f"  invalid_ch={qc_row.get('invalid_channels', '')}"
    ax.set_title(title, fontsize=10)
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path.with_suffix(".png"), dpi=150, bbox_inches="tight")
    fig.savefig(out_path.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)
    return fit


def pick_review_subjects(qc: pd.DataFrame, n_each: int = 3) -> list[str]:
    """挑选 ASD/TD、拟合好/差、低质量 代表被试。"""
    ids: list[str] = []
    ok = qc[qc["low_quality_subject"] == 0].sort_values("mean_r_squared", ascending=False)
    bad = qc[qc["low_quality_subject"] == 1]
    poor_r2 = qc[qc["low_quality_subject"] == 0].sort_values("mean_r_squared")

    for grp in ["ASD", "TD"]:
        sub_ok = ok[ok["group"] == grp]
        sub_poor = poor_r2[poor_r2["group"] == grp]
        ids.extend(sub_ok.head(n_each)["subject_id"].tolist())
        ids.extend(sub_poor.head(n_each)["subject_id"].tolist())
    ids.extend(bad.head(4)["subject_id"].tolist())
  # 去重保序
    seen: set[str] = set()
    out = []
    for sid in ids:
        if sid not in seen:
            seen.add(sid)
            out.append(sid)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="生成 specparam 拟合 QC 图")
    parser.add_argument("--subjects", nargs="*", help="指定 subject_id，如 S001 T004")
    parser.add_argument(
        "--preset",
        choices=["review_batch"],
        help="review_batch: 自动选 ASD/TD 好/差/低质量代表",
    )
    args = parser.parse_args()

    cfg = load_config()
    log = setup_logging(cfg, name="specparam_qc_review")
    deriv = Path(cfg["paths"]["derivatives_root"])
    out_dir = Path(cfg["paths"]["outputs_root"]) / "figures" / "qc_specparam_review"
    sp_cfg = cfg.get("specparam", {})

    qc = pd.read_csv(deriv / "specparam" / "specparam_qc_summary_subject.csv")
    qc["subject_id"] = qc["subject_id"].astype(str)

    if args.subjects:
        subject_ids = list(args.subjects)
    elif args.preset == "review_batch":
        subject_ids = pick_review_subjects(qc, n_each=3)
    else:
        subject_ids = pick_review_subjects(qc, n_each=2)
        log.info("未指定 --subjects，使用默认 review 批次（约 %d 人）", len(subject_ids))

    rows = []
    for sid in subject_ids:
        psd_path = deriv / "psd" / f"{sid}_psd.csv"
        if not psd_path.exists():
            log.warning("跳过 %s: 无 PSD", sid)
            continue
        psd_df = pd.read_csv(psd_path)
        group = psd_df["group"].iloc[0]
        freqs, power = _mean_psd(psd_df)
        qc_row = qc.loc[qc["subject_id"] == sid]
        qc_s = qc_row.iloc[0] if len(qc_row) else None
        fit = plot_subject_fit(
            sid, group, freqs, power, sp_cfg,
            out_dir / f"{sid}_fit",
            qc_s,
        )
        rows.append({"subject_id": sid, "group": group, **fit})
        log.info("已保存 %s", out_dir / f"{sid}_fit.png")

    if rows:
        save_csv(pd.DataFrame(rows), out_dir / "qc_review_index.csv")
    log.info("QC 拟合图目录: %s", out_dir.resolve())


if __name__ == "__main__":
    main()
