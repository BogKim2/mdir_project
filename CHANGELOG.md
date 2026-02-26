# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
