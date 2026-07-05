"""
rt_charts —— redtools 数据图表库（matplotlib）

为小红书图文配套的数据可视化。中文字体自动适配 macOS 系统字体，
配色/比例与 redtools 卡片风格统一，输出 1080px 宽的高清 PNG，
可直接和本工具导出的卡片一起放进小红书轮播图。

复用方式（见 content/<post>/make_charts.py）：
    import rt_charts as rc
    rc.waffle(tiers, "images/chart.png", title, subtitle, note)   # 点阵图（人群构成）
    rc.tiers_bar(tiers, "images/bar.png", title)                  # 对数条形（量级悬殊）
    rc.donut(parts, "images/donut.png", title)                    # 环形占比
    rc.trend(series, "images/trend.png", title, xlabels)          # 趋势折线
    rc.compare_bars(items, "images/cmp.png", title)               # 线性对比条形
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
GRID = "#EEF0F2"
# 主题强调色序列（与 .claude/skills 设计预设对应，[0] 是默认青绿主色）
PALETTE = ["#2F9488", "#6E5AA8", "#D98E3D", "#C25E70", "#3E6FA0", "#3DA35D", "#B0573A", "#7A6A55"]


def _ensure_dir(path):
    d = os.path.dirname(os.path.abspath(path))
    if d:
        os.makedirs(d, exist_ok=True)


def _vis_w(text):
    """近似视觉宽度：全角记 1，半角记 0.55。"""
    return sum(1.0 if ord(ch) > 0x2E80 else 0.55 for ch in str(text))


def _draw_note(fig, note, w_px, dpi, x, y, fs):
    """底部注释统一绘制：按画布宽度自动折行（最多两行），避免长口径说明溢出。"""
    text = "注：" + note
    limit = (w_px - 2 * x * w_px) / (fs / 72 * dpi)  # 每行可容纳的全角字数
    if _vis_w(text) > limit:
        lines, cur, acc = [], "", 0.0
        for ch in text:
            cw = 1.0 if ord(ch) > 0x2E80 else 0.55
            if acc + cw > limit and not lines:
                lines.append(cur)
                cur, acc = "", 0.0
            cur += ch
            acc += cw
        lines.append(cur)
        text = "\n".join(lines[:2])
    fig.text(x, y, text, va="bottom", fontsize=fs, color=SUB)


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
        _draw_note(fig, note, w, dpi, x=0.07, y=0.025, fs=12)

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
        _draw_note(fig, note, w, dpi, x=0.06, y=0.03, fs=10.5)
    _ensure_dir(out)
    fig.savefig(out, dpi=dpi, facecolor="white")
    plt.close(fig)
    return out


def donut(parts, out, title, subtitle="", note="", center="", px=(1080, 1080)):
    """占比环形图：份额/构成一目了然，中心可放一句话结论。

    parts: [{'label','pct','color'(可选),'sub'(可选，图例里的小字补充)}...]
    center: 中心文案，"大字\\n小字" 用换行拆两行；缺省取最大份额 "pct%\\nlabel"。
    """
    w, h = px
    dpi = 160
    fig = plt.figure(figsize=(w / dpi, h / dpi), dpi=dpi)
    fig.patch.set_facecolor("white")
    fig.text(0.5, 0.965, title, ha="center", va="top",
             fontsize=30, fontweight="bold", color=INK)
    if subtitle:
        fig.text(0.5, 0.898, subtitle, ha="center", va="top", fontsize=13, color=SUB)

    cols = [p.get("color") or PALETTE[i % len(PALETTE)] for i, p in enumerate(parts)]
    vals = [p["pct"] for p in parts]
    ax = fig.add_axes([0.16, 0.335, 0.68, 0.55])
    ax.pie(vals, colors=cols, startangle=90, counterclock=False,
           wedgeprops={"width": 0.34, "edgecolor": "white", "linewidth": 3})
    ax.set_aspect("equal")

    if not center:
        top = max(parts, key=lambda p: p["pct"])
        center = f"{top.get('pct_label', str(top['pct']) + '%')}\n{top['label']}"
    lines = center.split("\n")
    ax.text(0, 0.10, lines[0], ha="center", va="center",
            fontsize=34, fontweight="bold", color=INK)
    if len(lines) > 1:
        ax.text(0, -0.22, lines[1], ha="center", va="center", fontsize=14, color=SUB)

    # 图例：色块 + 标签(+小字) + 百分比右对齐，与 waffle 图例同一套版式
    n = len(parts)
    y0 = 0.275
    dy = min(0.062, (y0 - 0.06) / max(1, n - 1) if n > 1 else 0.062)
    for k, (p, c) in enumerate(zip(parts, cols)):
        y = y0 - k * dy
        fig.patches.append(plt.Rectangle((0.10, y - 0.014), 0.030, 0.027,
                                         transform=fig.transFigure,
                                         facecolor=c, edgecolor="none", clip_on=False))
        label = p["label"] + (f"  ·  {p['sub']}" if p.get("sub") else "")
        fig.text(0.145, y, label, va="center", fontsize=15.5,
                 fontweight="bold", color=INK)
        fig.text(0.90, y, p.get("pct_label", f"{p['pct']}%"), va="center", ha="right",
                 fontsize=15.5, fontweight="bold", color=c)

    if note:
        _draw_note(fig, note, w, dpi, x=0.07, y=0.022, fs=11.5)
    _ensure_dir(out)
    fig.savefig(out, dpi=dpi, facecolor="white")
    plt.close(fig)
    return out


def trend(series, out, title, xlabels, subtitle="", note="", ylabel="", px=(1080, 840)):
    """趋势折线图：变化与拐点。末点自动标注数值，多条线时右端标线名。

    series: [{'label','values','color'(可选),'unit'(可选，末点标注后缀)}...]
    xlabels: 横轴刻度标签（与 values 等长）
    """
    w, h = px
    dpi = 160
    fig = plt.figure(figsize=(w / dpi, h / dpi), dpi=dpi)
    fig.patch.set_facecolor("white")
    fig.text(0.5, 0.955, title, ha="center", va="top",
             fontsize=29, fontweight="bold", color=INK)
    if subtitle:
        fig.text(0.5, 0.862, subtitle, ha="center", va="top", fontsize=13.5, color=SUB)

    # 右侧要放"末值/线名"标注，按最长标注自适应留边距（CJK 按全角宽估算），避免出图被裁
    def _est_w(t):
        return sum(1.0 if ord(ch) > 0x2E80 else 0.55 for ch in str(t))
    longest = max([_est_w(f"{s['values'][-1]}{s.get('unit', '')}") for s in series] +
                  ([_est_w(s["label"]) for s in series] if len(series) > 1 else [0]))
    char_px = 15 / 72 * dpi                      # fontsize 15 的单个全角字宽
    margin = min(0.30, max(0.10, (14 + longest * char_px + 14) / w))
    ax = fig.add_axes([0.10, 0.15, 0.90 - 0.10 - margin, 0.62])
    xs = range(len(xlabels))
    for i, s in enumerate(series):
        c = s.get("color") or PALETTE[i % len(PALETTE)]
        ax.plot(list(xs), s["values"], color=c, linewidth=3.2,
                marker="o", markersize=7, markerfacecolor="white",
                markeredgewidth=2.4, markeredgecolor=c, zorder=3, clip_on=False)
        last = s["values"][-1]
        ax.annotate(f"{last}{s.get('unit', '')}",
                    xy=(len(xlabels) - 1, last), xytext=(10, 0),
                    textcoords="offset points", va="center",
                    fontsize=15, fontweight="bold", color=c,
                    annotation_clip=False)
        if len(series) > 1:
            ax.annotate(s["label"], xy=(len(xlabels) - 1, last), xytext=(10, 18),
                        textcoords="offset points", va="center",
                        fontsize=11, color=SUB, annotation_clip=False)

    ax.set_xticks(list(xs))
    ax.set_xticklabels(xlabels, fontsize=12, color=SUB)
    ax.tick_params(axis="y", labelsize=11, colors=SUB, length=0)
    ax.tick_params(axis="x", length=0)
    for sname in ("top", "right", "left"):
        ax.spines[sname].set_visible(False)
    ax.spines["bottom"].set_color("#E6E8EB")
    ax.grid(axis="y", color=GRID, zorder=0)
    ax.margins(x=0.03)
    if ylabel:
        fig.text(0.10, 0.80, ylabel, fontsize=12, color=SUB)

    if note:
        _draw_note(fig, note, w, dpi, x=0.06, y=0.03, fs=10.5)
    _ensure_dir(out)
    fig.savefig(out, dpi=dpi, facecolor="white")
    plt.close(fig)
    return out


def compare_bars(items, out, title, subtitle="", note="", unit="", px=(1080, 840)):
    """对比条形图（线性刻度）：少量条目的直观大小对比，条端标数值。

    items: [{'label','value','text'(可选，覆盖数值标注),'color'(可选)}...]，2–6 条最佳。
    量级跨度特别大（>100 倍）时改用 tiers_bar（对数刻度）。
    """
    w, h = px
    dpi = 160
    fig = plt.figure(figsize=(w / dpi, h / dpi), dpi=dpi)
    fig.patch.set_facecolor("white")
    fig.text(0.5, 0.955, title, ha="center", va="top",
             fontsize=29, fontweight="bold", color=INK)
    if subtitle:
        fig.text(0.5, 0.862, subtitle, ha="center", va="top", fontsize=13.5, color=SUB)

    labels = [it["label"] for it in items][::-1]
    vals = [it["value"] for it in items][::-1]
    cols = [it.get("color") or PALETTE[i % len(PALETTE)]
            for i, it in enumerate(items)][::-1]
    texts = [it.get("text", f"{it['value']}{unit}") for it in items][::-1]

    ax = fig.add_axes([0.26, 0.13, 0.62, 0.66])
    y = range(len(labels))
    ax.barh(list(y), vals, color=cols, height=0.58, zorder=3)
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=14, color=INK)
    ax.tick_params(axis="y", length=0)
    ax.set_xticks([])
    for sname in ("top", "right", "left", "bottom"):
        ax.spines[sname].set_visible(False)
    ax.set_xlim(0, max(vals) * 1.22)
    for i, (v, t) in enumerate(zip(vals, texts)):
        ax.text(v + max(vals) * 0.025, i, t, va="center",
                fontsize=14, fontweight="bold", color=INK)

    if note:
        _draw_note(fig, note, w, dpi, x=0.06, y=0.03, fs=10.5)
    _ensure_dir(out)
    fig.savefig(out, dpi=dpi, facecolor="white")
    plt.close(fig)
    return out
