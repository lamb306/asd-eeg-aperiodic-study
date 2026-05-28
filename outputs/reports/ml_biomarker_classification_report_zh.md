# ASD vs TD 静息态 EEG 非周期特征分类研究总结（Nested CV）

## 1. 研究目的与结论摘要

本研究旨在评估 aperiodic EEG features（非周期成分）在 ASD vs TD 分类中的判别能力，并与传统周期特征进行比较。  
核心结论如下：

- 在全样本中，非周期特征模型显著优于仅周期特征模型，但整体判别力为 **modest**。
- 采用年龄相关建模（`age_months` + 交互项）并聚焦 older child 子样本（`age_months > 72`）后，AUC 明显提升，达到 **0.80**。
- 当前最稳妥措辞应为：**candidate biomarker**，不建议表述为已确立 biomarker。

---

## 2. 数据与特征

### 2.1 输入数据

- 主建模表：`data.csv`
- 年龄信息：`data/participants/participants.csv`
- 通道级特征（channel-wise 实验）：`derivatives/specparam/specparam_channel_results.csv`

### 2.2 特征定义

- Model A（periodic）：
  - `alpha_pw`, `alpha_cf`, `theta_pw`, `beta_pw`
- Model B（aperiodic）：
  - `global_exponent`, `global_offset`, `posterior_exponent`
  - `frontal_exponent`, `central_exponent`, `temporal_exponent`, `parietal_exponent`, `occipital_exponent`
- Model C（combined）：
  - A + B 全部特征

### 2.3 增强特征（v2）

- 年龄主效应：`age_months`
- 交互项：
  - `age_x_global_exponent = age_months * global_exponent`
  - `age_x_posterior_exponent = age_months * posterior_exponent`

---

## 3. 方法学（严格防数据泄露）

- 评估框架：**Nested Cross-Validation**
  - Outer：`Stratified 5-fold`
  - Inner：`Stratified 5-fold` + `GridSearchCV`
- 防泄露实现：所有模型均使用
  - `Pipeline([StandardScaler(), classifier])`
- 分类器与调参：
  - SVM (RBF): `C=[0.01,0.1,1,10,100]`, `gamma=['scale',0.01,0.1,1]`
  - Logistic Regression: `C=[0.01,0.1,1,10]`
  - Random Forest: `n_estimators=[100,200]`, `max_depth=[3,5,None]`
- 指标：
  - AUC, Accuracy, Sensitivity, Specificity, Balanced Accuracy, F1
- 统计检验：
  - DeLong test（AUC 比较：A vs B、B vs C）
- 可解释性：
  - Tree 模型：SHAP
  - 线性/SVM：Permutation Importance

---

## 4. 主结果（全样本，基础模型）

来源文件：`outputs/ml_biomarker/classification_results.csv`  
最佳组合：

- **Model B (aperiodic) + RandomForest**
- `AUC_mean = 0.6813`

DeLong 结果（`outputs/ml_biomarker/delong_results.csv`）：

- Model A vs Model B: `p = 0.0205`（显著）
- Model B vs Model C: `p = 0.0238`（显著，且 Model C 未优于 Model B）

解释性（`outputs/ml_biomarker/feature_importance.csv`）：

- `posterior_exponent` 排名第 1（最重要特征）

结论：全样本下可支持“**modest but significant discriminative utility**”。

---

## 5. AUC 提升实验（你提出的三步）

来源文件：
- `outputs/ml_biomarker/classification_results__abc_ageint_older72_v2check.csv`
- `outputs/ml_biomarker/delong_results__abc_ageint_older72_v2check.csv`
- `outputs/ml_biomarker/classification_results__channelwise_older72_v2check.csv`

### 5.1 Step 1：加入年龄与交互项

- 全样本（含 age + interaction）下最优：
  - `Model B + age_interactions + LogisticRegression`
  - `AUC_mean` 提升明显（见 5.2 子样本结果更强）

### 5.2 Step 2：older child（`age_months > 72`）

- 最优模型：
  - **Model B (aperiodic) + age_interactions + LogisticRegression**
  - `AUC_mean = 0.8004`
  - `Balanced_Accuracy_mean = 0.7025`
  - `F1_mean = 0.6569`

DeLong（该配置下）：

- Model A vs Model B: `p = 0.0032`（显著）
- Model B vs Model C: `p = 0.9218`（不显著）

解释性（`feature_importance__abc_ageint_older72_v2check.csv`）：

- `posterior_exponent` 排名第 3
- `age_x_posterior_exponent` 进入前列（第 5）

### 5.3 Step 3：channel-wise exponent + Elastic Net

- `Model D (channelwise_aperiodic) + LogisticElasticNet`
- `AUC_mean = 0.6953`
- 在当前数据与参数网格下，未超过 Step 2 结果。

---

## 6. 图像与输出文件

关键图：

- ROC：`outputs/ml_biomarker/roc_curves_3models.png`
- older+age 版本 ROC：`outputs/ml_biomarker/roc_curves_3models__abc_ageint_older72_v2check.png`
- 混淆矩阵、特征重要性、SHAP 图均已在 `outputs/ml_biomarker` 生成。

核心表格：

- `classification_results.csv`
- `feature_importance.csv`
- `delong_results.csv`
- `classification_results__abc_ageint_older72_v2check.csv`
- `feature_importance__abc_ageint_older72_v2check.csv`
- `delong_results__abc_ageint_older72_v2check.csv`

---

## 7. 建议写作措辞（可直接用于文稿）

建议主文使用：

- 全样本：  
  “Aperiodic EEG features showed **modest but significant** discriminative utility for ASD vs TD classification.”
- 更谨慎定位：  
  “These findings support aperiodic EEG parameters as a **candidate biomarker** rather than a definitive diagnostic biomarker.”
- 分层发现：  
  “Classification performance improved substantially in older children, reaching acceptable-to-strong discrimination (AUC ~0.80).”

---

## 8. 复现命令

### 8.1 构建建模输入表

```bash
python scripts/26_build_ml_input_dataset.py --output_csv data.csv --periodic_scope global
```

### 8.2 基础模型（A/B/C）

```bash
python scripts/25_nested_cv_aperiodic_classifier.py --input_csv data.csv --output_dir outputs/ml_biomarker
```

### 8.3 年龄交互 + older child

```bash
python scripts/25_nested_cv_aperiodic_classifier.py --input_csv data.csv --output_dir outputs/ml_biomarker --use_age_interaction --older_than_months 72 --output_tag v2check
```

### 8.4 channel-wise

```bash
python scripts/25_nested_cv_aperiodic_classifier.py --output_dir outputs/ml_biomarker --channelwise --older_than_months 72 --output_tag v2check
```

