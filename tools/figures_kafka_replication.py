"""kafka/replication 그림. 오프셋은 0부터. 여백은 svgkit 규칙."""
from svgkit import V, Svg  # noqa: F401

CW, CG = 34, 4          # 로그 칸 폭 · 간격
KIND = {                # 칸 모양: (채움, 테두리, 글자색, 점선)
    "old": ("panel", "line", "ink", None),
    "acc": ("accbg", "acc", "ink", None),
    "ok": ("okbg", "ok", "ink", None),
    "out": ("panel", "line", "sub", "4 3"),
    "cut": ("panel", "bad", "bad", "4 3"),
}


def chip(s, x, y, w, label, fill="panel", stroke="line", tcolor="ink", h=30, size=12.5, weight=700, dash=None):
    s.rect(x, y, w, h, fill, stroke, 1.4, 7, dash)
    s.text(x + w / 2, y + h / 2 + size * 0.38, label, size, tcolor, weight, "middle")


def log(s, x, y, name, cells, note=None, note_color="sub"):
    """cells = [(라벨, 모양)]. 칸은 x 에서 시작, 이름은 왼쪽 70px 자리."""
    s.text(x - 70, y + 17, name, 12, "sub", 700)
    for i, (t, k) in enumerate(cells):
        f, st, tc, d = KIND[k]
        s.rect(x + i * (CW + CG), y, CW, 24, f, st, 1.3, 4, d)
        s.text(x + i * (CW + CG) + CW / 2, y + 16.5, t, 11.5, tc, 700, "middle")
    if note:
        s.text(x + len(cells) * (CW + CG) + 8, y + 17, note, 11.5, note_color, 700)


def hw_mark(s, x, idx, y0, y1):
    """idx 번째 칸 앞에 HW 선."""
    hx = x + idx * (CW + CG) - CG / 2
    s.add(f'<line x1="{hx}" y1="{y0}" x2="{hx}" y2="{y1}" style="stroke:{V["warn"]}" stroke-width="2" stroke-dasharray="5 4"/>')


def cells(n, new=None, kind="acc", base="old"):
    return [(str(i), kind if new is not None and i >= new else base) for i in range(n)]


# ------------------------------------------------------------- (1) fetch 와 HW 가 퍼지는 순서
ROW_H, ROW_GAP = 92, 10
LX = 330


def fig_fetch():
    s = Svg(0, 0, "팔로워 fetch와 HW 갱신 순서")
    rows = [
        ("리더에 4 씀", cells(5, 4), "LEO 5 · HW 4", cells(4), "LEO 4 · HW 4", 4, 4, None),
        ("팔로워 fetch (4부터)", cells(5), "LEO 5 · HW 4", cells(5, 4), "LEO 5 · HW 4", 4, 4, "응답에 리더 HW 4"),
        ("다음 fetch (5부터)", cells(5), "LEO 5 · HW 5", cells(5), "LEO 5 · HW 4", 5, 4, "acks=all 응답"),
        ("팔로워 HW 갱신", cells(5), "LEO 5 · HW 5", cells(5), "LEO 5 · HW 5", 5, 5, "응답에 리더 HW 5"),
    ]
    for i, (title, lc, ln, fc, fn, lhw, fhw, note) in enumerate(rows):
        y = 20 + i * (ROW_H + ROW_GAP)
        s.rect(20, y, 860, ROW_H, "soft", "line", 1.1, 10)
        s.badge(42, y + ROW_H / 2, str(i + 1), "ok" if i == 2 else "acc")
        s.text(62, y + ROW_H / 2 + 4.5, title, 13, "ink", 700)
        log(s, LX, y + 14, "리더", lc, ln, "warn" if i == 2 else "sub")
        log(s, LX, y + 54, "팔로워", fc, fn, "warn" if i == 3 else "sub")
        hw_mark(s, LX, lhw, y + 8, y + 42)
        hw_mark(s, LX, fhw, y + 48, y + 84)
        if note:
            chip(s, 700, y + 31, 160, note, "okbg" if i == 2 else "panel", "ok" if i == 2 else "line", size=11.5)
    y = 20 + len(rows) * (ROW_H + ROW_GAP) + 4
    s.add(f'<line x1="{LX}" y1="{y + 7}" x2="{LX + 22}" y2="{y + 7}" style="stroke:{V["warn"]}" stroke-width="2" stroke-dasharray="5 4"/>')
    s.text(LX + 30, y + 12, "HW (이 선 앞까지 컨슈머가 읽음)", 12, "sub", 600)
    return s.render()


# ------------------------------------------------------------- (2) ISR
def fig_isr():
    s = Svg(0, 0, "ISR과 HW")
    X = 150
    s.zone([(30, 60, 400, 24), (30, 94, 400, 24)], "ISR", "tm")
    log(s, X, 60, "리더", cells(6, 5), "LEO 6")
    log(s, X, 94, "팔로워 A", cells(5), "LEO 5")
    log(s, X, 160, "팔로워 B", [(str(i), "out") for i in range(2)], "LEO 2")
    hw_mark(s, X, 5, 52, 196)
    hx = X + 5 * (CW + CG) - CG / 2
    s.text(hx + 8, 212, "HW 5", 12, "warn", 700)
    s.badge(70, 40, "1", "acc")
    s.badge(hx, 40, "2", "warn")
    s.badge(20, 172, "3", "bad")
    return s.render()


# ------------------------------------------------------------- (3) leader epoch 로 맞추기
def fig_epoch():
    s = Svg(0, 0, "leader epoch로 로그를 맞추는 과정")
    rows = [
        ("A가 리더 (epoch 1)", [("A (리더)", [("0", "acc"), ("1", "acc"), ("2", "acc"), ("3", "acc")]),
                               ("B", [("0", "acc"), ("1", "acc"), ("2", "acc")])], None),
        ("A 장애 → B가 리더 (epoch 2)", [("A (죽음)", [("0", "out"), ("1", "out"), ("2", "out"), ("3", "out")]),
                                      ("B (리더)", [("0", "acc"), ("1", "acc"), ("2", "acc"), ("3", "ok")])], None),
        ("A 복귀 → 3 잘라냄", [("A", [("0", "acc"), ("1", "acc"), ("2", "acc"), ("3", "cut")]),
                               ("B (리더)", [("0", "acc"), ("1", "acc"), ("2", "acc"), ("3", "ok")])],
         "epoch 1은 3에서 끝"),
        ("B에서 3을 받아 옴", [("A", [("0", "acc"), ("1", "acc"), ("2", "acc"), ("3", "ok")]),
                             ("B (리더)", [("0", "acc"), ("1", "acc"), ("2", "acc"), ("3", "ok")])], None),
    ]
    for i, (title, logs, note) in enumerate(rows):
        y = 20 + i * (ROW_H + ROW_GAP)
        s.rect(20, y, 860, ROW_H, "soft", "line", 1.1, 10)
        s.badge(42, y + ROW_H / 2, str(i + 1), "bad" if i == 1 else "acc")
        s.text(62, y + ROW_H / 2 + 4.5, title, 13, "ink", 700)
        for k, (name, cs) in enumerate(logs):
            log(s, LX + 40, y + 14 + k * 40, name, cs)
        if note:
            chip(s, 700, y + 31, 160, note, "panel", "line", size=11.5)
    y = 20 + len(rows) * (ROW_H + ROW_GAP) + 4
    x = LX - 30
    for f, st, d, t in (("accbg", "acc", None, "epoch 1에 쓴 레코드"), ("okbg", "ok", None, "epoch 2에 쓴 레코드"),
                        ("panel", "bad", "4 3", "잘라냄")):
        s.rect(x, y, 22, 14, f, st, 1.4, 3, d)
        s.text(x + 30, y + 12, t, 12, "sub", 600)
        x += 30 + len(t) * 11 + 28
    return s.render()


FIGS = {"kafka-repl-fetch": fig_fetch, "kafka-isr": fig_isr, "kafka-epoch": fig_epoch}
