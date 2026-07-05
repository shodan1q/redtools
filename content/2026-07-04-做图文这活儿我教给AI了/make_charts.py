"""本篇数据图表：一篇图文的时间去向（对比条形）。运行: python3 make_charts.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "pipeline"))
import rt_charts as rc  # noqa: E402

OUT = os.path.join(HERE, "images")


def main():
    rc.compare_bars(
        [{"label": "想标题", "value": 45, "text": "≈ 45 分钟", "color": "#AEB4BD"},
         {"label": "磨文案", "value": 75, "text": "≈ 75 分钟", "color": "#AEB4BD"},
         {"label": "排版做图", "value": 120, "text": "≈ 120 分钟", "color": rc.PALETTE[0]}],
        os.path.join(OUT, "chart-01-time.png"),
        title="一篇图文的 4 小时，一半耗在排版",
        subtitle="发一篇笔记的时间去向（分钟/篇，个人均值）",
        note="个人统计，仅示意，你的比例可能不同。")
    print("图表已输出到:", OUT)


if __name__ == "__main__":
    main()
