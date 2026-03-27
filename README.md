# Filesystem MCP Server

A lightweight [FastMCP](https://github.com/jlowin/fastmcp) server that exposes a local directory to AI agents via the Model Context Protocol (MCP). It provides safe, sandboxed file operations — listing, reading, writing, and deleting files — all scoped to a single base directory.

---

## Features

- 📁 **List** files and folders in the base directory or any subdirectory
- 📖 **Read** text file contents
- ✏️ **Write** (create or overwrite) files, with automatic parent directory creation
- 🗑️ **Delete** files safely
- 🔒 **Path traversal protection** — all operations are sandboxed to the base directory

---

## Requirements

- Python 3.10+
- [fastmcp](https://pypi.org/project/fastmcp/)

Install the dependency:

```bash
pip install fastmcp
```

---

## Configuration

The base directory is defined near the top of `main.py`:

```python
BASE_DIR = Path(r'C:\Users\lamic\Downloads').resolve()
```

Change this path to whichever directory you want the server to operate in before running.

---

## Usage

Start the MCP server:

```bash
python main.py
```

The server will launch and listen for MCP-compatible clients (e.g. Claude Desktop, Cursor, or any MCP-enabled agent).

---

## Available Tools

### `list_files(subdir="")`
Lists all files and folders inside the base directory or an optional subdirectory.

| Parameter | Type | Description |
|-----------|------|-------------|
| `subdir` | `str` | Relative path to a subdirectory. Leave empty for the base directory. |

**Returns:** A list of strings prefixed with `[DIR]` or `[FILE]`.

---

### `read_file(path)`
Reads and returns the text content of a file.

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | `str` | File path relative to the base directory (e.g. `notes.txt`). |

---

### `write_file(path, content)`
Writes text content to a file, creating it (and any missing parent directories) if it doesn't exist, or overwriting it if it does.

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | `str` | File path relative to the base directory. |
| `content` | `str` | Text content to write. |

---

### `delete_file(path)`
Deletes a file from the base directory. Only files can be deleted — directories are not affected.

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | `str` | File path relative to the base directory. |

---

## Security

All paths are resolved and validated against `BASE_DIR` before any operation is performed. Any path that resolves outside the base directory (e.g. via `../` traversal) is rejected with an `Access denied` error. This ensures the server cannot be used to access or modify files outside the intended directory.

---

## Project Structure

```
.
└── main.py   # MCP server definition and all tool implementations
```