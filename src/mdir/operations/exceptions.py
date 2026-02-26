"""파일 작업 예외 클래스."""

from pathlib import Path


class MdirError(Exception):
    """mdir-tui 기본 예외."""


class FileOperationError(MdirError):
    """파일 작업 실패."""

    def __init__(self, message: str, path: Path | None = None) -> None:
        super().__init__(message)
        self.path = path


class PermissionDeniedError(MdirError):
    """파일/디렉토리 접근 권한 없음."""

    def __init__(self, path: Path) -> None:
        super().__init__(f"권한 없음: {path}")
        self.path = path


class PathNotFoundError(MdirError):
    """경로를 찾을 수 없음."""

    def __init__(self, path: Path) -> None:
        super().__init__(f"경로 없음: {path}")
        self.path = path


class DiskFullError(MdirError):
    """디스크 공간 부족."""

    def __init__(self, path: Path | None = None) -> None:
        super().__init__("디스크 공간이 부족합니다.")
        self.path = path
