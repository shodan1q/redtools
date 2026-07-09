"""docx_format —— 统一文档排版标准（redtools 文档家族通用）。

把任意 Markdown 或 Word 文档，套成同一套规范 Word 形态：微软雅黑正文、黑体分级标题、
数据表→三线表、安全/合规红线框加底纹、图表可读。**不管是学术报告、产品方案还是别的报告，
最终 Word 都走这里，保证"同一个格式"。** 内容一字不改，只统一排版。

用法：
    python3 pipeline/docx_format.py 报告.md                 # md → 规范 docx
    python3 pipeline/docx_format.py 方案.docx                # docx → 规范 docx（重排版，内容不动）
    python3 pipeline/docx_format.py in.md -o out.docx --line-spacing 1.5
依赖：pandoc（md 输入时需要）、python-docx。
"""
import argparse
import os
import shutil
import subprocess
import sys

from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.text import WD_LINE_SPACING

# ---- 统一格式常量（改这里 = 改全家族的文档外观）----------------------------
BODY_CJK = "微软雅黑"
BODY_LAT = "Arial"
BODY_PT = 12                     # 正文小四
HEAD_CJK = "微软雅黑"
HEAD_COLOR = RGBColor(0x1F, 0x35, 0x5E)   # 深蓝标题
HEAD_SIZES = {"Heading 1": 15, "Heading 2": 13, "Heading 3": 12}
HEADER_FILL = "F2F4F7"           # 三线表表头浅灰
REDLINE_FILL = "FDECEC"          # 红线框浅红
REDLINE_KEYS = ("●", "红线", "边界", "禁忌", "务必", "警告", "注意", "慎用", "警示")


def _set_cjk(style, west, cjk, size=None, bold=None, color=None):
    style.font.name = west
    rpr = style.element.get_or_add_rPr()
    rpr.get_or_add_rFonts().set(qn("w:eastAsia"), cjk)
    if size:
        style.font.size = Pt(size)
    if bold is not None:
        style.font.bold = bold
    if color:
        style.font.color.rgb = color


def _shade(cell, hexfill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), hexfill)
    tcPr.append(shd)


def _three_line(t):
    """去竖线，仅留顶/底粗线 + 表头下细线 = 三线表。"""
    tblPr = t._tbl.tblPr
    old = tblPr.find(qn("w:tblBorders"))
    if old is not None:
        tblPr.remove(old)
    b = OxmlElement("w:tblBorders")

    def edge(tag, sz, val="single"):
        e = OxmlElement("w:" + tag)
        e.set(qn("w:val"), val)
        e.set(qn("w:sz"), sz)
        e.set(qn("w:space"), "0")
        e.set(qn("w:color"), "000000")
        return e

    b.append(edge("top", "12"))
    b.append(edge("bottom", "12"))
    b.append(edge("insideH", "4"))
    for tag in ("left", "right", "insideV"):
        e = OxmlElement("w:" + tag)
        e.set(qn("w:val"), "none")
        b.append(e)
    tblPr.append(b)


def format_docx(path, line_spacing=1.15):
    """就地把一个 docx 套成统一格式。返回统计。"""
    doc = Document(path)

    normal = doc.styles["Normal"]
    _set_cjk(normal, BODY_LAT, BODY_CJK, BODY_PT)
    normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    normal.paragraph_format.line_spacing = line_spacing

    for name, sz in HEAD_SIZES.items():
        try:
            _set_cjk(doc.styles[name], HEAD_CJK, HEAD_CJK, sz, bold=True, color=HEAD_COLOR)
        except KeyError:
            pass

    three = box = 0
    for t in doc.tables:
        cols = len(t.columns)
        if cols == 1 and any(k in t.cell(0, 0).text for k in REDLINE_KEYS):
            _shade(t.cell(0, 0), REDLINE_FILL)          # 红线框
            box += 1
        elif cols > 1:
            _three_line(t)                               # 数据表 → 三线表
            for c in t.rows[0].cells:
                _shade(c, HEADER_FILL)
            three += 1

    doc.save(path)
    return {"tables": len(doc.tables), "three_line": three, "redline": box,
            "images": len(doc.inline_shapes),
            "headings": sum(1 for p in doc.paragraphs if p.style.name.startswith("Heading"))}


def md_to_docx(md, out):
    if not shutil.which("pandoc"):
        sys.exit("需要 pandoc 才能转换 Markdown：brew install pandoc")
    res = os.path.dirname(os.path.abspath(md)) or "."
    subprocess.run(["pandoc", md, "-o", out, "--resource-path", res], check=True)
    return out


def main(argv):
    ap = argparse.ArgumentParser(description="把 md/docx 套成统一规范 Word")
    ap.add_argument("input", help="输入 .md 或 .docx")
    ap.add_argument("-o", "--output", help="输出路径（默认 <名字>_规范版.docx）")
    ap.add_argument("--line-spacing", type=float, default=1.15,
                    help="行距，学术类建议 1.5，技术类 1.15（默认）")
    a = ap.parse_args(argv)

    base, ext = os.path.splitext(a.input)
    ext = ext.lower()
    out = a.output or (base + "_规范版.docx")

    if ext in (".md", ".markdown", ".txt"):
        md_to_docx(a.input, out)
    elif ext == ".docx":
        if os.path.abspath(a.input) != os.path.abspath(out):
            shutil.copy(a.input, out)
    else:
        sys.exit("只支持 .md 或 .docx 输入")

    st = format_docx(out, a.line_spacing)
    print("✓ 已套用统一格式（内容未改，仅排版）")
    print(f"  三线表 {st['three_line']} · 红线框 {st['redline']} · 图片 {st['images']} · 标题 {st['headings']}")
    print(f"  → {out}")


if __name__ == "__main__":
    main(sys.argv[1:])
