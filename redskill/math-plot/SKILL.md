---
name: math-plot
description: 通用数学图像生成——用一句表达式就能画任何数学图：函数曲线、参数曲线、极坐标玫瑰线、隐函数/等高线、三维曲面、向量场/相图、分形（曼德博/朱利亚）。坐标系是数学课本风（过原点带箭头、等比、浅网格），出 300dpi 高清 PNG。用户说「画个函数图/y=…的图像」「画极坐标/参数方程/隐函数」「画个三维曲面/向量场」「画曼德博/分形」「数学配图/函数图像」时用。含可运行 Python 脚本，任何函数名（sin/cos/exp/log…）都支持。
---

# 通用数学图像

任何数学图，只要把式子用字符串写出来就能画。坐标系走"课本风"——坐标轴过原点、带箭头、
浅网格、需要时等比。用 `scripts/mathviz.py`（matplotlib + numpy），出 300dpi 高清 PNG。

## 七大类（命令行，表达式用引号）

```bash
# 1) 函数 y=f(x)（可多条，自动图例、断点断开）
python3 scripts/mathviz.py function --expr "sin(x)" "sin(x)/x" --xlim -12.56 12.56 --title '$\sin x$ 与 sinc'

# 2) 参数曲线 x(t),y(t)（利萨如、螺线、摆线…）
python3 scripts/mathviz.py parametric --x "cos(3*t)" --y "sin(2*t)" --trange 0 6.2832

# 3) 极坐标 r=f(θ)（玫瑰线、心形线…）
python3 scripts/mathviz.py polar --r "1+cos(t)" --title '心形线'      # r=sin(4t) 是八瓣玫瑰

# 4) 隐函数 / 等高线 f(x,y)=0
python3 scripts/mathviz.py contour --f "x**2+y**2-4" --xlim -3 3 --ylim -3 3   # 圆
python3 scripts/mathviz.py contour --f "y-x**2" --open-contour                 # 只画 f=0 曲线不填色

# 5) 三维曲面 z=f(x,y)
python3 scripts/mathviz.py surface --z "sin(sqrt(x**2+y**2))" --xlim -8 8 --ylim -8 8

# 6) 向量场 / 相图 (u(x,y), v(x,y))
python3 scripts/mathviz.py field --u="-y" --v="x" --xlim -3 3 --ylim -3 3       # 旋转场

# 7) 分形
python3 scripts/mathviz.py fractal --fractal-kind mandelbrot     # 或 julia
```

也可 `import mathviz`，直接调用同名函数（传字符串表达式或直接传数组）。

## 写表达式的三条规则（重要）

1. **用 numpy 函数名**：`sin cos tan exp log log10 sqrt abs sign floor sinh cosh tanh arctan …`，
   常量 `pi e`。变量：函数/隐函数/曲面/场用 `x`（和 `y`），参数/极坐标用 `t`。
2. **幂用 `**` 不是 `^`**：写 `x**2`、`x**3`，不是 `x^2`。
3. **标题里的数学符号用 mathtext `$...$`**：如 `$x^2+y^2=4$`、`$\theta$`、`$\sin x$`——
   直接打"²"这类上标字在中文字体里可能缺字。

## 一个坑

命令行里表达式**以减号开头**（如 `-y`）会被误当成选项，要用**等号写法**：`--u="-y"`、`--x="-sin(t)"`。

## 出图建议

- 教学/笔记配图：`function` / `contour`，标题写清结论
- 好看能刷屏：`polar`（玫瑰线）、`fractal`（曼德博/朱利亚）、`surface`（3D 曲面），小红书很吃
- 依赖：`numpy`、`matplotlib`（没有就 `pip install numpy matplotlib`）
