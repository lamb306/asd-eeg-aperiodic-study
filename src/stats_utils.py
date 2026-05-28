"""通用统计分析函数。"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.formula.api import mixedlm, ols
from statsmodels.robust.robust_linear_model import RLM
from statsmodels.stats.multitest import multipletests

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 描述性统计
# ---------------------------------------------------------------------------

def descriptive_table(
    df: pd.DataFrame,
    group_col: str,
    variables: list[str],
    continuous: list[str] | None = None,
    categorical: list[str] | None = None,
) -> pd.DataFrame:
    """按组生成描述性统计表。"""
    continuous = continuous or variables
    categorical = categorical or []
    rows = []
    for grp, sub in df.groupby(group_col):
        for var in continuous:
            if var not in sub.columns:
                continue
            vals = sub[var].dropna()
            rows.append({
                "group": grp,
                "variable": var,
                "type": "continuous",
                "n": len(vals),
                "mean": vals.mean(),
                "std": vals.std(),
                "median": vals.median(),
                "q25": vals.quantile(0.25),
                "q75": vals.quantile(0.75),
            })
        for var in categorical:
            if var not in sub.columns:
                continue
            counts = sub[var].value_counts()
            for level, cnt in counts.items():
                rows.append({
                    "group": grp,
                    "variable": var,
                    "type": "categorical",
                    "level": level,
                    "n": int(cnt),
                    "percent": 100 * cnt / len(sub),
                })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 组间检验
# ---------------------------------------------------------------------------

def independent_ttest(x: np.ndarray, y: np.ndarray) -> dict[str, float]:
    """独立样本 t 检验。"""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    x, y = x[~np.isnan(x)], y[~np.isnan(y)]
    if len(x) < 2 or len(y) < 2:
        return {"statistic": np.nan, "pvalue": np.nan}
    stat, p = stats.ttest_ind(x, y, equal_var=False)
    return {"statistic": float(stat), "pvalue": float(p)}


def mann_whitney(x: np.ndarray, y: np.ndarray) -> dict[str, float]:
    """Mann-Whitney U 检验。"""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    x, y = x[~np.isnan(x)], y[~np.isnan(y)]
    if len(x) < 1 or len(y) < 1:
        return {"statistic": np.nan, "pvalue": np.nan}
    stat, p = stats.mannwhitneyu(x, y, alternative="two-sided")
    return {"statistic": float(stat), "pvalue": float(p)}


def chi_square_or_fisher(
    table: np.ndarray,
) -> dict[str, Any]:
    """卡方检验；2x2 小样本时用 Fisher 精确检验。"""
    table = np.asarray(table)
    if table.shape == (2, 2) and table.sum() < 40:
        odds, p = stats.fisher_exact(table)
        return {"test": "fisher", "statistic": float(odds), "pvalue": float(p)}
    chi2, p, dof, _ = stats.chi2_contingency(table)
    return {"test": "chi2", "statistic": float(chi2), "pvalue": float(p), "dof": int(dof)}


def cohens_d(x: np.ndarray, y: np.ndarray) -> float:
    """Cohen's d（独立样本）。"""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    x, y = x[~np.isnan(x)], y[~np.isnan(y)]
    n1, n2 = len(x), len(y)
    if n1 < 2 or n2 < 2:
        return np.nan
    pooled_std = np.sqrt(((n1 - 1) * x.std(ddof=1) ** 2 + (n2 - 1) * y.std(ddof=1) ** 2) / (n1 + n2 - 2))
    if pooled_std == 0:
        return np.nan
    return float((x.mean() - y.mean()) / pooled_std)


def fdr_correction(pvalues: np.ndarray, alpha: float = 0.05, method: str = "fdr_bh") -> tuple[np.ndarray, np.ndarray]:
    """FDR 校正，返回 reject 标志与校正后 p 值。"""
    pvalues = np.asarray(pvalues, dtype=float)
    mask = ~np.isnan(pvalues)
    reject = np.full_like(pvalues, False, dtype=bool)
    p_adj = np.full_like(pvalues, np.nan)
    if mask.sum() == 0:
        return reject, p_adj
    reject_mask, p_adj_mask, *_ = multipletests(
        pvalues[mask], alpha=alpha, method=method
    )
    reject[mask] = reject_mask
    p_adj[mask] = p_adj_mask
    return reject, p_adj


# ---------------------------------------------------------------------------
# 回归
# ---------------------------------------------------------------------------

def run_ols(formula: str, data: pd.DataFrame) -> Any:
    """OLS 回归（仅按公式变量剔除缺失，不整表 dropna）。"""
    model = ols(formula, data=data).fit()
    if model.nobs < 10:
        logger.warning("OLS 样本量过小 (n=%d): %s", int(model.nobs), formula)
    return model


def run_robust_regression(formula: str, data: pd.DataFrame) -> Any:
    """稳健回归 (RLM)。"""
    model = RLM.from_formula(formula, data=data).fit()
    return model


def run_mixedlm(
    formula: str,
    data: pd.DataFrame,
    groups: str,
    re_formula: str = "1",
) -> Any:
    """
    线性混合效应模型。

    若拟合失败，自动降级为 OLS 并在日志中提示。
    """
    try:
        model = mixedlm(formula, data=data, groups=data[groups], re_formula=re_formula)
        result = model.fit(method="lbfgs", maxiter=200, reml=False)
        result._used_mixedlm = True  # type: ignore
        return result
    except Exception as exc:
        logger.warning(
            "MixedLM 不稳定，降级为 OLS: %s\n公式: %s",
            exc,
            formula,
        )
        result = run_ols(formula, data)
        result._used_mixedlm = False  # type: ignore
        return result


def spearman_correlation(x: pd.Series, y: pd.Series) -> dict[str, float]:
    """Spearman 相关。"""
    mask = x.notna() & y.notna()
    if mask.sum() < 3:
        return {"rho": np.nan, "pvalue": np.nan, "n": int(mask.sum())}
    rho, p = stats.spearmanr(x[mask], y[mask])
    return {"rho": float(rho), "pvalue": float(p), "n": int(mask.sum())}


def model_results_to_row(
    model: Any,
    model_name: str,
    outcome: str,
    predictors: list[str] | None = None,
) -> list[dict[str, Any]]:
    """将回归结果转为长表行。"""
    rows = []
    params = model.params
    pvals = model.pvalues
    conf = model.conf_int()
    predictors = predictors or list(params.index)
    for term in predictors:
        if term not in params.index:
            continue
        rows.append({
            "model": model_name,
            "outcome": outcome,
            "term": term,
            "coef": params[term],
            "std_err": model.bse[term] if term in model.bse.index else np.nan,
            "pvalue": pvals[term],
            "ci_low": conf.loc[term, 0] if term in conf.index else np.nan,
            "ci_high": conf.loc[term, 1] if term in conf.index else np.nan,
            "n_obs": int(model.nobs),
            "r_squared": getattr(model, "rsquared", np.nan),
            "used_mixedlm": getattr(model, "_used_mixedlm", None),
        })
    return rows


def compare_groups_on_variable(
    df: pd.DataFrame,
    group_col: str,
    variable: str,
    group_a: str,
    group_b: str,
) -> dict[str, Any]:
    """对连续变量做 t 检验、U 检验与 Cohen's d。"""
    a = df.loc[df[group_col] == group_a, variable]
    b = df.loc[df[group_col] == group_b, variable]
    t_res = independent_ttest(a.values, b.values)
    u_res = mann_whitney(a.values, b.values)
    d = cohens_d(a.values, b.values)
    return {
        "variable": variable,
        "group_a": group_a,
        "group_b": group_b,
        "n_a": int(a.notna().sum()),
        "n_b": int(b.notna().sum()),
        "mean_a": float(a.mean()),
        "mean_b": float(b.mean()),
        "t_stat": t_res["statistic"],
        "t_pvalue": t_res["pvalue"],
        "u_stat": u_res["statistic"],
        "u_pvalue": u_res["pvalue"],
        "cohens_d": d,
    }
