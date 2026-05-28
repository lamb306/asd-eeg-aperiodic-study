#!/usr/bin/env python
"""
42_build_final_paper_stats_locked.py
------------------------------------
构建论文锁定主表（仅 ISC 族 + Delta 族）：
- ISC 族：mental / pain / neutral 组间比较，BH-FDR
- Delta 族：mental / pain 组间比较，BH-FDR

输出：
  outputs/tables/final_paper_stats_locked.csv
列：
  Analysis_Type, Cohort_N, Test_Statistic, Raw_p, FDR_p
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build final locked paper stats table with family-wise FDR.")
    parser.add_argument(
        "--project_root",
        type=str,
        default=".",
        help="项目根目录",
    )
    parser.add_argument(
        "--isc_family_csv",
        type=str,
        default="derivatives_task_movie/stats/movie_isc_family_fdr.csv",
        help="ISC family 输入（来自脚本33）",
    )
    parser.add_argument(
        "--delta_csv",
        type=str,
        default="derivatives_task_movie/stats/delta_exponent_group_ttests.csv",
        help="Delta 输入（来自脚本37）",
    )
    parser.add_argument(
        "--out_csv",
        type=str,
        default="outputs/tables/final_paper_stats_locked.csv",
        help="最终论文主表输出路径",
    )
    return parser.parse_args()


def _bh_fdr(pvals: np.ndarray) -> np.ndarray:
    pvals = np.asarray(pvals, dtype=float)
    fdr = np.full_like(pvals, np.nan, dtype=float)
    valid = np.isfinite(pvals)
    if valid.sum() > 0:
        _, p_adj, *_ = multipletests(pvals[valid], alpha=0.05, method="fdr_bh")
        fdr[valid] = p_adj
    return fdr


def main() -> None:
    args = parse_args()
    root = Path(args.project_root).resolve()
    isc_path = root / args.isc_family_csv
    delta_path = root / args.delta_csv
    out_path = root / args.out_csv

    if not isc_path.exists():
        raise FileNotFoundError(f"未找到 ISC family CSV: {isc_path}")
    if not delta_path.exists():
        raise FileNotFoundError(f"未找到 Delta CSV: {delta_path}")

    isc = pd.read_csv(isc_path)
    required_isc = {"event_type", "n_asd", "n_td", "t_stat", "raw_p"}
    if not required_isc.issubset(isc.columns):
        raise ValueError(f"ISC family CSV 缺少列: {sorted(required_isc - set(isc.columns))}")
    isc["event_type"] = isc["event_type"].astype(str).str.lower()
    target_events = ["mental", "pain", "neutral"]
    isc = isc[isc["event_type"].isin(target_events)].copy()
    if set(isc["event_type"].tolist()) != set(target_events):
        raise ValueError("ISC family 必须包含 mental / pain / neutral 三个事件。")
    isc = isc.set_index("event_type").loc[target_events].reset_index()
    isc["raw_p"] = pd.to_numeric(isc["raw_p"], errors="coerce")
    isc["fdr_p"] = _bh_fdr(isc["raw_p"].to_numpy(dtype=float))

    delta = pd.read_csv(delta_path)
    required_delta = {"metric", "n_asd", "n_td", "t_stat_welch", "p_value_welch"}
    if not required_delta.issubset(delta.columns):
        raise ValueError(f"Delta CSV 缺少列: {sorted(required_delta - set(delta.columns))}")
    target_metrics = ["Delta_Exponent_mental", "Delta_Exponent_pain"]
    delta = delta[delta["metric"].isin(target_metrics)].copy()
    if set(delta["metric"].tolist()) != set(target_metrics):
        raise ValueError("Delta family 必须包含 Delta_Exponent_mental 与 Delta_Exponent_pain。")
    delta = delta.set_index("metric").loc[target_metrics].reset_index()
    delta["p_value_welch"] = pd.to_numeric(delta["p_value_welch"], errors="coerce")
    delta["fdr_p"] = _bh_fdr(delta["p_value_welch"].to_numpy(dtype=float))

    rows: list[dict[str, str | float]] = []
    for _, r in isc.iterrows():
        rows.append(
            {
                "Analysis_Type": f"ISC_{r['event_type']}",
                "Cohort_N": f"ASD={int(r['n_asd'])},TD={int(r['n_td'])}",
                "Test_Statistic": float(r["t_stat"]),
                "Raw_p": float(r["raw_p"]),
                "FDR_p": float(r["fdr_p"]),
            }
        )
    for _, r in delta.iterrows():
        label = "mental" if str(r["metric"]).endswith("mental") else "pain"
        rows.append(
            {
                "Analysis_Type": f"Delta_{label}",
                "Cohort_N": f"ASD={int(r['n_asd'])},TD={int(r['n_td'])}",
                "Test_Statistic": float(r["t_stat_welch"]),
                "Raw_p": float(r["p_value_welch"]),
                "FDR_p": float(r["fdr_p"]),
            }
        )

    out_df = pd.DataFrame(rows, columns=["Analysis_Type", "Cohort_N", "Test_Statistic", "Raw_p", "FDR_p"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
    print(out_df)


if __name__ == "__main__":
    main()
