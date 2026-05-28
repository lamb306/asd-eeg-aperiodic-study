# 将本项目推送到 GitHub

目标仓库：**https://github.com/lamb306/asd-eeg-aperiodic-study**

## 一次性准备（若尚未创建远程仓库）

1. 浏览器打开 <https://github.com/new>
2. Repository name：`asd-eeg-aperiodic-study`
3. 选择 **Private**（含临床流程，建议私有）或 **Public**（课程公开展示代码）
4. **不要**勾选 “Add a README”（本地已有）
5. 点击 Create repository

## 在项目根目录执行

```powershell
cd d:\asd_eeg_aperiodic_study

git init
git branch -M main
git add .
git status
git commit -m "Initial public release: ASD resting EEG aperiodic analysis pipeline (v11)"

git remote add origin https://github.com/lamb306/asd-eeg-aperiodic-study.git
git push -u origin main
```

若已配置 SSH：

```powershell
git remote add origin git@github.com:lamb306/asd-eeg-aperiodic-study.git
git push -u origin main
```

推送时 GitHub 会要求登录或使用 [Personal Access Token](https://github.com/settings/tokens) 作为密码。

## 论文中的引用位置

已在 `manuscript_draft_zh_v11_final.md` **§2.9 数据与代码可用性** 写入上述 URL。Word 稿请打开 `manuscript_draft_zh_v11_final.docx`，在方法部分「机器学习」小节后插入相同 §2.9 段落，或从更新后的 Markdown 重新导出。
