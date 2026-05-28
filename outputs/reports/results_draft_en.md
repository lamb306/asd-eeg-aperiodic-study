# Results (Formal Draft · English)

Eyes-open resting-state EEG (EGI HydroCel-64) was decomposed with specparam (fixed aperiodic mode, 1–40 Hz). **Primary analysis:** *N* = 138 (ASD *n* = 61, TD *n* = 77). The coefficient `C(group)[T.TD]` denotes the TD–ASD contrast (ASD = reference).

---

## 3.1 Sample Inclusion and Data Quality

One hundred sixty-eight participants had analyzable resting-state EEG and metadata (ASD 80, TD 88). After preprocessing, 145 met the minimum usable-epoch criterion (≥ 60 two-second epochs); seven additional participants were excluded for poor subject-level specparam fit quality. The primary analysis included **138 complete cases** (ASD **61**, TD **77**) (`outputs/tables/sample_inclusion_flow.csv`).

Groups did not differ in age (Table 1). Full-sample IQ was higher in TD than ASD (~113 vs 93, *p* < .001); IQ was adjusted in all primary models. Group-mean PSDs are shown in Figure 1 (`fig01_group_mean_psd.png`). Visual inspection of representative specparam fits (`outputs/figures/qc_specparam_review/`) indicated generally acceptable model fits within 1–40 Hz.

---

## 3.2 Group Difference in Global Aperiodic Exponent

After adjusting for age, sex, full-scale IQ, and usable epoch count, TD children showed a significantly **higher global aperiodic exponent** than ASD children (β = **0.079**, SE = 0.031, **p = .012**, 95% CI [0.018, 0.140], *n* = 138).

Uncorrected descriptives: ASD *M* = 1.69 (*SD* = 0.14), TD *M* = 1.79 (*SD* = 0.14). **A higher exponent indicates a steeper power-law slope (faster relative decline of high-frequency vs low-frequency power).** Lower exponent values in ASD are consistent with a **flatter** 1/*f* background.

**Global aperiodic offset** showed a TD > ASD trend (β = 0.060, *p* = .095). See Figure 2 (`fig03_global_exponent.png`).

---

## 3.3 Robustness and Sensitivity Analyses

### Covariate models

The group effect was positive (TD > ASD) in every specification (`global_exponent_robustness_models.csv`):

| Model | β (TD vs ASD) | *p* |
|-------|---------------|-----|
| Group only | 0.096 | < .001 |
| + Age, sex | 0.090 | < .001 |
| + IQ | 0.080 | .011 |
| **Primary (+ usable epochs)** | **0.079** | **.012** |
| + Mean fit *R*² | 0.056 | .030 |
| + Bad-channel count | 0.081 | .011 |

No participant had IQ < 70; the low-IQ exclusion model matched the primary model.

### Frequency range and aperiodic mode

Under the **fixed** mode, group effects were consistent across 1–40, 2–40, 1–35, and 2–35 Hz (*p* = .016–.031; `sensitivity_analysis_final.csv`). Under the **knee** mode, directions were the same but statistical evidence was weaker (*p* ≈ .08–.16); knee-mode results are reported supplementarily. Epoch thresholds of 30 vs 60 yielded similar estimates (β ≈ 0.074, *p* ≈ .019).

---

## 3.4 Spatial Distribution (Exploratory)

### Preliminary HydroCel-64 ROI grouping

In a mixed model across five preliminary ROIs (frontal, central, temporal, parietal, occipital; `config/roi_channels.yaml`), the **group main effect was not significant** (*p* = .44), but the **group × ROI interaction was significant** (`roi_mixed_model.csv`; `fig05_roi_exponent.png`). Relative to central ROI, contrasts were larger for frontal, temporal, parietal, and occipital ROIs (interaction *p* ≈ .001–.02). ROI definitions were based on spatial channel groupings only; **no specific cortical sources are inferred**.

### Channel level

After FDR correction across 64 channels, **E33, E36, E37, and E38** remained significant (FDR *p* < .05), all TD > ASD (`significant_channels_fdr.csv`; `fig07_channel_exponent_topomap.png`). On the HydroCel-64 sensor layout, these sites correspond to the **parieto-occipital transition** and midline **Oz (E37)** neighborhood (consistent with posterior Pe sites such as 33, 36, and 38 in ERP montage diagrams); our ROI configuration also assigns E33 and E36–E38 to the occipital grouping. Effects are therefore described as **parieto-occipital HydroCel-64 channels**, **without inferring specific cortical sources**.

---

## 3.5 Periodic Peak Parameters

After covariate adjustment, group effects on alpha peak center frequency, power, and bandwidth, and on theta and beta peak power, were **not significant** (all group *p* > .24; `periodic_peak_analysis.csv`). Periodic peak measures did not show significant group differences; **observed group effects were therefore primarily carried by the aperiodic exponent** after specparam decomposition.

---

## 3.6 Clinical Associations (Exploratory; ASD Only)

Clinical models included only ASD participants who passed the same EEG and subject-level specparam QC as the primary analysis (*n* = **61**). ADOS subscores were mapped from Resting_info as follows: **ADOS-2** → total score; **Social** → `ADOS_SA`; **Communication** → `ADOS_communication` (**not** the standard ADOS RRB domain; see `clinical_model_n_and_variable_check.csv`).

Global exponent was not significantly associated with ADOS total (*p* = .188) or Communication (*p* = .257). The association with Social (`ADOS_SA`) was negative in direction but did not reach significance (OLS *p* = .057). Temporal ROI exponent was not significantly associated with language score (*n* = 55, *p* = .319).

**All clinical associations are reported as exploratory and did not meet conventional significance thresholds.**

---

## Figure and Table Index

| Item | File |
|------|------|
| Inclusion flow | `sample_inclusion_flow.csv` |
| Primary + robustness | `global_exponent_robustness_models.csv` |
| Clinical variable check | `clinical_model_n_and_variable_check.csv` |
| Fig 1 PSD | `fig01_group_mean_psd.png` |
| Fig 2 Exponent | `fig03_global_exponent.png` |
| Fig 3 ROI | `fig05_roi_exponent.png` |
| Fig 4 Channels | `fig07_channel_exponent_topomap.png` |
