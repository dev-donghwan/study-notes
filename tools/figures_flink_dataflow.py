"""flink/dataflow-checkpoint 그림. 여백·크기는 svgkit 규칙을 따른다."""
from svgkit import V, Svg
import figures_flink_lifecycle as L


def box(s, x, y, w, h, title, sub=None, fill="panel", stroke="line", sw=1.4):
    s.rect(x, y, w, h, fill, stroke, sw, 8)
    if sub:
        s.text(x + w / 2, y + h / 2 - 4, title, 13, "ink", 700, "middle")
        s.text(x + w / 2, y + h / 2 + 15, sub, 11.5, "sub", 600, "middle")
    else:
        s.text(x + w / 2, y + h / 2 + 5, title, 13, "ink", 700, "middle")


def chips(s, items, x_right, y):
    """버퍼 속 레코드·배리어. 오른쪽(받는 쪽)이 맨 앞."""
    x = x_right - 8
    for it in items:
        if it == "|":
            x -= 10
            s.rect(x, y - 20, 8, 40, "warn", "warn", 1, 2)
            s.text(x + 4, y - 24, "N", 11, "warn", 700, "middle")
            x -= 6
            continue
        post = it.startswith("~")
        lab = it.lstrip("~")
        x -= 34
        s.rect(x, y - 11, 34, 22, "panel" if post else "accbg", "sub" if post else "acc", 1.2, 5,
               "3 2" if post else None)
        s.text(x + 17, y + 4, lab, 11, "ink", 600, "middle")
        x -= 5


# ------------------------------------------------------------------ 1 데이터가 흐르는 길
def fig_flow():
    s = Svg(0, 0, "데이터가 흐르는 길")
    H, Y = 76, 62                      # 상자 높이·위치 (가운데 = 100)
    box(s, 20, Y, 120, H, "소스", "예: Kafka", "soft")
    subs = [(170, 150, "소스 서브태스크", "r7", "읽는 중"),
            (420, 170, "연산자 서브태스크", "r4", "처리 중"),
            (690, 150, "싱크 서브태스크", "r2", "쓰는 중")]
    s.zone([(x, Y, w, H) for x, w, *_ in subs], "TaskManager (서브태스크들)", "accbg")
    for x, w, title, rec, verb in subs:
        s.rect(x, Y, w, H, "panel", "acc", 1.4, 8)
        s.text(x + w / 2, Y + 24, title, 13, "ink", 700, "middle")
        # 지금 손에 든 레코드: 버퍼 칩과 같은 모양, 색만 강조
        cx = x + w / 2 - 34
        s.rect(cx, Y + 38, 34, 22, "warnbg", "warn", 1.6, 5)
        s.text(cx + 17, Y + 53, rec, 11, "ink", 700, "middle")
        s.text(cx + 42, Y + 53, verb, 11.5, "warn", 700)
    box(s, 880, Y, 110, H, "싱크", "예: 테이블", "soft")
    s.arrow([(142, 100), (168, 100)])
    s.arrow([(842, 100), (878, 100)])
    s.add(f'<line x1="322" y1="100" x2="418" y2="100" style="stroke:{V["line"]}" stroke-width="10" stroke-linecap="round"/>')
    s.add(f'<line x1="592" y1="100" x2="688" y2="100" style="stroke:{V["line"]}" stroke-width="10" stroke-linecap="round"/>')
    chips(s, ["r5", "r6"], 418, 100)
    chips(s, ["r3"], 688, 100)
    s.text(370, 128, "버퍼", 12, "sub", 700, "middle")
    s.text(640, 128, "버퍼", 12, "sub", 700, "middle")
    # 범례
    y = s.next_y()
    s.rect(170, y - 9, 30, 18, "warnbg", "warn", 1.6, 4); s.text(208, y + 5, "지금 서브태스크가 다루는 레코드", 12, "sub", 600)
    s.rect(440, y - 9, 30, 18, "accbg", "acc", 1.2, 4); s.text(478, y + 5, "버퍼에서 기다리는 레코드", 12, "sub", 600)
    return s.render()


# ------------------------------------------------------------------ 2 워터마크
def fig_watermark():
    s = Svg(0, 0, "발생 시각과 도착 시각, 워터마크")
    X = lambda sec: 110 + (sec - 50) * 40          # 10:00:50 ~ 10:01:10
    AY, EY = 70, 300                                 # 도착 축, 발생 축
    lab = lambda sec: f"10:{'00' if sec < 60 else '01'}:{sec % 60:02d}"

    def axis(y, title, below):
        s.add(f'<line x1="{X(50)}" y1="{y}" x2="{X(70)}" y2="{y}" style="stroke:{V["sub"]}" stroke-width="1.6"/>')
        for sec in range(50, 71, 5):
            s.add(f'<line x1="{X(sec)}" y1="{y-4}" x2="{X(sec)}" y2="{y+4}" style="stroke:{V["sub"]}" stroke-width="1.6"/>')
            s.text(X(sec), y + (22 if below else -22), lab(sec), 11.5, "sub", 600, "middle")
        s.text(20, y + 4, title, 12.5, "ink", 700)

    # 발생 시각 축 위에 윈도우
    s.rect(X(50) - 10, EY - 62, X(60) - X(50) + 10, 58, "accbg", "acc", 1.2, 8)
    s.rect(X(60), EY - 62, X(70) - X(60) + 10, 58, "okbg", "ok", 1.2, 8)
    s.text(X(50), EY - 44, "윈도우 10:00", 12, "acc", 700)
    s.text(X(70), EY - 44, "윈도우 10:01", 12, "ok", 700, "end")
    axis(AY, "도착 시각", False)
    axis(EY, "발생 시각", True)
    # 레코드: (도착 순서, 발생, 도착, 늦음)
    recs = [(1, 52, 53, False), (2, 63, 64, False), (3, 59, 65, False), (4, 66, 67, False), (5, 57, 69, True)]
    for n, ev, arr, late in recs:
        c, f_ = ("bad", "badbg") if late else ("acc", "panel")
        s.add(f'<line x1="{X(arr)}" y1="{AY+12}" x2="{X(ev)}" y2="{EY-22}" style="stroke:{V[c]}" '
              f'stroke-width="1.8" opacity="0.8"/>')
        for y in (AY, EY - 22):
            s.add(f'<circle cx="{X(arr) if y == AY else X(ev)}" cy="{y}" r="11" style="fill:{V[f_]};stroke:{V[c]}" stroke-width="2"/>')
            s.text(X(arr) if y == AY else X(ev), y + 4.5, str(n), 12, "bad" if late else "ink", 700, "middle")
        if arr - ev > 1:
            s.text(X(arr), AY + 32, f"+{arr - ev}초", 11.5, c, 700, "middle")
    # 워터마크 (4번 도착 뒤)
    wx = X(61)
    s.add(f'<line x1="{wx}" y1="{EY-70}" x2="{wx}" y2="{EY+6}" style="stroke:{V["warn"]}" stroke-width="2.4" stroke-dasharray="6 4"/>')
    s.text(wx + 8, EY - 72, "워터마크 10:01:01 (4번 도착 뒤)", 12, "warn", 700)
    # 범례
    y = s.next_y()
    s.add(f'<circle cx="30" cy="{y}" r="8" style="fill:{V["panel"]};stroke:{V["acc"]}" stroke-width="2"/>')
    s.text(44, y + 4, "윈도우에 반영", 12, "sub", 600)
    s.add(f'<circle cx="150" cy="{y}" r="8" style="fill:{V["badbg"]};stroke:{V["bad"]}" stroke-width="2"/>')
    s.text(164, y + 4, "워터마크보다 늦음", 12, "sub", 600)
    s.text(320, y + 4, "숫자 = 도착 순서 · 선 = 같은 레코드의 발생 → 도착", 12, "sub", 600)
    return s.render()


# ------------------------------------------------------------------ 3 백프레셔
def fig_backpressure():
    s = Svg(0, 0, "백프레셔")
    box(s, 20, 70, 110, 60, "소스", "예: Kafka", "soft")
    xs = [(170, "소스 서브태스크", "acc"), (400, "연산자 A", "acc"), (630, "연산자 B", "bad"), (860, "싱크", "acc")]
    for x, t, c in xs:
        box(s, x, 70, 120, 60, t, "느림" if c == "bad" else None, "badbg" if c == "bad" else "panel", c,
            2.4 if c == "bad" else 1.4)
    # 버퍼 채움 정도
    for x, full in ((300, 1.0), (530, 1.0), (760, 0.15)):
        s.rect(x, 88, 90, 24, "panel", "bad" if full > 0.9 else "line", 1.4, 5)
        s.rect(x + 2, 90, 86 * full, 20, "badbg" if full > 0.9 else "soft", "bad" if full > 0.9 else "line", 0, 4)
        s.text(x + 45, 132, "가득 참" if full > 0.9 else "비어 있음", 11.5, "bad" if full > 0.9 else "sub", 700, "middle")
    s.arrow([(132, 100), (168, 100)])
    s.arrow([(690, 62), (690, 44), (230, 44), (230, 66)], "bad", dash=True)
    s.text(460, 36, "막힘이 앞쪽으로 번짐", 12, "bad", 700, "middle")
    s.text(75, 154, "lag 쌓임", 12, "bad", 700, "middle")
    return s.render()


# ------------------------------------------------------------------ 5 배리어로 찍는 과정
def fig_barrier():
    s = Svg(0, 0, "배리어로 찍는 과정")
    rows = [
        ("1", ("위치 5 저장", True), ["r5", "|", "~r6"], ("합계 4", False), [], ("쓰는 중", False), "소스: 위치 5"),
        ("2", ("위치 6", False), ["~r6"], ("합계 5 저장", True), ["|"], ("쓰는 중", False), "+ 연산자: 합계 5"),
        ("3", ("위치 6", False), [], ("합계 6", False), [], ("미커밋 목록 저장", True), "+ 싱크: 미커밋 f1, f2"),
        ("4", ("위치 6", False), [], ("합계 6", False), [], ("f1, f2 커밋", True), "+ _metadata → 완료"),
    ]
    for i, (n, src, b1, op, b2, snk, s3) in enumerate(rows):
        y = 20 + i * 96
        s.badge(30, y + 28, n)
        for x, w, title, (st, on) in ((60, 150, "소스", src), (330, 170, "연산자", op), (620, 160, "싱크", snk)):
            box(s, x, y, w, 56, title, st, "okbg" if on else "panel", "ok" if on else "line", 2 if on else 1.3)
        s.add(f'<line x1="212" y1="{y+28}" x2="328" y2="{y+28}" style="stroke:{V["line"]}" stroke-width="8" stroke-linecap="round"/>')
        s.add(f'<line x1="502" y1="{y+28}" x2="618" y2="{y+28}" style="stroke:{V["line"]}" stroke-width="8" stroke-linecap="round"/>')
        chips(s, b1, 328, y + 28)
        chips(s, b2, 618, y + 28)
        s.rect(820, y, 170, 56, "soft", "sub", 1.2, 8)
        s.text(834, y + 22, "S3 · 체크포인트 N", 11.5, "sub", 700)
        s.text(834, y + 42, s3, 12, "ok", 700)
    # 범례
    y = s.next_y()
    s.rect(60, y - 10, 8, 20, "warn", "warn", 1, 2); s.text(76, y + 5, "배리어 N", 12, "sub", 600)
    s.rect(170, y - 9, 30, 18, "accbg", "acc", 1.2, 4); s.text(208, y + 5, "배리어 앞 레코드", 12, "sub", 600)
    s.rect(340, y - 9, 30, 18, "panel", "sub", 1.2, 4, "3 2"); s.text(378, y + 5, "배리어 뒤 레코드", 12, "sub", 600)
    s.rect(510, y - 9, 30, 18, "okbg", "ok", 1.6, 4); s.text(548, y + 5, "이 단계에 저장", 12, "sub", 600)
    return s.render()


def fig_barrier_stream():
    """Flink 공식 문서의 배리어 그림 방식 + 연산자를 사이에 둔 한 순간."""
    s = Svg(0, 0, "배리어가 흘러가며 경계를 자른다")
    W, G, Y = 46, 6, 130

    def tape(x, seq):
        pos = {}
        for it in seq:
            if it.startswith("|"):
                s.rect(x, Y - 32, 9, 64, "warn", "warn", 1, 2)
                s.text(x + 4.5, Y + 48, "배리어 " + it[1:], 11.5, "warn", 700, "middle")
                x += 9 + G
                continue
            post = it.startswith("~")
            lab = it.lstrip("~")
            s.rect(x, Y - 17, W, 34, "panel" if post else "accbg", "sub" if post else "acc", 1.4, 6, "4 3" if post else None)
            s.text(x + W / 2, Y + 5, lab, 12.5, "ink", 700, "middle")
            pos[lab] = (x, x + W)
            x += W + G
        return x, pos

    def node(x, w, title, state, saved):
        s.rect(x, Y - 30, w, 60, "panel", "acc", 1.6, 8)
        s.text(x + w / 2, Y + 5, title, 13.5, "ink", 700, "middle")
        f_, c = ("okbg", "ok") if saved else ("soft", "line")
        s.rect(x + 6, Y + 40, w - 12, 30, f_, c, 1.6 if saved else 1.2, 15)
        s.text(x + w / 2, Y + 60, state, 12, "ok" if saved else "sub", 700, "middle")

    node(20, 120, "소스", "위치 5 저장 ✓", True)
    x, p1 = tape(166, ["~r9", "~r8", "~r7"])
    s.arrow([(142, Y), (164, Y)])
    s.arrow([(x - G + 2, Y), (x + 20, Y)])
    ox = x + 22
    node(ox, 140, "연산자", "합계 5 저장 ✓", True)
    x, p2 = tape(ox + 166, ["~r6", "|N", "r5", "r4"])
    s.arrow([(ox + 142, Y), (ox + 164, Y)])
    s.arrow([(x - G + 2, Y), (x + 20, Y)])
    node(x + 22, 140, "싱크", "배리어 N 기다리는 중", False)

    def bracket(x0, x1, label, color):
        yb = Y - 48
        s.add(f'<path d="M{x0},{yb+8} L{x0},{yb} L{x1},{yb} L{x1},{yb+8}" fill="none" style="stroke:{V[color]}" stroke-width="1.8"/>')
        s.text((x0 + x1) / 2, yb - 10, label, 12, color, 700, "middle")

    bracket(p1["r9"][0], p1["r7"][1], "다음 체크포인트 몫", "sub")
    bracket(p2["r6"][0], p2["r6"][1], "다음 몫", "sub")
    bracket(p2["r5"][0], p2["r4"][1], "체크포인트 N 몫", "acc")
    # 범례
    y = s.next_y()
    s.rect(20, y - 10, 9, 20, "warn", "warn", 1, 2); s.text(36, y + 4, "배리어 N", 12, "sub", 600)
    s.rect(120, y - 9, 30, 18, "accbg", "acc", 1.2, 4); s.text(158, y + 4, "배리어 앞 레코드 (N에 반영)", 12, "sub", 600)
    s.rect(340, y - 9, 30, 18, "panel", "sub", 1.2, 4, "4 3"); s.text(378, y + 4, "배리어 뒤 레코드", 12, "sub", 600)
    s.rect(510, y - 9, 30, 18, "okbg", "ok", 1.6, 9); s.text(548, y + 4, "체크포인트 N에 저장한 상태", 12, "sub", 600)
    return s.render()


# ------------------------------------------------------------------ 6 안에 든 것
def fig_contents():
    s = Svg(0, 0, "체크포인트 안에 든 것")
    box(s, 20, 30, 200, 60, "JobManager", "체크포인트 코디네이터", "warnbg", "warn")
    for i, t in enumerate(("소스 서브태스크", "연산자 서브태스크", "싱크 서브태스크")):
        box(s, 20, 130 + i * 76, 200, 56, t, None, "panel", "acc")
    s.rect(380, 20, 300, 290, "soft", "sub", 1.4, 12)
    s.text(398, 48, "S3 · chk-N/", 14, "ink", 700)
    files = [("_metadata  (목차)", "warn"), ("소스 상태 — 읽은 위치", "acc"),
             ("연산자 상태 — 키별 값 · 타이머", "acc"), ("싱크 상태 — 미커밋 결과", "acc")]
    for i, (t, c) in enumerate(files):
        y = 66 + i * 58
        s.rect(398, y, 264, 42, "panel", c, 1.4, 6)
        s.text(414, y + 26, t, 12.5, "ink", 600)
    s.arrow([(222, 60), (396, 87)], "warn")
    for i in range(3):
        s.arrow([(222, 158 + i * 76), (396, 145 + i * 58)], "ok")
    s.text(300, 52, "목차 쓰기", 11.5, "warn", 700, "middle")
    return s.render()


# ------------------------------------------------------------------ 7 배리어 정렬
def fig_alignment():
    s = Svg(0, 0, "배리어 정렬")
    box(s, 20, 30, 150, 56, "입력 A", None, "panel", "acc")
    box(s, 20, 190, 150, 56, "입력 B", None, "panel", "acc")
    box(s, 640, 100, 200, 80, "연산자", "B의 배리어 대기 중", "warnbg", "warn", 2)
    s.add(f'<line x1="172" y1="58" x2="636" y2="128" style="stroke:{V["line"]}" stroke-width="8" stroke-linecap="round"/>')
    s.add(f'<line x1="172" y1="218" x2="636" y2="152" style="stroke:{V["line"]}" stroke-width="8" stroke-linecap="round"/>')
    # A: 배리어는 이미 도착, 뒤 데이터는 대기
    s.rect(430, 30, 150, 50, "warnbg", "warn", 1.4, 8, "5 3")
    s.text(505, 22, "대기 (처리 안 함)", 11.5, "warn", 700, "middle")
    chips(s, ["~a7", "~a8"], 572, 55)
    # B: 배리어 앞 데이터가 아직 남음
    chips(s, ["b5", "b6", "|"], 470, 196)
    s.text(372, 240, "아직 처리 중", 11.5, "acc", 700, "middle")
    s.text(905, 145, "", 1)
    return s.render()


# ------------------------------------------------------------------ 8 장애와 복구
def fig_failure():
    s = Svg(0, 0, "장애와 복구")
    L.draw_map(s, hl=("jobmaster", "rm", "k8s", "s3", "kafka", "tm1"), tm="full", dead=("tm2",))
    s.arrow([(690, 236), (690, 180)], "bad", dash=True); s.badge(708, 216, "1", "bad")
    s.badge(720, 166, "2")
    s.arrow([(520, 62), (520, 52), (778, 52), (778, 268), (788, 268)], "warn"); s.badge(650, 52, "3")
    s.arrow([(788, 196), (440, 266)], "ok"); s.badge(600, 232, "4", "ok")
    s.badge(956, 70, "5", "acc")
    return s.render()



def fig_jm_failure():
    s = Svg(0, 0, "JobManager 장애와 복구")
    box(s, 20, 130, 170, 60, "쿠버네티스", "Deployment가 파드 재생성", "soft")
    s.rect(280, 20, 200, 60, "badbg", "bad", 2, 8)
    s.text(380, 56, "JobManager (죽음)", 13, "bad", 700, "middle")
    s.add(f'<path d="M300,28 L460,72 M460,28 L300,72" style="stroke:{V["bad"]}" stroke-width="2.4" opacity="0.6"/>')
    box(s, 280, 130, 200, 60, "새 JobManager", None, "warnbg", "warn", 1.8)
    box(s, 600, 60, 220, 56, "HA ConfigMap", "리더 · 최신 체크포인트 위치", "soft")
    box(s, 600, 160, 220, 56, "HA 저장소 (S3)", "잡 정보 · 체크포인트", "soft")
    box(s, 190, 270, 160, 50, "TaskManager 1", None, "panel", "acc")
    box(s, 410, 270, 160, 50, "TaskManager 2", None, "panel", "acc")
    s.arrow([(380, 82), (380, 126)], "bad", dash=True)
    s.arrow([(192, 160), (276, 160)], "warn"); s.badge(234, 140, "1")
    s.arrow([(482, 148), (596, 92)], "warn"); s.badge(540, 112, "2")
    s.arrow([(482, 172), (596, 188)], "warn")
    s.arrow([(340, 192), (290, 266)], "ok"); s.arrow([(420, 192), (480, 266)], "ok"); s.badge(380, 232, "3", "ok")
    return s.render()



def fig_snapshot_timing():
    s = Svg(0, 0, "상태 저장 타이밍")
    L1, L2 = 70, 150                     # 처리 줄, 업로드 줄
    s.text(20, L1 + 5, "처리", 13, "ink", 700)
    s.text(20, L2 + 5, "업로드", 13, "ink", 700)
    s.add(f'<line x1="110" y1="{L1}" x2="940" y2="{L1}" style="stroke:{V["line"]}" stroke-width="2"/>')
    s.add(f'<line x1="110" y1="{L2}" x2="940" y2="{L2}" style="stroke:{V["line"]}" stroke-width="2"/>')
    # 처리 줄: 처리 → 사본 확보(짧게 멈춤) → 처리 계속
    s.rect(110, L1 - 16, 210, 32, "accbg", "acc", 1.4, 6); s.text(215, L1 + 5, "레코드 처리", 12.5, "ink", 700, "middle")
    s.rect(328, L1 - 16, 70, 32, "warnbg", "warn", 1.8, 6); s.text(363, L1 + 5, "사본", 12.5, "warn", 700, "middle")
    s.rect(406, L1 - 16, 534, 32, "accbg", "acc", 1.4, 6); s.text(673, L1 + 5, "레코드 처리 계속", 12.5, "ink", 700, "middle")
    # 배리어 도착 표시
    s.rect(324, L1 - 40, 8, 80, "warn", "warn", 1, 2)
    s.text(328, L1 - 46, "배리어 N 도착", 12, "warn", 700, "middle")
    # 업로드 줄
    s.rect(398, L2 - 16, 380, 32, "okbg", "ok", 1.6, 6); s.text(588, L2 + 5, "사본을 S3에 업로드", 12.5, "ok", 700, "middle")
    s.arrow([(363, L1 + 18), (363, L2), (394, L2)], "ok")
    # 보고
    box(s, 800, L2 + 50, 140, 50, "JobManager", None, "warnbg", "warn")
    s.arrow([(778, L2 + 10), (840, L2 + 48)], "warn")
    s.text(800, L2 + 30, "완료 + 파일 위치", 12, "warn", 700, "end")
    s.badge(363, L1 + 34, "1"); s.badge(588, L2 + 30, "2", "ok"); s.badge(870, L2 + 108, "3")
    s.text(940, L1 - 26, "시간 →", 12, "sub", 600, "end")
    return s.render()


FIGS = {
    "flow": fig_flow, "watermark": fig_watermark, "backpressure": fig_backpressure,
    "barrier-stream": fig_barrier_stream, "snapshot-timing": fig_snapshot_timing, "barrier": fig_barrier, "contents": fig_contents, "alignment": fig_alignment, "failure": fig_failure, "jm-failure": fig_jm_failure,
}
