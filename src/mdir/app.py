"""mdir-tui 메인 애플리케이션."""

from __future__ import annotations

import asyncio
from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal

from mdir.models.file_item import FileItem
from mdir.operations.copy import copy_items
from mdir.operations.delete import delete_items, make_directory, rename_item
from mdir.operations.exceptions import DiskFullError, FileOperationError, PathNotFoundError, PermissionDeniedError
from mdir.operations.move import move_items
from mdir.panels.dialogs import ConfirmScreen, InputScreen, PreviewScreen
from mdir.panels.file_panel import FilePanel, FilePanelCursorMoved, FilePanelFileSelected
from mdir.panels.status_bar import FunctionBar, StatusBar


class MdirApp(App):
    """mdir-tui: 모던 두 패널 TUI 파일 매니저."""

    CSS_PATH = "styles/mdir.tcss"

    BINDINGS = [
        Binding("tab", "switch_panel", "패널 전환", show=False, priority=True),
        Binding("f2", "rename", "이름변경", priority=True),
        Binding("f3", "preview", "보기", priority=True),
        Binding("f5", "copy", "복사", priority=True),
        Binding("f6", "move", "이동", priority=True),
        Binding("f7", "mkdir", "새 폴더", priority=True),
        Binding("f8", "delete", "삭제", priority=True),
        Binding("f10", "quit", "종료", priority=True),
        Binding("q", "quit", "종료", show=False),
        Binding("ctrl+h", "toggle_hidden", "숨김 토글", show=False, priority=True),
        Binding("ctrl+g", "goto_path", "경로 이동", show=False, priority=True),
        Binding("ctrl+a", "select_all", "전체 선택", show=False, priority=True),
        Binding("ctrl+s", "cycle_sort", "정렬 변경", show=False, priority=True),
        # 다이얼로그 Input 위젯과 충돌하지 않도록 priority=True 제거
        Binding("up", "cursor_up", "위", show=False),
        Binding("down", "cursor_down", "아래", show=False),
        Binding("enter", "enter_item", "진입", show=False),
        Binding("backspace", "go_parent", "상위 폴더", show=False),
        Binding("space", "toggle_select", "선택", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._active_panel_id = "left"

    def compose(self) -> ComposeResult:
        cwd = Path.cwd()
        with Horizontal(id="panels-container"):
            yield FilePanel(id="left", start_path=cwd)
            yield FilePanel(id="right", start_path=cwd)
        yield StatusBar()
        yield FunctionBar()

    def on_mount(self) -> None:
        self._active_panel.focus()
        self._update_status()
        # 포커스 변경을 감지하여 active panel 동기화 (마우스 클릭, Tab 등 모든 경로)
        self.watch(self.screen, "focused", self._sync_active_panel)

    # ── 패널 접근 헬퍼 ────────────────────────

    @property
    def _active_panel(self) -> FilePanel:
        return self.query_one(f"#{self._active_panel_id}", FilePanel)

    @property
    def _inactive_panel(self) -> FilePanel:
        other = "right" if self._active_panel_id == "left" else "left"
        return self.query_one(f"#{other}", FilePanel)

    @property
    def _status_bar(self) -> StatusBar:
        return self.query_one(StatusBar)

    # ── 액션 ─────────────────────────────────

    def _sync_active_panel(self, focused) -> None:
        """포커스된 위젯 기준으로 active panel ID를 동기화."""
        if focused is None:
            return
        fid = getattr(focused, "id", "") or ""
        if fid.startswith("table-"):
            panel_id = fid.replace("table-", "")
            if panel_id in ("left", "right") and panel_id != self._active_panel_id:
                self._active_panel_id = panel_id
                self._update_status()

    def action_switch_panel(self) -> None:
        """Tab: 반대 패널로 포커스 이동."""
        self._active_panel_id = "right" if self._active_panel_id == "left" else "left"
        # FilePanel이 아닌 내부 DataTable에 직접 포커스
        self._active_panel.query_one("DataTable").focus()
        self._update_status()

    def action_cursor_up(self) -> None:
        if len(self.screen_stack) > 1:
            return
        self._active_panel.navigate_up()

    def action_cursor_down(self) -> None:
        if len(self.screen_stack) > 1:
            return
        self._active_panel.navigate_down()

    def action_enter_item(self) -> None:
        """Enter: DataTable이 priority 없이 처리하므로 fallback 용도."""
        pass

    def action_go_parent(self) -> None:
        """Backspace: 상위 디렉토리."""
        if len(self.screen_stack) > 1:
            return
        self._active_panel.go_parent()
        self._update_status()

    def action_toggle_hidden(self) -> None:
        """Ctrl+H: 숨김 파일 표시 토글."""
        self._active_panel.toggle_hidden()
        self._update_status()

    def action_toggle_select(self) -> None:
        """Space: 항목 선택 토글."""
        self._active_panel.toggle_selection()
        self._update_status()

    def action_select_all(self) -> None:
        """Ctrl+A: 전체 선택/해제."""
        self._active_panel.select_all()
        self._update_status()

    def action_cycle_sort(self) -> None:
        """Ctrl+S: 정렬 기준 순환 (이름→크기→날짜, FR-13 보완)."""
        state = self._active_panel.state
        cycle = {"name": "size", "size": "modified", "modified": "name"}
        next_sort = cycle.get(state.sort_by, "name")
        self._active_panel.cycle_sort(
            {"name": "name", "size": "size", "modified": "date"}[next_sort]
        )
        self._update_status()

    def action_preview(self) -> None:
        """F3: 파일 미리보기."""
        item = self._active_panel.state.active_item
        if item is None or item.is_dir:
            return
        self.push_screen(PreviewScreen(item.path))

    @work
    async def action_copy(self) -> None:
        """F5: 반대 패널로 파일 복사."""
        items = self._active_panel.get_selected_items()
        if not items:
            return
        dest = self._inactive_panel.current_path
        names = _format_names(items)

        confirmed = await self.push_screen_wait(
            ConfirmScreen(
                title=" 복사 ",
                message=f"{names}\n→ {dest}",
            )
        )
        if not confirmed:
            return

        try:
            await asyncio.to_thread(copy_items, items, dest)
            self._inactive_panel.refresh_current()
            self._active_panel.state.clear_selection()
            self._active_panel.refresh_current()
            self._status_bar.update(left=f"복사 완료: {names}")
        except PermissionDeniedError as e:
            self._status_bar.set_error(str(e))
        except DiskFullError:
            self._status_bar.set_error("디스크 공간이 부족합니다.")
        except FileOperationError as e:
            self._status_bar.set_error(str(e))

    @work
    async def action_move(self) -> None:
        """F6: 반대 패널로 파일 이동."""
        items = self._active_panel.get_selected_items()
        if not items:
            return
        dest = self._inactive_panel.current_path
        names = _format_names(items)

        confirmed = await self.push_screen_wait(
            ConfirmScreen(
                title=" 이동 ",
                message=f"{names}\n→ {dest}",
            )
        )
        if not confirmed:
            return

        try:
            await asyncio.to_thread(move_items, items, dest)
            self._active_panel.refresh_current()
            self._inactive_panel.refresh_current()
            self._status_bar.update(left=f"이동 완료: {names}")
        except FileOperationError as e:
            self._status_bar.set_error(str(e))

    @work
    async def action_delete(self) -> None:
        """F8: 선택 항목 삭제 (휴지통)."""
        items = self._active_panel.get_selected_items()
        if not items:
            return
        names = _format_names(items)

        confirmed = await self.push_screen_wait(
            ConfirmScreen(
                title=" 삭제 (휴지통으로 이동) ",
                message=f"{names}",
            )
        )
        if not confirmed:
            return

        try:
            await asyncio.to_thread(delete_items, items)
            self._active_panel.refresh_current()
            self._refresh_sibling_if_same_path()
            self._status_bar.update(left=f"삭제 완료: {names}")
        except FileOperationError as e:
            self._status_bar.set_error(str(e))

    @work
    async def action_rename(self) -> None:
        """F2: 파일/폴더 이름 변경."""
        item = self._active_panel.state.active_item
        if item is None or item.name == "..":
            return

        new_name = await self.push_screen_wait(
            InputScreen(
                title=" 이름 변경 ",
                prompt=f"현재 이름: {item.name}",
                default=item.name,
            )
        )
        if not new_name or new_name == item.name:
            return

        try:
            rename_item(item, new_name)
            self._active_panel.refresh_current()
            self._refresh_sibling_if_same_path()
            self._status_bar.update(left=f"이름 변경: {item.name} → {new_name}")
        except FileOperationError as e:
            self._status_bar.set_error(str(e))

    @work
    async def action_mkdir(self) -> None:
        """F7: 새 폴더 생성."""
        folder_name = await self.push_screen_wait(
            InputScreen(
                title=" 새 폴더 ",
                prompt="폴더 이름 입력:",
                default="새 폴더",
            )
        )
        if not folder_name:
            return

        try:
            make_directory(self._active_panel.current_path, folder_name)
            self._active_panel.refresh_current()
            self._refresh_sibling_if_same_path()
            self._status_bar.update(left=f"폴더 생성: {folder_name}")
        except FileOperationError as e:
            self._status_bar.set_error(str(e))

    @work
    async def action_goto_path(self) -> None:
        """Ctrl+G: 경로 직접 입력."""
        current = str(self._active_panel.current_path)
        new_path = await self.push_screen_wait(
            InputScreen(
                title=" 경로 이동 ",
                prompt="이동할 경로:",
                default=current,
            )
        )
        if not new_path:
            return
        if not self._active_panel.go_to(new_path):
            self._status_bar.set_error(f"경로를 찾을 수 없음: {new_path}")
        else:
            self._update_status()

    # ── 이벤트 핸들러 ─────────────────────────

    def on_file_panel_cursor_moved(self, message: FilePanelCursorMoved) -> None:
        self._update_status()

    def on_file_panel_file_selected(self, message: FilePanelFileSelected) -> None:
        """Enter로 파일 선택 시 미리보기 화면 열기."""
        self.push_screen(PreviewScreen(message.item.path))

    # ── 내부 헬퍼 ─────────────────────────────

    def _refresh_sibling_if_same_path(self) -> None:
        """비활성 패널이 활성 패널과 같은 경로이면 함께 갱신."""
        if self._inactive_panel.current_path == self._active_panel.current_path:
            self._inactive_panel.refresh_current()

    def _update_panel_classes(self) -> None:
        """활성/비활성 패널 CSS 클래스 및 경로 바 표시기 갱신."""
        for panel_id in ("left", "right"):
            panel = self.query_one(f"#{panel_id}", FilePanel)
            panel.set_active(panel_id == self._active_panel_id)

    def _update_status(self) -> None:
        panel = self._active_panel
        # 현재 경로가 사라진 경우 상위 폴더로 자동 이동
        if not panel.current_path.exists():
            parent = panel.current_path.parent
            if parent.exists():
                panel.go_to(str(parent))
                self._status_bar.update(left=f"[경로 없음] 상위 폴더로 이동: {parent}")
                return
        self._update_panel_classes()
        self._status_bar.update(
            left=str(panel.current_path),
            right=panel.status_text(),
        )


def _format_names(items: list[FileItem]) -> str:
    """파일 목록을 표시용 문자열로 변환."""
    if len(items) == 1:
        return items[0].name
    return f"{items[0].name} 외 {len(items) - 1}개"


def main() -> None:
    """엔트리포인트."""
    app = MdirApp()
    app.run()


if __name__ == "__main__":
    main()
