"""파일/폴더 복사 작업."""

import shutil
from collections.abc import Callable
from pathlib import Path

from mdir.models.file_item import FileItem
from mdir.operations.exceptions import DiskFullError, FileOperationError, PermissionDeniedError


def resolve_conflict(dest: Path) -> Path:
    """이름 충돌 시 새 이름을 자동 생성.

    예) file.txt → file_copy.txt → file_copy2.txt
    """
    if not dest.exists():
        return dest

    stem = dest.stem
    suffix = dest.suffix
    parent = dest.parent

    # '_copy' 접미사가 이미 있으면 숫자 증가
    if stem.endswith("_copy"):
        base = stem
    else:
        base = f"{stem}_copy"

    candidate = parent / f"{base}{suffix}"
    counter = 2
    while candidate.exists():
        candidate = parent / f"{base}{counter}{suffix}"
        counter += 1
    return candidate


def copy_items(
    items: list[FileItem],
    dest_dir: Path,
    on_progress: Callable[[str], None] | None = None,
) -> list[Path]:
    """파일/폴더를 dest_dir 로 복사.

    - 파일: shutil.copy2 (메타데이터 보존)
    - 폴더: shutil.copytree
    - 이름 충돌: 자동 이름 해결
    Returns: 복사된 경로 목록
    """
    copied: list[Path] = []

    for item in items:
        dest = resolve_conflict(dest_dir / item.name)
        if on_progress:
            on_progress(item.name)
        try:
            if item.is_dir:
                shutil.copytree(item.path, dest)
            else:
                shutil.copy2(item.path, dest)
            copied.append(dest)
        except PermissionError as e:
            raise PermissionDeniedError(item.path) from e
        except OSError as e:
            if e.errno == 28:  # ENOSPC: No space left on device
                raise DiskFullError(dest) from e
            raise FileOperationError(f"복사 실패: {item.name} — {e}", item.path) from e

    return copied
