"""상태바 및 함수키 바 위젯."""

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label


class StatusBar(Widget):
    """화면 하단 상태 표시줄."""

    DEFAULT_CSS = """
    StatusBar {
        height: 1;
        layout: horizontal;
        background: #0f3460;
        color: #ccccdd;
        padding: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("준비", id="status-left")
        yield Label("", id="status-right")

    def update(self, left: str = "", right: str = "") -> None:
        self.query_one("#status-left", Label).update(left)
        self.query_one("#status-right", Label).update(right)

    def set_error(self, message: str) -> None:
        self.query_one("#status-left", Label).update(
            f"[bold red]오류: {message}[/]"
        )
        self.query_one("#status-right", Label).update("")


# F키 힌트 정의
_FKEYS = [
    ("F2", "이름변경"),
    ("F3", "보기"),
    ("F5", "복사"),
    ("F6", "이동"),
    ("F7", "폴더"),
    ("F8", "삭제"),
    ("F10", "종료"),
]


class FunctionBar(Widget):
    """화면 최하단 함수키 힌트 바."""

    DEFAULT_CSS = """
    FunctionBar {
        height: 1;
        layout: horizontal;
        background: #111122;
        padding: 0;
    }
    .fkey-num {
        background: #888899;
        color: #000000;
        width: auto;
        padding: 0 0;
    }
    .fkey-label {
        background: #111122;
        color: #cccccc;
        width: auto;
        padding: 0 1 0 0;
    }
    """

    def compose(self) -> ComposeResult:
        for key, label in _FKEYS:
            yield Label(key, classes="fkey-num")
            yield Label(label, classes="fkey-label")
