import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class LibraryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Personal Library Organizer")
        self.geometry("800x600")
        self.current_folder = None
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

        dest_dir = os.path.join(self.current_folder, tag)
        try:
            os.makedirs(dest_dir, exist_ok=True)
        except OSError as e:
            messagebox.showerror("Folder Error", f"Could not create tag folder:\n{e}")
            return

        moved = 0
        skipped = 0
        errors = []
        for item in selected:
            _, src_path = self.tree.item(item, "values")
            if not os.path.isfile(src_path):
                skipped += 1
                continue
            # Skip if already in destination directory
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

        # Refresh view
        self.scan_folder(self.current_folder)

        # Report summary
        msg_parts = [f"Moved: {moved}", f"Skipped: {skipped}"]
        if errors:
            msg_parts.append(f"Errors: {len(errors)}")
        messagebox.showinfo("Move Complete", " | ".join(msg_parts))
        if errors:
            # Optionally show detailed errors
            detail = "\n".join(f"- {p}: {err}" for p, err in errors[:10])
            messagebox.showwarning("Some files failed", f"First errors:\n{detail}")

if __name__ == "__main__":
    app = LibraryApp()
    app.mainloop()
