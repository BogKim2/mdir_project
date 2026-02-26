# mdir-tui Design Document

> **Summary**: Textual 프레임워크 기반 두 패널 TUI 파일 매니저 상세 설계
>
> **Project**: bkit_mdirproject
> **Version**: 0.1.0
> **Author**: kim
> **Date**: 2026-02-25
> **Status**: Draft
> **Planning Doc**: [mdir-tui.plan.md](../01-plan/features/mdir-tui.plan.md)

---

## 1. Overview

### 1.1 Design Goals

- Textual 위젯 시스템을 활용한 반응형 두 패널 TUI 레이아웃 구현
- `pathlib.Path` 기반의 크로스플랫폼 파일 시스템 추상화 레이어 설계
- 비동기(async) 파일 작업으로 UI 블로킹 없는 사용자 경험 제공
- 모듈별 단일 책임 원칙 적용으로 유지보수성 확보

### 1.2 Design Principles

- **Single Responsibility**: 각 위젯/모듈은 하나의 역할만 담당
- **Async First**: 파일 I/O 작업은 모두 `async/await` 처리
- **Fail Safe**: 파일 삭제는 반드시 `send2trash` 경유, 확인 다이얼로그 필수
- **Keyboard Driven**: 마우스 없이 키보드만으로 모든 작업 가능

---

## 2. Architecture

### 2.1 Widget Hierarchy

```
MdirApp (App)
├── PanelsContainer (Horizontal)
│   ├── FilePanel [id="left"] (Widget)
│   │   ├── PathBar (Label)          ← 현재 경로 표시
│   │   └── FileTable (DataTable)   ← 파일 목록
│   └── FilePanel [id="right"] (Widget)
│       ├── PathBar (Label)
│       └── FileTable (DataTable)
├── StatusBar (Widget)               ← 선택 정보, 디스크 사용량
└── FunctionBar (Widget)             ← F1~F10 키 힌트

# Screens (오버레이)
├── PreviewScreen (ModalScreen)      ← F3 파일 미리보기
├── ConfirmScreen (ModalScreen)      ← F5/F6/F8 확인 다이얼로그
└── InputScreen (ModalScreen)        ← F2/F7 텍스트 입력
```

### 2.2 Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  MdirApp                                                    │
│  ┌──────────────────┬──────────────────┐                   │
│  │  FilePanel(left) │  FilePanel(right)│                   │
│  │  ┌────────────┐  │  ┌────────────┐  │                   │
│  │  │  PathBar   │  │  │  PathBar   │  │                   │
│  │  ├────────────┤  │  ├────────────┤  │                   │
│  │  │            │  │  │            │  │                   │
│  │  │ FileTable  │  │  │ FileTable  │  │                   │
│  │  │ (focused)  │  │  │            │  │                   │
│  │  │            │  │  │            │  │                   │
│  │  └────────────┘  │  └────────────┘  │                   │
│  └──────────────────┴──────────────────┘                   │
│  ┌─────────────────────────────────────┐                   │
│  │  StatusBar                          │                   │
│  ├─────────────────────────────────────┤                   │
│  │  FunctionBar (F2~F10)               │                   │
│  └─────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Data Flow

```
키 입력 → MdirApp.on_key()
  → FilePanel.action_*()
    → FileOperation(copy/move/delete)
      → pathlib / shutil / send2trash
        → FilePanel.refresh_list()
          → FileTable 재렌더링
```

### 2.4 Module Dependencies

| Module | Depends On | Purpose |
|--------|-----------|---------|
| `app.py` | panels, styles | 앱 진입점, 키 바인딩 |
| `panels/file_panel.py` | models, operations | 파일 목록 표시 |
| `panels/preview_panel.py` | - | 텍스트 파일 미리보기 |
| `operations/copy.py` | models | 파일/폴더 복사 |
| `operations/move.py` | models | 파일/폴더 이동 |
| `operations/delete.py` | - | 파일/폴더 삭제 (send2trash) |
| `models/file_item.py` | - | 파일 항목 데이터 클래스 |

---

## 3. Data Model

### 3.1 FileItem (데이터 클래스)

```python
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime

@dataclass
class FileItem:
    path: Path                    # 절대 경로
    name: str                     # 파일명 (표시용)
    is_dir: bool                  # 디렉토리 여부
    is_hidden: bool               # 숨김 파일 여부 (도트 파일)
    size: int                     # 바이트 단위 크기 (디렉토리는 0)
    modified: datetime            # 최종 수정 시각
    is_symlink: bool = False      # 심볼릭 링크 여부
    is_selected: bool = False     # 다중 선택 상태

    @property
    def size_str(self) -> str:
        """사람이 읽기 좋은 파일 크기 문자열"""
        if self.is_dir:
            return "<DIR>"
        for unit in ("B", "K", "M", "G"):
            if self.size < 1024:
                return f"{self.size:>6.1f}{unit}"
            self.size /= 1024
        return f"{self.size:>6.1f}T"

    @property
    def modified_str(self) -> str:
        return self.modified.strftime("%Y-%m-%d %H:%M")

    @classmethod
    def from_path(cls, path: Path) -> "FileItem":
        stat = path.stat()
        return cls(
            path=path,
            name=path.name,
            is_dir=path.is_dir(),
            is_hidden=path.name.startswith("."),
            size=stat.st_size,
            modified=datetime.fromtimestamp(stat.st_mtime),
            is_symlink=path.is_symlink(),
        )
```

### 3.2 PanelState (패널 상태)

```python
@dataclass
class PanelState:
    current_path: Path            # 현재 디렉토리
    items: list[FileItem]         # 현재 목록 (정렬 후)
    cursor_index: int = 0         # 커서 위치
    selected_items: set[Path] = field(default_factory=set)  # 다중 선택
    sort_by: str = "name"         # "name" | "size" | "modified"
    sort_reverse: bool = False
    show_hidden: bool = False     # 숨김 파일 표시 여부

    @property
    def active_item(self) -> FileItem | None:
        if self.items and 0 <= self.cursor_index < len(self.items):
            return self.items[self.cursor_index]
        return None
```

### 3.3 Entity Relationships

```
PanelState
  └── items: list[FileItem]
        └── path: pathlib.Path   ← 실제 파일시스템 참조

MdirApp
  ├── left_state: PanelState
  └── right_state: PanelState
```

---

## 4. UI/UX Design

### 4.1 메인 화면 레이아웃

```
┌────────────────────────────┬────────────────────────────┐
│ /Users/kim/Documents       │ /Users/kim/Downloads       │
├──────┬──────────────┬──────┼──────┬──────────────┬──────┤
│ Name │     Size     │ Date │ Name │     Size     │ Date │
├──────┼──────────────┼──────┼──────┼──────────────┼──────┤
│ [..] │    <DIR>     │      │ [..] │    <DIR>     │      │
│ src  │    <DIR>     │02-25 │ imgs │    <DIR>     │02-20 │
│▶app.py│   3.2K      │02-25 │ a.zip│  128.5K      │02-18 │
│ conf │    1.1K      │02-24 │ b.pdf│   45.2K      │02-15 │
│      │              │      │      │              │      │
│      │              │      │      │              │      │
├──────┴──────────────┴──────┴──────┴──────────────┴──────┤
│ 4 files, 1 selected │ Free: 234.5G / 500G               │
├────────────────────────────────────────────────────────────┤
│ F2:Rename F3:View F5:Copy F6:Move F7:MkDir F8:Del F10:Quit│
└────────────────────────────────────────────────────────────┘
```

### 4.2 Textual CSS (mdir.tcss)

```css
/* 전체 레이아웃 */
Screen {
    layout: vertical;
    background: #1a1a2e;
}

#panels-container {
    layout: horizontal;
    height: 1fr;
}

/* 파일 패널 */
FilePanel {
    width: 1fr;
    border: solid #444455;
}

FilePanel:focus-within {
    border: solid #0099ff;
}

.path-bar {
    height: 1;
    background: #16213e;
    color: #aaaaff;
    padding: 0 1;
}

/* FileTable */
FileTable {
    height: 1fr;
    background: #1a1a2e;
}

FileTable > .datatable--header {
    background: #16213e;
    color: #888899;
    text-style: bold;
}

FileTable > .datatable--cursor {
    background: #0f3460;
    color: white;
}

.file-dir {
    color: #66aaff;
    text-style: bold;
}

.file-selected {
    color: #ffff00;
    text-style: bold;
}

.file-hidden {
    color: #666677;
}

.file-symlink {
    color: #ff88aa;
}

/* 상태바 */
StatusBar {
    height: 1;
    background: #0f3460;
    color: #ccccdd;
    padding: 0 1;
}

/* 함수키 바 */
FunctionBar {
    height: 1;
    background: #16213e;
    color: #aaaaaa;
}

.fkey-label {
    color: #000000;
    background: #aaaaaa;
}

/* 모달 */
ConfirmScreen, InputScreen, PreviewScreen {
    align: center middle;
}

.dialog-box {
    width: 60;
    height: auto;
    border: double #0099ff;
    background: #1a1a2e;
    padding: 1 2;
}

.preview-box {
    width: 80%;
    height: 80%;
    border: double #0099ff;
    background: #0d0d1a;
    padding: 1;
}
```

### 4.3 키 바인딩 명세

| Key | Action | 설명 |
|-----|--------|------|
| `↑` / `↓` | 커서 이동 | 파일 목록 탐색 |
| `Enter` | 폴더 진입 / 파일 실행 | 디렉토리면 진입, 파일이면 미리보기 |
| `Backspace` | 상위 폴더 이동 | `..` 이동 |
| `Tab` | 패널 전환 | Left ↔ Right 포커스 |
| `Space` | 선택 토글 | 단일 파일 선택/해제 |
| `Ctrl+A` | 전체 선택/해제 | 현재 패널 전체 |
| `Ctrl+H` | 숨김 파일 토글 | `.` 파일 표시/숨김 |
| `Ctrl+G` | 경로 직접 입력 | InputScreen 열기 |
| `F2` | 이름 변경 | InputScreen(rename) |
| `F3` | 미리보기 | PreviewScreen 열기 |
| `F5` | 복사 | 반대 패널로 복사, ConfirmScreen |
| `F6` | 이동 | 반대 패널로 이동, ConfirmScreen |
| `F7` | 새 폴더 생성 | InputScreen(mkdir) |
| `F8` | 삭제 | send2trash, ConfirmScreen |
| `F10` / `q` | 종료 | 앱 종료 |

### 4.4 ConfirmScreen 다이얼로그

```
┌─────────────────────────────────┐
│  복사 확인                       │
│  ─────────────────────────────  │
│  app.py (3.2K)                  │
│  → /Users/kim/Downloads/        │
│                                  │
│     [  확인  ]  [  취소  ]       │
└─────────────────────────────────┘
```

### 4.5 InputScreen 다이얼로그

```
┌─────────────────────────────────┐
│  이름 변경                       │
│  ─────────────────────────────  │
│  현재 이름: app.py               │
│  새 이름: [app_new.py          ] │
│                                  │
│     [  확인  ]  [  취소  ]       │
└─────────────────────────────────┘
```

### 4.6 PreviewScreen

```
┌─────────────────────────────────────────────────────────┐
│  app.py  (3.2K, 2026-02-25 08:00)          [ESC: 닫기] │
│  ─────────────────────────────────────────────────────  │
│  1  from textual.app import App, ComposeResult          │
│  2  from textual.widgets import Header, Footer          │
│  3                                                       │
│  4  class MdirApp(App):                                  │
│  5      ...                                              │
│                                                          │
│  ▼ (스크롤 가능)                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 5. Module Design

### 5.1 `app.py` - 메인 애플리케이션

```python
class MdirApp(App):
    """mdir-tui 메인 앱"""

    CSS_PATH = "styles/mdir.tcss"

    BINDINGS = [
        ("tab", "switch_panel", "패널 전환"),
        ("f2", "rename", "이름 변경"),
        ("f3", "preview", "미리보기"),
        ("f5", "copy", "복사"),
        ("f6", "move", "이동"),
        ("f7", "mkdir", "새 폴더"),
        ("f8", "delete", "삭제"),
        ("f10", "quit", "종료"),
        ("q", "quit", "종료"),
        ("ctrl+h", "toggle_hidden", "숨김 파일"),
        ("ctrl+g", "goto", "경로 이동"),
        ("ctrl+a", "select_all", "전체 선택"),
    ]

    def compose(self) -> ComposeResult:
        with Horizontal(id="panels-container"):
            yield FilePanel(id="left")
            yield FilePanel(id="right")
        yield StatusBar()
        yield FunctionBar()

    # 액션 메서드들...
    async def action_copy(self) -> None: ...
    async def action_move(self) -> None: ...
    async def action_delete(self) -> None: ...
    async def action_rename(self) -> None: ...
    async def action_mkdir(self) -> None: ...
    def action_preview(self) -> None: ...
    def action_switch_panel(self) -> None: ...
    def action_toggle_hidden(self) -> None: ...
    async def action_goto(self) -> None: ...
```

### 5.2 `panels/file_panel.py` - 파일 패널

```python
class FilePanel(Widget):
    """파일 목록 패널 (PathBar + FileTable)"""

    DEFAULT_CSS = ""
    state: reactive[PanelState]  # Textual reactive 상태

    def compose(self) -> ComposeResult:
        yield Label("", classes="path-bar", id="path-bar")
        yield FileTable()

    async def load_directory(self, path: Path) -> None:
        """디렉토리 로드 및 FileTable 갱신"""

    def get_active_item(self) -> FileItem | None:
        """현재 커서 위치 파일 항목 반환"""

    def get_selected_items(self) -> list[FileItem]:
        """다중 선택 항목 반환 (없으면 현재 커서 항목)"""

    def opposite_panel(self) -> "FilePanel":
        """반대 패널 참조 반환"""

    async def on_key(self, event: Key) -> None:
        """Enter, Backspace, Space 처리"""
```

### 5.3 `operations/copy.py` - 복사 작업

```python
async def copy_items(
    items: list[FileItem],
    dest_dir: Path,
    on_progress: Callable[[str], None] | None = None,
) -> list[Path]:
    """
    파일/폴더를 dest_dir로 복사.
    - 파일: shutil.copy2 (메타데이터 보존)
    - 폴더: shutil.copytree
    - 이름 충돌 시: dest_dir / "name_copy.ext" 자동 생성
    Returns: 복사된 경로 목록
    """

def resolve_conflict(dest: Path) -> Path:
    """이름 충돌 시 새 이름 생성: file.txt → file_copy.txt → file_copy2.txt"""
```

### 5.4 `operations/delete.py` - 삭제 작업

```python
from send2trash import send2trash

def delete_items(items: list[FileItem]) -> None:
    """
    파일/폴더를 시스템 휴지통으로 이동.
    - send2trash 사용 (복구 가능)
    - 실패 시 FileOperationError 발생
    """
    for item in items:
        try:
            send2trash(str(item.path))
        except Exception as e:
            raise FileOperationError(f"삭제 실패: {item.name}") from e
```

### 5.5 `operations/move.py` - 이동 작업

```python
import shutil

async def move_items(
    items: list[FileItem],
    dest_dir: Path,
) -> list[Path]:
    """
    파일/폴더를 dest_dir로 이동.
    - shutil.move 사용
    - 같은 파일시스템: rename (빠름)
    - 다른 파일시스템: copy + delete
    """
```

---

## 6. Error Handling

### 6.1 예외 클래스

```python
class MdirError(Exception):
    """mdir-tui 기본 예외"""

class FileOperationError(MdirError):
    """파일 작업 실패"""
    def __init__(self, message: str, path: Path | None = None):
        super().__init__(message)
        self.path = path

class PermissionError(MdirError):
    """권한 없음"""

class PathNotFoundError(MdirError):
    """경로 없음"""
```

### 6.2 에러 표시 방식

| 상황 | 처리 방법 |
|------|----------|
| 권한 없음 (삭제/복사) | StatusBar에 붉은 메시지 표시 |
| 경로 없음 (이동 후) | 상위 디렉토리로 자동 이동 |
| 디스크 풀 (복사) | ConfirmScreen으로 에러 표시 |
| 이름 충돌 (복사/이동) | 자동으로 `_copy` 접미사 추가 |
| 심볼릭 링크 접근 실패 | 해당 항목 회색으로 표시 |

---

## 7. Security Considerations

- [ ] 경로 traversal 방지: `Path.resolve()` 사용, 루트 경로 이탈 방지
- [ ] 파일 삭제: 항상 `send2trash` 경유, 직접 `os.remove` 사용 금지
- [ ] 심볼릭 링크: 링크 추적(follow) 비활성화 (기본 표시만)
- [ ] 권한 체크: 작업 전 `os.access()` 로 권한 사전 확인

---

## 8. Test Plan

### 8.1 Test Scope

| Type | Target | Tool |
|------|--------|------|
| Unit Test | FileItem, PanelState, operations/* | pytest |
| Integration Test | FilePanel 로드/네비게이션 | pytest + Textual pilot |
| Manual Test | 키 바인딩, 파일 작업 E2E | 수동 |

### 8.2 Key Test Cases

- [ ] `FileItem.from_path()` - 일반 파일, 디렉토리, 심링크 각각
- [ ] `FileItem.size_str` - B/K/M/G 단위 변환
- [ ] `copy_items()` - 파일, 폴더, 이름 충돌 케이스
- [ ] `move_items()` - 같은/다른 드라이브 간 이동
- [ ] `delete_items()` - 정상 삭제, 권한 없음 케이스
- [ ] `resolve_conflict()` - 중복 이름 자동 처리
- [ ] `FilePanel.load_directory()` - 빈 폴더, 숨김 파일 포함 폴더

---

## 9. Layer Assignment (Clean Architecture)

| Component | Layer | Location |
|-----------|-------|----------|
| `MdirApp` | Presentation | `src/mdir/app.py` |
| `FilePanel`, `FileTable` | Presentation | `src/mdir/panels/` |
| `PreviewScreen`, `ConfirmScreen`, `InputScreen` | Presentation | `src/mdir/panels/` |
| `StatusBar`, `FunctionBar` | Presentation | `src/mdir/panels/` |
| `copy_items`, `move_items`, `delete_items` | Application | `src/mdir/operations/` |
| `FileItem`, `PanelState` | Domain | `src/mdir/models/` |
| `pathlib.Path`, `shutil`, `send2trash` | Infrastructure | (외부 라이브러리) |

---

## 10. Coding Convention

### 10.1 Naming Conventions

| 대상 | 규칙 | 예시 |
|------|------|------|
| 클래스 | PascalCase | `FilePanel`, `MdirApp` |
| 함수/메서드 | snake_case | `load_directory()`, `get_active_item()` |
| 변수 | snake_case | `current_path`, `file_items` |
| 상수 | UPPER_SNAKE_CASE | `MAX_PREVIEW_SIZE`, `DEFAULT_SORT` |
| 파일명 | snake_case.py | `file_panel.py`, `copy.py` |
| 폴더명 | snake_case | `panels/`, `operations/`, `models/` |

### 10.2 Import Order (ruff-isort)

```python
# 1. stdlib
import os
from pathlib import Path
from dataclasses import dataclass

# 2. third-party
from textual.app import App
from textual.widgets import DataTable
from send2trash import send2trash

# 3. local
from mdir.models.file_item import FileItem
from mdir.operations.copy import copy_items
```

### 10.3 Type Hints

- 모든 public 함수/메서드에 타입 힌트 필수
- Python 3.10+ union 문법 사용: `str | None` (not `Optional[str]`)
- `list[FileItem]` (not `List[FileItem]`)

---

## 11. Implementation Order

1. [ ] `pyproject.toml` 생성 (의존성: textual, send2trash, watchfiles)
2. [ ] `models/file_item.py` - FileItem, PanelState 데이터 클래스
3. [ ] `styles/mdir.tcss` - 기본 레이아웃 CSS
4. [ ] `app.py` - MdirApp 뼈대 + 키 바인딩 선언
5. [ ] `panels/file_panel.py` - FilePanel + FileTable (FR-01~03)
6. [ ] `panels/file_panel.py` - Space/Ctrl+A 다중 선택 (FR-10~11)
7. [ ] `operations/copy.py` + `operations/move.py` (FR-04~05)
8. [ ] `operations/delete.py` (FR-06)
9. [ ] 이름 변경 / 새 폴더 (FR-07~08)
10. [ ] `panels/preview_panel.py` - 파일 미리보기 (FR-09)
11. [ ] 숨김 토글 / 정렬 / 상태바 (FR-12~14)
12. [ ] `tests/` 작성

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 0.1 | 2026-02-25 | Initial draft | kim |
