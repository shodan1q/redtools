"""
make_figure —— 发表级学术插图（matplotlib，300 dpi）。

图表规则移植自 Anthropic Claude Science 的 figure-style 技能（Apache-2.0），
适配为独立可运行 + 中文字体。核心标准：
  · 三档字号阶梯（标题/图例/刻度），按角色不按空间（§5.2）
  · 开放边框（只留左、下轴线）、刻度朝外、无边框图例（§3）
  · 焦点色主导、其余灰化——对比即观点（§4.2 focal_palette）
  · 小样本用点+中位数刻度，不用条形（§6.1 strip_with_median）
  · 误差条用 t 分布 95%CI（小样本正确，§6.1 bar_with_points）
  · 折线在末端直标，不用图例框（§6.3 end_of_line_labels）
  · 标题写结论（claim-title），坐标轴用大白话（§1/§5.6）
  · 300 dpi、字体内嵌（Type-42）、渲染后自检文字不重叠（§9）

复用：
    import make_figure as mf
    mf.apply_figure_style()
    fig, ax = mf.new_figure("坚持组六周后明显领先", "每周测验均分 · 模拟数据")
    mf.line_series(ax, x, {"坚持组": y1, "对照组": y2})   # 末端直标
    mf.save(fig, "fig1.png")
自检： python3 make_figure.py --demo out.png
依赖：matplotlib（必需）、numpy（条形/散点）、scipy（可选，ci95 更精确）。
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt

META_GREY = "#888888"

# ---- 中文字体：注册系统 CJK 字体，供 sans-serif 使用 -------------------------
_CJK_CANDIDATES = [
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]


def _cjk_family():
    from matplotlib import font_manager as fm
    for p in _CJK_CANDIDATES:
        if os.path.exists(p):
            try:
                fm.fontManager.addfont(p)
                return fm.FontProperties(fname=p).get_name()
            except Exception:
                continue
    return None


_CJK = _cjk_family()


def apply_figure_style(*, frame="open", sizes=(8, 7, 6), grid=False, cjk=True):
    """设发表级 rcParams（画图前调一次）。移植 figure-style::apply_figure_style。

    frame : 'open'(左下轴线，默认) | 'boxed'(四框) | 'none'
    sizes : (base, secondary, tick) = 标题/轴标/系列名, 图例/标注, 刻度 —— 至多三档
    grid  : 是否画网格（默认否）
    cjk   : 是否把中文字体放进 sans-serif 首位
    """
    if frame not in ("open", "boxed", "none"):
        raise ValueError("frame must be 'open'|'boxed'|'none'")
    base, secondary, tick = sizes
    boxed = frame == "boxed"
    rc = {
        "font.family": "sans-serif",
        "font.size": base, "axes.labelsize": base, "axes.titlesize": base,
        "legend.fontsize": secondary, "xtick.labelsize": tick, "ytick.labelsize": tick,
        "axes.linewidth": 0.6,
        "xtick.direction": "out", "ytick.direction": "out",
        "xtick.major.size": 3, "ytick.major.size": 3,
        "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "axes.spines.top": boxed, "axes.spines.right": boxed,
        "axes.spines.left": frame != "none", "axes.spines.bottom": frame != "none",
        "axes.grid": bool(grid), "legend.frameon": False,
        "figure.dpi": 200, "savefig.dpi": 300, "savefig.bbox": "tight",
        "axes.titleweight": "normal", "axes.titlelocation": "left",
        "axes.labelweight": "normal", "lines.linewidth": 1.4, "patch.linewidth": 0.6,
        "pdf.fonttype": 42, "ps.fonttype": 42, "axes.unicode_minus": False,
    }
    if cjk and _CJK:
        rc["font.sans-serif"] = [_CJK, "DejaVu Sans", "Arial"]
    mpl.rcParams.update(rc)


def set_frame(ax, style="open"):
    show = {"open": (False, False, True, True), "boxed": (True, True, True, True),
            "none": (False, False, False, False)}[style]
    for side, vis in zip(("top", "right", "bottom", "left"), show):
        ax.spines[side].set_visible(vis)
        if vis:
            ax.spines[side].set_linewidth(0.6)
    ax.tick_params(direction="out", length=0 if style == "none" else 3, width=0.6)


def new_figure(claim_title, subtitle="", figsize=(6.2, 4.0)):
    """建图并写**结论式标题**（claim-title，左对齐）+ 口径副标题。"""
    apply_figure_style()
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_title(claim_title, loc="left", pad=18 if subtitle else 8, fontweight="bold")
    if subtitle:
        ax.text(0, 1.02, subtitle, transform=ax.transAxes, fontsize=mpl.rcParams["legend.fontsize"],
                color=META_GREY, ha="left", va="bottom")
    return fig, ax


def panel_letter(ax, letter, dx=-0.16, dy=1.02, case="lower"):
    fs = mpl.rcParams.get("font.size", 8) + 1
    s = letter.lower() if case == "lower" else letter.upper()
    ax.text(dx, dy, s, transform=ax.transAxes, fontweight="bold", fontsize=fs, va="bottom", ha="left")


def focal_palette(labels, focal, focal_color="#2F6BB0", other="muted", base_colors=None):
    """§4.2：焦点系列高饱和主色，其余灰化/降饱和。对比即观点。"""
    import matplotlib.colors as mcolors
    focal_set = {focal} if isinstance(focal, str) else set(focal)
    n = len(labels)
    if not focal_set & set(labels):
        raise ValueError(f"focal {focal!r} not in labels")
    if base_colors is None:
        base_colors = ["#4C4C4C"] * n
    base_colors = [base_colors[i % len(base_colors)] for i in range(n)]
    if other == "grey":
        rest = ["#BCBCBC"] * n
    else:  # muted
        def mute(c):
            r, g, b = mcolors.to_rgb(c)
            m = (r + g + b) / 3
            return mcolors.to_hex((0.3 * r + 0.7 * m, 0.3 * g + 0.7 * m, 0.3 * b + 0.7 * m))
        rest = [mute(c) for c in base_colors]
    return [focal_color if l in focal_set else rest[i] for i, l in enumerate(labels)]


def bar_with_points(ax, x, ymat, labels, colors, jitter=0.08, show_points=True,
                    errorbar=None, point_alpha=0.5, point_size=9, unit=""):
    """§6.1：条=均值；叠原始点，或（show_points=False 时）画误差条。
    errorbar: None|'sd'|'ci95'（ci95 用 t 分布，小样本正确）。"""
    import numpy as np
    means = np.array([np.mean(y) for y in ymat], float)
    err = None
    if errorbar and not show_points:
        if errorbar == "sd":
            err = np.array([np.std(y, ddof=1) if np.size(y) > 1 else 0 for y in ymat])
        elif errorbar == "ci95":
            try:
                from scipy.stats import t
                def hw(y):
                    n = np.size(y)
                    return t.ppf(0.975, n - 1) * np.std(y, ddof=1) / np.sqrt(n) if n > 1 else 0
            except ImportError:
                def hw(y):
                    n = np.size(y)
                    return 1.96 * np.std(y, ddof=1) / np.sqrt(n) if n > 1 else 0
            err = np.array([hw(y) for y in ymat])
    ax.bar(x, means, color=colors, width=0.7, edgecolor="none",
           yerr=err, error_kw={"elinewidth": 0.8, "capsize": 0})
    if show_points:
        for xi, ys in zip(x, ymat):
            ys = np.asarray(ys)
            if ys.ndim and ys.size > 1:
                jit = (np.random.RandomState(0).rand(ys.size) - 0.5) * 2 * jitter
                ax.scatter(np.full(ys.size, xi) + jit, ys, s=point_size, color="black",
                           alpha=point_alpha, zorder=3, linewidths=0)
    else:
        for xi, m in zip(x, means):
            ax.text(xi, m, f" {round(m, 2)}{unit}", ha="center", va="bottom",
                    fontsize=mpl.rcParams["legend.fontsize"], fontweight="bold")
    ax.set_xticks(list(x)); ax.set_xticklabels(labels)
    ax.set_ylim(bottom=0)          # §3.1 条形必须从 0 起
    return ax


def strip_with_median(ax, groups, values, colors=None, jitter=0.12):
    """§6.1：小样本 → 抖动散点 + 加粗中位数刻度（不要条形）。"""
    import numpy as np
    labs = list(groups)
    colors = colors or ["#4C4C4C"] * len(labs)
    for i, (ys, c) in enumerate(zip(values, colors)):
        ys = np.asarray(ys)
        jit = (np.random.RandomState(i).rand(ys.size) - 0.5) * 2 * jitter
        ax.scatter(np.full(ys.size, i) + jit, ys, s=11, color=c, alpha=0.6, linewidths=0, zorder=2)
        m = np.median(ys)
        ax.plot([i - 0.22, i + 0.22], [m, m], color="black", lw=1.6, zorder=3)
    ax.set_xticks(range(len(labs))); ax.set_xticklabels(labs)
    return ax


def line_series(ax, x, series, direct_label=True, palette=None):
    """折线；多条时末端直标系列名（§6.3），不使用图例框。
    series: {名称: [值...]}。"""
    palette = palette or ["#2F6BB0", "#B0573A", "#3D8A6B", "#8A6AA8", "#6B6B6B"]
    names = list(series)
    for i, name in enumerate(names):
        c = palette[i % len(palette)]
        ax.plot(x, series[name], color=c, marker="o", ms=4.5, mfc="white",
                mec=c, mew=1.5, zorder=3, clip_on=False, label=name)
    if direct_label and len(names) >= 1:
        span = (ax.get_xlim()[1] - ax.get_xlim()[0]) or 1
        for i, name in enumerate(names):
            c = palette[i % len(palette)]
            ax.text(x[-1] + 0.012 * span, series[name][-1], name, color=c,
                    va="center", ha="left", fontsize=mpl.rcParams["font.size"],
                    fontweight="bold", clip_on=False)
        ax.margins(x=0.06)
    return ax


def goodness_arrow(ax, text="越高越好", loc="upper left", axis="y"):
    """§3.6：坐标不含方向含义时，角落放一个'越高越好'的朝向提示。"""
    pos = {"upper left": (0.02, 0.98), "upper right": (0.98, 0.98),
           "lower left": (0.02, 0.02), "lower right": (0.98, 0.02)}[loc]
    ha = "left" if "left" in loc else "right"
    va = "top" if "upper" in loc else "bottom"
    arrow = "↑ " if axis == "y" else "→ "
    ax.text(pos[0], pos[1], arrow + text, transform=ax.transAxes,
            fontsize=mpl.rcParams["legend.fontsize"], color=META_GREY, ha=ha, va=va)


def verify_overlaps(fig):
    """§9：渲染后自检——返回**标注级**文字互相重叠的对（应为空）。
    刻度标签由 matplotlib 自动布局、不参与判定（按 id 与字符串双重排除）。"""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    import matplotlib.text as mtext
    tick_ids, tick_strs = set(), set()
    for ax in fig.axes:
        for t in list(ax.get_xticklabels()) + list(ax.get_yticklabels()):
            tick_ids.add(id(t))
            s = (t.get_text() or "").strip()
            if s:
                tick_strs.add(s)
    cand = []
    for ax in fig.axes:
        for t in ax.findobj(mtext.Text):
            s = (t.get_text() or "").strip()
            if not s or id(t) in tick_ids or s in tick_strs:
                continue
            try:
                bb = t.get_window_extent(r)
            except Exception:
                continue
            if bb.width < 1 or bb.height < 1:      # 退化框跳过
                continue
            cand.append((s, bb))
    bad = []
    for i in range(len(cand)):
        for j in range(i + 1, len(cand)):
            if cand[i][1].overlaps(cand[j][1]):
                bad.append((cand[i][0][:12], cand[j][0][:12]))
    return bad


def save(fig, path):
    fig = fig.figure if hasattr(fig, "figure") else fig
    bad = verify_overlaps(fig)
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    if bad:
        sys.stderr.write(f"⚠ 文字重叠自检未过（{len(bad)} 处），建议增大 figsize 或减少标注：{bad[:3]}\n")
    return path


if __name__ == "__main__":
    if "--demo" in sys.argv:
        out = next((a for a in sys.argv if a.endswith(".png")), "demo.png")
        fig, ax = new_figure("坚持组六周后明显领先", "每周测验均分 · 模拟数据")
        line_series(ax, list(range(1, 7)),
                    {"坚持组": [55, 58, 64, 71, 76, 83], "对照组": [54, 55, 53, 56, 55, 57]})
        ax.set_xticks(range(1, 7)); ax.set_xticklabels([f"第{i}周" for i in range(1, 7)])
        ax.set_xlabel("周次"); ax.set_ylabel("测验均分")
        goodness_arrow(ax, "越高越好")
        save(fig, out)
        print("✓ 自检图（发表级标准）：", out)
    else:
        print(__doc__)
