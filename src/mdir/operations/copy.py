"""파일/폴더 복사 작업."""

import shutil
from collections.abc import Callable
from pathlib import Path

from mdir.models.file_item import FileItem
from mdir.operations.exceptions import DiskFullError, FileOperationError, PermissionDeniedError

# 충돌 해결 최대 시도 횟수 (VULN-05)
_MAX_CONFLICT_RETRIES = 999


def resolve_conflict(dest: Path) -> Path:
    """이름 충돌 시 새 이름을 자동 생성.

    예) file.txt → file_copy.txt → file_copy2.txt
    최대 시도 횟수: _MAX_CONFLICT_RETRIES (VULN-05 무한루프 방지)
    """
    if not dest.exists():
        return dest

    stem = dest.stem
    suffix = dest.suffix
    parent = dest.parent

    base = f"{stem}_copy" if not stem.endswith("_copy") else stem

    candidate = parent / f"{base}{suffix}"
    counter = 2
    while candidate.exists() and counter <= _MAX_CONFLICT_RETRIES:
        candidate = parent / f"{base}{counter}{suffix}"
        counter += 1

    if counter > _MAX_CONFLICT_RETRIES:
        raise FileOperationError(f"충돌 해결 실패: {dest.name} — 대체 이름을 찾을 수 없습니다.")

    return candidate


def copy_items(
    items: list[FileItem],
    dest_dir: Path,
    on_progress: Callable[[str], None] | None = None,
) -> list[Path]:
    """파일/폴더를 dest_dir 로 복사.

    - 파일: shutil.copy2 (메타데이터 보존)
    - 폴더: shutil.copytree (symlinks=True 로 심링크 원본 유지, VULN-02)
    - 이름 충돌: 자동 이름 해결
    Returns: 복사된 경로 목록
    """
    copied: list[Path] = []

    for item in items:
        # TOCTOU 완화: resolve_conflict 결과를 즉시 사용하고 OS 예외로 처리 (VULN-03)
        dest = resolve_conflict(dest_dir / item.name)
        if on_progress:
            on_progress(item.name)
        try:
            if item.is_dir:
                # symlinks=True: 심링크를 따라가지 않고 심링크 자체를 복사 (VULN-02)
                shutil.copytree(item.path, dest, symlinks=True)
            else:
                shutil.copy2(item.path, dest)
            copied.append(dest)
        except PermissionError as e:
            raise PermissionDeniedError(item.path) from e
        except OSError as e:
            if e.errno == 28:  # ENOSPC: No space left on device
                raise DiskFullError(dest) from e
            raise FileOperationError(f"복사 실패: {item.name}", item.path) from e

    return copied
