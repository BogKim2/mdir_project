# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-02-26

### Security
- **VULN-01 Critical** — Path traversal in `make_directory` / `rename_item`: added `_validate_filename()` + resolved-path parent check
- **VULN-02 High** — Symlink following in `shutil.copytree`: added `symlinks=True` to prevent escape outside destination
- **VULN-04 High** — TOCTOU race condition in rename/mkdir: removed pre-existence checks; rely on OS `FileExistsError`
- **VULN-05 Medium** — Unbounded conflict-resolution loop in `resolve_conflict`: bounded by `_MAX_CONFLICT_RETRIES = 999`
- **VULN-07 Medium** — No Windows filename validation: added regex for invalid characters and reserved names (CON, NUL, COM1–9, LPT1–9)
- **VULN-08 Medium** — `stat()` follows symlinks exposing target metadata: use `lstat()` for symlinks in `FileItem.from_path()`
- **VULN-10 Low** — `select_all()` could freeze UI on large directories: capped at `MAX_SELECT_ALL = 10_000`
- Added 11 security regression tests (`TestSecurityPathTraversal`, `TestSecurityFilenameValidation`, `TestSecurityConflictLoop`)
- Total test count: 46 passed, 1 skipped (up from 35)

## [0.1.0] - 2026-02-26

### Added
- Dual-panel TUI file manager layout (left / right panels)
- File operations: copy (F5), move (F6), delete to trash (F8), rename (F2), new folder (F7)
- Text file preview with inline viewer (F3)
- Column sorting by name, size, or date — click headers or Ctrl+S
- Hidden file toggle (Ctrl+H)
- Direct path navigation (Ctrl+G)
- Multi-file selection with Space / Ctrl+A
- Active panel visual indicator: `▶` marker, bright blue border, bright path bar
- Tab key panel switching with focus synchronization
- Status bar showing item count, sort order, and disk usage
- Function key bar (F2–F10) always visible at bottom
- Safe delete via `send2trash` (recycle bin)
- Dark theme (custom Textual CSS)
- 35 unit tests covering models and file operations

### Fixed
- Directory names containing brackets (e.g. `[docs]`) were invisible due to Rich markup parsing
- `NoActiveWorker` error on copy/move/delete/rename dialogs — added `@work` decorator
- Backspace in input dialogs navigated to parent directory instead of deleting characters
- Space in input dialogs triggered file selection instead of inserting a space character
- Folder created or renamed in one panel was not reflected in the other panel when both showed the same path
- Active panel state (`_active_panel_id`) not updated when switching panels via mouse click or Textual's built-in Tab cycling
