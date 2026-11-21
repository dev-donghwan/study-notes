# AGENTS.md — 공부 노트 사이트

LLM · 사람 모두 새 문서를 쓰기 전에 이 파일과 `STYLE.md`를 먼저 읽는다.

## 구조
| 경로 | 내용 |
|---|---|
| `src/site.json` | 홈 제목 · 소개 · 주제 순서 |
| `src/<주제>/series.json` | 주제 목록 + 문서 순서 (번호 · 이전/다음 링크가 여기서 나옴) |
| `src/<주제>/<문서>.html` | 문서 원본. 머리말 주석 + `<section class="chapter">` 들만 |
| `tools/figures_<주제>_<문서>.py` | 그림 모듈 (`FIGS = {"이름": 함수}`) |
| `tools/svgkit.py` | 그림 공통 도구 · 여백 상수 |
| `tools/build.py` | 빌드 + 규칙 검사 |
| `templates/partials/` | 공통 틀 (문서 · 주제 목록 · 홈). 모든 페이지 겉모양은 여기 하나에서 |
| `templates/page.html` | 복제용 문서 뼈대 (형식마다 언제 쓰는지 주석) |
| `templates/series.json` | 복제용 주제 설정 |
| `templates/figures_template.py` | 복제용 그림 모듈 |
| `src/sample/` + `tools/figures_sample.py` | 템플릿을 채운 예시 (홈에 안 나옴, `sample/sample.html`로 빌드) |
| `<주제>/*.html`, `index.html` | 빌드 결과. 직접 고치지 않는다 |

## 새 문서 쓰는 순서
1. 주제가 처음이면 `templates/series.json`을 `src/<주제>/series.json`으로 복사하고, `src/site.json`의 `topics`에 주제 폴더 이름을 넣는다.
2. `templates/page.html`을 `src/<주제>/<문서>.html`로 복사한다.
3. `series.json`의 `pages`에 `{"file", "title", "keywords"}`를 읽는 순서 자리에 넣는다.
4. 그림이 필요하면 `templates/figures_template.py`를 `tools/figures_<주제>_<문서>.py`로 복사한다. 그림 이름은 `<주제>-` 접두어.
5. 내용을 채운다. 형식은 `templates/page.html` 주석과 `src/sample/sample.html`을 따른다.
6. `python3 tools/build.py`를 돌린다. 규칙 위반이면 파일:줄이 나오니 고친다.
7. 브라우저(또는 headless Chrome 스크린샷)로 그림 겹침 · 여백을 확인한다.

## 지킬 것 (자세한 건 STYLE.md)
- 장 번호 · id · 목차 · 이전/다음 링크는 쓰지 않는다. 빌드가 만든다.
- 그림 안에는 이름 · 짧은 라벨 · 번호 배지 · 범례만. 설명은 본문.
- 두 문장 이상은 하위 불릿, 제목 없는 "문장 + 하위 불릿" 나열 금지.
- SQL · 코드는 코드 블록.
- 설정 키 · 기본값은 쓰는 버전의 소스 태그로 확인한다. 사내 정보(잡 이름 · 버킷 등)는 쓰지 않는다.
