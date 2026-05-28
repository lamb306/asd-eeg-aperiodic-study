#!/usr/bin/env python
"""
22_make_consort_flowchart.py
----------------------------
从 sample_inclusion_flow.csv 绘制 CONSORT 流程图。

输出:
  outputs/figures/paper_ready_v2/supp_consort_flow.*
  outputs/figures/consort/consort_flow.*
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config, setup_logging  # noqa: E402
from src.consort_flowchart import plot_consort_flowchart  # noqa: E402


def write_caption(out_dir: Path) -> None:
    text = """# Supplementary Figure. CONSORT-style participant flow

**File:** `supp_consort_flow` (PNG/PDF/SVG)

Resting-state eyes-open EEG (EGI HydroCel-64). Preprocessing included filtering, ICA (30 components, automated artifact rejection), epoching (2 s), and average reference. Spectral parameterization (specparam, fixed aperiodic mode, 1–40 Hz) required subject-level QC (invalid channel ratio ≤ 20%). The primary analysis included **N = 138** participants (ASD = 61, TD = 77) with complete aperiodic outcomes and covariates.

---

## 补充图说明（中文）

静息态睁眼 EEG（EGI HydroCel-64）。经预处理（滤波、ICA 30 成分自动剔除、2 s 分段、平均参考）后，要求可用 epoch ≥ 60；7 人因 specparam 被试级拟合质量（无效通道比例 > 20%）排除。主分析纳入 **138** 人（ASD 61，TD 77）。

"""
    (out_dir / "supp_consort_flow_caption.md").write_text(text, encoding="utf-8")


def main() -> None:
    cfg = load_config()
    log = setup_logging(cfg, name="make_consort_flowchart")
    outputs = Path(cfg["paths"]["outputs_root"])
    flow_path = outputs / "tables" / "sample_inclusion_flow.csv"
    if not flow_path.exists():
        raise FileNotFoundError(f"Missing {flow_path}; run scripts/17 first.")

    for out_base in (
        outputs / "figures" / "paper_ready_v2" / "supp_consort_flow",
        outputs / "figures" / "consort" / "consort_flow",
    ):
        meta = plot_consort_flowchart(flow_path, out_base)
        log.info("Saved CONSORT flow → %s (final N=%d)", out_base, meta["final_n"])

    write_caption(outputs / "figures" / "paper_ready_v2")
    log.info("Caption: paper_ready_v2/supp_consort_flow_caption.md")


if __name__ == "__main__":
    main()
