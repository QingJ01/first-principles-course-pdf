"""Run: python -m unittest discover -s tests -v"""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SkillTests(unittest.TestCase):
    def test_skill_metadata(self):
        r = subprocess.run([sys.executable, str(ROOT / 'scripts/validate_skill.py')],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_design_tokens(self):
        sty = (ROOT / 'templates/course-style.sty').read_text(encoding='utf-8')
        for token in ['CourseNavy', 'CourseTeal', 'CourseAmber', 'questionbox', 'whybox', 'takeawaybox', 'trybox', 'CourseCover']:
            self.assertIn(token, sty)
        self.assertIn('a4paper', sty)

    def test_new_course_both_modes(self):
        with tempfile.TemporaryDirectory() as td:
            for mode in ['problems', 'chapter']:
                project = Path(td) / mode
                p = subprocess.run([sys.executable, str(ROOT/'scripts/new_course.py'), mode,
                     '多项式不可约' if mode == 'problems' else '导数',
                     '--subject', '高等代数', '--dir', str(project)], capture_output=True, text=True)
                self.assertEqual(p.returncode, 0, p.stderr)
                self.assertTrue((project/'lesson.tex').is_file())
                self.assertTrue((project/'course-brief.md').is_file())
                self.assertTrue((project/'course.json').is_file())

    @unittest.skipUnless(shutil.which('xelatex') and shutil.which('latexmk') and
                         importlib.util.find_spec('fitz'), 'Requires XeLaTeX/latexmk/PyMuPDF')
    def test_compilable_examples(self):
        with tempfile.TemporaryDirectory() as td:
            for mode in ['from-problems', 'from-chapter']:
                dest = Path(td) / f'{mode}.pdf'
                p = subprocess.run([sys.executable, str(ROOT/'scripts/build_course.py'),
                         str(ROOT/'examples'/mode/'lesson.tex'), '--out', str(dest), '--strict'],
                         capture_output=True, text=True)
                self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
                self.assertGreater(dest.stat().st_size, 10_000)
                import fitz
                doc = fitz.open(dest)
                self.assertGreaterEqual(len(doc), 4)
                doc.close()


if __name__ == '__main__':
    unittest.main()
