"""本篇数据图表：被打断的真实代价（对比条形）。运行: python3 make_charts.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "pipeline"))
import rt_charts as rc  # noqa: E402

OUT = os.path.join(HERE, "images")


def main():
    rc.compare_bars(
        [{"label": "回一条消息", "value": 2, "text": "≈ 2 分钟", "color": "#AEB4BD"},
         {"label": "重新进入深度专注", "value": 23, "text": "≈ 23 分钟", "color": rc.PALETTE[0]}],
        os.path.join(OUT, "chart-01-refocus.png"),
        title="回消息 2 分钟，找回专注 23 分钟",
        subtitle="被打断后重新进入深度专注的平均耗时",
        note="23 分钟取自加州大学尔湾分校 Gloria Mark 团队研究（平均 23 分 15 秒），回复耗时为估算示意。")
    print("图表已输出到:", OUT)


if __name__ == "__main__":
    main()
