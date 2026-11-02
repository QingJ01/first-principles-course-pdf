# Contributing / 贡献指南

欢迎报告文案、数学、教学顺序和 LaTeX 兼容性问题。

- **改教学流程**：修改 `SKILL.md` 或 `references/pedagogy.md`；请提供一种真实题目/章节场景，以及这种修改为何能帮助零基础学习者。
- **改样例**：在 `examples/` 中提交完整正文；新知识点应讲概念动机、适用条件和反例，不只附答案。
- **改视觉样式**：不要随意改颜色/边距/标题。视觉规范是此 Skill 的产品接口；建议先提 issue，若必须修改，提升设计系统版本并更新参考图。
- **正确性**：特别检查题目条件、定义域、符号、反证逻辑、因式分解、公式代入等。

本地检查：

```bash
python scripts/validate_skill.py
python -m unittest discover -s tests -v
python scripts/build_course.py examples/from-problems/lesson.tex --out /tmp/sample.pdf --preview /tmp/sample-preview --strict
```

请勿提交字体二进制、包含他人受版权保护的整章扫描资料或无法审核的数学证明。MIT 许可覆盖此仓库的原创代码和文本，引用第三方资料须单独遵守其许可。
