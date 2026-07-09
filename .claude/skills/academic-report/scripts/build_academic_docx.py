"""
build_academic_docx —— 把结构化 Markdown 生成为发表级中文学术报告 .docx。

产出符合中文学术规范的 Word：封面（标题/副标题/作者机构）、可选目录、
正文宋体小四·1.5 倍行距·**首行缩进 2 字符**、标题黑体分级、数据表→**三线表**、
图/表**居中带编号题注**、参考文献**悬挂缩进**。内容一字不改，只做规范排版。

用法：
    python3 build_academic_docx.py report.md -o report.docx \
        --title "标题" --subtitle "副标题" --author "张三 / 某某大学" --toc
依赖：pandoc（Markdown→docx 基础转换）、python-docx（排版）。

Markdown 约定（让排版更准确）：
  # 一级标题   ## 二级   ### 三级
  图片单独成行： ![](fig1.png)      下一行写题注： 图1 降温曲线（示例）
  表格题注写在表格上方一行： 表1 参数窗口
  摘要段落以「摘要」或「Abstract」开头
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.text import WD_LINE_SPACING, WD_ALIGN_PARAGRAPH, WD_BREAK

# ---- 中文学术默认（改这里=改风格）------------------------------------------
BODY_CJK, BODY_LAT, BODY_PT = "宋体", "Times New Roman", 12          # 正文小四
HEAD_CJK = "黑体"
HEAD_COLOR = RGBColor(0x1A, 0x1A, 0x1A)
HEAD_SIZES = {"Heading 1": 15, "Heading 2": 13.5, "Heading 3": 12}
CAPTION_PT = 10.5
HEADER_FILL = "F2F2F2"
CAPTION_PREFIX = ("图", "表", "Figure", "Table", "Fig.")


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


def _run_cjk(run, west, cjk):
    run.font.name = west
    rpr = run._element.get_or_add_rPr()
    rpr.get_or_add_rFonts().set(qn("w:eastAsia"), cjk)


def _shade(cell, hexfill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), hexfill)
    tcPr.append(shd)


def _three_line(t):
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


def _has_image(p):
    return bool(p._p.findall(".//" + qn("w:drawing"))) or bool(
        p._p.findall(".//" + qn("w:object")))


def _is_caption(text):
    t = text.strip()
    return any(t.startswith(pre) and any(c.isdigit() for c in t[:6])
               for pre in CAPTION_PREFIX)


def _add_toc(anchor):
    """在 anchor 前插入一个 Word 目录域（打开后按 F9 / 更新域即生成）。"""
    p = anchor.insert_paragraph_before()
    run = p.add_run()
    for tag, attrs, txt in [
        ("w:fldChar", {"w:fldCharType": "begin"}, None),
        ("w:instrText", {"xml:space": "preserve"}, r' TOC \o "1-3" \h \z \u '),
        ("w:fldChar", {"w:fldCharType": "separate"}, None),
        ("w:t", {}, "目录将在 Word 中按“更新域”生成"),
        ("w:fldChar", {"w:fldCharType": "end"}, None),
    ]:
        el = OxmlElement(tag)
        for k, v in attrs.items():
            el.set(qn(k), v)
        if txt:
            el.text = txt
        run._element.append(el)
    brk = anchor.insert_paragraph_before()          # 目录后分页，正文从新页开始
    brk.add_run().add_break(WD_BREAK.PAGE)


def _build_cover(anchor, title, subtitle, author):
    def add(text, size, bold=False, color=None, space_after=6, cjk=HEAD_CJK):
        p = anchor.insert_paragraph_before()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(space_after)
        r = p.add_run(text)
        r.font.size = Pt(size)
        r.font.bold = bold
        if color:
            r.font.color.rgb = color
        _run_cjk(r, BODY_LAT, cjk)
        return p

    for _ in range(4):
        anchor.insert_paragraph_before()
    add(title, 24, bold=True)
    if subtitle:
        add(subtitle, 15, color=RGBColor(0x55, 0x55, 0x55))
    for _ in range(6):
        anchor.insert_paragraph_before()
    if author:
        add(author, 13, cjk=BODY_CJK)
    brk = anchor.insert_paragraph_before()
    brk.add_run().add_break(WD_BREAK.PAGE)


def style_academic(path, line_spacing=1.5, title=None, subtitle=None,
                   author=None, toc=False):
    doc = Document(path)

    normal = doc.styles["Normal"]
    _set_cjk(normal, BODY_LAT, BODY_CJK, BODY_PT)
    pf = normal.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = line_spacing
    for name, sz in HEAD_SIZES.items():
        try:
            _set_cjk(doc.styles[name], HEAD_CJK, HEAD_CJK, sz, bold=True, color=HEAD_COLOR)
        except KeyError:
            pass

    # 正文段落：首行缩进 2 字符；题注/图/标题/列表不缩进；参考文献悬挂缩进
    n_indent = n_cap = n_ref = 0
    for p in doc.paragraphs:
        name = p.style.name
        txt = p.text.strip()
        if not txt:
            continue
        if _has_image(p):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            continue
        if _is_caption(txt):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.size = Pt(CAPTION_PT)
                r.font.bold = True
            n_cap += 1
            continue
        if name.startswith("Heading") or name == "Title" or "List" in name:
            continue
        if re.match(r"^\[\d+\]", txt):          # 参考文献 → 悬挂缩进
            p.paragraph_format.left_indent = Pt(BODY_PT * 2)
            p.paragraph_format.first_line_indent = Pt(-BODY_PT * 2)
            n_ref += 1
            continue
        p.paragraph_format.first_line_indent = Pt(BODY_PT * 2)   # 正文首行缩进
        n_indent += 1

    three = 0
    for t in doc.tables:
        if len(t.columns) > 1:
            _three_line(t)
            for c in t.rows[0].cells:
                _shade(c, HEADER_FILL)
            three += 1

    if doc.paragraphs:
        anchor = doc.paragraphs[0]
        if title:
            _build_cover(anchor, title, subtitle, author)   # 封面在前
        if toc:
            _add_toc(anchor)                                 # 目录随后（封面之后、正文之前）

    doc.save(path)
    return {"tables": len(doc.tables), "three_line": three, "images": len(doc.inline_shapes),
            "indented": n_indent, "captions": n_cap, "refs": n_ref,
            "headings": sum(1 for p in doc.paragraphs if p.style.name.startswith("Heading"))}


def md_to_docx(md, out):
    if not shutil.which("pandoc"):
        sys.exit("需要 pandoc：brew install pandoc  或  apt install pandoc")
    res = os.path.dirname(os.path.abspath(md)) or "."
    subprocess.run(["pandoc", md, "-o", out, "--resource-path", res], check=True)
    return out


def main(argv):
    ap = argparse.ArgumentParser(description="Markdown → 发表级中文学术报告 .docx")
    ap.add_argument("input", help="结构化 Markdown（或已有 .docx）")
    ap.add_argument("-o", "--output")
    ap.add_argument("--title"); ap.add_argument("--subtitle"); ap.add_argument("--author")
    ap.add_argument("--toc", action="store_true", help="插入目录域")
    ap.add_argument("--line-spacing", type=float, default=1.5)
    a = ap.parse_args(argv)

    base, ext = os.path.splitext(a.input)
    out = a.output or (base + ".docx" if ext.lower() != ".docx" else base + "_排版.docx")
    if ext.lower() in (".md", ".markdown", ".txt"):
        md_to_docx(a.input, out)
    elif ext.lower() == ".docx":
        if os.path.abspath(a.input) != os.path.abspath(out):
            shutil.copy(a.input, out)
    else:
        sys.exit("只支持 .md 或 .docx")

    st = style_academic(out, a.line_spacing, a.title, a.subtitle, a.author, a.toc)
    print("✓ 发表级学术报告已生成（内容未改，仅排版）")
    print(f"  三线表 {st['three_line']} · 图片 {st['images']} · 题注 {st['captions']} · "
          f"首行缩进段 {st['indented']} · 参考文献悬挂 {st['refs']} · 标题 {st['headings']}")
    print(f"  → {out}")


if __name__ == "__main__":
    main(sys.argv[1:])
