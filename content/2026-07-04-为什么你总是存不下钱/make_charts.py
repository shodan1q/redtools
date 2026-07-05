"""本篇数据图表 —— 拿铁因子复利曲线 + 50/30/20 先付自己分配。

运行：python3 make_charts.py
依赖 ../../pipeline/rt_charts.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "pipeline"))
import rt_charts as rc  # noqa: E402

OUT = os.path.join(HERE, "images")

ACCENT = "#D98E3D"  # 预设6·墨黑杂志的主题强调色（金橙）
GRAY = "#AEB4BD"
GRAY_LIGHT = "#C9CDD2"

# 每天 30 元 = 每年 10,950 元；定投按年化 6% 复利（普通年金）测算，单位：万元
# 末值标注画在坐标区右侧，线名≤2字、数值取整，避免超出画布被裁切
YEARS = [5, 10, 15, 20, 25, 30]
INVEST = [6, 14, 26, 40, 60, 87]  # 10950 * ((1.06^n - 1) / 0.06)，取整
CASH = [5, 11, 16, 22, 27, 33]    # 10950 * n，取整


def main():
    rc.trend(
        [
            {"label": "定投", "values": INVEST, "unit": "万", "color": ACCENT},
            {"label": "现金", "values": CASH, "unit": "万", "color": GRAY},
        ],
        os.path.join(OUT, "chart-01-latte-trend.png"),
        title="一天 30 元，30 年后的两种命运",
        subtitle="同样每天 30 元：存进指数定投 vs 只存现金（单位：万元）",
        xlabels=[f"第{y}年" for y in YEARS],
        note="估算示意：按每年 10,950 元、年化 6% 复利推算，不构成任何投资建议。",
    )
    rc.donut(
        [
            {"label": "必要开销", "pct": 50, "sub": "房租、吃饭、通勤", "color": GRAY_LIGHT},
            {"label": "想要的", "pct": 30, "sub": "娱乐、社交、购物", "color": GRAY},
            {"label": "先付自己", "pct": 20, "sub": "到账当天自动转走", "color": ACCENT},
        ],
        os.path.join(OUT, "chart-02-payself-donut.png"),
        title="先付自己：到账先分，再谈花钱",
        subtitle="50 / 30 / 20 预算框架",
        center="20%\n先转给未来的你",
        note="50/30/20 为通用预算框架，比例可按收入与负债情况调整，仅示意。",
    )
    print("图表已输出到:", OUT)


if __name__ == "__main__":
    main()
