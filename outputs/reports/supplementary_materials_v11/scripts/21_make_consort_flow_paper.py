#!/usr/bin/env python
"""
21_make_consort_flow_paper.py
-----------------------------
论文版 CONSORT 样本纳入流程图 → supp_consort_flow_paper.{png,pdf,svg}

用法（项目根目录）:
    python scripts/21_make_consort_flow_paper.py
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config, setup_logging  # noqa: E402
from src.consort_flowchart_paper import load_flow_data, plot_consort_flow_paper  # noqa: E402

CAPTION = """# Supplementary figure caption — CONSORT flow

## English (for manuscript)

**Supplementary Figure X.** CONSORT-style flow diagram for the resting-state EEG aperiodic analysis. Of 168 participants with available and preprocessed resting-state EEG data, 145 met the usable epoch criterion of at least 60 two-second epochs. Seven additional participants were excluded because more than 20% of channels failed specparam quality control, resulting in a primary analysis cohort of 138 participants (61 ASD, 77 TD).

## 中文（补充材料说明）

**补充图 X.** 静息态 EEG 非周期（specparam）分析的 CONSORT 式纳入流程。168 名被试具备可用且完成预处理的静息态 EEG；145 名达到至少 60 个 2 秒可用分段标准；另有 7 人因超过 20% 通道未通过 specparam 质量控制而排除，最终主分析纳入 138 人（ASD 61，TD 77）。

**文件:** `supp_consort_flow_paper.png` / `.pdf` / `.svg`
"""


def main() -> None:
    cfg = load_config()
    log = setup_logging(cfg, name="make_consort_flow_paper")
    outputs = Path(cfg["paths"]["outputs_root"])
    flow_csv = outputs / "tables" / "sample_inclusion_flow.csv"
    out_dir = outputs / "figures" / "paper_ready_v2"
    out_base = out_dir / "supp_consort_flow_paper"

    data = load_flow_data(flow_csv if flow_csv.exists() else None)
    if flow_csv.exists():
        log.info("Loaded inclusion counts from %s", flow_csv)
    else:
        log.warning("Using built-in default counts (%s not found)", flow_csv)

    paths = plot_consort_flow_paper(data, out_base)
    for p in paths:
        print(p.resolve())

    caption_path = out_dir / "supp_consort_flow_caption.md"
    caption_path.write_text(CAPTION, encoding="utf-8")
    print(caption_path.resolve())
    log.info("Wrote caption → %s", caption_path)


if __name__ == "__main__":
    main()
