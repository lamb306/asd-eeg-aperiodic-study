#!/usr/bin/env python
"""
根据 Resting_info.xlsx 与 data/raw 下实际 .mff 数据同步 participants.csv。

规则:
- 纳入 participants.csv: Resting_info 与 data/raw 均有的被试 (included_final=1)
- 不纳入: Resting_info 有记录但 EEG 已删除 → participants_excluded_no_eeg_data.csv
- 统计: 有 EEG 但 Resting_info 无记录 → participants_data_without_info.csv

支持:
- 多个 Excel 工作表（如 TD / ASD 分 sheet）
- ID 以 S 开头 → ASD，T 开头 → TD
- 可选列 ADOS_total / ADOS_SA / ADOS_RRB 等（若表中存在则自动映射）
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

RESTING_INFO = PROJECT_ROOT / "data" / "participants" / "Resting_info.xlsx"
RAW_ROOT = PROJECT_ROOT / "data" / "raw"
OUT_CSV = PROJECT_ROOT / "data" / "participants" / "participants.csv"

COLUMNS = [
    "subject_id", "group", "age_months", "sex", "IQ_total", "IQ_verbal", "IQ_nonverbal",
    "ADOS_total", "ADOS_SA", "ADOS_communication", "ADOS_RRB", "SRS_total", "CARS_total", "ABC_total",
    "language_score", "medication_status", "raw_EEG_file", "EEG_usable_seconds",
    "EEG_usable_epochs", "included_final", "exclusion_reason",
]

# Resting_info 列名 → participants 列名（存在则映射）
# ASD 表常见三列: ADOS-2（总分）, Communication（沟通）, Social（社交）
# 注意: Communication ≠ ADOS 标准 RRB 域；单独存入 ADOS_communication
OPTIONAL_COLUMN_MAP = {
    "ADOS": "ADOS_total",
    "ADOS_total": "ADOS_total",
    "ADOS-2": "ADOS_total",
    "ADOS_SA": "ADOS_SA",
    "ADOS_RRB": "ADOS_RRB",
    "ADOS-SA": "ADOS_SA",
    "ADOS-RRB": "ADOS_RRB",
    "Social": "ADOS_SA",
    "Communication": "ADOS_communication",
    "CARS": "CARS_total",
    "CARS_total": "CARS_total",
    "ABC": "ABC_total",
    "ABC_total": "ABC_total",
    "IQ_verbal": "IQ_verbal",
    "VIQ": "IQ_verbal",
    "IQ_nonverbal": "IQ_nonverbal",
    "PIQ": "IQ_nonverbal",
    "NVIQ": "IQ_nonverbal",
}

# ASD 区块在 Sheet1 中从该表头行开始（0-based，与 Excel 第 104 行对应）
ASD_HEADER_ROW = 103


def _sex_code(val) -> str:
    """Resting_info: 0/1 → M/F（0=男，1=女）。"""
    if pd.isna(val):
        return ""
    try:
        v = int(float(val))
    except (TypeError, ValueError):
        s = str(val).strip().upper()
        if s in ("M", "MALE", "男", "0"):
            return "M"
        if s in ("F", "FEMALE", "女", "1"):
            return "F"
        return s[:1] if s else ""
    return "F" if v == 1 else "M"


def infer_group(subject_id: str, data_map: dict | None = None) -> str:
    """由 ID 前缀或 data 目录推断组别。"""
    sid = str(subject_id).strip().upper()
    if sid.startswith("S"):
        return "ASD"
    if sid.startswith("T"):
        return "TD"
    if data_map and sid in data_map:
        return data_map[sid]["group"]
    return ""


def scan_mff_files() -> dict[str, dict]:
    """扫描 ASD/TD 目录，返回 {subject_id: {group, path}}。"""
    mapping: dict[str, dict] = {}
    for group, folder in (("ASD", "ASD"), ("TD", "TD")):
        root = RAW_ROOT / folder
        if not root.exists():
            continue
        for p in sorted(root.iterdir()):
            if not p.is_dir() or not p.name.lower().endswith(".mff"):
                continue
            m = re.match(r"^([ST]\d+)", p.name, re.I)
            if not m:
                continue
            sid = m.group(1).upper()
            rel = p.relative_to(PROJECT_ROOT).as_posix()
            mapping[sid] = {"group": group, "raw_EEG_file": rel, "mff_name": p.name}
    return mapping


def _clean_numeric(val):
    """将 /、空字符串等转为可空数值。"""
    if pd.isna(val):
        return ""
    if isinstance(val, str) and val.strip() in ("/", "", "-", "nan"):
        return ""
    try:
        return float(val)
    except (TypeError, ValueError):
        return ""


def _normalize_block(df: pd.DataFrame, group: str) -> pd.DataFrame:
    """统一 TD / ASD 区块为 subject_id + 标准列。"""
    if "ID" not in df.columns:
        raise ValueError(f"{group} 区块缺少 ID 列: {list(df.columns)}")

    out = df.copy()
    out["subject_id"] = out["ID"].astype(str).str.strip().str.upper()
    out = out[out["subject_id"].str.match(r"^[ST]\d+$", na=False)]
    out["_force_group"] = group
    out["_n_valid"] = out.notna().sum(axis=1)
    out = out.sort_values("_n_valid", ascending=False)
    out = out.drop_duplicates(subset=["subject_id"], keep="first")
    return out.drop(columns=["_n_valid"], errors="ignore")


def load_resting_info() -> pd.DataFrame:
    """
    读取 Resting_info.xlsx。

    当前文件结构（Sheet1）:
    - 第 1–101 行: TD（T001–T100），表头在第 1 行
    - 第 104 行起: ASD（S001…），表头在第 104 行（index=103）
 若将来改为分 sheet，则自动合并各 sheet 中 S/T 开头 ID。
    """
    if not RESTING_INFO.exists():
        raise FileNotFoundError(f"未找到 {RESTING_INFO}")

    parts: list[pd.DataFrame] = []

    # TD 区块
    td = pd.read_excel(RESTING_INFO, sheet_name=0, header=0)
    td = _normalize_block(td[td["ID"].astype(str).str.match(r"^T\d+", na=False)], "TD")
    parts.append(td)

    # ASD 区块（同一 sheet 下半部分）
    try:
        asd = pd.read_excel(RESTING_INFO, sheet_name=0, header=ASD_HEADER_ROW)
        asd = _normalize_block(asd[asd["ID"].astype(str).str.match(r"^S\d+", na=False)], "ASD")
        parts.append(asd)
    except Exception:
        pass

    # 额外工作表（若用户将 ASD 单独成 sheet）
    sheets = pd.ExcelFile(RESTING_INFO).sheet_names
    for sheet in sheets[1:]:
        df = pd.read_excel(RESTING_INFO, sheet_name=sheet)
        if "ID" not in df.columns:
            continue
        s_mask = df["ID"].astype(str).str.match(r"^S\d+", na=False)
        t_mask = df["ID"].astype(str).str.match(r"^T\d+", na=False)
        if s_mask.any():
            parts.append(_normalize_block(df[s_mask], "ASD"))
        if t_mask.any():
            parts.append(_normalize_block(df[t_mask], "TD"))

    if not parts:
        raise ValueError(f"{RESTING_INFO} 无有效 TD/ASD 记录")

    combined = pd.concat(parts, ignore_index=True)
    combined = combined.drop_duplicates(subset=["subject_id"], keep="first")
    return combined


def _row_from_info(row_info: pd.Series, sid: str, data_map: dict) -> dict:
    """将 Resting_info 一行转为 participants 记录。"""
    group = row_info.get("_force_group") or infer_group(sid, data_map)
    if not group:
        group = data_map[sid]["group"]

    age = _clean_numeric(row_info.get("Age_mo", row_info.get("age_months")))
    iq = _clean_numeric(row_info.get("FSIQ", row_info.get("IQ_total")))
    srs = _clean_numeric(row_info.get("SRS", row_info.get("SRS_total")))
    tomi = _clean_numeric(row_info.get("ToMI_Total", row_info.get("language_score")))

    out = {
        "subject_id": sid,
        "group": group,
        "age_months": age,
        "sex": _sex_code(row_info.get("Sex", row_info.get("sex"))),
        "IQ_total": iq,
        "IQ_verbal": "",
        "IQ_nonverbal": "",
        "ADOS_total": "",
        "ADOS_SA": "",
        "ADOS_communication": "",
        "ADOS_RRB": "",
        "SRS_total": srs,
        "CARS_total": "",
        "ABC_total": "",
        "language_score": tomi,
        "medication_status": "",
        "raw_EEG_file": data_map[sid]["raw_EEG_file"],
        "EEG_usable_seconds": "",
        "EEG_usable_epochs": "",
        "included_final": 1,
        "exclusion_reason": "",
    }

    for src_col, dst_col in OPTIONAL_COLUMN_MAP.items():
        if src_col in row_info.index and pd.notna(row_info.get(src_col)):
            val = _clean_numeric(row_info[src_col])
            if val != "":
                out[dst_col] = val

    return out


def build_participants() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, str]:
    info = load_resting_info()
    data_map = scan_mff_files()

    info_ids = set(info["subject_id"])
    data_ids = set(data_map.keys())

    in_both = sorted(info_ids & data_ids)
    info_only = sorted(info_ids - data_ids)
    data_only = sorted(data_ids - info_ids)

    rows = [_row_from_info(info.loc[info["subject_id"] == sid].iloc[0], sid, data_map) for sid in in_both]
    participants = pd.DataFrame(rows, columns=COLUMNS)

    # info 有、data 无
    excluded_rows = []
    for sid in info_only:
        row_info = info.loc[info["subject_id"] == sid].iloc[0]
        excluded_rows.append({
            "subject_id": sid,
            "group": row_info.get("_force_group") or infer_group(sid),
            "in_Resting_info": 1,
            "has_eeg_data": 0,
            "exclusion_reason": "Resting_info中有记录但data/raw中无EEG文件",
            "Age_mo": row_info.get("Age_mo"),
            "Sex": row_info.get("Sex"),
            "FSIQ": row_info.get("FSIQ"),
            "SRS": row_info.get("SRS"),
        })
    excluded_out = pd.DataFrame(excluded_rows)

    # data 有、info 无
    no_info = pd.DataFrame([
        {
            "subject_id": sid,
            "group": data_map[sid]["group"],
            "raw_EEG_file": data_map[sid]["raw_EEG_file"],
            "in_Resting_info": 0,
            "has_eeg_data": 1,
            "note": "有EEG数据但Resting_info.xlsx中无记录",
        }
        for sid in data_only
    ])

    n_asd_info = sum(1 for s in info_ids if infer_group(s) == "ASD")
    n_td_info = sum(1 for s in info_ids if infer_group(s) == "TD")
    n_asd_both = sum(1 for s in in_both if infer_group(s) == "ASD")
    n_td_both = sum(1 for s in in_both if infer_group(s) == "TD")

    report_lines = [
        "participants 同步报告",
        "=" * 50,
        f"Resting_info.xlsx 被试数（去重）: {len(info_ids)}  (ASD: {n_asd_info}, TD: {n_td_info})",
        f"data/raw 中 .mff 被试数: {len(data_ids)}",
        f"  - ASD: {sum(1 for s in data_ids if data_map[s]['group'] == 'ASD')}",
        f"  - TD:  {sum(1 for s in data_ids if data_map[s]['group'] == 'TD')}",
        "",
        f"纳入 participants.csv: {len(participants)} (included_final=1)",
        f"  - ASD（info+data）: {n_asd_both}",
        f"  - TD（info+data）: {n_td_both}",
        "",
        f"不可用 — info有、data无 ({len(info_only)}): {', '.join(info_only) or '无'}",
        f"不可用 — data有、info无 ({len(data_only)}): {len(data_only)} 名",
    ]
    if data_only:
        asd_only = [s for s in data_only if data_map[s]["group"] == "ASD"]
        td_only = [s for s in data_only if data_map[s]["group"] == "TD"]
        if asd_only:
            report_lines.append(
                f"  ASD ({len(asd_only)}): {', '.join(asd_only[:15])}{'...' if len(asd_only) > 15 else ''}"
            )
        if td_only:
            report_lines.append(f"  TD ({len(td_only)}): {', '.join(td_only)}")

    return participants, excluded_out, no_info, "\n".join(report_lines)


def main() -> None:
    participants, excluded, no_info, report = build_participants()

    out_dir = OUT_CSV.parent
    try:
        participants.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
        out_path = OUT_CSV
    except PermissionError:
        out_path = out_dir / "participants_new.csv"
        participants.to_csv(out_path, index=False, encoding="utf-8-sig")
        report += f"\n\n注意: {OUT_CSV.name} 被占用，已写入 {out_path.name}"

    excluded.to_csv(out_dir / "participants_excluded_no_eeg_data.csv", index=False, encoding="utf-8-sig")
    no_info.to_csv(out_dir / "participants_data_without_info.csv", index=False, encoding="utf-8-sig")
    (out_dir / "participants_sync_report.txt").write_text(report, encoding="utf-8")

    print(report)
    print(f"\n已写入: {out_path}")


if __name__ == "__main__":
    main()
