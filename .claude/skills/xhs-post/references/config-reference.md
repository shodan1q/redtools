# meta.json / RT_CONFIG 参数对照

`meta.json` 里只有下列键会传给渲染器（其余键被 `export_cards.py` 忽略，
可放 `_comment` 之类的注释字段）：

| 键 | 类型 | 说明 |
|---|---|---|
| `title` | str | 仅归档用，渲染以正文第一行为准 |
| `source` | str | 正文文件名，默认 `原长文.md` |
| `raw` | str | （导出脚本自动从 source 读入，meta 里不用写） |
| `signature` | str | 署名，封面右下 + 每页页脚 `@署名` |
| `themeIndex` | 0–15 | 配色主题，见下表 |
| `customColor` | hex/null | 覆盖主题强调色（高亮词/进度条/徽章用色） |
| `customBg` | hex/null | 覆盖底色（慎用，会重算整套文字色） |
| `ratioIndex` | 0/1 | 0 = 3:4（1080×1440）；1 = 3:5（1080×1800）长文 |
| `patternIndex` | 0–10 | 底纹，见下表 |
| `coverLayout` | 0/1/2 | 0 卡片（**必须配 heroImg**）；1 全屏（无图时深色渐变兜底）；2 融入（**必须配 heroImg**） |
| `heroImg` | 路径/null | 封面配图，相对项目根，如 `covers/photo-13.jpg`，可指向图表 PNG |
| `titleFontIndex` | 0–9 | 标题字体，见下表 |
| `bodyFontIndex` | 0–9 | 正文字体（只用 0/1/2/5） |
| `targetPages` | int | 期望张数（含封面与结尾页）。是分页预算而非硬约束，实际张数可能略多 |
| `closingOn` | bool | 结尾金句页开关 |
| `dedication` | str | 自定义结尾寄语；留空则取正文最后一段（≤80 字时） |

## 主题（themeIndex）

| # | 名称 | 底色调 | 强调色 | | # | 名称 | 底色调 | 强调色 |
|---|---|---|---|---|---|---|---|---|
| 0 | 鸿蒙橙 | 米白 | 橙 #C26B2E | | 8 | 薄荷绿 | 浅绿 | 绿 #2F8F6B |
| 1 | 奶油棕 | 奶油 | 棕 #B5764A | | 9 | 青瓷 | 浅青 | 青 #2F8F86 |
| 2 | 松墨绿 | 浅绿 | 深绿 #3E7A5E | | 10 | 藕荷 | 浅粉紫 | 紫红 #9E5A8C |
| 3 | 黛蓝 | 浅灰蓝 | 蓝 #3E6FA0 | | 11 | 浅紫 | 浅紫 | 紫 #6E5AA8 |
| 4 | 莓粉 | 浅粉 | 莓红 #C25E70 | | 12 | 豆沙 | 浅豆沙 | 砖红 #B0573A |
| 5 | 米白 | 暖白 | 赭 #A8763E | | 13 | 暖灰 | 暖灰 | 灰棕 #7A6A55 |
| 6 | 浅杏 | 浅杏 | 杏橙 #D98E3D | | 14 | 墨黑★深色 | 墨黑 | 金橙 #D98E3D |
| 7 | 雾霾蓝 | 雾蓝 | 灰蓝 #3E6F84 | | 15 | 靛夜★深色 | 深藏蓝 | 亮蓝 #5B8FD0 |

## 底纹（patternIndex）

0 无 · 1 网格 · 2 圆点 · 3 斜线 · 4 竖线 · 5 横线 · 6 公式手稿(位图) ·
7 数学(矢量) · 8 物理 · 9 化学 · 10 计算机

## 字体（titleFontIndex / bodyFontIndex）

0 黑体 · 1 细黑 · 2 宋体 · 3 雅宋 · 4 海报体 · 5 圆体 · 6 手写 · 7 龙藏 · 8 志莽 · 9 毛笔

6–9 为手写系，只可做标题；正文限 0/1/2/5。

## 常用命令

```bash
# 新建一篇（生成 content/<今天>-<slug>/ 脚手架）
python3 pipeline/new_post.py new "标题"

# 一键构建：跑 make_charts.py 出图表 → 无头导出全部卡片
python3 pipeline/new_post.py build content/<日期-标题>

# 只导卡片（图表已就绪时）
python3 pipeline/export_cards.py content/<日期-标题>
```

## 排错

| 症状 | 原因 / 处理 |
|---|---|
| 报缺 playwright | `pip install playwright && playwright install chromium` |
| 卡片字体不对（黑体兜底） | 字体走 CDN，需联网；重跑一次 build |
| 图表页空白/裂图 | `![]()` 路径必须**相对项目根**且文件已存在——先出图表再导卡片 |
| 某页文字太挤 | `targetPages` +2 重导；或换 `ratioIndex: 1` 长图 |
| 某页大片留白 | 多半是整页图表/要点卡等**原子块**顶开的，调 targetPages 无效——调块序（小标题→图表→释义）、并段、增删句子（见 writing-guide） |
| 封面出现"封面配图"占位框 | 卡片/融入版式没给 `heroImg`：补图，或改 `coverLayout: 1` |
| 实际张数 ≠ targetPages | 正常，它是分页预算；差太多就调字数或 targetPages |
| 张数变少后旧卡残留 | 导出脚本会自动清理多余的 card-NN.png；若手动删过文件，重导一遍即可 |
