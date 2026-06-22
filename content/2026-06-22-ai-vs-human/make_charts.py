"""本篇数据图表 —— AI 使用层级（复刻图7）。

运行：python3 make_charts.py
依赖 ../../pipeline/rt_charts.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "pipeline"))
import rt_charts as rc  # noqa: E402

OUT = os.path.join(HERE, "images")

# 每个点代表 320 万人，2500 点 = 81 亿人（2026-02 估算）
TIERS = [
    {"label": "从未使用过 AI", "people": "约 68 亿人", "pct": 84, "color": "#C9CDD2",
     "dots": 2118, "desc": "不了解、不接触或从未使用过任何 AI 产品。"},
    {"label": "用过免费 AI 工具", "people": "约 8 亿人", "pct": 10, "color": "#3DA35D",
     "dots": 250, "desc": "偶尔使用 ChatGPT 免费版、Gemini、Copilot 等。"},
    {"label": "高频使用 AI", "people": "约 4 亿人", "pct": 5, "color": "#3E7BE6",
     "dots": 125, "desc": "工作/学习/创作中常用：写作、翻译、分析、编程。"},
    {"label": "为 AI 付费", "people": "约 2,000 万人", "pct": 0.25, "pct_label": "0.25%",
     "color": "#F5A623", "dots": 6, "desc": "订阅 ChatGPT Plus、Claude Pro、Midjourney 等。"},
    {"label": "用 AI 构建工具 / Agent", "people": "约 200 万人", "pct": 0.024, "pct_label": "0.024%",
     "color": "#E1483D", "dots": 1, "desc": "用 AI 编程工具、自动化框架、构建 Agent/应用的专业用户。"},
]

# 条形图用的绝对数值（人）
for t, v in zip(TIERS, [6_800_000_000, 800_000_000, 400_000_000, 20_000_000, 2_000_000]):
    t["value"] = v


def main():
    rc.waffle(
        TIERS, os.path.join(OUT, "chart-01-people-dots.png"),
        title="每个点代表 320 万人",
        subtitle="2,500 个点 = 81 亿人 · 全球 AI 使用层级现状（2026 年 2 月，估算）",
        note="本图基于公开数据、行业报告及统计推算，仅用于趋势展示，不代表精确统计结果。",
    )
    rc.tiers_bar(
        TIERS, os.path.join(OUT, "chart-02-tiers.png"),
        title="AI 使用层级 · 全球估算",
        subtitle="人数对数刻度 · 越往上越稀少",
        note="数据为估算推演，仅用于趋势展示。",
    )
    print("图表已输出到:", OUT)


if __name__ == "__main__":
    main()
