"""파일 작업 단위 테스트."""

from pathlib import Path
from unittest.mock import patch

import pytest

from mdir.models.file_item import FileItem
from mdir.operations.copy import copy_items, resolve_conflict
from mdir.operations.delete import delete_items, make_directory, rename_item
from mdir.operations.exceptions import FileOperationError, PermissionDeniedError
from mdir.operations.move import move_items


class TestResolveConflict:
    def test_no_conflict(self, tmp_path: Path) -> None:
        dest = tmp_path / "file.txt"
        assert resolve_conflict(dest) == dest

    def test_conflict_adds_copy(self, tmp_path: Path) -> None:
        dest = tmp_path / "file.txt"
        dest.write_text("")
        result = resolve_conflict(dest)
        assert result.name == "file_copy.txt"

    def test_conflict_increments(self, tmp_path: Path) -> None:
        (tmp_path / "file.txt").write_text("")
        (tmp_path / "file_copy.txt").write_text("")
        result = resolve_conflict(tmp_path / "file.txt")
        assert result.name == "file_copy2.txt"


class TestCopyItems:
    def test_copy_file(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        dst = tmp_path / "dst"
        src.mkdir()
        dst.mkdir()
        f = src / "hello.txt"
        f.write_text("hello")
        item = FileItem.from_path(f)
        copied = copy_items([item], dst)
        assert len(copied) == 1
        assert (dst / "hello.txt").read_text() == "hello"

    def test_copy_directory(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        dst = tmp_path / "dst"
        src.mkdir()
        dst.mkdir()
        d = src / "mydir"
        d.mkdir()
        (d / "inner.txt").write_text("inner")
        item = FileItem.from_path(d)
        copied = copy_items([item], dst)
        assert (dst / "mydir" / "inner.txt").exists()

    def test_copy_conflict(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        dst = tmp_path / "dst"
        src.mkdir()
        dst.mkdir()
        f = src / "file.txt"
        f.write_text("new")
        (dst / "file.txt").write_text("old")
        item = FileItem.from_path(f)
        copied = copy_items([item], dst)
        assert copied[0].name == "file_copy.txt"


class TestMoveItems:
    def test_move_file(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        dst = tmp_path / "dst"
        src.mkdir()
        dst.mkdir()
        f = src / "move_me.txt"
        f.write_text("data")
        item = FileItem.from_path(f)
        move_items([item], dst)
        assert not f.exists()
        assert (dst / "move_me.txt").exists()


class TestDeleteItems:
    def test_delete_calls_send2trash(self, tmp_path: Path) -> None:
        f = tmp_path / "delete_me.txt"
        f.write_text("bye")
        item = FileItem.from_path(f)
        with patch("mdir.operations.delete.send2trash") as mock_trash:
            delete_items([item])
            mock_trash.assert_called_once_with(str(f))

    def test_delete_failure_raises(self, tmp_path: Path) -> None:
        f = tmp_path / "file.txt"
        f.write_text("")
        item = FileItem.from_path(f)
        with patch("mdir.operations.delete.send2trash", side_effect=Exception("fail")):
            with pytest.raises(FileOperationError):
                delete_items([item])


class TestRenameItem:
    def test_rename(self, tmp_path: Path) -> None:
        f = tmp_path / "old.txt"
        f.write_text("")
        item = FileItem.from_path(f)
        new_path = rename_item(item, "new.txt")
        assert new_path.name == "new.txt"
        assert new_path.exists()

    def test_rename_empty_name(self, tmp_path: Path) -> None:
        f = tmp_path / "file.txt"
        f.write_text("")
        item = FileItem.from_path(f)
        with pytest.raises(FileOperationError):
            rename_item(item, "")

    def test_rename_conflict(self, tmp_path: Path) -> None:
        f = tmp_path / "a.txt"
        f.write_text("")
        (tmp_path / "b.txt").write_text("")
        item = FileItem.from_path(f)
        with pytest.raises(FileOperationError):
            rename_item(item, "b.txt")


class TestMakeDirectory:
    def test_create(self, tmp_path: Path) -> None:
        new_dir = make_directory(tmp_path, "newdir")
        assert new_dir.is_dir()

    def test_empty_name(self, tmp_path: Path) -> None:
        with pytest.raises(FileOperationError):
            make_directory(tmp_path, "")

    def test_already_exists(self, tmp_path: Path) -> None:
        (tmp_path / "existing").mkdir()
        with pytest.raises(FileOperationError):
            make_directory(tmp_path, "existing")
