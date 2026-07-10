# claude-science/ · Anthropic Claude Science 技能（原样转载）

本目录是 Anthropic 公开发布的 **Claude Science / Claude 技能集**的**原样转载**（未修改内容），
均以 **Apache License 2.0** 授权。搬运至此仅为在小红书 RedSkill 分发 + 加中文说明。

- 版权所有 © Anthropic, PBC；原始许可证见各技能目录内的 `LICENSE.txt`。
- 转载者 AgentOPC 未改动任何技能本身（Apache-2.0 要求：保留许可证与署名、如有修改需注明——此处无修改）。

## ⚠️ 上传前务必知道

**1. 必须选「转载」不是「原创」。** 上传 RedSkill 时「内容来源」选 **Skill 源码来自转载**，
   「来源」填 Anthropic 官方技能仓库地址。标成「原创」= 冒名，违规且失信。

**2. 大部分技能在别人的 AI 助手里跑不起来。** 它们依赖 claude.ai Science 的专有运行环境
   （`repl` Python 内核、`host.*` SDK）。别人从小红书装到自己的通用 AI 助手后，一调用这些函数
   就会报错。传这些等于给粉丝发不能用的技能——建议**只传下表标 ✅ 的**，或干脆走
   `../` 里我自制的 `xhs-*` / `academic-report`（自包含、真能跑）。

## 各技能能不能被别人独立使用

| 技能 | 别人装了能不能跑 | 说明 |
|---|---|---|
| algorithmic-art | ✅ 较可能 | p5.js 生成艺术，代码较独立 |
| indication-dossier | ✅ 较可能 | 医学适应症档案，纯提示词方法论 |
| learn | ✅ 较可能 | 学习/讲解方法，通用 |
| web-artifacts-builder | ⚠️ 半依赖 | 面向 claude.ai 的 React 制品，离开 claude.ai 会打折 |
| product-self-knowledge | ⚠️ 无意义 | 专讲 Anthropic 产品，搬到小红书没用 |
| figure-style | ❌ 需 claude.ai | 依赖 `apply_figure_style` 等内核函数 |
| figure-composer | ❌ 需 claude.ai | 依赖 `repl` / `host.*` 多智能体编排 |
| paper-narrative | ❌ 需 claude.ai | 依赖内核函数 |
| literature-review | ❌ 需 claude.ai | 依赖检索/内核环境 |
| pdf-explore | ❌ 需 claude.ai | 依赖 `pdf_pages` 等内核解析器 |
| self-awareness | ❌ 需 claude.ai | 讲 Claude Science 内部数据库，外部无意义 |
| customize | ❌ 需 claude.ai | Anthropic 的 `host.agents/skills` SDK |
| skill-creator | ❌ 需 claude.ai | Anthropic 建技能工具链（252KB，含评测器） |

> 「✅ 较可能」也只是没检测到硬编码依赖，仍可能默认 claude.ai 语境；上传前最好在你自己的
> AI 助手里实测一下再决定。

## 更稳的替代（推荐）

想要这些技能的**能力**又不想踩"别人跑不了"的坑：我已经把 `figure-style` 的发表级图表方法论
移植进了自制的 `academic-report/scripts/make_figure.py`（自包含、300dpi、真能跑、署名 Anthropic）。
同理可把 `literature-review`（文献核验方法）、`paper-narrative`（图表叙事弧）等移植成
自制可用技能——合法、能跑、是你维护的。需要就说。
