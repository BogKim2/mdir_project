"""파일/폴더 이동 작업."""

import shutil
from pathlib import Path

from mdir.models.file_item import FileItem
from mdir.operations.copy import resolve_conflict
from mdir.operations.exceptions import FileOperationError


def move_items(
    items: list[FileItem],
    dest_dir: Path,
) -> list[Path]:
    """파일/폴더를 dest_dir 로 이동.

    - shutil.move 사용 (같은 FS: rename / 다른 FS: copy+delete)
    - 이름 충돌: 자동 이름 해결
    Returns: 이동된 경로 목록
    """
    moved: list[Path] = []

    for item in items:
        dest = resolve_conflict(dest_dir / item.name)
        try:
            shutil.move(str(item.path), dest)
            moved.append(dest)
        except PermissionError as e:
            raise FileOperationError(f"권한 없음: {item.name}", item.path) from e
        except OSError as e:
            raise FileOperationError(f"이동 실패: {item.name} — {e}", item.path) from e

    return moved
