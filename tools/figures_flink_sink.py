"""flink/sink-exactly-once 그림. 시간이 왼쪽 → 오른쪽으로 흐르는 레인 그림. 여백은 svgkit 규칙."""
from svgkit import V, Svg  # noqa: F401

LANE_H = 54
LANE_GAP = 10
TOP = 20


def chip(s, cx, y, w, label, fill="panel", stroke="line", tcolor="ink", dash=None, h=30, size=12.5, weight=700):
    s.rect(cx - w / 2, y, w, h, fill, stroke, 1.5, 7, dash)
    s.text(cx, y + h / 2 + size * 0.38, label, size, tcolor, weight, "middle")


def span(s, x0, x1, y, label, fill, stroke, tcolor="ink", dash="6 4", h=30):
    s.rect(x0, y, x1 - x0, h, fill, stroke, 1.5, 7, dash)
    s.text((x0 + x1) / 2, y + h / 2 + 4.8, label, 12.5, tcolor, 700, "middle")


def lanes(s, names, x1):
    """레인 배경과 이름. 반환: 이름 → 레인 안 칩을 놓을 y (위쪽)."""
    ys = {}
    for i, n in enumerate(names):
        y = TOP + i * (LANE_H + LANE_GAP)
        s.rect(20, y, x1 - 20, LANE_H, "soft", "line", 1.1, 10)
        s.text(36, y + LANE_H / 2 + 4.5, n, 12.5, "sub", 700)
        ys[n] = y + (LANE_H - 30) / 2
    bottom = TOP + len(names) * (LANE_H + LANE_GAP) - LANE_GAP
    return ys, bottom


def vline(s, x, y0, y1, color="sub"):
    s.add(f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1}" style="stroke:{V[color]}" stroke-width="1.4" '
          f'stroke-dasharray="4 4" opacity="0.8"/>')


def time_axis(s, x0, x1, y):
    s.arrow([(x0, y), (x1, y)], "sub", sw=1.4)
    s.text(x1, y + 20, "시간", 11.5, "sub", 600, "end")


def crash(s, x, y0, y1, cy):
    vline(s, x, y0, y1, "bad")
    s.add(f'<circle cx="{x}" cy="{cy}" r="13" style="fill:{V["bad"]}"/>')
    s.o.append(f'<text x="{x}" y="{cy + 5}" font-size="14" fill="#fff" font-weight="700" text-anchor="middle">✕</text>')


# ------------------------------------------------------------- 장면 그림 공통
# 한 줄 = 한 순간. 칸은 소스 토픽(읽은 위치 ▼) → Flink(위치 · 상태) → 싱크 토픽(쓴 결과).
ROW_H, ROW_GAP, HEAD = 72, 12, 30
SRC_X, FL_X, FL_W, SK_X, SK_W = 236, 520, 170, 742, 104


def board_head(s):
    s.text(SRC_X, HEAD, "소스 토픽 (▼ 읽은 위치)", 12.5, "sub", 700)
    s.text(FL_X, HEAD, "Flink", 12.5, "sub", 700)
    s.text(SK_X, HEAD, "싱크 토픽 (바깥에 쓴 결과)", 12.5, "sub", 700)


def row_y(i):
    return HEAD + 18 + i * (ROW_H + ROW_GAP)


def board_row(s, i, title, pos, flink, sink, color="acc", mark=None):
    """pos: 100 또는 150. flink: (위치 줄, 상태 줄, 색). sink: [(라벨, 모양)], 모양 = solid|new|pending|drop|dup."""
    y = row_y(i)
    s.rect(20, y, SK_X + 3 * (SK_W + 6) + 12 - 20, ROW_H, "soft", "line", 1.1, 10)
    s.badge(42, y + ROW_H / 2, str(i + 1), color)
    s.text(62, y + ROW_H / 2 + 4.5, title, 13, "ink", 700)
    # 소스 토픽
    cy = y + 22
    for k, t in enumerate(("1 ~ 100", "101 ~ 150", "151 ~ 200")):
        s.rect(SRC_X + k * 82, cy, 78, 30, "panel", "line", 1.2, 6)
        s.text(SRC_X + k * 82 + 39, cy + 19.5, t, 11.5, "ink", 600, "middle")
    px = SRC_X + (80 if pos == 100 else 162)
    pc = "warn" if mark == "rewind" else "acc"
    s.add(f'<path d="M{px - 7},{cy - 13} L{px + 7},{cy - 13} L{px},{cy - 3} z" style="fill:{V[pc]}"/>')
    s.arrow([(SRC_X + 244, y + ROW_H / 2), (FL_X - 6, y + ROW_H / 2)], "sub", sw=1.6)
    # Flink
    l1, l2, fc = flink
    s.rect(FL_X, y + 10, FL_W, ROW_H - 20, "panel" if fc == "line" else fc + "bg", fc, 1.5, 8)
    s.text(FL_X + FL_W / 2, y + 31, l1, 12.5, "ink", 700, "middle")
    s.text(FL_X + FL_W / 2, y + 50, l2, 12, "sub", 600, "middle")
    s.arrow([(FL_X + FL_W + 2, y + ROW_H / 2), (SK_X - 6, y + ROW_H / 2)], "sub", sw=1.6)
    # 싱크 토픽
    style = {"solid": ("panel", "line", "ink", None), "new": ("okbg", "ok", "ink", None),
             "pending": ("panel", "acc", "sub", "5 4"), "open": ("panel", "acc", "acc", "5 4"), "drop": ("panel", "bad", "sub", "5 4"),
             "dup": ("badbg", "bad", "bad", None)}
    for k, (t, kind) in enumerate(sink):
        f, st, tc, d = style[kind]
        x = SK_X + k * (SK_W + 6)
        s.rect(x, y + 21, SK_W, 30, f, st, 1.5, 6, d)
        s.text(x + SK_W / 2, y + 40.5, t, 11.5, tc, 700, "middle")
        if kind == "drop":
            s.add(f'<line x1="{x + 6}" y1="{y + 36}" x2="{x + SK_W - 6}" y2="{y + 36}" style="stroke:{V["bad"]}" stroke-width="2"/>')


def board_legend(s, n, kinds):
    y = row_y(n) + 8
    items = {"solid": ("panel", "line", None, "보임"), "new": ("okbg", "ok", None, "보임 (새로 생김)"),
             "pending": ("panel", "acc", "5 4", "커밋 전 · 안 보임"), "drop": ("panel", "bad", "5 4", "롤백 · 안 보임"),
             "dup": ("badbg", "bad", None, "중복으로 보임")}
    x = SRC_X
    for k in kinds:
        f, st, d, t = items[k]
        s.rect(x, y, 22, 14, f, st, 1.4, 3, d)
        s.text(x + 30, y + 12, t, 12, "sub", 600)
        x += 30 + len(t) * 11 + 28


# ------------------------------------------------------------- (1) 트랜잭션 없이 쓰면
def fig_no_txn():
    s = Svg(0, 0, "트랜잭션 없이 쓰면 생기는 중복")
    board_head(s)
    board_row(s, 0, "체크포인트 N", 100, ("위치 100", "합계 100 · 저장 ✓", "acc"), [("~ 100 결과", "solid")])
    board_row(s, 1, "101 ~ 150 처리", 150, ("위치 150", "합계 150", "line"),
              [("~ 100 결과", "solid"), ("101 ~ 150", "new")], "ok")
    board_row(s, 2, "장애 → N으로 복구", 100, ("위치 100", "합계 100 (되돌아감)", "warn"),
              [("~ 100 결과", "solid"), ("101 ~ 150", "solid")], "warn", "rewind")
    board_row(s, 3, "101 ~ 150 다시 처리", 150, ("위치 150", "합계 150", "line"),
              [("~ 100 결과", "solid"), ("101 ~ 150", "solid"), ("101 ~ 150", "dup")], "bad")
    board_legend(s, 4, ("solid", "new", "dup"))
    return s.render()


# ------------------------------------------------------------- (2) 2단계 커밋 · 정상
def fig_2pc():
    s = Svg(0, 0, "2단계 커밋 정상 흐름")
    board_head(s)
    board_row(s, 0, "체크포인트 N", 100, ("위치 100", "합계 100 · 저장 ✓", "acc"), [("~ 100 결과", "solid")])
    board_row(s, 1, "트랜잭션 T1 열기", 100, ("위치 100", "합계 100", "line"),
              [("~ 100 결과", "solid"), ("T1 (비어 있음)", "open")])
    board_row(s, 2, "T1에 씀", 150, ("위치 150", "합계 150", "line"),
              [("~ 100 결과", "solid"), ("T1: 101 ~ 150", "pending")])
    board_row(s, 3, "배리어 N+1 · 사전 커밋", 150, ("N+1 저장 ✓", "위치 150 · 합계 150 · T1", "acc"),
              [("~ 100 결과", "solid"), ("T1: 101 ~ 150", "pending"), ("T2 (비어 있음)", "open")])
    board_row(s, 4, "N+1 완료 → T1 커밋", 150, ("위치 150", "합계 150", "line"),
              [("~ 100 결과", "solid"), ("T1: 101 ~ 150", "new"), ("T2", "open")], "ok")
    board_legend(s, 5, ("solid", "pending", "new"))
    return s.render()


# ------------------------------------------------------------- (3) 2단계 커밋 · 커밋 전에 죽으면
def fig_2pc_fail():
    s = Svg(0, 0, "2단계 커밋 중 장애")
    board_head(s)
    board_row(s, 0, "체크포인트 N", 100, ("위치 100", "합계 100 · 저장 ✓", "acc"), [("~ 100 결과", "solid")])
    board_row(s, 1, "T1을 열고 쓰다가 장애", 150, ("위치 150", "합계 150", "line"),
              [("~ 100 결과", "solid"), ("T1: 101 ~ 150", "pending")], "bad")
    board_row(s, 2, "N으로 복구 · T1 롤백", 100, ("위치 100", "합계 100 (되돌아감)", "warn"),
              [("~ 100 결과", "solid"), ("T1: 101 ~ 150", "drop")], "warn", "rewind")
    board_row(s, 3, "T1' 열고 다시 씀", 150, ("위치 150", "합계 150", "line"),
              [("~ 100 결과", "solid"), ("T1: 101 ~ 150", "drop"), ("T1': 101 ~ 150", "pending")], "acc")
    board_row(s, 4, "N+1 완료 → T1' 커밋", 150, ("위치 150", "합계 150", "line"),
              [("~ 100 결과", "solid"), ("T1: 101 ~ 150", "drop"), ("T1': 101 ~ 150", "new")], "ok")
    board_legend(s, 5, ("solid", "pending", "drop", "new"))
    return s.render()


FIGS = {"sink-no-txn": fig_no_txn, "sink-2pc": fig_2pc, "sink-2pc-fail": fig_2pc_fail}
