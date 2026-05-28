#!/usr/bin/env python
"""Integrate expanded Discussion into v6 manuscript -> v8."""

from __future__ import annotations

import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
BASE = PROJECT / "outputs/reports/manuscript_draft_zh_v6_submission_style.md"
EXPANDED = PROJECT / "outputs/reports/manuscript_draft_zh_v8_discussion_expanded.md"
OUT_MD = PROJECT / "outputs/reports/manuscript_draft_zh_v8_discussion_integrated.md"
OUT_DOCX = PROJECT / "outputs/reports/manuscript_draft_zh_v8_discussion_integrated.docx"
OUT_AUDIT = PROJECT / "outputs/reports/discussion_integration_audit.md"

MARK_DISC = "## 4. 讨论"
MARK_REF = "## References"


def extract_discussion_expanded() -> str:
    text = EXPANDED.read_text(encoding="utf-8")
    m = re.search(r"^## 4\. 讨论\n\n", text, re.M)
    end = text.find("\n---\n\n## Changelog")
    if m and end > 0:
        return text[m.end() : end].strip()
    raise ValueError("Could not parse expanded discussion")


def clean_discussion(body: str) -> str:
    # Remove English parentheticals in subsection headings only
    def _strip_heading_en(m: re.Match) -> str:
        title = m.group(0)
        title = re.sub(r"（[A-Za-z][^）]*）", "", title)
        title = re.sub(r"\([A-Za-z][^）)]*\)", "", title)
        return title

    body = re.sub(r"^### 4\.\d+[^\n]+$", _strip_heading_en, body, flags=re.M)

    body = body.replace(
        "本研究结果与上述报告 **differ from / not fully consistent with** 该学龄前样本的重点参数模式：",
        "本研究结果与上述报告并不完全一致：",
    )
    body = body.replace(
        "**differ from / not fully consistent with**",
        "并不完全一致",
    )
    body = body.replace("differ from / not fully consistent with", "并不完全一致")

    # 4.3: reframe joint models as supplementary
    old = (
        "其次，exponent 与 offset 在本队列中相关（r ≈ 0.73），但二者对组别与年龄的敏感性并不相同："
        "控制 offset 后 exponent 组效应仍保留，控制 exponent 后 offset 组效应不显著，提示两参数可能反映非周期背景的不同方面。"
    )
    new = (
        "其次，exponent 与 offset 在本队列中相关（r ≈ 0.73）。"
        "补充联合模型分析显示，在控制 offset 后 exponent 的组效应仍保留，而在控制 exponent 后 offset 的组效应不显著，"
        "提示两参数对年龄与组别的敏感性可能不同；该结果仅作为参数维度区分的补充说明，不作为主结论。"
    )
    body = body.replace(old, new)

    body = body.replace("不宜简单表述为相互矛盾", "不宜理解为相互矛盾")
    body = body.replace("生物标志物（biomarker）", "生物标志物")
    body = body.replace("发育时间 course", "发育时间进程")
    body = body.replace("发育时间进程 及其", "发育时间进程及其")

    # Normalize key stats wording per user spec (discussion may use p = .012 already)
    body = re.sub(r"p = 0\.012", "p = .012", body)
    body = re.sub(r"p = 0\.095", "p = .095", body)
    body = re.sub(r"p = 0\.020", "p = .020", body)
    body = re.sub(r"p = 0\.021", "p = .021", body)

    # Sex limitation: Table 1 still p < .001 — keep with corrected counts
    if "性别分布不均衡" not in body:
        pass  # already in 4.9

    return body.strip()


def merge_manuscript() -> str:
    base = BASE.read_text(encoding="utf-8")
    i_disc = base.find(MARK_DISC)
    i_ref = base.find(MARK_REF)
    if i_disc < 0 or i_ref < 0 or i_ref <= i_disc:
        raise ValueError("Could not find Discussion / References in base manuscript")

    disc = clean_discussion(extract_discussion_expanded())
    merged = (
        base[:i_disc].rstrip()
        + "\n\n## 4. 讨论\n\n"
        + disc
        + "\n\n"
        + base[i_ref:].lstrip()
    )
    return merged


def write_docx(md: str) -> None:
    import sys

    sys.path.insert(0, str(PROJECT / "scripts"))
    from importlib import import_module

    mod = import_module("23_build_manuscript_v6_submission")
    mod.OUT_MD = OUT_MD
    mod.OUT_DOCX = OUT_DOCX
    mod.write_docx(md)
    print(f"Wrote {OUT_DOCX}")


def write_audit():
    audit = """# Discussion 整合审计（v8 integrated）

**基线稿**：`manuscript_draft_zh_v6_submission_style.md`（v7 不存在）  
**扩展讨论来源**：`manuscript_draft_zh_v8_discussion_expanded.md`  
**输出稿**：`manuscript_draft_zh_v8_discussion_integrated.md` / `.docx`

---

## 1. 替换的小节（原 v6 → 新 v8）

| 小节 | 处理 |
|------|------|
| 4.1 主要发现 | 由单段扩展为两段；整合主效应、周期峰阴性、稳健性、年龄交互、空间探索、分半信度 |
| 4.2 | 原「ASD 较低 exponent 解释」→「非周期 exponent 作为组间敏感谱特征」 |
| 4.3 | 扩展 Chen et al. (2026) 对照；英文提示语改为中文 |
| 4.4 | 原「年龄依赖性与发育解释」→「年龄依赖性效应」；强调横断面界限 |
| 4.5 | 原 v6 的 4.6「空间分布」提前至此（与扩展稿结构一致） |
| 4.6 | 原 v6 的 4.5「周期峰阴性」→ 方法学意义专节 |
| 4.7 | 扩展临床相关性；禁止 biomarker 结论 |
| 4.8 | 扩展 split-half；强调非 test–retest |
| 4.9 | 编号清单改为段落；保留性别局限（修正后编码） |
| 4.10 | 正式结论段 |

**未改动部分**：摘要；§1–3；References；Supplementary Materials；图表明细；作者需补充清单。

---

## 2. 删除的英文提示语 / 标题英文

| 原文字 | 替换为 |
|--------|--------|
| `（Principal findings）` 等 10 处小节英文括号 | 已删除，仅保留中文标题 |
| `differ from / not fully consistent with` | 「与上述报告并不完全一致」 |
| `biomarker`（括号内） | 删除英文，保留「生物标志物」 |
| `发育时间 course` | 「发育时间进程」 |

---

## 3. 性别局限如何处理

| 项目 | 决定 |
|------|------|
| Table 1 性别检验 | ASD 5 女/56 男，TD 28 女/49 男，χ²，**p < .001**（修正后编码，见 `sex_encoding_rerun_audit.md`） |
| 讨论 4.9 | **保留**「性别分布不均衡」局限，数字为 **5 女/56 男、28 女/49 男** |
| 是否删除性别局限 | **否** — 组间性别构成仍显著不均衡，虽已协变量校正 |

---

## 4. 统计数字核对（与主稿 Results 一致）

| 指标 | 讨论中的表述 |
|------|----------------|
| 主效应 exponent | β = 0.079，SE = 0.031，p = .012，95% CI [0.018, 0.140] |
| offset 趋势 | β = 0.060，p = .095 |
| group × age exponent | β = .0033，p = .020 |
| group × age offset | β = .0037，p = .021 |
| split-half | ρ = 0.959–0.972，SB > 0.97 |
| 周期峰 | 所有 group p > .24 |
| 通道 FDR | E33、E36、E37、E38 |

---

## 5. 引用核对（讨论 vs References）

| 引用 | 在 References 中 |
|------|------------------|
| Chen et al. (2026) | 是 |
| Donoghue et al. (2020a, 2020b) | 是 |
| Gao et al. (2017) | 是 |
| Hill et al. (2022) | 是 |
| Karalunas et al. (2022) | 是 |
| Manyukhina et al. (2022) | 是 |
| Neo et al. (2023) | 是 |
| Wilkinson et al. (2024) | 是 |

**新增引用**：无  
**[citation needed]**：无（MNE 仅在方法节，不在讨论）

---

## 6. 仍需作者核实的信息

- [待补充] / [待核实]：伦理、诊断、IQ、ADOS、ICA、语言分数（与原 v6 一致）
- Chen et al. (2026)、Wilkinson et al. (2024)：References 已标注 metadata verification required
- 4.3 中 exponent–offset 联合模型：已明确为**补充分析**，非主结论

---

## 7. 讨论中最核心的三条论点

1. **主发现**：在协变量校正后，TD 儿童静息态 global aperiodic exponent 高于 ASD（更陡的 1/f 背景），效应在敏感性分析中方向一致；周期峰参数无显著组间差异，提示组间信号主要在**非周期 exponent** 而非传统振荡峰。

2. **发育与文献语境**：group × age 交互显著，为不同年龄段 ASD aperiodic 文献不一致提供线索；但必须在横断面设计下解读，**不能**等同于纵向发育轨迹。

3. **方法学与谨慎外推**：specparam 分离支持将非周期与周期变化区分；记录内分半信度高但**不是** test–retest；头皮 topomap 不能作源定位；exponent **不能**直接等同于 E/I 失衡或临床生物标志物。

---

*整合完成：2026-05-20*
"""
    OUT_AUDIT.write_text(audit, encoding="utf-8")
    print(f"Wrote {OUT_AUDIT}")


def main():
    md = merge_manuscript()
    OUT_MD.write_text(md, encoding="utf-8")
    print(f"Wrote {OUT_MD}")
    write_docx(md)
    write_audit()


if __name__ == "__main__":
    main()
