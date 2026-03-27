from fastmcp import FastMCP
from pathlib import Path

mcp = FastMCP('filesystem-server')


BASE_DIR = Path(r'C:\Users\lamic\Downloads').resolve()

def safe_path(path: str) -> Path:
    """Resolve a relative path inside BASE_DIR and reject path-traversal attempts."""
    p = (BASE_DIR / path).resolve()
    if not str(p).startswith(str(BASE_DIR)):
        raise ValueError(f"Access denied: '{path}' is outside the allowed directory.")
    return p


# ── Tools ────────────────────────────────────────────────────────────────────

@mcp.tool()
def list_files(subdir: str = '') -> list[str]:
    """
    List all files and folders inside the base directory (or a subdirectory).

    Args:
        subdir: Optional subfolder path relative to the base directory.
                Leave empty to list the base directory itself.

    Returns a list of entry names with a [DIR] or [FILE] prefix.
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
        path: File path relative to the base directory (e.g. 'notes.txt').
    """
    p = safe_path(path)
    if not p.exists():
        return f"File does not exist: {path}"
    if not p.is_file():
        return f"'{path}' is a directory, not a file."
    return p.read_text(encoding='utf-8', errors='replace')


@mcp.tool()
def write_file(path: str, content: str) -> str:
    """
    Write (or overwrite) a file with the given content.
    Parent directories are created automatically if they don't exist.

    Args:
        path:    File path relative to the base directory (e.g. 'notes.txt').
        content: Text content to write.
    """
    p = safe_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='utf-8')
    return f"File written successfully: {p}"


@mcp.tool()
def delete_file(path: str) -> str:
    """
    Delete a file from the base directory.

    Args:
        path: File path relative to the base directory (e.g. 'old_notes.txt').
    """
    p = safe_path(path)
    if not p.exists():
        return f"File does not exist: {path}"
    if not p.is_file():
        return f"'{path}' is a directory. Only files can be deleted with this tool."
    p.unlink()
    return f"File deleted: {path}"


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
