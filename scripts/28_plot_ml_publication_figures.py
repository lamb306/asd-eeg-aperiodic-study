"""
Publication-style figures for EEG classification results.

Figures:
1) Grouped AUC bar chart (full cohort vs older subgroup)
2) Multi-model ROC curves (full cohort and older subgroup)
3) Feature-importance ranking (full cohort and older subgroup)
"""

from __future__ import annotations

import os
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import auc, roc_curve
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


def get_model_space() -> Dict[str, Tuple[object, dict]]:
    return {
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
        "LogisticElasticNet": (
            LogisticRegression(
                penalty="elasticnet",
                solver="saga",
                max_iter=10000,
                random_state=RANDOM_STATE,
            ),
            {"classifier__C": [0.01, 0.1, 1, 10], "classifier__l1_ratio": [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]},
        ),
    }


def add_age_and_interactions(df: pd.DataFrame) -> pd.DataFrame:
    participants = pd.read_csv("data/participants/participants.csv")[["subject_id", "age_months"]]
    participants = participants.drop_duplicates(subset=["subject_id"])
    out = df.merge(participants, on="subject_id", how="left")
    out["age_x_global_exponent"] = out["age_months"] * out["global_exponent"]
    out["age_x_posterior_exponent"] = out["age_months"] * out["posterior_exponent"]
    return out


def get_best_rows_by_model_prefix(results_df: pd.DataFrame) -> Dict[str, pd.Series]:
    out: Dict[str, pd.Series] = {}
    for prefix in ["Model A", "Model B", "Model C"]:
        sub = results_df[results_df["feature_set"].str.startswith(prefix)].copy()
        if len(sub) == 0:
            continue
        out[prefix] = sub.sort_values("AUC_mean", ascending=False).iloc[0]
    return out


def nested_oof_scores(
    df: pd.DataFrame,
    feature_cols: List[str],
    y: np.ndarray,
    classifier_name: str,
) -> np.ndarray:
    model_space = get_model_space()
    estimator, param_grid = model_space[classifier_name]

    X = df[feature_cols].copy()
    outer_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    inner_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    oof = np.full(len(y), np.nan, dtype=float)

    for tr, te in outer_cv.split(X, y):
        X_train, X_test = X.iloc[tr], X.iloc[te]
        y_train = y[tr]
        pipe = Pipeline([("scaler", StandardScaler()), ("classifier", clone(estimator))])
        grid = GridSearchCV(
            estimator=pipe,
            param_grid=param_grid,
            scoring="roc_auc",
            cv=inner_cv,
            n_jobs=-1,
            refit=True,
        )
        grid.fit(X_train, y_train)
        oof[te] = grid.best_estimator_.predict_proba(X_test)[:, 1]
    return oof


def set_pub_style() -> None:
    plt.rcParams.update(
        {
            "font.size": 11,
            "axes.titlesize": 12,
            "axes.labelsize": 11,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.fontsize": 9,
            "figure.dpi": 150,
            "savefig.dpi": 300,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def plot_auc_grouped_bar(
    full_df: pd.DataFrame,
    older_df: pd.DataFrame,
    out_png: str,
) -> None:
    full_best = get_best_rows_by_model_prefix(full_df)
    older_best = get_best_rows_by_model_prefix(older_df)

    models = ["Model A", "Model B", "Model C"]
    full_vals = [full_best[m]["AUC_mean"] for m in models]
    older_vals = [older_best[m]["AUC_mean"] for m in models]

    x = np.arange(len(models))
    w = 0.35
    fig, ax = plt.subplots(figsize=(8.2, 5.6))
    b1 = ax.bar(x - w / 2, full_vals, width=w, color="#8DA0CB", label="Full cohort")
    b2 = ax.bar(x + w / 2, older_vals, width=w, color="#FC8D62", label="Older subgroup (>72 months)")

    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.set_ylim(0.35, 0.9)
    ax.set_ylabel("AUC (outer-fold mean)")
    ax.set_title("AUC Comparison Across Feature Sets and Cohorts")
    ax.axhline(0.7, color="gray", linestyle="--", linewidth=1, alpha=0.7)
    ax.axhline(0.8, color="gray", linestyle=":", linewidth=1, alpha=0.7)
    ax.legend(frameon=False, loc="upper left")

    for bars in [b1, b2]:
        for bar in bars:
            h = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                h + 0.008,
                f"{h:.3f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )
    for i, (f, o) in enumerate(zip(full_vals, older_vals)):
        ax.text(x[i], max(f, o) + 0.03, f"Δ={o-f:+.3f}", ha="center", va="bottom", fontsize=9)

    fig.tight_layout()
    fig.savefig(out_png, bbox_inches="tight")
    plt.close(fig)


def plot_multi_model_roc(
    full_base_df: pd.DataFrame,
    older_ageint_df: pd.DataFrame,
    full_results: pd.DataFrame,
    older_results: pd.DataFrame,
    out_png: str,
) -> None:
    full_best = get_best_rows_by_model_prefix(full_results)
    older_best = get_best_rows_by_model_prefix(older_results)

    y_full = encode_group_label(full_base_df["group"])
    y_older = encode_group_label(older_ageint_df["group"])

    fig, axes = plt.subplots(1, 2, figsize=(12, 5.2), sharex=True, sharey=True)
    color_map = {"Model A": "#1b9e77", "Model B": "#d95f02", "Model C": "#7570b3"}

    for model_key, row in full_best.items():
        feature_cols = row["features"].split(";")
        scores = nested_oof_scores(full_base_df, feature_cols, y_full, row["classifier"])
        fpr, tpr, _ = roc_curve(y_full, scores)
        axes[0].plot(
            fpr,
            tpr,
            color=color_map[model_key],
            linewidth=2,
            label=f"{model_key} ({row['classifier']}, AUC={row['AUC_mean']:.3f})",
        )
    axes[0].plot([0, 1], [0, 1], "k--", linewidth=1)
    axes[0].set_title("Full Cohort")
    axes[0].set_xlabel("False Positive Rate")
    axes[0].set_ylabel("True Positive Rate")
    axes[0].legend(frameon=False, loc="lower right")

    for model_key, row in older_best.items():
        feature_cols = row["features"].split(";")
        scores = nested_oof_scores(older_ageint_df, feature_cols, y_older, row["classifier"])
        fpr, tpr, _ = roc_curve(y_older, scores)
        axes[1].plot(
            fpr,
            tpr,
            color=color_map[model_key],
            linewidth=2,
            label=f"{model_key} ({row['classifier']}, AUC={row['AUC_mean']:.3f})",
        )
    axes[1].plot([0, 1], [0, 1], "k--", linewidth=1)
    axes[1].set_title("Older Subgroup (>72 months, +Age Interactions)")
    axes[1].set_xlabel("False Positive Rate")
    axes[1].legend(frameon=False, loc="lower right")

    fig.suptitle("ROC Curves Across Feature Sets and Cohorts", y=1.02, fontsize=13)
    fig.tight_layout()
    fig.savefig(out_png, bbox_inches="tight")
    plt.close(fig)


def feature_color(feature_name: str) -> str:
    name = feature_name.lower()
    if "age_x_" in name or name == "age_months":
        return "#E67E22"  # age effects
    if "exponent" in name or "offset" in name:
        return "#2C7FB8"  # aperiodic
    return "#66A61E"  # periodic


def plot_feature_importance_rank(
    full_imp: pd.DataFrame,
    older_imp: pd.DataFrame,
    out_png: str,
) -> None:
    top_full = full_imp.sort_values("rank").head(10).copy()
    top_old = older_imp.sort_values("rank").head(10).copy()

    fig, axes = plt.subplots(1, 2, figsize=(12, 6), sharex=False)

    for ax, df_plot, title in [
        (axes[0], top_full, "Full Cohort Best Model"),
        (axes[1], top_old, "Older Subgroup Best Model"),
    ]:
        df_plot = df_plot.iloc[::-1]
        colors = [feature_color(f) for f in df_plot["feature"]]
        bars = ax.barh(df_plot["feature"], df_plot["importance"], color=colors)
        ax.set_title(title)
        ax.set_xlabel("Importance")
        for b in bars:
            w = b.get_width()
            ax.text(w + 0.001, b.get_y() + b.get_height() / 2, f"{w:.3f}", va="center", fontsize=8)

    handles = [
        plt.Line2D([0], [0], color="#2C7FB8", lw=8, label="Aperiodic features"),
        plt.Line2D([0], [0], color="#E67E22", lw=8, label="Age / interaction features"),
        plt.Line2D([0], [0], color="#66A61E", lw=8, label="Periodic features"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.03))
    fig.suptitle("Feature Importance Ranking", y=1.02, fontsize=13)
    fig.tight_layout()
    fig.savefig(out_png, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    set_pub_style()

    full_results = pd.read_csv(os.path.join(OUT_DIR, "classification_results.csv"))
    older_results = pd.read_csv(
        os.path.join(OUT_DIR, "classification_results__abc_ageint_older72_v2check.csv")
    )
    full_imp = pd.read_csv(os.path.join(OUT_DIR, "feature_importance.csv"))
    older_imp = pd.read_csv(
        os.path.join(OUT_DIR, "feature_importance__abc_ageint_older72_v2check.csv")
    )

    full_base_df = pd.read_csv("outputs/tables/resting_features_locked.csv").copy()
    older_ageint_df = add_age_and_interactions(full_base_df)
    older_ageint_df = older_ageint_df.loc[older_ageint_df["age_months"] > 72].copy()
    older_ageint_df = older_ageint_df.dropna(
        subset=[
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
    ).reset_index(drop=True)

    auc_bar_path = os.path.join(OUT_DIR, "paper_auc_grouped_bar.png")
    roc_path = os.path.join(OUT_DIR, "paper_roc_multimodel.png")
    fi_path = os.path.join(OUT_DIR, "paper_feature_importance_rank.png")

    plot_auc_grouped_bar(full_results, older_results, auc_bar_path)
    plot_multi_model_roc(full_base_df, older_ageint_df, full_results, older_results, roc_path)
    plot_feature_importance_rank(full_imp, older_imp, fi_path)

    print("========== Publication figures done ==========")
    print(f"Saved: {auc_bar_path}")
    print(f"Saved: {roc_path}")
    print(f"Saved: {fi_path}")
    print(f"Older subgroup n used in plotting: {len(older_ageint_df)}")


if __name__ == "__main__":
    main()
