"""그림 모듈 템플릿. tools/figures_<주제>_<문서>.py 로 복사해서 쓴다.

규칙 (STYLE.md 그림 절)
- 그림 안에는 상자 이름, 짧은 화살표 라벨, 번호 배지, 범례만 둔다. 설명 문장은 본문으로.
- 번호 배지는 본문 <ol> 번호와 맞추고, 읽는 순서(위 → 아래, 왼쪽 → 오른쪽)대로 놓는다.
- 캔버스 크기는 정하지 않는다. Svg 가 그린 범위를 재서 여백(PAD)을 둔다. 여백 상수는 svgkit 에만.
- 색은 V 의 CSS 변수 이름만 쓴다 (다크 모드 자동). 이름: ink sub line soft acc accbg ok okbg warn warnbg bad badbg tm panel figbg
- 그림 이름은 사이트 전체에서 하나의 이름 공간이다. "<주제>-" 접두어를 붙인다 (예: kafka-txn-flow).

자주 쓰는 모양 (실물 예시)
- 장면 줄(storyboard): 한 줄 = 한 순간, 같은 칸을 줄마다 반복 → tools/figures_flink_sink.py
- 시간 레인: 가로 = 시간, 세로 = 참여자            → tools/figures_flink_dataflow.py (barrier-stream)
- 영역 묶음: 점선 영역 안에 상자들 (s.zone)        → tools/figures_flink_lifecycle.py (overview)
- 작은 패널: 한 현상만 보여 주는 작은 그림          → tools/figures_flink_join.py (fig_bn_*)
"""
from svgkit import V, Svg  # noqa: F401


def chip(s, x, y, w, label, fill="panel", stroke="line", tcolor="ink", h=30, size=12.5, weight=700, dash=None):
    """글자가 가운데 놓인 상자. 대부분의 그림은 이것과 화살표 · 배지로 충분하다."""
    s.rect(x, y, w, h, fill, stroke, 1.4, 7, dash)
    s.text(x + w / 2, y + h / 2 + size * 0.38, label, size, tcolor, weight, "middle")


# ------------------------------------------------------------- 예시: 왼쪽 → 오른쪽 흐름 + 번호 배지
def fig_example_flow():
    s = Svg(0, 0, "예시 흐름")                     # 두 번째 인자까지는 예전 호환용, 라벨은 접근성 이름
    chip(s, 20, 40, 120, "소스", "accbg", "acc")
    chip(s, 220, 40, 140, "처리", "panel", "line")
    chip(s, 440, 40, 120, "싱크", "okbg", "ok")
    s.arrow([(142, 55), (216, 55)], "acc")          # 점 목록을 잇는 화살표. 꺾으려면 점을 더 넣는다
    s.arrow([(362, 55), (436, 55)], "ok")
    s.badge(179, 38, "1", "acc")                    # 본문 <ol> 1번과 짝
    s.badge(399, 38, "2", "ok")
    # 범례가 필요하면 그린 내용 아래에 붙인다: y = s.next_y()
    return s.render()


# 빌드가 읽는 표. 키 = 원본에 쓰는 <!--fig:이름--> 의 이름
FIGS = {
    "template-example-flow": fig_example_flow,
}
