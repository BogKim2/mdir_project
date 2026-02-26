# mdir-tui

A modern two-panel TUI file manager inspired by the classic mdir (DOS) and Midnight Commander, built with Python and [Textual](https://textual.textualize.io/).

![screenshot](screenshot.svg)

## Features

- **Dual-panel layout** — side-by-side panels for easy file management
- **Keyboard-driven** — full keyboard navigation with function key shortcuts
- **File operations** — copy, move, delete (to trash), rename, and create folders
- **File preview** — view text file contents inline (F3)
- **Column sorting** — sort by name, size, or date; click column headers or use Ctrl+S
- **Hidden files** — toggle visibility with Ctrl+H
- **Path navigation** — jump to any path with Ctrl+G
- **Multi-select** — select multiple files/folders with Space, or select all with Ctrl+A
- **Active panel indicator** — clear visual distinction (▶ marker + bright border)
- **Safe delete** — files are moved to the system recycle bin via `send2trash`
- **Dark theme** — eye-friendly dark color scheme

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Installation

```bash
# Clone the repository
git clone https://github.com/BogKim2/mdir_project.git
cd mdir_project

# Install in editable mode (pip)
pip install -e .

# Or using uv
uv sync
```

## Usage

```bash
# Run directly
python run.py

# Or using the installed entry point
mdir
```

The application opens with both panels showing the current working directory.

## Key Bindings

| Key | Action |
|-----|--------|
| `Tab` | Switch active panel |
| `↑` / `↓` | Navigate file list |
| `Enter` | Enter directory / Preview file |
| `Backspace` | Go to parent directory |
| `Space` | Toggle file selection |
| `Ctrl+A` | Select / deselect all |
| `Ctrl+H` | Toggle hidden files |
| `Ctrl+S` | Cycle sort order (name → size → date) |
| `Ctrl+G` | Go to path (type path directly) |
| `F2` | Rename file or folder |
| `F3` | Preview file contents |
| `F5` | Copy selected items to opposite panel |
| `F6` | Move selected items to opposite panel |
| `F7` | Create new folder |
| `F8` | Delete selected items (to trash) |
| `F10` / `Q` | Quit |

## Project Structure

```
mdir_project/
├── run.py                  # Entry point
├── pyproject.toml          # Project configuration
├── src/
│   └── mdir/
│       ├── app.py          # Main Textual application
│       ├── models/
│       │   └── file_item.py    # FileItem, PanelState data models
│       ├── operations/
│       │   ├── copy.py         # File copy with conflict resolution
│       │   ├── move.py         # File move
│       │   ├── delete.py       # Delete (trash), rename, mkdir
│       │   └── exceptions.py   # Custom exception classes
│       ├── panels/
│       │   ├── file_panel.py   # FilePanel widget (path bar + file table)
│       │   ├── dialogs.py      # Modal dialogs (confirm, input, preview)
│       │   └── status_bar.py   # Status bar and function key bar
│       └── styles/
│           └── mdir.tcss       # Textual CSS (dark theme)
└── tests/
    ├── test_file_item.py   # Unit tests for models
    └── test_operations.py  # Unit tests for file operations
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check src/
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| UI Framework | [Textual](https://textual.textualize.io/) 0.89+ |
| Language | Python 3.13 |
| Safe Delete | [send2trash](https://github.com/arsenetar/send2trash) |
| Linter | [ruff](https://docs.astral.sh/ruff/) |
| Testing | pytest |
| Build | hatchling |

## License

MIT
