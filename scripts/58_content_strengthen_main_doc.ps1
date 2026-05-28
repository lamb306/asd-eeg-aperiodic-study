$ErrorActionPreference = "Stop"

$docPath = "d:\asd_eeg_aperiodic_study\manuscript_submission_final.docx"
$backupPath = "d:\asd_eeg_aperiodic_study\manuscript_submission_final_before_content_strengthen.docx"

Copy-Item -LiteralPath $docPath -Destination $backupPath -Force

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open($docPath)

function Get-ParagraphIndexByPrefix {
    param(
        [object]$Document,
        [string]$Prefix
    )
    for ($i = 1; $i -le $Document.Paragraphs.Count; $i++) {
        $t = $Document.Paragraphs.Item($i).Range.Text.Trim("`r", "`a", " ")
        if ($t.StartsWith($Prefix)) {
            return $i
        }
    }
    throw "Heading not found: $Prefix"
}

function Set-ParagraphAfterHeading {
    param(
        [object]$Document,
        [string]$HeadingPrefix,
        [string]$Text
    )
    $idx = Get-ParagraphIndexByPrefix -Document $Document -Prefix $HeadingPrefix
    $Document.Paragraphs.Item($idx + 1).Range.Text = $Text + "`r"
}

# 2.1 Participants and study design
$text21 = "本研究采用横断面观察设计。初始样本 168 例，经可用无伪迹 epoch 阈值筛选后为 145 例，再经谱参数化质量控制后纳入静息态主分析 138 例（ASD = 61，TD = 77）。ASD 诊断信息来源于临床既往诊断与研究期复核记录，主文仅作保守表述，不在此处扩展未经核验的量表细节。TD 纳入标准为无已知神经发育障碍或重大精神/神经系统疾病史，且满足 EEG 与电影任务数据质量要求。排除标准包括关键人口学或核心分析变量缺失、EEG 质量控制不达标、以及不满足最小可用 epoch 条件。IQ 与临床量表用于描述样本特征并用于协变量敏感性评估；量表名称、版本及实施流程细节见补充方法与文末核验清单。电影分析样本与静息态样本不完全一致，反映不同分析任务的有效数据可用性差异。"
Set-ParagraphAfterHeading -Document $doc -HeadingPrefix "2.1 Participants and study design /" -Text $text21

# 2.5 Naturalistic movie ISC
$text25 = "电影范式采用自然观看任务并按预定义事件窗提取神经同步指标。事件类别包含 mental、pain 与 neutral：其中 mental 指包含显著心理状态理解成分的情节，pain 指以疼痛/伤害线索为主的情节，neutral 指不以社会认知或疼痛线索为核心的情节。事件标注基于研究期事件注释表；标注流程与一致性指标在补充方法中详细说明。ISC 采用 TD-template 策略计算并经 Fisher z 转换后得到事件级指标，再在同类别事件内聚合形成被试级结果。跨状态耦合优先使用 mental ISC，是因为其在研究问题中对应最高社会认知负荷并与假设路径直接相关。Delta_Exponent 定义为事件窗口相对基线窗口的非周期指数变化。质量控制协变量包括年龄、性别、IQ_total、可用无伪迹 epoch 以及模型/通道质量指标；无法在项目记录中逐条确认的参数不在主文展开，统一在补充方法与核验清单标注。"
Set-ParagraphAfterHeading -Document $doc -HeadingPrefix "2.5 Naturalistic movie ISC /" -Text $text25

# 2.7 Statistical analysis
$text27 = "统计推断采用双侧检验并以 p < 0.05 为名义阈值。Primary outcomes 为静息态全局非周期指数组间效应、后部非周期指数相关的跨状态交互项及电影 ISC 主效应；secondary/sensitivity outcomes 包括全局非周期偏移、自动 ICA 阈值敏感性、严格纳入标准敏感性及稳健回归结果；exploratory outcomes 包括临床相关与机器学习分类。协变量选择依据为先验混杂风险与数据质量相关性（年龄、性别、IQ_total、可用无伪迹 epoch 及相关 QC 指标）。缺失数据采用可用样本分析，不进行结果插补，并在各分析中报告对应 n。多重比较按预定义家族分别进行 BH-FDR 控制（事件级 ISC 家族、Delta_Exponent 家族、通道级家族）。考虑到离群值和异方差对交互项估计的潜在影响，并行报告 OLS 与稳健回归（RLM/winsor）；稳健回归用于验证方向与显著性稳定性，而非替代主模型。"
Set-ParagraphAfterHeading -Document $doc -HeadingPrefix "2.7 Statistical analysis /" -Text $text27

# 3.1 extra sentence before detailed result
$text31 = "Different analyses used different available samples because resting-state, movie ISC, and coupling models required different quality-control and completeness criteria. 静息态主分析显示 ASD 组全局非周期指数低于 TD 组。回归模型中 TD 相对 ASD 的组别效应为 β = 0.0791，SE = 0.0310，95% CI [0.0177, 0.1404]，p = 0.0119（n = 138）。描述统计为 ASD：1.69 ± 0.14，TD：1.79 ± 0.14。全局非周期偏移仅呈趋势（β = 0.0596，p = 0.0951）。该结果支持 ASD 宽频谱背景相对平坦，但不支持单一机制解释。"
Set-ParagraphAfterHeading -Document $doc -HeadingPrefix "3.1 Resting-state aperiodic exponent was reduced in ASD" -Text $text31

# 3.4 clarify neutral and Delta direction uncertainty
$text34 = "三类事件均表现 TD > ASD 且经 FDR 校正显著：mental（t = -2.3021，p = 0.0228，q = 0.0228）、pain（t = -3.9259，p = 1.36e-04，q = 2.03e-04）、neutral（t = -4.3572，p = 2.46e-05，q = 7.38e-05）。Neutral ISC was also significantly reduced, indicating that the observed ISC differences were not restricted to explicitly social events. Delta_Exponent 在 mental 和 pain 事件中同样达到家族内校正后显著（q = 7.11e-04），主文据此报告 group difference present；其 t 统计量方向对应的原始 contrast coding 仍需在补充材料与核验清单中由作者终核。"
Set-ParagraphAfterHeading -Document $doc -HeadingPrefix "3.4 Naturalistic movie ISC was reduced across event categories" -Text $text34

# 3.5 p-only stringent statement
$text35 = "跨状态耦合中，主分析样本（n = 128）交互项在 OLS 与 RLM/winsor 均显著（β = -0.3519，p = 0.0102；β = -0.5318，p = 0.00259）。严格纳入标准敏感性分析（n = 102）中，OLS 不显著（p = 0.0792），RLM 仍显著（p = 0.0195），说明证据在稳健回归中更强，而普通回归对纳入标准和模型设定敏感。Strict/stringent sensitivity results are reported as p-only sensitivity analyses because β and CI were unavailable in the current output."
Set-ParagraphAfterHeading -Document $doc -HeadingPrefix "3.5 Resting posterior exponent showed model-dependent coupling with mental ISC" -Text $text35

# Discussion expansions
$text43 = "后部电极簇表现最稳定组差，且后部非周期指数与 mental ISC 呈交互关系。该模式支持'基础神经背景影响自然情境加工效率'的解释框架。然而，交互证据在普通回归与稳健回归中的强度不同，并对纳入标准敏感，因此应表述为支持性证据而非确定性机制。就机制层面而言，后部非周期指数可被视为反映皮层群体活动背景状态的统计表征，而自然观看 ISC 反映跨个体时间锁定加工效率；二者相关提示'背景状态-信息整合效率'可能存在耦合，但不能据此推出单一神经生理通路。"
Set-ParagraphAfterHeading -Document $doc -HeadingPrefix "4.3 Posterior aperiodic effects and naturalistic neural synchrony" -Text $text43

$text44 = "电影 ISC 在三类事件均表现 TD > ASD，且 pain 与 neutral 同样显著。这一结果提示 ASD 儿童在自然连续信息处理中可能存在广泛同步降低，而非仅限于单一社会心理化事件。因而，结果更符合'跨类别加工效率下降'而非'纯社会特异性缺陷'的解释。neutral 事件也显著这一事实具有理论意义：其支持更广义的自然情境神经同步差异框架，并提示组间差异可能涉及跨情境信息整合而不完全依赖显性社会线索。"
Set-ParagraphAfterHeading -Document $doc -HeadingPrefix "4.4 Broad ISC reductions across mental, pain, and neutral events" -Text $text44

$text47 = "后部非周期指数与 CARS 的关联在不同分析设定下不稳定，且 QC 调整后不显著，因此仅能作为探索性信号。机器学习结果显示统计可分性，但缺乏独立测试集和外部验证，不应外推为临床诊断工具。性别与 IQ 的组间不平衡可能影响效应量估计和可迁移性边界，因此相关模型结果应理解为‘已做协变量控制但仍可能残留混杂’。机器学习模块在本研究中的定位是探索潜在可分特征而非构建可部署诊断器，其输出用于生成后续可验证假设。"
Set-ParagraphAfterHeading -Document $doc -HeadingPrefix "4.7 Clinical and translational boundaries" -Text $text47

$text48 = "本研究局限包括：横断面设计限制因果推断；性别与 IQ 组间不平衡可能残留混杂；交互与临床相关分析样本量仍有限；电影 ISC 事件标注与模板构建细节需完整披露；EEG 头皮电极结果不能进行脑源定位推断；部分结果对伪迹清洗策略和纳入标准敏感；缺乏独立外部验证队列；机器学习未在独立测试集验证。尤其需要强调，横断面 group × age 结果不能解释为个体纵向发育轨迹；电极层面效应也不能被解释为源定位结论。"
Set-ParagraphAfterHeading -Document $doc -HeadingPrefix "4.8 Limitations" -Text $text48

# Ensure verification checklist includes unresolved items
$verifyIdx = Get-ParagraphIndexByPrefix -Document $doc -Prefix "Items requiring author verification before submission"
$needItems = @(
    "- ASD 诊断流程与量表版本（ADOS/CARS 版本及施测流程）",
    "- IQ 量表名称、版本及施测时间窗",
    "- 电影事件标注者数量、一致性指标与冲突解决规则",
    "- Delta_Exponent 的原始 contrast coding 方向（t 正负对应组别）",
    "- Funding 最终正式文本"
)

$existing = @()
for ($i = $verifyIdx + 1; $i -le $doc.Paragraphs.Count; $i++) {
    $tt = $doc.Paragraphs.Item($i).Range.Text.Trim("`r", "`a", " ")
    if ($tt -eq "") { continue }
    if ($tt.StartsWith("Supplementary") -or $tt.StartsWith("Author Contributions") -or $tt.StartsWith("Conflict")) { break }
    $existing += $tt
}

foreach ($item in $needItems) {
    if (-not ($existing -contains $item)) {
        $doc.Paragraphs.Item($doc.Paragraphs.Count).Range.InsertParagraphAfter()
        $doc.Paragraphs.Item($doc.Paragraphs.Count).Range.Text = $item + "`r"
    }
}

$doc.Save()
$doc.Close()
$word.Quit()

Write-Output "content_strengthen_done=True"
Write-Output "backup=$backupPath"
