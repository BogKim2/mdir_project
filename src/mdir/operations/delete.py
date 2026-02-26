"""파일/폴더 삭제 작업 (휴지통 경유)."""

from pathlib import Path

from send2trash import send2trash

from mdir.models.file_item import FileItem
from mdir.operations.exceptions import FileOperationError


def delete_items(items: list[FileItem]) -> None:
    """파일/폴더를 시스템 휴지통으로 이동 (send2trash).

    직접 삭제(os.remove/shutil.rmtree)는 사용하지 않음.
    Raises: FileOperationError
    """
    for item in items:
        try:
            send2trash(str(item.path))
        except Exception as e:
            raise FileOperationError(f"삭제 실패: {item.name}", item.path) from e


def rename_item(item: FileItem, new_name: str) -> Path:
    """파일/폴더 이름 변경.

    Returns: 변경된 새 경로
    Raises: FileOperationError
    """
    new_name = new_name.strip()
    if not new_name:
        raise FileOperationError("이름을 입력하세요.")
    if "/" in new_name or "\\" in new_name:
        raise FileOperationError("이름에 경로 구분자를 사용할 수 없습니다.")

    new_path = item.path.parent / new_name
    if new_path.exists():
        raise FileOperationError(f"이미 존재하는 이름: {new_name}")

    try:
        item.path.rename(new_path)
        return new_path
    except PermissionError as e:
        raise FileOperationError(f"권한 없음: {item.name}", item.path) from e
    except OSError as e:
        raise FileOperationError(f"이름 변경 실패: {e}", item.path) from e


def make_directory(parent: Path, name: str) -> Path:
    """새 디렉토리 생성.

    Returns: 생성된 디렉토리 경로
    Raises: FileOperationError
    """
    name = name.strip()
    if not name:
        raise FileOperationError("폴더 이름을 입력하세요.")

    new_dir = parent / name
    if new_dir.exists():
        raise FileOperationError(f"이미 존재합니다: {name}")

    try:
        new_dir.mkdir(parents=False)
        return new_dir
    except PermissionError as e:
        raise FileOperationError(f"권한 없음: {parent}", parent) from e
    except OSError as e:
        raise FileOperationError(f"폴더 생성 실패: {e}") from e
