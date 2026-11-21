"""kafka/delivery-guarantee 의 outbox · inbox 흐름 그림. 시간 레인. 여백은 svgkit 규칙."""
from svgkit import V, Svg  # noqa: F401

LANE_H, LANE_GAP, TOP = 54, 10, 44
W = 150


def chip(s, x, y, w, label, fill="panel", stroke="line", tcolor="ink", h=30, size=11.5, weight=700, dash=None):
    s.rect(x, y, w, h, fill, stroke, 1.4, 7, dash)
    s.text(x + w / 2, y + h / 2 + size * 0.38, label, size, tcolor, weight, "middle")


def lanes(s, names, x1):
    ys = {}
    for i, n in enumerate(names):
        y = TOP + i * (LANE_H + LANE_GAP)
        s.rect(20, y, x1 - 20, LANE_H, "soft", "line", 1.1, 10)
        s.text(36, y + LANE_H / 2 + 4.5, n, 12.5, "sub", 700)
        ys[n] = y + (LANE_H - 30) / 2
    return ys, TOP + len(names) * (LANE_H + LANE_GAP) - LANE_GAP


def time_axis(s, x0, x1, y):
    s.arrow([(x0, y), (x1, y)], "sub", sw=1.4)
    s.text(x1, y + 20, "시간", 11.5, "sub", 600, "end")


# ------------------------------------------------------------- (1) outbox 흐름
def fig_outbox_flow():
    s = Svg(0, 0, "outbox 패턴의 흐름")
    names = ("앱", "DB: orders", "DB: outbox", "릴레이 (폴러 / CDC)", "Kafka 토픽")
    COLS = (330, 520, 710, 900)
    X1 = 1000
    ys, bottom = lanes(s, names, X1)
    app, orders, outbox, relay, topic = names

    def at(col, lane, label, fill="panel", stroke="line", tcolor="ink", dash=None, dx=0):
        chip(s, COLS[col] - W / 2 + dx, ys[lane], W, label, fill, stroke, tcolor, dash=dash)

    # 1 한 DB 트랜잭션
    at(0, app, "BEGIN … COMMIT", "accbg", "acc")
    at(0, orders, "주문 INSERT")
    at(0, outbox, "이벤트 INSERT (미발행)", "panel", "acc", "sub", "5 4")
    s.arrow([(COLS[0] - 30, ys[app] + 32), (COLS[0] - 30, ys[orders] - 2)], "acc", sw=1.4)
    s.arrow([(COLS[0] + 50, ys[app] + 32), (COLS[0] + 50, ys[outbox] - 2)], "acc", sw=1.4)
    # 2 미발행 행 읽기
    at(1, relay, "미발행 행 읽기")
    s.arrow([(COLS[0] + W / 2 + 2, ys[outbox] + 15), (COLS[1] - 20, ys[outbox] + 15),
             (COLS[1] - 20, ys[relay] - 2)], "sub", sw=1.4)
    # 3 send
    at(2, relay, "send() 키=주문 id", "accbg", "acc")
    at(2, topic, "OrderCreated", "okbg", "ok")
    s.arrow([(COLS[1] + W / 2 + 2, ys[relay] + 15), (COLS[2] - W / 2 - 4, ys[relay] + 15)], "sub", sw=1.4)
    s.arrow([(COLS[2], ys[relay] + 32), (COLS[2], ys[topic] - 2)], "acc", sw=1.4)
    # 4 published_at 기록
    at(3, outbox, "published_at 기록", "okbg", "ok")
    at(3, relay, "성공 응답 받음", "okbg", "ok")
    s.arrow([(COLS[2] + W / 2 + 2, ys[topic] + 15), (COLS[3], ys[topic] + 15), (COLS[3], ys[relay] + 34)],
            "ok", dash=True, sw=1.4)
    s.arrow([(COLS[3], ys[relay] - 2), (COLS[3], ys[outbox] + 34)], "ok", sw=1.4)
    for i, c in enumerate(COLS):
        s.badge(c, TOP - 18, str(i + 1), "ok" if i == 3 else "acc")
    time_axis(s, 240, X1 - 20, bottom + 16)
    return s.render()


# ------------------------------------------------------------- (2) inbox 흐름
def fig_inbox_flow():
    s = Svg(0, 0, "inbox 패턴의 흐름")
    names = ("Kafka 토픽", "컨슈머", "DB: inbox", "DB: settlement")
    COLS = (300, 470, 640, 810, 980)
    X1 = 1080
    ys, bottom = lanes(s, names, X1)
    topic, cons, inbox, sett = names

    def at(col, lane, label, fill="panel", stroke="line", tcolor="ink", dash=None, w=W):
        chip(s, COLS[col] - w / 2, ys[lane], w, label, fill, stroke, tcolor, dash=dash)

    # 1 poll
    at(0, topic, "이벤트 (event_id)")
    at(0, cons, "poll", "accbg", "acc")
    s.arrow([(COLS[0], ys[topic] + 32), (COLS[0], ys[cons] - 2)], "acc", sw=1.4)
    # 2 BEGIN + event_id INSERT
    at(1, cons, "BEGIN", "accbg", "acc")
    at(1, inbox, "event_id INSERT")
    s.arrow([(COLS[1], ys[cons] + 32), (COLS[1], ys[inbox] - 2)], "acc", sw=1.4)
    # 3 1건이면 반영 / 0건이면 건너뜀
    at(2, sett, "1건이면 정산 반영", "okbg", "ok")
    at(2, inbox, "0건 → 건너뜀", "panel", "warn", "warn", "5 4")
    s.arrow([(COLS[1] + 40, ys[inbox] + 32), (COLS[1] + 40, ys[sett] + 15), (COLS[2] - W / 2 - 4, ys[sett] + 15)],
            "ok", sw=1.4)
    s.arrow([(COLS[1] + W / 2 + 2, ys[inbox] + 15), (COLS[2] - W / 2 - 4, ys[inbox] + 15)], "warn", dash=True, sw=1.4)
    # 4 COMMIT
    at(3, cons, "COMMIT", "accbg", "acc")
    # 5 오프셋 커밋
    at(4, cons, "오프셋 커밋", "panel", "line", "sub")
    s.arrow([(COLS[4], ys[cons] - 2), (COLS[4], ys[topic] + 32)], "sub", dash=True, sw=1.4)
    for i, c in enumerate(COLS):
        s.badge(c, TOP - 18, str(i + 1), "ok" if i == 2 else "acc")
    time_axis(s, 220, X1 - 20, bottom + 16)
    return s.render()


FIGS = {"kafka-outbox-flow": fig_outbox_flow, "kafka-inbox-flow": fig_inbox_flow}
