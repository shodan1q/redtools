"""
build_academic_docx —— 把结构化 Markdown 生成为**规范中文学术论文** .docx。

对齐中文学位论文/期刊论文排版：A4 页面、独立封面页、正文宋体小四·1.5 倍行距·
**首行缩进 2 字符**、标题黑体分级、摘要/关键词规范样式、数据表→**三线表**、
图/表**居中编号题注**、**真·脚注（角注）** 小五号、参考文献悬挂缩进。内容不改，只排版。

用法：
    python3 build_academic_docx.py report.md -o report.docx \
        --title "标题" --subtitle "副标题" --author "张三 / 某某大学" --render
依赖：pandoc（Markdown→docx；脚注/图表/引用都由它转）、python-docx（排版）、
     可选 LibreOffice soffice（--render 时转 PDF 便于核对）。

Markdown 约定：
  # 一级(章)  ## 二级(节)  ### 三级
  角注：正文用 [^1] 标记，文末 `[^1]: 注文`
  图：![](fig.png) 单独一行，**下一行**写题注 `图1 xxx`
  表题写在表格**上方**一行 `表1 xxx`
  摘要段落标题写 `摘要` / `Abstract`；关键词行以 `关键词：` / `Keywords:` 开头
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

from docx import Document
from docx.shared import Pt, RGBColor, Mm
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.text import WD_LINE_SPACING, WD_ALIGN_PARAGRAPH

# ---- 中文学术排版默认（改这里=改风格）--------------------------------------
BODY_CJK, BODY_LAT, BODY_PT = "宋体", "Times New Roman", 12          # 正文小四
HEAD_CJK = "黑体"
HEAD = {  # 级别: (字号pt, 加粗, 对齐, 段前pt, 段后pt)
    "Heading 1": (15, True, "center", 24, 18),
    "Heading 2": (13.5, True, "left", 12, 6),
    "Heading 3": (12, True, "left", 12, 6),
}
BODY_STYLES = ("Normal", "First Paragraph", "Body Text", "Compact")  # pandoc 正文样式
REF_TITLES = ("参考文献", "references")
CAPTION_PT = 10.5           # 图表题注小五
FOOTNOTE_PT = 9            # 脚注小五
HEADER_FILL = "F2F2F2"
ABSTRACT_TITLES = ("摘要", "中文摘要", "abstract", "英文摘要")
KEYWORD_HEADS = ("关键词", "关 键 词", "keywords", "key words")
CAP_RE = re.compile(r"^(图|表|Figure|Table|Fig\.?)\s*[\d一二三四五六七八九十]", re.I)
ALIGN = {"center": WD_ALIGN_PARAGRAPH.CENTER, "left": WD_ALIGN_PARAGRAPH.LEFT,
         "right": WD_ALIGN_PARAGRAPH.RIGHT, "justify": WD_ALIGN_PARAGRAPH.JUSTIFY}


def _set_style(style, cjk=None, lat=None, size=None, bold=None, color=None):
    if lat:
        style.font.name = lat
    if cjk:
        rpr = style.element.get_or_add_rPr()
        rpr.get_or_add_rFonts().set(qn("w:eastAsia"), cjk)
    if size:
        style.font.size = Pt(size)
    if bold is not None:
        style.font.bold = bold
    if color:
        style.font.color.rgb = color


def _run_font(run, cjk, lat, size=None, bold=None, color=None):
    run.font.name = lat
    rpr = run._element.get_or_add_rPr()
    rpr.get_or_add_rFonts().set(qn("w:eastAsia"), cjk)
    if size:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if color:
        run.font.color.rgb = color


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
        e.set(qn("w:val"), val); e.set(qn("w:sz"), sz)
        e.set(qn("w:space"), "0"); e.set(qn("w:color"), "000000")
        return e

    b.append(edge("top", "12")); b.append(edge("bottom", "12")); b.append(edge("insideH", "4"))
    for tag in ("left", "right", "insideV"):
        e = OxmlElement("w:" + tag); e.set(qn("w:val"), "none"); b.append(e)
    tblPr.append(b)


def _has_image(p):
    return bool(p._p.findall(".//" + qn("w:drawing")))


def _norm(s):
    return s.strip().rstrip("：:").strip().lower()


def _build_cover(anchor, title, subtitle, author):
    """在正文前插入独立封面页；正文首段设 page_break_before 保证封面独占一页。"""
    def spacer(n=1):
        for _ in range(n):
            anchor.insert_paragraph_before()

    def centered(text, cjk, lat, size, bold=False, color=None):
        p = anchor.insert_paragraph_before()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(text)
        _run_font(r, cjk, lat, size, bold, color)
        return p

    spacer(6)
    centered(title, HEAD_CJK, BODY_LAT, 24, bold=True)
    if subtitle:
        spacer(1)
        centered(subtitle, BODY_CJK, BODY_LAT, 15, color=RGBColor(0x55, 0x55, 0x55))
    spacer(10)
    if author:
        centered(author, BODY_CJK, BODY_LAT, 13)
    anchor.paragraph_format.page_break_before = True     # 正文另起一页


def style_academic(path, line_spacing=1.5, title=None, subtitle=None, author=None):
    doc = Document(path)

    sec = doc.sections[0]                                  # A4 + 学位论文页边距
    sec.page_width, sec.page_height = Mm(210), Mm(297)
    sec.top_margin, sec.bottom_margin = Mm(25), Mm(25)
    sec.left_margin, sec.right_margin = Mm(30), Mm(25)

    normal = doc.styles["Normal"]
    _set_style(normal, BODY_CJK, BODY_LAT, BODY_PT)
    pf = normal.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = line_spacing
    for bn in ("First Paragraph", "Body Text", "Compact"):   # pandoc 正文样式同款字体
        try:
            _set_style(doc.styles[bn], BODY_CJK, BODY_LAT, BODY_PT)
        except KeyError:
            pass
    for name, (sz, bold, align, sb, sa) in HEAD.items():
        try:
            st = doc.styles[name]
            _set_style(st, HEAD_CJK, BODY_LAT, sz, bold=bold, color=RGBColor(0x1A, 0x1A, 0x1A))
            st.paragraph_format.alignment = ALIGN[align]
            st.paragraph_format.space_before = Pt(sb)
            st.paragraph_format.space_after = Pt(sa)
        except KeyError:
            pass
    for fn in ("Footnote Text", "footnote text"):          # 脚注小五
        try:
            _set_style(doc.styles[fn], BODY_CJK, BODY_LAT, FOOTNOTE_PT)
            doc.styles[fn].paragraph_format.first_line_indent = Pt(0)
            break
        except KeyError:
            pass

    n_ind = n_cap = n_abs = 0
    in_refs = first_h1 = False
    for p in doc.paragraphs:
        name = p.style.name
        raw = p.text.strip()
        low = _norm(raw)
        if name.startswith("Heading") or name == "Title":  # 标题：分页 + 记录参考文献段
            in_refs = any(low == t or low.startswith(t) for t in REF_TITLES)
            if in_refs:
                p.paragraph_format.page_break_before = True     # 参考文献另起一页
            elif name == "Heading 1" and not first_h1:
                p.paragraph_format.page_break_before = True     # 正文首章另起一页
                first_h1 = True
            continue
        if _has_image(p):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            continue
        if CAP_RE.match(raw):                              # 图表题注：居中小五加粗
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                _run_font(r, BODY_CJK, BODY_LAT, CAPTION_PT, bold=True)
            n_cap += 1
            continue
        if low in ABSTRACT_TITLES:                         # 摘要/Abstract：居中黑体小三
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if low in ("abstract", "英文摘要"):             # 英文摘要另起一页
                p.paragraph_format.page_break_before = True
            for r in p.runs:
                _run_font(r, HEAD_CJK, BODY_LAT, 15, bold=True)
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            n_abs += 1
            continue
        if any(low.startswith(k) for k in KEYWORD_HEADS):  # 关键词：顶格、标签加粗
            p.paragraph_format.first_line_indent = Pt(0)
            p.paragraph_format.left_indent = Pt(0)
            for r in p.runs:
                _run_font(r, BODY_CJK, BODY_LAT, BODY_PT)
            if p.runs:
                p.runs[0].font.bold = True
            continue
        if in_refs and raw:                                # 参考文献：悬挂缩进、小五、不首行缩进
            p.paragraph_format.left_indent = Pt(21)
            p.paragraph_format.first_line_indent = Pt(-21)
            for r in p.runs:
                _run_font(r, BODY_CJK, BODY_LAT, CAPTION_PT)
            continue
        if name in BODY_STYLES and raw:                    # 正文首行缩进 2 字符
            p.paragraph_format.first_line_indent = Pt(BODY_PT * 2)
            n_ind += 1

    three = 0
    for t in doc.tables:
        if len(t.columns) > 1:
            _three_line(t)
            for c in t.rows[0].cells:
                _shade(c, HEADER_FILL)
            three += 1

    if title and doc.paragraphs:
        _build_cover(doc.paragraphs[0], title, subtitle, author)

    doc.save(path)
    return {"tables": len(doc.tables), "three_line": three, "images": len(doc.inline_shapes),
            "indented": n_ind, "captions": n_cap, "abstract_titles": n_abs,
            "headings": sum(1 for p in doc.paragraphs if p.style.name.startswith("Heading"))}


def md_to_docx(md, out):
    if not shutil.which("pandoc"):
        sys.exit("需要 pandoc：brew install pandoc")
    res = os.path.dirname(os.path.abspath(md)) or "."
    subprocess.run(["pandoc", md, "-o", out, "--resource-path", res], check=True)
    return out


def _soffice():
    for p in ("soffice", "/Applications/LibreOffice.app/Contents/MacOS/soffice",
              "libreoffice"):
        if shutil.which(p) or os.path.exists(p):
            return shutil.which(p) or p
    return None


def render_pdf(docx_path):
    so = _soffice()
    if not so:
        return None
    out_dir = os.path.dirname(os.path.abspath(docx_path))
    subprocess.run([so, "--headless", "--convert-to", "pdf", "--outdir", out_dir, docx_path],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pdf = os.path.splitext(docx_path)[0] + ".pdf"
    return pdf if os.path.exists(pdf) else None


def main(argv):
    ap = argparse.ArgumentParser(description="Markdown → 规范中文学术论文 .docx")
    ap.add_argument("input")
    ap.add_argument("-o", "--output")
    ap.add_argument("--title"); ap.add_argument("--subtitle"); ap.add_argument("--author")
    ap.add_argument("--line-spacing", type=float, default=1.5)
    ap.add_argument("--render", action="store_true", help="转 PDF 便于核对（需 LibreOffice）")
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

    st = style_academic(out, a.line_spacing, a.title, a.subtitle, a.author)
    print("✓ 规范学术论文已生成")
    print(f"  三线表 {st['three_line']} · 图片 {st['images']} · 题注 {st['captions']} · "
          f"摘要标题 {st['abstract_titles']} · 首行缩进段 {st['indented']} · 标题 {st['headings']}")
    print(f"  → {out}")
    if a.render:
        pdf = render_pdf(out)
        print(f"  PDF：{pdf}" if pdf else "  （未找到 LibreOffice，跳过 PDF）")


if __name__ == "__main__":
    main(sys.argv[1:])
