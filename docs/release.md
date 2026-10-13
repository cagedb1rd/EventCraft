# 发布维护指南 / Release maintenance

面向维护者。用户安装请看 [README](../README.md) 和 [使用指南](skill-usage.md)。当前源码版本为 **1.1.1**。

## 检查与构建

在项目虚拟环境执行：

```sh
python -m pip install -e '.[dev]'
python -m playwright install chromium
python -m ruff check eventcraft scripts tests
python scripts/validate_skill.py
python scripts/release_check.py
python -m pytest -q
python -m build --wheel
python scripts/package_skill.py
```

默认用户 Skill ZIP 包含指令、运行代码、必要配置、原创推荐素材、输入样例和使用指南；不包含 tests、开发脚本、CI 或 Gallery。`--with-examples` 构建另一个可选开发资料包，不作为用户默认下载。wheel 用于本地安装验证，不需要上传到面向 Skill 用户的 Release。

CI 在临时 runner 中构建 wheel 和源码包，运行报告与烟测输出作为 artifact 保存；这些文件不进入 Git。源码包只包含当前精简 Gallery，不重新收录旧版大目录。

## 上传

选择 CI 通过的提交创建对应版本 tag。上传以下文件并生成对应 SHA256：

- `eventcraft-skill-1.1.1.zip`
- `SHA256SUMS-1.1.1.txt`

使用 [发布说明](release-notes-1.1.1.md)。上传完成后检查资产大小及 GitHub 返回的 SHA256，再发布。不要把新包覆盖到 v1.1.0；历史版本保留完整快照。文档变更后也应重新打包。

## 文件边界

测试源码留在 Git 供 CI 检查；测试运行报告、开发画廊、原始活动输出放在忽略的 `output/` 或 `tmp/`。`/image/` 研究资料、用户附件、密钥、环境和系统字体不发布。源码目录缩小不会重写 Git 历史；仅需当前代码可用 `git clone --depth 1`。
