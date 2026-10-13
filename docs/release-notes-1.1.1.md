# EventCraft 1.1.1

## 中文

AI 海报生成与活动物料 Skill 的安装和文档整理更新。

- 当前源码树移除旧版生成图、重复 HTML/PDF 和历史运行报告，保留十套当前海报、四种邀请函及精简打印示例。
- README 按效果、下载、安装依赖、活动提示、三款选择和成品查看重写。
- 默认用户包只包含 Skill 指令、运行代码、必要设计资源、使用指南和输入样例；不含测试或开发脚本。
- 测试源码继续在 GitHub CI 中检查；旧完整验收材料保存在 v1.1.0 快照。

## English

A packaging and onboarding update for the AI poster and event campaign Skill.

- Trim obsolete galleries, duplicate exports, and historical QA output from the current source tree. Keep representative posters, four invitations, and print samples.
- Rework both READMEs around downloading, runtime setup, event input, style selection, and viewing deliverables.
- Exclude tests and development scripts from the default complete Skill archive. Automated test source stays in Git for CI.

Download `eventcraft-skill-1.1.1.zip`. Python 3.11+, Chromium and CJK fonts are required. The archive includes runtime code; no separate Python wheel is needed.

[使用指南 / Usage](skill-usage.md) · [Gallery](style-gallery.md)
