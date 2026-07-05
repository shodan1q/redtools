# 数据图表指南（pipeline/rt_charts.py）

图表是小红书图文的**收藏率放大器**——一张好图表能单独成为别人保存这篇笔记的理由。
本项目所有图表用 `pipeline/rt_charts.py` 生成，白底、中文字体自适应、1080px 宽、
与卡片视觉同源，可整页嵌入内容卡。

## 选图表类型（按你要说的话选）

| 你想说什么 | 用 | 函数 | 默认尺寸 |
|---|---|---|---|
| "大多数人是 X，只有极少数是 Y"（人群构成） | 点阵图 | `waffle(tiers, out, title, ...)` | 1080×1180 |
| "这几层数量差了几个数量级" | 对数条形 | `tiers_bar(tiers, out, title, ...)` | 1080×840 |
| "X 占了几成"（份额/构成） | 环形占比 | `donut(parts, out, title, ...)` | 1080×1080 |
| "一直在涨/在跌/出现拐点" | 趋势折线 | `trend(series, out, title, xlabels, ...)` | 1080×840 |
| "A 和 B 差多少"（直观对比） | 线性条形 | `compare_bars(items, out, title, ...)` | 1080×840 |

## 用法（写进本篇的 make_charts.py）

```python
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "pipeline"))
import rt_charts as rc

OUT = os.path.join(HERE, "images")

# 环形占比：parts 的 pct 合计 ≈100；center 放一句话结论（"大字\n小字"）
rc.donut([{"label": "通勤与杂事", "pct": 34, "sub": "补充小字"},
          {"label": "深度工作", "pct": 21}],
         os.path.join(OUT, "chart-01-time.png"),
         title="你的8小时去哪了", subtitle="工作日时间抽样",
         center="21%\n真正在深度工作", note="数据来源说明")

# 趋势折线：多条线自动右端标名+末值（右边距按标注长度自适应，
# 但线名 ≤3 字、末值取整仍然更好看——右侧留白少，折线区更大）
rc.trend([{"label": "坚持组", "values": [55, 64, 76, 83], "unit": "分"}],
         os.path.join(OUT, "chart-02-trend.png"),
         title="六周后差距开始说话", xlabels=["第1周", "第2周", "第3周", "第4周"])

# 线性对比：2–6 条最佳；text 可覆盖数值标注
rc.compare_bars([{"label": "刷短视频", "value": 168, "text": "168 分钟"},
                 {"label": "阅读", "value": 12, "text": "12 分钟"}],
                os.path.join(OUT, "chart-03-cmp.png"), title="时间都花在哪")

# 点阵图 / 对数条形（tiers 结构见 content/2026-06-22-ai-vs-human/make_charts.py 实例）
# tiers: [{"label","people","pct","color","value","desc"}...]
```

## 设计守则（图表的"精美"来自这里）

- **一图一句话**：标题直接写结论（"六周后差距开始说话"），不写变量名（"成绩变化趋势图"）。
  副标题交代口径，note 交代数据来源/免责（超过约 40 个全角字符会自动折成两行，
  上限两行，再长会被截断——尽量 ≤80 字）。
- **配色**：不传 color 时自动用 `rc.PALETTE`（青绿/紫/金橙/莓红…，与卡片主题同源）。
  要强调某一项时，只给那一项传主题强调色，其余用灰 `#AEB4BD`——对比即观点。
- **尺寸**：嵌入内容卡的图表**宁方勿高**（高图会被限高缩小）。默认尺寸都调好了，别改；
  确要改，宽固定 1080，高不超过 1180。
- **数据要少**：每张图 ≤6 个类目 / ≤2 条线。要讲的多就拆成两张图，别堆一张。
- **诚实**：估算/示意数据必须在 note 里写明（"基于公开数据推算，仅示意"），
  这既是底线也免得评论区翻车。
- 文件名 `chart-NN-语义.png`（如 `chart-01-time-donut.png`），存进本篇 `images/`。
- **深色主题（墨黑/靛夜）嵌白底图表**会形成"深底白卡"的强对比——圆角卡片框
  让它成立，但这是全套图里最大的风格跳变。图表密集（≥3 张）的选题优先选浅色预设；
  深色预设下图表页前后放文字页缓冲，别连排两张图表页。

## 嵌进卡片

在 `原长文.md` 里单独一行写：

```markdown
![每个点代表320万人，灰色是从未用过AI的人](content/<本篇目录>/images/chart-01-xxx.png)
```

- 图注（方括号内）一句话告诉读者看哪里，会渲染在图下方。
- 必须**先跑 make_charts.py 再导卡片**（`new_post.py build` 已按此顺序）。
- 最有冲击力的一张图可兼任封面：`meta.json` 里 `heroImg` 指向它。
