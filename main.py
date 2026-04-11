from __future__ import annotations

import shutil
from pathlib import Path
from typing import List

from fastmcp import FastMCP

mcp = FastMCP('filesystem-server')

BASE_DIR = Path(r'C:\Users\lamic\Downloads').resolve()


def safe_path(path: str) -> Path:
    """
    Resolve *path* relative to BASE_DIR.
    Uses Path.relative_to() — immune to Windows drive-letter casing issues.
    Raises ValueError if the resolved path escapes the sandbox.
    """
    p = (BASE_DIR / path).resolve()
    try:
        p.relative_to(BASE_DIR)
    except ValueError:
        raise ValueError(f"Access denied: '{path}' is outside the allowed directory.")
    return p


# ── Tools ────────────────────────────────────────────────────────────────────

@mcp.tool()
def list_files(subdir: str = '') -> List[str]:
    """
    List all files and folders inside the Downloads directory (or a subdirectory).

    Args:
        subdir: Optional subfolder path relative to Downloads.
                Leave empty (or pass '') to list Downloads itself.

    Returns a list of entries with a [DIR] or [FILE] prefix.
    """
    target = safe_path(subdir) if subdir else BASE_DIR
    if not target.exists():
        return [f"Directory does not exist: {target}"]
    return [
        f"[DIR]  {entry.name}" if entry.is_dir() else f"[FILE] {entry.name}"
        for entry in sorted(target.iterdir())
    ]


@mcp.tool()
def read_file(path: str) -> str:
    """
    Read and return the text contents of a file.

    Args:
        path: File path relative to Downloads (e.g. 'notes.txt' or 'myproject/main.py').
    """
    p = safe_path(path)
    if not p.exists():
        return f"File does not exist: {path}"
    if not p.is_file():
        return f"'{path}' is a directory, not a file."
    return p.read_text(encoding='utf-8', errors='replace')


@mcp.tool()
def read_multiple_files(paths: List[str]) -> dict[str, str]:
    """
    Read multiple files at once and return their contents as a dict.

    Args:
        paths: List of file paths relative to Downloads.

    Returns:
        {filepath: content_or_error_message, ...}
    """
    result: dict[str, str] = {}
    for path in paths:
        try:
            p = safe_path(path)
            if not p.exists():
                result[path] = f"File does not exist: {path}"
            elif not p.is_file():
                result[path] = f"'{path}' is a directory, not a file."
            else:
                result[path] = p.read_text(encoding='utf-8', errors='replace')
        except Exception as e:
            result[path] = f"Error reading file: {str(e)}"
    return result


@mcp.tool()
def create_folder(path: str) -> str:
    """
    Create a folder (and any missing parent folders) inside Downloads.
    Safe to call even if the folder already exists.

    Args:
        path: Folder path relative to Downloads (e.g. 'myproject' or 'myproject/src').

    Use this when you need to guarantee a directory exists before writing files into it.
    NOTE: write_file and write_multiple_files already call this automatically, so you
    only need this tool when you explicitly want to create an empty folder.
    """
    p = safe_path(path)
    p.mkdir(parents=True, exist_ok=True)
    return f"Folder ready: {p}"


@mcp.tool()
def write_file(path: str, content: str) -> str:
    """
    Write (or overwrite) a single file. Parent folders are created automatically.

    Args:
        path:    File path relative to Downloads (e.g. 'notes.txt' or 'project/main.py').
        content: Text content to write.

    IMPORTANT: For writing multiple files at once, use write_multiple_files instead —
    it is more efficient and handles entire project structures in one call.
    """
    p = safe_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='utf-8')
    return f"File written successfully: {p}"


@mcp.tool()
def write_multiple_files(files: dict[str, str]) -> dict[str, str]:
    """
    Write multiple files at once. ALL intermediate folders are created automatically.

    Use this tool whenever the user asks to create more than one file,
    set up a project structure, or write an entire codebase — never call
    write_file in a loop when this tool is available.

    Args:
        files: A JSON object (dict) mapping each file path to its content.
               Paths are relative to Downloads and MAY include sub-folders.

    Schema:
        {
          "relative/path/to/file.ext": "file content as a string",
          ...
        }

    Examples:
        Single folder project:
        {
          "hello_project/main.py":      "print('Hello World')",
          "hello_project/README.md":    "# Hello Project",
          "hello_project/utils/math.py": "def add(a, b): return a + b"
        }

        Config + source:
        {
          "app/config.json":  "{\"debug\": true}",
          "app/server.py":    "from flask import Flask\\napp = Flask(__name__)"
        }

    Returns:
        {filepath: "Successfully written: <full_path>" or "Error: <message>", ...}

    NOTE: Sub-folders like "myproject/src/" are created automatically.
    You do NOT need to call create_folder first.
    """
    result: dict[str, str] = {}
    for path, content in files.items():
        try:
            p = safe_path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(str(content), encoding='utf-8')
            result[path] = f"Successfully written: {p}"
        except Exception as e:
            result[path] = f"Error: {str(e)}"
    return result


@mcp.tool()
def delete_file(path: str) -> str:
    """
    Delete a single file from Downloads.
    To delete a folder use delete_folder instead.

    Args:
        path: File path relative to Downloads (e.g. 'old_notes.txt').
    """
    p = safe_path(path)
    if not p.exists():
        return f"File does not exist: {path}"
    if not p.is_file():
        return f"'{path}' is a directory — use delete_folder to remove directories."
    p.unlink()
    return f"File deleted: {path}"


@mcp.tool()
def delete_folder(path: str) -> str:
    """
    Delete a folder and ALL its contents recursively. This is irreversible.

    Args:
        path: Folder path relative to Downloads (e.g. 'old_project').
    """
    p = safe_path(path)
    if not p.exists():
        return f"Folder does not exist: {path}"
    if not p.is_dir():
        return f"'{path}' is a file — use delete_file to remove files."
    shutil.rmtree(p)
    return f"Folder deleted: {path}"


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
