"""모든 그림이 공유하는 SVG 도구와 여백 규칙.

여백은 여기 상수만 고치면 모든 그림에 똑같이 적용된다.
- 캔버스 크기는 손으로 정하지 않는다. 그린 요소 전체의 범위를 재서 PAD 만큼 여백을 둔다.
- 색은 CSS 변수라 페이지 다크 모드를 따른다.
"""
import math
import re

# ---------------------------------------------------------------- 여백 규칙
PAD = 22      # 그림 바깥 여백 (상하좌우 동일)
ZPAD = 14     # 영역(점선 테두리)과 안쪽 상자 사이 여백 (좌·우·아래)
ZHEAD = 40    # 영역 위쪽: 제목 자리 포함 여백
ZGAP = 12     # 영역 제목의 왼쪽 들여쓰기 (ZPAD 에 더함)
GAP = 22      # 블록 사이 세로 간격 (그림 아래 범례·캡션 등)

V = {k: f"var(--{k})" for k in (
    "ink", "sub", "line", "soft", "acc", "accbg", "ok", "okbg", "warn", "warnbg",
    "bad", "badbg", "tm", "panel", "figbg")}
MARK_KEYS = ("sub", "acc", "ok", "warn", "bad")


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text_width(s, size, weight=400):
    """글자 폭 대략치: 한글·한자는 글자 크기만큼, 그 외는 0.58배."""
    w = sum(size * (0.95 if ord(c) > 0x2E80 else 0.58) for c in str(s))
    return w * (1.04 if weight >= 600 else 1.0)


_NUM = r"(-?[\d.]+)"


class Svg:
    """그린 요소의 범위를 자동으로 추적해 viewBox 를 정하는 SVG 빌더."""

    def __init__(self, w, h, label):
        # w, h 는 예전 호환용. 실제 크기는 그린 내용으로 정해진다.
        self.label, self.o = label, []
        self.bb = [math.inf, math.inf, -math.inf, -math.inf]

    # -- 범위 추적
    def _ext(self, x0, y0, x1, y1):
        b = self.bb
        b[0], b[1] = min(b[0], x0, x1), min(b[1], y0, y1)
        b[2], b[3] = max(b[2], x0, x1), max(b[3], y0, y1)

    def _track(self, s):
        if s.startswith("<rect"):
            m = re.search(rf'x="{_NUM}" y="{_NUM}" width="{_NUM}" height="{_NUM}"', s)
            if m:
                x, y, w, h = map(float, m.groups())
                self._ext(x, y, x + w, y + h)
        elif s.startswith("<circle"):
            m = re.search(rf'cx="{_NUM}" cy="{_NUM}" r="{_NUM}"', s)
            if m:
                cx, cy, r = map(float, m.groups())
                self._ext(cx - r, cy - r, cx + r, cy + r)
        elif s.startswith("<line"):
            m = re.search(rf'x1="{_NUM}" y1="{_NUM}" x2="{_NUM}" y2="{_NUM}"', s)
            if m:
                x1, y1, x2, y2 = map(float, m.groups())
                self._ext(x1, y1, x2, y2)
        elif s.startswith("<path"):
            m = re.search(r'd="([^"]+)"', s)
            if m:
                nums = list(map(float, re.findall(r"-?[\d.]+", m.group(1))))
                for x, y in zip(nums[0::2], nums[1::2]):
                    self._ext(x - 6, y - 6, x + 6, y + 6)  # 화살촉 몫
        elif s.startswith("<text"):
            m = re.search(rf'x="{_NUM}" y="{_NUM}" font-size="{_NUM}"', s)
            if m:
                x, y, size = map(float, m.groups())
                body = re.sub(r"<[^>]+>", "", s[s.index(">") + 1:])
                weight = 700 if 'font-weight="7' in s or 'font-weight="6' in s else 400
                w = text_width(body, size, weight)
                anchor = re.search(r'text-anchor="(\w+)"', s)
                a = anchor.group(1) if anchor else "start"
                x0 = x - w if a == "end" else x - w / 2 if a == "middle" else x
                self._ext(x0, y - size, x0 + w, y + size * 0.3)

    def add(self, s):
        self._track(s)
        self.o.append(s)

    # -- 그리기
    def rect(self, x, y, w, h, fill="soft", stroke="line", sw=1.3, rx=8, dash=None, op=1):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" style="fill:{V[fill]};'
                 f'stroke:{V[stroke]}" stroke-width="{sw}"{d} opacity="{op}"/>')

    def text(self, x, y, s, size=13, color="ink", weight=400, anchor="start", op=1):
        self.add(f'<text x="{x}" y="{y}" font-size="{size}" style="fill:{V[color]}" font-weight="{weight}" '
                 f'text-anchor="{anchor}" opacity="{op}">{esc(s)}</text>')

    def lines(self, x, y, items, size=12, color="sub", gap=17, anchor="start", op=1, weight=400):
        for i, s in enumerate(items):
            self.text(x, y + i * gap, s, size, color, weight, anchor, op)

    def arrow(self, pts, color="sub", dash=False, sw=2):
        d = "M" + " L".join(f"{x},{y}" for x, y in pts)
        da = ' stroke-dasharray="6 4"' if dash else ""
        self.add(f'<path d="{d}" fill="none" style="stroke:{V[color]}" stroke-width="{sw}"{da} '
                 f'stroke-linejoin="round" marker-end="url(#{self.mid}-{color})"/>')

    def badge(self, x, y, n, color="warn"):
        self.add(f'<circle cx="{x}" cy="{y}" r="11" style="fill:{V[color]}"/>')
        self.o.append(f'<text x="{x}" y="{y + 4.5}" font-size="12" fill="#fff" font-weight="700" '
                      f'text-anchor="middle">{esc(n)}</text>')

    def zone(self, members, title, fill, top=None):
        """members = [(x, y, w, h), ...] 를 감싸는 점선 영역. 여백은 ZPAD/ZHEAD 공통값."""
        x0 = min(m[0] for m in members) - ZPAD
        x1 = max(m[0] + m[2] for m in members) + ZPAD
        y0 = (top if top is not None else min(m[1] for m in members)) - ZHEAD
        y1 = max(m[1] + m[3] for m in members) + ZPAD
        self.add(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="14" '
                 f'style="fill:{V[fill]};stroke:{V["sub"]}" fill-opacity="0.45" stroke-width="1.2" '
                 f'stroke-dasharray="7 5"/>')
        self.text(x0 + ZPAD + ZGAP - 10, y0 + 24, title, 12.5, "sub", 700)

    def next_y(self, extra=0):
        """지금까지 그린 내용의 맨 아래 + GAP. 아래에 이어 붙일 요소의 기준선."""
        return self.bb[3] + GAP + extra

    @property
    def mid(self):
        return "f" + str(sum((i + 1) * ord(c) for i, c in enumerate(self.label)))

    def render(self):
        marks = "".join(
            f'<marker id="{self.mid}-{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M0,0L10,5L0,10z" style="fill:{V[k]}"/></marker>'
            for k in MARK_KEYS)
        x0, y0, x1, y1 = self.bb
        x0, y0 = math.floor(x0 - PAD), math.floor(y0 - PAD)
        w, h = math.ceil(x1 + PAD) - x0, math.ceil(y1 + PAD) - y0
        # 원래 크기보다 크게 늘리지 않는다 (작은 그림이 글자만 커지는 것 방지)
        style = f"max-width:{w}px;margin:0 auto" + (";min-width:0" if w < 680 else "")
        return (f'<svg viewBox="{x0} {y0} {w} {h}" style="{style}" role="img" aria-label="{esc(self.label)}">'
                f'<defs>{marks}</defs>' + "".join(self.o) + "</svg>")
