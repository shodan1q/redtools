---
name: xhs-charts
description: 为小红书笔记生成数据图表/信息图：点阵人群图、环形占比、趋势折线、对比条形、对数层级条形，1080px 白底高清 PNG，与本项目卡片风格统一。用户说「把这组数据做成图」「给笔记配个数据图表」「画个占比图/趋势图」时用；需要整套图文卡片时用 xhs-post（它会在流程里调用同一套图表库）。
---

# 小红书数据图表

用 `pipeline/rt_charts.py` 出图。**完整的函数签名、示例代码、选型表、设计守则都在
[../xhs-post/references/charts-guide.md](../xhs-post/references/charts-guide.md)，先读它。**

本 skill 独立使用时的额外约定：

## 输出位置

- 属于某篇笔记的图 → 该篇 `content/<日期-标题>/images/chart-NN-语义.png`
- 独立散图（用户临时要的）→ `content/charts/<日期>-<语义>.png`

## 工作流

1. 弄清数据和**要传达的那句话**——一图一结论，标题写结论不写变量名
2. 按 charts-guide.md 的选型表挑图型（构成→donut/waffle，趋势→trend，
   对比→compare_bars，量级悬殊→tiers_bar）
3. 写个临时脚本或直接 `python3 -c` 调 rt_charts 出图
4. 用 Read 查看 PNG 成品：中文无豆腐块、无文字重叠、重点色突出、note 有数据口径
5. 交付路径 + 一句"这张图适合放在笔记哪个位置"的建议

## 快速示例

```bash
python3 - <<'EOF'
import sys; sys.path.insert(0, "pipeline")
import rt_charts as rc
rc.donut([{"label": "会用AI的", "pct": 16},
          {"label": "还没用的", "pct": 84}],
         "content/charts/2026-07-04-ai-usage.png",
         title="10个人里只有不到2个在用AI",
         center="16%\n已经在用", note="估算数据，仅示意。")
EOF
```

## 风格红线

- 每图 ≤6 类目 / ≤2 条线；多了拆图
- 估算数据必须 note 注明；配色不自定义时用默认 `rc.PALETTE`（与卡片主题同源）
- 嵌卡片的图宁方勿高（默认尺寸已调好，别乱改）
