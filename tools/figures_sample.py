"""src/sample/sample.html 그림. 템플릿을 채운 예시라 새 그림을 만들 때 참고한다."""
from svgkit import V, Svg  # noqa: F401


def chip(s, x, y, w, label, fill="panel", stroke="line", tcolor="ink", h=34, size=12.5, weight=700, dash=None):
    s.rect(x, y, w, h, fill, stroke, 1.4, 7, dash)
    s.text(x + w / 2, y + h / 2 + size * 0.38, label, size, tcolor, weight, "middle")


def fig_sample_flow():
    """왼쪽 → 오른쪽 흐름. 번호 배지는 본문 <ol> 1 ~ 3 과 짝."""
    s = Svg(0, 0, "문서가 사이트에 오르는 흐름")
    chip(s, 20, 40, 150, "src 원본", "accbg", "acc")
    chip(s, 240, 40, 150, "build.py", "panel", "line")
    chip(s, 460, 40, 150, "규칙 검사", "warnbg", "warn")
    chip(s, 680, 40, 150, "사이트 HTML", "okbg", "ok")
    s.arrow([(172, 57), (236, 57)], "acc")
    s.arrow([(392, 57), (456, 57)], "sub")
    s.arrow([(612, 57), (676, 57)], "ok")
    s.badge(315, 34, "1", "acc")
    s.badge(535, 34, "2", "warn")
    s.badge(755, 34, "3", "ok")
    # 아래 줄: 실패하면 되돌아감 (점선)
    s.arrow([(535, 76), (535, 110), (95, 110), (95, 78)], "bad", dash=True)
    s.text(315, 128, "위반하면 빌드 중단", 12, "bad", 700, "middle")
    return s.render()


FIGS = {"sample-flow": fig_sample_flow}
