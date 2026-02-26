"""파일 패널 위젯 (PathBar + FileTable)."""

from pathlib import Path

from rich.markup import escape as markup_escape
from textual.app import ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.widget import Widget
from textual.widgets import DataTable, Label

from mdir.models.file_item import FileItem, PanelState, format_size

# 컬럼 키 상수
COL_NAME = "name"
COL_SIZE = "size"
COL_DATE = "date"

# 파일 타입별 색상 마크업
_DIR_STYLE = "bold bright_blue"
_SYM_STYLE = "bright_magenta"
_HIDDEN_STYLE = "#666677"
_SELECT_STYLE = "bold yellow"
_NORMAL_STYLE = ""

# 정렬 컬럼 순환: 이름 → 크기 → 날짜
_SORT_CYCLE = {"name": "size", "size": "modified", "modified": "name"}
_SORT_LABELS = {"name": "이름", "size": "크기", "modified": "날짜"}


def _item_markup(item: FileItem) -> tuple[str, str, str]:
    """FileItem → (name_markup, size_str, date_str) 반환."""
    if item.is_selected:
        style = _SELECT_STYLE
    elif item.is_dir and item.name != "..":
        style = _DIR_STYLE
    elif item.is_symlink:
        style = _SYM_STYLE
    elif item.is_hidden:
        style = _HIDDEN_STYLE
    else:
        style = _NORMAL_STYLE

    display_name = item.name
    if item.is_dir and item.name != "..":
        display_name = f"[{item.name}]"
    if item.is_symlink:
        display_name = f"{item.name} →"

    # 대괄호 등 Rich 마크업 특수문자를 이스케이프 처리
    safe_name = markup_escape(display_name)
    name_cell = f"[{style}]{safe_name}[/{style}]" if style else safe_name
    size_cell = item.size_str
    date_cell = item.modified_str if item.name != ".." else ""
    return name_cell, size_cell, date_cell


class FilePanelCursorMoved(Message):
    """커서 이동 알림 메시지."""

    def __init__(self, panel: "FilePanel") -> None:
        super().__init__()
        self.panel = panel


class FilePanelFileSelected(Message):
    """Enter 키로 파일 선택 시 미리보기 요청 메시지."""

    def __init__(self, panel: "FilePanel", item: FileItem) -> None:
        super().__init__()
        self.panel = panel
        self.item = item


class FilePanel(Widget):
    """두 패널 파일 매니저의 단일 패널.

    구성:
        PathBar (Label) — 현재 경로 표시
        FileTable (DataTable) — 파일 목록
    """

    DEFAULT_CSS = """
    FilePanel {
        layout: vertical;
        width: 1fr;
    }
    """

    BINDINGS = [
        Binding("space", "toggle_select", "선택", show=False),
    ]

    def __init__(self, start_path: Path | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.state = PanelState(
            current_path=(start_path or Path.cwd()).resolve()
        )
        self._is_active: bool = False

    def compose(self) -> ComposeResult:
        yield Label("", classes="path-bar", id=f"path-{self.id}")
        table = DataTable(id=f"table-{self.id}", cursor_type="row", zebra_stripes=True)
        table.add_column("이름 ↕", key=COL_NAME, width=28)
        table.add_column("크기", key=COL_SIZE, width=9)
        table.add_column("날짜", key=COL_DATE, width=14)
        yield table

    def on_mount(self) -> None:
        # items는 빈 리스트로 초기화되므로 마운트 시 디렉토리 로드 필요
        self.state.enter_directory(self.state.current_path)
        self._refresh_table()

    # ── 공개 API ──────────────────────────────

    def navigate_up(self) -> None:
        table = self._table
        if table.cursor_row > 0:
            table.move_cursor(row=table.cursor_row - 1)
            self.state.cursor_index = table.cursor_row

    def navigate_down(self) -> None:
        table = self._table
        if table.cursor_row < table.row_count - 1:
            table.move_cursor(row=table.cursor_row + 1)
            self.state.cursor_index = table.cursor_row

    def enter_selected(self) -> None:
        item = self.state.active_item
        if item and item.is_dir:
            self.state.enter_directory(item.path)
            self._refresh_table()

    def go_parent(self) -> None:
        parent = self.state.current_path.parent
        if parent != self.state.current_path:
            prev_name = self.state.current_path.name
            self.state.enter_directory(parent)
            self._refresh_table()
            for i, item in enumerate(self.state.items):
                if item.name == prev_name:
                    self._table.move_cursor(row=i)
                    self.state.cursor_index = i
                    break

    def toggle_hidden(self) -> None:
        self.state.show_hidden = not self.state.show_hidden
        self.state.refresh()
        self._refresh_table()

    def toggle_selection(self) -> None:
        item = self.state.active_item
        if item:
            self.state.toggle_selection(item)
            self._refresh_row(self.state.cursor_index)
            self.navigate_down()

    def select_all(self) -> None:
        if self.state.selected_paths:
            self.state.clear_selection()
        else:
            self.state.select_all()
        self._refresh_table()

    def cycle_sort(self, col_key: str) -> None:
        """컬럼 헤더 클릭 시 해당 컬럼으로 정렬 (FR-13).

        같은 컬럼 재클릭 시 역순 토글.
        """
        col_map = {COL_NAME: "name", COL_SIZE: "size", COL_DATE: "modified"}
        sort_key = col_map.get(col_key, "name")

        if self.state.sort_by == sort_key:
            self.state.sort_reverse = not self.state.sort_reverse
        else:
            self.state.sort_by = sort_key
            self.state.sort_reverse = False

        self.state.refresh()
        self._refresh_table()
        self._update_column_headers()

    def go_to(self, path_str: str) -> bool:
        path = Path(path_str).expanduser().resolve()
        if path.is_dir():
            self.state.enter_directory(path)
            self._refresh_table()
            return True
        return False

    def refresh_current(self) -> None:
        self.state.refresh()
        self._refresh_table()

    def get_selected_items(self) -> list[FileItem]:
        return self.state.get_selected_items()

    @property
    def current_path(self) -> Path:
        return self.state.current_path

    def status_text(self) -> str:
        sel_count = len(self.state.selected_paths)
        total = len([i for i in self.state.items if i.name != ".."])
        free, total_disk = self.state.disk_info()
        disk_str = f"여유: {format_size(free)} / {format_size(total_disk)}"
        sort_indicator = f"정렬: {_SORT_LABELS.get(self.state.sort_by, '이름')}"
        if sel_count:
            return f"{sel_count}개 선택 / 총 {total}개  |  {sort_indicator}  |  {disk_str}"
        return f"총 {total}개  |  {sort_indicator}  |  {disk_str}"

    def set_active(self, active: bool) -> None:
        """활성/비활성 패널 상태 설정 (CSS 클래스 + 경로 바 표시기)."""
        self._is_active = active
        if active:
            self.add_class("active-panel")
        else:
            self.remove_class("active-panel")
        self._update_path_bar()

    # ── 액션 ─────────────────────────────────

    def action_toggle_select(self) -> None:
        self.toggle_selection()

    # ── 이벤트 핸들러 ─────────────────────────

    def on_data_table_header_selected(self, event: DataTable.HeaderSelected) -> None:
        """컬럼 헤더 클릭 → 정렬 (FR-13)."""
        self.cycle_sort(str(event.column_key))

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        self.state.cursor_index = event.cursor_row
        self.post_message(FilePanelCursorMoved(self))

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Enter: 디렉토리 진입 또는 파일 미리보기 요청."""
        item = self.state.active_item
        if item is None:
            return
        if item.is_dir:
            self.enter_selected()
            self.post_message(FilePanelCursorMoved(self))
        else:
            self.post_message(FilePanelFileSelected(self, item))

    # ── 내부 헬퍼 ─────────────────────────────

    @property
    def _table(self) -> DataTable:
        return self.query_one(DataTable)

    @property
    def _path_label(self) -> Label:
        return self.query_one(".path-bar", Label)

    def _refresh_table(self) -> None:
        table = self._table
        table.clear()
        for item in self.state.items:
            name_cell, size_cell, date_cell = _item_markup(item)
            table.add_row(name_cell, size_cell, date_cell)

        idx = min(self.state.cursor_index, max(0, table.row_count - 1))
        if table.row_count > 0:
            table.move_cursor(row=idx)

        self._update_path_bar()
        self._update_column_headers()

    def _refresh_row(self, row_index: int) -> None:
        if row_index >= len(self.state.items):
            return
        item = self.state.items[row_index]
        name_cell, size_cell, date_cell = _item_markup(item)
        table = self._table
        table.update_cell_at((row_index, 0), name_cell)
        table.update_cell_at((row_index, 1), size_cell)
        table.update_cell_at((row_index, 2), date_cell)

    def _update_path_bar(self) -> None:
        """경로 바 레이블 업데이트 (활성 패널에 ▶ 표시기 포함)."""
        prefix = "[bold bright_blue]▶[/bold bright_blue] " if self._is_active else "  "
        safe_path = markup_escape(str(self.state.current_path))
        self._path_label.update(f"{prefix}{safe_path}")

    def _update_column_headers(self) -> None:
        """정렬 상태를 컬럼 헤더에 반영 (화살표 표시)."""
        col_map = {"name": COL_NAME, "size": COL_SIZE, "modified": COL_DATE}
        labels = {COL_NAME: "이름", COL_SIZE: "크기", COL_DATE: "날짜"}
        active_col = col_map.get(self.state.sort_by, COL_NAME)
        arrow = "↓" if self.state.sort_reverse else "↑"

        table = self._table
        for col_key, label in labels.items():
            indicator = f" {arrow}" if col_key == active_col else ""
            try:
                table.update_column(col_key, label=f"{label}{indicator}")
            except Exception:
                pass
