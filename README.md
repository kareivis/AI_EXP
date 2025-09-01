# Personal Library Organizer

A Python application to sort and manage your personal library of documents (PDF, DOCX, TXT, etc.) stored on your local hard drive.

## Features
- Scan folders for documents
- Categorize and tag files
- Search and filter documents
- User-friendly interface
 - Create tag-named folders and move files accordingly
 - Auto-tag files with Google AI and move to tag folders

## Requirements
- Python 3.9+
- Tkinter (for GUI)
- python-docx, PyPDF2 (for document parsing)

## Getting Started
1. Install dependencies:
   pip install -r requirements.txt
2. Run the application:
   python src/main.py

## Tag-Based Folder Organization
- Select a base folder using "Browse Folder".
- Enter a tag in the "Tag" field.
- Select one or more files in the list.
- Click "Move to Tag Folder" to create a folder named after the tag under the selected base folder and move the files into it.
- Invalid characters for Windows folder names are removed automatically from the tag.

## Auto-Tagging with Google AI Studio
- Install the extra dependency:
  pip install -r requirements.txt
- Set your Google AI Studio API key in the environment (recommended):
  - Windows PowerShell: $env:GOOGLE_API_KEY = "<YOUR_API_KEY>"
  - macOS/Linux bash: export GOOGLE_API_KEY="<YOUR_API_KEY>"
- Alternatively, paste the key into the "Google API Key" field in the app and click "Use Key" (session only).
- Click "Auto Tag + Move" to analyze selected files; if none are selected, all visible files are processed.
- The app uses model `gemini-1.5-flash` to assign a concise tag (1–3 words) based on content and moves each file into a folder named after that tag within the selected base folder.

Notes
- Supported types for auto-tagging: .pdf, .docx, .txt
- Large documents are truncated to the first ~8k characters for analysis.
- If a file with the same name exists in the destination folder, a counter suffix like " (1)" is appended to avoid overwriting.

---

This is a work in progress. Features and UI will be improved iteratively.
