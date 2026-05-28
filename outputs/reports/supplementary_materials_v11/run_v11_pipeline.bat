@echo off
REM 从项目根目录运行 v11 论文对应分析（课程作业 / 复现用）
REM 用法: 在 asd_eeg_aperiodic_study 根目录执行:
REM   outputs\reports\supplementary_materials_v11\run_v11_pipeline.bat

setlocal
cd /d "%~dp0\..\..\.."
if not exist "scripts\00_check_environment.py" (
    echo [ERROR] 未找到项目根目录 scripts\00_check_environment.py
    echo 请在本 bat 所在仓库根目录下运行。
    exit /b 1
)

echo Project root: %CD%
echo.

python scripts\00_check_environment.py
if errorlevel 1 exit /b 1

REM --- 阶段 A: 预处理（数据量大，默认跳过；需要时去掉下面 REM）---
REM python scripts\01_prepare_participants.py
REM python scripts\02_preprocess_eeg.py
REM python scripts\03_compute_psd.py
REM python scripts\04_run_specparam.py
REM python scripts\05_specparam_qc.py
REM python scripts\06_compute_roi_metrics.py

echo --- 阶段 B: 主统计 ---
python scripts\07_demographic_and_qc_stats.py
python scripts\07b_table1_main_cohort.py
python scripts\08_main_group_analysis.py
python scripts\09_roi_mixed_model.py
python scripts\10_channel_level_analysis.py
python scripts\11_clinical_correlation.py
python scripts\12_periodic_peak_analysis.py
python scripts\14_sensitivity_analysis.py
python scripts\17_qc_and_sensitivity_followup.py

echo --- 阶段 C: 年龄与信度 ---
python scripts\18_compare_with_preschool_study_checks.py
python scripts\19_development_and_reliability_extension.py

echo --- 阶段 D: ICLabel 敏感性（需 mne-icalabel）---
python scripts\23_iclabel_artifact_sensitivity.py --threshold 0.80 --threshold 0.70 --overwrite

echo --- 阶段 E: 机器学习 ---
python scripts\26_build_ml_input_dataset.py
python scripts\25_nested_cv_aperiodic_classifier.py
python scripts\28_plot_ml_publication_figures.py

echo --- 阶段 F: 论文图 ---
python scripts\21_make_consort_flow_paper.py
python scripts\21_make_paper_figures_v2.py
python scripts\16_generate_report_tables.py

echo.
echo [DONE] v11 流水线执行完毕。输出见 derivatives\ stats\ outputs\
endlocal
