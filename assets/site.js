(function () {
  // 테마 전환 (저장 실패해도 동작)
  var root = document.documentElement;
  function get() { try { return localStorage.getItem("theme"); } catch (e) { return null; } }
  function set(v) { try { localStorage.setItem("theme", v); } catch (e) {} }
  var saved = get();
  if (saved) root.setAttribute("data-theme", saved);
  var btn = document.querySelector(".theme-btn");
  function isDark() {
    var t = root.getAttribute("data-theme");
    return t ? t === "dark" : window.matchMedia("(prefers-color-scheme: dark)").matches;
  }
  function label() { if (btn) btn.textContent = isDark() ? "라이트 모드" : "다크 모드"; }
  if (btn) btn.addEventListener("click", function () {
    var v = isDark() ? "light" : "dark";
    root.setAttribute("data-theme", v); set(v); label();
  });
  label();

  // 복사 억제: 코드 블록 · 인라인 코드 밖에서는 우클릭 · 복사 · 끌기를 막는다
  function inCode(n) { return n && n.closest && n.closest("pre.code, code"); }
  function el(n) { return n && n.nodeType === 3 ? n.parentElement : n; }
  ["contextmenu", "dragstart"].forEach(function (ev) {
    document.addEventListener(ev, function (e) { if (!inCode(el(e.target))) e.preventDefault(); });
  });
  document.addEventListener("copy", function (e) {
    var s = window.getSelection && window.getSelection();
    if (!s || !s.rangeCount || !inCode(el(s.getRangeAt(0).commonAncestorContainer))) e.preventDefault();
  });

  // 새 탭은 문서 본문(장) 안에서 다른 페이지를 여는 링크만.
  // 상단 바 · 목록 행 · 이전/다음 같은 이동 링크는 같은 탭에서 이동한다.
  document.querySelectorAll(".chapter a[href]").forEach(function (a) {
    var h = a.getAttribute("href");
    if (h && h.charAt(0) !== "#") { a.target = "_blank"; a.rel = "noopener"; }
  });

  // 목차: 보고 있는 장 강조
  var links = [].slice.call(document.querySelectorAll(".toc a"));
  if (!links.length || !("IntersectionObserver" in window)) return;
  var byId = {};
  links.forEach(function (a) { byId[a.getAttribute("href").slice(1)] = a; });
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      if (e.isIntersecting) {
        links.forEach(function (a) { a.classList.remove("on"); });
        var a = byId[e.target.id]; if (a) a.classList.add("on");
      }
    });
  }, { rootMargin: "-30% 0px -60% 0px" });
  document.querySelectorAll(".chapter[id]").forEach(function (s) { io.observe(s); });
})();
