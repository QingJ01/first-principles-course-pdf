#!/usr/bin/env python3
"""Lightweight PDF structural preflight; a visual review of render previews is still mandatory."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys


def inspect(path: Path):
    try:
        import fitz
    except ImportError:
        print("请安装 pymupdf (pip install pymupdf)；无法执行程序化检查。", file=sys.stderr)
        return 2
    doc = fitz.open(path)
    warnings = []
    cover = doc[0]
    print(f"文件：{path.name}\n页数：{len(doc)}\n封面尺寸：{cover.rect.width:.2f}×{cover.rect.height:.2f} pt")
    if not 1 < len(doc):
        warnings.append("课程不足 2 页（课程一般需要封面、正文和练习）")
    if doc.is_encrypted:
        warnings.append("PDF 被加密")
    expected_size = (595.28, 841.89)
    for i, page in enumerate(doc):
        r = page.rect
        if abs(r.width - expected_size[0]) > 1 or abs(r.height - expected_size[1]) > 1:
            warnings.append(f"第 {i+1} 页不是标准 A4 纵版")
        text = page.get_text()
        if i > 0 and len(text.strip()) < 22:
            warnings.append(f"第 {i+1} 页文本很少，可能有大块空白")
        if "�" in text:
            warnings.append(f"第 {i+1} 页包含 U+FFFD 替代字符")
        if "??" in text:
            warnings.append(f"第 {i+1} 页包含 ??：可能有交叉引用未解析")
        for block in page.get_text("dict")["blocks"]:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    x0,y0,x1,y1 = span["bbox"]
                    if x0 < -2 or x1 > r.width+2 or y0 < -2 or y1 > r.height+2:
                        warnings.append(f"第 {i+1} 页文字超出纸张（span: {span['text'][:24]!r}）")
                        break
    all_text = "\n".join(p.get_text() for p in doc)
    for name in ("目录", "先说读法"):
        if name not in all_text:
            warnings.append(f"缺少栏目：{name}")
    # Verify fonts are embedded; subset CJK fonts generally appear as Type0.
    missing_fonts = 0
    font_names = set()
    for page in doc:
        for font in page.get_fonts():
            font_names.add(font[3])
            try:
                embedded = doc.extract_font(font[0])
                if not embedded[3]:
                    missing_fonts += 1
            except Exception:
                pass
    print("检测到的部分字体：" + ", ".join(sorted(font_names)[:9]))
    if missing_fonts:
        warnings.append(f"可能存在未嵌入字体引用（{missing_fonts} 项，可能重复）")
    print("\n检查结果：" + ("存在需要检查的问题" if warnings else "未发现明显结构错误"))
    for w in dict.fromkeys(warnings):
        print(" - " + w)
    print("注意：仍需查看全页缩略图，检验换行、框体、公式和中文显示。")
    return 0 if not warnings else 1


def main():
    a=argparse.ArgumentParser(description="PDF 课程结构/字体/文本越界检查（不能代替人工审阅）")
    a.add_argument("pdf",type=Path)
    args=a.parse_args()
    if not args.pdf.is_file():
        a.error(f"文件不存在：{args.pdf}")
    return inspect(args.pdf)


if __name__ == "__main__":
    sys.exit(main())
