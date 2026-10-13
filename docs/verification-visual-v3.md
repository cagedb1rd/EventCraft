# 验证记录 / Verification

## 当前验证方式

GitHub CI 在每次推送时运行代码检查、Skill 资源校验、发布范围和链接检查、真实 Chromium 测试、完整活动导出与打包。请查看 [GitHub Actions](https://github.com/cagedb1rd/EventCraft/actions) 中对应提交的结果。

清理前的公开完整 CI 已验证 **115 项测试**及活动导出、打包；记录：[c34cc83 CI](https://github.com/cagedb1rd/EventCraft/actions/runs/38248156027)。该结果属于对应提交，不是后续提交的新验收声明。

自动化测试源码保留在 `tests/`，用于字体适配、事实一致性、二维码、图片与 PDF、选择状态、素材完整性及可迁移导出检查。测试报告与输出由 CI artifact 保存，不再将运行报告提交到 `docs/`。默认用户 Skill ZIP 不含测试、CI、开发脚本或生成样例。

## 视觉系统的历史验收

2026-10-12 的 v3 开发验收实际使用了 15 次内置图像生成，输出 16 套虚构活动物料、60 个 PDF / 66 页，检查十套风格、同风格不同主题、长标题、四种邀请函和隔离 Skill 工作流。人工查看的是代表性成品和总览，并非声称人工逐页审核全部 66 页。

当前保留 [精简 Gallery](style-gallery.md) 中的代表性图片和打印示例；完整报告、生成凭据及机器检查记录可以在 [v1.1.0 快照](https://github.com/cagedb1rd/EventCraft/blob/v1.1.0/docs/verification-visual-v3.md) 中查看。当前精简没有改变这些图片，也没有进行新的图像生成。

## 限制

- 文字边界和背景采样辅助检查，不能证明审美质量；新活动仍需 Agent 实际查看图片和 PDF。
- 原创图像能力取决于当前宿主工具；Python CLI 不能自行调用聊天内的 ImageGen。
- 平台字体会影响排版；安装包不附带商业字体。
- PDF 是 RGB 浏览器输出，未提供 CMYK、出血或实体双面打印校准。
- 旧生成文件保留在 Git 历史和版本快照中。当前源码树已精简，完整历史克隆仍会下载旧对象；只需最新开发代码时可使用 `git clone --depth 1`。
