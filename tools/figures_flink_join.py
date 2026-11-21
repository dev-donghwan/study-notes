"""flink/join 그림. 여백은 svgkit 규칙."""
from svgkit import V, Svg  # noqa: F401


def chip(s, x, y, w, label, fill="panel", stroke="line", tcolor="ink", h=30, size=12.5, weight=700, dash=None):
    s.rect(x, y, w, h, fill, stroke, 1.4, 7, dash)
    s.text(x + w / 2, y + h / 2 + size * 0.38, label, size, tcolor, weight, "middle")


# ------------------------------------------------------------- (1) 조인이 상태를 쌓는 이유
def fig_join_state():
    s = Svg(0, 0, "조인 서브태스크의 상태")
    # 입력
    s.text(20, 44, "클릭 스트림", 12.5, "sub", 700)
    for i, k in enumerate(("k1", "k2", "k1")):
        chip(s, 20 + i * 62, 56, 54, k, "accbg", "acc")
    s.text(20, 174, "주문 스트림", 12.5, "sub", 700)
    for i, k in enumerate(("k3", "k1")):
        chip(s, 20 + i * 62, 186, 54, k, "warnbg", "warn")
    s.arrow([(206, 71), (300, 100)], "acc")
    s.arrow([(144, 201), (300, 176)], "warn")
    # 조인 서브태스크
    s.rect(306, 20, 470, 240, "tm", "sub", 1.4, 14)
    s.text(322, 44, "조인 서브태스크 (키별 상태)", 12.5, "sub", 700)
    s.rect(322, 60, 214, 184, "panel", "acc", 1.5, 10)
    s.text(338, 84, "클릭 대기", 13, "ink", 700)
    s.rect(546, 60, 214, 184, "panel", "warn", 1.5, 10)
    s.text(562, 84, "주문 대기", 13, "ink", 700)
    for i, (k, v, hit) in enumerate((("k1", "클릭 2건", True), ("k2", "클릭 1건", False))):
        y = 100 + i * 40
        s.rect(338, y, 182, 30, "okbg" if hit else "soft", "ok" if hit else "line", 1.3, 6)
        s.text(352, y + 20, k, 12.5, "ink", 700)
        s.text(508, y + 20, v, 12, "sub", 600, "end")
    for i, (k, v, hit) in enumerate((("k1", "주문 1건", True), ("k3", "주문 1건", False))):
        y = 100 + i * 40
        s.rect(562, y, 182, 30, "okbg" if hit else "soft", "ok" if hit else "line", 1.3, 6)
        s.text(576, y + 20, k, 12.5, "ink", 700)
        s.text(732, y + 20, v, 12, "sub", 600, "end")
    s.text(429, 222, "…", 16, "sub", 700, "middle")
    s.text(653, 222, "…", 16, "sub", 700, "middle")
    # 결과
    s.arrow([(778, 140), (836, 140)], "ok")
    chip(s, 842, 112, 120, "k1 클릭 × 주문", "okbg", "ok", h=56)
    # 번호
    s.badge(300, 100, "1", "acc")
    s.badge(540, 115, "2", "ok")
    s.badge(429, 254, "3", "bad")
    s.badge(653, 254, "3", "bad")
    return s.render()


# ------------------------------------------------------------- (2) 조인 종류별로 상태에 남는 것
def fig_join_kinds():
    s = Svg(0, 0, "조인 종류별 상태")
    X0, X1 = 230, 900         # 시간축: 왼쪽 = 과거, 오른쪽 = 지금
    rows = [
        ("일반 조인", [(X0, X1, "badbg", "bad", "양쪽 전부 · 계속 쌓임")]),
        ("일반 조인 + TTL", [(X0, 620, "panel", "line", "TTL 지나 지워짐"), (620, X1, "warnbg", "warn", "최근 TTL만큼")]),
        ("구간 조인", [(X0, 760, "panel", "line", "워터마크 지나 지워짐"), (760, X1, "okbg", "ok", "±구간만")]),
        ("윈도우 조인", [(X0, 700, "panel", "line", "닫힌 윈도우는 지워짐"), (700, X1, "okbg", "ok", "지금 윈도우만")]),
        ("temporal 조인", [(X0, X1, "panel", "line", None)]),
        ("lookup 조인", []),
    ]
    for i, (name, bands) in enumerate(rows):
        y = 20 + i * 52
        s.rect(20, y, X1 - 20 + 20, 42, "soft", "line", 1.1, 10)
        s.text(36, y + 26, name, 12.5, "ink", 700)
        for x0, x1, f, st, t in bands:
            if name == "temporal 조인":
                continue
            s.rect(x0, y + 7, x1 - x0, 28, f, st, 1.3, 6, None if f != "panel" else "4 3")
            if t:
                s.text((x0 + x1) / 2, y + 25.5, t, 12, "ink" if f != "panel" else "sub", 700, "middle")
        if name == "temporal 조인":
            for j, t in enumerate(("k1 v1", "k1 v2", "k2 v1")):
                s.rect(X1 - 330 + j * 110, y + 7, 100, 28, "okbg", "ok", 1.3, 6)
                s.text(X1 - 280 + j * 110, y + 25.5, t, 12, "ink", 700, "middle")
            s.text(X0 + 10, y + 25.5, "차원 쪽 키별 버전", 12, "sub", 700)
        if name == "lookup 조인":
            s.text(X0 + 10, y + 25.5, "상태 없음", 12, "sub", 700)
            s.rect(X1 - 150, y + 7, 150, 28, "panel", "acc", 1.3, 6)
            s.text(X1 - 75, y + 25.5, "외부 테이블 조회", 12, "acc", 700, "middle")
    yb = 20 + len(rows) * 52 + 8
    s.arrow([(X0, yb), (X1, yb)], "sub", sw=1.4)
    s.text(X0, yb + 20, "과거", 11.5, "sub", 600)
    s.text(X1, yb + 20, "지금", 11.5, "sub", 600, "end")
    return s.render()


# ------------------------------------------------------------- (3) 조인별 병목 모양
PW, PH = 470, 210


def panel(s, x, y, title, w=PW, h=PH):
    s.rect(x, y, w, h, "soft", "line", 1.2, 12)
    s.text(x + 16, y + 26, title, 13, "ink", 700)


def wm(s, x, y0, y1, label, color="warn"):
    s.add(f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1}" style="stroke:{V[color]}" stroke-width="2" stroke-dasharray="5 4"/>')
    s.text(x, y0 - 6, label, 11.5, color, 700, "middle")


def fig_bn_regular():
    s = Svg(0, 0, "일반 조인 병목")
    x, y = 20, 0
    for i, (k, hot) in enumerate((("상품 A", 1), ("상품 A", 1), ("상품 B", 0), ("상품 A", 1), ("상품 A", 1))):
        chip(s, x + 16, y + 44 + i * 31, 70, k, "warnbg" if hot else "accbg", "warn" if hot else "acc", h=24, size=11.5)
    for i, (name, busy) in enumerate((("서브태스크 0", 1), ("서브태스크 1", 0), ("서브태스크 2", 0))):
        yy = y + 50 + i * 52
        chip(s, x + 150, yy, 110, name, "badbg" if busy else "panel", "bad" if busy else "line", h=36, size=12)
        s.rect(x + 276, yy + 8, 170 if busy else 34, 20, "badbg" if busy else "okbg", "bad" if busy else "ok", 1.2, 4)
    s.text(x + 361, y + 51, "상태", 11.5, "bad", 700, "middle")
    s.arrow([(x + 90, y + 56), (x + 146, y + 66)], "warn")
    s.arrow([(x + 90, y + 118), (x + 146, y + 76)], "warn")
    s.arrow([(x + 90, y + 180), (x + 146, y + 82)], "warn")
    s.arrow([(x + 90, y + 118), (x + 146, y + 120)], "acc")
    return s.render()


def fig_bn_interval():
    s = Svg(0, 0, "구간 조인 병목")
    x, y = 20, 0
    for i in range(7):
        s.rect(x + 40 + i * 40, y + 70, 32, 26, "badbg", "bad", 1.2, 4)
    s.text(x + 170, y + 116, "지울 때가 지났지만 못 지운 상태", 11.5, "bad", 700, "middle")
    s.rect(x + 330, y + 70, 110, 26, "okbg", "ok", 1.3, 4)
    s.text(x + 385, y + 88, "±구간", 11.5, "ok", 700, "middle")
    wm(s, x + 30, y + 58, y + 176, "")
    s.text(x + 24, y + 52, "워터마크 (멈춤)", 11.5, "warn", 700)
    chip(s, x + 200, y + 140, 160, "쉬는 파티션 · 데이터 없음", "panel", "line", "sub", h=26, size=11.5, dash="4 3")
    s.arrow([(x + 30, y + 190), (x + 450, y + 190)], "sub", sw=1.3)
    s.text(x + 450, y + 205, "지금", 11, "sub", 600, "end")
    return s.render()


def fig_bn_window():
    s = Svg(0, 0, "윈도우 조인 병목")
    x, y = 20, 0
    for i, bx in enumerate((x + 30, x + 170, x + 310)):
        s.rect(bx, y + 52, 136, 24, "accbg", "acc", 1.2, 5)
        s.text(bx + 68, y + 69, f"윈도우 {i + 1}", 11.5, "ink", 700, "middle")
        s.rect(bx + 120, y + 92, 16, 78, "warnbg", "warn", 1.3, 3)
    s.text(x + 40, y + 136, "결과", 11.5, "warn", 700)
    s.arrow([(x + 30, y + 186), (x + 450, y + 186)], "sub", sw=1.3)
    return s.render()


def fig_bn_temporal():
    s = Svg(0, 0, "temporal 조인 병목")
    x, y = 20, 0
    s.text(x + 16, y + 78, "주문", 12, "sub", 700)
    s.text(x + 16, y + 148, "환율", 12, "sub", 700)
    s.rect(x + 90, y + 132, 60, 24, "okbg", "ok", 1.2, 4)
    s.text(x + 120, y + 149, "변경", 11.5, "ok", 700, "middle")
    s.rect(x + 160, y + 56, 284, 36, "warnbg", "warn", 1.2, 6, "4 3")
    for i in range(8):
        s.rect(x + 70 + i * 46, y + 62, 36, 24, "accbg", "acc", 1.2, 4)
    s.text(x + 304, y + 106, "결과 대기", 11.5, "warn", 700, "middle")
    wm(s, x + 160, y + 120, y + 192, "", "warn")
    s.text(x + 172, y + 182, "환율 워터마크 (멈춤)", 11.5, "warn", 700)
    return s.render()


def fig_bn_lookup():
    s = Svg(0, 0, "lookup 조인 병목")
    x, y = 20, 0
    chip(s, x + 30, y + 70, 90, "소스", "panel", "line", h=40)
    for i in range(5):
        s.rect(x + 160 + i * 26, y + 76, 20, 28, "badbg", "bad", 1.2, 3)
    s.text(x + 212, y + 126, "버퍼 가득", 11.5, "bad", 700, "middle")
    chip(s, x + 320, y + 64, 150, "조인 서브태스크", "panel", "acc", h=52)
    s.arrow([(x + 124, y + 90), (x + 154, y + 90)], "sub")
    s.arrow([(x + 294, y + 90), (x + 316, y + 90)], "sub")
    s.arrow([(x + 395, y + 118), (x + 395, y + 136)], "ok")
    chip(s, x + 355, y + 140, 80, "결과", "okbg", "ok", h=32)
    chip(s, x + 700, y + 64, 200, "외부 DB · 조회 느림", "badbg", "bad", h=52)
    s.arrow([(x + 470, y + 76), (x + 696, y + 76)], "acc", dash=True)
    s.arrow([(x + 696, y + 104), (x + 470, y + 104)], "bad", dash=True)
    s.text(x + 583, y + 66, "레코드마다 조회", 11.5, "acc", 700, "middle")
    s.text(x + 583, y + 126, "늦은 응답", 11.5, "bad", 700, "middle")
    s.arrow([(x + 300, y + 152), (x + 75, y + 152), (x + 75, y + 114)], "bad", dash=True)
    s.text(x + 190, y + 170, "백프레셔", 11.5, "bad", 700, "middle")
    return s.render()


FIGS = {"join-state": fig_join_state, "join-kinds": fig_join_kinds, "bn-regular": fig_bn_regular, "bn-interval": fig_bn_interval, "bn-window": fig_bn_window, "bn-temporal": fig_bn_temporal, "bn-lookup": fig_bn_lookup}
