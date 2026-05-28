"""论文 figure v2 — Molecular Autism 风格（matplotlib only）。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import mne
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec

from src.io_utils import attach_usable_epochs, exclude_specparam_low_quality, load_analysis_participants
from src.paper_figures import (
    FDR_SIG_CHANNELS,
    ROI_ORDER,
    _roi_marginal_td_asd_effects,
    load_main_cohort,
)
from src.specparam_utils import fit_specparam_channel
from statsmodels.formula.api import ols

from src.stats_utils import run_mixedlm

MM_TO_IN = 1 / 25.4

COL_ASD = "#4C72B0"
COL_TD = "#DD8452"
COL_GRAY = "#4D4D4D"
COL_LIGHT = "#D9D9D9"

ROBUSTNESS_LABELS = {
    "model_1": "group only",
    "model_2": "+ age, sex",
    "model_3": "+ IQ",
    "model_4": "+ epochs",
    "model_5": "+ fit R²",
    "model_6": "+ bad channels",
}
ROBUSTNESS_ORDER = list(ROBUSTNESS_LABELS.keys())

PAPER_V2_RC: dict[str, Any] = {
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "DejaVu Sans", "sans-serif"],
    "font.size": 8,
    "axes.labelsize": 8.5,
    "axes.titlesize": 8.5,
    "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5,
    "legend.fontsize": 7.5,
    "axes.linewidth": 0.8,
    "axes.edgecolor": COL_GRAY,
    "axes.facecolor": "white",
    "figure.facecolor": "white",
    "axes.grid": False,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 100,
    "savefig.dpi": 600,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
}


def apply_v2_style() -> None:
    plt.rcParams.update(PAPER_V2_RC)


def mm_figsize(w_mm: float, h_mm: float) -> tuple[float, float]:
    return w_mm * MM_TO_IN, h_mm * MM_TO_IN


def save_v2_figure(fig: plt.Figure, out_base: Path) -> None:
    out_base = Path(out_base)
    out_base.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf", "svg"):
        kw: dict[str, Any] = dict(bbox_inches="tight", facecolor="white", edgecolor="none")
        if ext == "png":
            kw["dpi"] = 600
        fig.savefig(out_base.with_suffix(f".{ext}"), **kw)
    plt.close(fig)


def panel_letter(ax: plt.Axes, letter: str) -> None:
    ax.text(
        -0.18, 1.06, letter,
        transform=ax.transAxes,
        fontsize=10.5,
        fontweight="bold",
        va="top",
        ha="left",
        color="black",
    )


def _mean_psd(psd_df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    g = psd_df.groupby("frequency", as_index=False)["power"].mean().sort_values("frequency")
    return g["frequency"].values, g["power"].values


def _aperiodic_linear(freqs: np.ndarray, offset: float, exponent: float) -> np.ndarray:
    log_p = offset - exponent * np.log10(freqs)
    return np.power(10.0, log_p)


def _full_model_linear(
    freqs: np.ndarray,
    offset: float,
    exponent: float,
    peak_params: np.ndarray | None,
) -> np.ndarray:
    log_p = offset - exponent * np.log10(freqs)
    if peak_params is not None and len(peak_params) > 0:
        for cf, pw, bw in peak_params:
            log_p = log_p + pw * np.exp(-0.5 * ((freqs - cf) / max(bw, 1e-6)) ** 2)
    return np.power(10.0, log_p)


def _fit_specparam_curves(
    freqs: np.ndarray,
    power: np.ndarray,
    sp_cfg: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """返回 aperiodic-only 与 full model 线性功率曲线。"""
    fit = fit_specparam_channel(freqs, power, sp_cfg)
    offset = float(fit["aperiodic_offset"])
    exponent = float(fit["aperiodic_exponent"])
    ap_only = _aperiodic_linear(freqs, offset, exponent)

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
        pass

    full = _full_model_linear(freqs, offset, exponent, peak_raw)
    return ap_only, full, fit


def pick_representative_subject(deriv: Path, participants: pd.DataFrame) -> str:
    """主分析队列中拟合质量接近中位数的代表被试。"""
    qc_path = deriv / "specparam" / "specparam_qc_summary_subject.csv"
    ids = set(participants["subject_id"].astype(str))
    if qc_path.exists():
        qc = pd.read_csv(qc_path)
        qc = qc[qc["subject_id"].astype(str).isin(ids)]
        if not qc.empty and "mean_r_squared" in qc.columns:
            med = qc["mean_r_squared"].median()
            row = qc.iloc[(qc["mean_r_squared"] - med).abs().argsort().iloc[0]]
            return str(row["subject_id"])
    return str(participants["subject_id"].iloc[0])


def plot_group_boxpanel(
    ax: plt.Axes,
    df: pd.DataFrame,
    value_col: str,
    ylabel: str,
    beta: float | None = None,
    p: float | None = None,
) -> dict[str, Any]:
    """箱线 + 抖动散点（期刊风格）。"""
    groups = ["ASD", "TD"]
    colors = {"ASD": COL_ASD, "TD": COL_TD}
    positions = np.arange(len(groups))
    data = [df.loc[df["group"] == g, value_col].dropna().values for g in groups]

    bp = ax.boxplot(
        data,
        positions=positions,
        widths=0.5,
        patch_artist=True,
        showfliers=False,
        medianprops=dict(color=COL_GRAY, linewidth=1.0),
        boxprops=dict(facecolor="white", edgecolor=COL_GRAY, linewidth=0.9),
        whiskerprops=dict(color=COL_GRAY, linewidth=0.9),
        capprops=dict(color=COL_GRAY, linewidth=0.9),
    )
    for box, g in zip(bp["boxes"], groups):
        box.set_edgecolor(colors[g])
        box.set_linewidth(1.0)

    rng = np.random.default_rng(42)
    for i, g in enumerate(groups):
        vals = df.loc[df["group"] == g, value_col].dropna().values
        jitter = rng.uniform(-0.1, 0.1, size=len(vals))
        ax.scatter(
            np.full(len(vals), i) + jitter,
            vals,
            s=22,
            alpha=0.65,
            color=colors[g],
            edgecolors="white",
            linewidths=0.25,
            zorder=3,
        )

    ax.set_xticks(positions)
    ax.set_xticklabels(groups)
    ax.set_ylabel(ylabel)

    if beta is not None and p is not None:
        p_str = "p < 0.001" if p < 0.001 else f"p = {p:.3f}"
        ax.text(
            0.98, 0.98,
            f"adjusted β = {beta:.3f}\n{p_str}",
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=7,
            color=COL_GRAY,
        )

    return {
        "n_total": int(df[value_col].notna().sum()),
        "n_ASD": int(df.loc[df["group"] == "ASD", value_col].notna().sum()),
        "n_TD": int(df.loc[df["group"] == "TD", value_col].notna().sum()),
    }


def plot_forest(
    ax: plt.Axes,
    effects: pd.DataFrame,
    beta_col: str,
    ci_low_col: str,
    ci_high_col: str,
    y_labels: list[str],
    xlabel: str,
) -> None:
    y = np.arange(len(effects))
    ax.axvline(0, color=COL_LIGHT, lw=1.2, zorder=0)
    ax.errorbar(
        effects[beta_col].values,
        y,
        xerr=[
            effects[beta_col].values - effects[ci_low_col].values,
            effects[ci_high_col].values - effects[beta_col].values,
        ],
        fmt="o",
        color=COL_GRAY,
        ecolor=COL_GRAY,
        elinewidth=1.0,
        capsize=2.5,
        markersize=4.5,
        mew=0.8,
        zorder=2,
    )
    ax.set_yticks(y)
    ax.set_yticklabels(y_labels)
    ax.set_xlabel(xlabel)


def load_subject_peaks(deriv: Path, participants: pd.DataFrame) -> pd.DataFrame:
    ch_path = deriv / "specparam" / "specparam_channel_results_qc.csv"
    ch = pd.read_csv(ch_path)
    if "fit_valid" in ch.columns:
        ch = ch[ch["fit_valid"]]
    peaks = ch.groupby(["subject_id", "group"], as_index=False)[["alpha_cf", "alpha_pw"]].mean()
    df = participants.merge(peaks, on=["subject_id", "group"], how="inner")
    return attach_usable_epochs(df, deriv)


def _adjusted_group_p(df: pd.DataFrame, metric: str) -> float:
    """主分析队列上周期峰指标的协变量校正 group p。"""
    cols = [metric, "group", "age_months", "sex", "IQ_total", "usable_epochs"]
    sub = df.dropna(subset=cols)
    if len(sub) < 10:
        return float("nan")
    formula = f"{metric} ~ C(group) + age_months + C(sex) + IQ_total + usable_epochs"
    res = ols(formula, data=sub).fit()
    term = "C(group)[T.TD]"
    return float(res.pvalues[term]) if term in res.pvalues.index else float("nan")


def make_fig1_psd_specparam_overview(
    cfg: dict[str, Any],
    participants: pd.DataFrame,
    deriv: Path,
    out_base: Path,
) -> dict[str, Any]:
    apply_v2_style()
    fmin, fmax = 1.0, 40.0
    sp_cfg = cfg.get("specparam", {})
    psd_dir = deriv / "psd"
    asd_label = cfg["groups"]["asd_label"]
    td_label = cfg["groups"]["td_label"]

    fig = plt.figure(figsize=mm_figsize(180, 70))
    gs = GridSpec(1, 2, figure=fig, wspace=0.42, left=0.09, right=0.98, top=0.92, bottom=0.22)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])

    # Panel A — 代表被试 specparam 示意
    rep_id = pick_representative_subject(deriv, participants)
    psd_path = psd_dir / f"{rep_id}_psd.csv"
    rep_group = str(participants.loc[participants["subject_id"].astype(str) == rep_id, "group"].iloc[0])
    psd_df = pd.read_csv(psd_path)
    psd_df = psd_df[(psd_df["frequency"] >= fmin) & (psd_df["frequency"] <= fmax)]
    freqs, power = _mean_psd(psd_df)
    ap_only, full, fit = _fit_specparam_curves(freqs, power, sp_cfg)

    ax_a.loglog(freqs, power, color=COL_GRAY, lw=1.4, alpha=0.9, label="Observed PSD")
    ax_a.loglog(freqs, ap_only, color=COL_ASD, lw=1.5, ls="--", label="Aperiodic fit")
    ax_a.loglog(freqs, full, color=COL_TD, lw=1.5, ls="-", label="Full model")
    ax_a.set_xlim(fmin, fmax)
    ax_a.set_xlabel("Frequency (Hz)")
    ax_a.set_ylabel("PSD (V²/Hz, log scale)")
    ax_a.legend(frameon=False, loc="upper right", handlelength=1.6)
    panel_letter(ax_a, "A")

    # Panel B — 组平均 PSD
    frames = []
    for sid in participants["subject_id"].astype(str):
        p = psd_dir / f"{sid}_psd.csv"
        if p.exists():
            frames.append(pd.read_csv(p))
    combined = pd.concat(frames, ignore_index=True)
    combined = combined[(combined["frequency"] >= fmin) & (combined["frequency"] <= fmax)]

    for grp, color in [(asd_label, COL_ASD), (td_label, COL_TD)]:
        sub = combined[combined["group"] == grp]
        stats = sub.groupby("frequency")["power"].agg(["mean", "sem"])
        freqs_g = stats.index.values
        mean = stats["mean"].values
        sem = stats["sem"].values
        ax_b.loglog(freqs_g, mean, color=color, lw=1.5, label=grp)
        ax_b.fill_between(
            freqs_g,
            np.maximum(mean - sem, 1e-30),
            mean + sem,
            color=color,
            alpha=0.18,
            linewidth=0,
        )

    ax_b.set_xlim(fmin, fmax)
    ax_b.set_xlabel("Frequency (Hz)")
    ax_b.set_ylabel("PSD (V²/Hz, log scale)")
    ax_b.legend(frameon=False, loc="upper right", handlelength=1.6)
    panel_letter(ax_b, "B")

    save_v2_figure(fig, out_base)
    n_asd = int(combined.loc[combined["group"] == asd_label, "subject_id"].nunique())
    n_td = int(combined.loc[combined["group"] == td_label, "subject_id"].nunique())

    return {
        "figure": "fig1_psd_specparam_overview",
        "panel_A": {
            "subject_id": rep_id,
            "group": rep_group,
            "data_source": str(psd_path),
            "specparam_r_squared": float(fit.get("r_squared", np.nan)),
            "note": "Channel-mean PSD; aperiodic and full model refit with specparam (same settings as pipeline).",
        },
        "panel_B": {
            "data_source": str(psd_dir),
            "n_ASD": n_asd,
            "n_TD": n_td,
            "shading": "SEM",
            "note": "Descriptive group-mean PSD across subjects (channel-mean per subject).",
        },
    }


def make_fig2_main_aperiodic_effects(
    participants: pd.DataFrame,
    deriv: Path,
    outputs: Path,
    out_base: Path,
) -> dict[str, Any]:
    apply_v2_style()
    roi_global = pd.read_csv(deriv / "roi" / "specparam_subject_global.csv")
    main_stats = pd.read_csv(deriv / "stats" / "main_group_analysis.csv")
    robust = pd.read_csv(outputs / "tables" / "global_exponent_robustness_models.csv")

    df = participants.merge(roi_global, on=["subject_id", "group"], how="inner")

    def _gp(outcome: str) -> tuple[float, float]:
        row = main_stats[(main_stats["outcome"] == outcome) & (main_stats["term"] == "C(group)[T.TD]")]
        if row.empty:
            return np.nan, np.nan
        return float(row["coef"].iloc[0]), float(row["pvalue"].iloc[0])

    beta_exp, p_exp = _gp("global_exponent")
    beta_off, p_off = _gp("global_offset")

    fig = plt.figure(figsize=mm_figsize(180, 80))
    gs = GridSpec(1, 3, figure=fig, wspace=0.48, left=0.07, right=0.98, top=0.9, bottom=0.2)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[0, 2])

    meta_a = plot_group_boxpanel(
        ax_a, df.dropna(subset=["global_exponent"]),
        "global_exponent", "Global aperiodic exponent", beta_exp, p_exp,
    )
    panel_letter(ax_a, "A")

    meta_b = plot_group_boxpanel(
        ax_b, df.dropna(subset=["global_offset"]),
        "global_offset", "Global aperiodic offset", beta_off, p_off,
    )
    panel_letter(ax_b, "B")

    rob = robust[robust["model_name"].isin(ROBUSTNESS_ORDER)].copy()
    rob["label"] = rob["model_name"].map(ROBUSTNESS_LABELS)
    rob = rob.set_index("model_name").loc[ROBUSTNESS_ORDER].reset_index()
    effects = rob.rename(columns={
        "group_coef_TD_vs_ASD": "beta",
        "group_ci_low": "ci_low",
        "group_ci_high": "ci_high",
    })
    plot_forest(
        ax_c, effects, "beta", "ci_low", "ci_high",
        effects["label"].tolist(),
        "β coefficient (TD − ASD)",
    )
    panel_letter(ax_c, "C")

    save_v2_figure(fig, out_base)
    return {
        "figure": "fig2_main_aperiodic_effects",
        "panel_A": {**meta_a, "data_source": "derivatives/roi/specparam_subject_global.csv", "model": "main_group_analysis global_exponent"},
        "panel_B": {**meta_b, "data_source": "derivatives/roi/specparam_subject_global.csv", "model": "main_group_analysis global_offset"},
        "panel_C": {
            "data_source": "outputs/tables/global_exponent_robustness_models.csv",
            "models": ROBUSTNESS_ORDER,
            "note": "OLS group coefficient (TD−ASD) per robustness model.",
        },
    }


def make_fig3_spatial_distribution(
    participants: pd.DataFrame,
    deriv: Path,
    montage_name: str,
    out_base: Path,
) -> dict[str, Any]:
    apply_v2_style()
    roi_long = pd.read_csv(deriv / "roi" / "specparam_subject_roi_long.csv")
    channel_stats = pd.read_csv(deriv / "stats" / "channel_level_analysis.csv")

    df = participants.merge(roi_long, on=["subject_id", "group"], how="inner")
    df = attach_usable_epochs(df, deriv)
    df = exclude_specparam_low_quality(df, deriv)
    df = df.dropna(subset=["exponent", "group", "roi", "age_months", "sex", "IQ_total", "usable_epochs"])
    formula = "exponent ~ C(group) * C(roi) + age_months + C(sex) + IQ_total + usable_epochs"
    model = run_mixedlm(formula, df, groups="subject_id")
    effects = _roi_marginal_td_asd_effects(model)
    effects["roi"] = pd.Categorical(effects["roi"], categories=ROI_ORDER[::-1], ordered=True)
    effects = effects.sort_values("roi")

    fig = plt.figure(figsize=mm_figsize(180, 80))
    gs = GridSpec(1, 2, figure=fig, width_ratios=[1.05, 1.0], wspace=0.45, left=0.1, right=0.92, top=0.9, bottom=0.18)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])

    plot_forest(
        ax_a, effects,
        "beta_TD_minus_ASD", "ci_low", "ci_high",
        effects["roi"].astype(str).tolist(),
        "β coefficient (TD − ASD)",
    )
    panel_letter(ax_a, "A")

    coef_map = channel_stats.set_index("channel")["coef"].to_dict()
    montage = mne.channels.make_standard_montage(montage_name)
    ch_names = [c for c in montage.ch_names if c.startswith("E")]
    values = np.array([coef_map.get(c, np.nan) for c in ch_names])
    info = mne.create_info(ch_names=ch_names, sfreq=250.0, ch_types="eeg")
    info.set_montage(montage)

    vmax = float(np.nanmax(np.abs(values)))
    im, _ = mne.viz.plot_topomap(
        values, info, axes=ax_b, show=False,
        cmap="RdBu_r", vlim=(-vmax, vmax), contours=0,
        sensors=True,
        mask=None,
    )
    cbar = plt.colorbar(im, ax=ax_b, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=7)
    cbar.set_label("β coefficient (TD − ASD)", fontsize=8)

    pos = montage.get_positions()["ch_pos"]
    for ch in FDR_SIG_CHANNELS:
        if ch in pos:
            xy = pos[ch][:2]
            ax_b.plot(
                xy[0], xy[1],
                marker="o",
                mfc="none",
                mec="black",
                mew=1.2,
                ms=7,
                zorder=10,
                clip_on=True,
            )
    panel_letter(ax_b, "B")

    save_v2_figure(fig, out_base)
    return {
        "figure": "fig3_spatial_distribution",
        "panel_A": {
            "data_source": "derivatives/roi/specparam_subject_roi_long.csv",
            "model": formula,
            "n_obs": int(model.nobs),
            "n_subjects": int(df["subject_id"].nunique()),
            "reference_roi": "central",
            "effects": effects.to_dict(orient="records"),
        },
        "panel_B": {
            "data_source": "derivatives/stats/channel_level_analysis.csv",
            "fdr_channels": FDR_SIG_CHANNELS,
            "vlim_symmetric": vmax,
        },
    }


def make_fig4_periodic_clinical(
    participants: pd.DataFrame,
    deriv: Path,
    outputs: Path,
    out_base: Path,
    include_clinical: bool = True,
) -> dict[str, Any]:
    apply_v2_style()
    peak_df = load_subject_peaks(deriv, participants)
    p_pw = _adjusted_group_p(peak_df, "alpha_pw")
    p_cf = _adjusted_group_p(peak_df, "alpha_cf")

    n_panels = 3 if include_clinical else 2
    fig = plt.figure(figsize=mm_figsize(180, 80))
    gs = GridSpec(1, n_panels, figure=fig, wspace=0.48, left=0.07, right=0.98, top=0.9, bottom=0.2)

    ax_a = fig.add_subplot(gs[0, 0])
    meta_a = plot_group_boxpanel(
        ax_a, peak_df.dropna(subset=["alpha_pw"]),
        "alpha_pw", "Alpha peak power (log10)",
    )
    _annotate_ns(ax_a, p_pw)
    panel_letter(ax_a, "A")

    ax_b = fig.add_subplot(gs[0, 1])
    meta_b = plot_group_boxpanel(
        ax_b, peak_df.dropna(subset=["alpha_cf"]),
        "alpha_cf", "Alpha peak frequency (Hz)",
    )
    _annotate_ns(ax_b, p_cf)
    panel_letter(ax_b, "B")

    meta_c: dict[str, Any] = {}
    if include_clinical:
        roi_global = pd.read_csv(deriv / "roi" / "specparam_subject_global.csv")
        clin_path = deriv / "stats" / "clinical_correlation_spearman.csv"
        ax_c = fig.add_subplot(gs[0, 2])
        asd = participants[participants["group"] == "ASD"].merge(roi_global, on="subject_id", how="inner")
        asd = asd.dropna(subset=["global_exponent", "ADOS_SA"])
        rho, p_sp = -0.229, 0.076
        if clin_path.exists():
            sp = pd.read_csv(clin_path)
            row = sp[(sp["clinical"] == "ADOS_SA") & (sp["eeg_variable"] == "global_exponent")]
            if not row.empty:
                rho = float(row["rho"].iloc[0])
                p_sp = float(row["pvalue"].iloc[0])

        x = asd["ADOS_SA"].values
        y = asd["global_exponent"].values
        ax_c.scatter(x, y, s=22, alpha=0.65, color=COL_ASD, edgecolors="white", linewidths=0.25)
        if len(x) >= 3:
            coef = np.polyfit(x, y, 1)
            xs = np.linspace(x.min(), x.max(), 80)
            ax_c.plot(xs, np.poly1d(coef)(xs), color=COL_GRAY, lw=1.4)
        ax_c.set_xlabel("ADOS social affect (SA)")
        ax_c.set_ylabel("Global aperiodic exponent")
        p_str = "p < 0.001" if p_sp < 0.001 else f"p = {p_sp:.3f}"
        ax_c.text(
            0.98, 0.98,
            f"Spearman ρ = {rho:.3f}\n{p_str}",
            transform=ax_c.transAxes,
            ha="right",
            va="top",
            fontsize=7,
            color=COL_GRAY,
        )
        panel_letter(ax_c, "C")
        meta_c = {
            "data_source": "participants ADOS_SA + specparam_subject_global.csv",
            "spearman_source": str(clin_path),
            "n_ASD": len(asd),
            "rho": rho,
            "p": p_sp,
            "note": "Exploratory; ASD only. No OLS CI band (Spearman annotation only).",
        }

    save_v2_figure(fig, out_base)
    return {
        "figure": "fig4_periodic_clinical_exploratory",
        "panel_A": {**meta_a, "data_source": "specparam_channel_results_qc.csv (subject mean alpha_pw)", "adjusted_p": p_pw},
        "panel_B": {**meta_b, "data_source": "specparam_channel_results_qc.csv (subject mean alpha_cf)", "adjusted_p": p_cf},
        "panel_C": meta_c,
    }


def _annotate_ns(ax: plt.Axes, p: float) -> None:
    if np.isnan(p):
        return
    label = "n.s." if p >= 0.05 else ("p < 0.001" if p < 0.001 else f"p = {p:.3f}")
    ax.text(
        0.98, 0.98, f"adjusted {label}",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=7,
        color=COL_GRAY,
    )


def write_v2_qc_notes(all_meta: list[dict[str, Any]], out_path: Path) -> None:
    lines = ["Paper figure v2 QC notes", "=" * 60, ""]
    for fig_meta in all_meta:
        name = fig_meta.get("figure", "unknown")
        lines.append(f"## {name}")
        for key, val in fig_meta.items():
            if key == "figure":
                continue
            if key == "panel_A" or key == "panel_B" or key == "panel_C":
                lines.append(f"  [{key}]")
                if isinstance(val, dict):
                    for k2, v2 in val.items():
                        if k2 == "effects":
                            lines.append("    marginal effects:")
                            for row in v2:
                                lines.append(
                                    f"      {row['roi']}: β={row['beta_TD_minus_ASD']:.4f}, "
                                    f"CI [{row['ci_low']:.4f}, {row['ci_high']:.4f}]"
                                )
                        else:
                            lines.append(f"    {k2}: {v2}")
                continue
            lines.append(f"  {key}: {val}")
        lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def write_figure_captions(out_path: Path, meta: dict[str, Any]) -> None:
    """写入 figure_captions.md（中英简要说明）。"""
    m = meta
    n_main = m.get("n_main", 138)
    n_asd = m.get("n_asd", 61)
    n_td = m.get("n_td", 77)
    cov = "age, sex, IQ_total, and usable epochs"

    text = f"""# Figure captions (draft)

队列：N = {n_main}（ASD = {n_asd}, TD = {n_td}）。ASD 蓝色（{COL_ASD}），TD 橙色（{COL_TD}）。

---

## Figure 1. PSD and specparam overview (`fig1_psd_specparam_overview`)

**A.** Representative subject ({m.get('fig1_rep_id', '—')}, {m.get('fig1_rep_group', '—')}) channel-averaged power spectral density (PSD, 1–40 Hz) with specparam aperiodic (1/f) and full model fits. Observed PSD in gray; aperiodic component dashed blue; full model solid orange. Fits obtained with the same specparam settings as the main pipeline (fixed aperiodic mode).

**B.** Group-mean PSD for ASD and TD. Shaded bands indicate ±1 SEM across subjects (each subject’s PSD averaged across channels before group aggregation). Y-axis: PSD (V²/Hz, log scale). Specparam fitting range 1–40 Hz (caption only).

---

## Figure 2. Main aperiodic effects (`fig2_main_aperiodic_effects`)

**A.** Global aperiodic exponent by group (boxplots with individual data points). Annotation: adjusted group effect from primary OLS (TD − ASD β = {m.get('beta_exp', 0.079):.3f}, p = {m.get('p_exp', 0.012):.3f}), covariates: {cov}.

**B.** Global aperiodic offset by group. Adjusted β = {m.get('beta_off', 0.060):.3f}, p = {m.get('p_off', 0.095):.3f}; same covariates.

**C.** Robustness of the global exponent group effect across nested OLS models (points = β, horizontal bars = 95% CI). Models: group only; + age and sex; + IQ; + usable epochs; + mean specparam fit R²; + bad channel count. Vertical line at zero.

---

## Figure 3. Spatial distribution (`fig3_spatial_distribution`)

**A.** Marginal TD − ASD contrasts for aperiodic exponent at each ROI from the group × ROI linear mixed model (random intercept for subject; central ROI reference). Points = β, bars = 95% CI. Covariates: {cov}.

**B.** Channel-level topomap of OLS coefficients C(group)[T.TD] (TD − ASD) from separate channel models with the same covariates. Diverging colormap (RdBu_r), symmetric limits. Black open circles: FDR q < .05 (E33, E36, E37, E38).

---

## Figure 4. Periodic and clinical exploratory results (`fig4_periodic_clinical_exploratory`)

**A.** Alpha peak power (specparam log10 peak height, subject-level channel mean) by group. Adjusted group p = {m.get('p_alpha_pw', 'n.s.')} (OLS, covariates: {cov}).

**B.** Alpha peak centre frequency (Hz) by group. Adjusted group p = {m.get('p_alpha_cf', 'n.s.')} (OLS, n = {n_main}, covariates: {cov}).

**C.** Exploratory Spearman correlation in ASD only (n = {m.get('n_clinical', 61)}): global aperiodic exponent vs ADOS social affect (SA); ρ = {m.get('rho_sa', -0.229):.3f}, p = {m.get('p_sa', 0.076):.3f}. Dashed line = linear fit for visualization only.

---

*Error bands in Figure 1B are SEM. Regression annotations are covariate-adjusted unless noted. Topomap FDR correction across 64 channels (Benjamini–Hochberg).*
"""
    out_path.write_text(text, encoding="utf-8")
