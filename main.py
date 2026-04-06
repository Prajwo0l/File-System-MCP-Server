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
def read_multiple_files(paths:List[str])-> dict[str, str]:
    """
    Read multiple files at once and return their contents.
    Args:
        paths: List of file paths relative to the base directory.
    Returns:
        A dictionary where key=filepath,value=file content or error message.
    """
    result={}
    for path in paths:
        try :
            p=safe_path(path)
            if not p.exists():
                result[path]=f'File does not exist:{path}'
            elif not p.is_file():
                result[path]=f"'{path}'is a directory , not a file." 
            else:
                result[path]=p.read_text(encoding='utf-8',errors='replace')
        except Exception as e:
            result[path]=f'Error reading file:{str(e)}'    
    return result




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
def write_multiple_files(files:dict[str,str]) -> dict[str,str]:
    """
    Write multiple files at once.
    Args:
        files:Dictionary where:
                - key = file path(relative to BASE_DIR)
                - value = content to write            
    Example:
        {
            'hello.py': 'print('Hello World)',
            'README.md':" # My Project\n\nDescription here...",
            'config/settings.json' : '{'debug':true}
        }
    Returns:
        Dictionary with results for each file(success or error message)
    """
    result={}
    for path,content in files.items():
        try:
            p=safe_path(path)
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(str(content),encoding='utf-8')
            result[path]=f'Successfully written:{p}'
        except Exception as e:
            result[path]=f'Error:{str(e)}'
    return result


@mcp.tool()
def delete_file(path: str) -> str:
    """
    Delete a single file from the base directory.
    Use delete_folder to remove a directory.

    Args:
        path: File path relative to the base directory (e.g. 'old_notes.txt').
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
    Delete a folder and ALL its contents recursively from the base directory.
    This is irreversible — use with caution.

    Args:
        path: Folder path relative to the base directory (e.g. 'old_project').
    """
    import shutil
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
