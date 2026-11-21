"""kafka/delivery-guarantee 그림. 여백은 svgkit 규칙."""
from svgkit import V, Svg  # noqa: F401


def chip(s, x, y, w, label, fill="panel", stroke="line", tcolor="ink", h=30, size=12.5, weight=700, dash=None):
    s.rect(x, y, w, h, fill, stroke, 1.4, 7, dash)
    s.text(x + w / 2, y + h / 2 + size * 0.38, label, size, tcolor, weight, "middle")


def cross(s, x, cy):
    s.add(f'<circle cx="{x}" cy="{cy}" r="12" style="fill:{V["bad"]}"/>')
    s.o.append(f'<text x="{x}" y="{cy + 5}" font-size="13" fill="#fff" font-weight="700" text-anchor="middle">✕</text>')


def legend(s, x, y, items):
    """items = [(fill, stroke, dash, 라벨)]"""
    for f, st, d, t in items:
        s.rect(x, y, 22, 14, f, st, 1.4, 3, d)
        s.text(x + 30, y + 12, t, 12, "sub", 600)
        x += 30 + len(t) * 11 + 28


# ------------------------------------------------------------- (1) 유실 · 중복이 생기는 자리
def fig_map():
    s = Svg(0, 0, "Kafka 경로 위 유실과 중복 지점")
    prod = (20, 70, 130, 50)
    leader, f1, f2 = (240, 70, 120, 50), (380, 70, 110, 50), (510, 70, 110, 50)
    cons, ext = (710, 70, 130, 50), (910, 70, 130, 50)
    s.zone([prod], "프로듀서", "soft")
    s.zone([leader, f1, f2], "브로커", "tm")
    s.zone([cons, ext], "컨슈머", "soft")
    chip(s, *prod[:3], "앱 · send()", h=50, size=13)
    chip(s, *leader[:3], "리더", "accbg", "acc", h=50, size=13)
    chip(s, *f1[:3], "팔로워", h=50, size=13)
    chip(s, *f2[:3], "팔로워", h=50, size=13)
    chip(s, *cons[:3], "poll · 처리", h=50, size=13)
    chip(s, *ext[:3], "외부 저장", "okbg", "ok", h=50, size=13)
    s.arrow([(152, 95), (236, 95)], "acc")
    s.arrow([(362, 95), (376, 95)], "sub", sw=1.6)
    s.arrow([(492, 95), (506, 95)], "sub", sw=1.6)
    s.arrow([(636, 95), (706, 95)], "acc")
    s.arrow([(842, 95), (906, 95)], "acc")
    # 오프셋 커밋 (컨슈머 → 브로커)
    s.arrow([(775, 122), (775, 176), (435, 176), (435, 140)], "sub", dash=True, sw=1.6)
    s.text(605, 194, "오프셋 커밋", 12, "sub", 700, "middle")
    s.text(194, 86, "전송", 11.5, "sub", 600, "middle")
    s.text(671, 86, "poll", 11.5, "sub", 600, "middle")
    s.text(874, 86, "쓰기", 11.5, "sub", 600, "middle")
    # 번호 = 본문 장: 프로듀서 · 브로커 · 컨슈머
    s.badge(85, 22, "1", "acc")
    s.badge(430, 22, "2", "acc")
    s.badge(875, 22, "3", "acc")
    return s.render()


# ------------------------------------------------------------- (2) acks 와 복제
CW, CH, CG = 34, 24, 4


def log_row(s, x, y, name, n, new_from=None, color="ok", lost=False):
    s.text(x, y + 17, name, 12, "sub", 700)
    for i in range(n):
        cx = x + 84 + i * (CW + CG)
        hot = new_from is not None and i + 1 >= new_from
        if lost and hot:
            s.rect(cx, y, CW, CH, "panel", "bad", 1.3, 4, "4 3")
            s.text(cx + CW / 2, y + 16.5, str(i + 1), 11.5, "bad", 700, "middle")
        else:
            s.rect(cx, y, CW, CH, color + "bg" if hot else "panel", color if hot else "line", 1.3, 4)
            s.text(cx + CW / 2, y + 16.5, str(i + 1), 11.5, "ink", 700, "middle")


def acks_panel(s, x, title, follower_a, result_ok):
    y = 20
    s.rect(x, y, 470, 270, "soft", "line", 1.2, 12)
    s.text(x + 16, y + 26, title, 13, "ink", 700)
    log_row(s, x + 16, y + 48, "리더", 5, 4, "acc")
    log_row(s, x + 16, y + 80, "팔로워 A", follower_a, 4, "acc")
    log_row(s, x + 16, y + 112, "팔로워 B", 3)
    chip(s, x + 320, y + 46, 130, "프로듀서에 성공 응답", "okbg", "ok", h=28, size=11.5)
    s.badge(x + 320, y + 46, "1", "acc")
    # 장애
    s.add(f'<line x1="{x + 16}" y1="{y + 152}" x2="{x + 454}" y2="{y + 152}" style="stroke:{V["line"]}" stroke-width="1.2"/>')
    cross(s, x + 30, y + 178)
    s.text(x + 50, y + 183, "리더 장애 → 팔로워 A가 새 리더", 12.5, "ink", 700)
    s.badge(x + 320, y + 178, "2", "acc")
    if result_ok:
        log_row(s, x + 16, y + 206, "새 리더", 5, 4, "ok")
        s.text(x + 16, y + 254, "응답한 4, 5가 남음", 12, "ok", 700)
    else:
        log_row(s, x + 16, y + 206, "새 리더", 5, 4, "bad", lost=True)
        s.text(x + 16, y + 254, "응답한 4, 5가 사라짐", 12, "bad", 700)
    s.badge(x + 320, y + 218, "3", "bad" if not result_ok else "ok")


def fig_acks():
    s = Svg(0, 0, "acks 설정에 따른 리더 장애 결과")
    acks_panel(s, 20, "acks=1", 3, False)
    acks_panel(s, 510, "acks=all · min.insync.replicas=2", 5, True)
    legend(s, 36, 312, (("accbg", "acc", None, "새로 쓴 레코드"), ("panel", "bad", "4 3", "유실")))
    return s.render()


# ------------------------------------------------------------- (3) 멱등 프로듀서
ROW_H, ROW_GAP = 64, 10


def idem_row(s, i, title, color, send, logs, note=None):
    y = 20 + i * (ROW_H + ROW_GAP)
    s.rect(20, y, 900, ROW_H, "soft", "line", 1.1, 10)
    s.badge(42, y + ROW_H / 2, str(i + 1), color)
    s.text(62, y + ROW_H / 2 + 4.5, title, 13, "ink", 700)
    if send:
        lab, sc = send
        chip(s, 236, y + 17, 120, lab, "panel", sc)
        s.arrow([(358, y + 32), (420, y + 32)], sc, dash=(sc == "bad"), sw=1.6)
    for k, (t, kind) in enumerate(logs):
        f, st, tc = {"old": ("panel", "line", "ink"), "new": ("okbg", "ok", "ink"),
                     "dup": ("badbg", "bad", "bad")}[kind]
        chip(s, 426 + k * 86, y + 17, 80, t, f, st, tc, size=11.5)
    if note:
        t, c = note
        s.text(426 + len(logs) * 86 + 8, y + 37, t, 12, c, 700)


def fig_idempotent():
    s = Svg(0, 0, "멱등 프로듀서가 재전송을 거르는 과정")
    s.text(236, 14, "프로듀서 (PID 42)", 12, "sub", 700)
    s.text(426, 14, "파티션 로그", 12, "sub", 700)
    idem_row(s, 0, "seq 7 보냄", "acc", ("배치 seq 7", "acc"),
             [("seq 5", "old"), ("seq 6", "old"), ("seq 7", "new")])
    idem_row(s, 1, "응답 유실", "bad", ("응답 못 받음", "bad"),
             [("seq 5", "old"), ("seq 6", "old"), ("seq 7", "old")])
    idem_row(s, 2, "seq 7 재전송", "ok", ("배치 seq 7", "acc"),
             [("seq 5", "old"), ("seq 6", "old"), ("seq 7", "old")], ("이미 있음 → 성공만 응답", "ok"))
    idem_row(s, 3, "멱등 끄면", "warn", ("배치 (seq 없음)", "acc"),
             [("5", "old"), ("6", "old"), ("7", "old"), ("7 다시", "dup")], ("중복 저장", "bad"))
    return s.render()


# ------------------------------------------------------------- (4) 컨슈머 커밋 시점
def commit_row(s, y, title, steps, result):
    s.rect(20, y, 1000, 96, "soft", "line", 1.2, 12)
    s.text(36, y + 26, title, 13, "ink", 700)
    x = 36
    for i, (t, kind) in enumerate(steps):
        w = 132
        if kind == "crash":
            cross(s, x + 16, y + 63)
            s.text(x + 34, y + 68, t, 12, "bad", 700)
            w = 96
        else:
            f, st = {"step": ("panel", "line"), "commit": ("accbg", "acc")}[kind]
            chip(s, x, y + 48, w, t, f, st, size=12)
        nx = x + w + 30
        if i < len(steps) - 1:
            s.arrow([(x + w + 4, y + 63), (nx - 6, y + 63)], "sub", sw=1.4)
        x = nx
    t, c = result
    s.arrow([(x - 26, y + 63), (x + 4, y + 63)], c, sw=1.6)
    chip(s, x + 8, y + 48, 150, t, c + "bg", c, c, size=12)


def fig_commit():
    s = Svg(0, 0, "컨슈머 커밋 시점과 장애")
    commit_row(s, 20, "처리 전에 커밋",
               [("poll 101 ~ 150", "step"), ("커밋 150", "commit"), ("처리 중", "step"), ("장애", "crash"),
                ("150부터 다시 읽음", "step")], ("101 ~ 150 유실", "bad"))
    commit_row(s, 132, "처리 후에 커밋",
               [("poll 101 ~ 150", "step"), ("처리 완료", "step"), ("장애", "crash"), ("커밋 못 함", "step"),
                ("101부터 다시 읽음", "step")], ("101 ~ 150 두 번", "warn"))
    return s.render()


# ------------------------------------------------------------- (5) 트랜잭션: 읽고-처리하고-쓰기
LANE_H, LANE_GAP, TOP = 54, 10, 44
COLS = (300, 450, 600, 760, 920)


def fig_txn():
    s = Svg(0, 0, "트랜잭션으로 결과와 오프셋을 한 번에 커밋")
    names = ("앱 (트랜잭션 프로듀서)", "트랜잭션 코디네이터", "출력 토픽", "__consumer_offsets")
    ys = {}
    for i, n in enumerate(names):
        y = TOP + i * (LANE_H + LANE_GAP)
        s.rect(20, y, 1000, LANE_H, "soft", "line", 1.1, 10)
        s.text(36, y + LANE_H / 2 + 4.5, n, 12.5, "sub", 700)
        ys[n] = y + (LANE_H - 30) / 2
    W = 132

    def at(col, lane, label, fill="panel", stroke="line", tcolor="ink", dash=None):
        chip(s, COLS[col] - W / 2, ys[lane], W, label, fill, stroke, tcolor, size=11.5, dash=dash)

    app, co, out, off = names
    at(0, app, "begin", "accbg", "acc")
    at(1, app, "결과 send", "accbg", "acc")
    at(2, app, "오프셋 전달", "accbg", "acc")
    at(3, app, "commit", "accbg", "acc")
    chip(s, COLS[1] - 76, ys[co], 108, "파티션 등록", size=11.5)
    at(3, co, "커밋 준비 기록")
    at(4, co, "완료 기록", "okbg", "ok")
    at(1, out, "결과 (안 보임)", "panel", "acc", "sub", "5 4")
    at(4, out, "커밋 마커", "okbg", "ok")
    at(2, off, "오프셋 (안 보임)", "panel", "acc", "sub", "5 4")
    at(4, off, "커밋 마커", "okbg", "ok")
    # 화살표
    s.arrow([(COLS[1] - 22, ys[app] + 32), (COLS[1] - 22, ys[co] - 2)], "acc", sw=1.4)
    s.arrow([(COLS[1] + 50, ys[app] + 32), (COLS[1] + 50, ys[out] - 2)], "acc", sw=1.4)
    s.arrow([(COLS[2], ys[app] + 32), (COLS[2], ys[off] - 2)], "acc", sw=1.4)
    s.arrow([(COLS[3], ys[app] + 32), (COLS[3], ys[co] - 2)], "acc", sw=1.4)
    s.arrow([(COLS[3] + W / 2 + 2, ys[co] + 15), (COLS[4] - W / 2 - 4, ys[co] + 15)], "ok", sw=1.4)
    s.arrow([(COLS[4], ys[co] + 32), (COLS[4], ys[out] - 2)], "ok", sw=1.4)
    s.arrow([(COLS[4] + 40, ys[out] + 32), (COLS[4] + 40, ys[off] - 2)], "ok", sw=1.4)
    # 번호
    for i, c in enumerate(COLS):
        s.badge(c, TOP - 18, str(i + 1), "ok" if i == 4 else "acc")
    yb = TOP + 4 * (LANE_H + LANE_GAP) + 6
    s.arrow([(240, yb), (1000, yb)], "sub", sw=1.4)
    s.text(1000, yb + 20, "시간", 11.5, "sub", 600, "end")
    return s.render()


# ------------------------------------------------------------- (6) 전송에서 유실
def fig_send_callback():
    s = Svg(0, 0, "콜백 에러를 버리면 생기는 유실")
    commit_row(s, 20, "콜백 에러를 버림",
               [("send()", "step"), ("재시도 반복", "step"), ("120초 초과", "crash"), ("에러 로그만", "step")],
               ("레코드 유실", "bad"))
    commit_row(s, 132, "콜백에서 처리",
               [("send()", "step"), ("재시도 반복", "step"), ("120초 초과", "crash"), ("재처리 큐 · 앱 중단", "commit")],
               ("다시 보낼 수 있음", "ok"))
    return s.render()


# ------------------------------------------------------------- (7) unclean 선출
CELL = {"old": ("panel", "line", "ink", None), "acc": ("accbg", "acc", "ink", None),
        "out": ("panel", "line", "sub", "4 3"), "cut": ("panel", "bad", "bad", "4 3")}


def cellrow(s, x, y, name, cells, note=None, note_color="sub"):
    s.text(x - 90, y + 17, name, 12, "sub", 700)
    for i, (t, k) in enumerate(cells):
        f, st, tc, d = CELL[k]
        s.rect(x + i * 38, y, 34, 24, f, st, 1.3, 4, d)
        s.text(x + i * 38 + 17, y + 16.5, t, 11.5, tc, 700, "middle")
    if note:
        s.text(x + len(cells) * 38 + 8, y + 17, note, 11.5, note_color, 700)


def fig_unclean():
    s = Svg(0, 0, "ISR이 모두 죽었을 때 unclean 선출")
    UR_H, UR_GAP, LX = 92, 10, 400
    a_all = [(str(i), "acc") for i in range(1, 7)]
    a_dead = [(str(i), "out") for i in range(1, 7)]
    b3 = [(str(i), "old") for i in range(1, 4)]
    rows = [
        ("ISR이 리더 하나로 줄어듦", "acc", [("A (리더 · ISR)", a_all, None), ("B (ISR 밖)", b3, None)], None),
        ("A 장애", "bad", [("A (죽음)", a_dead, None), ("B (ISR 밖)", b3, None)], None),
        ("unclean 끔", "warn", [("A (죽음)", a_dead, None), ("B", b3, None)], ("리더 없음 · 파티션 멈춤", "warnbg", "warn")),
        ("unclean 켬", "bad", [("A (죽음)", a_dead, None),
                              ("B (리더)", b3 + [(str(i), "cut") for i in range(4, 7)], ("4 ~ 6 유실", "bad"))], None),
    ]
    for i, (title, color, logs, chipd) in enumerate(rows):
        y = 20 + i * (UR_H + UR_GAP)
        s.rect(20, y, 920, UR_H, "soft", "line", 1.1, 10)
        s.badge(42, y + UR_H / 2, str(i + 1), color)
        s.text(62, y + UR_H / 2 + 4.5, title, 13, "ink", 700)
        for k, (name, cs, note) in enumerate(logs):
            cellrow(s, LX, y + 14 + k * 40, name, cs, *(note or ()))
        if chipd:
            t, f, st = chipd
            chip(s, 740, y + 31, 180, t, f, st, st, size=12)
    return s.render()


# ------------------------------------------------------------- (8) 보존 · 오프셋 만료
def fig_retention():
    s = Svg(0, 0, "보존 기간을 넘긴 lag")
    s.rect(20, 20, 1000, 112, "soft", "line", 1.2, 12)
    s.text(36, 46, "파티션 로그", 13, "ink", 700)
    segs = (("0 ~ 99", True), ("100 ~ 199", True), ("200 ~ 299", False), ("300 ~ 399", False))
    for i, (t, gone) in enumerate(segs):
        x = 200 + i * 160
        if gone:
            chip(s, x, 76, 150, t + " (삭제)", "panel", "bad", "bad", h=34, size=12, dash="5 4")
        else:
            chip(s, x, 76, 150, t, "panel", "line", h=34, size=12)
    cx = 200 + 160 + 75
    s.add(f'<path d="M{cx - 7},{56} L{cx + 7},{56} L{cx},{68} z" style="fill:{V["warn"]}"/>')
    s.text(cx - 12, 64, "그룹 커밋 150", 12, "warn", 700, "end")
    bx = 200 + 2 * 160 - 5
    s.add(f'<line x1="{bx}" y1="50" x2="{bx}" y2="120" style="stroke:{V["sub"]}" stroke-width="1.6" stroke-dasharray="5 4"/>')
    s.text(bx + 8, 62, "보존 기간 경계", 11.5, "sub", 700)
    commit_row(s, 150, "다시 시작하면",
               [("150은 범위 밖", "step"), ("reset=latest", "step"), ("400부터 읽음", "step")],
               ("150 ~ 399 건너뜀", "bad"))
    return s.render()


# ------------------------------------------------------------- (9) 외부 쓰기 중복
def fig_external():
    s = Svg(0, 0, "외부 쓰기 중복과 inbox")
    commit_row(s, 20, "그냥 쓰면",
               [("poll 101 ~ 150", "step"), ("DB에 씀", "step"), ("장애", "crash"), ("커밋 못 함", "step"),
                ("101부터 다시", "step")], ("DB에 두 번", "warn"))
    commit_row(s, 132, "inbox",
               [("poll 101 ~ 150", "step"), ("DB + id 기록", "commit"), ("장애", "crash"), ("101부터 다시", "step"),
                ("id 있음 → 건너뜀", "step")], ("DB에 한 번", "ok"))
    return s.render()


FIGS = {
    "kafka-map": fig_map,
    "kafka-acks": fig_acks,
    "kafka-idempotent": fig_idempotent,
    "kafka-commit": fig_commit,
    "kafka-txn": fig_txn,
    "kafka-send-callback": fig_send_callback,
    "kafka-unclean": fig_unclean,
    "kafka-retention": fig_retention,
    "kafka-external": fig_external,
}
