"""
Targeted experiments to improve ASD vs TD AUC.

Experiments:
1) Add age + age interaction features to aperiodic ROI model.
2) Restrict to older children (age_months > 72).
3) Channel-wise exponent features with Elastic-Net logistic regression.
"""

from __future__ import annotations

import os
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


RANDOM_STATE = 42
OUT_DIR = "outputs/ml_biomarker"


def encode_group_label(group_series: pd.Series) -> np.ndarray:
    mapping = {"asd": 1, "td": 0, "1": 1, "0": 0}
    encoded = group_series.astype(str).str.strip().str.lower().map(mapping)
    if encoded.isna().any():
        raise ValueError(f"Unexpected group labels: {group_series.unique().tolist()}")
    return encoded.astype(int).to_numpy()


def compute_metrics(y_true: np.ndarray, y_score: np.ndarray) -> Dict[str, float]:
    y_pred = (y_score >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    sens = tp / (tp + fn) if (tp + fn) > 0 else np.nan
    spec = tn / (tn + fp) if (tn + fp) > 0 else np.nan
    return {
        "AUC": roc_auc_score(y_true, y_score),
        "Accuracy": accuracy_score(y_true, y_pred),
        "Sensitivity": sens,
        "Specificity": spec,
        "Balanced_Accuracy": balanced_accuracy_score(y_true, y_pred),
        "F1": f1_score(y_true, y_pred),
    }


def nested_cv_eval(
    X: pd.DataFrame,
    y: np.ndarray,
    model_space: Dict[str, Tuple[object, dict]],
) -> pd.DataFrame:
    outer_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    inner_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    outer_splits = list(outer_cv.split(np.zeros(len(y)), y))

    rows = []
    for model_name, (estimator, param_grid) in model_space.items():
        fold_metrics = []
        for train_idx, test_idx in outer_splits:
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            pipe = Pipeline(
                [("scaler", StandardScaler()), ("classifier", estimator)]
            )
            grid = GridSearchCV(
                estimator=pipe,
                param_grid=param_grid,
                scoring="roc_auc",
                cv=inner_cv,
                n_jobs=-1,
                refit=True,
            )
            grid.fit(X_train, y_train)
            y_score = grid.best_estimator_.predict_proba(X_test)[:, 1]
            fold_metrics.append(compute_metrics(y_test, y_score))

        fold_df = pd.DataFrame(fold_metrics)
        row = {"model": model_name, "n": len(y), "n_features": X.shape[1]}
        for m in ["AUC", "Accuracy", "Sensitivity", "Specificity", "Balanced_Accuracy", "F1"]:
            row[f"{m}_mean"] = fold_df[m].mean()
            row[f"{m}_std"] = fold_df[m].std(ddof=1)
        rows.append(row)
    return pd.DataFrame(rows).sort_values("AUC_mean", ascending=False)


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)

    base = pd.read_csv("outputs/tables/resting_features_locked.csv")
    participants = pd.read_csv("data/participants/participants.csv")[
        ["subject_id", "age_months"]
    ].drop_duplicates("subject_id")
    channel = pd.read_csv("derivatives/specparam/specparam_channel_results.csv")[
        ["subject_id", "group", "channel", "aperiodic_exponent"]
    ]

    # Merge age into subject-level dataset.
    df = base.merge(participants, on="subject_id", how="left")

    aperiodic_cols = [
        "global_exponent",
        "global_offset",
        "posterior_exponent",
        "frontal_exponent",
        "central_exponent",
        "temporal_exponent",
        "parietal_exponent",
        "occipital_exponent",
    ]
    required = aperiodic_cols + ["age_months", "group"]
    df = df.dropna(subset=required).copy()
    y_full = encode_group_label(df["group"])

    model_space_std = {
        "SVM_RBF": (
            SVC(kernel="rbf", probability=True, random_state=RANDOM_STATE),
            {"classifier__C": [0.01, 0.1, 1, 10, 100], "classifier__gamma": ["scale", 0.01, 0.1, 1]},
        ),
        "LogisticRegression": (
            LogisticRegression(solver="liblinear", max_iter=5000, random_state=RANDOM_STATE),
            {"classifier__C": [0.01, 0.1, 1, 10]},
        ),
        "RandomForest": (
            RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1),
            {"classifier__n_estimators": [100, 200], "classifier__max_depth": [3, 5, None]},
        ),
    }

    # (1) Age interaction features
    exp1 = df.copy()
    exp1["age_x_global_exponent"] = exp1["age_months"] * exp1["global_exponent"]
    exp1["age_x_posterior_exponent"] = exp1["age_months"] * exp1["posterior_exponent"]
    x1_cols = aperiodic_cols + ["age_months", "age_x_global_exponent", "age_x_posterior_exponent"]
    res1 = nested_cv_eval(exp1[x1_cols], y_full, model_space_std)
    res1.insert(0, "experiment", "Exp1_AperiodicPlusAgeInteractions")

    # (2) Older child only (>72 months)
    older = exp1.loc[exp1["age_months"] > 72].copy()
    y2 = encode_group_label(older["group"])
    res2 = nested_cv_eval(older[x1_cols], y2, model_space_std)
    res2.insert(0, "experiment", "Exp2_OlderChild_AperiodicPlusAgeInteractions")

    # (3) Channel-wise exponent + Elastic-Net logistic
    ch_wide = (
        channel.pivot_table(
            index=["subject_id", "group"],
            columns="channel",
            values="aperiodic_exponent",
            aggfunc="mean",
        )
        .reset_index()
    )
    ch_wide.columns.name = None
    ch_wide = ch_wide.merge(participants, on="subject_id", how="left")
    ch_wide = ch_wide.dropna(subset=["age_months"]).copy()

    channel_cols = [c for c in ch_wide.columns if isinstance(c, str) and c.startswith("E")]
    ch_wide = ch_wide.dropna(subset=channel_cols)
    y3 = encode_group_label(ch_wide["group"])

    model_space_ch = {
        "LogisticElasticNet": (
            LogisticRegression(
                penalty="elasticnet",
                solver="saga",
                max_iter=10000,
                random_state=RANDOM_STATE,
            ),
            {
                "classifier__C": [0.01, 0.1, 1, 10],
                "classifier__l1_ratio": [0.1, 0.3, 0.5, 0.7, 0.9, 1.0],
            },
        )
    }
    res3 = nested_cv_eval(ch_wide[channel_cols], y3, model_space_ch)
    res3.insert(0, "experiment", "Exp3_ChannelWiseExponent_ElasticNet")

    all_res = pd.concat([res1, res2, res3], axis=0, ignore_index=True)
    out_csv = os.path.join(OUT_DIR, "auc_boost_experiments.csv")
    all_res.to_csv(out_csv, index=False)

    best = all_res.sort_values("AUC_mean", ascending=False).iloc[0]
    print("========== AUC boost experiments done ==========")
    print(f"Saved: {out_csv}")
    print(
        f"Best: {best['experiment']} + {best['model']} | "
        f"AUC_mean={best['AUC_mean']:.4f} | n={int(best['n'])}"
    )


if __name__ == "__main__":
    main()
