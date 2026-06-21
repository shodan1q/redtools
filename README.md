# 小红书图文生成器

把一段长文（支持 Markdown）自动排版成小红书风格的封面图 + 内容长图（1080×1800），
支持配色 / 主色调色板 / 10 种字体（标题与正文分开）/ 6 种底纹 / 3 种封面版式（卡片·全屏·融入）/
20 张内置科技风封面图 / 自定义上传，一键导出每张高清 PNG。

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
index.html                 # 入口（静态页面）
support.js                 # 运行时（必须与 index.html 同目录）
covers/                    # 20 张内置封面图 photo-01.jpg … photo-20.jpg
```
