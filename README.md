# Personal Library Organizer

A Python application to sort and manage your personal library of documents (PDF, DOCX, TXT, etc.) stored on your local hard drive.

## Features
- Scan folders for documents
- Categorize and tag files
- Search and filter documents
- User-friendly interface
 - Create tag-named folders and move files accordingly

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

---

This is a work in progress. Features and UI will be improved iteratively.
