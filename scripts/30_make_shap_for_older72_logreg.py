"""
Generate SHAP summary plot for the older-child (>72 months) + age-interaction
Logistic Regression model (the ~0.80 AUC setting).
"""

from __future__ import annotations

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


RANDOM_STATE = 42
OUT_DIR = "outputs/ml_biomarker"


def encode_group_label(group_series: pd.Series) -> np.ndarray:
    mapping = {"asd": 1, "td": 0, "1": 1, "0": 0}
    y = group_series.astype(str).str.strip().str.lower().map(mapping)
    if y.isna().any():
        raise ValueError(f"Unexpected group labels: {group_series.unique().tolist()}")
    return y.astype(int).to_numpy()


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)

    base = pd.read_csv("outputs/tables/resting_features_locked.csv")
    age = pd.read_csv("data/participants/participants.csv")[["subject_id", "age_months"]]
    age = age.drop_duplicates(subset=["subject_id"])
    df = base.merge(age, on="subject_id", how="left")
    df = df.loc[df["age_months"] > 72].copy()

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
    ]
    df["age_x_global_exponent"] = df["age_months"] * df["global_exponent"]
    df["age_x_posterior_exponent"] = df["age_months"] * df["posterior_exponent"]
    features += ["age_x_global_exponent", "age_x_posterior_exponent"]

    df = df.dropna(subset=features + ["group"]).reset_index(drop=True)
    X = df[features].copy()
    y = encode_group_label(df["group"])

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
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    grid = GridSearchCV(
        estimator=pipe,
        param_grid={"classifier__C": [0.01, 0.1, 1, 10]},
        scoring="roc_auc",
        cv=cv,
        n_jobs=-1,
        refit=True,
    )
    grid.fit(X, y)
    best_model = grid.best_estimator_

    scaler = best_model.named_steps["scaler"]
    clf = best_model.named_steps["classifier"]
    X_scaled = scaler.transform(X)

    explainer = shap.LinearExplainer(clf, X_scaled)
    shap_values = explainer.shap_values(X_scaled)
    if isinstance(shap_values, list):
        shap_values = shap_values[0]

    out_png = os.path.join(OUT_DIR, "shap_summary_older72_ageint_logreg.png")
    plt.figure()
    shap.summary_plot(
        shap_values,
        features=X_scaled,
        feature_names=features,
        show=False,
        max_display=20,
    )
    plt.tight_layout()
    plt.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.close()

    mean_abs = np.mean(np.abs(shap_values), axis=0)
    out_csv = os.path.join(OUT_DIR, "shap_importance_older72_ageint_logreg.csv")
    pd.DataFrame(
        {"feature": features, "mean_abs_shap": mean_abs}
    ).sort_values("mean_abs_shap", ascending=False).to_csv(out_csv, index=False)

    print("========== SHAP done ==========")
    print(f"Saved: {out_png}")
    print(f"Saved: {out_csv}")
    print(f"n={len(df)}, best_C={grid.best_params_['classifier__C']}")


if __name__ == "__main__":
    main()
