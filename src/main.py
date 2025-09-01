import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Optional

class LibraryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Personal Library Organizer")
        self.geometry("800x600")
        self.current_folder = None
        self.api_key: Optional[str] = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_GENAI_API_KEY")
        self.model_name: str = "gemini-1.5-flash"
        self.create_widgets()

    def create_widgets(self):
        self.folder_label = ttk.Label(self, text="No folder selected")
        self.folder_label.pack(pady=10)
        self.browse_btn = ttk.Button(self, text="Browse Folder", command=self.browse_folder)
        self.browse_btn.pack(pady=5)
        # Files table
        self.tree = ttk.Treeview(self, columns=("Type", "Path"), show="headings", selectmode="extended")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Path", text="Path")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tag controls
        controls = ttk.Frame(self)
        controls.pack(fill=tk.X, padx=10, pady=(0, 10))
        ttk.Label(controls, text="Tag:").pack(side=tk.LEFT)
        self.tag_entry = ttk.Entry(controls, width=30)
        self.tag_entry.pack(side=tk.LEFT, padx=5)
        self.move_btn = ttk.Button(controls, text="Move to Tag Folder", command=self.move_selected_to_tag)
        self.move_btn.pack(side=tk.LEFT, padx=5)

        # AI controls
        ai_controls = ttk.Frame(self)
        ai_controls.pack(fill=tk.X, padx=10, pady=(0, 10))
        ttk.Label(ai_controls, text="Google API Key:").pack(side=tk.LEFT)
        self.api_key_entry = ttk.Entry(ai_controls, width=45, show="*")
        if self.api_key:
            # Show only last 6 chars as hint; keep field empty for safety
            self.api_key_entry.insert(0, "")
        self.api_key_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(ai_controls, text="Use Key", command=self.set_api_key).pack(side=tk.LEFT)
        ttk.Button(ai_controls, text="Auto Tag + Move", command=self.auto_tag_and_move).pack(side=tk.LEFT, padx=5)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_label.config(text=folder)
            self.current_folder = folder
            self.scan_folder(folder)

    def scan_folder(self, folder):
        self.tree.delete(*self.tree.get_children())
        for root, _, files in os.walk(folder):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in [".pdf", ".docx", ".txt"]:
                    self.tree.insert("", "end", values=(ext[1:].upper(), os.path.join(root, file)))

    def _sanitize_tag(self, tag: str) -> str:
        # Remove characters invalid for Windows folder names: \ / : * ? " < > |
        invalid = set('\\/:*?"<>|')
        cleaned = "".join(ch for ch in tag.strip() if ch not in invalid)
        return cleaned

    def _unique_dest_path(self, dest_dir: str, filename: str) -> str:
        base, ext = os.path.splitext(filename)
        candidate = os.path.join(dest_dir, filename)
        counter = 1
        while os.path.exists(candidate):
            candidate = os.path.join(dest_dir, f"{base} ({counter}){ext}")
            counter += 1
        return candidate

    def move_selected_to_tag(self):
        if not self.current_folder:
            messagebox.showwarning("No Folder", "Please select a base folder first.")
            return
        raw_tag = self.tag_entry.get()
        tag = self._sanitize_tag(raw_tag)
        if not tag:
            messagebox.showwarning("Invalid Tag", "Please enter a valid tag name.")
            return

        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select one or more files to move.")
            return
        self._move_files_to_tag(tag, [self.tree.item(i, "values")[1] for i in selected])

    def _move_files_to_tag(self, tag: str, file_paths: list[str], *, silent: bool = False):
        dest_dir = os.path.join(self.current_folder, tag)
        try:
            os.makedirs(dest_dir, exist_ok=True)
        except OSError as e:
            if not silent:
                messagebox.showerror("Folder Error", f"Could not create tag folder:\n{e}")
            return 0, 0, [("<create-folder>", str(e))]

        moved = 0
        skipped = 0
        errors = []
        for src_path in file_paths:
            if not os.path.isfile(src_path):
                skipped += 1
                continue
            try:
                if os.path.dirname(os.path.abspath(src_path)) == os.path.abspath(dest_dir):
                    skipped += 1
                    continue
                filename = os.path.basename(src_path)
                dest_path = self._unique_dest_path(dest_dir, filename)
                shutil.move(src_path, dest_path)
                moved += 1
            except Exception as e:
                errors.append((src_path, str(e)))

        if not silent:
            self.scan_folder(self.current_folder)
            msg_parts = [f"Moved: {moved}", f"Skipped: {skipped}"]
            if errors:
                msg_parts.append(f"Errors: {len(errors)}")
            messagebox.showinfo("Move Complete", " | ".join(msg_parts))
            if errors:
                detail = "\n".join(f"- {p}: {err}" for p, err in errors[:10])
                messagebox.showwarning("Some files failed", f"First errors:\n{detail}")
        return moved, skipped, errors

    def set_api_key(self):
        key = self.api_key_entry.get().strip()
        if not key and not self.api_key:
            messagebox.showwarning("Missing API Key", "Enter a Google AI Studio API key or set the GOOGLE_API_KEY environment variable.")
            return
        if key:
            self.api_key = key
            messagebox.showinfo("API Key Set", "API key configured for this session.")

    def _extract_text(self, path: str) -> str:
        ext = os.path.splitext(path)[1].lower()
        try:
            if ext == ".txt":
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()
            elif ext == ".docx":
                try:
                    from docx import Document  # python-docx
                except Exception as e:
                    raise RuntimeError("python-docx is not installed") from e
                doc = Document(path)
                return "\n".join(p.text for p in doc.paragraphs)
            elif ext == ".pdf":
                try:
                    from PyPDF2 import PdfReader
                except Exception as e:
                    raise RuntimeError("PyPDF2 is not installed") from e
                text_parts = []
                reader = PdfReader(path)
                for page in reader.pages:
                    try:
                        text_parts.append(page.extract_text() or "")
                    except Exception:
                        continue
                return "\n".join(text_parts)
        except Exception as e:
            raise RuntimeError(f"Failed to read {os.path.basename(path)}: {e}") from e
        return ""

    def _ensure_model(self):
        if not self.api_key:
            raise RuntimeError("Google API key not configured. Set GOOGLE_API_KEY env var or use the key field.")
        try:
            import google.generativeai as genai
        except Exception as e:
            raise RuntimeError("google-generativeai is not installed. Run: pip install google-generativeai") from e
        genai.configure(api_key=self.api_key)
        return genai.GenerativeModel(self.model_name)

    def _ai_tag_for_text(self, text: str) -> str:
        model = self._ensure_model()
        # Limit to avoid extremely long prompts
        snippet = text.strip()
        if len(snippet) > 8000:
            snippet = snippet[:8000]
        prompt = (
            "You are a librarian. Read the document text and return a single concise tag (1-3 words) that best categorizes it. "
            "Return ONLY the tag text without quotes or extra words.\n\nDocument:\n" + snippet
        )
        resp = model.generate_content(prompt)
        tag_raw = (getattr(resp, "text", None) or "").strip().splitlines()[0] if resp else ""
        tag = self._sanitize_tag(tag_raw) or "Uncategorized"
        # Keep tag short
        return tag[:40]

    def auto_tag_and_move(self):
        if not self.current_folder:
            messagebox.showwarning("No Folder", "Please select a base folder first.")
            return
        # Determine files to process: selected or all visible
        selected = self.tree.selection()
        items = selected if selected else self.tree.get_children()
        if not items:
            messagebox.showinfo("No Files", "No files available to tag.")
            return
        file_paths = [self.tree.item(i, "values")[1] for i in items]

        # First pass: classify and group by tag (no UI prompts)
        tag_to_files: dict[str, list[str]] = {}
        classify_errors = []
        for path in file_paths:
            try:
                text = self._extract_text(path)
                if not text.strip():
                    raise RuntimeError("No readable text found")
                tag = self._ai_tag_for_text(text) or "Uncategorized"
                tag_to_files.setdefault(tag, []).append(path)
            except Exception as e:
                classify_errors.append((path, str(e)))

        # Second pass: move per tag, silently; aggregate results
        total_moved = 0
        total_skipped = 0
        move_errors = []
        for tag, paths in tag_to_files.items():
            moved, skipped, errs = self._move_files_to_tag(tag, paths, silent=True)
            total_moved += moved
            total_skipped += skipped
            move_errors.extend(errs)

        # Refresh view once and show a single summary
        self.scan_folder(self.current_folder)
        total_errors = classify_errors + move_errors
        msg_parts = [
            f"Categorized: {total_moved}",
            f"Skipped: {total_skipped}",
        ]
        if total_errors:
            msg_parts.append(f"Errors: {len(total_errors)}")
        messagebox.showinfo("Auto Tag Complete", " | ".join(msg_parts))
        if total_errors:
            detail = "\n".join(f"- {os.path.basename(p)}: {err}" for p, err in total_errors[:10])
            messagebox.showwarning("Some files failed", f"First errors:\n{detail}")

if __name__ == "__main__":
    app = LibraryApp()
    app.mainloop()
