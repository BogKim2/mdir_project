"""파일/폴더 삭제 작업 (휴지통 경유)."""

import re
from pathlib import Path

from send2trash import send2trash

from mdir.models.file_item import FileItem
from mdir.operations.exceptions import FileOperationError

# Windows 예약 문자 및 예약 이름 (VULN-07)
_INVALID_CHARS_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_WINDOWS_RESERVED = re.compile(
    r"^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(\.|$)", re.IGNORECASE
)


def _validate_filename(name: str) -> None:
    """파일/폴더 이름 유효성 검사.

    - 경로 구분자 및 특수문자 차단 (VULN-01, VULN-07)
    - Windows 예약 이름 차단
    - 경로 순회(..) 차단
    """
    if not name or not name.strip():
        raise FileOperationError("이름을 입력하세요.")
    name = name.strip()
    if _INVALID_CHARS_RE.search(name):
        raise FileOperationError("이름에 사용할 수 없는 문자가 포함되어 있습니다.")
    if _WINDOWS_RESERVED.match(name):
        raise FileOperationError(f"시스템 예약 이름은 사용할 수 없습니다: {name}")
    if name in (".", ".."):
        raise FileOperationError("'..' 또는 '.'은 이름으로 사용할 수 없습니다.")


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
    _validate_filename(new_name)

    new_path = item.path.parent / new_name

    # 경로 순회 차단: 결과 경로가 반드시 부모 디렉토리 안에 있어야 함 (VULN-01)
    try:
        if new_path.resolve().parent != item.path.parent.resolve():
            raise FileOperationError("경로 순회가 감지되었습니다.")
    except OSError:
        pass

    # TOCTOU 방지: 존재 여부를 사전 검사하지 않고 OS 오류로 처리 (VULN-04)
    try:
        item.path.rename(new_path)
        return new_path
    except FileExistsError:
        raise FileOperationError(f"이미 존재하는 이름: {new_name}")
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
    _validate_filename(name)

    new_dir = parent / name

    # 경로 순회 차단: 생성 위치가 반드시 부모 디렉토리 안이어야 함 (VULN-01 Critical)
    try:
        resolved_parent = parent.resolve()
        resolved_new = (parent / name).resolve()
        if resolved_new.parent != resolved_parent:
            raise FileOperationError("경로 순회가 감지되었습니다.")
    except OSError:
        pass

    # TOCTOU 방지: 사전 존재 검사 없이 mkdir 예외로 처리 (VULN-04)
    try:
        new_dir.mkdir(parents=False)
        return new_dir
    except FileExistsError:
        raise FileOperationError(f"이미 존재합니다: {name}")
    except PermissionError as e:
        raise FileOperationError(f"권한 없음: {parent}", parent) from e
    except OSError as e:
        raise FileOperationError(f"폴더 생성 실패: {e}") from e
