#!/usr/bin/env python
"""
39_translational_incremental_models.py
--------------------------------------
Translational Analysis:
Model A (resting only) vs Model C (resting + delta + task ISC)
using strict nested CV and paired DeLong test.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.base import clone
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


RANDOM_STATE = 42


@dataclass
class ModelResult:
    model_name: str
    features: List[str]
    oof_scores: np.ndarray
    auc_fold: List[float]
    best_params: List[dict]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Nested-CV translational incremental models")
    parser.add_argument("--project_root", type=str, default=".", help="项目根目录")
    parser.add_argument(
        "--resting_csv",
        type=str,
        default="outputs/tables/resting_features_locked.csv",
        help="静息态特征CSV",
    )
    parser.add_argument(
        "--delta_csv",
        type=str,
        default="derivatives_task_movie/stats/delta_exponent_subject_values.csv",
        help="Delta exponent CSV",
    )
    parser.add_argument(
        "--isc_csv",
        type=str,
        default="derivatives_task_movie/stats/movie_isc_subject_values_with_neutral.csv",
        help="含 neutral 的ISC CSV",
    )
    parser.add_argument(
        "--out_stats_dir",
        type=str,
        default="derivatives_task_movie/stats",
        help="统计输出目录",
    )
    parser.add_argument(
        "--out_fig_dir",
        type=str,
        default="outputs_task_movie/figures",
        help="图像输出目录",
    )
    parser.add_argument("--n_splits", type=int, default=5, help="外层/内层CV折数")
    return parser.parse_args()


def encode_group_label(group_series: pd.Series) -> np.ndarray:
    mapping = {"asd": 1, "td": 0, "1": 1, "0": 0}
    encoded = group_series.astype(str).str.strip().str.lower().map(mapping)
    if encoded.isna().any():
        vals = sorted(group_series.astype(str).unique().tolist())
        raise ValueError(f"无法编码group为二分类: {vals}")
    return encoded.astype(int).to_numpy()


def compute_midrank(x: np.ndarray) -> np.ndarray:
    order = np.argsort(x)
    sorted_x = x[order]
    n = len(x)
    midranks = np.zeros(n, dtype=float)
    i = 0
    while i < n:
        j = i
        while j < n and sorted_x[j] == sorted_x[i]:
            j += 1
        midranks[i:j] = 0.5 * (i + j - 1) + 1
        i = j
    out = np.empty(n, dtype=float)
    out[order] = midranks
    return out


def fast_delong(preds_sorted_transposed: np.ndarray, label_1_count: int):
    m = label_1_count
    n = preds_sorted_transposed.shape[1] - m
    pos = preds_sorted_transposed[:, :m]
    neg = preds_sorted_transposed[:, m:]
    k = preds_sorted_transposed.shape[0]

    tx = np.empty((k, m), dtype=float)
    ty = np.empty((k, n), dtype=float)
    tz = np.empty((k, m + n), dtype=float)

    for r in range(k):
        tx[r, :] = compute_midrank(pos[r, :])
        ty[r, :] = compute_midrank(neg[r, :])
        tz[r, :] = compute_midrank(preds_sorted_transposed[r, :])

    aucs = tz[:, :m].sum(axis=1) / (m * n) - (m + 1.0) / (2.0 * n)
    v01 = (tz[:, :m] - tx[:, :]) / n
    v10 = 1.0 - (tz[:, m:] - ty[:, :]) / m
    sx = np.cov(v01)
    sy = np.cov(v10)
    delong_cov = sx / m + sy / n
    return aucs, delong_cov


def delong_roc_test(y_true: np.ndarray, pred1: np.ndarray, pred2: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=int)
    pred1 = np.asarray(pred1, dtype=float)
    pred2 = np.asarray(pred2, dtype=float)

    order = np.argsort(-y_true)
    label_1_count = int(y_true.sum())
    preds = np.vstack([pred1, pred2])[:, order]

    aucs, delong_cov = fast_delong(preds, label_1_count)
    diff = aucs[0] - aucs[1]
    var = delong_cov[0, 0] + delong_cov[1, 1] - 2 * delong_cov[0, 1]
    if var <= 0:
        return 1.0
    z = np.abs(diff) / np.sqrt(var)
    p_value = 2 * (1 - stats.norm.cdf(z))
    return float(p_value)


def nested_cv_logistic(
    X: pd.DataFrame,
    y: np.ndarray,
    outer_splits: List[Tuple[np.ndarray, np.ndarray]],
    inner_cv: StratifiedKFold,
    model_name: str,
) -> ModelResult:
    oof_scores = np.full(shape=len(y), fill_value=np.nan, dtype=float)
    fold_aucs: List[float] = []
    best_params: List[dict] = []

    clf = LogisticRegression(
        solver="liblinear",
        max_iter=5000,
        random_state=RANDOM_STATE,
    )
    pipe = Pipeline([("scaler", StandardScaler()), ("classifier", clf)])
    grid = {"classifier__C": [0.01, 0.1, 1, 10, 100]}

    for train_idx, test_idx in outer_splits:
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        gs = GridSearchCV(
            estimator=clone(pipe),
            param_grid=grid,
            scoring="roc_auc",
            cv=inner_cv,
            n_jobs=-1,
            refit=True,
        )
        gs.fit(X_train, y_train)
        best = gs.best_estimator_
        best_params.append(gs.best_params_)
        y_score = best.predict_proba(X_test)[:, 1]
        oof_scores[test_idx] = y_score
        fold_aucs.append(float(roc_auc_score(y_test, y_score)))

    return ModelResult(
        model_name=model_name,
        features=X.columns.tolist(),
        oof_scores=oof_scores,
        auc_fold=fold_aucs,
        best_params=best_params,
    )


def build_dataset(resting: pd.DataFrame, delta: pd.DataFrame, isc: pd.DataFrame) -> pd.DataFrame:
    rest = resting[["subject_id", "group", "posterior_exponent"]].copy()
    rest["subject_id"] = rest["subject_id"].astype(str)
    rest["group"] = rest["group"].astype(str).str.upper()
    rest["posterior_exponent"] = pd.to_numeric(rest["posterior_exponent"], errors="coerce")
    rest = rest.rename(columns={"posterior_exponent": "resting_posterior_exponent"})

    d = delta[
        [
            "subject_id",
            "group",
            "Delta_Exponent_mental",
            "Delta_Exponent_pain",
        ]
    ].copy()
    d["subject_id"] = d["subject_id"].astype(str)
    d["group"] = d["group"].astype(str).str.upper()
    for c in ["Delta_Exponent_mental", "Delta_Exponent_pain"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")

    i = isc[["subject_id", "group", "event_type", "isc_z"]].copy()
    i["subject_id"] = i["subject_id"].astype(str)
    i["group"] = i["group"].astype(str).str.upper()
    i["event_type"] = i["event_type"].astype(str).str.lower()
    i["isc_z"] = pd.to_numeric(i["isc_z"], errors="coerce")
    i = i[i["event_type"].isin(["mental", "pain", "neutral"])].copy()
    i_wide = i.pivot_table(
        index=["subject_id", "group"],
        columns="event_type",
        values="isc_z",
        aggfunc="mean",
    ).reset_index()
    i_wide.columns.name = None
    i_wide = i_wide.rename(
        columns={
            "mental": "mental_isc_z",
            "pain": "pain_isc_z",
            "neutral": "neutral_isc_z",
        }
    )

    merged = rest.merge(d, on=["subject_id", "group"], how="inner").merge(
        i_wide, on=["subject_id", "group"], how="inner"
    )
    return merged


def main() -> None:
    args = parse_args()
    root = Path(args.project_root).resolve()
    out_stats = (root / args.out_stats_dir).resolve()
    out_fig = (root / args.out_fig_dir).resolve()
    out_stats.mkdir(parents=True, exist_ok=True)
    out_fig.mkdir(parents=True, exist_ok=True)

    resting = pd.read_csv(root / args.resting_csv)
    delta = pd.read_csv(root / args.delta_csv)
    isc = pd.read_csv(root / args.isc_csv)
    df = build_dataset(resting=resting, delta=delta, isc=isc)

    model_a_features = ["resting_posterior_exponent"]
    model_c_features = [
        "resting_posterior_exponent",
        "Delta_Exponent_mental",
        "Delta_Exponent_pain",
        "mental_isc_z",
        "pain_isc_z",
        "neutral_isc_z",
    ]

    req = ["group"] + model_c_features
    ml_df = df.dropna(subset=req).reset_index(drop=True)
    y = encode_group_label(ml_df["group"])

    outer_cv = StratifiedKFold(n_splits=args.n_splits, shuffle=True, random_state=RANDOM_STATE)
    outer_splits = list(outer_cv.split(np.zeros(len(y)), y))
    inner_cv = StratifiedKFold(n_splits=args.n_splits, shuffle=True, random_state=RANDOM_STATE)

    res_a = nested_cv_logistic(
        X=ml_df[model_a_features],
        y=y,
        outer_splits=outer_splits,
        inner_cv=inner_cv,
        model_name="Model A (resting posterior only)",
    )
    res_c = nested_cv_logistic(
        X=ml_df[model_c_features],
        y=y,
        outer_splits=outer_splits,
        inner_cv=inner_cv,
        model_name="Model C (resting + delta + task ISC)",
    )

    auc_a = float(roc_auc_score(y, res_a.oof_scores))
    auc_c = float(roc_auc_score(y, res_c.oof_scores))
    delong_p = delong_roc_test(y, res_c.oof_scores, res_a.oof_scores)

    summary = pd.DataFrame(
        [
            {
                "model": res_a.model_name,
                "n_total": int(len(ml_df)),
                "n_asd": int((ml_df["group"] == "ASD").sum()),
                "n_td": int((ml_df["group"] == "TD").sum()),
                "features": ";".join(res_a.features),
                "auc_oof": auc_a,
                "auc_fold_mean": float(np.mean(res_a.auc_fold)),
                "auc_fold_sd": float(np.std(res_a.auc_fold, ddof=1)),
            },
            {
                "model": res_c.model_name,
                "n_total": int(len(ml_df)),
                "n_asd": int((ml_df["group"] == "ASD").sum()),
                "n_td": int((ml_df["group"] == "TD").sum()),
                "features": ";".join(res_c.features),
                "auc_oof": auc_c,
                "auc_fold_mean": float(np.mean(res_c.auc_fold)),
                "auc_fold_sd": float(np.std(res_c.auc_fold, ddof=1)),
            },
        ]
    )
    auc_comp = pd.DataFrame(
        [
            {
                "comparison": "Model C vs Model A",
                "auc_model_c_oof": auc_c,
                "auc_model_a_oof": auc_a,
                "auc_delta_c_minus_a": auc_c - auc_a,
                "delong_p_value": delong_p,
            }
        ]
    )

    summary_path = out_stats / "translational_model_auc_summary.csv"
    comp_path = out_stats / "translational_model_auc_comparison_delong.csv"
    data_path = out_stats / "translational_model_input_dataset.csv"
    oof_path = out_stats / "translational_model_oof_scores.csv"
    params_path = out_stats / "translational_model_best_params_by_fold.csv"
    summary.to_csv(summary_path, index=False)
    auc_comp.to_csv(comp_path, index=False)
    ml_df.to_csv(data_path, index=False)
    pd.DataFrame(
        {
            "subject_id": ml_df["subject_id"].values,
            "group": ml_df["group"].values,
            "y_true": y,
            "model_a_score": res_a.oof_scores,
            "model_c_score": res_c.oof_scores,
        }
    ).to_csv(oof_path, index=False)
    param_rows = []
    for i, p in enumerate(res_a.best_params, start=1):
        param_rows.append({"model": "A", "fold": i, **p})
    for i, p in enumerate(res_c.best_params, start=1):
        param_rows.append({"model": "C", "fold": i, **p})
    pd.DataFrame(param_rows).to_csv(params_path, index=False)

    fpr_a, tpr_a, _ = roc_curve(y, res_a.oof_scores)
    fpr_c, tpr_c, _ = roc_curve(y, res_c.oof_scores)
    plt.figure(figsize=(7.2, 5.8))
    plt.plot(fpr_a, tpr_a, lw=2, label=f"Model A (AUC={auc_a:.3f})")
    plt.plot(fpr_c, tpr_c, lw=2, label=f"Model C (AUC={auc_c:.3f})")
    plt.plot([0, 1], [0, 1], "--", color="gray", lw=1)
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("Nested-CV OOF ROC: Translational Incremental Value")
    plt.legend(loc="lower right")
    plt.text(
        0.98,
        0.02,
        f"DeLong p = {delong_p:.4g}\nDelta AUC = {auc_c - auc_a:.3f}",
        ha="right",
        va="bottom",
        transform=plt.gca().transAxes,
        fontsize=10,
        bbox={"facecolor": "white", "alpha": 0.82, "edgecolor": "#777"},
    )
    plt.tight_layout()
    fig_path = out_fig / "translational_modelA_vs_modelC_roc.png"
    plt.savefig(fig_path, dpi=220)
    plt.close()

    print("Saved:", summary_path)
    print("Saved:", comp_path)
    print("Saved:", data_path)
    print("Saved:", oof_path)
    print("Saved:", params_path)
    print("Saved:", fig_path)
    print("\nAUC summary:")
    print(summary.to_string(index=False))
    print("\nAUC comparison:")
    print(auc_comp.to_string(index=False))


if __name__ == "__main__":
    main()

