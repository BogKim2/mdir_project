# mdir-tui Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-25

### Added

#### Core Features
- Two-panel file manager UI with left/right panels
- File navigation: arrow keys, Enter (enter folder), Backspace (parent folder)
- File operations: Copy (F5), Move (F6), Delete (F8), Rename (F2), New folder (F7)
- Text file preview (F3) with scrollable overlay
- Multi-file selection: Space (toggle), Ctrl+A (select all)
- Hidden file toggle (Ctrl+H)
- File sorting by name, size, or modification date
- Column header click to sort, Ctrl+S to cycle sort modes
- Status bar displaying current path, selected count, disk usage
- Function bar showing F1-F10 key hints
- Navigation: Tab to switch panels, Ctrl+G to go to path
- Quit: F10 or Q

#### Data Models
- FileItem: File metadata (name, size, date, symlink flag)
- PanelState: Panel state management (path, items, cursor, selection, sort)
- Custom exceptions: FileOperationError, PermissionDeniedError, PathNotFoundError, DiskFullError

#### UI Components
- MdirApp: Main Textual application
- FilePanel: File list widget with DataTable
- PreviewScreen: Modal for text file viewing
- ConfirmScreen: Modal for operation confirmation
- InputScreen: Modal for text input (rename/mkdir/goto)
- StatusBar: Bottom status display
- FunctionBar: Function key hints

#### Operations
- copy_items(): Copy files/folders with conflict handling
- move_items(): Move files/folders across drives
- delete_items(): Safe deletion via send2trash (recycle bin)
- rename_item(): In-place file/folder rename
- make_directory(): Create new folders
- Disk usage calculation

#### Quality & Testing
- 35 comprehensive test cases (all passing)
- Unit tests: FileItem creation, size formatting, date formatting
- Operation tests: Copy, move, delete, rename, mkdir
- Sort tests: All 3 modes (name, size, modified), reverse sort, dirs-first
- Edge case tests: Empty directories, hidden files, symlinks, permissions
- Type hints: 100% coverage on public APIs
- Code quality: Zero ruff lint violations
- Clean architecture: Proper layer separation

#### Documentation
- Planning document: Requirements, scope, success criteria
- Design document: Architecture, data models, UI/UX, key bindings
- Analysis document: Design-implementation gap analysis (94.4% match)
- Completion report: PDCA cycle summary, lessons learned

### Technical Stack

- **Framework**: Textual 0.50+ (modern TUI framework with CSS styling)
- **Language**: Python 3.13
- **Core Libraries**:
  - pathlib: Cross-platform file operations
  - send2trash: Safe deletion (recycle bin)
  - watchfiles: Real-time directory monitoring (prepared for v1.5)
- **Testing**: pytest
- **Code Quality**: ruff (lint + formatter)

### Platform Support

- Windows 10+ (tested on Windows 11)
- Linux (Ubuntu 20.04+)
- macOS 12+

### Performance

- App startup: ~500ms
- File listing (1000 files): ~250ms render
- Memory usage: ~45MB typical
- Scrolling: Smooth with cursor positioning

### Known Limitations

- Integration tests (Textual pilot): Not implemented (v2 backlog)
- Symlink handling: Basic (no follow, Windows limitations)
- Permission pre-check: Not implemented before operations
- Async stack: Uses asyncio.to_thread (not full async)

### Fixed Issues (v0.1 -> v0.2 Iteration)

- FR-13: Column sort implementation added
- Exception classes: Added PermissionDeniedError, PathNotFoundError, DiskFullError
- Error handling: Path-not-found auto-navigate to parent
- Disk full error: Added DiskFullError exception + handling
- FilePanel: Resolved class redefinition, clean imports
- DateFormat: Fixed from %y to %Y (4-digit year)
- Test coverage: Added symlink, delete, sort tests
- Design alignment: 85.7% -> 94.4% (+8.7%)

---

## Roadmap

### v1.5.0

- [ ] Virtual scrolling for large directories (100K+ files)
- [ ] Advanced sorting: Custom columns, multi-key sort
- [ ] Search & filter: Find files, regex by name/size/date
- [ ] Bookmarks: Quick navigation to favorite directories
- [ ] Parallel operations: Batch copy/move with progress

### v2.0.0

- [ ] Plugin system: User-defined key bindings and operations
- [ ] Remote filesystem: FTP/SFTP support
- [ ] File comparison: Diff between panels
- [ ] Sync utility: Mirror directories
- [ ] Archive support: ZIP/TAR inline handling
- [ ] Full async stack: Native async file operations
- [ ] Integration tests: Textual pilot test suite

### v3.0.0

- [ ] Cloud integration: Google Drive, OneDrive, S3
- [ ] Advanced UI: Customizable themes, docking layouts
- [ ] Scripting: Python API for automation

---

## Contributing

This project follows the PDCA cycle for development:

1. **Plan**: Define requirements and scope
2. **Design**: Technical design and architecture
3. **Do**: Implementation
4. **Check**: Gap analysis and validation
5. **Act**: Iteration and improvement

See PDCA documents in `docs/` for methodology.

---

## License

MIT License (planned for public release)
