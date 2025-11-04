#!/usr/bin/env python3
"""Add Google-style docstring skeletons to Python source files.

This script scans Python files under `src/` and inserts a minimal
Google-style docstring for functions and classes that currently lack
any docstring. It makes a backup copy of each file it modifies
as `<filename>.bak`.

Usage:
    python -m scripts.add_docstrings

Notes:
 - The script makes a best-effort skeleton (Args/Returns/Raises). It
   does not attempt to infer complex types. Review and edit the
   generated docstrings to add detail.
 - The script skips files in `__pycache__` and files that already have
   any docstring for the target node.
"""

from __future__ import annotations

import ast
import os
from pathlib import Path
from typing import List, Tuple


def get_arg_names(node: ast.FunctionDef) -> List[str]:
    names = []
    for arg in node.args.args:
        if arg.arg == "self":
            continue
        names.append(arg.arg)
    # include vararg and kwarg names
    if node.args.vararg:
        names.append("*" + node.args.vararg.arg)
    if node.args.kwarg:
        names.append("**" + node.args.kwarg.arg)
    return names


def make_function_docstring(node: ast.FunctionDef) -> str:
    args = get_arg_names(node)
    lines = ["Short description."]
    if args:
        lines.append("")
        lines.append("Args:")
        for a in args:
            lines.append(f"    {a}: Description.")
    # Attempt to detect return usage
    returns = node.returns is not None
    if returns:
        lines.append("")
        lines.append("Returns:")
        lines.append("    Description.")
    lines.append("")
    lines.append("Raises:")
    lines.append("    Description.")
    # Join into triple-quoted string
    body = "\n".join(lines)
    return '"""' + "\n" + body + "\n" + '"""'


def make_class_docstring(node: ast.ClassDef) -> str:
    lines = ["Short description of the class.", "", "Attributes:", "    attr1: Description."]
    body = "\n".join(lines)
    return '"""' + "\n" + body + "\n" + '"""'


def insert_docstrings(source: str) -> Tuple[str, int]:
    """Return modified source with docstrings inserted and count of edits."""
    tree = ast.parse(source)
    edits: List[Tuple[int, str]] = []  # (insertion_line_index (0-based), text)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if ast.get_docstring(node) is None:
                # Insert docstring after the function signature (first line of body)
                if not node.body:
                    continue
                first = node.body[0]
                line_no = first.lineno - 1  # 0-based
                doc = make_function_docstring(node)
                indent = " " * (node.col_offset + 4)
                doc_lines = [(indent + l) if l else l for l in doc.splitlines()]
                text = "\n".join(doc_lines) + "\n"
                edits.append((line_no, text))
        elif isinstance(node, ast.ClassDef):
            if ast.get_docstring(node) is None:
                if not node.body:
                    continue
                first = node.body[0]
                line_no = first.lineno - 1
                doc = make_class_docstring(node)
                indent = " " * (node.col_offset + 4)
                doc_lines = [(indent + l) if l else l for l in doc.splitlines()]
                text = "\n".join(doc_lines) + "\n"
                edits.append((line_no, text))

    if not edits:
        return source, 0

    # Apply edits in reverse order so line numbers remain valid
    lines = source.splitlines(keepends=True)
    for lineno, text in sorted(edits, reverse=True):
        # Insert before the line index
        lines.insert(lineno, text)

    return "".join(lines), len(edits)


def process_file(path: Path) -> int:
    src = path.read_text(encoding="utf-8")
    new_src, edits = insert_docstrings(src)
    if edits:
        bak = path.with_suffix(path.suffix + ".bak")
        path.rename(bak)
        path.write_text(new_src, encoding="utf-8")
        print(f"Patched {path} (+{edits} docstrings), backup saved to {bak}")
    return edits


def find_python_files(base: Path) -> List[Path]:
    files = []
    for p in base.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        if p.match("*/scripts/add_docstrings.py"):
            continue
        files.append(p)
    return files


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    src_dir = repo_root / "src"
    if not src_dir.exists():
        print("No src/ directory found — run this from the project root.")
        return
    files = find_python_files(src_dir)
    total = 0
    for f in files:
        try:
            total += process_file(f)
        except Exception as exc:
            print(f"Failed to process {f}: {exc}")
    print(f"Done. Inserted {total} docstrings.")


if __name__ == "__main__":
    main()
