import os
import shutil
import sys
from pathlib import Path

# Ensure we can import the app
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import tkinter as tk
from main import LibraryApp


def assert_true(cond, msg):
    if not cond:
        raise AssertionError(msg)


def main():
    base = ROOT / "_tmp_smoke"
    if base.exists():
        shutil.rmtree(base)
    base.mkdir(parents=True, exist_ok=True)

    # Create sample files
    f1 = base / "report.txt"
    f1.write_text("This is an invoice report for Q1.", encoding="utf-8")
    f2 = base / "report.txt"  # same name in same dir to test collision on second move
    # We'll create a duplicate after first move

    # Start app in headless mode
    app = LibraryApp()
    app.withdraw()
    app.current_folder = str(base)

    # Move first file to tag folder
    tag = app._sanitize_tag("Invoices/")
    app._move_files_to_tag(tag, [str(f1)])
    dest_dir = base / tag
    assert_true(dest_dir.exists(), "Destination tag folder was not created")
    assert_true(not f1.exists(), "Source file should be moved")
    moved1 = dest_dir / "report.txt"
    assert_true(moved1.exists(), "Moved file missing in destination")

    # Create a second file with same original name and move again to test collision suffix
    f2.write_text("Another invoice report for Q2.", encoding="utf-8")
    app._move_files_to_tag(tag, [str(f2)])
    moved2 = dest_dir / "report (1).txt"
    assert_true(moved2.exists(), "Collision-resolved filename not created (report (1).txt)")

    # Test _extract_text on a simple txt
    text = app._extract_text(str(moved1))
    assert_true("invoice" in text.lower(), "Text extraction failed for txt file")

    print("SMOKE TEST PASSED: move + collision + txt extract")


if __name__ == "__main__":
    main()

