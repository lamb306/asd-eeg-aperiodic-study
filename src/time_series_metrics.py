"""时间序列波动率指标：方差、多尺度熵等。"""

from __future__ import annotations

import numpy as np


def coarse_grain(x: np.ndarray, scale: int) -> np.ndarray:
    """非重叠粗粒化（Costa et al. 多尺度熵）。"""
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    n = len(x)
    if scale < 1 or n < scale:
        return np.array([], dtype=float)
    n_use = (n // scale) * scale
    return x[:n_use].reshape(-1, scale).mean(axis=1)


def sample_entropy(x: np.ndarray, m: int = 2, r: float | None = None) -> float:
    """Sample entropy（SampEn），m=2 为常用默认。"""
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    n = len(x)
    if n < m + 2:
        return np.nan
    sd = float(np.std(x, ddof=1))
    if r is None:
        r = 0.2 * sd
    if not np.isfinite(r) or r <= 0:
        return np.nan

    def _phi(mm: int) -> float:
        count = 0
        for i in range(n - mm):
            template = x[i : i + mm]
            for j in range(i + 1, n - mm + 1):
                if np.max(np.abs(template - x[j : j + mm])) <= r:
                    count += 1
        return float(count)

    b = _phi(m)
    a = _phi(m + 1)
    if a == 0 or b == 0:
        return np.nan
    return float(-np.log(a / b))


def multiscale_entropy(
    x: np.ndarray,
    scales: tuple[int, ...] = (1, 2, 3, 4, 5),
    m: int = 2,
) -> tuple[float, dict[int, float]]:
    """返回 (各尺度 SampEn 的均值, 分尺度字典)。"""
    per_scale: dict[int, float] = {}
    for s in scales:
        cg = coarse_grain(x, s)
        per_scale[s] = sample_entropy(cg, m=m) if len(cg) >= m + 2 else np.nan
    vals = [v for v in per_scale.values() if np.isfinite(v)]
    return (float(np.mean(vals)) if vals else np.nan), per_scale


def exponent_variability_metrics(
    series: np.ndarray,
    mse_scales: tuple[int, ...] = (1, 2, 3, 4, 5),
) -> dict[str, float]:
    """从 exponent 时间序列计算核心波动率指标。"""
    x = np.asarray(series, dtype=float)
    x = x[np.isfinite(x)]
    out: dict[str, float] = {
        "n_windows": float(len(x)),
        "exponent_mean_ts": np.nan,
        "exponent_var": np.nan,
        "exponent_std": np.nan,
        "exponent_cv": np.nan,
        "exponent_range": np.nan,
        "exponent_mse_mean": np.nan,
        "exponent_sampen_scale1": np.nan,
    }
    if len(x) < 3:
        return out

    mu = float(np.mean(x))
    var = float(np.var(x, ddof=1)) if len(x) > 1 else np.nan
    std = float(np.std(x, ddof=1)) if len(x) > 1 else np.nan
    mse_mean, mse_dict = multiscale_entropy(x, scales=mse_scales)

    out["exponent_mean_ts"] = mu
    out["exponent_var"] = var
    out["exponent_std"] = std
    out["exponent_cv"] = float(std / mu) if mu != 0 and np.isfinite(mu) else np.nan
    out["exponent_range"] = float(np.max(x) - np.min(x))
    out["exponent_mse_mean"] = mse_mean
    out["exponent_sampen_scale1"] = mse_dict.get(1, np.nan)
    return out
