import os
import shutil
import sys
from pathlib import Path

# Ensure we can import the app
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from main import LibraryApp


def main():
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_GENAI_API_KEY")
    if not api_key:
        print("ERROR: Set GOOGLE_API_KEY in the environment before running.")
        sys.exit(1)

    base = ROOT / "_tmp_ai_smoke"
    if base.exists():
        shutil.rmtree(base)
    base.mkdir(parents=True, exist_ok=True)

    # Create sample files with distinct topics
    files = {
        "invoice_q2.txt": "Invoice #2451 for Q2 2025. Amount due: 4500 EUR. Vendor: ACME Corp. Payment terms Net 30.",
        "project_proposal.txt": "Project proposal: Implement a web-based task tracker using React and Node.js with PostgreSQL.",
        "medical_notes.txt": "Patient exhibits symptoms of seasonal allergies. Recommended antihistamines and follow-up in two weeks.",
    }
    for name, text in files.items():
        (base / name).write_text(text, encoding="utf-8")

    app = LibraryApp()
    app.withdraw()  # do not show UI
    app.current_folder = str(base)
    app.api_key = api_key

    results = []
    for name in files.keys():
        path = str(base / name)
        text = app._extract_text(path)
        tag = app._ai_tag_for_text(text)
        app._move_files_to_tag(tag, [path])
        results.append((name, tag))

    print("Assigned tags:")
    for name, tag in results:
        print(f" - {name} -> {tag}")

    print("\nResulting folders:")
    for p in sorted(base.iterdir()):
        if p.is_dir():
            print(f" - {p.name}")

    print("\nAI SMOKE TEST COMPLETED")


if __name__ == "__main__":
    main()

