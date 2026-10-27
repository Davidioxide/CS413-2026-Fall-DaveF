"""Locate the Assignment 5 source AST without depending on the cwd."""
from pathlib import Path

ASSIGNS_ROOT = next(
    parent for parent in Path(__file__).resolve().parents
    if (parent / "05" / "lambda1_vp.py").is_file()
)
ASSIGN05 = ASSIGNS_ROOT / "05"
