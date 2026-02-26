# mdir-tui Security Specification

> Security and safety analysis for a two-panel TUI file manager performing real filesystem operations.

**Date**: 2026-02-26
**Analyst**: Security Architect (bkit-security-architect)
**Scope**: All source files under `src/mdir/`, test files under `tests/`
**Application Type**: Desktop TUI (Textual), local filesystem operations
**Risk Profile**: High -- destructive file operations (copy, move, delete, rename, mkdir)

---

## Executive Summary

The mdir-tui project is a local two-panel TUI file manager that directly manipulates the filesystem. The primary threat model centers on **unintended destructive operations** rather than network-based attacks. Overall the codebase demonstrates several good security practices (trash-based deletion, confirmation dialogs, path separator rejection in rename). However, the analysis identified **13 specific issues** ranging from a critical path traversal vulnerability in `make_directory` to several medium and low-severity gaps.

| Severity | Count |
|----------|-------|
| Critical | 1     |
| High     | 3     |
| Medium   | 5     |
| Low      | 3     |
| Info     | 1     |

---

## 1. Positive Security Findings

Before listing vulnerabilities, the following good practices are acknowledged:

| Practice | Location | Description |
|----------|----------|-------------|
| Trash-based deletion | `operations/delete.py:19` | Uses `send2trash` instead of permanent deletion |
| Confirmation dialogs | `app.py:165-228` | Copy, move, delete all require user confirmation |
| Path separator check in rename | `operations/delete.py:33` | Rejects `/` and `\` in rename input |
| Rich markup escaping | `panels/file_panel.py:51` | Uses `markup_escape()` to prevent Rich markup injection |
| Safe preview size limit | `panels/dialogs.py:95` | 512KB preview cap prevents memory exhaustion |
| Graceful error handling | `models/file_item.py:48` | `PermissionError`/`OSError` caught in `from_path()` |
| Conflict resolution | `operations/copy.py:11-34` | Automatic rename on name collision prevents overwrite |
| Path resolution | `panels/file_panel.py:184` | `go_to()` uses `expanduser().resolve()` |

---

## 2. Vulnerability Report

### VULN-01: Path Traversal in `make_directory` (Critical)

**File**: `src/mdir/operations/delete.py`, lines 49-69
**OWASP**: A01 Broken Access Control / A03 Injection

**Description**: The `make_directory()` function validates only that the name is non-empty and that the target does not already exist. Unlike `rename_item()` which explicitly blocks `/` and `\`, `make_directory()` performs NO path separator validation. A user can type `../../etc/malicious_dir` or `..\..\Windows\something` in the F7 dialog and create a directory outside the current working directory.

```python
# delete.py:49-60 -- NO path traversal check
def make_directory(parent: Path, name: str) -> Path:
    name = name.strip()
    if not name:
        raise FileOperationError("...")
    new_dir = parent / name          # <-- path traversal via "../" in name
    if new_dir.exists():
        raise FileOperationError(...)
    new_dir.mkdir(parents=False)     # parents=False mitigates SOME cases
```

**Severity**: **Critical**
- `parents=False` prevents creating intermediate directories, but `..` components are resolved by the OS before `mkdir` is called. The path `parent / "../../target"` resolves to an ancestor directory, and if `target` does not exist there, it will be created.

**Proof of Concept**: If current directory is `C:\Users\kim\Documents`, input `..\..\Public\pwned` would create `C:\Users\Public\pwned`.

**Fix**:
```python
def make_directory(parent: Path, name: str) -> Path:
    name = name.strip()
    if not name:
        raise FileOperationError("...")
    # Block path separators and traversal components
    if "/" in name or "\\" in name:
        raise FileOperationError("Name must not contain path separators.")
    if name in (".", "..") or ".." in name.split("/"):
        raise FileOperationError("Name must not contain path traversal components.")
    new_dir = parent / name
    # Verify the resolved path is actually inside parent
    if new_dir.resolve().parent != parent.resolve():
        raise FileOperationError("Invalid directory name.")
    ...
```

---

### VULN-02: Symlink Following in Copy/Move Operations (High)

**File**: `src/mdir/operations/copy.py`, lines 57-58; `src/mdir/operations/move.py`, lines 26
**OWASP**: A01 Broken Access Control

**Description**: `shutil.copytree()` and `shutil.copy2()` follow symlinks by default. If a user selects a symlink for copy, the operation follows the symlink and copies the target content. In a crafted scenario (malicious symlink pointing to sensitive system file), this could exfiltrate data by copying sensitive files into an attacker-visible directory.

For `shutil.copytree()`, symlinks within a directory tree are followed by default, meaning a directory containing a symlink to `/etc/shadow` (on Linux) would copy the actual shadow file.

```python
# copy.py:57 -- follows symlinks by default
shutil.copytree(item.path, dest)          # symlinks_to=False by default
# copy.py:59
shutil.copy2(item.path, dest)             # follows symlinks
```

**Severity**: **High**
- On multi-user systems or if operating on untrusted directory trees, symlink attacks can cause unintended data exposure.

**Fix**:
```python
# For copytree: preserve symlinks as symlinks instead of following them
shutil.copytree(item.path, dest, symlinks=True)

# For individual files: detect and handle symlinks explicitly
if item.is_symlink:
    link_target = os.readlink(item.path)
    os.symlink(link_target, dest)
else:
    shutil.copy2(item.path, dest)
```

---

### VULN-03: Race Condition (TOCTOU) in Copy Conflict Resolution (High)

**File**: `src/mdir/operations/copy.py`, lines 11-34
**OWASP**: A04 Insecure Design

**Description**: The `resolve_conflict()` function checks if a destination path exists, then returns a non-conflicting name. Between the check (`dest.exists()`) and the actual file operation (`shutil.copy2` or `shutil.copytree`), another process could create a file with that name. This is a classic Time-of-Check-Time-of-Use (TOCTOU) race condition.

```python
def resolve_conflict(dest: Path) -> Path:
    if not dest.exists():      # CHECK
        return dest
    # ... generate new name
    while candidate.exists():  # CHECK
        ...
    return candidate           # USE happens later in copy_items
```

**Severity**: **High**
- On single-user desktop use, risk is low in practice. However, if both panels operate on the same directory or another process writes concurrently, data could be silently overwritten.

**Fix**:
```python
# Option A: Use exclusive file creation (best for files)
import os
fd = os.open(str(dest), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
os.close(fd)
shutil.copy2(item.path, dest)

# Option B: Catch FileExistsError and retry
try:
    shutil.copy2(item.path, dest)
except FileExistsError:
    dest = resolve_conflict(dest)
    shutil.copy2(item.path, dest)
```

---

### VULN-04: Race Condition (TOCTOU) in Rename and Mkdir (High)

**File**: `src/mdir/operations/delete.py`, lines 37-41, 59-64
**OWASP**: A04 Insecure Design

**Description**: Both `rename_item()` and `make_directory()` check for existence before performing the operation:

```python
# rename_item -- delete.py:37-41
if new_path.exists():                   # CHECK
    raise FileOperationError(...)
item.path.rename(new_path)              # USE -- could overwrite if created in between

# make_directory -- delete.py:59-64
if new_dir.exists():                    # CHECK
    raise FileOperationError(...)
new_dir.mkdir(parents=False)            # USE -- could fail or conflict
```

**Severity**: **High** (same TOCTOU pattern as VULN-03)

**Fix**: For mkdir, catch `FileExistsError` directly. For rename, use `os.rename()` wrapped in try/except rather than pre-checking:
```python
try:
    new_dir.mkdir(parents=False, exist_ok=False)
except FileExistsError:
    raise FileOperationError(f"Already exists: {name}")
```

---

### VULN-05: Unbounded Conflict Resolution Loop (Medium)

**File**: `src/mdir/operations/copy.py`, lines 30-33
**OWASP**: A04 Insecure Design

**Description**: The `resolve_conflict()` while-loop has no upper bound:

```python
counter = 2
while candidate.exists():
    candidate = parent / f"{base}{counter}{suffix}"
    counter += 1
```

If a directory contains thousands of `file_copy`, `file_copy2`, ..., `file_copy99999` entries, this loop will iterate for a very long time, causing the TUI to become unresponsive. Additionally, there is no protection against integer overflow (theoretical at Python scale) or filesystem name length limits.

**Severity**: **Medium** -- Denial-of-service to the local user only.

**Fix**:
```python
MAX_CONFLICT_RETRIES = 9999
counter = 2
while candidate.exists():
    if counter > MAX_CONFLICT_RETRIES:
        raise FileOperationError(f"Too many name conflicts for: {dest.name}")
    candidate = parent / f"{base}{counter}{suffix}"
    counter += 1
```

---

### VULN-06: Error Message Information Disclosure (Medium)

**File**: `src/mdir/panels/dialogs.py`, lines 119-120; `src/mdir/operations/copy.py`, line 66
**OWASP**: A04 Insecure Design / A09 Logging and Monitoring

**Description**: Error messages expose raw exception details to the user:

```python
# dialogs.py:120 -- preview error shows raw exception
return f"[Preview error: {e}]"

# copy.py:66 -- exposes raw OSError
raise FileOperationError(f"Copy failed: {item.name} -- {e}", item.path)

# status_bar.py:31 -- directly displays error messages
f"[bold red]Error: {message}[/]"
```

Raw exception strings may contain full filesystem paths, internal Python error details, or OS-level error codes that leak information about the system layout and configuration.

**Severity**: **Medium** -- In a local TUI app, the user already has filesystem access. However, if screen contents are shared (screen sharing, screenshots), sensitive paths could be exposed.

**Fix**: Sanitize error messages before display. Map known OSError codes to user-friendly messages:
```python
_ERROR_MAP = {
    errno.EACCES: "Permission denied",
    errno.ENOSPC: "Disk full",
    errno.ENOENT: "File not found",
}
```

---

### VULN-07: No Filename Character Validation (Medium)

**File**: `src/mdir/operations/delete.py`, lines 24-46 (rename_item), lines 49-69 (make_directory)
**OWASP**: A03 Injection

**Description**: While `rename_item()` blocks `/` and `\`, neither function validates against other dangerous or invalid filename characters:
- Windows reserved characters: `<`, `>`, `:`, `"`, `|`, `?`, `*`
- Windows reserved names: `CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, `LPT1-9`
- Null bytes (`\0`)
- Leading/trailing dots or spaces (Windows behavior differences)
- Excessively long names (>255 chars on most filesystems)

A user could attempt to create a file named `CON` on Windows, which would fail with a cryptic OS error, or create names with embedded control characters.

**Severity**: **Medium**

**Fix**:
```python
import re
import sys

_INVALID_CHARS_PATTERN = re.compile(r'[\x00-\x1f<>:"|?*]')
_WINDOWS_RESERVED = {"CON", "PRN", "AUX", "NUL"} | {
    f"{n}{i}" for n in ("COM", "LPT") for i in range(1, 10)
}
MAX_NAME_LENGTH = 255

def validate_filename(name: str) -> None:
    if len(name) > MAX_NAME_LENGTH:
        raise FileOperationError("Name is too long (max 255 characters).")
    if _INVALID_CHARS_PATTERN.search(name):
        raise FileOperationError("Name contains invalid characters.")
    if sys.platform == "win32":
        stem = name.split(".")[0].upper()
        if stem in _WINDOWS_RESERVED:
            raise FileOperationError(f"Reserved name on Windows: {name}")
```

---

### VULN-08: `FileItem.from_path()` Uses `stat()` Which Follows Symlinks (Medium)

**File**: `src/mdir/models/file_item.py`, lines 44-45
**OWASP**: A01 Broken Access Control

**Description**: `path.stat()` follows symlinks and returns the stat of the target file rather than the symlink itself. While `is_symlink()` is correctly detected via `path.is_symlink()`, the `size` and `modified` fields reflect the symlink target. If a symlink points to a very large file or a special file (device node), the stat call could hang or return misleading information.

```python
stat = path.stat()          # follows symlink to target
size = stat.st_size         # size of target, not link
modified = datetime.fromtimestamp(stat.st_mtime)  # mtime of target
```

**Severity**: **Medium** -- Misleading information display and potential for hanging on special files.

**Fix**:
```python
stat = path.lstat()         # stat the symlink itself, not target
```

---

### VULN-09: Preview of Arbitrary Files Without Type Checking (Low)

**File**: `src/mdir/panels/dialogs.py`, lines 109-120
**OWASP**: A04 Insecure Design

**Description**: `PreviewScreen._load_content()` opens any file and attempts UTF-8 decoding with `errors="replace"`. While the 512KB cap prevents memory exhaustion, there is no check on file type. Previewing a binary file (e.g., a large `.exe`) will load 512KB of garbage into memory and render nonsensical output. On systems with special files (Linux `/dev/zero`, `/dev/random`), reading would consume resources.

```python
with open(self._path, encoding="utf-8", errors="replace") as f:
    content = f.read(self.MAX_SIZE)    # reads any file type
```

**Severity**: **Low** -- Local user impact only. The `errors="replace"` prevents crashes.

**Fix**:
```python
import mimetypes

def _load_content(self) -> str:
    # Reject known binary types
    mime, _ = mimetypes.guess_type(str(self._path))
    if mime and not mime.startswith("text/"):
        return f"[Binary file: {mime}]"

    # Reject device files on Linux
    if not self._path.is_file():
        return "[Not a regular file]"
    ...
```

---

### VULN-10: No Maximum Selection Count (Low)

**File**: `src/mdir/models/file_item.py`, lines 164-170 (`select_all`)
**OWASP**: A04 Insecure Design

**Description**: `select_all()` and subsequent operations (copy, move, delete) have no upper bound on the number of selected items. In a directory with hundreds of thousands of files, selecting all and performing a copy would cause the TUI to freeze during the synchronous loop in `copy_items`.

**Severity**: **Low** -- Self-inflicted DoS on a local application.

**Fix**: Add a configurable maximum selection count, or warn the user when selecting more than a threshold:
```python
MAX_SELECTION = 10000
if len(state.items) > MAX_SELECTION:
    # Show warning dialog before proceeding
```

---

### VULN-11: Partial Operation Failure (No Transaction/Rollback) (Low)

**File**: `src/mdir/operations/copy.py`, lines 37-68; `src/mdir/operations/move.py`, lines 11-33
**OWASP**: A04 Insecure Design

**Description**: When copying or moving multiple items, if the operation fails mid-way (e.g., permission denied on the 3rd of 5 files), the first 2 items are already copied/moved, but the error is raised and the operation stops. There is no rollback of successfully completed sub-operations, and the user is not informed about which items succeeded vs. failed.

```python
for item in items:
    ...
    try:
        shutil.copy2(item.path, dest)
        copied.append(dest)
    except PermissionError as e:
        raise PermissionDeniedError(item.path) from e   # <-- items 1,2 already copied
```

**Severity**: **Low** -- Leaves filesystem in an inconsistent state, but the user can manually clean up.

**Fix**: Collect errors per item and report all of them, or implement rollback:
```python
errors = []
for item in items:
    try:
        ...
    except Exception as e:
        errors.append((item, e))
if errors:
    names = ", ".join(item.name for item, _ in errors)
    raise FileOperationError(f"Failed: {names} ({len(copied)} succeeded)")
```

---

### VULN-12: `goto_path` Allows Navigation to Any System Directory (Info)

**File**: `src/mdir/panels/file_panel.py`, lines 183-189; `src/mdir/app.py`, lines 284-300
**OWASP**: A01 Broken Access Control

**Description**: The Ctrl+G "goto path" feature allows navigating to any directory on the filesystem. Combined with copy/move to the opposite panel, a user could inadvertently copy sensitive system files or navigate to protected system directories.

```python
def go_to(self, path_str: str) -> bool:
    path = Path(path_str).expanduser().resolve()
    if path.is_dir():
        self.state.enter_directory(path)
        return True
    return False
```

**Severity**: **Info** -- This is expected behavior for a file manager. It runs with the user's own permissions, so this is by design. However, it is noted here for awareness. If the application ever runs with elevated privileges (e.g., via `sudo`), this becomes a significant risk.

**Recommendation**: If the application needs to be sandboxed in the future, add an optional `--root-dir` flag that constrains navigation to a subtree:
```python
if self._root_dir and not path.is_relative_to(self._root_dir):
    return False
```

---

### VULN-13: Missing Test Coverage for Security-Critical Paths (Medium)

**File**: `tests/test_operations.py`
**OWASP**: A04 Insecure Design

**Description**: The existing test suite has good basic coverage but lacks tests for security-critical edge cases:

| Missing Test Case | Risk |
|-------------------|------|
| `rename_item` with path traversal (`../evil`) | Already blocked, but no test proves it |
| `make_directory` with path traversal (`../../evil`) | NOT blocked (see VULN-01) |
| `make_directory` with special characters (`CON`, `NUL`) | NOT validated |
| Copy/move of symlinks | No test for symlink behavior |
| `resolve_conflict` with very large counter | Unbounded loop |
| `rename_item` with null bytes in name | Not tested |
| Preview of binary/special files | Not tested |

**Severity**: **Medium** -- Missing tests mean regressions can silently reintroduce vulnerabilities.

**Fix**: Add security-focused test cases (see Section 4 below for specific test code).

---

## 3. Summary Matrix

| ID | Vulnerability | File:Line | Severity | OWASP | Fix Effort |
|----|--------------|-----------|----------|-------|------------|
| VULN-01 | Path traversal in `make_directory` | `delete.py:49-69` | Critical | A01,A03 | Low |
| VULN-02 | Symlink following in copy/move | `copy.py:57-59` | High | A01 | Low |
| VULN-03 | TOCTOU in conflict resolution | `copy.py:11-34` | High | A04 | Medium |
| VULN-04 | TOCTOU in rename/mkdir | `delete.py:37-41,59-64` | High | A04 | Low |
| VULN-05 | Unbounded conflict loop | `copy.py:30-33` | Medium | A04 | Low |
| VULN-06 | Error message info disclosure | `dialogs.py:119-120` | Medium | A09 | Low |
| VULN-07 | No filename character validation | `delete.py:24-69` | Medium | A03 | Medium |
| VULN-08 | `stat()` follows symlinks | `file_item.py:44-45` | Medium | A01 | Low |
| VULN-09 | Preview of arbitrary file types | `dialogs.py:109-120` | Low | A04 | Low |
| VULN-10 | No max selection count | `file_item.py:164-170` | Low | A04 | Low |
| VULN-11 | Partial operation no rollback | `copy.py:37-68` | Low | A04 | Medium |
| VULN-12 | Unrestricted directory navigation | `file_panel.py:183-189` | Info | A01 | Low |
| VULN-13 | Missing security test coverage | `tests/` | Medium | A04 | Medium |

---

## 4. Recommended Security Test Cases

```python
"""Security-focused test cases for mdir-tui."""
import os
import sys
import pytest
from pathlib import Path
from mdir.operations.delete import make_directory, rename_item
from mdir.operations.copy import resolve_conflict, copy_items
from mdir.operations.exceptions import FileOperationError
from mdir.models.file_item import FileItem


class TestPathTraversal:
    """VULN-01: Path traversal prevention."""

    def test_mkdir_rejects_path_separator_forward(self, tmp_path):
        with pytest.raises(FileOperationError):
            make_directory(tmp_path, "../../evil")

    def test_mkdir_rejects_path_separator_backward(self, tmp_path):
        with pytest.raises(FileOperationError):
            make_directory(tmp_path, "..\\..\\evil")

    def test_mkdir_rejects_dotdot(self, tmp_path):
        with pytest.raises(FileOperationError):
            make_directory(tmp_path, "..")

    def test_mkdir_rejects_dot(self, tmp_path):
        with pytest.raises(FileOperationError):
            make_directory(tmp_path, ".")

    def test_rename_rejects_path_separator(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("")
        item = FileItem.from_path(f)
        with pytest.raises(FileOperationError):
            rename_item(item, "../evil.txt")

    def test_rename_rejects_backslash(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("")
        item = FileItem.from_path(f)
        with pytest.raises(FileOperationError):
            rename_item(item, "..\\evil.txt")


class TestFilenameValidation:
    """VULN-07: Invalid filename characters."""

    def test_mkdir_rejects_null_byte(self, tmp_path):
        with pytest.raises((FileOperationError, ValueError)):
            make_directory(tmp_path, "bad\x00name")

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows only")
    def test_mkdir_rejects_windows_reserved(self, tmp_path):
        for name in ["CON", "PRN", "AUX", "NUL", "COM1", "LPT1"]:
            with pytest.raises(FileOperationError):
                make_directory(tmp_path, name)


class TestConflictResolutionBounds:
    """VULN-05: Bounded conflict resolution."""

    def test_resolve_conflict_has_upper_bound(self, tmp_path):
        # Create enough conflicts to verify the function does not loop forever
        (tmp_path / "file.txt").write_text("")
        (tmp_path / "file_copy.txt").write_text("")
        for i in range(2, 102):
            (tmp_path / f"file_copy{i}.txt").write_text("")
        # Should still resolve (bounded)
        result = resolve_conflict(tmp_path / "file.txt")
        assert result.name == "file_copy102.txt"


class TestSymlinkSafety:
    """VULN-02, VULN-08: Symlink handling."""

    def test_copy_preserves_symlink(self, tmp_path):
        src = tmp_path / "src"
        dst = tmp_path / "dst"
        src.mkdir()
        dst.mkdir()
        target = src / "target.txt"
        target.write_text("secret")
        link = src / "link.txt"
        try:
            link.symlink_to(target)
        except (OSError, NotImplementedError):
            pytest.skip("Symlinks not supported")
        item = FileItem.from_path(link)
        copied = copy_items([item], dst)
        # After fix: copied file should be a symlink, not a copy of target
        # assert (dst / "link.txt").is_symlink()
```

---

## 5. Fix Priority and Roadmap

### Immediate (before any release)

1. **VULN-01**: Add path separator and traversal validation to `make_directory()`. This is a one-line fix.

### Before Next Release

2. **VULN-02**: Add `symlinks=True` to `shutil.copytree()` and explicit symlink handling in copy.
3. **VULN-04**: Replace TOCTOU checks with exception-based flow in rename/mkdir.
4. **VULN-07**: Add comprehensive filename validation function shared by rename and mkdir.
5. **VULN-13**: Add the security test cases listed in Section 4.

### Next Sprint

6. **VULN-03**: Implement retry-based conflict resolution.
7. **VULN-05**: Add upper bound to conflict resolution loop.
8. **VULN-06**: Sanitize error messages.
9. **VULN-08**: Use `lstat()` instead of `stat()` for symlink-aware metadata.

### Backlog

10. **VULN-09**: Add MIME type checking for preview.
11. **VULN-10**: Add selection count warning.
12. **VULN-11**: Implement per-item error collection for bulk operations.

---

## 6. Dependency Security

| Dependency | Version | Known Vulnerabilities | Notes |
|------------|---------|----------------------|-------|
| textual | >=0.89.0 | None known | TUI framework, no network exposure |
| send2trash | >=1.8.3 | None known | Platform trash integration |
| watchfiles | >=1.0.0 | None known | Rust-based file watcher |
| hatchling | build-only | N/A | Build tool, not runtime |

**Recommendation**: Pin exact versions in a lock file and enable automated dependency scanning (e.g., `pip-audit`, Dependabot).

---

## 7. Threat Model Summary

| Threat | Likelihood | Impact | Mitigated? |
|--------|-----------|--------|------------|
| User accidentally deletes important files | Medium | High | Yes (trash-based delete + confirmation) |
| Path traversal via user input | Low | Critical | Partial (rename yes, mkdir NO) |
| Symlink-based data exfiltration | Low | Medium | No |
| Race condition data loss | Low | Medium | No |
| Application freeze via large directory | Low | Low | No |
| Privilege escalation | Very Low | High | N/A (runs as current user) |

---

## 8. Architecture Recommendations

1. **Input validation layer**: Create a shared `validate_name(name: str) -> None` function in `operations/validators.py` used by both `rename_item` and `make_directory`.

2. **Sandboxing option**: Add an optional `--root` CLI argument that restricts all file operations to a subtree.

3. **Operation logging**: Log all destructive operations (copy, move, delete, rename) to a local log file for audit trail.

4. **Undo support**: Since `send2trash` is used for deletion, consider adding undo for copy/move operations via a journal file.
