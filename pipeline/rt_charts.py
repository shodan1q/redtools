"""
rt_charts —— redtools 数据图表库（matplotlib）

为小红书图文配套的数据可视化。中文字体自动适配 macOS 系统字体，
配色/比例与 redtools 卡片风格统一，输出 1080px 宽的高清 PNG，
可直接和本工具导出的卡片一起放进小红书轮播图。

复用方式（见 content/<post>/make_charts.py）：
    import rt_charts as rc
    rc.waffle(tiers, "images/chart.png", title, subtitle, note)
    rc.tiers_bar(tiers, "images/bar.png", title)
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

# ---- 中文字体 ----------------------------------------------------------------
_FONT_CANDIDATES = [
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
]


def _setup_font():
    for p in _FONT_CANDIDATES:
        if os.path.exists(p):
            try:
                fm.fontManager.addfont(p)
                name = fm.FontProperties(fname=p).get_name()
                plt.rcParams["font.family"] = name
                plt.rcParams["axes.unicode_minus"] = False
                return name
            except Exception:
                continue
    return None


FONT = _setup_font()

# ---- 配色（与小红书层级图一致）---------------------------------------------
INK = "#1F2329"
SUB = "#8A8F99"


def _ensure_dir(path):
    d = os.path.dirname(os.path.abspath(path))
    if d:
        os.makedirs(d, exist_ok=True)


def waffle(tiers, out, title, subtitle="", note="", cols=50, rows=50, px=(1080, 1180)):
    """点阵/华夫图：每个点代表固定人数，按层级从上到下填充。

    tiers: [{'label','people','pct','color','dots'(可选)}...]，dots 不给则按 pct 估算。
    """
    total = cols * rows
    # 计算每层占用的点数（小层级至少 1 个点，余数补到第一个层级）
    dots = []
    for t in tiers:
        if "dots" in t and t["dots"] is not None:
            dots.append(int(t["dots"]))
        else:
            dots.append(max(1, round(t["pct"] / 100.0 * total)))
    if sum(dots) != total:
        dots[0] += total - sum(dots)

    # 展开成每个点的颜色（从上到下、逐行填充）
    colors = []
    for t, d in zip(tiers, dots):
        colors += [t["color"]] * d
    colors = colors[:total]

    # 浅灰太淡、嵌进卡片缩小后看不清 —— 统一加深一档
    colors = ["#AEB4BD" if c == "#C9CDD2" else c for c in colors]

    w, h = px
    dpi = 160
    fig = plt.figure(figsize=(w / dpi, h / dpi), dpi=dpi)
    fig.patch.set_facecolor("white")

    # 标题区
    fig.text(0.5, 0.965, title, ha="center", va="top",
             fontsize=32, fontweight="bold", color=INK)
    if subtitle:
        fig.text(0.5, 0.910, subtitle, ha="center", va="top",
                 fontsize=12.5, color=SUB)

    # 点阵区（离散方点、留间隙，像信息图）
    grid_top, grid_bottom = 0.875, 0.40
    ax = fig.add_axes([0.07, grid_bottom, 0.86, grid_top - grid_bottom])
    ax.set_xlim(-0.6, cols - 0.4)
    ax.set_ylim(-0.6, rows - 0.4)
    ax.invert_yaxis()
    ax.axis("off")
    ax.set_aspect("equal")
    xs = [i % cols for i in range(total)]
    ys = [i // cols for i in range(total)]
    ax.scatter(xs, ys, c=colors, marker="s", s=14, linewidths=0)

    # 图例区（紧凑：色块 + 标签·人数 + 百分比，省略长描述）
    n = len(tiers)
    y0 = 0.345
    dy = y0 / (n + 0.2)
    pct_palette = {"#3DA35D": "#2F8F4E", "#3E7BE6": "#2F6BD6",
                   "#F5A623": "#D98E1E", "#E1483D": "#D23A30"}
    for k, t in enumerate(tiers):
        y = y0 - k * dy
        fig.patches.append(plt.Rectangle((0.07, y - 0.016), 0.034, 0.030,
                                         transform=fig.transFigure,
                                         facecolor=t["color"], edgecolor="none",
                                         clip_on=False))
        fig.text(0.12, y, f"{t['label']}  ·  {t['people']}", va="center",
                 fontsize=16.5, fontweight="bold", color=INK)
        pc = pct_palette.get(t["color"], SUB)
        fig.text(0.93, y, t["pct_label"] if "pct_label" in t else f"{t['pct']}%",
                 va="center", ha="right", fontsize=16.5, fontweight="bold", color=pc)

    if note:
        fig.text(0.07, 0.025, "注：" + note, va="bottom", fontsize=12, color=SUB)

    _ensure_dir(out)
    fig.savefig(out, dpi=dpi, facecolor="white")
    plt.close(fig)
    return out


def tiers_bar(tiers, out, title, subtitle="", note="", px=(1080, 840)):
    """层级条形图（对数刻度，跨度极大时仍清晰），带人数标注。"""
    w, h = px
    dpi = 160
    fig = plt.figure(figsize=(w / dpi, h / dpi), dpi=dpi)
    fig.patch.set_facecolor("white")
    fig.text(0.5, 0.955, title, ha="center", va="top",
             fontsize=29, fontweight="bold", color=INK)
    if subtitle:
        fig.text(0.5, 0.905, subtitle, ha="center", va="top", fontsize=13.5, color=SUB)

    ax = fig.add_axes([0.30, 0.13, 0.64, 0.70])
    labels = [t["label"] for t in tiers][::-1]
    vals = [t["value"] for t in tiers][::-1]
    cols = [t["color"] for t in tiers][::-1]
    peo = [t["people"] for t in tiers][::-1]
    pcts = [t.get("pct_label", f"{t['pct']}%") for t in tiers][::-1]
    y = range(len(labels))
    ax.barh(list(y), vals, color=cols, height=0.62, zorder=3)
    ax.set_xscale("log")
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=13, color=INK)
    ax.tick_params(axis="x", labelsize=10, colors=SUB)
    ax.tick_params(axis="y", length=0)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color("#E6E8EB")
    ax.grid(axis="x", color="#EEF0F2", zorder=0)
    ax.set_xlim(left=min(vals) * 0.4, right=max(vals) * 60)
    for i, (v, p, pc) in enumerate(zip(vals, peo, pcts)):
        ax.text(v * 1.5, i, f"{p}  ({pc})", va="center", fontsize=12,
                fontweight="bold", color=INK)

    if note:
        fig.text(0.06, 0.03, "注：" + note, va="bottom", fontsize=10.5, color=SUB)
    _ensure_dir(out)
    fig.savefig(out, dpi=dpi, facecolor="white")
    plt.close(fig)
    return out
