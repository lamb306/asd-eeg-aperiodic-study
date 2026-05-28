"""HBN 外部验证集：路径映射、静息分段选择与 participants 表构建。"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import mne
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

RESTING_SET_SUFFIX = "_task-RestingState_eeg.set"
THEPRESENT_SET_SUFFIX = "_task-ThePresent_eeg.set"
EVENTS_SUFFIX = "_events.tsv"

CLOSE_MARKER = "instructed_toCloseEyes"
OPEN_MARKER = "instructed_toOpenEyes"
RESTING_START_MARKER = "resting_start"

# HBN 任务说明：闭眼块 40 s，睁眼块 20 s（各 5 次）
HBN_EYES_CLOSED_BLOCK_SEC = 40.0
HBN_EYES_OPEN_BLOCK_SEC = 20.0


def is_mac_resource_fork(path: Path) -> bool:
    return path.name.startswith("._") or path.name == ".DS_Store"


def resting_set_path(
    external_root: Path,
    release: str,
    subject_id: str,
) -> Path | None:
    """返回 RestingState EEGLAB .set 路径；排除 Mac 残留 ._ 文件。"""
    rel = str(release).strip()
    sid = str(subject_id).strip()
    eeg_dir = Path(external_root) / rel / f"sub-{sid}" / "eeg"
    if not eeg_dir.is_dir():
        return None
    direct = eeg_dir / f"sub-{sid}{RESTING_SET_SUFFIX}"
    if direct.exists() and not is_mac_resource_fork(direct):
        return direct
    candidates = [
        p for p in eeg_dir.glob(f"sub-*{RESTING_SET_SUFFIX}")
        if not is_mac_resource_fork(p)
    ]
    return candidates[0] if candidates else None


def thepresent_set_path(
    external_root: Path,
    release: str,
    subject_id: str,
) -> Path | None:
    """返回 ThePresent（movie 替代）.set 路径。"""
    rel = str(release).strip()
    sid = str(subject_id).strip()
    eeg_dir = Path(external_root) / rel / f"sub-{sid}" / "eeg"
    if not eeg_dir.is_dir():
        return None
    direct = eeg_dir / f"sub-{sid}{THEPRESENT_SET_SUFFIX}"
    if direct.exists() and not is_mac_resource_fork(direct):
        return direct
    candidates = [
        p for p in eeg_dir.glob(f"sub-*{THEPRESENT_SET_SUFFIX}")
        if not is_mac_resource_fork(p)
    ]
    return candidates[0] if candidates else None


def events_tsv_for_set(set_path: Path) -> Path | None:
    """BIDS 侧车 events.tsv（与 .set 同目录、同 task 前缀）。"""
    name = set_path.name
    if name.endswith("_eeg.set"):
        ev_name = name.replace("_eeg.set", EVENTS_SUFFIX)
        ev_path = set_path.parent / ev_name
        if ev_path.exists():
            return ev_path
    return None


def _sex_code_to_label(code: Any) -> str:
    """HBN sex: 0=F, 1=M（与主研究 participants 一致）。"""
    if pd.isna(code):
        return ""
    v = float(code)
    if v == 0.0:
        return "F"
    if v == 1.0:
        return "M"
    return str(code)


def load_hbn_selection_table(
    subjects_csv: Path,
    audit_csv: Path | None = None,
) -> pd.DataFrame:
    """合并 60x60 名单与下载审计表。"""
    sub = pd.read_csv(subjects_csv)
    sub["subject_id"] = sub["subject_id"].astype(str)
    if audit_csv and Path(audit_csv).exists():
        aud = pd.read_csv(audit_csv)
        aud["subject_id"] = aud["subject_id"].astype(str)
        merge_cols = [c for c in aud.columns if c != "group"]
        sub = sub.merge(aud[merge_cols], on="subject_id", how="left", suffixes=("", "_audit"))
    return sub


def build_participants_external_hbn(
    subjects_csv: Path,
    audit_csv: Path,
    external_eeg_root: Path,
    project_root: Path,
) -> pd.DataFrame:
    """
    生成外部验证 participants 表（字段对齐主流程）。

    included_final：默认仅当存在 RestingState .set 时为 1（静息预处理队列）。
    """
    df = load_hbn_selection_table(subjects_csv, audit_csv)
    external_eeg_root = Path(external_eeg_root)
    project_root = Path(project_root)

    rows: list[dict[str, Any]] = []
    for _, r in df.iterrows():
        sid = str(r["subject_id"])
        release = str(r.get("release", "")).strip()
        group = str(r.get("group_std", r.get("group", ""))).strip()
        if group not in ("ASD", "TD"):
            group = str(r.get("group", "")).strip()

        rest_path = resting_set_path(external_eeg_root, release, sid)
        movie_path = thepresent_set_path(external_eeg_root, release, sid)

        has_resting = int(rest_path is not None)
        has_movie = int(movie_path is not None)

        age_years = pd.to_numeric(r.get("age"), errors="coerce")
        age_months = age_years * 12.0 if pd.notna(age_years) else np.nan
        iq = pd.to_numeric(r.get("fsiq", r.get("IQ_total")), errors="coerce")

        def _rel(p: Path | None) -> str:
            if p is None:
                return ""
            try:
                return str(p.relative_to(project_root)).replace("\\", "/")
            except ValueError:
                return str(p).replace("\\", "/")

        rows.append({
            "subject_id": sid,
            "group": group,
            "sex": _sex_code_to_label(r.get("sex")),
            "age_months": age_months,
            "IQ_total": iq,
            "release": release,
            "raw_EEG_file_resting": _rel(rest_path),
            "raw_EEG_file_movie": _rel(movie_path),
            "raw_EEG_file": _rel(rest_path),
            "has_resting": has_resting,
            "has_movie": has_movie,
            "included_final": has_resting,
            "exclusion_reason": "" if has_resting else "missing_resting_set",
            "source_cohort": "hbn_external_60x60",
        })

    out = pd.DataFrame(rows)
    out = out.sort_values(["group", "subject_id"]).reset_index(drop=True)
    return out


def _event_onsets_from_tsv(events_path: Path, value_substr: str) -> list[float]:
    ev = pd.read_csv(events_path, sep="\t")
    if "value" not in ev.columns or "onset" not in ev.columns:
        raise ValueError(f"events.tsv 缺少 onset/value 列: {events_path}")
    mask = ev["value"].astype(str).str.contains(value_substr, case=False, na=False)
    onsets = pd.to_numeric(ev.loc[mask, "onset"], errors="coerce").dropna().tolist()
    return [float(x) for x in onsets]


def _event_onsets_from_annotations(raw: mne.io.BaseRaw, value_substr: str) -> list[float]:
    if len(raw.annotations) == 0:
        return []
    desc = np.array(raw.annotations.description, dtype=str)
    onsets = np.array(raw.annotations.onset, dtype=float)
    idx = [i for i, d in enumerate(desc) if value_substr.lower() in d.lower()]
    return [float(onsets[i]) for i in idx]


def get_resting_event_onsets(
    raw: mne.io.BaseRaw,
    set_path: Path,
    marker: str,
) -> list[float]:
    """优先 .set 内 annotations，否则读取 BIDS events.tsv。"""
    from_ann = _event_onsets_from_annotations(raw, marker)
    if from_ann:
        return sorted(from_ann)
    ev_path = events_tsv_for_set(set_path)
    if ev_path is not None:
        return sorted(_event_onsets_from_tsv(ev_path, marker))
    return []


def crop_hbn_resting_segments(
    raw: mne.io.BaseRaw,
    set_path: Path,
    mode: str,
) -> mne.io.BaseRaw:
    """
    按 HBN RestingState 事件结构裁剪/拼接静息片段。

    Parameters
    ----------
    mode : str
        - ``eyes_closed``：拼接 5 段闭眼（各约 40 s，与 BIDS events 一致）
        - ``eyes_open``：拼接 5 段睁眼（各约 20 s）
        - ``continuous``：从 ``resting_start`` 至 recording 结束（或 boundary 前）
        - ``none``：不裁剪
    """
    mode = str(mode).lower().strip()
    if mode in ("", "none", "full"):
        return raw

    sfreq = float(raw.info["sfreq"])
    total_dur = float(raw.n_times / sfreq)

    if mode == "eyes_closed":
        onsets = get_resting_event_onsets(raw, set_path, CLOSE_MARKER)
        block_sec = HBN_EYES_CLOSED_BLOCK_SEC
    elif mode == "eyes_open":
        onsets = get_resting_event_onsets(raw, set_path, OPEN_MARKER)
        block_sec = HBN_EYES_OPEN_BLOCK_SEC
    elif mode == "continuous":
        onsets = get_resting_event_onsets(raw, set_path, RESTING_START_MARKER)
        if not onsets:
            onsets = [0.0]
        tmin = float(onsets[0])
        boundary = get_resting_event_onsets(raw, set_path, "boundary")
        tmax = float(boundary[0]) if boundary else total_dur - 1.0 / sfreq
        tmax = min(tmax, total_dur - 1.0 / sfreq)
        logger.info("HBN resting continuous: tmin=%.3f, tmax=%.3f", tmin, tmax)
        return raw.copy().crop(tmin=tmin, tmax=tmax)
    else:
        raise ValueError(f"未知 hbn_resting_segment_mode: {mode}")

    if not onsets:
        raise RuntimeError(
            f"未找到 RestingState 事件 ({mode})，请检查 .set annotations 或 events.tsv: {set_path}"
        )

    segments: list[mne.io.BaseRaw] = []
    for onset in onsets:
        tmin = max(0.0, float(onset))
        tmax = min(tmin + block_sec, total_dur - 1.0 / sfreq)
        if tmax - tmin < 1.0:
            continue
        segments.append(raw.copy().crop(tmin=tmin, tmax=tmax))

    if not segments:
        raise RuntimeError(f"无法构建有效静息片段 (mode={mode}): {set_path}")

    if len(segments) == 1:
        out = segments[0]
    else:
        out = mne.concatenate_raws(segments)

    logger.info(
        "HBN resting %s: %d 段, 总时长 %.1f s",
        mode,
        len(segments),
        out.n_times / sfreq,
    )
    return out


def build_participants_external_hbn_movie(
    subjects_csv: Path,
    external_eeg_root: Path,
    project_root: Path,
) -> pd.DataFrame:
    """生成 HBN 外部验证 movie（ThePresent）预处理队列。"""
    df = pd.read_csv(subjects_csv)
    df["subject_id"] = df["subject_id"].astype(str)
    external_eeg_root = Path(external_eeg_root)
    project_root = Path(project_root)

    rows: list[dict[str, Any]] = []
    for _, r in df.iterrows():
        sid = str(r["subject_id"])
        release = str(r.get("release", "")).strip()
        group = str(r.get("group_std", r.get("group", ""))).strip()
        if group not in ("ASD", "TD"):
            group = str(r.get("group", "")).strip()

        movie_path = thepresent_set_path(external_eeg_root, release, sid)
        has_movie = int(movie_path is not None)

        age_years = pd.to_numeric(r.get("age"), errors="coerce")
        age_months = age_years * 12.0 if pd.notna(age_years) else np.nan
        iq = pd.to_numeric(r.get("fsiq", r.get("IQ_total")), errors="coerce")

        def _rel(p: Path | None) -> str:
            if p is None:
                return ""
            try:
                return str(p.relative_to(project_root)).replace("\\", "/")
            except ValueError:
                return str(p).replace("\\", "/")

        rows.append({
            "subject_id": sid,
            "group": group,
            "sex": _sex_code_to_label(r.get("sex")),
            "age_months": age_months,
            "IQ_total": iq,
            "release": release,
            "raw_EEG_file_movie": _rel(movie_path),
            "raw_EEG_file": _rel(movie_path),
            "has_movie": has_movie,
            "included_final": has_movie,
            "exclusion_reason": "" if has_movie else "missing_thepresent_set",
            "source_cohort": "hbn_external_100x2",
        })

    out = pd.DataFrame(rows)
    return out.sort_values(["group", "subject_id"]).reset_index(drop=True)


def build_attrition_report(
    participants: pd.DataFrame,
    summary: pd.DataFrame,
    failures: pd.DataFrame,
    min_epochs: int,
    *,
    cohort_label: str = "60x60",
    task_label: str = "resting",
) -> pd.DataFrame:
    """被试流失与 QC 汇总（外部 HBN 队列）。"""
    n_total = len(participants)
    n_has_resting = int(participants["has_resting"].sum()) if "has_resting" in participants.columns else np.nan
    n_has_movie = int(participants["has_movie"].sum()) if "has_movie" in participants.columns else np.nan
    n_included = int((participants["included_final"].astype(int) == 1).sum())

    rows = [
        {"stage": f"cohort_selected_{cohort_label}", "n": n_total, "note": "balanced ASD+TD selection"},
    ]
    if pd.notna(n_has_resting):
        rows.append({
            "stage": "has_resting_set_local",
            "n": int(n_has_resting),
            "note": "local RestingState .set",
        })
    if pd.notna(n_has_movie):
        rows.append({
            "stage": "has_thepresent_set_local",
            "n": int(n_has_movie),
            "note": "local ThePresent .set",
        })
    rows.append({
        "stage": f"included_final_{task_label}_preprocess",
        "n": n_included,
        "note": f"participants queued for {task_label} preprocess",
    })

    if not summary.empty:
        n_preproc_ok = len(summary)
        n_epoch_pass = int(summary["usable_epochs"].ge(min_epochs).sum()) if "usable_epochs" in summary.columns else 0
        rows.extend([
            {"stage": "preprocess_ok", "n": n_preproc_ok, "note": "status=ok in preproc_summary"},
            {
                "stage": f"usable_epochs_ge_{min_epochs}",
                "n": n_epoch_pass,
                "note": "matches main epoch QC gate",
            },
        ])

    if not failures.empty:
        rows.append({
            "stage": "preprocess_failed",
            "n": len(failures),
            "note": failures["status"].value_counts().to_dict() if "status" in failures.columns else "",
        })

    rep = pd.DataFrame(rows)
    if not summary.empty and "group" in summary.columns:
        by_grp = summary.groupby("group").size().reset_index(name="n_preproc_ok")
        rep.attrs["by_group_preproc_ok"] = by_grp
    return rep
