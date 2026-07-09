---
name: academic-report
description: 发表级学术报告生成器：文献综述 / 课程论文 / 实验报告 / 博士硕士学位论文，从结构化写作到一键导出规范 Word（.docx）。含可运行 Python 脚本——build_academic_docx.py 产出中文学术规范排版（A4/独立封面页/中英文摘要与关键词/首行缩进/三线表/图表编号题注/真·脚注角注/悬挂缩进参考文献，遵 GB/T 7713.1、GB/T 7714），make_figure.py 出 300dpi 发表级插图（图表规则移植自 figure-style：结论式标题、焦点色主导、小样本点+中位数、折线末端直标、渲染自检）。用户要「写文献综述」「课程论文」「实验报告」「学位/毕业论文」「生成学术报告 Word」「把材料整理成规范论文」时用。帮你把真实材料组织成规范初稿并导出成品，不代查文献、不编造数据。
---

# 发表级学术报告

把你的材料，做成一份**结构规范、逻辑清晰、能直接导出 Word 的学术报告**。分工：你提供
真实内容（论据/数据/文献），skill 负责结构、逻辑主线、图表与规范排版。产出是给你继续
填充打磨的成稿，**不替你编造数据与文献**（编错查重/检测一测就出事，也是学术不端）。

## 目录

```
academic-report/
├── SKILL.md                     ← 本文件（工作流）
├── scripts/
│   ├── build_academic_docx.py   ← Markdown → 发表级 .docx（封面/摘要/三线表/首行缩进/题注/脚注）
│   └── make_figure.py           ← 300dpi 学术插图（结论式标题、去冗余边框）
└── references/
    ├── structure.md             ← 三种报告骨架 + 分节写作要点
    └── citations.md             ← GB/T 7714 / APA 引用格式 + 学术诚信红线
```

## 工作流

### 1. 定类型，搭骨架

问清：哪种报告（综述/课程论文/实验报告）？给谁看、什么要求（字数、引用格式、模板）？
手上有什么真实材料？然后**读 [references/structure.md](references/structure.md)** 选骨架、
按分节要点组织。逻辑主线：钩子→背景→证据→结论，一条线贯穿。

### 2. 写成结构化 Markdown

按这个约定写正文（让脚本排版更准）：

```markdown
摘要
（摘要正文 200–600 字，脚本自动居中标题 + 首行缩进）
关键词：词1；词2；词3

Abstract
(English abstract)
Keywords: w1; w2; w3

# 1 引言
正文段落……（脚本自动首行缩进 2 字符）。需要角注处用 [^1] 标注[^1]。

表1 参数窗口
| 参数 | 取值 | 依据 |
|---|---|---|
| … | … | … |

![](fig1.png)
图1 降温曲线呈指数衰减（示例数据）

[^1]: 这是角注内容——pandoc 会转成真·Word 页脚注，带分隔线、小五号。
```

- 「摘要 / Abstract」单独成行 → 居中黑体小三标题；「关键词：/ Keywords:」开头 → 标签加粗。
- 角注用 pandoc 脚注语法 `[^n]`，文末 `[^n]: 注文`，生成**真·Word 脚注**。
- 引用按 [references/citations.md](references/citations.md)（GB/T 7714）格式，
  **具体文献用真实读过的替换、逐条核实**——AI 不代查、不编造 DOI。

### 3. 配图（有数据就配，标准移植自 figure-style）

用 `make_figure.py` 出 300dpi 发表级图。规则来自 Claude Science 的 figure-style：
标题写**结论**、开放边框、焦点色主导其余灰化、折线末端直标、渲染后自检文字不重叠。

```python
import sys; sys.path.insert(0, "scripts")
import make_figure as mf
fig, ax = mf.new_figure("坚持组六周后明显领先", "每周测验均分 · 模拟数据")
mf.line_series(ax, list(range(1,7)),
               {"坚持组":[55,58,64,71,76,83], "对照组":[54,55,53,56,55,57]})   # 末端直标，无图例框
ax.set_xticks(range(1,7)); ax.set_xticklabels([f"第{i}周" for i in range(1,7)])
ax.set_ylabel("测验均分"); mf.goodness_arrow(ax, "越高越好")
mf.save(fig, "fig1.png")
```

**按数据形状选图型**：趋势→`line_series`；分组均值+原始点→`bar_with_points`
（焦点组用 `focal_palette` 高亮、其余灰化）；**小样本 n≲10→`strip_with_median`**
（点+中位数刻度，不要用条形）。图注写在图**下方**：`图1 …`。

### 4. 一键导出发表级 Word

```bash
python3 scripts/build_academic_docx.py report.md -o report.docx \
    --title "标题" --subtitle "副标题" --author "姓名 / 单位" --line-spacing 1.5 --render
```

自动套：**独立封面页**、中英文摘要与关键词样式、正文宋体小四·1.5 倍行距·**首行缩进 2 字符**、
标题黑体分级、数据表→**三线表**、图/表**居中编号题注**、`[^n]`→**真·脚注**、参考文献**悬挂缩进**。
`--render` 调 LibreOffice 转 PDF 便于逐页核对（改完必看渲染，别只信结构）。**内容一字不改，只排版。**

### 5. 质检

- 逻辑主线连不连贯（每节首句连读成故事）
- 结果与讨论是否分离；讨论有没有写局限
- 引用格式全篇统一、**有无未核实/编造的引用**
- 图表标题是结论、正文有引用解读
- 是否需要按规定披露 AI 使用

## 运行环境说明

- **能跑 Python 的环境**（有 pandoc + python-docx + matplotlib）：直接产出 .docx 成品与插图。
- **不能跑脚本的环境**：skill 退化为写作指导，输出规范 Markdown，让用户自行用
  `pandoc report.md -o report.docx` 转换。核心方法论（结构/逻辑/引用/诚信）不依赖脚本。

## 硬约束（学术诚信）

- **不编造数据与文献**：数据用你的真实实测/来源；具体引用给格式示例并标注"需替换核实"，
  绝不虚构作者/年份/DOI。见 [references/citations.md](references/citations.md)。
- **应独立完成的作业自己写**：本 skill 帮结构、逻辑、格式与排版，不替你把该原创的内容做完。
- **AI 使用要披露**：按学校/期刊规定如实说明。
- 依赖：`pip install python-docx matplotlib` + 系统装 `pandoc`。
