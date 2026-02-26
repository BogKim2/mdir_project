"""파일 항목 및 패널 상태 데이터 모델."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class FileItem:
    """파일/디렉토리 항목을 나타내는 데이터 클래스."""

    path: Path
    name: str
    is_dir: bool
    is_hidden: bool
    size: int
    modified: datetime
    is_symlink: bool = False
    is_selected: bool = False

    @property
    def size_str(self) -> str:
        """사람이 읽기 좋은 파일 크기 문자열 반환."""
        if self.is_dir:
            return "  <DIR>"
        size = float(self.size)
        for unit in ("B", "K", "M", "G", "T"):
            if size < 1024:
                return f"{size:>7.1f}{unit}"
            size /= 1024
        return f"{size:>7.1f}P"

    @property
    def modified_str(self) -> str:
        """수정 날짜 문자열 반환."""
        return self.modified.strftime("%Y-%m-%d %H:%M")

    @classmethod
    def from_path(cls, path: Path) -> FileItem:
        """Path 객체로부터 FileItem 생성."""
        try:
            stat = path.stat()
            size = stat.st_size
            modified = datetime.fromtimestamp(stat.st_mtime)
        except (PermissionError, OSError):
            size = 0
            modified = datetime.fromtimestamp(0)

        return cls(
            path=path,
            name=path.name,
            is_dir=path.is_dir(),
            is_hidden=path.name.startswith("."),
            size=size,
            modified=modified,
            is_symlink=path.is_symlink(),
        )

    @classmethod
    def parent_entry(cls, path: Path) -> FileItem:
        """상위 폴더 진입을 위한 '..' 항목 생성."""
        return cls(
            path=path.parent,
            name="..",
            is_dir=True,
            is_hidden=False,
            size=0,
            modified=datetime.fromtimestamp(0),
        )


SortKey = str  # "name" | "size" | "modified"


def load_directory(
    path: Path,
    show_hidden: bool = False,
    sort_by: SortKey = "name",
    sort_reverse: bool = False,
) -> list[FileItem]:
    """디렉토리 내용을 읽어 FileItem 목록 반환.

    정렬 순서: 디렉토리 먼저, 지정된 컬럼 기준 정렬.
    sort_by: "name" | "size" | "modified"
    """
    items: list[FileItem] = []

    try:
        entries = list(path.iterdir())
    except PermissionError:
        return []

    for entry in entries:
        item = FileItem.from_path(entry)
        if not show_hidden and item.is_hidden:
            continue
        items.append(item)

    # 정렬 키 선택
    if sort_by == "size":
        key_fn = lambda x: (not x.is_dir, x.size if not x.is_dir else -1)  # noqa: E731
    elif sort_by == "modified":
        key_fn = lambda x: (not x.is_dir, x.modified)  # noqa: E731
    else:  # "name" (기본)
        key_fn = lambda x: (not x.is_dir, x.name.lower())  # noqa: E731

    items.sort(key=key_fn, reverse=sort_reverse)
    # 단, 역순이어도 디렉토리는 항상 앞에 오도록 재정렬
    if sort_reverse:
        dirs = [i for i in items if i.is_dir]
        files = [i for i in items if not i.is_dir]
        items = dirs + files

    return items


@dataclass
class PanelState:
    """파일 패널의 상태를 나타내는 데이터 클래스."""

    current_path: Path
    items: list[FileItem] = field(default_factory=list)
    cursor_index: int = 0
    selected_paths: set[Path] = field(default_factory=set)
    sort_by: str = "name"  # "name" | "size" | "modified"
    sort_reverse: bool = False
    show_hidden: bool = False

    @property
    def active_item(self) -> FileItem | None:
        """현재 커서 위치의 파일 항목 반환."""
        if self.items and 0 <= self.cursor_index < len(self.items):
            return self.items[self.cursor_index]
        return None

    def get_selected_items(self) -> list[FileItem]:
        """다중 선택 항목 반환. 선택 없으면 커서 항목 반환."""
        if self.selected_paths:
            return [item for item in self.items if item.path in self.selected_paths]
        if self.active_item and self.active_item.name != "..":
            return [self.active_item]
        return []

    def toggle_selection(self, item: FileItem) -> None:
        """항목 선택 토글 (.. 항목 제외)."""
        if item.name == "..":
            return
        if item.path in self.selected_paths:
            self.selected_paths.discard(item.path)
            item.is_selected = False
        else:
            self.selected_paths.add(item.path)
            item.is_selected = True

    def clear_selection(self) -> None:
        """전체 선택 해제."""
        for item in self.items:
            item.is_selected = False
        self.selected_paths.clear()

    def select_all(self) -> None:
        """전체 선택 (.. 항목 제외)."""
        self.selected_paths.clear()
        for item in self.items:
            if item.name != "..":
                item.is_selected = True
                self.selected_paths.add(item.path)

    def refresh(self) -> None:
        """현재 디렉토리 재로드."""
        old_name = self.active_item.name if self.active_item else None
        self.items = []
        if self.current_path.parent != self.current_path:
            self.items.append(FileItem.parent_entry(self.current_path))
        self.items.extend(
            load_directory(self.current_path, self.show_hidden, self.sort_by, self.sort_reverse)
        )
        self.selected_paths.clear()

        # 이전 커서 위치 복원 시도
        if old_name:
            for i, item in enumerate(self.items):
                if item.name == old_name:
                    self.cursor_index = i
                    return
        self.cursor_index = min(self.cursor_index, max(0, len(self.items) - 1))

    def enter_directory(self, path: Path) -> None:
        """디렉토리 진입."""
        self.current_path = path.resolve()
        self.cursor_index = 0
        self.selected_paths.clear()
        self.items = []
        if self.current_path.parent != self.current_path:
            self.items.append(FileItem.parent_entry(self.current_path))
        self.items.extend(
            load_directory(self.current_path, self.show_hidden, self.sort_by, self.sort_reverse)
        )

    def set_sort(self, sort_by: str, sort_reverse: bool = False) -> None:
        """정렬 기준 변경 후 목록 재로드."""
        self.sort_by = sort_by
        self.sort_reverse = sort_reverse
        self.refresh()

    def disk_info(self) -> tuple[int, int]:
        """(free_bytes, total_bytes) 반환."""
        try:
            stat = os.statvfs(str(self.current_path)) if os.name != "nt" else None
            if stat:
                return stat.f_bavail * stat.f_frsize, stat.f_blocks * stat.f_frsize
            # Windows
            import shutil
            usage = shutil.disk_usage(str(self.current_path))
            return usage.free, usage.total
        except Exception:
            return 0, 0


def format_size(size: int) -> str:
    """바이트를 사람이 읽기 좋은 문자열로 변환."""
    for unit in ("B", "K", "M", "G", "T"):
        if size < 1024:
            return f"{size:.1f}{unit}"
        size //= 1024
    return f"{size:.1f}P"
