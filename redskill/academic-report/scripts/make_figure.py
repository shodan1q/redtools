"""
make_figure —— 发表级学术插图（matplotlib，300 dpi）。

方法论借鉴 figure-style：标题写**结论**不写变量名、去冗余边框、刻度朝外、
图例无框、字号分级、中文字体自适应。给报告配图用，输出 PNG 可直接插进
build_academic_docx 的 Markdown。

复用：
    import make_figure as mf
    ax = mf.new_ax("六周后差距开始拉开", "每周测验均分（模拟数据）")
    mf.line(ax, x, y_series)          # 折线（末点标名）
    mf.bar(ax, labels, values)        # 条形（条端标值）
    mf.save(ax, "fig1.png")
命令行自检： python3 make_figure.py --demo out.png
依赖：matplotlib。
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

_CJK = ["/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"]
for _p in _CJK:
    if os.path.exists(_p):
        try:
            fm.fontManager.addfont(_p)
            plt.rcParams["font.family"] = fm.FontProperties(fname=_p).get_name()
            break
        except Exception:
            continue
plt.rcParams["axes.unicode_minus"] = False

INK, SUB, GRID = "#1A1A1A", "#8A8A8A", "#E6E6E6"
ACCENT = "#2F6BB0"


def new_ax(title, subtitle="", figsize=(6.2, 4.0)):
    """建图并写结论式标题。title=一句话结论，subtitle=口径。"""
    fig, ax = plt.subplots(figsize=figsize, dpi=300)
    fig.subplots_adjust(top=0.84, bottom=0.13, left=0.12, right=0.95)
    ax.set_title(title, fontsize=13, fontweight="bold", color=INK, loc="left", pad=16)
    if subtitle:
        ax.text(0, 1.02, subtitle, transform=ax.transAxes, fontsize=9.5,
                color=SUB, ha="left", va="bottom")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#CCCCCC")
    ax.tick_params(direction="out", length=3, colors=SUB, labelsize=9.5)
    ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    return ax


def line(ax, x, series, xlabels=None):
    """series: {名称: [值...]}，多条时末点标名。"""
    palette = [ACCENT, "#B0573A", "#3D8A6B", "#8A6AA8", "#8A8A8A"]
    for i, (name, ys) in enumerate(series.items()):
        c = palette[i % len(palette)]
        ax.plot(x, ys, color=c, lw=2.2, marker="o", ms=4.5,
                mfc="white", mec=c, mew=1.6, zorder=3, clip_on=False)
        ax.annotate(name, xy=(x[-1], ys[-1]), xytext=(6, 0),
                    textcoords="offset points", va="center", fontsize=9.5,
                    color=c, fontweight="bold", annotation_clip=False)
    if xlabels is not None:
        ax.set_xticks(list(x))
        ax.set_xticklabels(xlabels)
    ax.margins(x=0.04)
    return ax


def bar(ax, labels, values, highlight=None, unit=""):
    """条形图，可高亮某一条（highlight=索引），其余灰。"""
    cols = [ACCENT if (highlight is None or i == highlight) else "#BFBFBF"
            for i in range(len(values))]
    b = ax.bar(labels, values, color=cols, width=0.62, zorder=3)
    for rect, v in zip(b, values):
        ax.text(rect.get_x() + rect.get_width() / 2, v, f"{v}{unit}",
                ha="center", va="bottom", fontsize=9.5, fontweight="bold", color=INK)
    ax.margins(y=0.15)
    return ax


def save(ax, path):
    ax.figure.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(ax.figure)
    return path


if __name__ == "__main__":
    if "--demo" in sys.argv:
        out = sys.argv[-1] if sys.argv[-1].endswith(".png") else "demo.png"
        ax = new_ax("坚持组六周后明显领先", "每周测验均分 · 模拟数据")
        line(ax, list(range(1, 7)),
             {"坚持组": [55, 58, 64, 71, 76, 83], "对照组": [54, 55, 53, 56, 55, 57]},
             xlabels=[f"第{i}周" for i in range(1, 7)])
        save(ax, out)
        print("✓ 自检图已输出：", out)
    else:
        print(__doc__)
