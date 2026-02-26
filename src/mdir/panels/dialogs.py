"""모달 다이얼로그: 확인, 입력, 미리보기."""

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static


class ConfirmScreen(ModalScreen[bool]):
    """Yes/No 확인 다이얼로그."""

    BINDINGS = [
        Binding("enter", "confirm", show=False),
        Binding("escape", "cancel", show=False),
        Binding("y", "confirm", show=False),
        Binding("n", "cancel", show=False),
    ]

    def __init__(self, title: str, message: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._title = title
        self._message = message

    def compose(self) -> ComposeResult:
        with Static(classes="dialog-box"):
            yield Label(self._title, classes="dialog-title")
            yield Label(self._message, classes="dialog-message")
            with Static(classes="dialog-buttons"):
                yield Button("확인 (Y)", id="btn-ok", classes="btn-ok", variant="primary")
                yield Button("취소 (N)", id="btn-cancel", classes="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "btn-ok")

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)


class InputScreen(ModalScreen[str | None]):
    """텍스트 입력 다이얼로그 (이름 변경, 새 폴더, 경로 이동)."""

    BINDINGS = [
        Binding("escape", "cancel", show=False),
    ]

    def __init__(self, title: str, prompt: str, default: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self._title = title
        self._prompt = prompt
        self._default = default

    def compose(self) -> ComposeResult:
        with Static(classes="dialog-box"):
            yield Label(self._title, classes="dialog-title")
            yield Label(self._prompt, classes="dialog-message")
            yield Input(value=self._default, id="input-field", classes="dialog-input")
            with Static(classes="dialog-buttons"):
                yield Button("확인", id="btn-ok", classes="btn-ok", variant="primary")
                yield Button("취소", id="btn-cancel", classes="btn-cancel")

    def on_mount(self) -> None:
        input_widget = self.query_one("#input-field", Input)
        input_widget.focus()
        # 기존 값 전체 선택
        input_widget.cursor_position = len(self._default)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-ok":
            value = self.query_one("#input-field", Input).value.strip()
            self.dismiss(value or None)
        else:
            self.dismiss(None)

    def on_input_submitted(self, _event: Input.Submitted) -> None:
        value = self.query_one("#input-field", Input).value.strip()
        self.dismiss(value or None)

    def action_cancel(self) -> None:
        self.dismiss(None)


class PreviewScreen(ModalScreen):
    """텍스트 파일 미리보기 (읽기 전용)."""

    BINDINGS = [
        Binding("escape", "dismiss", "닫기"),
        Binding("q", "dismiss", "닫기"),
    ]

    MAX_SIZE = 512 * 1024  # 512KB 이상은 일부만 미리보기

    def __init__(self, path: Path, **kwargs) -> None:
        super().__init__(**kwargs)
        self._path = path

    def compose(self) -> ComposeResult:
        with Static(classes="preview-box"):
            yield Label(
                f" {self._path.name}  [dim](ESC: 닫기)[/]",
                classes="preview-title",
            )
            yield Static(self._load_content(), classes="preview-content", markup=False)

    def _load_content(self) -> str:
        try:
            size = self._path.stat().st_size
            with open(self._path, encoding="utf-8", errors="replace") as f:
                content = f.read(self.MAX_SIZE)
            if size > self.MAX_SIZE:
                content += f"\n\n... (이하 생략, 총 {size:,} bytes)"
            return content
        except PermissionError:
            return "[권한 없음: 파일을 읽을 수 없습니다]"
        except Exception as e:
            return f"[미리보기 오류: {e}]"

    def action_dismiss(self) -> None:
        self.dismiss()
