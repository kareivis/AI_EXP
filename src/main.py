import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class LibraryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Personal Library Organizer")
        self.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        self.folder_label = ttk.Label(self, text="No folder selected")
        self.folder_label.pack(pady=10)
        self.browse_btn = ttk.Button(self, text="Browse Folder", command=self.browse_folder)
        self.browse_btn.pack(pady=5)
        self.tree = ttk.Treeview(self, columns=("Type", "Path"), show="headings")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Path", text="Path")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_label.config(text=folder)
            self.scan_folder(folder)

    def scan_folder(self, folder):
        self.tree.delete(*self.tree.get_children())
        for root, _, files in os.walk(folder):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in [".pdf", ".docx", ".txt"]:
                    self.tree.insert("", "end", values=(ext[1:].upper(), os.path.join(root, file)))

if __name__ == "__main__":
    app = LibraryApp()
    app.mainloop()
