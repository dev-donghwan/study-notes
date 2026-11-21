"""flink/job-lifecycle 그림. 색은 CSS 변수라 페이지 다크 모드를 따른다."""

from svgkit import V, Svg, esc  # noqa: F401  (여백 규칙은 svgkit 상수)


# ------------------------------------------------------------------ 전체 지도
BOX = {
    "user": (30, 40, 180, 56, "사용자", ["FlinkDeployment 적용"]),
    "operator": (30, 140, 180, 56, "Flink Operator", ["JM 파드 생성 · 재배포 관리"]),
    "kafka": (790, 40, 180, 60, "소스", ["읽어 오는 곳 · 예: Kafka"]),
    "s3": (790, 130, 180, 80, "상태 저장소", ["체크포인트 · HA", "예: S3"]),
    "k8s": (790, 240, 180, 60, "쿠버네티스 API", ["파드 생성 · 종료"]),
    "result": (790, 330, 180, 60, "싱크", ["결과를 쓰는 곳 · 예: 테이블"]),
}
JM = (250, 24, 500, 170)
JMIN = {
    "dispatcher": (266, 62, 145, 116, "Dispatcher", ["잡 접수", "웹 UI · REST"]),
    "rm": (423, 62, 150, 116, "ResourceManager", ["슬롯 · TM 관리", "TM 파드 요청"]),
    "jobmaster": (585, 62, 150, 116, "JobMaster", ["실행 계획 · 배치", "장애 처리", "체크포인트 지휘"]),
}
TMS = {"tm1": (250, 236, 240, 256, "TaskManager 1"), "tm2": (510, 236, 240, 256, "TaskManager 2")}
SLOTS = {"tm1": [(262, 272), (374, 272)], "tm2": [(522, 272), (634, 272)]}
SW, SH = 104, 210
FULL = {("tm1", 0): [("소스·A·B 0", 1), ("C·싱크 0", 2)], ("tm1", 1): [("소스·A·B 1", 1), ("C·싱크 1", 2)],
        ("tm2", 0): [("C·싱크 2", 2)], ("tm2", 1): [("C·싱크 3", 2)]}


def task_colors(t):
    return ("accbg", "acc") if t == 1 else ("okbg", "ok")


def draw_zones(s):
    top = min(JM[1], *(b[1] for b in BOX.values()))   # 세 영역의 윗선을 맞춤
    deploy = [BOX[k][:4] for k in ("user", "operator")]
    cluster = [JM] + [v[:4] for v in TMS.values()]
    external = [BOX[k][:4] for k in ("kafka", "s3", "k8s", "result")]
    s.zone(deploy, "배포 · 관리", "soft", top)
    s.zone(cluster, "Flink 클러스터 — 잡 하나 (application 모드)", "accbg", top)
    s.zone(external, "외부 시스템", "okbg", top)


def draw_map(s, hl=(), tm="full", dead=(), state_tag=False):
    draw_zones(s)
    focus = bool(hl)

    def opa(k):
        return 1 if (not focus or k in hl) else 0.35

    def stroke(k):
        return ("warn", 2.6) if (focus and k in hl) else ("line", 1.3)

    for k, (x, y, w, h, t, ls) in BOX.items():
        st, sw = stroke(k)
        s.rect(x, y, w, h, "soft", st, sw, 8, op=opa(k))
        s.text(x + 12, y + 22, t, 14, "ink", 700, op=opa(k))
        s.lines(x + 12, y + 41, ls, 12, "sub", 17, op=opa(k))
    jm_on = (not focus) or any(k in hl for k in ("dispatcher", "rm", "jobmaster"))
    x, y, w, h = JM
    s.rect(x, y, w, h, "warnbg", "warn" if jm_on else "line", 1.6, 12, op=1 if jm_on else 0.35)
    s.text(x + 16, y + 24, "JobManager (파드)", 14, "ink", 700, op=1 if jm_on else 0.35)
    for k, (bx, by, bw, bh, t, ls) in JMIN.items():
        st, sw = stroke(k)
        s.rect(bx, by, bw, bh, "panel", st, sw, 8, op=opa(k))
        s.text(bx + bw / 2, by + 24, t, 13.5, "ink", 700, "middle", op=opa(k))
        s.lines(bx + bw / 2, by + 48, ls, 12, "sub", 18, "middle", op=opa(k))
    for k, (tx, ty, tw, th, t) in TMS.items():
        on = opa(k)
        if tm == "empty":
            # 지도와 같은 자리·모양의 빈 윤곽 = 아직 없는 것
            s.add(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="12" fill="none" '
                  f'style="stroke:{V["sub"]}" stroke-width="1.6" stroke-dasharray="8 6" opacity="0.7"/>')
            for sx, sy in SLOTS[k]:
                s.add(f'<rect x="{sx}" y="{sy}" width="{SW}" height="{SH}" rx="8" fill="none" '
                      f'style="stroke:{V["line"]}" stroke-width="1.1" stroke-dasharray="4 5"/>')
            s.text(tx + 14, ty + 24, t + " — 아직 없음", 13.5, "sub", 700)
            s.text(tx + tw / 2, ty + th / 2 + 4, "아직 생성 전", 12, "sub", 600, "middle")
            continue
        is_dead = k in dead
        st, sw = ("bad", 2.6) if is_dead else stroke(k)
        s.rect(tx, ty, tw, th, "badbg" if is_dead else "tm", st, sw, 12, op=on)
        s.text(tx + 14, ty + 24, t + " (파드)", 14, "bad" if is_dead else "ink", 700, op=on)
        for i, (sx, sy) in enumerate(SLOTS[k]):
            s.rect(sx, sy, SW, SH, "panel", "sub", 1.1, 8, "5 4", op=on)
            s.text(sx + 8, sy + 18, f"슬롯 {i}", 11.5, "sub", 600, op=on)
            if tm == "up":
                s.text(sx + SW / 2, sy + SH / 2, "빈 슬롯", 12, "sub", 400, "middle", op=on)
            elif tm == "full":
                for j, (name, t_) in enumerate(FULL[(k, i)]):
                    f, c = task_colors(t_)
                    cy = sy + 30 + j * 58
                    s.rect(sx + 6, cy, SW - 12, 46 if state_tag else 36, f, c, 1.4, 6, op=on)
                    s.text(sx + SW / 2, cy + 22, name, 11.5, "ink", 600, "middle", op=on)
                    if state_tag:
                        s.text(sx + SW / 2, cy + 39, "+ 상태 백엔드", 10.5, c, 600, "middle", op=on)
        if is_dead:
            s.add(f'<path d="M{tx+24},{ty+44} L{tx+tw-24},{ty+th-24} M{tx+tw-24},{ty+44} L{tx+24},{ty+th-24}" '
                  f'style="stroke:{V["bad"]}" stroke-width="4" opacity="0.5"/>')


def side_note(s, title, items, color="line", tcolor="ink", h=196):
    s.rect(30, 236, 200, h, "panel", color, 1.6 if color != "line" else 1.3, 10)
    y = 260
    if title:
        s.text(42, y, title, 13.5, tcolor, 700)
        y += 24
    s.lines(42, y, items, 12.5, "ink", 20)


def legend_tasks(s, x, y):
    s.rect(x, y, 14, 12, "accbg", "acc", 1.2, 3)
    s.text(x + 20, y + 11, "태스크 소스·A·B (병렬도 2)", 12, "sub")
    s.rect(x + 210, y, 14, 12, "okbg", "ok", 1.2, 3)
    s.text(x + 230, y + 11, "태스크 C·싱크 (병렬도 4)", 12, "sub")


# ------------------------------------------------------------------ 그림들
def fig_overview():
    s = Svg(1000, 530, "Flink 전체 지도")
    draw_map(s)
    s.arrow([(120, 96), (120, 138)])
    s.arrow([(210, 168), (248, 130)])
    s.arrow([(500, 194), (500, 234)], "acc", dash=True)
    s.text(508, 220, "배치 · 지휘", 11.5, "acc", 600)
    legend_tasks(s, 250, s.next_y())
    return s.render()


def fig_jm_sequence():
    s = Svg(1000, 548, "JM 안에서 일어나는 일")
    lanes = [("Dispatcher", 110, "warn", 0), ("JobMaster", 310, "warn", 226),
             ("ResourceManager", 510, "warn", 0), ("쿠버네티스 API", 710, "sub", 0), ("TaskManager", 895, "sub", 392)]
    for name, x, c, start in lanes:
        s.rect(x - 80, 16, 160, 40, "warnbg" if c == "warn" else "soft", c, 1.5, 8)
        s.text(x, 41, name, 13.5, "ink", 700, "middle")
        y0 = max(60, start)
        s.add(f'<line x1="{x}" y1="{y0}" x2="{x}" y2="534" style="stroke:{V["line"]}" stroke-width="2" '
              f'stroke-dasharray="5 5"/>')
        if start:
            s.rect(x - 34, start - 16, 68, 22, "panel", c, 1.2, 11)
            s.text(x, start - 1, "생성됨", 11, c, 700, "middle")
    # 1 JM 파드 시작
    s.badge(24, 92, "1")
    s.rect(40, 78, 560, 30, "warnbg", "warn", 1.2, 8)
    s.text(320, 98, "JM 파드 시작 (TM 0개)", 12.5, "ink", 600, "middle")
    # 2 main() 실행
    s.badge(24, 146, "2")
    s.rect(40, 124, 200, 44, "panel", "warn", 1.4, 8)
    s.text(140, 151, "main() → 잡 그래프", 12.5, "ink", 700, "middle")
    # 3 JobMaster 생성
    s.badge(24, 200, "3")
    s.text(192, 192, "JobMaster 생성", 11.5, "warn", 700, "middle")
    s.arrow([(112, 200), (306, 200), (306, 206)], "warn")
    # 4 실행 그래프 + 슬롯 요청
    s.badge(24, 268, "4")
    s.rect(230, 246, 160, 44, "panel", "warn", 1.4, 8)
    s.text(310, 273, "실행 그래프", 12.5, "ink", 700, "middle")
    s.text(410, 304, "슬롯 4개 요청", 11.5, "warn", 700, "middle")
    s.arrow([(312, 312), (506, 312)], "warn")
    # 5 TM 파드 요청
    s.badge(24, 346, "5")
    s.text(610, 338, "TM 파드 2개 요청", 11.5, "warn", 700, "middle")
    s.arrow([(512, 346), (706, 346)], "warn")
    s.text(800, 366, "파드 생성", 11.5, "sub", 700, "middle")
    s.arrow([(712, 374), (890, 374)], "sub")
    # 6 등록
    s.badge(24, 420, "6")
    s.text(700, 412, "등록 · 슬롯 보고", 11.5, "acc", 700, "middle")
    s.arrow([(893, 420), (514, 420)], "acc", dash=True)
    # 7 슬롯 제공
    s.badge(24, 456, "7")
    s.text(410, 440, "JobMaster 연결", 11.5, "acc", 700, "middle")
    s.arrow([(508, 448), (314, 448)], "acc", dash=True)
    s.text(700, 466, "슬롯 제공", 11.5, "acc", 700, "middle")
    s.arrow([(893, 474), (314, 474)], "acc", dash=True)
    # 8 배포
    s.badge(24, 512, "8")
    s.text(600, 500, "서브태스크 배포", 11.5, "ok", 700, "middle")
    s.arrow([(312, 508), (890, 508)], "ok")
    return s.render()


def fig_jobgraph():
    s = Svg(1000, 432, "잡 그래프와 체이닝")

    def node(x, y, label, c="sub", f="panel"):
        s.add(f'<circle cx="{x}" cy="{y}" r="27" style="fill:{V[f]};stroke:{V[c]}" stroke-width="1.8"/>')
        s.text(x, y + 5, label, 13.5, "ink", 700, "middle")

    xs = {"소스": 70, "A": 180, "B": 290, "C": 470, "싱크": 580}
    # ① 작성한 코드
    s.text(24, 30, "작성한 코드", 14, "ink", 700)
    for n, x in xs.items():
        node(x, 84, n)
    for a_, b_ in (("소스", "A"), ("A", "B"), ("C", "싱크")):
        s.arrow([(xs[a_] + 29, 84), (xs[b_] - 29, 84)])
    s.arrow([(xs["B"] + 29, 84), (xs["C"] - 29, 84)], "warn", sw=2.6)
    s.text(380, 72, "keyBy", 12.5, "warn", 700, "middle")
    # 변환 화살표
    s.arrow([(320, 128), (320, 168)], "acc", sw=2.4)
    s.text(334, 154, "체이닝", 12.5, "acc", 700)
    # ③ 체이닝 결과
    s.rect(30, 186, 300, 96, "accbg", "acc", 2, 48)
    s.rect(430, 186, 190, 96, "okbg", "ok", 2, 48)
    for n in ("소스", "A", "B"):
        node(xs[n], 234, n, "acc")
    for n in ("C", "싱크"):
        node(xs[n], 234, n, "ok")
    for a_, b_ in (("소스", "A"), ("A", "B"), ("C", "싱크")):
        s.add(f'<line x1="{xs[a_]+27}" y1="234" x2="{xs[b_]-27}" y2="234" style="stroke:{V["sub"]}" stroke-width="2"/>')
    s.arrow([(332, 234), (428, 234)], "warn", sw=2.6)
    s.text(180, 304, "태스크 1", 12.5, "acc", 700, "middle")
    s.text(525, 304, "태스크 2", 12.5, "ok", 700, "middle")

    # 오른쪽: 왜 keyBy에서 끊기나
    s.rect(672, 16, 304, 196, "soft", "line", 1.3, 12)
    s.text(688, 40, "forward → 묶임", 13, "acc", 700)
    ly = (80, 140); ry = (80, 140)
    for y in ly:
        s.add(f'<circle cx="740" cy="{y}" r="11" style="fill:{V["accbg"]};stroke:{V["acc"]}" stroke-width="1.6"/>')
    for y in ry:
        s.add(f'<circle cx="890" cy="{y}" r="11" style="fill:{V["accbg"]};stroke:{V["acc"]}" stroke-width="1.6"/>')
    for y in ly:
        s.arrow([(752, y), (877, y)], "acc")

    s.rect(672, 226, 304, 196, "soft", "line", 1.3, 12)
    s.text(688, 250, "keyBy → 끊김", 13, "warn", 700)
    ly2 = (300, 360); ry2 = (276, 314, 352, 390)
    for y in ly2:
        s.add(f'<circle cx="740" cy="{y}" r="11" style="fill:{V["accbg"]};stroke:{V["acc"]}" stroke-width="1.6"/>')
    for y in ry2:
        s.add(f'<circle cx="890" cy="{y}" r="11" style="fill:{V["okbg"]};stroke:{V["ok"]}" stroke-width="1.6"/>')
    for y1 in ly2:
        for y2 in ry2:
            s.add(f'<line x1="752" y1="{y1}" x2="878" y2="{y2}" style="stroke:{V["warn"]}" stroke-width="1.4" opacity="0.7"/>')

    return s.render()


def fig_submit():
    s = Svg(1000, 510, "잡 제출")
    draw_map(s, hl=("user", "operator", "dispatcher", "jobmaster", "s3"), tm="empty")
    s.arrow([(120, 96), (120, 138)], "warn"); s.badge(142, 117, "1")
    s.arrow([(210, 168), (264, 140)], "warn"); s.badge(234, 178, "2")
    s.arrow([(340, 178), (340, 186), (660, 186), (660, 180)], "warn"); s.badge(500, 186, "3")
    s.arrow([(735, 100), (788, 158)], "warn"); s.badge(768, 118, "4")
    return s.render()


def fig_execgraph():
    s = Svg(1000, 362, "실행 그래프")
    # 위: 잡 그래프 요약
    s.rect(24, 16, 200, 36, "accbg", "acc", 1.4, 8); s.text(124, 39, "태스크 1  × 병렬도 2", 13, "ink", 700, "middle")
    s.arrow([(226, 34), (318, 34)], "warn"); s.text(272, 27, "keyBy", 11.5, "warn", 700, "middle")
    s.rect(320, 16, 200, 36, "okbg", "ok", 1.4, 8); s.text(420, 39, "태스크 2  × 병렬도 4", 13, "ink", 700, "middle")
    # 왼쪽: 태스크 1 서브태스크 2개
    L = [(150, "0"), (290, "1")]
    for cy, i in L:
        s.rect(40, cy - 28, 230, 56, "accbg", "acc", 1.6, 10)
        s.text(155, cy - 4, f"태스크 1 · 서브태스크 {i}", 13, "ink", 700, "middle")
        s.text(155, cy + 15, "소스 → A → B", 11.5, "sub", 600, "middle")
    # 오른쪽: 태스크 2 서브태스크 4개 + 키 그룹
    R = [(110, 0), (180, 1), (250, 2), (320, 3)]
    for cy, i in R:
        s.rect(600, cy - 26, 214, 52, "okbg", "ok", 1.6, 10)
        s.text(707, cy - 3, f"태스크 2 · 서브태스크 {i}", 13, "ink", 700, "middle")
        s.text(707, cy + 15, "C → 싱크", 11.5, "sub", 600, "middle")
        s.rect(826, cy - 15, 150, 30, "panel", "ok", 1.3, 15)
        s.text(901, cy + 5, f"키 그룹 {i*32} ~ {i*32+31}", 12, "ok", 700, "middle")
    # keyBy: 모든 서브태스크끼리 연결
    for ly, _ in L:
        for ry, _ in R:
            s.add(f'<line x1="272" y1="{ly}" x2="596" y2="{ry}" style="stroke:{V["warn"]}" stroke-width="1.4" opacity="0.55"/>')
    s.rect(352, 196, 168, 50, "panel", "warn", 1.4, 10)
    s.text(436, 226, "keyBy 셔플", 12.5, "warn", 700, "middle")
    return s.render()


def fig_resources():
    s = Svg(1000, 510, "자원 확보")
    draw_map(s, hl=("rm", "jobmaster", "k8s", "tm1", "tm2"), tm="up")
    s.arrow([(660, 62), (660, 52), (498, 52), (498, 60)], "warn"); s.badge(579, 52, "1")
    s.arrow([(530, 178), (530, 214), (775, 214), (775, 270), (788, 270)], "warn"); s.badge(652, 214, "2")
    s.arrow([(800, 300), (800, 320), (754, 320)], "warn"); s.badge(818, 312, "3")
    s.arrow([(460, 236), (460, 180)], "acc", dash=True); s.badge(444, 216, "4", "acc")
    return s.render()


def fig_relation():
    s = Svg(1000, 420, "TM, 슬롯, 서브태스크의 관계")
    # TM 하나를 확대
    s.rect(30, 24, 600, 372, "tm", "sub", 1.6, 14)
    s.text(48, 50, "TaskManager 1  =  파드 하나  =  JVM 프로세스 하나", 14.5, "ink", 700)
    for i, x in enumerate((48, 340)):
        s.rect(x, 66, 272, 228, "panel", "sub", 1.2, 10, "6 4")
        s.text(x + 14, 88, f"슬롯 {i}", 13, "sub", 700)
        for j, (name, f, c) in enumerate(((f"소스·A·B 서브태스크 {i}", "accbg", "acc"),
                                         (f"C·싱크 서브태스크 {i}", "okbg", "ok"))):
            y = 102 + j * 92
            s.rect(x + 14, y, 244, 78, f, c, 1.6, 8)
            s.text(x + 26, y + 24, name, 13, "ink", 700)
            s.text(x + 26, y + 46, "= 스레드 1개", 12, "sub", 400)
            s.rect(x + 150, y + 50, 100, 20, "panel", c, 1.2, 10)
            s.text(x + 200, y + 64, "자기 상태 백엔드", 11, c, 600, "middle")
    # 공유 자원
    s.rect(48, 306, 272, 32, "warnbg", "warn", 1.2, 6)
    s.text(184, 327, "관리 메모리 ½ (슬롯 0 몫)", 12, "warn", 700, "middle")
    s.rect(340, 306, 272, 32, "warnbg", "warn", 1.2, 6)
    s.text(476, 327, "관리 메모리 ½ (슬롯 1 몫)", 12, "warn", 700, "middle")
    s.rect(48, 346, 564, 32, "soft", "line", 1.2, 6)
    s.text(330, 367, "JVM 힙 · CPU — 슬롯끼리 같이 씀 (격리 없음)", 12, "sub", 700, "middle")
    # 오른쪽: 포함 관계와 개수
    s.text(660, 50, "포함 관계", 14, "ink", 700)
    rows = [("TaskManager", "파드 · JVM 하나", "tm", "sub"),
            ("슬롯", "TM당 numberOfTaskSlots 개", "panel", "sub"),
            ("서브태스크", "슬롯 안에 태스크별 1개씩", "okbg", "ok"),
            ("스레드 + 상태 백엔드", "서브태스크마다 1개씩", "accbg", "acc")]
    for i, (a, b, f, c) in enumerate(rows):
        x, y, w = 660 + i * 14, 66 + i * 58, 310 - i * 28
        s.rect(x, y, w, 46, f, c, 1.4, 8)
        s.text(x + 12, y + 20, a, 13, "ink", 700)
        s.text(x + 12, y + 37, b, 11.5, "sub")
    return s.render()


def fig_deploy():
    s = Svg(1000, 530, "서브태스크 배치")
    draw_map(s, hl=("jobmaster", "tm1", "tm2"), tm="full", state_tag=True)
    s.arrow([(620, 178), (430, 268)], "warn")
    s.arrow([(690, 178), (686, 268)], "warn")
    s.text(698, 226, "서브태스크 배포", 12, "warn", 700)
    s.add(f'<path d="M490,360 L510,360" style="stroke:{V["acc"]}" stroke-width="2.5" stroke-dasharray="4 3"/>')
    return s.render()


def fig_summary():
    s = Svg(1000, 530, "한 장 요약")
    draw_map(s, tm="full")
    s.badge(228, 150, "1"); s.badge(712, 48, "2"); s.badge(552, 48, "3"); s.badge(500, 216, "4")
    legend_tasks(s, 250, s.next_y())
    return s.render()


FIGS = {
    "overview": fig_overview, "jm-sequence": fig_jm_sequence, "jobgraph": fig_jobgraph, "submit": fig_submit, "execgraph": fig_execgraph,
    "resources": fig_resources, "relation": fig_relation, "deploy": fig_deploy,
    "summary": fig_summary,
}
