# LaTeX 正文撰写指南

## 1. 两层结构

- `templates/course-style.sty`：所有课程共用的“锁定版式”。除非发布一个明确的新设计版本，否则不修改该文件的字体、配色、纸张、标题、页眉页脚或盒子样式。
- `lesson.tex`：一门课程的全部内容，使用 `\documentclass[12pt,a4paper,UTF8,fontset=none]{ctexart}` 和 `\usepackage{course-style}` 导入设计。

## 2. 课程元信息

在 `\begin{document}` 之前写：

```latex
\renewcommand{\CourseSubject}{高等数学}
\renewcommand{\CourseTopic}{导数的定义}
\renewcommand{\CourseEyebrow}{从第一性原理学习・高等数学}
\renewcommand{\CourseTitleTop}{从第一性原理学会}
\renewcommand{\CourseTitleBottom}{导数到底是什么}
\renewcommand{\CourseSubtitle}{从平均变化率到瞬时变化率}
\renewcommand{\CourseRouteA}{函数与\\斜率}
\renewcommand{\CourseRouteB}{极限与\\定义}
\renewcommand{\CourseRouteC}{例题与\\练习}
\renewcommand{\CoursePromise}{\textbf{三项承诺：}先讲为什么，再推导定理，然后做题。}
\renewcommand{\CourseFooter}{先修知识・推导・例题・练习}
\renewcommand{\CourseEdition}{学习版 · 2026 年}
```

文字可能撑破封面时请\textbf{缩短封面文案}，保持 29pt 标题和固定位置不变。

## 3. 推荐正文结构

```latex
\begin{document}
\CourseCover
\section*{先说读法：怎样学会这节课？}
...目标、用法、目录...
\tableofcontents
\clearpage
\section{地基：先修知识}
\subsection{直觉、符号、正反例}
...
\section{核心原理：从定义推出工具}
...
\section{例题逐讲}
\subsection{例题 1：为什么要这样做？}
\begin{questionbox}[黑板例题 1]...\end{questionbox}
\stephead{第 1 步：观察。} ...
\begin{whybox}...\end{whybox}
\begin{trybox}...\end{trybox}
\begin{takeawaybox}...\end{takeawaybox}
\section{分层练习}
\section{答案与复盘}
\end{document}
```

完整可编译范例见 `examples/from-problems/lesson.tex`（五道多项式题）和 `examples/from-chapter/lesson.tex`（导数定义）。

## 4. 公式与引用

- 行内数学用 `$...$`，单行重要公式用 `\[...\]`，多行变形用 `aligned` 或 `align*`。
- 用 `\frac{...}{...}`, `\sqrt{...}`, `\sqrt[n]{...}`, `\mathbb{Q}`；不要依赖屏幕截图保存数学公式。
- 导入用户图片作为题目来源时，先人工核对转录，课本图片无需原尺寸铺满页面。
- 不要使用 `eqnarray`；优先 `aligned` 对齐等号，并逐步解释变形原因。
- 尽可能使用稳定的断行环境；不要擅自缩小正文或改变页边距容纳长式子。

## 5. 构建及复核

```bash
python scripts/build_course.py my-course/lesson.tex \
  --out my-course/course.pdf \
  --preview my-course/preview
python scripts/verify_pdf.py my-course/course.pdf
```

第一页封面不应出现页眉；正文页眉显示学科及章节，底部居中页码。查看 `preview/contact-sheet.png` 后还须逐页查看长公式、带色盒子、横向表格、最后一页；结构检查不是人工视觉验收的替代品。
