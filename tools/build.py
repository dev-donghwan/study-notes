"""사이트 빌드: src/ 원본을 공통 틀(templates/partials/)로 감싸 HTML 을 만든다.

    python3 tools/build.py

구조
    src/site.json                홈 제목 · 소개 · 주제 순서
    src/<주제>/series.json       주제 목록 페이지 + 문서 순서 (이전/다음 링크도 여기서 나옴)
    src/<주제>/<문서>.html       문서 원본: 머리말 주석 + 장(section) 들만 쓴다
    tools/figures_*.py           그림 모듈. FIGS = {"이름": 함수} 를 모두 합쳐 한 이름 공간
    templates/partials/*.html    공통 틀 (문서 · 주제 목록 · 홈)

빌드가 해 주는 것
    - 원본의 <!--fig:이름--> 을 그림(인라인 SVG)으로 바꾼다
    - 장(<section class="chapter">)마다 id="cN" 과 번호를 붙이고, h2 로 목차를 만든다
      목차 문구를 짧게 하려면 <h2 data-toc="짧은 이름">긴 제목</h2>
    - series.json 순서로 이전/다음 링크, 주제 목록, 홈 목록을 만든다
    - 다 만든 뒤 STYLE.md 규칙 중 기계로 잡을 수 있는 것을 검사하고, 어기면 멈춘다

예전 형식(<!doctype 으로 시작하는 완성본 원본)은 그림만 끼워 그대로 내보낸다. 새 문서는 이 형식으로 쓰지 않는다.
"""
import html
import importlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
PARTIALS = ROOT / "templates" / "partials"
sys.path.insert(0, str(ROOT / "tools"))

# ---------------------------------------------------------------- 그림 모음
FIGS = {}
for path in sorted((ROOT / "tools").glob("figures_*.py")):
    mod = importlib.import_module(path.stem)
    for name, fn in mod.FIGS.items():
        if name in FIGS:
            raise SystemExit(f"그림 이름 중복: {name} ({path.name})")
        FIGS[name] = fn


def put_figs(text, where):
    def put(m):
        name = m.group(1)
        if name not in FIGS:
            raise SystemExit(f"{where}: 그림 '{name}' 없음")
        return '<div class="fig">' + FIGS[name]() + "</div>"
    return re.sub(r"<!--fig:([\w-]+)-->", put, text)


# ---------------------------------------------------------------- 공통 틀 채우기
def fill(name, **vals):
    out = (PARTIALS / name).read_text(encoding="utf-8")
    out = re.sub(r"<!--\n  공통 틀:.*?-->\n", "", out, count=1, flags=re.S)  # 틀 설명 주석은 결과에 안 남김
    for k, v in vals.items():
        out = out.replace("{{" + k + "}}", v)
    left = re.findall(r"\{\{\w+\}\}", out)
    if left:
        raise SystemExit(f"{name}: 채우지 않은 자리 {left}")
    return out


def read_meta(text, where):
    """원본 맨 위 <!-- key: value --> 머리말을 읽고, 나머지 본문을 돌려준다."""
    m = re.match(r"\s*<!--\n(.*?)\n-->\n", text, re.S)
    if not m:
        raise SystemExit(f"{where}: 머리말 주석(<!-- title: … -->)이 없음")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    for k in ("title", "description", "lead"):
        if not meta.get(k):
            raise SystemExit(f"{where}: 머리말에 {k} 가 없음")
    return meta, text[m.end():]


def number_chapters(body, where):
    """장마다 id · 번호를 붙이고 목차 <li> 를 만든다."""
    toc = []
    n = 0

    def sec(_):
        nonlocal n
        n += 1
        return f'<section class="chapter" id="c{n}">'
    body = re.sub(r'<section class="chapter">', sec, body)

    k = 0

    def h2(m):
        nonlocal k
        k += 1
        attrs, text = m.group(1), m.group(2)
        short = re.search(r'data-toc="([^"]+)"', attrs)
        toc.append(f'      <li><a href="#c{k}">{k}. {short.group(1) if short else text}</a></li>')
        return f'<h2><span class="no">{k}</span>{text}</h2>'
    body = re.sub(r"<h2([^>]*)>(.*?)</h2>", h2, body)
    if n != k:
        raise SystemExit(f"{where}: 장(section) {n}개와 제목(h2) {k}개가 맞지 않음")
    return body, "\n".join(toc)


def pager(pages, i, topic):
    """이전 / 다음. 처음과 끝은 주제 목록으로."""
    right_style = ' style="text-align:right"'

    def to_list(style):
        return f'      <a href="index.html"{style}><small>목록</small>{topic} 목록</a>'
    if i == 0:
        left = to_list("")
    else:
        p = pages[i - 1]
        left = f'      <a href="{p["file"]}"><small>← 이전</small>{p["title"]}</a>'
    if i == len(pages) - 1:
        right = to_list(right_style)
    else:
        p = pages[i + 1]
        right = f'      <a href="{p["file"]}"{right_style}><small>다음 →</small>{p["title"]}</a>'
    return left + "\n" + right


def write(rel, text):
    (ROOT / rel).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / rel).write_text(text, encoding="utf-8")
    print("built", rel)
    return ROOT / rel


# ---------------------------------------------------------------- 빌드
KW_BUDGET = 680   # 목록 행 오른쪽 칸 폭(px, 1200px 화면 기준). 칩이 한 줄에 들어가야 한다
KW_SPLIT = re.compile(r" · |&|/|,")


def chip_width(k):
    from svgkit import text_width
    return text_width(k, 12.5) + 18 + 6     # 글자 + 좌우 패딩 + 칩 간격


def check_keywords(where, kws):
    """칩 하나 = 개념 하나, 한 줄 폭 예산 안. 어기면 빌드 중단."""
    joined = [k for k in kws if KW_SPLIT.search(k)]
    if joined:
        raise SystemExit(f"{where}: 키워드 칩 하나에 개념 하나만 (' · ', '&', '/', ',' 로 묶지 않음): {joined}")
    w = sum(chip_width(k) for k in kws)
    if w > KW_BUDGET:
        raise SystemExit(f"{where}: 키워드 칩이 한 줄을 넘음 ({w:.0f}px > {KW_BUDGET}px). 줄이거나 짧게: {kws}")


def build_series(topic_dir, series, built):
    topic = topic_dir.name
    pages = series["pages"]
    rows = []
    for i, pg in enumerate(pages):
        check_keywords(f"{topic_dir.relative_to(ROOT)}/series.json · {pg['file']}", pg["keywords"])
        src = topic_dir / pg["file"]
        meta, body = read_meta(src.read_text(encoding="utf-8"), src.relative_to(ROOT))
        body, toc = number_chapters(put_figs(body, src), src.relative_to(ROOT))
        out = fill("layout.html", root="../", topic=series["title"], toc=toc, body=body.rstrip() + "\n",
                   pager=pager(pages, i, series["title"]), title=meta["title"], lead=meta["lead"],
                   description=html.escape(meta["description"], quote=True))
        built.append(write(f"{topic}/{pg['file']}", out))
        rows.append(f'    <a class="card" href="{pg["file"]}">\n      <span class="no">{i + 1}</span>\n'
                    f'      <h3>{pg["title"]}</h3>\n      <p class="kws">'
                    + "".join(f'<span class="kw">{k}</span>' for k in pg["keywords"]) + '</p>\n    </a>')
    built.append(write(f"{topic}/index.html", fill(
        "topic.html", root="../", topic=series["title"], intro=series["intro"],
        description=html.escape(series["description"], quote=True), rows="\n".join(rows))))
    return {topic_dir / p["file"] for p in pages}


HOME_KW = 9   # 홈 한 줄에 보여 줄 키워드 수. 넘치면 "…"


def home_keywords(series):
    """문서마다 앞 키워드를 번갈아 하나씩 모아(중복 제거) 주제 전체를 고루 보여 준다. 많으면 HOME_KW 개 + "…"."""
    lists = [pg["keywords"] for pg in series["pages"]]
    kws = []
    for i in range(max(map(len, lists), default=0)):
        for kl in lists:
            if i < len(kl) and kl[i] not in kws:
                kws.append(kl[i])
    shown, used = [], chip_width("…")
    for k in kws[:HOME_KW]:
        if used + chip_width(k) > KW_BUDGET:
            break
        shown.append(k)
        used += chip_width(k)
    chips = "".join(f'<span class="kw">{k}</span>' for k in shown)
    return chips + ('<span class="kw">…</span>' if len(kws) > len(shown) else "")


def build():
    site = json.loads((SRC / "site.json").read_text(encoding="utf-8"))
    built, home = [], []
    for topic_dir in sorted(p for p in SRC.iterdir() if p.is_dir()):
        seen = set()
        sj = topic_dir / "series.json"
        if sj.exists():
            series = json.loads(sj.read_text(encoding="utf-8"))
            seen = build_series(topic_dir, series, built)
            if not series.get("hidden"):
                home.append((topic_dir.name, series))
        # series.json 에 없는 원본은 예전 형식(완성본)만 허용
        for src in sorted(topic_dir.glob("*.html")):
            if src in seen:
                continue
            text = src.read_text(encoding="utf-8")
            if not text.lstrip().lower().startswith("<!doctype"):
                raise SystemExit(f"{src.relative_to(ROOT)}: series.json 의 pages 에 등록되지 않음")
            print(f"  (예전 형식, 목록 미등록) {src.relative_to(ROOT)}")
            built.append(write(f"{topic_dir.name}/{src.name}", put_figs(text, src)))

    order = {t: i for i, t in enumerate(site["topics"])}
    home.sort(key=lambda r: order.get(r[0], 999))
    rows = "\n".join(f'    <a class="card" href="{t}/index.html">\n      <h3>{s["title"]}</h3>\n'
                     f'      <p class="kws">{home_keywords(s)}</p>\n    </a>' for t, s in home)
    built.append(write("index.html", fill("home.html", title=site["title"], intro=site["intro"],
                                          description=html.escape(site["description"], quote=True), rows=rows)))
    lint(built)


# ---------------------------------------------------------------- 규칙 검사 (STYLE.md 의 [자동] 항목)
RULES = [
    (r"\d+\s*편", "목록에 'N편' 같은 번호를 달지 않는다"),
    (r"시리즈\s*·", "목록에 '시리즈 · N' 표시를 달지 않는다"),
    (r'class="tag"', "목록 행에 'N편' 같은 태그를 달지 않는다 (키워드는 series.json keywords)"),
    (r'class="cards [^"]+"', "목록은 기본 .cards 한 줄 행만 쓴다 (변형 클래스 금지)"),
    (r"\(\d+장", "'(N장)' 대신 장 이름 링크를 쓴다"),
    (r"대개", "'대개' 대신 '보통'"),
    (r"<h3>알아 둘", "소제목은 개념 이름으로 ('알아 둘 성질' 금지)"),
    (r"(?<![가-힣])창(을|이|에|의|은|과)", "'창' 대신 '윈도우'"),
    (r"<p><code>[^<]*(SELECT|JOIN|INSERT|CREATE|\(\)|;)", "SQL · 코드는 <pre class=\"code\"> 코드 블록으로"),
]


def lint(files):
    bad = []
    for f in files:
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if "<svg" in line:          # 그림 SVG 줄은 검사하지 않는다
                continue
            for pat, why in RULES:
                if re.search(pat, line):
                    bad.append(f"{f.relative_to(ROOT)}:{n}: {why}\n    {line.strip()[:120]}")
    if bad:
        raise SystemExit("규칙 위반 (STYLE.md):\n" + "\n".join(bad))


if __name__ == "__main__":
    build()
