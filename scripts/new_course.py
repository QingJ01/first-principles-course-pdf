#!/usr/bin/env python3
"""Create a new course project using the locked First Principles visual template."""
from __future__ import annotations
import argparse
import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "lesson.tex"


def latex_escape(value: str) -> str:
    mapping = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
               "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
               "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(mapping.get(c, c) for c in value)


def main() -> int:
    p = argparse.ArgumentParser(description="Create a first-principles course scaffold")
    p.add_argument("mode", choices=["problems", "chapter"], help="题目驱动 or 章节驱动")
    p.add_argument("title", help="课程标题，例如 多项式不可约 / 导数与微分")
    p.add_argument("--subject", default="学科课程", help="高等代数、高等数学、物理... ")
    p.add_argument("--dir", required=True, type=Path, help="Output project directory")
    args = p.parse_args()

    dest = args.dir.expanduser().resolve()
    dest.mkdir(parents=True, exist_ok=True)
    out = dest / "lesson.tex"
    if out.exists():
        raise SystemExit(f"Refusing to overwrite existing lesson: {out}")

    tex = TEMPLATE.read_text(encoding="utf-8")
    tex = tex.replace("【学科名称】", latex_escape(args.subject))
    tex = tex.replace("【章节主题】", latex_escape(args.title))
    tex = tex.replace("【课程标题】", latex_escape(args.title))
    tex = tex.replace("2026 年", f"{dt.date.today().year} 年")
    out.write_text(tex, encoding="utf-8")

    brief = f"""# 课程制作清单（内部工作底稿，不直接出现在 PDF）

- 入口：{'题目驱动 (problem-driven)' if args.mode == 'problems' else '章节驱动 (chapter-driven)'}
- 学科：{args.subject}
- 主题：{args.title}
- 基础：零基础（默认）
- 学习目标：待填 3-6 条可验证目标

## 原始输入 / 章节边界

{'将用户全部题目忠实抄录于此，逐项核对指数、根号、定义域、参数条件。' if args.mode == 'problems' else '明确教材（如果给了）、章/节范围、重点与不讲的边界；不要臆造指定教材的内容。'}

## 先修知识依赖树

- 【目标题/章节技能】
  - 【定理】
    - 【定义】
      - 【学生可直接验证的事实】

## 课堂结构

1. 诊断题 + 学习承诺
2. 先修地基与直观引入
3. 第一性原理推导与严格证明
4. {'覆盖全部输入题的逐题精讲' if args.mode == 'problems' else '覆盖核心技能的典型例题'}
5. A/B/C 三层自测与完整答案
6. 常见误区与脱稿复盘

## 数学/知识正确性检查

- [ ] 已独立核对全部原始题目和结论
- [ ] 已证明/说明每条关键性质的前提
- [ ] 已设计误区辨析和至少一道迁移题
- [ ] 公式代入/数值边界/符号化简完成必要核验

## 最终交付

- [ ] A4 固定风格：深蓝封面、青绿标题、琥珀重点
- [ ] 完成两轮编译，目录页码完整
- [ ] 渲染所有页面并检查截断、重叠、中文/数学字体
"""
    (dest / "course-brief.md").write_text(brief, encoding="utf-8")
    (dest / "course.json").write_text(json.dumps({"mode": args.mode, "title": args.title,
            "subject": args.subject, "template": "first-principles-course-pdf@1.0"}, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(f"Created {out} and course-brief.md ({args.mode}).")
    print(f"Edit the lesson, then run: python {ROOT / 'scripts/build_course.py'} {out} --out {dest / 'course.pdf'} --preview {dest / 'preview'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
