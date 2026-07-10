"""
mathviz —— 通用数学图像生成（matplotlib + numpy，出 300dpi 高清 PNG）。

任何函数只要用字符串写出来就能画（sin/cos/exp/log/sqrt… 全支持），覆盖数学作图七大类：
  function   y=f(x) 函数图像（可多条）
  parametric 参数曲线 x(t),y(t)（利萨如、螺线、摆线…）
  polar      极坐标 r=f(θ)（玫瑰线、心形线…）
  contour    等高线 / 隐函数 f(x,y)=0
  surface    三维曲面 z=f(x,y)
  field      向量场 / 相图 (u(x,y), v(x,y))
  fractal    分形（曼德博 / 朱利亚集）

坐标系是"数学课本"风格：坐标轴过原点、带箭头、浅网格、等比可选。

用法（命令行，表达式用引号）：
  python3 mathviz.py function --expr "sin(x)" "0.5*x" --xlim -6.28 6.28 --title "正弦与直线"
  python3 mathviz.py parametric --x "cos(3*t)" --y "sin(2*t)" --trange 0 6.2832
  python3 mathviz.py polar --r "1+cos(t)"            # 心形线
  python3 mathviz.py contour --f "x**2+y**2-4" --xlim -3 3 --ylim -3 3   # 隐函数=0 的圆
  python3 mathviz.py surface --z "sin(sqrt(x**2+y**2))" --xlim -6 6 --ylim -6 6
  python3 mathviz.py field --u "-y" --v "x" --xlim -3 3 --ylim -3 3       # 旋转场
  python3 mathviz.py fractal --kind mandelbrot
也可 `import mathviz` 直接调用同名函数。依赖：numpy、matplotlib。
"""
import argparse
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

# ---- 中文字体 --------------------------------------------------------------
for _p in ["/System/Library/Fonts/Hiragino Sans GB.ttc", "/System/Library/Fonts/STHeiti Medium.ttc",
           "C:/Windows/Fonts/msyh.ttc", "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"]:
    if os.path.exists(_p):
        try:
            fm.fontManager.addfont(_p)
            plt.rcParams["font.sans-serif"] = [fm.FontProperties(fname=_p).get_name(), "DejaVu Sans"]
            break
        except Exception:
            pass
plt.rcParams["axes.unicode_minus"] = False

INK, ACCENT = "#1F2329", "#2F6BB0"
PALETTE = ["#2F6BB0", "#C0392B", "#2E8B57", "#8E44AD", "#D68910", "#16A085"]

# 安全 eval 命名空间：numpy 数学函数 + 常量
_NS = {k: getattr(np, k) for k in
       ("sin cos tan arcsin arccos arctan arctan2 sinh cosh tanh exp log log10 log2 "
        "sqrt abs sign floor ceil power maximum minimum where real imag angle pi e "
        "cbrt hypot").split()}
_NS["abs"] = np.abs


def _ev(expr, **vars):
    return eval(expr, {"__builtins__": {}}, {**_NS, **vars})


def _new(figsize=(7, 6), title=""):
    fig, ax = plt.subplots(figsize=figsize, dpi=300)
    if title:
        ax.set_title(title, fontsize=15, fontweight="bold", color=INK, pad=12)
    return fig, ax


def _math_axes(ax, equal=False):
    """课本风：坐标轴过原点 + 箭头 + 浅网格。"""
    ax.spines["left"].set_position("zero")
    ax.spines["bottom"].set_position("zero")
    ax.spines["right"].set_color("none")
    ax.spines["top"].set_color("none")
    ax.spines["left"].set_color("#555"); ax.spines["bottom"].set_color("#555")
    ax.plot(1, 0, ">k", ms=6, transform=ax.get_yaxis_transform(), clip_on=False)
    ax.plot(0, 1, "^k", ms=6, transform=ax.get_xaxis_transform(), clip_on=False)
    ax.grid(True, color="#E6E8EB", lw=0.7)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=10, colors="#555")
    if equal:
        ax.set_aspect("equal")


def _save(fig, out):
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


def function(exprs, out="fn.png", xlim=(-6.283, 6.283), title="", n=1600):
    fig, ax = _new(title=title)
    x = np.linspace(xlim[0], xlim[1], n)
    for i, ex in enumerate(exprs):
        y = _ev(ex, x=x).astype(float)
        y[np.abs(np.gradient(y)) > (np.nanmax(y) - np.nanmin(y) or 1) * 0.4] = np.nan  # 断点断开
        ax.plot(x, y, color=PALETTE[i % len(PALETTE)], lw=2.2, label=f"$y={ex}$")
    ax.set_xlim(xlim)
    _math_axes(ax)
    ax.legend(fontsize=11, framealpha=0.9, loc="best")
    return _save(fig, out)


def parametric(x_expr, y_expr, out="param.png", trange=(0, 6.283), title="", n=3000):
    fig, ax = _new(title=title)
    t = np.linspace(trange[0], trange[1], n)
    ax.plot(_ev(x_expr, t=t), _ev(y_expr, t=t), color=ACCENT, lw=2)
    _math_axes(ax, equal=True)
    return _save(fig, out)


def polar(r_expr, out="polar.png", trange=(0, 6.283), title="", n=3000):
    fig, ax = _new(title=title)
    t = np.linspace(trange[0], trange[1], n)
    r = _ev(r_expr, t=t)
    ax.plot(r * np.cos(t), r * np.sin(t), color="#8E44AD", lw=2)
    _math_axes(ax, equal=True)
    return _save(fig, out)


def contour(f_expr, out="contour.png", xlim=(-3, 3), ylim=(-3, 3), title="", filled=True, n=400):
    fig, ax = _new(figsize=(7, 6), title=title)
    xs = np.linspace(*xlim, n); ys = np.linspace(*ylim, n)
    X, Y = np.meshgrid(xs, ys)
    Z = _ev(f_expr, x=X, y=Y)
    if filled:
        cf = ax.contourf(X, Y, Z, levels=20, cmap="RdBu_r")
        fig.colorbar(cf, ax=ax, shrink=0.85)
    ax.contour(X, Y, Z, levels=[0], colors="k", linewidths=2)   # f=0 曲线
    ax.set_aspect("equal")
    ax.tick_params(labelsize=10)
    return _save(fig, out)


def surface(z_expr, out="surface.png", xlim=(-6, 6), ylim=(-6, 6), title="", n=120):
    fig = plt.figure(figsize=(8, 6.5), dpi=300)
    ax = fig.add_subplot(111, projection="3d")
    xs = np.linspace(*xlim, n); ys = np.linspace(*ylim, n)
    X, Y = np.meshgrid(xs, ys)
    Z = _ev(z_expr, x=X, y=Y)
    ax.plot_surface(X, Y, Z, cmap="viridis", linewidth=0, antialiased=True, rcount=n, ccount=n)
    if title:
        ax.set_title(title, fontsize=15, fontweight="bold", pad=8)
    ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_zlabel("z")
    return _save(fig, out)


def field(u_expr, v_expr, out="field.png", xlim=(-3, 3), ylim=(-3, 3), title="", n=22):
    fig, ax = _new(figsize=(7, 6), title=title)
    xs = np.linspace(*xlim, n); ys = np.linspace(*ylim, n)
    X, Y = np.meshgrid(xs, ys)
    U, V = _ev(u_expr, x=X, y=Y) + 0 * X, _ev(v_expr, x=X, y=Y) + 0 * Y
    M = np.hypot(U, V)
    ax.streamplot(X, Y, U, V, color=M, cmap="viridis", density=1.2, linewidth=1)
    _math_axes(ax, equal=True)
    ax.set_xlim(xlim); ax.set_ylim(ylim)
    return _save(fig, out)


def fractal(out="fractal.png", kind="mandelbrot", n=1000, iters=200, title=""):
    if kind == "julia":
        x = np.linspace(-1.6, 1.6, n); y = np.linspace(-1.6, 1.6, n)
        X, Y = np.meshgrid(x, y)
        Z = X + 1j * Y
        C = np.full(X.shape, complex(-0.8, 0.156))
    else:
        x = np.linspace(-2.2, 0.8, n); y = np.linspace(-1.5, 1.5, n)
        X, Y = np.meshgrid(x, y)
        Z = np.zeros_like(X, complex)
        C = X + 1j * Y
    out_it = np.zeros(X.shape)
    m = np.ones(X.shape, bool)                          # 仍在迭代的点
    for i in range(iters):
        Z[m] = Z[m] ** 2 + C[m]
        esc = np.abs(Z) > 2
        out_it[esc & m] = i
        m &= ~esc
    fig, ax = _new(figsize=(7, 7), title=title)
    ax.imshow(out_it ** 0.4, cmap="twilight_shifted", extent=[x[0], x[-1], y[0], y[-1]])
    ax.axis("off")
    return _save(fig, out)


def main(argv):
    ap = argparse.ArgumentParser(description="通用数学图像 → PNG")
    ap.add_argument("kind", choices=["function", "parametric", "polar", "contour",
                                     "surface", "field", "fractal"])
    ap.add_argument("--expr", nargs="+", help="function: 一个或多个 y=f(x) 表达式")
    ap.add_argument("--x"); ap.add_argument("--y"); ap.add_argument("--r")
    ap.add_argument("--f"); ap.add_argument("--z"); ap.add_argument("--u"); ap.add_argument("--v")
    ap.add_argument("--xlim", type=float, nargs=2, default=[-6.283, 6.283])
    ap.add_argument("--ylim", type=float, nargs=2, default=[-3, 3])
    ap.add_argument("--trange", type=float, nargs=2, default=[0, 6.283])
    ap.add_argument("--fractal-kind", dest="fkind", default="mandelbrot",
                    choices=["mandelbrot", "julia"])
    ap.add_argument("--title", default="")
    ap.add_argument("--out", default=None)
    ap.add_argument("--open-contour", dest="filled", action="store_false")
    a = ap.parse_args(argv)
    o = a.out or f"math-{a.kind}.png"
    if a.kind == "function":
        function(a.expr or ["sin(x)"], o, tuple(a.xlim), a.title)
    elif a.kind == "parametric":
        parametric(a.x or "cos(3*t)", a.y or "sin(2*t)", o, tuple(a.trange), a.title)
    elif a.kind == "polar":
        polar(a.r or "1+cos(t)", o, tuple(a.trange), a.title)
    elif a.kind == "contour":
        contour(a.f or "x**2+y**2-4", o, tuple(a.xlim), tuple(a.ylim), a.title, a.filled)
    elif a.kind == "surface":
        surface(a.z or "sin(sqrt(x**2+y**2))", o, tuple(a.xlim), tuple(a.ylim), a.title)
    elif a.kind == "field":
        field(a.u or "-y", a.v or "x", o, tuple(a.xlim), tuple(a.ylim), a.title)
    else:
        fractal(o, a.fkind, title=a.title)
    print("✓", o)


if __name__ == "__main__":
    main(sys.argv[1:])
