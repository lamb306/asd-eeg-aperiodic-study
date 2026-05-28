"""
Visualize directional coefficients for the older-child + age-interaction
logistic regression model (Model B).

Outputs:
- outputs/ml_biomarker/logreg_coef_direction_older72_ageint.csv
- outputs/ml_biomarker/logreg_coef_direction_older72_ageint.png
"""

from __future__ import annotations

import os
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


RANDOM_STATE = 42
OUT_DIR = "outputs/ml_biomarker"


def encode_group_label(group_series: pd.Series) -> np.ndarray:
    mapping = {"asd": 1, "td": 0, "1": 1, "0": 0}
    out = group_series.astype(str).str.strip().str.lower().map(mapping)
    if out.isna().any():
        raise ValueError(f"Unexpected group labels: {group_series.unique().tolist()}")
    return out.astype(int).to_numpy()


def build_dataset() -> pd.DataFrame:
    base = pd.read_csv("outputs/tables/resting_features_locked.csv")
    age = pd.read_csv("data/participants/participants.csv")[["subject_id", "age_months"]]
    age = age.drop_duplicates(subset=["subject_id"])

    df = base.merge(age, on="subject_id", how="left")
    df = df.loc[df["age_months"] > 72].copy()
    df["age_x_global_exponent"] = df["age_months"] * df["global_exponent"]
    df["age_x_posterior_exponent"] = df["age_months"] * df["posterior_exponent"]
    return df


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)

    df = build_dataset()
    features = [
        "global_exponent",
        "global_offset",
        "posterior_exponent",
        "frontal_exponent",
        "central_exponent",
        "temporal_exponent",
        "parietal_exponent",
        "occipital_exponent",
        "age_months",
        "age_x_global_exponent",
        "age_x_posterior_exponent",
    ]
    df = df.dropna(subset=features + ["group"]).reset_index(drop=True)
    X = df[features].copy()
    y = encode_group_label(df["group"])

    outer_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    inner_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    coef_matrix: List[np.ndarray] = []
    best_cs: List[float] = []
    fold_id = 0

    for tr, _te in outer_cv.split(X, y):
        fold_id += 1
        X_train, y_train = X.iloc[tr], y[tr]

        pipe = Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "classifier",
                    LogisticRegression(
                        solver="liblinear",
                        max_iter=5000,
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        )
        grid = GridSearchCV(
            estimator=pipe,
            param_grid={"classifier__C": [0.01, 0.1, 1, 10]},
            scoring="roc_auc",
            cv=inner_cv,
            n_jobs=-1,
            refit=True,
        )
        grid.fit(X_train, y_train)
        best_model = grid.best_estimator_
        clf = best_model.named_steps["classifier"]
        coef_matrix.append(clf.coef_.ravel())
        best_cs.append(float(grid.best_params_["classifier__C"]))

    coef_arr = np.vstack(coef_matrix)
    mean_coef = coef_arr.mean(axis=0)
    std_coef = coef_arr.std(axis=0, ddof=1)
    pos_rate = (coef_arr > 0).mean(axis=0)

    out_df = pd.DataFrame(
        {
            "feature": features,
            "coef_mean": mean_coef,
            "coef_std": std_coef,
            "positive_rate_across_outer_folds": pos_rate,
            "abs_coef_mean": np.abs(mean_coef),
        }
    ).sort_values("abs_coef_mean", ascending=False)

    out_csv = os.path.join(OUT_DIR, "logreg_coef_direction_older72_ageint.csv")
    out_df.to_csv(out_csv, index=False)

    # Plot top-to-bottom by absolute magnitude.
    plot_df = out_df.iloc[::-1].copy()
    colors = np.where(plot_df["coef_mean"] >= 0, "#D62728", "#1F77B4")

    plt.figure(figsize=(10, 7))
    plt.barh(
        plot_df["feature"],
        plot_df["coef_mean"],
        xerr=plot_df["coef_std"],
        color=colors,
        alpha=0.9,
        ecolor="black",
        capsize=3,
    )
    plt.axvline(0, color="black", linewidth=1)
    plt.xlabel("Standardized Logistic Coefficient (mean ± SD across outer folds)")
    plt.ylabel("Feature")
    plt.title("Directional Coefficients: Older Children (>72 months), Model B + Age Interactions")
    plt.tight_layout()

    out_png = os.path.join(OUT_DIR, "logreg_coef_direction_older72_ageint.png")
    plt.savefig(out_png, dpi=300)
    plt.close()

    print("========== Done ==========")
    print(f"Saved: {out_csv}")
    print(f"Saved: {out_png}")
    print(f"n={len(df)}")
    print(f"Best C across outer folds: {best_cs}")


if __name__ == "__main__":
    main()
