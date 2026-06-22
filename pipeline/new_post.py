"""
new_post —— 小红书内容生产流水线编排。

按时间归档：每篇内容一个 content/<日期>-<标题>/ 文件夹，含
    原长文.md  概述.md  meta.json  make_charts.py  images/

子命令：
    新建脚手架：
        python3 pipeline/new_post.py new "AI不会取代人类"
    构建（出数据图表 + 无头导出本工具卡片到 images/）：
        python3 pipeline/new_post.py build content/2026-06-22-ai-vs-human
"""
import datetime
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")

META_TMPL = """{{
  "title": "{title}",
  "source": "原长文.md",
  "signature": "AgentOPC",
  "themeIndex": 14,
  "ratioIndex": 0,
  "patternIndex": 7,
  "coverLayout": 1,
  "titleFontIndex": 4,
  "bodyFontIndex": 0,
  "targetPages": 9,
  "closingOn": true,
  "heroImg": "covers/photo-13.jpg",
  "_comment": "themeIndex见getThemes()顺序;patternIndex 7=数学8=物理9=化学10=计算机;coverLayout 0卡片1全屏2融入;ratioIndex 0=3:4 1=长文3:5"
}}
"""

CHARTS_TMPL = '''"""本篇数据图表。运行: python3 make_charts.py"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "pipeline"))
import rt_charts as rc

OUT = os.path.join(HERE, "images")

# 在这里填本篇的数据，然后调用 rc.waffle / rc.tiers_bar 等
TIERS = [
    # {{"label": "...", "people": "约 X", "pct": 50, "color": "#3DA35D", "value": 1, "desc": "..."}},
]

def main():
    if not TIERS:
        print("请先在 TIERS 中填入本篇数据")
        return
    rc.tiers_bar(TIERS, os.path.join(OUT, "chart-01.png"), title="{title}")
    print("图表已输出到:", OUT)

if __name__ == "__main__":
    main()
'''

OVERVIEW_TMPL = """# 概述 · {title}

- **发布日期**：{date}
- **主题**：
- **平台**：小红书（图文长文）

## 核心观点

1.

## 一句话钩子

>

## 适用人群 / 标签

#

## 产出清单
- `原长文.md`：完整长文（本工具图文排版源）
- `概述.md`：本文件
- `meta.json`：本工具生成参数
- `images/`：本工具导出的卡片 + Python 数据图表
"""


def slugify(title):
    s = re.sub(r"[\s/\\:?？！!，。、]+", "-", title.strip())
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:40] or "post"


def cmd_new(title):
    date = datetime.date.today().isoformat()
    folder = os.path.join(CONTENT, f"{date}-{slugify(title)}")
    os.makedirs(os.path.join(folder, "images"), exist_ok=True)
    _write(os.path.join(folder, "原长文.md"), title + "\n\n（在此粘贴/撰写正文。第一行即标题，空行分段，"
           "「一、」「1.」识别小标题，「- 」识别要点，**关键词** 或 【关键词】 高亮。）\n")
    _write(os.path.join(folder, "概述.md"), OVERVIEW_TMPL.format(title=title, date=date))
    _write(os.path.join(folder, "meta.json"), META_TMPL.format(title=title))
    _write(os.path.join(folder, "make_charts.py"), CHARTS_TMPL.format(title=title))
    print("已创建:", folder)
    print("下一步: 编辑 原长文.md / make_charts.py，再运行")
    print(f"  python3 pipeline/new_post.py build {os.path.relpath(folder, ROOT)}")


def cmd_build(folder):
    folder = os.path.abspath(folder)
    charts = os.path.join(folder, "make_charts.py")
    if os.path.exists(charts):
        print("== 生成数据图表 ==")
        subprocess.run([sys.executable, charts], check=False)
    print("== 无头导出本工具卡片 ==")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import export_cards
    export_cards.export(folder)


def _write(path, content):
    if os.path.exists(path):
        return
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "new":
        cmd_new(" ".join(sys.argv[2:]))
    elif len(sys.argv) == 3 and sys.argv[1] == "build":
        cmd_build(sys.argv[2])
    else:
        sys.exit(__doc__)
