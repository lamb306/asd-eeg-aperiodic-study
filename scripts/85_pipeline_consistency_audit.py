#!/usr/bin/env python
"""主研究 vs HBN 外部验证：流程一致性系统审计。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import mne
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.formula.api import mixedlm, ols

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config  # noqa: E402
from src.io_utils import attach_usable_epochs, exclude_specparam_low_quality, load_analysis_participants, save_csv  # noqa: E402
from src.stats_utils import model_results_to_row, run_ols  # noqa: E402

COV = " + age_months + C(sex) + IQ_total + usable_epochs"
POST_CH = ("E33", "E36", "E37", "E38")
OUT = PROJECT_ROOT / "outputs_external_hbn" / "pipeline_consistency_audit"
MAIN_CFG = PROJECT_ROOT / "config/config_resting_matched_postqc.yaml"
HBN = {
    "eyes_open": PROJECT_ROOT / "config/config_external_hbn_resting_100x2_eyes_open.yaml",
    "eyes_closed": PROJECT_ROOT / "config/config_external_hbn_resting_100x2_eyes_closed.yaml",
    "continuous": PROJECT_ROOT / "config/config_external_hbn_resting_100x2_continuous.yaml",
}


def electrode_coords() -> pd.DataFrame:
    montage = mne.channels.make_standard_montage("GSN-HydroCel-64_1.0")
    pos = montage.get_positions()["ch_pos"]
    rows = []
    for ch in POST_CH:
        xyz = pos[ch]
        rows.append({"channel": ch, "x_m": xyz[0], "y_m": xyz[1], "z_m": xyz[2]})
    return pd.DataFrame(rows)


def compare_configs() -> pd.DataFrame:
    cfgs = {"main": load_config(MAIN_CFG)}
    for k, p in HBN.items():
        cfgs[f"hbn_{k}"] = load_config(p)
    keys = [
        ("eeg.montage", lambda c: c["eeg"]["montage"]),
        ("eeg.resting_condition", lambda c: c["eeg"].get("resting_condition")),
        ("filter.notch_hz", lambda c: c["filter"]["notch_hz"]),
        ("epochs.min_usable_epochs", lambda c: c["epochs"]["min_usable_epochs"]),
        ("psd.welch", lambda c: c["psd"]["welch"]),
        ("specparam", lambda c: c["specparam"]),
        ("fit_quality.min_r_squared", lambda c: c["fit_quality"]["min_r_squared"]),
        ("fit_quality.subject_invalid_channel_ratio_max", lambda c: c["fit_quality"]["subject_invalid_channel_ratio_max"]),
    ]
    rows = []
    for label, fn in keys:
        row = {"parameter": label}
        for name, cfg in cfgs.items():
            row[name] = str(fn(cfg))
        rows.append(row)
    return pd.DataFrame(rows)


def segment_stats() -> pd.DataFrame:
    rows = []
    for cond, cfg_path in HBN.items():
        pre = pd.read_csv(Path(load_config(cfg_path)["paths"]["derivatives_root"]) / "qc/preproc_summary.csv")
        ok = pre[pre["status"] == "ok"].copy()
        rows.append(
            {
                "condition": cond,
                "n_ok": len(ok),
                "seconds_mean": ok["usable_seconds"].mean(),
                "seconds_median": ok["usable_seconds"].median(),
                "seconds_p10": ok["usable_seconds"].quantile(0.1),
                "seconds_p90": ok["usable_seconds"].quantile(0.9),
                "epochs_mean": ok["usable_epochs"].mean(),
                "epochs_median": ok["usable_epochs"].median(),
                "expected_theoretical_sec": { "eyes_open": 100, "eyes_closed": 200, "continuous": "~300+"}[cond],
            }
        )
    return pd.DataFrame(rows)


def qc_group_compare(label: str, deriv: Path) -> pd.DataFrame:
    pre = pd.read_csv(deriv / "qc/preproc_summary.csv")
    sp = pd.read_csv(deriv / "specparam/specparam_qc_summary_subject.csv")
    ch = pd.read_csv(deriv / "specparam/specparam_channel_results_qc.csv")
    if "fit_valid" in ch.columns:
        ch = ch[ch["fit_valid"]]
    ch_sub = ch.groupby(["subject_id", "group"]).agg(
        r2_mean=("r_squared", "mean"),
        fit_error_mean=("fit_error", "mean"),
        n_valid_ch=("channel", "count"),
    ).reset_index()
    df = pre.merge(sp, on=["subject_id", "group"], how="inner", suffixes=("_pre", "_sp"))
    df = df.merge(ch_sub, on=["subject_id", "group"], how="left")
    metrics = ["usable_epochs", "bad_channel_count", "ica_n_removed", "mean_r_squared", "invalid_channel_ratio", "r2_mean", "fit_error_mean"]
    rows = []
    for m in metrics:
        a = pd.to_numeric(df.loc[df["group"] == "ASD", m], errors="coerce").dropna()
        t = pd.to_numeric(df.loc[df["group"] == "TD", m], errors="coerce").dropna()
        if len(a) < 3 or len(t) < 3:
            continue
        _, p = stats.ttest_ind(a, t, equal_var=False)
        rows.append({"dataset": label, "metric": m, "ASD_mean": a.mean(), "TD_mean": t.mean(), "pvalue": p, "n_asd": len(a), "n_td": len(t)})
    return pd.DataFrame(rows)


def run_group_models(cfg_path: Path, label: str) -> pd.DataFrame:
    cfg = load_config(cfg_path)
    deriv = Path(cfg["paths"]["derivatives_root"])
    participants = load_analysis_participants(cfg)
    participants = attach_usable_epochs(participants, deriv)
    participants = exclude_specparam_low_quality(participants, deriv)
    roi = pd.read_csv(deriv / "roi/specparam_subject_global.csv")
    df = participants.merge(roi, on=["subject_id", "group"], how="inner")
    ch = pd.read_csv(deriv / "specparam/specparam_channel_results_qc.csv")
    if "fit_valid" in ch.columns:
        ch = ch[ch["fit_valid"]]
    rows = []
    for outcome in ["global_exponent", "occipital_exponent"]:
        sub = df.dropna(subset=[outcome, "group", "age_months", "sex", "IQ_total", "usable_epochs"])
        rows.extend(model_results_to_row(run_ols(f"{outcome} ~ C(group){COV}", sub), label, outcome))
    e38 = ch[ch["channel"] == "E38"].merge(participants, on=["subject_id", "group"])
    e38 = e38.dropna(subset=["aperiodic_exponent", "group", "age_months", "sex", "IQ_total", "usable_epochs"])
    rows.extend(model_results_to_row(run_ols(f"aperiodic_exponent ~ C(group){COV}", e38), label, "E38_exponent"))
    cl = ch[ch["channel"].isin(POST_CH)].merge(participants, on=["subject_id", "group"])
    cl_mean = cl.groupby(["subject_id", "group"], as_index=False)["aperiodic_exponent"].mean().rename(columns={"aperiodic_exponent": "post4_exponent"})
    cl_df = participants.merge(cl_mean, on=["subject_id", "group"]).dropna(subset=["post4_exponent", "group", "age_months", "sex", "IQ_total", "usable_epochs"])
    rows.extend(model_results_to_row(run_ols(f"post4_exponent ~ C(group){COV}", cl_df), label, "post4_mean_exponent"))
    return pd.DataFrame(rows)


def ec_eo_delta_and_mixed() -> tuple[pd.DataFrame, pd.DataFrame]:
    cfg_ec = load_config(HBN["eyes_closed"])
    cfg_eo = load_config(HBN["eyes_open"])
    dec = Path(cfg_ec["paths"]["derivatives_root"])
    deo = Path(cfg_eo["paths"]["derivatives_root"])
    roi_ec = pd.read_csv(dec / "roi/specparam_subject_global.csv")
    roi_eo = pd.read_csv(deo / "roi/specparam_subject_global.csv")
    ch_ec = pd.read_csv(dec / "specparam/specparam_channel_results_qc.csv")
    ch_eo = pd.read_csv(deo / "specparam/specparam_channel_results_qc.csv")
    for ch in (ch_ec, ch_eo):
        if "fit_valid" in ch.columns:
            ch.drop(ch[~ch["fit_valid"]].index, inplace=True)
    part = load_analysis_participants(cfg_ec)
    part = attach_usable_epochs(part, dec)
    part = exclude_specparam_low_quality(part, dec)
    common = set(roi_ec["subject_id"]) & set(roi_eo["subject_id"]) & set(part["subject_id"])
    roi_ec = roi_ec[roi_ec["subject_id"].isin(common)].copy()
    roi_eo = roi_eo[roi_eo["subject_id"].isin(common)].copy()
    delta = roi_ec.merge(roi_eo, on=["subject_id", "group"], suffixes=("_ec", "_eo"))
    delta["occipital_delta_ec_minus_eo"] = delta["occipital_exponent_ec"] - delta["occipital_exponent_eo"]
    delta["global_delta_ec_minus_eo"] = delta["global_exponent_ec"] - delta["global_exponent_eo"]
    p = part[part["subject_id"].isin(common)]
    delta = delta.merge(p[["subject_id", "age_months", "sex", "IQ_total", "usable_epochs"]], on="subject_id")
    delta_rows = []
    for outcome in ["occipital_delta_ec_minus_eo", "global_delta_ec_minus_eo"]:
        sub = delta.dropna(subset=[outcome, "group", "age_months", "sex", "IQ_total", "usable_epochs"])
        delta_rows.extend(model_results_to_row(run_ols(f"{outcome} ~ C(group){COV}", sub), "ec_minus_eo_delta", outcome))

    # E38 delta
    e38_ec = ch_ec[ch_ec["channel"] == "E38"][["subject_id", "group", "aperiodic_exponent"]].rename(columns={"aperiodic_exponent": "e38_ec"})
    e38_eo = ch_eo[ch_eo["channel"] == "E38"][["subject_id", "aperiodic_exponent"]].rename(columns={"aperiodic_exponent": "e38_eo"})
    d38 = e38_ec.merge(e38_eo, on="subject_id").merge(p, on=["subject_id", "group"], how="inner")
    d38["e38_delta"] = d38["e38_ec"] - d38["e38_eo"]
    sub = d38.dropna(subset=["e38_delta", "group", "age_months", "sex", "IQ_total", "usable_epochs"])
    delta_rows.extend(model_results_to_row(run_ols(f"e38_delta ~ C(group){COV}", sub), "ec_minus_eo_delta", "E38_delta"))

    # long format mixed model on occipital
    long_rows = []
    for cond, roi in [("eyes_closed", roi_ec), ("eyes_open", roi_eo)]:
        tmp = roi.merge(p, on=["subject_id", "group"], how="inner")
        tmp["eye_condition"] = cond
        long_rows.append(tmp[["subject_id", "group", "eye_condition", "occipital_exponent", "global_exponent", "age_months", "sex", "IQ_total", "usable_epochs"]])
    long_df = pd.concat(long_rows, ignore_index=True)
    long_df = long_df.dropna(subset=["occipital_exponent", "group", "eye_condition", "age_months", "sex", "IQ_total", "usable_epochs"])
    long_df["eye_condition"] = pd.Categorical(long_df["eye_condition"], categories=["eyes_open", "eyes_closed"])
    mixed_rows = []
    for outcome in ["occipital_exponent", "global_exponent"]:
        formula = f"{outcome} ~ C(group) * C(eye_condition) + age_months + C(sex) + IQ_total + usable_epochs"
        try:
            md = mixedlm(formula, long_df, groups=long_df["subject_id"])
            fit = md.fit(reml=False, method="lbfgs", maxiter=200, disp=False)
            for term in fit.params.index:
                mixed_rows.append({"outcome": outcome, "term": term, "coef": fit.params[term], "pvalue": fit.pvalues[term], "n_obs": len(long_df), "n_subjects": long_df["subject_id"].nunique()})
        except Exception as exc:
            mixed_rows.append({"outcome": outcome, "term": "ERROR", "coef": np.nan, "pvalue": np.nan, "n_obs": len(long_df), "n_subjects": long_df["subject_id"].nunique(), "error": str(exc)})
    return pd.DataFrame(delta_rows), pd.DataFrame(mixed_rows)


def sample_event_audit(n: int = 8) -> pd.DataFrame:
    from src.external_hbn import CLOSE_MARKER, OPEN_MARKER, RESTING_START_MARKER, events_tsv_for_set, resting_set_path

    sub = pd.read_csv(PROJECT_ROOT / "data/participants/external_validation_subjects_hbn_eeg_balanced_100x2.csv").head(n)
    root = PROJECT_ROOT / "data/external_hbn_eeg"
    rows = []
    for _, r in sub.iterrows():
        p = resting_set_path(root, r["release"], r["subject_id"])
        if p is None or not p.exists():
            continue
        ev_path = events_tsv_for_set(p)
        if ev_path is None:
            continue
        ev = pd.read_csv(ev_path, sep="\t")
        close = ev[ev["value"].astype(str).str.contains(CLOSE_MARKER, case=False, na=False)]["onset"].tolist()
        open_ = ev[ev["value"].astype(str).str.contains(OPEN_MARKER, case=False, na=False)]["onset"].tolist()
        start = ev[ev["value"].astype(str).str.contains(RESTING_START_MARKER, case=False, na=False)]["onset"].tolist()
        rows.append(
            {
                "subject_id": r["subject_id"],
                "n_close_events": len(close),
                "n_open_events": len(open_),
                "n_resting_start": len(start),
                "close_onsets_first5": str(close[:5]),
                "open_onsets_first5": str(open_[:5]),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    save_csv(electrode_coords(), OUT / "posterior_electrode_coords_gsn_hydrocel_64.csv")
    save_csv(compare_configs(), OUT / "config_comparison.csv")
    save_csv(segment_stats(), OUT / "hbn_segment_duration_summary.csv")
    save_csv(sample_event_audit(8), OUT / "hbn_event_marker_audit_sample.csv")

    qc_all = [qc_group_compare("main", Path(load_config(MAIN_CFG)["paths"]["derivatives_root"]))]
    for cond, p in HBN.items():
        qc_all.append(qc_group_compare(f"hbn_{cond}", Path(load_config(p)["paths"]["derivatives_root"])))
    save_csv(pd.concat(qc_all, ignore_index=True), OUT / "qc_group_comparison.csv")

    models = [run_group_models(MAIN_CFG, "main")]
    for cond, p in HBN.items():
        models.append(run_group_models(p, f"hbn_{cond}"))
    res = pd.concat(models, ignore_index=True)
    save_csv(res, OUT / "key_outcomes_group_models.csv")
    delta_df, mixed_df = ec_eo_delta_and_mixed()
    save_csv(delta_df, OUT / "ec_minus_eo_delta_models.csv")
    save_csv(mixed_df, OUT / "group_by_eye_condition_mixed_models.csv")

    summary = res[res["term"].str.contains("group", na=False)][["model", "outcome", "coef", "pvalue", "n_obs"]]
    print("=== posterior electrode coords (GSN-HydroCel-64_1.0) ===")
    print(pd.read_csv(OUT / "posterior_electrode_coords_gsn_hydrocel_64.csv").to_string(index=False))
    print("\n=== segment duration summary ===")
    print(pd.read_csv(OUT / "hbn_segment_duration_summary.csv").to_string(index=False))
    print("\n=== key group models (C(group)[T.TD]) ===")
    print(summary.to_string(index=False))
    print("\n=== EC-EO delta models ===")
    print(delta_df[delta_df["term"].str.contains("group", na=False)][["model", "outcome", "coef", "pvalue", "n_obs"]].to_string(index=False))
    print("\n=== group x eye mixed model ===")
    print(mixed_df.to_string(index=False))
    print(f"\nSaved audit outputs to {OUT}")


if __name__ == "__main__":
    main()
