# pipeline · 小红书内容生产流水线

把「写长文 → 出数据图表 → 用本工具生成图文卡片 → 按时间归档」串成一条可复用流水线。

## 目录约定

每篇内容一个文件夹，按日期归档：

```
content/<日期>-<标题>/
├── 原长文.md      # 完整长文（第一行即标题），也是本工具的排版输入
├── 概述.md        # 核心观点 / 钩子 / 数据看点 / 标签
├── meta.json      # 本工具生成参数（主题/底纹/比例/封面/署名/张数…）
├── make_charts.py # 本篇数据图表脚本（matplotlib）
└── images/        # 产出：本工具卡片 card-NN.png + 数据图表 chart-*.png
```

## 三个脚本

| 文件 | 作用 |
|---|---|
| `rt_charts.py` | 可复用图表库：`waffle()` 点阵图、`tiers_bar()` 对数条形图；中文字体自动适配，配色与卡片统一，输出 1080px PNG |
| `export_cards.py` | 用 Playwright 无头驱动 redtools，注入文案+参数，逐张导出图文卡片到 `images/` |
| `new_post.py` | 编排：`new` 建脚手架；`build` 一键出图表+导出卡片 |
| `charts.ipynb` | Jupyter 版图表（与 `rt_charts.py` 等价，可交互预览） |

## 用法

```bash
# 一次性依赖
pip install matplotlib playwright && playwright install chromium

# 1) 新建一篇
python3 pipeline/new_post.py new "AI不会取代人类"
#    → 生成 content/<今天>-AI不会取代人类/ 脚手架

# 2) 编辑 原长文.md（正文）、make_charts.py（本篇数据）、meta.json（样式）

# 3) 一键构建：出数据图表 + 无头导出全部卡片到 images/
python3 pipeline/new_post.py build content/<今天>-AI不会取代人类
```

单独运行也可以：

```bash
python3 content/<dir>/make_charts.py        # 只出数据图表
python3 pipeline/export_cards.py content/<dir>   # 只导出本工具卡片
```

## 把数据图表插进图文流（关键）

在 `原长文.md` 里用 **Markdown 图片语法**单独成行，即可在该位置插入一张「整页图表卡」：

```markdown
- 只有约200万人（**0.024%**）在用AI构建Agent。

![](content/2026-06-22-ai-vs-human/images/chart-01-people-dots.png)

![](content/2026-06-22-ai-vs-human/images/chart-02-tiers.png)

金字塔尖那0.024%，才是真正把AI当生产力的人。
```

- 路径用**相对项目根目录**（导出时本工具从根目录提供服务）。
- 图表会被 `export_cards.py` 一并导出成 `card-NN.png`，和文字卡片混排在同一轮播里。
- 图表尺寸建议出成 1080×1440（3:4），与卡片同比，整页填满无留白。
- 顺序：先 `make_charts.py` 出图，再 `export_cards.py` 导卡（`build` 已按此顺序）。

## meta.json 参数对照

- `themeIndex`：主题配色，见 `index.html` 的 `getThemes()` 顺序（14=墨黑，15=靛夜…）
- `patternIndex`：底纹，`7=数学 8=物理 9=化学 10=计算机`（0 无 / 1 网格 / …/ 6 公式）
- `coverLayout`：`0 卡片 / 1 全屏 / 2 融入`
- `ratioIndex`：`0 = 3:4(1080×1440) / 1 = 长文 3:5(1080×1800)`
- `heroImg`：封面配图，相对路径（如 `covers/photo-13.jpg`，也可指向某张数据图表）
- 其余：`signature 署名`、`titleFontIndex/bodyFontIndex 字体`、`targetPages 张数`、`closingOn 结尾页`

## 集成原理（无头桥接）

`index.html` 内置一个**仅在 `window.RT_CONFIG` 存在时激活**的桥接：
注入配置后按其渲染，并暴露 `window.RT_PAGE_COUNT()` 与 `window.RT_EXPORT_DATAURL(i)`。
正常浏览器使用零影响；`export_cards.py` 用它把每张卡片取成 PNG。
