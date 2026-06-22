"""
export_cards —— 用 Playwright 无头驱动 redtools，导出某篇内容的全部图文卡片。

读取 content/<post>/ 下的 meta.json 与原长文 md，注入 redtools 的无头桥接
(window.RT_CONFIG)，逐张导出 PNG 到 content/<post>/images/card-NN.png。

用法：
    python3 pipeline/export_cards.py content/2026-06-22-ai-vs-human
依赖：pip install playwright && playwright install chromium
"""
import base64
import functools
import http.server
import json
import os
import socket
import sys
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # redtools 项目根
# 仅这些键会传给 redtools 状态（其余 meta 字段忽略）
STATE_KEYS = {
    "raw", "signature", "themeIndex", "ratioIndex", "patternIndex", "coverLayout",
    "titleFontIndex", "bodyFontIndex", "targetPages", "closingOn", "dedication",
    "heroImg", "customColor", "customBg",
}


def _free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def _serve(root, port):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=root)
    httpd = http.server.HTTPServer(("127.0.0.1", port), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd


def export(content_dir):
    content_dir = os.path.abspath(content_dir)
    meta = json.load(open(os.path.join(content_dir, "meta.json"), encoding="utf-8"))
    raw = open(os.path.join(content_dir, meta.get("source", "原长文.md")), encoding="utf-8").read()

    cfg = {k: v for k, v in meta.items() if k in STATE_KEYS}
    cfg["raw"] = raw
    out_dir = os.path.join(content_dir, "images")
    os.makedirs(out_dir, exist_ok=True)

    port = _free_port()
    httpd = _serve(ROOT, port)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("缺少 playwright：pip install playwright && playwright install chromium")

    saved = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(device_scale_factor=2, viewport={"width": 1400, "height": 1000})
        page.add_init_script("window.RT_CONFIG = " + json.dumps(cfg, ensure_ascii=False) + ";")
        page.goto(f"http://127.0.0.1:{port}/index.html", wait_until="networkidle")
        page.wait_for_function("window.RT_READY === true", timeout=30000)
        try:
            page.wait_for_function("document.fonts && document.fonts.status === 'loaded'", timeout=15000)
        except Exception:
            pass
        page.wait_for_timeout(1200)  # 等字体就绪后的重新分页(regen)稳定
        n = page.evaluate("window.RT_PAGE_COUNT()")
        print(f"共 {n} 张，导出中…")
        for i in range(n):
            data_url = page.evaluate("async (i) => await window.RT_EXPORT_DATAURL(i)", i)
            if not data_url:
                print(f"  第 {i+1} 张导出失败，跳过")
                continue
            b64 = data_url.split(",", 1)[1]
            fn = os.path.join(out_dir, f"card-{i+1:02d}.png")
            with open(fn, "wb") as f:
                f.write(base64.b64decode(b64))
            saved.append(fn)
            print(f"  ✓ card-{i+1:02d}.png")
        browser.close()
    httpd.shutdown()
    print(f"完成：{len(saved)} 张卡片 → {out_dir}")
    return saved


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("用法: python3 pipeline/export_cards.py content/<日期-标题>")
    export(sys.argv[1])
