# mdir-tui Planning Document

> **Summary**: DOS 시대의 mdir 파일 매니저를 현대화한 Python 터미널 TUI 파일 매니저
>
> **Project**: bkit_mdirproject
> **Version**: 0.1.0
> **Author**: kim
> **Date**: 2026-02-25
> **Status**: Draft

---

## 1. Overview

### 1.1 Purpose

DOS 시대에 널리 사용된 `mdir`(및 Midnight Commander) 스타일의 두 패널 파일 매니저를 Python으로 현대화한다.
터미널에서 직관적이고 빠른 파일 탐색·관리 경험을 제공하며, Windows/Linux/Mac 크로스 플랫폼을 지원한다.

### 1.2 Background

- mdir/MC(Midnight Commander)는 두 패널 파일 브라우저로 키보드 중심의 빠른 파일 작업을 제공했음
- 현재 GUI 파일 탐색기 대비 터미널 환경에서의 빠른 파일 관리 도구 수요가 있음
- Python의 `Textual` 프레임워크가 현대적 TUI 앱 개발을 가능하게 함
- 개인 개발 도구로 시작하여 점진적으로 확장 가능한 구조 지향

### 1.3 Related Documents

- References: [Textual 공식 문서](https://textual.textualize.io/)
- References: [Midnight Commander](https://midnight-commander.org/)
- References: Python pathlib, send2trash, watchfiles

---

## 2. Scope

### 2.1 In Scope

- [x] 두 패널 파일 브라우저 (Left/Right Panel)
- [x] 키보드 기반 네비게이션 (화살표키, Tab, Enter)
- [x] 기본 파일 작업: 복사(F5), 이동(F6), 삭제(F8), 이름변경(F2)
- [x] 새 폴더 생성 (F7)
- [x] 파일 미리보기 (F3) - 텍스트 파일
- [x] 파일 정보 표시 (크기, 날짜, 권한)
- [x] 숨김 파일 토글 (Ctrl+H)
- [x] 경로 직접 입력 (Ctrl+G)
- [x] 홈 디렉토리 이동 (~)
- [x] 종료 (F10 / Q)
- [x] 상태바 (현재 경로, 선택 파일 수, 디스크 사용량)
- [x] 파일/폴더 정렬 (이름, 크기, 날짜)

### 2.2 Out of Scope

- FTP/SFTP 원격 파일 시스템 접근 (v2 고려)
- ZIP/TAR 압축/해제 인라인 처리 (v2 고려)
- 플러그인 시스템
- 북마크/즐겨찾기 관리 (v2 고려)
- 파일 검색 (Ctrl+F) (v2 고려)
- 파일 비교/동기화 (v2 고려)

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-01 | 두 패널 동시 표시, Tab으로 포커스 전환 | High | Pending |
| FR-02 | 화살표키로 파일 목록 네비게이션 | High | Pending |
| FR-03 | Enter로 폴더 진입, Backspace/.. 로 상위 폴더 | High | Pending |
| FR-04 | F5: 반대 패널로 파일/폴더 복사 (확인 다이얼로그) | High | Pending |
| FR-05 | F6: 반대 패널로 파일/폴더 이동 (확인 다이얼로그) | High | Pending |
| FR-06 | F8: 선택 파일 삭제 (휴지통, 확인 다이얼로그) | High | Pending |
| FR-07 | F2: 파일/폴더 이름 변경 (인라인 편집) | High | Pending |
| FR-08 | F7: 현재 패널에 새 폴더 생성 | High | Pending |
| FR-09 | F3: 텍스트 파일 미리보기 (오버레이 팝업) | Medium | Pending |
| FR-10 | Space: 단일 파일 선택/해제 (다중 선택) | Medium | Pending |
| FR-11 | Ctrl+A: 전체 선택 / 전체 해제 | Medium | Pending |
| FR-12 | Ctrl+H: 숨김 파일(도트 파일) 표시/숨김 토글 | Medium | Pending |
| FR-13 | 컬럼 헤더 클릭으로 정렬 (이름/크기/날짜) | Medium | Pending |
| FR-14 | 상태바: 현재 경로, 선택 항목 수, 총 디스크 사용량 | Medium | Pending |
| FR-15 | F10 / Q: 앱 종료 | High | Pending |

### 3.2 Non-Functional Requirements

| Category | Criteria | Measurement Method |
|----------|----------|-------------------|
| Performance | 1000개 파일 목록 렌더링 < 500ms | 수동 측정 |
| Startup | 앱 시작 시간 < 1초 | 수동 측정 |
| Compatibility | Windows 10+, macOS 12+, Ubuntu 20.04+ | 수동 테스트 |
| Memory | 일반 사용 시 < 100MB RAM | Task Manager |
| Usability | 기존 mdir/MC 사용자가 5분 내 기본 조작 습득 | 사용자 테스트 |

---

## 4. Success Criteria

### 4.1 Definition of Done

- [ ] FR-01 ~ FR-09 모든 기능 구현 완료
- [ ] FR-10 ~ FR-15 기능 구현 완료
- [ ] Windows 11에서 정상 동작 확인
- [ ] 키보드 기반 전체 워크플로우 동작 확인
- [ ] 파일 복사/이동/삭제 오류 없이 동작 확인

### 4.2 Quality Criteria

- [ ] ruff lint 에러 없음
- [ ] 주요 파일 작업에 예외 처리 구현
- [ ] 코드 모듈화 (panel, operations, styles 분리)

---

## 5. Risks and Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Windows 경로 구분자 문제 (\\ vs /) | High | High | pathlib.Path 일관 사용 |
| 대용량 디렉토리(10만+ 파일) 성능 저하 | Medium | Medium | 가상 스크롤 / 페이징 도입 |
| 파일 삭제 실수 (복구 불가) | High | Medium | send2trash 사용, 확인 다이얼로그 필수 |
| Textual 버전 호환성 이슈 | Low | Low | 버전 고정 (pyproject.toml) |
| 심볼릭 링크 처리 복잡성 | Low | Medium | 초기 버전에서 심링크 표시만, 추적 미지원 |

---

## 6. Architecture Considerations

### 6.1 Project Level Selection

| Level | 선택 | 이유 |
|-------|:----:|------|
| Starter | ☐ | 단순 스크립트 수준 이상의 복잡도 |
| **Dynamic** | ☑ | 기능별 모듈 분리, 적절한 규모 |
| Enterprise | ☐ | 오버엔지니어링 |

### 6.2 Key Architectural Decisions

| Decision | Options | Selected | Rationale |
|----------|---------|----------|-----------|
| TUI Framework | Textual / urwid / curses | **Textual** | 현대적 CSS 스타일링, 위젯 시스템, 활발한 유지보수 |
| 파일 시스템 | os / pathlib | **pathlib** | 모던 API, 크로스플랫폼 경로 처리 |
| 파일 삭제 | os.remove / send2trash | **send2trash** | 안전 삭제 (휴지통) |
| 파일 감시 | polling / watchfiles | **watchfiles** | 실시간 디렉토리 변경 감지, 비동기 지원 |
| 패키지 관리 | pip / uv / poetry | **uv** | 빠른 설치, 현대적 Python 패키징 |
| 코드 품질 | flake8 / ruff | **ruff** | 빠르고 통합된 린터+포매터 |
| 테스트 | unittest / pytest | **pytest** | 간결한 문법, 풍부한 플러그인 |

### 6.3 Project Structure

```
bkit_mdirproject/
├── docs/                          # PDCA 문서 (현재 위치)
│   ├── 01-plan/features/
│   ├── 02-design/features/
│   └── 03-analysis/
├── src/
│   └── mdir/
│       ├── __init__.py
│       ├── app.py                 # Textual App 진입점
│       ├── panels/
│       │   ├── __init__.py
│       │   ├── file_panel.py      # 파일 목록 패널 위젯
│       │   └── preview_panel.py   # 파일 미리보기 팝업
│       ├── operations/
│       │   ├── __init__.py
│       │   ├── copy.py            # 복사 작업
│       │   ├── move.py            # 이동 작업
│       │   └── delete.py          # 삭제 작업
│       ├── models/
│       │   ├── __init__.py
│       │   └── file_item.py       # 파일 항목 데이터 클래스
│       └── styles/
│           └── mdir.tcss          # Textual CSS 스타일
├── tests/
│   ├── test_operations.py
│   └── test_file_panel.py
├── pyproject.toml                 # 패키지 설정 + 의존성
└── README.md
```

---

## 7. Convention Prerequisites

### 7.1 Existing Project Conventions

- [ ] CLAUDE.md 코딩 컨벤션 섹션 없음 (새 프로젝트)
- [ ] docs/01-plan/conventions.md 없음 (생성 필요)
- [ ] CONVENTIONS.md 없음
- [ ] ruff 설정 (pyproject.toml에 포함 예정)

### 7.2 Conventions to Define

| Category | Current State | To Define | Priority |
|----------|---------------|-----------|:--------:|
| **Naming** | Missing | snake_case (모듈/변수), PascalCase (클래스) | High |
| **Folder structure** | Missing | src/mdir/ 레이아웃 | High |
| **Import order** | Missing | stdlib → third-party → local (ruff-isort) | Medium |
| **Error handling** | Missing | try/except 패턴, 사용자 메시지 표시 방식 | Medium |
| **Type hints** | Missing | 모든 public 함수에 타입 힌트 필수 | Medium |

### 7.3 Environment Variables Needed

| Variable | Purpose | Scope |
|----------|---------|-------|
| `MDIR_EDITOR` | 기본 텍스트 에디터 경로 | 사용자 환경 |
| `MDIR_THEME` | 컬러 테마 (default/dark/light) | 사용자 환경 |

### 7.4 Pipeline Integration

이 프로젝트는 bkit 9-phase Development Pipeline을 따르지 않고
PDCA 사이클로 직접 개발합니다 (Python TUI 특성).

---

## 8. Next Steps

1. [ ] `/pdca design mdir-tui` - 상세 설계 문서 작성
2. [ ] `pyproject.toml` 생성 및 의존성 정의
3. [ ] Textual 기반 기본 앱 뼈대 구현
4. [ ] 파일 패널 위젯 구현 (FR-01 ~ FR-03)
5. [ ] 파일 작업 구현 (FR-04 ~ FR-08)
6. [ ] 미리보기 기능 구현 (FR-09)
7. [ ] `/pdca analyze mdir-tui` - 갭 분석

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 0.1 | 2026-02-25 | Initial draft | kim |
