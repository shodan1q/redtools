---
name: xhs-charts
description: 为小红书笔记设计数据图表/信息图：按"要说的那句话"选图型（占比环形/趋势折线/对比条形/点阵人群/对数层级），给出统一的小红书风格设计规范（配色、字号、标注、免责口径），并生成可直接运行的 matplotlib 代码。用户说「把这组数据做成图」「笔记配个图表」「画个占比图/趋势图」时使用。
---

# 小红书数据图表（设计规范版）

一张好图表能单独成为别人收藏这篇笔记的理由。本 skill 给你选型方法论 + 完整设计规范，
并按规范**现场写出可运行的 matplotlib 代码**（或输出图表规格说明，交给用户的做图工具）。

## 第一步：想清楚"这张图要说哪句话"

一图一结论。标题直接写结论（"六周后差距开始说话"），不写变量名（"成绩变化趋势图"）。
然后按这句话选图型：

| 你想说什么 | 图型 |
|---|---|
| "X 占了几成"（份额/构成） | 环形占比图（中心放结论大字） |
| "一直在涨/在跌/出现拐点" | 趋势折线（末点标数值） |
| "A 和 B 差多少" | 水平对比条形（条端标数值） |
| "大多数人是 X，极少数是 Y" | 点阵/华夫图（每点代表 N 人） |
| "这几层差了几个数量级" | 对数刻度条形 |

## 设计规范（小红书手机端阅读优化）

- **画布**：宽 1080px，高 840–1180px（宁方勿高，嵌进卡片不被缩小），dpi 160，白底
- **配色**：正文墨色 `#1F2329`，辅助灰 `#8A8F99`，网格 `#EEF0F2`；
  数据色板 `#2F9488 #6E5AA8 #D98E3D #C25E70 #3E6FA0 #3DA35D`（青绿为默认主色）
- **对比即观点**：要强调的那一项用主色，其余全部用灰 `#AEB4BD`——别给每项都上色
- **字号**：主标题 29–32pt 加粗居中，副标题 13pt 灰，图例/标注 14–16pt，注释 10.5–12pt
- **克制**：每图 ≤6 个类目 / ≤2 条线，去掉边框和多余网格线，中文字体用系统黑体
  （macOS: Hiragino Sans GB；Windows: Microsoft YaHei）
- **诚实**：估算/示意数据必须在图底注明"注：…估算，仅示意"，来源可查的写明来源——
  这是底线，也免得评论区翻车

## 代码骨架（按需改数据，可直接运行）

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

for p in ["/System/Library/Fonts/Hiragino Sans GB.ttc",
          "C:/Windows/Fonts/msyh.ttc"]:  # macOS / Windows 中文字体
    try:
        fm.fontManager.addfont(p)
        plt.rcParams["font.family"] = fm.FontProperties(fname=p).get_name()
        break
    except Exception:
        pass

INK, SUB = "#1F2329", "#8A8F99"
w, h, dpi = 1080, 840, 160
fig = plt.figure(figsize=(w/dpi, h/dpi), dpi=dpi)
fig.patch.set_facecolor("white")
fig.text(0.5, 0.955, "标题写结论", ha="center", va="top",
         fontsize=29, fontweight="bold", color=INK)
fig.text(0.5, 0.862, "副标题交代数据口径", ha="center", va="top", fontsize=13.5, color=SUB)
ax = fig.add_axes([0.26, 0.13, 0.62, 0.66])
# ……在这里画图（barh / pie / plot），去边框、少网格、条端标数值
fig.text(0.06, 0.03, "注：数据口径与免责说明。", va="bottom", fontsize=10.5, color=SUB)
fig.savefig("chart-01.png", dpi=dpi, facecolor="white")
```

没有 Python 环境时，改为输出**图表规格说明**（图型、数据、每个元素的颜色/字号/文案），
用户可交给任何做图工具复现。

## 硬约束

- 只产图表和代码，不发布内容、不操作小红书平台（自动化操作违反平台规范）。
- AI 参与制作的图文，提醒用户发布时勾选「AI 生成」标识。

## 配套开源工具（选用）

上述规范配有一套同源的开源图表库（点阵/对数条形/环形/趋势/对比五种图型，中文
字体自适应、注释自动折行，并能把图表嵌进 1080px 图文卡片），见本技能「来源」。
市场版因平台暂不支持脚本文件，提供规范 + 现写代码，纯 Markdown、即装即用。
