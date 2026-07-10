"""
art —— 生成式算法艺术（numpy + Pillow，直接出高清 PNG，无需浏览器）。

方法论借鉴 Anthropic 的 algorithmic-art 技能（Apache-2.0）：不画具体图形，而是让
美学从算法过程中"涌现"——每换一个种子就得到独一无二的一张。适合做小红书封面/背景。

四种风格：
  flow    有机湍流·流场      —— 上千粒子沿噪声力场流动，织出丝线纹理
  wave    量子谐波·波干涉    —— 多波源叠加干涉，呼吸般的斑纹场
  cells   随机结晶·Voronoi   —— 随机点长成细胞镶嵌
  tree    递归低语·分形树    —— L 系统式递归枝桠

用法：
    python3 art.py flow                      # 出一张流场（默认调色板、随机种子）
    python3 art.py wave --palette 赛博落日 --seed 7 --out a.png
    python3 art.py all                       # 四种各出一张
配色：深海霓虹 / 赛博落日 / 松石森林 / 莫兰迪雾（--palette）
依赖：numpy、Pillow。
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

# 调色板：bg 背景，stops 渐变色（低→高）
PALETTES = {
    "深海霓虹": {"bg": (6, 8, 14), "stops": [(64, 224, 208), (120, 140, 255), (255, 64, 160)]},
    "赛博落日": {"bg": (20, 8, 34), "stops": [(255, 122, 0), (255, 61, 129), (157, 78, 221)]},
    "松石森林": {"bg": (6, 18, 15), "stops": [(46, 230, 160), (30, 160, 170), (200, 240, 210)]},
    "莫兰迪雾": {"bg": (43, 43, 51), "stops": [(196, 164, 132), (150, 160, 170), (222, 210, 196)]},
}


def _ramp(stops, t):
    """在多色停靠点间线性取色，t∈[0,1]，返回 (3,) 或 (...,3)。"""
    stops = np.array(stops, float)
    t = np.clip(t, 0, 1) * (len(stops) - 1)
    i = np.floor(t).astype(int)
    i = np.clip(i, 0, len(stops) - 2)
    f = (t - i)[..., None]
    return stops[i] * (1 - f) + stops[i + 1] * f


def flow(seed, pal, S=1400, n=4200, steps=200):
    rng = np.random.default_rng(seed)
    F = np.fft.fft2(rng.standard_normal((S, S)))
    fy = np.fft.fftfreq(S)[:, None]; fx = np.fft.fftfreq(S)[None, :]
    r = np.sqrt(fx**2 + fy**2)
    fld = np.real(np.fft.ifft2(F * np.exp(-(r / 0.005)**2)))
    ang = (fld - fld.min()) / np.ptp(fld) * 2 * np.pi * 3
    buf = np.zeros((S, S, 3))
    px = rng.uniform(0, S, n); py = rng.uniform(0, S, n)
    for s in range(steps):
        a = ang[np.clip(py.astype(int), 0, S - 1), np.clip(px.astype(int), 0, S - 1)]
        px += np.cos(a) * 1.5; py += np.sin(a) * 1.5
        col = _ramp(pal["stops"], s / steps) / 255.0
        m = (px >= 0) & (px < S) & (py >= 0) & (py < S)
        np.add.at(buf, (py[m].astype(int), px[m].astype(int)), col * 0.05)
    img = np.array(pal["bg"]) / 255.0 + (1 - np.exp(-buf * 1.5))
    return _to_img(img)


def wave(seed, pal, S=1400, sources=8):
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:S, 0:S].astype(float)
    acc = np.zeros((S, S))
    for _ in range(sources):
        d = np.sqrt((x - rng.uniform(0, S))**2 + (y - rng.uniform(0, S))**2)
        acc += np.sin(d * rng.uniform(0.03, 0.07) + rng.uniform(0, 6.28))
    acc = (acc - acc.min()) / np.ptp(acc)
    img = _ramp([pal["bg"]] + pal["stops"], acc) / 255.0
    return _to_img(img ** 0.85)


def cells(seed, pal, S=1400, k=48):
    rng = np.random.default_rng(seed)
    pts = rng.uniform(0, S, (k, 2))
    y, x = np.mgrid[0:S, 0:S].astype(float)
    best = np.full((S, S), 1e18); who = np.zeros((S, S), int); second = np.full((S, S), 1e18)
    for i, (cx, cy) in enumerate(pts):
        d = (x - cx)**2 + (y - cy)**2
        upd = d < best
        second = np.where(upd, best, np.minimum(second, d))
        who = np.where(upd, i, who); best = np.minimum(best, d)
    t = (pts[who, 0] + pts[who, 1]) / (2 * S)          # 按点位置取色
    img = _ramp([pal["bg"]] + pal["stops"], t) / 255.0
    edge = (np.sqrt(second) - np.sqrt(best)) < 3        # 细胞边界描暗线
    img[edge] *= 0.35
    return _to_img(img)


def tree(seed, pal, S=1400, depth=11):
    rng = np.random.default_rng(seed)
    img = Image.new("RGB", (S, S), pal["bg"])
    dr = ImageDraw.Draw(img)

    def branch(x, y, ang, ln, d):
        if d > depth or ln < 3:
            return
        x2 = x + np.cos(ang) * ln; y2 = y - np.sin(ang) * ln
        c = tuple(int(v) for v in _ramp(pal["stops"], d / depth))
        dr.line([x, y, x2, y2], fill=c, width=max(1, int(depth - d) // 2))
        spread = 0.45 + rng.uniform(-0.1, 0.1)
        branch(x2, y2, ang + spread + rng.uniform(-0.2, 0.2), ln * 0.78, d + 1)
        branch(x2, y2, ang - spread + rng.uniform(-0.2, 0.2), ln * 0.78, d + 1)
        if rng.random() < 0.25:
            branch(x2, y2, ang + rng.uniform(-0.15, 0.15), ln * 0.7, d + 1)

    for base in (0.5, 0.22, 0.78):                      # 几株并立
        branch(S * base, S * 0.98, np.pi / 2 + rng.uniform(-0.2, 0.2), S * 0.16, 0)
    return img


def _to_img(arr):
    return Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))


STYLES = {"flow": flow, "wave": wave, "cells": cells, "tree": tree}


def main(argv):
    ap = argparse.ArgumentParser(description="生成式算法艺术 → PNG")
    ap.add_argument("style", choices=list(STYLES) + ["all"])
    ap.add_argument("--palette", default="深海霓虹", choices=list(PALETTES))
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=None)
    ap.add_argument("--size", type=int, default=1400)
    a = ap.parse_args(argv)
    pal = PALETTES[a.palette]
    styles = list(STYLES) if a.style == "all" else [a.style]
    for st in styles:
        out = a.out or f"art-{st}-{a.palette}-{a.seed}.png"
        if a.style == "all":
            out = f"art-{st}.png"
        STYLES[st](a.seed, pal, S=a.size).save(out)
        print("✓", out)


if __name__ == "__main__":
    main(sys.argv[1:])
