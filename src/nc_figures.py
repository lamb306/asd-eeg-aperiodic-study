"""Nature Communications narrative figures for manuscript_NC_revised_zh."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import mne
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from statsmodels.formula.api import ols

from src.paper_figures import FDR_SIG_CHANNELS, load_main_cohort
from src.paper_figures_v2 import (
    COL_ASD,
    COL_GRAY,
    COL_LIGHT,
    COL_TD,
    ROBUSTNESS_ORDER,
    _aperiodic_linear,
    apply_v2_style,
    mm_figsize,
    panel_letter,
    plot_forest,
    plot_group_boxpanel,
    save_v2_figure,
)

NC_OUT = Path("outputs/figures/nc_manuscript")


def _save(fig: plt.Figure, name: str) -> Path:
    out = NC_OUT / name
    save_v2_figure(fig, out)
    return out.with_suffix(".png")


def _forest_from_rows(
    ax: plt.Axes,
    rows: list[dict[str, Any]],
    *,
    xlabel: str = "β (TD − ASD)",
    highlight: set[str] | None = None,
) -> None:
    df = pd.DataFrame(rows)
    labels = df["label"].tolist()
    y = np.arange(len(df))
    ax.axvline(0, color=COL_LIGHT, lw=1.2, zorder=0)
    for i, row in df.iterrows():
        color = COL_TD if highlight and row["label"] in highlight else COL_GRAY
        ax.errorbar(
            row["beta"],
            y[i],
            xerr=[[row["beta"] - row["ci_low"]], [row["ci_high"] - row["beta"]]],
            fmt="o",
            color=color,
            ecolor=color,
            elinewidth=1.0,
            capsize=2.5,
            markersize=4.5,
            mew=0.8,
            zorder=2,
        )
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel(xlabel)


def _draw_flow_panel(ax: plt.Axes) -> None:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    boxes = [
        (0.5, 0.86, "168 children with preprocessed\nresting-state EEG\nASD = 80, TD = 88"),
        (0.5, 0.58, "145 passed minimum usable epoch criterion\nASD = 65, TD = 80"),
        (0.5, 0.30, "138 passed subject-level specparam QC\nASD = 61, TD = 77"),
        (0.5, 0.06, "Final primary analysis cohort\nN = 138"),
    ]
    excl = [
        (0.84, 0.72, "Excluded = 23\nusable_epochs < 60"),
        (0.84, 0.44, "Excluded = 7\nlow-quality specparam fit /\ninvalid channel ratio"),
    ]
    for cx, cy, text in boxes:
        patch = FancyBboxPatch(
            (cx - 0.28, cy - 0.07), 0.56, 0.14,
            boxstyle="round,pad=0.01,rounding_size=0.02",
            linewidth=0.9, edgecolor=COL_GRAY, facecolor="white",
            transform=ax.transAxes, clip_on=False,
        )
        ax.add_patch(patch)
        ax.text(cx, cy, text, ha="center", va="center", fontsize=6.2, transform=ax.transAxes)
    for cx, cy, text in excl:
        patch = FancyBboxPatch(
            (cx - 0.16, cy - 0.06), 0.32, 0.12,
            boxstyle="round,pad=0.01,rounding_size=0.02",
            linewidth=0.8, edgecolor=COL_GRAY, facecolor="#F2F2F2",
            transform=ax.transAxes, clip_on=False,
        )
        ax.add_patch(patch)
        ax.text(cx, cy, text, ha="center", va="center", fontsize=5.8, transform=ax.transAxes)
    for y0, y1 in [(0.79, 0.65), (0.51, 0.37), (0.23, 0.13)]:
        ax.annotate("", xy=(0.5, y1), xytext=(0.5, y0),
                    xycoords="axes fraction", textcoords="axes fraction",
                    arrowprops=dict(arrowstyle="-|>", color=COL_GRAY, lw=0.8))
    for y in [0.72, 0.44]:
        ax.annotate("", xy=(0.84, y), xytext=(0.78, y),
                    xycoords="axes fraction", textcoords="axes fraction",
                    arrowprops=dict(arrowstyle="-|>", color=COL_GRAY, lw=0.7))


def _specparam_schematic(ax: plt.Axes) -> None:
    freqs = np.linspace(1, 40, 400)
    offset, exponent = -10.0, 1.75
    ap = _aperiodic_linear(freqs, offset, exponent)
    peak = 0.35 * np.exp(-0.5 * ((freqs - 10.0) / 1.5) ** 2)
    full = ap * (1 + peak)
    ax.semilogy(freqs, full, color=COL_GRAY, lw=1.5, label="Observed spectrum")
    ax.semilogy(freqs, ap, color=COL_GRAY, ls="--", lw=1.3, label="Aperiodic fit")
    ax.fill_between(freqs, ap, full, color=COL_TD, alpha=0.35, label="Periodic peaks")
    ax.annotate("Aperiodic exponent", xy=(18, ap[180]), xytext=(24, ap[180] * 3),
                arrowprops=dict(arrowstyle="->", color=COL_GRAY, lw=0.8),
                fontsize=6.5, color=COL_GRAY)
    ax.annotate("Offset", xy=(3, ap[30]), xytext=(6, ap[30] * 0.25),
                arrowprops=dict(arrowstyle="->", color=COL_GRAY, lw=0.8),
                fontsize=6.5, color=COL_GRAY)
    ax.annotate("Periodic peaks", xy=(10, full[90]), xytext=(14, full[90] * 2.5),
                arrowprops=dict(arrowstyle="->", color=COL_TD, lw=0.8),
                fontsize=6.5, color=COL_TD)
    ax.set_xlim(1, 40)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Power")
    ax.legend(frameon=False, fontsize=6, loc="upper right")


def _group_psd_panel(ax: plt.Axes, participants: pd.DataFrame, psd_dir: Path, cfg: dict) -> None:
    fmin, fmax = 1.0, 40.0
    frames = []
    for sid in participants["subject_id"].astype(str):
        p = psd_dir / f"{sid}_psd.csv"
        if p.exists():
            frames.append(pd.read_csv(p))
    combined = pd.concat(frames, ignore_index=True)
    combined = combined[(combined["frequency"] >= fmin) & (combined["frequency"] <= fmax)]
    for grp, color in [(cfg["groups"]["asd_label"], COL_ASD), (cfg["groups"]["td_label"], COL_TD)]:
        sub = combined[combined["group"] == grp]
        stats = sub.groupby("frequency")["power"].agg(["mean", "sem"])
        freqs_g = stats.index.values
        mean = stats["mean"].values
        sem = stats["sem"].values
        ax.semilogy(freqs_g, mean, color=color, lw=1.5, label=grp)
        ax.fill_between(freqs_g, np.maximum(mean - sem, 1e-30), mean + sem,
                        color=color, alpha=0.18, linewidth=0)
    ax.axvspan(8, 13, color="#E8E8E8", alpha=0.45, zorder=0)
    ax.set_xlim(fmin, fmax)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Power")
    ax.legend(frameon=False, fontsize=6.5, loc="upper right")


def _interaction_lines(
    ax: plt.Axes,
    df: pd.DataFrame,
    outcome: str,
    interaction_beta: float,
    interaction_p: float,
) -> None:
    sub = df.dropna(subset=[outcome, "group", "age_months", "sex", "IQ_total", "usable_epochs"]).copy()
    med = {
        "sex": sub["sex"].mode().iloc[0],
        "IQ_total": sub["IQ_total"].median(),
        "usable_epochs": sub["usable_epochs"].median(),
    }
    ages = np.linspace(sub["age_months"].min(), sub["age_months"].max(), 80)
    formula = (
        f"{outcome} ~ C(group) * age_months + C(sex) + IQ_total + usable_epochs"
    )
    model = ols(formula, data=sub).fit()
    for grp, color in [("ASD", COL_ASD), ("TD", COL_TD)]:
        pred_df = pd.DataFrame({
            "group": grp,
            "age_months": ages,
            "sex": med["sex"],
            "IQ_total": med["IQ_total"],
            "usable_epochs": med["usable_epochs"],
        })
        pred = model.predict(pred_df)
        ax.plot(ages, pred, color=color, lw=1.6, label=grp)
        pts = sub[sub["group"] == grp]
        ax.scatter(pts["age_months"], pts[outcome], s=14, alpha=0.45,
                   color=color, edgecolors="white", linewidths=0.2, zorder=3)
    ax.set_xlabel("Age (months)")
    ax.set_ylabel(outcome.replace("_", " "))
    ax.legend(frameon=False, fontsize=6.5, loc="best")
    p_str = f"p = {interaction_p:.3f}"
    ax.text(0.02, 0.98, f"group × age: β = {interaction_beta:.4f}\n{p_str}",
            transform=ax.transAxes, ha="left", va="top", fontsize=6.5, color=COL_GRAY)


def make_figure1(cfg: dict, participants: pd.DataFrame, deriv: Path) -> Path:
    apply_v2_style()
    roi = pd.read_csv(deriv / "roi" / "specparam_subject_global.csv")
    periodic = pd.read_csv(deriv / "stats" / "periodic_peak_analysis.csv")
    df = participants.merge(roi, on=["subject_id", "group"], how="inner")

    fig = plt.figure(figsize=mm_figsize(183, 145))
    gs = GridSpec(2, 3, figure=fig, hspace=0.55, wspace=0.45,
                  left=0.08, right=0.98, top=0.95, bottom=0.08)

    ax_a = fig.add_subplot(gs[0, 0])
    _draw_flow_panel(ax_a)
    panel_letter(ax_a, "A")

    ax_b = fig.add_subplot(gs[0, 1])
    _group_psd_panel(ax_b, participants, deriv / "psd", cfg)
    panel_letter(ax_b, "B")

    ax_c = fig.add_subplot(gs[0, 2])
    _specparam_schematic(ax_c)
    panel_letter(ax_c, "C")

    ax_d = fig.add_subplot(gs[1, 0])
    plot_group_boxpanel(ax_d, df.dropna(subset=["global_exponent"]),
                        "global_exponent", "Global aperiodic exponent", 0.079, 0.012)
    ax_d.text(0.98, 0.06, "TD > ASD", transform=ax_d.transAxes, ha="right", va="bottom",
              fontsize=6.5, color=COL_GRAY)
    panel_letter(ax_d, "D")

    ax_e = fig.add_subplot(gs[1, 1])
    plot_group_boxpanel(ax_e, df.dropna(subset=["global_offset"]),
                        "global_offset", "Global offset", 0.060, 0.095)
    ax_e.text(0.98, 0.06, "nonsignificant trend", transform=ax_e.transAxes,
              ha="right", va="bottom", fontsize=6.2, color=COL_GRAY)
    panel_letter(ax_e, "E")

    ax_f = fig.add_subplot(gs[1, 2])
    rows = []
    for metric, label in [
        ("alpha_cf", "alpha_cf"), ("alpha_pw", "alpha_pw"), ("alpha_bw", "alpha_bw"),
        ("theta_pw", "theta_pw"), ("beta_pw", "beta_pw"),
    ]:
        r = periodic[(periodic["outcome"] == metric) & (periodic["term"] == "C(group)[T.TD]")].iloc[0]
        rows.append({
            "label": label,
            "beta": float(r["coef"]),
            "ci_low": float(r["ci_low"]),
            "ci_high": float(r["ci_high"]),
        })
    _forest_from_rows(ax_f, rows)
    ax_f.set_title("Periodic peak parameters", fontsize=7.5)
    panel_letter(ax_f, "F")

    return _save(fig, "Figure1_spectral_parameterization")


def make_figure2(cfg: dict, participants: pd.DataFrame, deriv: Path) -> Path:
    apply_v2_style()
    montage_name = cfg.get("eeg", {}).get("montage", "GSN-HydroCel-64_1.0")
    channel_stats = pd.read_csv(deriv / "stats" / "channel_level_analysis.csv")
    features = pd.read_csv(Path("outputs/tables/resting_features_locked.csv"))

    fig = plt.figure(figsize=mm_figsize(183, 110))
    gs = GridSpec(1, 4, figure=fig, wspace=0.55, left=0.07, right=0.98, top=0.88, bottom=0.18)

    ax_a = fig.add_subplot(gs[0, 0])
    coef_map = channel_stats.set_index("channel")["coef"].to_dict()
    montage = mne.channels.make_standard_montage(montage_name)
    ch_names = [c for c in montage.ch_names if c.startswith("E")]
    values = np.array([coef_map.get(c, np.nan) for c in ch_names])
    info = mne.create_info(ch_names=ch_names, sfreq=250.0, ch_types="eeg")
    info.set_montage(montage)
    vmax = float(np.nanmax(np.abs(values)))
    im, _ = mne.viz.plot_topomap(values, info, axes=ax_a, show=False,
                                 cmap="RdBu_r", vlim=(-vmax, vmax), contours=0, sensors=True)
    cbar = plt.colorbar(im, ax=ax_a, fraction=0.05, pad=0.04)
    cbar.ax.tick_params(labelsize=6)
    cbar.set_label("β (TD − ASD)", fontsize=7)
    pos = montage.get_positions()["ch_pos"]
    for ch in FDR_SIG_CHANNELS:
        if ch in pos:
            xy = pos[ch][:2]
            ax_a.plot(xy[0], xy[1], marker="o", mfc="none", mec="black", mew=1.0, ms=6, zorder=10)
    panel_letter(ax_a, "A")

    ax_b = fig.add_subplot(gs[0, 1])
    ax_b.set_xlim(-0.12, 0.12)
    ax_b.set_ylim(-0.12, 0.12)
    ax_b.set_aspect("equal")
    ax_b.axis("off")
    for ch, xy in pos.items():
        if not ch.startswith("E"):
            continue
        color = COL_TD if ch in FDR_SIG_CHANNELS else "#CCCCCC"
        size = 55 if ch in FDR_SIG_CHANNELS else 18
        ax_b.scatter(xy[0], xy[1], s=size, c=color, edgecolors="white", linewidths=0.3, zorder=2)
    ax_b.text(0, -0.105, "Posterior ROI\n(E33, E36, E37, E38)", ha="center", fontsize=7)
    panel_letter(ax_b, "B")

    ax_c = fig.add_subplot(gs[0, 2])
    plot_group_boxpanel(ax_c, features.dropna(subset=["posterior_exponent"]),
                        "posterior_exponent", "Posterior exponent", 0.133, 0.000133)
    panel_letter(ax_c, "C")

    ax_d = fig.add_subplot(gs[0, 3])
    rows = [
        {"label": "Global exponent\n(primary)", "beta": 0.079, "ci_low": 0.018, "ci_high": 0.140},
        {"label": "Posterior exponent\nICLabel 0.70 all", "beta": 0.121, "ci_low": 0.054, "ci_high": 0.189},
        {"label": "Posterior exponent\nICLabel 0.80 all", "beta": 0.128, "ci_low": 0.054, "ci_high": 0.201},
    ]
    _forest_from_rows(ax_d, rows)
    panel_letter(ax_d, "D")

    return _save(fig, "Figure2_posterior_topography")


def make_figure3(cfg: dict, participants: pd.DataFrame, deriv: Path) -> Path:
    apply_v2_style()
    roi = pd.read_csv(deriv / "roi" / "specparam_subject_global.csv")
    df = participants.merge(roi, on=["subject_id", "group"], how="inner")
    age_pred = pd.read_csv("outputs/tables/nonlinear_age_sensitivity/group_difference_by_age.csv")

    fig = plt.figure(figsize=mm_figsize(183, 125))
    gs = GridSpec(2, 3, figure=fig, hspace=0.5, wspace=0.45,
                  left=0.08, right=0.98, top=0.94, bottom=0.08)

    ax_a = fig.add_subplot(gs[0, 0])
    _interaction_lines(ax_a, df, "global_exponent", 0.0033, 0.020)
    panel_letter(ax_a, "A")

    ax_b = fig.add_subplot(gs[0, 1])
    _interaction_lines(ax_b, df, "global_offset", 0.0037, 0.021)
    panel_letter(ax_b, "B")

    ax_c = fig.add_subplot(gs[0, 2])
    _forest_from_rows(ax_c, [
        {"label": "≤72 months (n=23)", "beta": 0.055, "ci_low": -0.100, "ci_high": 0.211},
        {"label": ">72 months (n=115)", "beta": 0.076, "ci_low": 0.007, "ci_high": 0.145},
    ])
    panel_letter(ax_c, "C")

    ax_d = fig.add_subplot(gs[1, 0])
    tert = pd.read_csv("outputs/tables/compare_preschool_study/age_stratified_group_effects.csv")
    texp = tert[tert["outcome"] == "global_exponent"]
    rows = []
    for _, r in texp.iterrows():
        label = r["age_stratum"].replace("tertile_", "").replace("_", " ")
        rows.append({"label": label, "beta": r["coef_TD_vs_ASD_adjusted"],
                     "ci_low": r["ci_low"], "ci_high": r["ci_high"]})
    _forest_from_rows(ax_d, rows, highlight={"3 oldest", "tertile 3 oldest"})
    panel_letter(ax_d, "D")

    ax_e = fig.add_subplot(gs[1, 1:])
    post = age_pred[
        (age_pred["outcome"] == "posterior_exponent") &
        (age_pred["model"] == "linear_interaction")
    ]
    for grp, color in [("ASD", COL_ASD), ("TD", COL_TD)]:
        col = "ASD_pred" if grp == "ASD" else "TD_pred"
        ax_e.plot(post["age_months"], post[col], color=color, lw=1.6, label=grp)
    feat = pd.read_csv("outputs/tables/resting_features_locked.csv")
    feat = participants.merge(feat[["subject_id", "posterior_exponent"]], on="subject_id", how="inner")
    for grp, color in [("ASD", COL_ASD), ("TD", COL_TD)]:
        pts = feat[feat["group"] == grp]
        ax_e.scatter(pts["age_months"], pts["posterior_exponent"], s=14, alpha=0.45,
                     color=color, edgecolors="white", linewidths=0.2, zorder=3)
    ax_e.set_xlabel("Age (months)")
    ax_e.set_ylabel("Posterior exponent")
    ax_e.legend(frameon=False, fontsize=6.5)
    r = pd.read_csv("outputs/tables/spectral_maturation/age_group_interaction_models.csv")
    ix = r[(r["outcome"] == "posterior_exponent") & (r["term"] == "C(group)[T.TD]:age_months")].iloc[0]
    ax_e.text(0.02, 0.98, f"group × age: β = {ix['coef']:.4f}\np = {ix['pvalue']:.4f}",
              transform=ax_e.transAxes, ha="left", va="top", fontsize=6.5, color=COL_GRAY)
    panel_letter(ax_e, "E")

    return _save(fig, "Figure3_age_moderation")


def make_figure4(deriv: Path) -> Path:
    apply_v2_style()
    scores = pd.read_csv(deriv / "stats" / "normative_exponent_scores.csv")
    dev = pd.read_csv(deriv / "stats" / "spectral_maturation_deviation_scores.csv")
    dev = dev.merge(
        scores[["subject_id", "global_exponent"]],
        on="subject_id", how="left", suffixes=("", "_obs"),
    )

    fig = plt.figure(figsize=mm_figsize(183, 110))
    gs = GridSpec(1, 4, figure=fig, wspace=0.5, left=0.07, right=0.98, top=0.88, bottom=0.18)

    ax_a = fig.add_subplot(gs[0, 0])
    td = scores[scores["group"] == "TD"]
    asd = scores[scores["group"] == "ASD"]
    age_grid = np.linspace(scores["age_months"].min(), scores["age_months"].max(), 80)
    med = {
        "sex": scores["sex"].mode().iloc[0],
        "IQ_total": scores["IQ_total"].median(),
        "usable_epochs": scores["usable_epochs"].median(),
        "mean_r_squared": scores["mean_r_squared"].median(),
    }
    fit = ols(
        "global_exponent ~ age_months + C(sex) + IQ_total + usable_epochs + mean_r_squared",
        data=td,
    ).fit()
    pred_df = pd.DataFrame({
        "age_months": age_grid,
        "sex": med["sex"],
        "IQ_total": med["IQ_total"],
        "usable_epochs": med["usable_epochs"],
        "mean_r_squared": med["mean_r_squared"],
    })
    ax_a.plot(age_grid, fit.predict(pred_df), color=COL_TD, lw=1.6, label="TD normative fit")
    ax_a.scatter(asd["age_months"], asd["global_exponent"], s=16, alpha=0.6,
                 color=COL_ASD, edgecolors="white", linewidths=0.2, label="ASD")
    ax_a.set_xlabel("Age (months)")
    ax_a.set_ylabel("Global exponent")
    ax_a.legend(frameon=False, fontsize=6)
    panel_letter(ax_a, "A")

    ax_b = fig.add_subplot(gs[0, 1])
    plot_group_boxpanel(ax_b, scores.dropna(subset=["deviation_z"]),
                        "deviation_z", "Global deviation (z)", None, None)
    ax_b.axhline(0, color=COL_LIGHT, lw=1.0, zorder=0)
    panel_letter(ax_b, "B")

    ax_c = fig.add_subplot(gs[0, 2])
    dev_post = dev.dropna(subset=["posterior_exponent_deviation_z"]).copy()
    dev_post = dev_post.rename(columns={"posterior_exponent_deviation_z": "deviation_z"})
    plot_group_boxpanel(ax_c, dev_post, "deviation_z", "Posterior deviation (z)", None, None)
    ax_c.axhline(0, color=COL_LIGHT, lw=1.0, zorder=0)
    panel_letter(ax_c, "C")

    ax_d = fig.add_subplot(gs[0, 3])
    asd_dev = scores[scores["group"] == "ASD"]
    ax_d.scatter(asd_dev["age_months"], asd_dev["deviation_z"], s=18, alpha=0.65,
                 color=COL_ASD, edgecolors="white", linewidths=0.2)
    if len(asd_dev) >= 3:
        coef = np.polyfit(asd_dev["age_months"], asd_dev["deviation_z"], 1)
        xs = np.linspace(asd_dev["age_months"].min(), asd_dev["age_months"].max(), 50)
        ax_d.plot(xs, np.poly1d(coef)(xs), color=COL_GRAY, lw=1.3)
    ax_d.axhline(0, color=COL_LIGHT, lw=1.0, zorder=0)
    ax_d.set_xlabel("Age (months)")
    ax_d.set_ylabel("Deviation score (ASD)")
    panel_letter(ax_d, "D")

    return _save(fig, "Figure4_normative_deviation")


def make_figure5(outputs: Path, deriv: Path) -> Path:
    apply_v2_style()
    robust = pd.read_csv(outputs / "tables" / "global_exponent_robustness_models.csv")
    knee = pd.read_csv(outputs / "tables" / "compare_preschool_study" / "fixed_vs_knee_summary.csv")
    split = pd.read_csv(outputs / "tables" / "extension" / "split_half_reliability.csv")
    iclabel = pd.read_csv(outputs / "tables" / "iclabel_sensitivity" / "iclabel_local_posterior_exponent_fdr_summary.csv")
    ic_g = pd.read_csv(outputs / "tables" / "iclabel_sensitivity" / "iclabel_vs_primary_comparison.csv")

    fig = plt.figure(figsize=mm_figsize(183, 145))
    gs = GridSpec(2, 3, figure=fig, hspace=0.55, wspace=0.5,
                  left=0.10, right=0.98, top=0.94, bottom=0.08)

    ax_a = fig.add_subplot(gs[0, 0])
    rob = robust[robust["model_name"].isin(ROBUSTNESS_ORDER)].copy()
    rob["label"] = rob["model_name"].map({
        "model_1": "Group only",
        "model_2": "Age, sex",
        "model_3": "IQ",
        "model_4": "Primary",
        "model_5": "Mean R²",
        "model_6": "Bad channels",
    })
    rob = rob.set_index("model_name").loc[ROBUSTNESS_ORDER].reset_index()
    effects = rob.rename(columns={
        "group_coef_TD_vs_ASD": "beta",
        "group_ci_low": "ci_low",
        "group_ci_high": "ci_high",
    })
    plot_forest(ax_a, effects, "beta", "ci_low", "ci_high", effects["label"].tolist(), "β (TD − ASD)")
    panel_letter(ax_a, "A")

    ax_b = fig.add_subplot(gs[0, 1])
    rows = []
    for _, r in knee.iterrows():
        fr = r["freq_range"].replace("–", "-").replace(" Hz", "")
        mode = "fixed" if r["aperiodic_mode"] == "fixed" else "knee"
        rows.append({
            "label": f"{fr} {mode}",
            "beta": r["coef_TD_vs_ASD"],
            "ci_low": r["ci_low"],
            "ci_high": r["ci_high"],
            "mode": mode,
        })
    y = np.arange(len(rows))
    ax_b.axvline(0, color=COL_LIGHT, lw=1.2)
    for i, row in enumerate(rows):
        fmt = "o" if row["mode"] == "fixed" else "o"
        mfc = COL_GRAY if row["mode"] == "fixed" else "white"
        ax_b.errorbar(row["beta"], i,
                      xerr=[[row["beta"] - row["ci_low"]], [row["ci_high"] - row["beta"]]],
                      fmt=fmt, color=COL_GRAY, ecolor=COL_GRAY, markerfacecolor=mfc,
                      elinewidth=1.0, capsize=2.5, markersize=4.5, mew=0.8)
    ax_b.set_yticks(y)
    ax_b.set_yticklabels([r["label"] for r in rows], fontsize=6)
    ax_b.set_xlabel("β (TD − ASD)")
    panel_letter(ax_b, "B")

    ax_c = fig.add_subplot(gs[0, 2])
    ic_rows = [{"label": "Global primary", "beta": 0.079, "ci_low": 0.018, "ci_high": 0.140}]
    for _, r in ic_g[(ic_g["outcome"] == "global_exponent") & (ic_g["analysis"].str.startswith("iclabel"))].iterrows():
        ic_rows.append({
            "label": r["analysis"].replace("iclabel_threshold_", "Global ICLabel "),
            "beta": r["coef_TD_vs_ASD"],
            "ci_low": r["ci_low"],
            "ci_high": r["ci_high"],
        })
    for _, r in iclabel.iterrows():
        ic_rows.append({
            "label": f"Posterior {r['threshold']} {r['subset'][:5]}",
            "beta": r["coef_TD_vs_ASD"],
            "ci_low": r["ci_low"],
            "ci_high": r["ci_high"],
        })
    _forest_from_rows(ax_c, ic_rows)
    panel_letter(ax_c, "C")

    ax_d = fig.add_subplot(gs[1, 0])
    metrics = split["metric"].str.replace("_", " ").tolist()
    sb = split["spearman_brown_spearman"].values
    ax_d.bar(metrics, sb, color=COL_GRAY, alpha=0.75, width=0.6)
    ax_d.set_ylim(0.94, 1.0)
    ax_d.set_ylabel("Spearman–Brown")
    ax_d.tick_params(axis="x", rotation=25, labelsize=6)
    panel_letter(ax_d, "D")

    ax_e = fig.add_subplot(gs[1, 1:])
    iaf = pd.read_csv("outputs/tables/spectral_maturation/age_group_interaction_models.csv")
    indep = pd.read_csv("outputs/tables/spectral_maturation/independence_models.csv")
    age_row = iaf[(iaf["outcome"] == "alpha_cf") & (iaf["term"] == "age_months")].iloc[0]
    grp_row = iaf[(iaf["outcome"] == "alpha_cf") & (iaf["term"] == "C(group)[T.TD]")].iloc[0]
    post_row = indep[
        (indep["model"] == "posterior_exponent_adjusted_iaf")
        & (indep["term"] == "C(group)[T.TD]")
    ].iloc[0]
    forest_rows = [
        {
            "label": "alpha_cf group (n.s.)",
            "beta": float(grp_row["coef"]),
            "ci_low": float(grp_row["ci_low"]),
            "ci_high": float(grp_row["ci_high"]),
        },
        {
            "label": "posterior exponent\nafter alpha_cf adj.",
            "beta": float(post_row["coef"]),
            "ci_low": float(post_row["ci_low"]),
            "ci_high": float(post_row["ci_high"]),
        },
    ]
    ax_e.axis("off")
    ax_e.text(0.02, 0.92, "IAF / alpha_cf sensitivity", fontsize=8, fontweight="bold", transform=ax_e.transAxes)
    ax_e.text(0.02, 0.72, f"alpha_cf increases with age (β = {age_row['coef']:.4f})", fontsize=7, transform=ax_e.transAxes)
    ax_e.text(0.02, 0.58, "No significant alpha_cf group or group × age effect", fontsize=7, transform=ax_e.transAxes)
    inner = ax_e.inset_axes([0.45, 0.12, 0.52, 0.78])
    _forest_from_rows(inner, forest_rows)
    panel_letter(ax_e, "E")

    return _save(fig, "Figure5_robustness")


def make_extended_data_figure1(outputs: Path) -> Path:
    apply_v2_style()
    full = pd.read_csv(outputs / "ml_biomarker" / "classification_results.csv")
    older = pd.read_csv(outputs / "ml_biomarker" / "classification_results__abc_ageint_older72_v2check.csv")
    delong_full = pd.read_csv(outputs / "ml_biomarker" / "delong_results.csv")
    delong_old = pd.read_csv(outputs / "ml_biomarker" / "delong_results__abc_ageint_older72_v2check.csv")
    imp_full = pd.read_csv(outputs / "ml_biomarker" / "feature_importance.csv")
    imp_old = pd.read_csv(outputs / "ml_biomarker" / "feature_importance__abc_ageint_older72_v2check.csv")

    def best_auc(df: pd.DataFrame, prefix: str) -> float:
        sub = df[df["feature_set"].str.startswith(prefix)]
        return float(sub["AUC_mean"].max())

    fig = plt.figure(figsize=mm_figsize(183, 95))
    gs = GridSpec(1, 4, figure=fig, wspace=0.45, left=0.07, right=0.98, top=0.85, bottom=0.22)

    ax_a = fig.add_subplot(gs[0, 0])
    aucs = [best_auc(full, "Model A"), best_auc(full, "Model B"), best_auc(full, "Model C")]
    labels = ["Periodic\n(Model A)", "Aperiodic\n(Model B)", "Combined\n(Model C)"]
    bars = ax_a.bar(labels, aucs, color=[COL_GRAY, COL_ASD, COL_TD], width=0.65, alpha=0.85)
    ax_a.set_ylim(0.4, 0.9)
    ax_a.set_ylabel("AUC")
    ax_a.axhline(0.5, color=COL_LIGHT, lw=1.0)
    for b, v in zip(bars, aucs):
        ax_a.text(b.get_x() + b.get_width() / 2, v + 0.02, f"{v:.3f}", ha="center", fontsize=6.5)
    p_ab = delong_full.loc[delong_full["comparison"] == "Model A vs Model B", "p_value"].iloc[0]
    p_bc = delong_full.loc[delong_full["comparison"] == "Model B vs Model C", "p_value"].iloc[0]
    ax_a.text(0.5, 0.98, f"DeLong A vs B: p = {p_ab:.3f}\nDeLong B vs C: p = {p_bc:.3f}",
              transform=ax_a.transAxes, ha="center", va="top", fontsize=6)
    ax_a.set_title("Full sample", fontsize=7.5)
    panel_letter(ax_a, "A")

    ax_b = fig.add_subplot(gs[0, 1])
    b_auc = best_auc(older, "Model B")
    row = older[(older["feature_set"].str.startswith("Model B")) & (older["classifier"] == "LogisticRegression")].iloc[0]
    ax_b.bar(["Model B +\nage interactions"], [b_auc], color=COL_ASD, width=0.5, alpha=0.85)
    ax_b.set_ylim(0.4, 0.95)
    ax_b.set_ylabel("AUC")
    ax_b.text(0, b_auc + 0.02, f"AUC = {b_auc:.3f}", ha="center", fontsize=6.5)
    ax_b.text(0.5, 0.55, f"Balanced Acc = {row['Balanced_Accuracy_mean']:.3f}\nF1 = {row['F1_mean']:.3f}",
              transform=ax_b.transAxes, ha="center", fontsize=6.5)
    p_ab2 = delong_old.loc[delong_old["comparison"] == "Model A vs Model B", "p_value"].iloc[0]
    p_bc2 = delong_old.loc[delong_old["comparison"] == "Model B vs Model C", "p_value"].iloc[0]
    ax_b.text(0.5, 0.98, f"A vs B: p = {p_ab2:.3f}\nB vs C: p = {p_bc2:.3f}",
              transform=ax_b.transAxes, ha="center", va="top", fontsize=6)
    ax_b.set_title(">72 months", fontsize=7.5)
    panel_letter(ax_b, "B")

    ax_c = fig.add_subplot(gs[0, 2])
    ax_c.bar(["Full\nModel B", ">72 mo\nModel B"], [aucs[1], b_auc],
             color=[COL_ASD, COL_TD], width=0.55, alpha=0.85)
    ax_c.set_ylim(0.4, 0.95)
    ax_c.set_ylabel("Best AUC")
    ax_c.text(0.5, 0.95, "ROC curves unavailable;\nAUC summary shown",
              transform=ax_c.transAxes, ha="center", va="top", fontsize=6, color=COL_GRAY)
    panel_letter(ax_c, "C")

    ax_d = fig.add_subplot(gs[0, 3])
    top = imp_old.head(6).iloc[::-1]
    ax_d.barh(top["feature"], top["importance"], color=COL_GRAY, alpha=0.8)
    ax_d.set_xlabel("Permutation importance")
    ax_d.set_title(">72 mo Model B", fontsize=7)
    panel_letter(ax_d, "D")

    return _save(fig, "ExtendedData_Figure1_machine_learning")


def make_supplementary_figure3() -> Path:
    apply_v2_style()
    fig, ax = plt.subplots(figsize=mm_figsize(120, 90))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    boxes = [
        (5, 9.0, "Traditional periodic peaks:\nno robust group differences", "#EEEEEE"),
        (5, 7.2, "Global exponent:\nASD flatter than TD", COL_ASD),
        (5, 5.4, "Posterior exponent:\nstrongest spatially concentrated effect", COL_TD),
        (5, 3.6, "Age moderation:\nstronger in older children", "#D9EAF7"),
        (5, 1.8, "Normative deviation:\nnegative ASD offset from TD trajectory", "#E8F5E9"),
        (5, 0.2, "Machine learning:\nexploratory stratification, not diagnosis", "#F5F5F5"),
    ]
    for x, y, text, color in boxes:
        patch = FancyBboxPatch((x - 3.5, y - 0.55), 7.0, 1.1,
                               boxstyle="round,pad=0.02,rounding_size=0.08",
                               linewidth=0.8, edgecolor=COL_GRAY, facecolor=color)
        ax.add_patch(patch)
        ax.text(x, y, text, ha="center", va="center", fontsize=8)
    for y0, y1 in [(8.45, 7.75), (6.65, 5.95), (4.85, 4.15), (3.05, 2.35), (1.25, 0.55)]:
        ax.annotate("", xy=(5, y1), xytext=(5, y0),
                    arrowprops=dict(arrowstyle="-|>", color=COL_GRAY, lw=1.0))
    return _save(fig, "Supplementary_Figure_S3_result_hierarchy")


def generate_all_nc_figures(cfg: dict[str, Any], deriv: Path, outputs: Path) -> dict[str, Path]:
    NC_OUT.mkdir(parents=True, exist_ok=True)
    participants = load_main_cohort(cfg, deriv)
    paths = {
        "Figure1": make_figure1(cfg, participants, deriv),
        "Figure2": make_figure2(cfg, participants, deriv),
        "Figure3": make_figure3(cfg, participants, deriv),
        "Figure4": make_figure4(deriv),
        "Figure5": make_figure5(outputs, deriv),
        "ExtendedData1": make_extended_data_figure1(outputs),
        "SupplementaryS3": make_supplementary_figure3(),
    }
    return paths
