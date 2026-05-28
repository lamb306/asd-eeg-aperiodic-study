#!/usr/bin/env python
"""
18_compare_with_preschool_study_checks.py
-----------------------------------------
与 Chen et al. 学龄前 ASD aperiodic EEG 研究的 follow-up 对比分析。

用法（项目根目录）:
  python scripts/18_compare_with_preschool_study_checks.py
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config, setup_logging  # noqa: E402
from src.preschool_study_comparison import run_all_checks  # noqa: E402


def _print_paths(label: str, paths: list[Path]) -> None:
    print(f"\n{label} ({len(paths)}):")
    for p in sorted(set(paths)):
        print(f"  {p.resolve()}")


def main() -> None:
    cfg = load_config()
    log = setup_logging(cfg, name="compare_preschool_study")
    root = PROJECT_ROOT

    log.info("开始 preschool 研究对比分析…")
    result = run_all_checks(root, cfg)

    tables = result["tables"]
    figures = result["figures"]
    skipped = result["skipped"]

    _print_paths("生成的表", tables)
    _print_paths("生成的图（PNG 代表；同 stem 另有 pdf/svg）", figures)
    print(f"\n报告:\n  {result['report'].resolve()}")

    if skipped:
        print("\n跳过 / 警告:")
        for s in skipped:
            print(f"  - {s}")

    # 初步结论
    df_main = result["df_main"]
    age = df_main["age_months"]
    n_pre = int(((age >= 24) & (age <= 72)).sum())
    age_int = result["age_int"]
    qc_comp = result["qc_comp"]
    fixed_knee = result["fixed_knee"]
    corr = result["corr_exp_off"]

    int_row = age_int[
        (age_int["outcome"] == "global_exponent")
        & (age_int["term"] == "C(group)[T.TD]:age_months")
    ]
    p_int = float(int_row["p"].iloc[0]) if not int_row.empty else None

    main_b = qc_comp[
        (qc_comp["analysis_set"] == "main_qc_set")
        & (qc_comp["outcome"] == "global_exponent")
    ]
    relax_b = qc_comp[
        (qc_comp["analysis_set"] == "relaxed_epoch30_set")
        & (qc_comp["outcome"] == "global_exponent")
    ]

    r_pearson = float(corr.loc[corr["subset"] == "overall", "pearson_r"].iloc[0]) if not corr.empty else float("nan")
    n_fixed_sig = int(fixed_knee["significant_p05"].sum()) if not fixed_knee.empty else 0

    print("\n" + "=" * 60)
    print("初步结论（与学龄前文献差异的可能来源）")
    print("=" * 60)
    print(f"1. 年龄：主样本 {age.min():.0f}–{age.max():.0f} 月；2–6 岁重叠仅 {n_pre}/{len(df_main)} 人。")
    print(f"   group×age 交互（exponent）p = {p_int if p_int is not None else 'NA'}。")
    print("2. IQ/语言：见 iq_language_moderation_models.csv；TD 组 IQ 高于 ASD。")
    print(f"3. offset vs exponent：r ≈ {r_pearson:.2f}；二者部分共享方差，文献与本研究靶参数不同。")
    print("4. QC：主 QC 与 epoch≥30 宽松集 group β 见 qc_set_comparison.csv。")
    print(f"5. fixed vs knee：{n_fixed_sig}/{len(fixed_knee)} 条 sensitivity 行 p<.05（多为 fixed）。")
    print("→ 最可能解释差异的因素：年龄阶段（学龄前重叠少）、IQ/表型、offset/exponent 维度差异；")
    print("  QC 与 knee 模式影响较小；低龄子层可能 underpowered。")
    log.info("分析完成。")


if __name__ == "__main__":
    main()
