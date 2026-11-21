"""flink/state-backend 그림. 여백·캔버스 크기는 svgkit 규칙을 따른다."""
from svgkit import V, Svg, esc  # noqa: F401


def chip(s, x, y, w, label, fill="panel", stroke="line", tcolor="ink", h=30, size=12, weight=600):
    s.rect(x, y, w, h, fill, stroke, 1.4, 7)
    s.text(x + w / 2, y + h / 2 + size * 0.38, label, size, tcolor, weight, "middle")


# ------------------------------------------------------------- (a) 현재 키로 읽고 쓰기
def fig_access():
    s = Svg(0, 0, "현재 키로 상태 읽고 쓰기")
    # 들어오는 레코드
    s.text(740, 22, "들어오는 레코드", 12.5, "sub", 700)
    chip(s, 740, 34, 76, "상품 A", "warnbg", "warn")
    chip(s, 826, 34, 76, "상품 B", "accbg", "acc")
    chip(s, 912, 34, 76, "상품 A", "accbg", "acc")
    # 연산자 코드
    s.rect(20, 118, 380, 150, "soft", "line", 1.4, 10)
    s.text(36, 144, "연산자 코드", 13.5, "ink", 700)
    s.rect(36, 160, 348, 34, "panel", "ok", 1.4, 6)
    s.text(50, 182, "c = count.value()", 13, "ink", 600)
    s.rect(36, 206, 348, 34, "panel", "warn", 1.4, 6)
    s.text(50, 228, "count.update(c + 1)", 13, "ink", 600)
    # 상태 백엔드
    s.rect(460, 100, 440, 260, "soft", "line", 1.4, 10)
    s.text(476, 126, "상태 백엔드 (이 서브태스크 것)", 13.5, "ink", 700)
    s.rect(476, 140, 408, 36, "warnbg", "warn", 1.6, 8)
    s.text(492, 164, "현재 키 = 상품 A", 13, "ink", 700)
    s.text(492, 204, "키", 12, "sub", 700)
    s.text(700, 204, "count", 12, "sub", 700)
    rows = [("상품 A", "2 → 3", True), ("상품 B", "5", False), ("상품 C", "1", False)]
    for i, (k, v, on) in enumerate(rows):
        y = 214 + i * 42
        s.rect(476, y, 408, 34, "okbg" if on else "panel", "ok" if on else "line", 1.6 if on else 1.2, 6)
        s.text(492, y + 22, k, 13, "ink", 600)
        s.text(700, y + 22, v, 13, "ok" if on else "ink", 700)
    # 화살표
    s.arrow([(778, 66), (778, 138)], "warn"); s.badge(800, 100, "1")
    s.arrow([(386, 177), (430, 177), (430, 224), (474, 224)], "ok"); s.badge(430, 200, "2", "ok")
    s.arrow([(386, 223), (414, 223), (414, 240), (474, 240)], "warn"); s.badge(440, 258, "3")
    return s.render()


# ------------------------------------------------------------- (b) 서브태스크마다 따로
def fig_per_subtask():
    s = Svg(0, 0, "서브태스크마다 따로인 상태 백엔드")
    s.rect(20, 20, 780, 300, "tm", "sub", 1.6, 14)
    s.text(38, 46, "TaskManager (파드 하나 · JVM 하나)", 14, "ink", 700)
    for i, x in enumerate((40, 420)):
        s.rect(x, 62, 360, 196, "panel", "sub", 1.2, 10, "6 4")
        s.text(x + 14, 84, f"슬롯 {i}", 12.5, "sub", 700)
        s.rect(x + 16, 98, 328, 46, "okbg", "ok", 1.6, 8)
        s.text(x + 180, 126, f"연산자 서브태스크 {i}", 13, "ink", 700, "middle")
        s.arrow([(x + 180, 146), (x + 180, 170)], "ok")
        s.rect(x + 16, 172, 328, 70, "accbg", "acc", 1.8, 8)
        s.text(x + 180, 200, f"상태 백엔드 #{i}", 13.5, "ink", 700, "middle")
        s.text(x + 180, 222, "키 그룹 0 ~ 63" if i == 0 else "키 그룹 64 ~ 127", 12, "acc", 700, "middle")
    s.add(f'<line x1="400" y1="200" x2="420" y2="200" style="stroke:{V["bad"]}" stroke-width="2.4"/>')
    s.text(410, 192, "✕", 13, "bad", 700, "middle")
    s.rect(40, 270, 740, 36, "warnbg", "warn", 1.2, 8)
    s.text(410, 293, "공유 자원: JVM 힙 · 관리 메모리 · 로컬 디스크", 12.5, "warn", 700, "middle")
    return s.render()


# ------------------------------------------------------------- (c) LSM 쓰기 경로
def fig_lsm_write():
    s = Svg(0, 0, "RocksDB 쓰기 경로")
    chip(s, 20, 120, 120, "update()", "panel", "warn", "ink", 44, 13.5, 700)
    mem = [(190, 98, 170, 88), (390, 98, 170, 88)]
    s.zone(mem, "메모리 (네이티브)", "accbg")
    s.rect(190, 98, 170, 88, "panel", "acc", 1.6, 8)
    s.text(275, 126, "memtable", 13.5, "ink", 700, "middle")
    s.text(275, 150, "B=6  A=5", 12, "sub", 600, "middle")
    s.text(275, 170, "(키 순 정렬)", 11, "sub", 400, "middle")
    s.rect(390, 98, 170, 88, "panel", "acc", 1.4, 8, "5 4")
    s.text(475, 126, "읽기 전용 memtable", 13, "ink", 700, "middle")
    s.text(475, 152, "가득 찬 것", 12, "sub", 600, "middle")
    # 디스크
    lv = {0: 280, 1: 352, 2: 424}
    disk = [(190, 280, 560, 44), (190, 352, 560, 44), (190, 424, 560, 44)]
    s.zone(disk, "TM 로컬 디스크", "okbg")
    for l, y in lv.items():
        chip(s, 190, y, 50, f"L{l}", "soft", "sub", "sub", 44, 13, 700)
    for i, rng in enumerate(("a ~ z", "c ~ x", "b ~ y")):
        chip(s, 252 + i * 112, 280, 100, f"SST · {rng}", "panel", "ok", "ink", 44, 12)
    for i, rng in enumerate(("a ~ h", "i ~ p", "q ~ z")):
        chip(s, 252 + i * 166, 352, 156, f"SST · {rng}", "panel", "ok", "ink", 44, 12)
    for i, rng in enumerate(("a ~ e", "f ~ k", "l ~ r", "s ~ z")):
        chip(s, 252 + i * 124, 424, 116, f"SST · {rng}", "panel", "ok", "ink", 44, 12)
    s.arrow([(142, 142), (188, 142)], "warn"); s.badge(165, 120, "1")
    s.arrow([(362, 142), (388, 142)], "acc"); s.badge(375, 120, "2", "acc")
    s.arrow([(475, 188), (475, 222), (414, 222), (414, 276)], "ok"); s.badge(444, 222, "3", "ok")
    s.arrow([(700, 326), (700, 350)], "sub"); s.badge(724, 338, "4", "sub")
    s.arrow([(700, 398), (700, 422)], "sub")
    return s.render()


# ------------------------------------------------------------- (d) 읽기 경로와 캐싱
def fig_read_path():
    s = Svg(0, 0, "RocksDB 읽기 경로")
    chip(s, 20, 20, 150, "value() · 키 A", "panel", "warn", "ink", 40, 13, 700)
    rows = [
        ("memtable", 80, [("없음", False)]),
        ("읽기 전용 memtable", 140, [("없음", False)]),
        ("L0 (전부, 최신부터)", 200, [("SST 3 · 없음", False), ("SST 2 · 없음", False), ("SST 1 · 없음", False)]),
        ("L1 (범위 맞는 1개)", 270, [("a ~ h", True), ("i ~ p", False), ("q ~ z", False)]),
        ("L2", 340, [("a ~ e", False), ("f ~ k", False), ("l ~ r", False), ("s ~ z", False)]),
    ]
    for name, y, files in rows:
        s.text(40, y + 26, name, 12.5, "ink", 700)
        w = 300 / len(files) - 8
        for i, (lab, on) in enumerate(files):
            x = 200 + i * (w + 8)
            fill, st = ("okbg", "ok") if on else ("panel", "line")
            if name.startswith("L2"):
                fill, st = "soft", "line"
            chip(s, x, y + 6, w, lab, fill, st, "ok" if on else ("sub" if name.startswith("L2") else "ink"), 32, 11.5)
    s.arrow([(95, 62), (95, 84)], "warn")
    for y in (118, 178, 248):
        s.arrow([(28, y), (28, y + 22)], "warn")
    s.add(f'<line x1="28" y1="84" x2="28" y2="300" style="stroke:{V["warn"]}" stroke-width="2"/>')
    s.badge(180, 96, "1"); s.badge(180, 222, "2"); s.badge(180, 292, "3")
    # SST 하나 안
    bx, by = 620, 120
    s.rect(bx, by, 360, 250, "soft", "line", 1.4, 12)
    s.text(bx + 16, by + 26, "SST 파일 하나 안", 13.5, "ink", 700)
    s.badge(bx + 340, by + 20, "4")
    chip(s, bx + 20, by + 44, 180, "블룸 필터", "panel", "acc", "ink", 40, 13, 700)
    chip(s, bx + 20, by + 114, 180, "인덱스 블록", "panel", "acc", "ink", 40, 13, 700)
    chip(s, bx + 20, by + 184, 180, "데이터 블록", "panel", "ok", "ink", 40, 13, 700)
    s.arrow([(bx + 110, by + 86), (bx + 110, by + 112)], "acc")
    s.arrow([(bx + 110, by + 156), (bx + 110, by + 182)], "acc")
    s.text(bx + 210, by + 70, "없음 → 건너뜀", 11.5, "sub", 600)
    chip(s, bx + 232, by + 184, 112, "블록 캐시", "warnbg", "warn", "ink", 40, 12.5, 700)
    s.arrow([(bx + 230, by + 204), (bx + 202, by + 204)], "warn", dash=True)
    s.add(f'<path d="M502,292 C560,292 570,260 {bx - 2},260" fill="none" style="stroke:{V["ok"]}" '
          f'stroke-width="1.6" stroke-dasharray="5 4"/>')
    return s.render()


# ------------------------------------------------------------- (e) 증분 체크포인트
def fig_incremental():
    """왼쪽부터 시간 순: ① 체크포인트 N → ② 컴팩션 → ③ 체크포인트 N+1, 아래 S3에서 ④ 정리."""
    s = Svg(0, 0, "증분 체크포인트")
    for n, x, title, files in ((1, 20, "체크포인트 N 시점 · 로컬 SST", [("1", 0), ("2", 0), ("3", 0)]),
                               (3, 520, "체크포인트 N+1 시점 · 로컬 SST", [("3", 0), ("4", 1), ("5", 1)])):
        s.rect(x, 20, 420, 110, "soft", "line", 1.4, 12)
        s.badge(x + 26, 41, str(n), "acc" if n == 1 else "ok")
        s.text(x + 44, 46, title, 13, "ink", 700)
        for j, (k, new) in enumerate(files):
            chip(s, x + 20 + j * 130, 64, 110, f"SST {k}", "okbg" if new else "panel", "ok" if new else "line",
                 "ok" if new else "ink", 44, 13, 700)
    s.badge(480, 41, "2", "sub")
    s.arrow([(446, 86), (514, 86)], "sub")
    # S3
    s.rect(20, 200, 920, 158, "soft", "line", 1.4, 12)
    s.text(36, 226, "S3 · 체크포인트 shared/", 13, "ink", 700)
    xs = {str(n): 60 + (n - 1) * 176 for n in range(1, 6)}
    for n, x in xs.items():
        gone = n in ("1", "2")
        chip(s, x, 244, 120, f"SST {n}", "panel", "line" if gone else "ok", "sub" if gone else "ink", 40, 13, 700)
    s.add(f'<path d="M60,298 L60,306 L532,306 L532,298" fill="none" style="stroke:{V["acc"]}" stroke-width="2"/>')
    s.text(296, 324, "체크포인트 N 이 참조", 12, "acc", 700, "middle")
    s.add(f'<path d="M412,312 L412,320 L884,320 L884,312" fill="none" style="stroke:{V["ok"]}" stroke-width="2"/>')
    s.text(648, 338, "체크포인트 N+1 이 참조", 12, "ok", 700, "middle")
    s.arrow([(230, 132), (230, 196)], "acc")
    s.arrow([(730, 132), (730, 196)], "ok")
    s.badge(36, 264, "4", "sub")
    return s.render()


def fig_backend_overview():
    """서브태스크 안을 위아래로: 사용자 코드 → 상태 백엔드(키별 칸) → 실제 저장 위치, 옆으로 S3."""
    s = Svg(0, 0, "상태 백엔드 큰 그림")

    def mono(x, y, txt):
        s.add(f'<text x="{x}" y="{y}" font-size="13" style="fill:{V["ink"]};font-family:ui-monospace,Menlo,monospace" '
              f'font-weight="600">{esc(txt)}</text>')

    # 들어오는 레코드
    s.text(20, 44, "들어오는 레코드", 12, "sub", 700)
    for i, (k, on) in enumerate((("상품 A", True), ("상품 B", False), ("상품 A", False))):
        s.rect(20, 58 + i * 40, 96, 30, "warnbg" if on else "accbg", "warn" if on else "acc", 1.6 if on else 1.2, 6)
        s.text(68, 78 + i * 40, k, 12.5, "ink", 700, "middle")
    s.arrow([(118, 73), (186, 88)], "warn")
    # 서브태스크
    s.rect(170, 20, 600, 330, "tm", "sub", 1.4, 14)
    s.text(186, 42, "서브태스크 (TaskManager 안)", 12.5, "sub", 700)
    # 사용자 코드
    s.rect(190, 56, 560, 76, "panel", "acc", 1.6, 10)
    s.text(206, 78, "연산자 · 사용자 코드", 13, "ink", 700)
    mono(206, 102, "c = count.value()")
    mono(206, 122, "count.update(c + 1)")
    # 상태 백엔드
    s.rect(190, 170, 560, 164, "warnbg", "warn", 1.8, 10)
    s.text(206, 194, "상태 백엔드", 13.5, "ink", 700)
    s.rect(330, 178, 170, 26, "panel", "warn", 1.4, 13)
    s.text(415, 196, "현재 키 = 상품 A", 12, "warn", 700, "middle")
    rows = (("상품 A", "2 → 3", True), ("상품 B", "5", False), ("상품 C", "1", False))
    for i, (k, v, on) in enumerate(rows):
        y = 216 + i * 34
        s.rect(206, y, 300, 28, "okbg" if on else "panel", "ok" if on else "line", 1.6 if on else 1.1, 6)
        s.text(220, y + 19, k, 12.5, "ink", 700)
        s.text(492, y + 19, v, 12.5, "ok" if on else "ink", 700, "end")
    # 실제 저장 위치
    s.text(640, 196, "실제로 두는 곳", 12, "sub", 700, "middle")
    s.rect(540, 208, 200, 40, "panel", "line", 1.3, 8); s.text(640, 233, "HashMap · JVM 힙", 12.5, "ink", 700, "middle")
    s.text(640, 268, "또는", 12, "sub", 600, "middle")
    s.rect(540, 280, 200, 40, "panel", "line", 1.3, 8); s.text(640, 305, "RocksDB · 로컬 디스크", 12.5, "ink", 700, "middle")
    s.add(f'<line x1="508" y1="264" x2="536" y2="264" style="stroke:{V["sub"]}" stroke-width="1.4" stroke-dasharray="4 3"/>')
    # 꺼내기 · 넣기
    s.arrow([(300, 134), (300, 214)], "warn"); s.badge(300, 156, "1")
    s.arrow([(440, 214), (440, 134)], "ok"); s.badge(440, 156, "2", "ok")
    # S3
    s.rect(830, 170, 140, 164, "soft", "sub", 1.4, 10)
    s.text(900, 244, "S3", 14, "ink", 700, "middle")
    s.text(900, 264, "체크포인트 저장소", 11.5, "sub", 600, "middle")
    s.text(900, 282, "(두 백엔드 공통)", 11.5, "sub", 600, "middle")
    s.arrow([(752, 210), (826, 210)], "ok"); s.badge(789, 194, "3", "ok")
    s.arrow([(826, 296), (752, 296)], "acc"); s.badge(789, 312, "4", "acc")
    return s.render()

FIGS = {
    "backend-overview": fig_backend_overview, "access": fig_access, "per-subtask": fig_per_subtask, "lsm-write": fig_lsm_write,
    "read-path": fig_read_path, "incremental": fig_incremental,
}
