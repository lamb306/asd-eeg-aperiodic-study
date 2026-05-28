"""
Nested-CV EEG biomarker classification for ASD vs TD.

Implements:
1) Model A (periodic only), Model B (aperiodic only), Model C (combined)
2) Strict nested CV with leakage-safe Pipeline(StandardScaler + classifier)
3) SVM (RBF), Logistic Regression, Random Forest with GridSearchCV
4) Metrics comparison + DeLong test for AUC
5) Explainability: SHAP for tree, permutation importance for SVM/Logistic
6) Figures: ROC (A/B/C in one figure), confusion matrix, feature importance,
   SHAP summary (if applicable)

Default input file is `outputs/tables/resting_features_locked.csv`.
"""

from __future__ import annotations

import argparse
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


RANDOM_STATE = 42

try:
    import shap  # type: ignore
except ImportError:
    shap = None


@dataclass
class NestedCVResult:
    feature_set: str
    classifier: str
    selected_features: List[str]
    fold_metrics: List[Dict[str, float]]
    oof_scores: np.ndarray
    oof_preds: np.ndarray
    best_params_per_fold: List[dict]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Nested CV ASD vs TD EEG classifier with DeLong and explainability."
    )
    parser.add_argument(
        "--input_csv",
        type=str,
        default="outputs/tables/resting_features_locked.csv",
        help="Input CSV path (default: outputs/tables/resting_features_locked.csv).",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="outputs/ml_biomarker",
        help="Output directory for csv/png results.",
    )
    parser.add_argument(
        "--age_csv",
        type=str,
        default="data/participants/participants.csv",
        help="CSV containing subject_id and age_months (used for age filters/interactions).",
    )
    parser.add_argument(
        "--channel_csv",
        type=str,
        default="derivatives/specparam/specparam_channel_results.csv",
        help="Channel-level specparam CSV used by --channelwise mode.",
    )
    parser.add_argument(
        "--use_age_interaction",
        action="store_true",
        help="Add age_months and interactions: age*global_exponent, age*posterior_exponent.",
    )
    parser.add_argument(
        "--older_than_months",
        type=float,
        default=None,
        help="If set, only keep subjects with age_months > this value.",
    )
    parser.add_argument(
        "--channelwise",
        action="store_true",
        help="Run channel-wise exponent model (Logistic Elastic-Net) instead of A/B/C.",
    )
    parser.add_argument(
        "--output_tag",
        type=str,
        default="",
        help="Optional tag appended to output filenames.",
    )
    return parser.parse_args()


def resolve_input_csv_path(input_csv: str) -> str:
    input_path = Path(input_csv)
    if input_path.exists():
        return str(input_path)

    workspace = Path(".").resolve()
    csv_candidates = sorted(workspace.rglob("*.csv"))

    # Heuristic: prefer csv files whose headers contain at least `group`,
    # then prioritize files containing some EEG feature columns.
    scored: List[Tuple[int, str]] = []
    for p in csv_candidates:
        try:
            header_df = pd.read_csv(p, nrows=0)
            cols = [c.lower().strip() for c in header_df.columns]
        except Exception:
            continue

        if "group" not in cols:
            continue

        score = 0
        keys = [
            "global_exponent",
            "global_offset",
            "posterior_exponent",
            "alpha_pw",
            "alpha_cf",
            "theta_pw",
            "beta_pw",
            "frontal_exponent",
            "central_exponent",
            "temporal_exponent",
            "parietal_exponent",
            "occipital_exponent",
        ]
        for k in keys:
            if k in cols:
                score += 1
        scored.append((score, str(p.relative_to(workspace)).replace("\\", "/")))

    scored.sort(key=lambda x: (-x[0], x[1]))
    top_paths = [s[1] for s in scored[:8]]

    msg = (
        f"Input CSV not found: {input_csv}\n"
        "Please pass a valid file path via --input_csv.\n"
    )
    if top_paths:
        msg += "Candidate CSVs in this project (ranked):\n- " + "\n- ".join(top_paths)
    else:
        msg += "No candidate CSV with `group` column found in project."

    raise FileNotFoundError(msg)


def _normalize_col(col_name: str) -> str:
    return re.sub(r"[\s\-]+", "_", col_name.strip().lower())


def _find_first_matching_column(
    columns: List[str], exact_candidates: List[str], regex_patterns: List[str]
) -> str | None:
    col_map = {_normalize_col(c): c for c in columns}

    for cand in exact_candidates:
        key = _normalize_col(cand)
        if key in col_map:
            return col_map[key]

    for col in columns:
        col_norm = _normalize_col(col)
        for pattern in regex_patterns:
            if re.search(pattern, col_norm):
                return col
    return None


def resolve_feature_sets(df: pd.DataFrame) -> Dict[str, List[str]]:
    cols = df.columns.tolist()
    resolved: Dict[str, str] = {}

    feature_specs = {
        "alpha_pw": (["alpha_pw"], [r"alpha.*pw", r"pw.*alpha"]),
        "alpha_cf": (["alpha_cf"], [r"alpha.*cf", r"cf.*alpha"]),
        "theta_pw": (["theta_pw"], [r"theta.*pw", r"pw.*theta"]),
        "beta_pw": (["beta_pw"], [r"beta.*pw", r"pw.*beta"]),
        "global_exponent": (["global_exponent"], [r"global.*exponent", r"exponent.*global"]),
        "global_offset": (["global_offset"], [r"global.*offset", r"offset.*global"]),
        "posterior_exponent": (
            ["posterior_exponent"],
            [r"posterior.*exponent", r"exponent.*posterior"],
        ),
        "frontal_exponent": (
            ["frontal_exponent", "frontal_roi_exponent"],
            [r"frontal.*exponent", r"exponent.*frontal"],
        ),
        "central_exponent": (
            ["central_exponent", "central_roi_exponent"],
            [r"central.*exponent", r"exponent.*central"],
        ),
        "temporal_exponent": (
            ["temporal_exponent", "temporal_roi_exponent"],
            [r"temporal.*exponent", r"exponent.*temporal"],
        ),
        "parietal_exponent": (
            ["parietal_exponent", "parietal_roi_exponent"],
            [r"parietal.*exponent", r"exponent.*parietal"],
        ),
        "occipital_exponent": (
            ["occipital_exponent", "occipital_roi_exponent"],
            [r"occipital.*exponent", r"exponent.*occipital"],
        ),
    }

    missing = []
    for std_name, (exact_candidates, regex_patterns) in feature_specs.items():
        found_col = _find_first_matching_column(cols, exact_candidates, regex_patterns)
        if found_col is None:
            missing.append(std_name)
        else:
            resolved[std_name] = found_col

    # Prompt says periodic features are optional. Missing any periodic columns -> Model A skipped.
    periodic_std = ["alpha_pw", "alpha_cf", "theta_pw", "beta_pw"]
    aperiodic_std = [
        "global_exponent",
        "global_offset",
        "posterior_exponent",
        "frontal_exponent",
        "central_exponent",
        "temporal_exponent",
        "parietal_exponent",
        "occipital_exponent",
    ]

    missing_aperiodic = [f for f in aperiodic_std if f not in resolved]
    if missing_aperiodic:
        raise ValueError(
            "Aperiodic required features are missing: "
            f"{missing_aperiodic}\nAvailable columns: {cols}"
        )

    model_b = [resolved[f] for f in aperiodic_std]
    model_a = [resolved[f] for f in periodic_std if f in resolved]

    feature_sets: Dict[str, List[str]] = {"Model B (aperiodic)": model_b}
    if len(model_a) == 4:
        feature_sets["Model A (periodic)"] = model_a
    else:
        print(
            "[Warning] Periodic features incomplete; Model A and Model C will be skipped. "
            f"Found periodic features: {model_a}"
        )

    if len(model_a) == 4:
        feature_sets["Model C (combined)"] = model_a + model_b

    # Ensure order A, B, C when available.
    ordered = {}
    for k in ["Model A (periodic)", "Model B (aperiodic)", "Model C (combined)"]:
        if k in feature_sets:
            ordered[k] = feature_sets[k]
    return ordered


def resolve_age_column(df: pd.DataFrame) -> str | None:
    return _find_first_matching_column(
        df.columns.tolist(),
        exact_candidates=["age_months", "age", "age_month"],
        regex_patterns=[r"^age(_months)?$"],
    )


def augment_feature_sets_with_age_interactions(
    df: pd.DataFrame,
    feature_sets: Dict[str, List[str]],
    use_age_interaction: bool,
) -> Dict[str, List[str]]:
    age_col = resolve_age_column(df)
    if age_col is None:
        raise ValueError(
            "Age-based options requested, but no age column found. "
            "Please provide age_months via --age_csv merge."
        )
    if not use_age_interaction:
        return feature_sets

    if "global_exponent" not in df.columns or "posterior_exponent" not in df.columns:
        raise ValueError(
            "--use_age_interaction requires global_exponent and posterior_exponent columns."
        )

    age_x_global = "age_x_global_exponent"
    age_x_posterior = "age_x_posterior_exponent"
    df[age_x_global] = df[age_col] * df["global_exponent"]
    df[age_x_posterior] = df[age_col] * df["posterior_exponent"]

    new_sets: Dict[str, List[str]] = {}
    for fs_name, fs_cols in feature_sets.items():
        cols = fs_cols.copy()
        if age_col not in cols:
            cols.append(age_col)
        if "global_exponent" in fs_cols and age_x_global not in cols:
            cols.append(age_x_global)
        if "posterior_exponent" in fs_cols and age_x_posterior not in cols:
            cols.append(age_x_posterior)
        new_sets[fs_name + " + age_interactions"] = cols
    return new_sets


def build_output_name(base_name: str, tag: str) -> str:
    if not tag:
        return base_name
    stem, ext = os.path.splitext(base_name)
    return f"{stem}__{tag}{ext}"


def build_config_tag(args: argparse.Namespace) -> str:
    parts = []
    if args.channelwise:
        parts.append("channelwise")
    else:
        parts.append("abc")
    if args.use_age_interaction:
        parts.append("ageint")
    if args.older_than_months is not None:
        parts.append(f"older{int(args.older_than_months)}")
    if args.output_tag:
        parts.append(args.output_tag)
    return "_".join(parts)


def merge_age_if_needed(df: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    need_age = args.use_age_interaction or (args.older_than_months is not None)
    if not need_age:
        return df
    if resolve_age_column(df) is not None:
        return df

    if "subject_id" not in df.columns:
        raise ValueError(
            "Age options require `subject_id` in input_csv to merge age_months."
        )
    age_df = pd.read_csv(args.age_csv)
    if "subject_id" not in age_df.columns:
        raise ValueError("--age_csv must contain subject_id column.")
    age_col = resolve_age_column(age_df)
    if age_col is None:
        raise ValueError("--age_csv must contain age_months (or age) column.")
    age_df = age_df[["subject_id", age_col]].drop_duplicates(subset=["subject_id"])
    merged = df.merge(age_df, on="subject_id", how="left")
    return merged


def build_channelwise_dataset(args: argparse.Namespace) -> pd.DataFrame:
    df_ch = pd.read_csv(args.channel_csv)
    required = {"subject_id", "group", "channel", "aperiodic_exponent"}
    if not required.issubset(df_ch.columns):
        raise ValueError(
            f"--channel_csv missing required columns: {sorted(required - set(df_ch.columns))}"
        )

    wide = (
        df_ch.pivot_table(
            index=["subject_id", "group"],
            columns="channel",
            values="aperiodic_exponent",
            aggfunc="mean",
        )
        .reset_index()
    )
    wide.columns.name = None
    eeg_cols = [c for c in wide.columns if isinstance(c, str) and c.startswith("E")]
    wide = wide.dropna(subset=eeg_cols).copy()

    # Merge age when age-based options are used.
    if args.use_age_interaction or (args.older_than_months is not None):
        age_df = pd.read_csv(args.age_csv)
        age_col = resolve_age_column(age_df)
        if age_col is None:
            raise ValueError("--age_csv must contain age_months (or age) for channelwise mode.")
        age_df = age_df[["subject_id", age_col]].drop_duplicates(subset=["subject_id"])
        wide = wide.merge(age_df, on="subject_id", how="left")

    return wide


def encode_group_label(group_series: pd.Series) -> np.ndarray:
    if pd.api.types.is_numeric_dtype(group_series):
        vals = sorted(pd.unique(group_series.dropna()))
        if set(vals).issubset({0, 1}):
            return group_series.astype(int).to_numpy()

    mapping = {"asd": 1, "td": 0, "1": 1, "0": 0}
    encoded = group_series.astype(str).str.strip().str.lower().map(mapping)
    if encoded.isna().any():
        unique_vals = sorted(group_series.astype(str).unique().tolist())
        raise ValueError(
            "Unable to map `group` values to binary ASD=1/TD=0. "
            f"Observed values: {unique_vals}"
        )
    return encoded.astype(int).to_numpy()


def get_model_space(channelwise: bool = False) -> Dict[str, Tuple[object, dict]]:
    if channelwise:
        return {
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
    return {
        "SVM_RBF": (
            SVC(kernel="rbf", probability=True, random_state=RANDOM_STATE),
            {
                "classifier__C": [0.01, 0.1, 1, 10, 100],
                "classifier__gamma": ["scale", 0.01, 0.1, 1],
            },
        ),
        "LogisticRegression": (
            LogisticRegression(
                solver="liblinear", max_iter=5000, random_state=RANDOM_STATE
            ),
            {"classifier__C": [0.01, 0.1, 1, 10]},
        ),
        "RandomForest": (
            RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1),
            {
                "classifier__n_estimators": [100, 200],
                "classifier__max_depth": [3, 5, None],
            },
        ),
    }


def compute_binary_metrics(y_true: np.ndarray, y_score: np.ndarray) -> Dict[str, float]:
    y_pred = (y_score >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()

    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else np.nan
    specificity = tn / (tn + fp) if (tn + fp) > 0 else np.nan

    return {
        "AUC": roc_auc_score(y_true, y_score),
        "Accuracy": accuracy_score(y_true, y_pred),
        "Sensitivity": sensitivity,
        "Specificity": specificity,
        "Balanced_Accuracy": balanced_accuracy_score(y_true, y_pred),
        "F1": f1_score(y_true, y_pred),
    }


def nested_cv_single_setting(
    X: pd.DataFrame,
    y: np.ndarray,
    feature_set_name: str,
    classifier_name: str,
    classifier,
    param_grid: dict,
    outer_splits: List[Tuple[np.ndarray, np.ndarray]],
    inner_cv: StratifiedKFold,
) -> NestedCVResult:
    oof_scores = np.full(shape=len(y), fill_value=np.nan, dtype=float)
    oof_preds = np.full(shape=len(y), fill_value=np.nan, dtype=float)
    fold_metrics = []
    best_params_per_fold = []

    for fold_id, (train_idx, test_idx) in enumerate(outer_splits, start=1):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        pipeline = Pipeline(
            [
                ("scaler", StandardScaler()),
                ("classifier", clone(classifier)),
            ]
        )

        grid = GridSearchCV(
            estimator=pipeline,
            param_grid=param_grid,
            scoring="roc_auc",
            cv=inner_cv,
            n_jobs=-1,
            refit=True,
        )
        grid.fit(X_train, y_train)
        best_model = grid.best_estimator_
        best_params_per_fold.append(grid.best_params_)

        y_score = best_model.predict_proba(X_test)[:, 1]
        y_pred = (y_score >= 0.5).astype(int)

        oof_scores[test_idx] = y_score
        oof_preds[test_idx] = y_pred

        fold_m = compute_binary_metrics(y_test, y_score)
        fold_m["fold"] = fold_id
        fold_metrics.append(fold_m)

    return NestedCVResult(
        feature_set=feature_set_name,
        classifier=classifier_name,
        selected_features=X.columns.tolist(),
        fold_metrics=fold_metrics,
        oof_scores=oof_scores,
        oof_preds=oof_preds,
        best_params_per_fold=best_params_per_fold,
    )


def summarize_nested_result(result: NestedCVResult, y_true: np.ndarray) -> Dict[str, object]:
    fold_df = pd.DataFrame(result.fold_metrics)
    pooled_metrics = compute_binary_metrics(y_true, result.oof_scores)

    row = {
        "feature_set": result.feature_set,
        "classifier": result.classifier,
        "features": ";".join(result.selected_features),
    }
    for m in ["AUC", "Accuracy", "Sensitivity", "Specificity", "Balanced_Accuracy", "F1"]:
        row[f"{m}_mean"] = fold_df[m].mean()
        row[f"{m}_std"] = fold_df[m].std(ddof=1)
        row[f"{m}_pooled_oof"] = pooled_metrics[m]
    return row


# -------- DeLong test (AUC comparison) --------
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


def plot_roc_three_models(
    y_true: np.ndarray, model_best_scores: Dict[str, np.ndarray], out_png: str
) -> None:
    plt.figure(figsize=(8, 6))
    for model_name, scores in model_best_scores.items():
        fpr, tpr, _ = roc_curve(y_true, scores)
        auc = roc_auc_score(y_true, scores)
        plt.plot(fpr, tpr, lw=2, label=f"{model_name} (AUC={auc:.3f})")
    plt.plot([0, 1], [0, 1], linestyle="--", color="gray")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curves (Best Classifier in Each Feature Set)")
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(out_png, dpi=300)
    plt.close()


def plot_confusion_matrix_best(
    y_true: np.ndarray, y_pred: np.ndarray, title: str, out_png: str
) -> None:
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["TD(0)", "ASD(1)"])
    fig, ax = plt.subplots(figsize=(6, 5))
    disp.plot(ax=ax, cmap="Blues", colorbar=False)
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(out_png, dpi=300)
    plt.close(fig)


def plot_feature_importance(importance_df: pd.DataFrame, out_png: str) -> None:
    top = importance_df.head(20).copy()
    plt.figure(figsize=(9, 7))
    plt.barh(top["feature"][::-1], top["importance"][::-1])
    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.title("Top 20 Feature Importance")
    plt.tight_layout()
    plt.savefig(out_png, dpi=300)
    plt.close()


def explain_best_model(
    best_row: pd.Series,
    X: pd.DataFrame,
    y: np.ndarray,
    model_space: Dict[str, Tuple[object, dict]],
    out_dir: str,
    shap_png_name: str = "shap_summary.png",
) -> pd.DataFrame:
    classifier_name = best_row["classifier"]
    feature_set_name = best_row["feature_set"]
    feature_cols = best_row["features"].split(";")
    estimator, param_grid = model_space[classifier_name]

    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("classifier", clone(estimator)),
        ]
    )
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    grid = GridSearchCV(
        estimator=pipeline,
        param_grid=param_grid,
        scoring="roc_auc",
        cv=cv,
        n_jobs=-1,
        refit=True,
    )
    X_sel = X[feature_cols]
    grid.fit(X_sel, y)
    best_model = grid.best_estimator_

    clf = best_model.named_steps["classifier"]
    scaler = best_model.named_steps["scaler"]

    if isinstance(clf, RandomForestClassifier):
        if shap is None:
            raise ImportError(
                "Best model is tree-based and requires `shap`, but shap is not installed. "
                "Please run: pip install shap"
            )
        X_scaled = scaler.transform(X_sel)
        explainer = shap.TreeExplainer(clf)
        shap_values = explainer.shap_values(X_scaled)

        # For binary classification, SHAP may return list or array.
        if isinstance(shap_values, list):
            shap_values_to_use = shap_values[1]
        else:
            if shap_values.ndim == 3:
                shap_values_to_use = shap_values[:, :, 1]
            else:
                shap_values_to_use = shap_values

        mean_abs = np.mean(np.abs(shap_values_to_use), axis=0)
        importance_df = pd.DataFrame(
            {"feature": feature_cols, "importance": mean_abs}
        ).sort_values("importance", ascending=False)

        shap_png = os.path.join(out_dir, shap_png_name)
        plt.figure()
        shap.summary_plot(
            shap_values_to_use,
            features=X_scaled,
            feature_names=feature_cols,
            show=False,
            max_display=20,
        )
        plt.tight_layout()
        plt.savefig(shap_png, dpi=300, bbox_inches="tight")
        plt.close()
    else:
        perm = permutation_importance(
            estimator=best_model,
            X=X_sel,
            y=y,
            scoring="roc_auc",
            n_repeats=30,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )
        importance_df = pd.DataFrame(
            {"feature": feature_cols, "importance": perm.importances_mean}
        ).sort_values("importance", ascending=False)

    importance_df["rank"] = np.arange(1, len(importance_df) + 1)
    importance_df["feature_set"] = feature_set_name
    importance_df["classifier"] = classifier_name
    importance_df = importance_df[
        ["rank", "feature", "importance", "feature_set", "classifier"]
    ]
    return importance_df


def find_feature_set_key(
    keys: List[str], target_prefix: str
) -> str | None:
    for k in keys:
        if k.startswith(target_prefix):
            return k
    return None


def main() -> None:
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    config_tag = build_config_tag(args)

    if args.channelwise:
        input_csv_path = args.channel_csv
        df = build_channelwise_dataset(args)
    else:
        input_csv_path = resolve_input_csv_path(args.input_csv)
        df = pd.read_csv(input_csv_path)

    df = merge_age_if_needed(df, args)
    if "group" not in df.columns:
        raise ValueError("Input CSV must contain a `group` column (ASD=1, TD=0).")

    age_col = resolve_age_column(df)
    if args.older_than_months is not None:
        if age_col is None:
            raise ValueError(
                "--older_than_months requested, but no age column was found in merged dataframe."
            )
        df = df.loc[df[age_col] > args.older_than_months].copy()

    if len(df) < 30:
        raise ValueError(
            f"Too few samples after filtering ({len(df)}). "
            "Please relax filtering criteria."
        )

    df = df.reset_index(drop=True)
    y = encode_group_label(df["group"])
    if args.channelwise:
        channel_cols = [c for c in df.columns if isinstance(c, str) and c.startswith("E")]
        if not channel_cols:
            raise ValueError("No channel-wise exponent columns found (expected E1..E64 style).")
        feature_sets = {"Model D (channelwise_aperiodic)": channel_cols}
        if args.use_age_interaction:
            if age_col is None:
                raise ValueError("--use_age_interaction requires age column in channelwise mode.")
            # For channelwise mode, include age as an additive covariate.
            feature_sets = {
                "Model D (channelwise_aperiodic + age)": channel_cols + [age_col]
            }
        model_space = get_model_space(channelwise=True)
    else:
        feature_sets = resolve_feature_sets(df)
        feature_sets = augment_feature_sets_with_age_interactions(
            df=df,
            feature_sets=feature_sets,
            use_age_interaction=args.use_age_interaction,
        )
        model_space = get_model_space(channelwise=False)

    # Build fixed outer splits to keep paired evaluation comparable across settings.
    outer_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    outer_splits = list(outer_cv.split(np.zeros(len(y)), y))
    inner_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    all_nested_results: List[NestedCVResult] = []
    summary_rows = []

    for fs_name, fs_cols in feature_sets.items():
        X_fs = df[fs_cols].copy()
        for clf_name, (clf_estimator, param_grid) in model_space.items():
            print(f"[Running] {fs_name} + {clf_name}")
            result = nested_cv_single_setting(
                X=X_fs,
                y=y,
                feature_set_name=fs_name,
                classifier_name=clf_name,
                classifier=clf_estimator,
                param_grid=param_grid,
                outer_splits=outer_splits,
                inner_cv=inner_cv,
            )
            all_nested_results.append(result)
            summary_rows.append(summarize_nested_result(result, y))

    results_df = pd.DataFrame(summary_rows).sort_values(
        ["feature_set", "AUC_mean"], ascending=[True, False]
    )
    results_path = os.path.join(
        args.output_dir, build_output_name("classification_results.csv", config_tag)
    )
    results_df.to_csv(results_path, index=False)

    # Pick best classifier in each feature set by mean outer-fold AUC.
    model_best_rows = (
        results_df.sort_values("AUC_mean", ascending=False)
        .groupby("feature_set", as_index=False)
        .first()
    )

    # Map nested results for quick retrieval.
    result_lookup = {
        (r.feature_set, r.classifier): r
        for r in all_nested_results
    }

    model_best_scores: Dict[str, np.ndarray] = {}
    for _, row in model_best_rows.iterrows():
        key = (row["feature_set"], row["classifier"])
        model_best_scores[row["feature_set"]] = result_lookup[key].oof_scores

    # DeLong tests.
    delong_records = []
    fs_keys = list(model_best_scores.keys())
    key_a = find_feature_set_key(fs_keys, "Model A (periodic)")
    key_b = find_feature_set_key(fs_keys, "Model B (aperiodic)")
    key_c = find_feature_set_key(fs_keys, "Model C (combined)")

    if key_a is not None and key_b is not None:
        p_ab = delong_roc_test(
            y,
            model_best_scores[key_a],
            model_best_scores[key_b],
        )
        delong_records.append(
            {"comparison": "Model A vs Model B", "p_value": p_ab}
        )
    if key_b is not None and key_c is not None:
        p_bc = delong_roc_test(
            y,
            model_best_scores[key_b],
            model_best_scores[key_c],
        )
        delong_records.append(
            {"comparison": "Model B vs Model C", "p_value": p_bc}
        )
    delong_df = pd.DataFrame(delong_records)
    delong_path = os.path.join(
        args.output_dir, build_output_name("delong_results.csv", config_tag)
    )
    delong_df.to_csv(delong_path, index=False)

    # ROC of best classifier per model set.
    roc_path = os.path.join(
        args.output_dir, build_output_name("roc_curves_3models.png", config_tag)
    )
    plot_roc_three_models(y, model_best_scores, roc_path)

    # Best overall setting.
    best_overall_row = results_df.sort_values("AUC_mean", ascending=False).iloc[0]
    best_key = (best_overall_row["feature_set"], best_overall_row["classifier"])
    best_result = result_lookup[best_key]

    cm_path = os.path.join(
        args.output_dir, build_output_name("confusion_matrix_best_model.png", config_tag)
    )
    plot_confusion_matrix_best(
        y_true=y,
        y_pred=best_result.oof_preds.astype(int),
        title=(
            f"Confusion Matrix (Best: {best_overall_row['feature_set']} + "
            f"{best_overall_row['classifier']})"
        ),
        out_png=cm_path,
    )

    importance_df = explain_best_model(
        best_row=best_overall_row,
        X=df,
        y=y,
        model_space=model_space,
        out_dir=args.output_dir,
        shap_png_name=build_output_name("shap_summary.png", config_tag),
    )
    fi_path = os.path.join(
        args.output_dir, build_output_name("feature_importance.csv", config_tag)
    )
    importance_df.to_csv(fi_path, index=False)

    fi_png = os.path.join(
        args.output_dir, build_output_name("feature_importance_top20.png", config_tag)
    )
    plot_feature_importance(importance_df, fi_png)

    posterior_rank = importance_df.loc[
        importance_df["feature"].str.contains("posterior", case=False, regex=True),
        "rank",
    ]
    posterior_rank_text = (
        str(int(posterior_rank.iloc[0])) if not posterior_rank.empty else "Not found"
    )

    print("\n========== Done ==========")
    print(f"Input file: {input_csv_path}")
    print(f"Output directory: {args.output_dir}")
    print(f"Run tag: {config_tag}")
    print(f"N after filters: {len(df)}")
    print(f"Saved: {results_path}")
    print(f"Saved: {fi_path}")
    print(f"Saved: {roc_path}")
    print(f"Saved: {cm_path}")
    tagged_shap = os.path.join(
        args.output_dir, build_output_name("shap_summary.png", config_tag)
    )
    if os.path.exists(tagged_shap):
        print(f"Saved: {tagged_shap}")
    print(f"Saved: {fi_png}")
    print(f"Saved: {delong_path}")
    print("\nBest overall model:")
    print(
        f"- {best_overall_row['feature_set']} + {best_overall_row['classifier']} "
        f"(AUC_mean={best_overall_row['AUC_mean']:.4f})"
    )
    print(f"posterior_exponent rank in importance: {posterior_rank_text}")


if __name__ == "__main__":
    main()
