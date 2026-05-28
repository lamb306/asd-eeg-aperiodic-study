# ICLabel artifact-control sensitivity report

## 1. Rationale
Test whether residual ocular/myogenic artifacts influence the global aperiodic exponent group effect.

## 2. Method
- **Tool**: mne-icalabel (ICLabel), extended infomax ICA
- **Not**: HAPPE, MARA (not run unless explicitly added later)
- **Reject classes** (prob ≥ threshold): eye blink, muscle, heart, line noise, channel noise
- **Keep**: brain, other
- **Threshold tag**: `threshold_0_80`

## 3. QC summary
- Success: 138, Failed: 0
- Mean components removed: 3.41
- Mean % removed: 11.38
- Mean retained artifact prob: 0.082

## 4. Main model comparison

        outcome                 analysis  threshold  n_total  n_ASD  n_TD  coef_TD_vs_ASD       se    ci_low  ci_high        p  r_squared   ASD_mean   ASD_sd    TD_mean    TD_sd
global_exponent iclabel_artifact_control        0.7      137     60    77        0.053395 0.033999 -0.013863 0.120654 0.118714   0.041024   1.627326 0.148225   1.686524 0.161657
  global_offset iclabel_artifact_control        0.7      137     60    77        0.032244 0.039749 -0.046389 0.110877 0.418731   0.183266 -10.184879 0.185014 -10.181538 0.212675
global_exponent iclabel_artifact_control        0.8      135     58    77        0.052749 0.033234 -0.013005 0.118503 0.114914   0.037498   1.641312 0.141444   1.696540 0.159544
  global_offset iclabel_artifact_control        0.8      135     58    77        0.028777 0.039250 -0.048879 0.106434 0.464776   0.168642 -10.160821 0.175856 -10.165538 0.210415

## 5. vs Primary

              analysis         outcome  n_total  coef_TD_vs_ASD    ci_low  ci_high        p                        interpretation
iclabel_threshold_0.70 global_exponent      137        0.053395 -0.013863 0.120654 0.118714 direction consistent, weaker evidence
iclabel_threshold_0.80 global_exponent      135        0.052749 -0.013005 0.118503 0.114914 direction consistent, weaker evidence
               primary global_exponent      138        0.079082  0.017735 0.140429 0.011917                     primary reference
iclabel_threshold_0.70   global_offset      137        0.032244 -0.046389 0.110877 0.418731 direction consistent, weaker evidence
iclabel_threshold_0.80   global_offset      135        0.028777 -0.048879 0.106434 0.464776 direction consistent, weaker evidence
               primary   global_offset      138        0.059559 -0.010513 0.129631 0.095063                     primary reference

## 6. Limitations
- Sensitivity only; primary pipeline unchanged
- ICLabel training assumptions may not fully match pediatric EGI preprocessing
