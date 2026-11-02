#!/usr/bin/env python3
"""Offline lightweight SKILL.md schema validation."""
from __future__ import annotations
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "SKILL.md"
body = path.read_text(encoding="utf-8")
assert body.startswith("---\n"), "SKILL.md missing YAML frontmatter"
front = body.split("---", 2)[1]
name_m = re.search(r"^name:\s*(\S+)\s*$", front, re.MULTILINE)
desc_m = re.search(r"^description:\s*(.+)$", front, re.MULTILINE)
assert name_m and desc_m, "name/description required"
name = name_m.group(1)
assert 1 <= len(name) <= 64 and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name)
assert name == root.name, f"Skill name must equal containing directory ({root.name})"
assert 0 < len(desc_m.group(1)) <= 1024
assert (root / "templates/course-style.sty").exists()
for rel in re.findall(r"\]\((references/[^)]+)\)", body):
    assert (root / rel).exists(), f"Unresolved reference: {rel}"
print(f"Valid skill: {name}; description {len(desc_m.group(1))} chars")
