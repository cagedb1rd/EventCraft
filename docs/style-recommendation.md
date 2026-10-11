# 可解释的十选三推荐

`eventcraft recommend event.json` 执行代码评分，并输出前三套实际渲染预览。配置、评分版本、所有候选的分项分数、输入摘要/hash、配置 hash、推荐列表和用户选择持久化；这不是自由 Prompt 的临场答案。

## 特征和权重

| 维度 | 权重 | 输入与规则 |
|---|---:|---|
| 活动类型 | 30 | category/subtype、每个 profile 的 types；未知类型走通用匹配 |
| 受众与传播渠道 | 20 | 显式 audience（中英常见名称归一）和 channels；未知受众用中性值 |
| 气质与正式度 | 15 | formality 与 profiles 匹配，避免场景降分 |
| 素材与场景 | 10 | 主题关键词、开始小时、室内/户外、主图存在性 |
| 文案密度 | 10 | 标题、副标题、亮点长度；超长标题降低低密度版式得分 |
| 品牌适配 | 10 | 色板可重配、原 Logo 保留；冲突先排除 |
| 可读性与语言 | 5 | 中英混排支持；渲染阶段真实对比度和文字测量 |

这是公开工程规则，不代表调研或审美客观概率。可用 `--weights` 传入七个同名键，总和必须是 100。缺失事实不能进入理由；category/formality 的推断可在 sources 中标 inferred。正式报名、地点、主办方、票价和受众不推断。

先处理硬约束：forbidden_styles；要求色与禁用色矛盾；未替换的预设色使用禁用色。被排除项有 conflicts，前三不包含。品牌色优先于参考色，正文和小标签对比度 ≥4.5，Logo 原貌始终保留。高对比是最低要求，不以分数绕过。

活动类别是主因，夜间娱乐和竞技有显式区别：电竞比赛优先 sports-dynamic；包含 DJ/派对的电竞娱乐优先 neon-night；婚礼/正式晚宴优先 luxury-elegant。学术科技允许 academic-clean 与 tech-gradient 同时出现，取舍由具体布局文字解释。十套布局的 family 各不相同，稳定排序的前三天然具有结构差异；不为了“创意第三名”跳过明显更适合的候选。“更有创意”只是 UI 角色名称，不代表客观创新评分。

## 状态与覆盖

```sh
eventcraft recommend examples/inputs/lecture.json --output output/selection
eventcraft recommend examples/inputs/lecture.json --output output/selection --next
eventcraft all examples/inputs/lecture.json --select 2 --state output/selection --output output/chosen
```

页 1 为 1–3、页 2 为 4–6，按所有 eligible 排序划分，互不重复；页末可能不足三套，如实告知。未知事实允许带草稿标记预览，但不会写入 event 的假占位值。final generation 仍严格检查必填。

数字映射当前 state 的 position；自动选择从全体 eligible 取最高。event_digest 不同会拒绝旧数字选择。显式 ID/中文名/英文名可选池外任意风格。显式风格高于编号/自动；参考图高于三选一交互，显式风格决定参考基础版式。`--all` 只在主动请求时展示完整候选，冲突项有说明而不渲染。

每项返回 style_id、rank、position、score、reason、tradeoff、preview_path、来源 digest 和布局检查。图由同一 Chromium 引擎生成，预览分辨率 540×540；不是第三方网图。真实运行见 [终端记录](recommendation-terminal.txt)、[比较页](../examples/recommendation/recommendations.html) 和 README 截图。
