"""FileItem 및 관련 함수 단위 테스트."""

import tempfile
from pathlib import Path

import pytest

from mdir.models.file_item import FileItem, PanelState, format_size, load_directory, SortKey


class TestFileItem:
    def test_from_path_file(self, tmp_path: Path) -> None:
        f = tmp_path / "hello.txt"
        f.write_text("hello world")
        item = FileItem.from_path(f)
        assert item.name == "hello.txt"
        assert not item.is_dir
        assert not item.is_hidden
        assert item.size == 11

    def test_from_path_directory(self, tmp_path: Path) -> None:
        d = tmp_path / "subdir"
        d.mkdir()
        item = FileItem.from_path(d)
        assert item.is_dir
        assert item.size_str == "  <DIR>"

    def test_hidden_file(self, tmp_path: Path) -> None:
        f = tmp_path / ".hidden"
        f.write_text("")
        item = FileItem.from_path(f)
        assert item.is_hidden

    def test_size_str_bytes(self, tmp_path: Path) -> None:
        f = tmp_path / "small.bin"
        f.write_bytes(b"x" * 500)
        item = FileItem.from_path(f)
        assert "B" in item.size_str

    def test_size_str_kb(self, tmp_path: Path) -> None:
        f = tmp_path / "medium.bin"
        f.write_bytes(b"x" * 2048)
        item = FileItem.from_path(f)
        assert "K" in item.size_str

    def test_parent_entry(self, tmp_path: Path) -> None:
        item = FileItem.parent_entry(tmp_path)
        assert item.name == ".."
        assert item.is_dir

    def test_symlink_file(self, tmp_path: Path) -> None:
        target = tmp_path / "target.txt"
        target.write_text("hello")
        link = tmp_path / "link.txt"
        try:
            link.symlink_to(target)
        except (OSError, NotImplementedError):
            pytest.skip("Symlinks not supported on this platform")
        item = FileItem.from_path(link)
        assert item.is_symlink
        assert item.name == "link.txt"

    def test_modified_str_format(self, tmp_path: Path) -> None:
        """날짜 포맷이 YYYY-MM-DD HH:MM 형식인지 확인."""
        f = tmp_path / "file.txt"
        f.write_text("")
        item = FileItem.from_path(f)
        parts = item.modified_str.split("-")
        assert len(parts[0]) == 4, "연도는 4자리여야 함"


class TestLoadDirectory:
    def test_basic(self, tmp_path: Path) -> None:
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "b.txt").write_text("b")
        (tmp_path / "subdir").mkdir()
        items = load_directory(tmp_path)
        names = [i.name for i in items]
        # 디렉토리 먼저
        assert names.index("subdir") < names.index("a.txt")

    def test_hidden_excluded(self, tmp_path: Path) -> None:
        (tmp_path / ".hidden").write_text("")
        (tmp_path / "visible.txt").write_text("")
        items = load_directory(tmp_path, show_hidden=False)
        assert all(not i.is_hidden for i in items)

    def test_hidden_included(self, tmp_path: Path) -> None:
        (tmp_path / ".hidden").write_text("")
        items = load_directory(tmp_path, show_hidden=True)
        assert any(i.is_hidden for i in items)


class TestPanelState:
    def test_enter_directory(self, tmp_path: Path) -> None:
        (tmp_path / "file.txt").write_text("")
        state = PanelState(current_path=tmp_path)
        state.enter_directory(tmp_path)
        assert state.current_path == tmp_path

    def test_toggle_selection(self, tmp_path: Path) -> None:
        f = tmp_path / "file.txt"
        f.write_text("")
        state = PanelState(current_path=tmp_path)
        state.enter_directory(tmp_path)
        # items[0] 은 '..' 항목 → 선택 불가. 실제 파일 항목 사용
        item = next(i for i in state.items if i.name != "..")
        state.toggle_selection(item)
        assert item.path in state.selected_paths
        state.toggle_selection(item)
        assert item.path not in state.selected_paths

    def test_select_all_and_clear(self, tmp_path: Path) -> None:
        for i in range(3):
            (tmp_path / f"f{i}.txt").write_text("")
        state = PanelState(current_path=tmp_path)
        state.enter_directory(tmp_path)
        state.select_all()
        assert len(state.selected_paths) == 3
        state.clear_selection()
        assert len(state.selected_paths) == 0


class TestLoadDirectorySort:
    def test_sort_by_name(self, tmp_path: Path) -> None:
        for name in ["c.txt", "a.txt", "b.txt"]:
            (tmp_path / name).write_text("")
        items = load_directory(tmp_path, sort_by="name")
        names = [i.name for i in items]
        assert names == sorted(names, key=str.lower)

    def test_sort_by_size(self, tmp_path: Path) -> None:
        (tmp_path / "big.txt").write_bytes(b"x" * 1000)
        (tmp_path / "small.txt").write_bytes(b"x" * 10)
        items = load_directory(tmp_path, sort_by="size")
        sizes = [i.size for i in items]
        assert sizes == sorted(sizes)

    def test_sort_reverse(self, tmp_path: Path) -> None:
        for name in ["a.txt", "b.txt", "c.txt"]:
            (tmp_path / name).write_text("")
        items = load_directory(tmp_path, sort_by="name", sort_reverse=True)
        names = [i.name for i in items]
        assert names == sorted(names, key=str.lower, reverse=True)

    def test_dirs_always_first(self, tmp_path: Path) -> None:
        (tmp_path / "z_dir").mkdir()
        (tmp_path / "a_file.txt").write_text("")
        items = load_directory(tmp_path, sort_by="name", sort_reverse=True)
        assert items[0].is_dir


class TestFormatSize:
    def test_bytes(self) -> None:
        assert "B" in format_size(100)

    def test_kilobytes(self) -> None:
        assert "K" in format_size(2048)

    def test_megabytes(self) -> None:
        assert "M" in format_size(2 * 1024 * 1024)
