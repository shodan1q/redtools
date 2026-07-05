# 小红书 Skills 家族

本目录是 redtools 项目的**小红书内容技能库**。所有与小红书内容生产相关的 skill 都放在这里，
Claude Code 会自动发现 `.claude/skills/<名字>/SKILL.md` 并按需触发。

## 现有技能

| Skill | 干什么 | 典型说法 |
|---|---|---|
| `xhs-post` | **主技能**：从主题/素材/长文一条龙生成完整图文笔记（文案+图表+精美卡片+发布文案） | "帮我做一篇关于××的小红书" |
| `xhs-copy` | 纯文案：爆款标题、正文、发布 caption、话题标签 | "给我写个小红书标题/文案" |
| `xhs-charts` | 数据图表：与卡片风格统一的 1080px 信息图 | "把这组数据做成小红书配图" |

## 家族约定（新增 skill 请遵守）

1. **命名**：一律 `xhs-` 前缀 + 小写连字符，如 `xhs-video-script`、`xhs-comment-reply`。
2. **结构**：每个 skill 一个目录，`SKILL.md` 必备；超过 500 行的内容拆到 `references/`，
   可执行工具放 `scripts/`。
3. **设计系统是共享的**：所有涉及视觉产出的 skill 都复用
   [`xhs-post/references/design-presets.md`](xhs-post/references/design-presets.md) 里的风格预设，
   不要另起一套配色。这样整个账号的图文有统一的视觉识别。
4. **产出归档**：任何 skill 生成的成品都归档到项目根的 `content/<日期>-<标题>/`，
   由 `pipeline/new_post.py` 统一管理，不要散落别处。
5. **底层渲染不重复造轮子**：出卡片一律走 `pipeline/export_cards.py`（无头驱动根目录
   `index.html`），出图表一律用 `pipeline/rt_charts.py`。要新增视觉能力时优先扩展这两处。
6. **description 要"外向"**：写清楚什么时候该触发（包括用户没明说"小红书"的场景），
   宁可稍微激进，不要漏触发。
7. **只生产内容，绝不自动发布**：任何 xhs-* skill 都不得登录、驱动或模拟操作小红书
   平台（包括定时发布、自动发布、批量互动、托管代发）。产出一律交给用户手动发布，
   并提醒用户按平台规定为 AI 生成内容勾选标识。这是平台红线（违者封号），也是本
   家族能上架 RedSkill 市场的前提。本项目里唯一的"无头浏览器"用途是渲染根目录的
   本地 `index.html` 出图，与小红书平台没有任何交互。

## 依赖

```bash
pip install matplotlib playwright && playwright install chromium
```

导出卡片时字体从 CDN 加载（思源黑/宋、站酷系列），需要联网。
