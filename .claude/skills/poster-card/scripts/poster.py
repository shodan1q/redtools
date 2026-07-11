"""
poster —— 精美文字海报 / 金句卡片生成（Pillow + numpy，出高清 PNG）。

输入一句话，直接产出可发布的海报卡：讲究的渐变背景 + 微噪质感 + 暗角、
字体层次分明、装饰克制（引号 / 强调线 / 署名）。6 套精调预设、3 种比例。

用法：
  python3 poster.py --text "把重复的时间还给自己" --sub "@AgentOPC" --preset 暮光
  python3 poster.py --text "越简单  越高级" --preset 墨黑金 --ratio 1:1 --quote
  python3 poster.py --text "..." --preset 极简白 --ratio 9:16 --out card.png
预设：极简白 / 暮光 / 墨黑金 / 莫兰迪 / 薄荷 / 深海
比例：3:4（小红书，默认）/ 1:1（方图）/ 9:16（故事·壁纸）
依赖：numpy、Pillow。
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ---- 预设：bg 渐变停靠色 / ink 文字 / accent 强调 / dark 是否深色 ----------
PRESETS = {
    "极简白": {"bg": [(250, 250, 247), (238, 236, 230)], "ink": (26, 26, 26), "accent": (192, 57, 43), "dark": False},
    "暮光":   {"bg": [(53, 92, 125), (108, 91, 123), (192, 108, 132)], "ink": (255, 252, 248), "accent": (255, 211, 165), "dark": True},
    "墨黑金": {"bg": [(26, 24, 22), (42, 38, 32)], "ink": (245, 240, 230), "accent": (201, 162, 75), "dark": True},
    "莫兰迪": {"bg": [(217, 202, 179), (176, 161, 143)], "ink": (58, 52, 46), "accent": (125, 110, 91), "dark": False},
    "薄荷":   {"bg": [(168, 230, 207), (86, 198, 169)], "ink": (16, 64, 59), "accent": (255, 255, 255), "dark": False},
    "深海":   {"bg": [(15, 32, 39), (32, 58, 67), (44, 83, 100)], "ink": (232, 240, 242), "accent": (78, 205, 196), "dark": True},
}
RATIOS = {"3:4": (1080, 1440), "1:1": (1080, 1080), "9:16": (1080, 1920), "4:3": (1440, 1080)}

_FONTS = ["/System/Library/Fonts/Hiragino Sans GB.ttc", "/System/Library/Fonts/PingFang.ttc",
          "/System/Library/Fonts/STHeiti Medium.ttc", "C:/Windows/Fonts/msyh.ttc",
          "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"]
_FONT = next((f for f in _FONTS if os.path.exists(f)), None)


def _font(size):
    return ImageFont.truetype(_FONT, size) if _FONT else ImageFont.load_default()


def gradient(size, stops, angle=135):
    """沿 angle 方向的多色线性渐变。"""
    W, H = size
    a = np.deg2rad(angle)
    yy, xx = np.mgrid[0:H, 0:W]
    t = (xx * np.cos(a) + yy * np.sin(a))
    t = (t - t.min()) / np.ptp(t)
    stops = np.array(stops, float)
    pos = np.linspace(0, 1, len(stops))
    img = np.stack([np.interp(t, pos, stops[:, c]) for c in range(3)], axis=-1)
    return img


def finish(arr, dark):
    """微噪 + 暗角，出质感。"""
    H, W, _ = arr.shape
    arr = arr + np.random.default_rng(0).normal(0, 4, arr.shape)      # 胶片颗粒
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W / 2))**2 + ((yy - H / 2) / (H / 2))**2)
    vig = 1 - np.clip(d - 0.6, 0, 1) * (0.28 if dark else 0.14)        # 暗角
    arr = arr * vig[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def wrap(text, font, draw, max_w):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for ch in para:
            if draw.textlength(cur + ch, font=font) > max_w and cur:
                lines.append(cur); cur = ch
            else:
                cur += ch
        lines.append(cur)
    return lines


def fit(draw, text, max_w, max_h, big):
    paras = text.split("\n")                              # 手动换行的行数
    for size in range(big, 28, -3):
        f = _font(size)
        lines = wrap(text, f, draw, max_w)
        lh = int(size * 1.42)
        # 有手动换行时，只接受"没有任何一行被再拆开"的字号，避免落单字
        no_orphan = (len(lines) == len(paras)) if len(paras) > 1 else True
        if no_orphan and len(lines) * lh <= max_h:
            return f, lines, lh, size
    f = _font(30)
    return f, wrap(text, f, draw, max_w), 44, 30


def render(text, sub="", preset="暮光", ratio="3:4", out="poster.png", quote=False, signature=""):
    p = PRESETS[preset]; W, H = RATIOS[ratio]
    img = finish(gradient((W, H), p["bg"], angle=125), p["dark"])
    dr = ImageDraw.Draw(img)
    pad = int(W * 0.12)
    ink, acc = p["ink"], p["accent"]

    # 顶部装饰引号
    top = pad
    if quote:
        qf = _font(int(W * 0.22))
        dr.text((pad - int(W * 0.01), int(H * 0.06)), "“", font=qf, fill=acc + (0,))
        dr.text((pad - int(W * 0.01), int(H * 0.06)), "“", font=qf, fill=tuple(acc))
        top = int(H * 0.20)

    # 主文案：自适应字号，竖直居中
    area_h = int(H * (0.52 if (sub or signature) else 0.6))
    f, lines, lh, size = fit(dr, text, W - 2 * pad, area_h, int(W * 0.13))
    block_h = len(lines) * lh
    y = top + (H - top - int(H * 0.16) - block_h) // 2
    sw = max(1, size // 22)
    for ln in lines:
        w = dr.textlength(ln, font=f)
        dr.text(((W - w) / 2, y), ln, font=f, fill=ink, stroke_width=sw, stroke_fill=ink)
        y += lh

    # 强调线 + 副文案
    by = y + int(H * 0.02)
    dr.line([(W / 2 - 40, by), (W / 2 + 40, by)], fill=acc, width=4)
    if sub:
        sf = _font(int(W * 0.036))
        w = dr.textlength(sub, font=sf)
        dr.text(((W - w) / 2, by + int(H * 0.03)), sub, font=sf, fill=acc)

    # 署名（右下角）
    if signature:
        gf = _font(int(W * 0.028))
        s = "— @" + signature.lstrip("@")
        w = dr.textlength(s, font=gf)
        dr.text((W - pad - w, H - pad + int(H * 0.02)), s, font=gf,
                fill=tuple(int(c * 0.85) for c in ink))

    img.save(out)
    return out


def main(argv):
    ap = argparse.ArgumentParser(description="精美文字海报 / 金句卡 → PNG")
    ap.add_argument("--text", required=True, help="主文案（用 \\n 手动换行）")
    ap.add_argument("--sub", default="", help="副文案 / 出处")
    ap.add_argument("--preset", default="暮光", choices=list(PRESETS))
    ap.add_argument("--ratio", default="3:4", choices=list(RATIOS))
    ap.add_argument("--quote", action="store_true", help="加装饰引号（金句卡）")
    ap.add_argument("--signature", default="", help="右下角署名")
    ap.add_argument("--out", default="poster.png")
    a = ap.parse_args(argv)
    render(a.text.replace("\\n", "\n"), a.sub, a.preset, a.ratio, a.out, a.quote, a.signature)
    print("✓", a.out)


if __name__ == "__main__":
    main(sys.argv[1:])
