"""
Tests for DocxProcessor and RprCommand ('dt rpr').
"""

from pathlib import Path
import docx
import git
import pytest

from devtul.commands.repr_cmd import RprCommand
from devtul.core.docx_processor import DocxProcessor


def test_docx_processor_frontmatter():
    md = """---
title: Test Document
author: Will
version: 1.0.0
---

# Heading 1
Paragraph text here.
"""
    fm, body = DocxProcessor.extract_frontmatter(md)
    assert fm["title"] == "Test Document"
    assert fm["author"] == "Will"
    assert "# Heading 1" in body


def test_docx_processor_conversion(tmp_path):
    md = """---
title: Sample Report
version: 2.1
---

# Main Heading

Here is some regular text with **bold**, *italic*, and `inline_code`.

```python
def greet(name: str):
    return f"Hello, {name}!"
```

| Header A | Header B |
| --- | --- |
| Val 1 | Val 2 |
"""
    out_docx = tmp_path / "test_output.docx"
    DocxProcessor.convert_markdown_to_docx(md, out_docx)
    assert out_docx.exists()
    assert out_docx.stat().st_size > 0

    # Verify that python-docx can open and read it back
    doc = docx.Document(out_docx)
    headings = [p.text for p in doc.paragraphs if p.text.strip()]
    assert "Sample Report" in headings
    assert "Main Heading" in headings


def test_rpr_command_formats(tmp_path):
    # Setup test workspace
    src_dir = tmp_path / "workspace"
    src_dir.mkdir()
    (src_dir / "module.py").write_text("def run():\n    pass\n", encoding="utf-8")
    (src_dir / "notes.txt").write_text("some notes\n", encoding="utf-8")

    cmd = RprCommand()

    # 1. Markdown format
    md_file = tmp_path / "repr.md"
    res_md = cmd.execute(path=src_dir, file=md_file, format="md")
    assert res_md is not None
    assert res_md.format == "md"
    assert md_file.exists()
    assert "module.py" in md_file.read_text(encoding="utf-8")

    # 2. Word .docx format
    docx_file = tmp_path / "repr.docx"
    res_docx = cmd.execute(path=src_dir, file=docx_file, docx_flag=True)
    assert res_docx is not None
    assert res_docx.format == "docx"
    assert docx_file.exists()
    assert docx_file.stat().st_size > 0

    # 3. Text format
    txt_file = tmp_path / "repr.txt"
    res_txt = cmd.execute(path=src_dir, file=txt_file, format="text")
    assert res_txt is not None
    assert res_txt.format == "text"
    assert txt_file.exists()


def test_rpr_command_filter(tmp_path):
    src_dir = tmp_path / "workspace"
    src_dir.mkdir()
    (src_dir / "keep.py").write_text("print('keep')\n", encoding="utf-8")
    (src_dir / "ignore.tmp").write_text("print('ignore')\n", encoding="utf-8")

    cmd = RprCommand()
    md_file = tmp_path / "filtered.md"
    res = cmd.execute(path=src_dir, file=md_file, match=["*.py"])
    assert res is not None
    assert len(res.files) == 1
    assert res.files[0].relative_path.name == "keep.py"


def test_rpr_clone_command(tmp_path):
    # Create a local source git repository to serve as the remote URL
    remote_repo_dir = tmp_path / "source_repo"
    remote_repo_dir.mkdir()
    repo = git.Repo.init(remote_repo_dir)
    (remote_repo_dir / "app.py").write_text("print('cloned app')\n", encoding="utf-8")
    repo.index.add(["app.py"])
    repo.index.commit("Initial commit")

    out_file = tmp_path / "cloned_repr.md"

    from devtul.commands.repr_cmd import rpr_command

    # Test cloning using rpr_command("clone", str(remote_repo_dir), file=out_file)
    res = rpr_command(
        target="clone",
        url=str(remote_repo_dir),
        file=out_file,
        format="md",
    )
    assert res is not None
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "app.py" in content
    assert "cloned app" in content
