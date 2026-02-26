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


# ── 보안 테스트 (VULN-01, VULN-07) ──────────────────────────────────

class TestSecurityPathTraversal:
    """경로 순회 공격 차단 테스트 (VULN-01 Critical)."""

    def test_mkdir_dotdot_blocked(self, tmp_path: Path) -> None:
        """'..' 포함 폴더명으로 경로 순회 시도 차단."""
        with pytest.raises(FileOperationError):
            make_directory(tmp_path, "../escaped")

    def test_mkdir_backslash_path_blocked(self, tmp_path: Path) -> None:
        """백슬래시 경로 구분자 차단."""
        with pytest.raises(FileOperationError):
            make_directory(tmp_path, "sub\\escape")

    def test_mkdir_slash_path_blocked(self, tmp_path: Path) -> None:
        """슬래시 경로 구분자 차단."""
        with pytest.raises(FileOperationError):
            make_directory(tmp_path, "sub/escape")

    def test_rename_dotdot_blocked(self, tmp_path: Path) -> None:
        """이름 변경 시 '..' 경로 순회 차단."""
        f = tmp_path / "file.txt"
        f.write_text("")
        item = FileItem.from_path(f)
        with pytest.raises(FileOperationError):
            rename_item(item, "../outside.txt")

    def test_rename_slash_blocked(self, tmp_path: Path) -> None:
        """이름 변경 시 슬래시 경로 구분자 차단."""
        f = tmp_path / "file.txt"
        f.write_text("")
        item = FileItem.from_path(f)
        with pytest.raises(FileOperationError):
            rename_item(item, "sub/file.txt")


class TestSecurityFilenameValidation:
    """파일명 유효성 검사 테스트 (VULN-07)."""

    def test_windows_reserved_name_con(self, tmp_path: Path) -> None:
        """Windows 예약 이름 CON 차단."""
        with pytest.raises(FileOperationError):
            make_directory(tmp_path, "CON")

    def test_windows_reserved_name_nul(self, tmp_path: Path) -> None:
        """Windows 예약 이름 NUL 차단."""
        with pytest.raises(FileOperationError):
            make_directory(tmp_path, "NUL")

    def test_invalid_char_colon(self, tmp_path: Path) -> None:
        """콜론(:) 문자 차단."""
        with pytest.raises(FileOperationError):
            make_directory(tmp_path, "folder:name")

    def test_invalid_char_pipe(self, tmp_path: Path) -> None:
        """|  문자 차단."""
        with pytest.raises(FileOperationError):
            make_directory(tmp_path, "folder|name")

    def test_dotdot_name_blocked(self, tmp_path: Path) -> None:
        """'..' 이름 자체 차단."""
        with pytest.raises(FileOperationError):
            make_directory(tmp_path, "..")


class TestSecurityConflictLoop:
    """충돌 해결 무한루프 방지 테스트 (VULN-05)."""

    def test_conflict_limit(self, tmp_path: Path) -> None:
        """최대 재시도 초과 시 FileOperationError 발생."""
        from mdir.operations.copy import _MAX_CONFLICT_RETRIES
        # base 파일과 _copy, _copy2 ... _copyN 전부 생성
        (tmp_path / "file.txt").write_text("")
        (tmp_path / "file_copy.txt").write_text("")
        for i in range(2, _MAX_CONFLICT_RETRIES + 1):
            (tmp_path / f"file_copy{i}.txt").write_text("")
        with pytest.raises(FileOperationError, match="충돌 해결 실패"):
            resolve_conflict(tmp_path / "file.txt")
