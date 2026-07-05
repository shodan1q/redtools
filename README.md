# 小红书图文生成器

把一段长文（支持 Markdown）自动排版成小红书风格的封面图 + 内容长图（1080×1440，小红书推荐 3:4），
支持 16 套配色 / 主色调色板 / 10 种字体（标题与正文分开）/ 11 种底纹 / 3 种封面版式（卡片·全屏·融入）/
20 张内置科技风封面图 / 自定义上传，一键导出每张高清 PNG。

## 用 Claude Code 一句话出图文（推荐）

本项目内置**小红书 Skills 家族**（[`.claude/skills/`](.claude/skills/README.md)），
在项目目录里打开 Claude Code，直接说：

- "帮我做一篇关于××的小红书" → `xhs-post` 一条龙：文案 + 数据图表 + 精美卡片 + 发布文案
- "给这篇笔记写个标题/文案" → `xhs-copy` 纯文案
- "把这组数据做成配图" → `xhs-charts` 风格统一的信息图

产出自动按日期归档到 `content/`。设计风格由
[风格预设库](.claude/skills/xhs-post/references/design-presets.md) 保证：10 套按内容类型
调好的「主题×字体×底纹×封面」组合，开箱即精美。后续新增的小红书技能也统一放
`.claude/skills/`（约定见其 README）。

## 本地运行

这是纯静态页面，**推荐用本地服务器打开**（直接双击 `index.html` 在部分浏览器下，字体加载与导出可能受限）。

### 方式一：Python（系统自带，最简单）
```bash
cd 项目目录
python3 -m http.server 8000
```
然后浏览器打开： http://localhost:8000/

### 方式二：Node
```bash
npx serve .
# 或
npx http-server -p 8000
```
打开终端里给出的地址即可。

> 入口文件是 `index.html`。
> 字体（思源黑/宋、站酷系列等）和导出库 html2canvas 从 CDN 加载，运行时需联网。

## 上传到你的 GitHub

在项目目录执行（把 `<仓库名>` 换成你建好的空仓库名）：
```bash
git init
git add .
git commit -m "小红书图文生成器"
git branch -M main
git remote add origin https://github.com/shodan1q/<仓库名>.git
git push -u origin main
```

## 在线访问（可选，GitHub Pages）

推送后，进入仓库 **Settings → Pages**，Source 选 `main` 分支、根目录 `/ (root)`，保存。
等一两分钟即可通过下面地址访问：
```
https://shodan1q.github.io/<仓库名>/
```

## 目录结构
```
index.html                 # 入口（静态页面，也是无头导出的渲染引擎）
support.js                 # 运行时（必须与 index.html 同目录）
.claude/skills/            # 小红书 Skills 家族·本地完整版（xhs-post / xhs-copy / xhs-charts …）
redskill/                  # RedSkill 市场上传包（纯 Markdown 版，完整体验即本仓库）
covers/                    # 20 张内置封面图 photo-01.jpg … photo-20.jpg
pipeline/                  # 内容生产流水线（Python：图表库 / 无头导出 / 归档编排）
content/                   # 按日期归档的每篇内容（长文 / 概述 / meta / 图片）
uploads/                   # 自备封面图等上传素材
```

> 合规说明：本项目所有 skills **只生产内容，不做任何自动发布**——无头浏览器仅用于渲染
> 本地 `index.html` 出图，与小红书平台零交互；AI 生成内容发布时请按平台规定勾选标识。

## 内容生产流水线（Python + Jupyter）

把「写长文 → Python 出数据图表 → 无头驱动本工具导出图文卡片 → 按时间归档」串成一条命令。
详见 [`pipeline/README.md`](pipeline/README.md)。

```bash
pip install matplotlib playwright && playwright install chromium

python3 pipeline/new_post.py new "标题"                       # 建日期文件夹脚手架
# 编辑 content/<日期-标题>/ 下的 原长文.md、make_charts.py、meta.json
python3 pipeline/new_post.py build content/<日期-标题>         # 出图表 + 导出全部卡片
```

每篇产出归档在 `content/<日期>-<标题>/`：`原长文.md`、`概述.md`、`meta.json`、
`images/`（本工具卡片 `card-NN.png` + Python 数据图表 `chart-*.png`）。

> 无头导出依赖 `index.html` 内置的桥接（仅当注入 `window.RT_CONFIG` 时激活，正常使用零影响）。
