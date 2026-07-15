#!/usr/bin/env python3
"""발행 전 계약 검증기 — blog-publisher가 push 전에 실행한다.

사용법: python tools/check_post.py <slug>
검사 항목 (README 발행 규약의 기계 검사 가능한 부분):
  1) posts/<slug>.html 존재 + 미치환 플레이스홀더({{) 없음
  2) KaTeX 일관성 — 본문에 수식 있으면 head에 KaTeX, 없으면 KaTeX 삭제
  3) 목록 4곳(index/archive/feed/sitemap)에 slug 반영
  4) index.html 최근 글 5개 이하
  5) feed.xml 해당 item의 pubDate가 RFC822
  6) 읽기 시간 — 한글자수/500 + 영단어수/200 (분, 반올림, 최소 1) ↔ meta '약 N분' 일치
  7) 그림 접근성 — figure마다 figcaption, svg마다 aria-label·viewBox
  8) og:url이 posts/<slug>.html과 일치
  9) 스타일 규약 — SVG 색은 CSS 변수만(hex 등 리터럴 금지),
     인라인 style은 overflow 스크롤 래퍼(overflow-x:auto·max-width:100%)만 허용,
     url(#id) 참조는 같은 SVG 안에 정의돼야 함(크로스-SVG 참조 금지)

전부 PASS면 exit 0, 하나라도 FAIL이면 exit 1. stdlib만 사용.
"""

import os
import re
import sys
from email.utils import parsedate_to_datetime

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

results = []  # (ok, label, detail)


def check(ok, label, detail=""):
    results.append((ok, label, detail))


def read(relpath):
    with open(os.path.join(ROOT, relpath), encoding="utf-8") as f:
        return f.read()


def between(text, start_marker, end_marker):
    """마커 주석 사이 구간 (마커는 부분 문자열 매칭)."""
    s = text.find(start_marker)
    e = text.find(end_marker)
    return text[s:e] if s != -1 and e != -1 and s < e else ""


def reading_minutes(article_text):
    plain = re.sub(r"<script\b.*?</script>", "", article_text, flags=re.S)
    plain = re.sub(r"<style\b.*?</style>", "", plain, flags=re.S)
    plain = re.sub(r"<[^>]+>", " ", plain)
    ko = len(re.findall(r"[가-힣]", plain))
    en = len(re.findall(r"[A-Za-z][A-Za-z0-9'-]*", plain))
    return max(1, int(ko / 500 + en / 200 + 0.5)), ko, en


def main():
    if len(sys.argv) != 2:
        print("사용법: python tools/check_post.py <slug>")
        sys.exit(2)
    slug = sys.argv[1].removesuffix(".html")
    post_rel = f"posts/{slug}.html"
    post_path = os.path.join(ROOT, "posts", f"{slug}.html")

    # 1) 존재 + 플레이스홀더
    if not os.path.isfile(post_path):
        print(f"FAIL  포스트 없음: {post_rel}")
        sys.exit(1)
    html = read(post_rel)
    check("{{" not in html, "미치환 플레이스홀더 없음",
          "" if "{{" not in html else "'{{' 잔존 — 템플릿 치환 누락")

    # 본문/헤드 분리
    head = html.split("</head>")[0]
    m = re.search(r"<article\b.*?</article>", html, flags=re.S)
    article = m.group(0) if m else html

    # 2) KaTeX 일관성 (수식 탐지는 article 안에서만 — head의 KaTeX 설정 문자열 오탐 방지)
    has_math = "$$" in article or "\\(" in article
    has_katex = "katex" in head.lower()
    check(has_math == has_katex, "KaTeX head ↔ 본문 수식 일관",
          "" if has_math == has_katex else
          ("수식 있는데 head에 KaTeX 없음" if has_math else "수식 없는데 KaTeX 3줄 잔존 — 삭제"))

    # 3) 목록 4곳 반영
    for rel in ("index.html", "archive.html", "feed.xml", "sitemap.xml"):
        check(slug in read(rel), f"{rel}에 반영", "" if slug in read(rel) else f"'{slug}' 링크 없음")

    # 4) index 최근 글 5개 이하
    recent = between(read("index.html"), "posts:start", "posts:end")
    n_li = len(re.findall(r"<li\b", recent))
    check(n_li <= 5, "index.html 최근 글 5개 이하", f"현재 {n_li}개")

    # 5) feed.xml pubDate RFC822
    feed = read("feed.xml")
    item = next((it for it in re.findall(r"<item\b.*?</item>", feed, flags=re.S) if slug in it), None)
    if item is None:
        check(False, "feed.xml item pubDate", "해당 slug의 <item> 없음")
    else:
        pd = re.search(r"<pubDate>(.*?)</pubDate>", item)
        ok = False
        detail = "<pubDate> 없음"
        if pd:
            try:
                parsedate_to_datetime(pd.group(1).strip())
                ok, detail = True, pd.group(1).strip()
            except (ValueError, TypeError):
                detail = f"RFC822 파싱 실패: {pd.group(1).strip()}"
        check(ok, "feed.xml item pubDate RFC822", detail)

    # 6) 읽기 시간
    mins, ko, en = reading_minutes(article)
    meta_min = re.search(r"약\s*(\d+)분", html)
    if meta_min is None:
        check(False, "읽기 시간 meta", "'약 N분' 표기 없음")
    else:
        got = int(meta_min.group(1))
        check(got == mins, "읽기 시간 meta 일치",
              f"계산 {mins}분 (한글 {ko}자, 영단어 {en}개)" if got == mins
              else f"meta {got}분 ≠ 계산 {mins}분 (한글 {ko}자, 영단어 {en}개) — meta를 {mins}분으로 수정")

    # 7) 그림 접근성
    figures = re.findall(r"<figure\b.*?</figure>", article, flags=re.S)
    no_cap = sum(1 for f in figures if "<figcaption" not in f)
    check(no_cap == 0, f"figure {len(figures)}개 모두 figcaption",
          "" if no_cap == 0 else f"{no_cap}개 figcaption 누락")
    svgs = re.findall(r"<svg\b[^>]*>", article)
    bad_svg = sum(1 for s in svgs if "aria-label" not in s or "viewBox" not in s)
    check(bad_svg == 0, f"svg {len(svgs)}개 모두 aria-label·viewBox",
          "" if bad_svg == 0 else f"{bad_svg}개 속성 누락")

    # 8) og:url
    og = re.search(r'property="og:url"\s+content="([^"]+)"', head)
    want = f"posts/{slug}.html"
    ok = bool(og) and og.group(1).endswith(want)
    check(ok, "og:url ↔ slug 일치", og.group(1) if og else "og:url 없음")

    # 9a) SVG 색은 CSS 변수만 (fill/stroke에 hex 등 리터럴 금지)
    svg_blocks = re.findall(r"<svg\b.*?</svg>", article, flags=re.S)
    bad_colors = []
    for block in svg_blocks:
        for attr, val in re.findall(r'\b(fill|stroke)="([^"]+)"', block):
            if not (val.startswith("var(") or val in ("none", "transparent", "currentColor")):
                bad_colors.append(f'{attr}="{val}"')
    check(not bad_colors, "SVG 색 CSS 변수만 사용",
          "" if not bad_colors else f"리터럴 색 {len(bad_colors)}건: {', '.join(sorted(set(bad_colors)))}")

    # 9b) 인라인 style은 overflow 스크롤 래퍼만 허용
    allowed_decls = {"overflow-x:auto", "max-width:100%"}
    bad_styles = []
    for sty in re.findall(r'style="([^"]*)"', article):
        decls = {d.strip().replace(" ", "") for d in sty.split(";") if d.strip()}
        if not decls <= allowed_decls:
            bad_styles.append(sty)
    check(not bad_styles, "인라인 style 스크롤 래퍼만",
          "" if not bad_styles else f"허용 외 인라인 style {len(bad_styles)}건: " + "; ".join(bad_styles[:3]))

    # 9c) url(#id) 참조는 같은 SVG 안에 정의 (크로스-SVG 참조 금지)
    dangling = []
    for block in svg_blocks:
        ids = set(re.findall(r'\bid="([^"]+)"', block))
        for ref in re.findall(r"url\(#([^)]+)\)", block):
            if ref not in ids:
                dangling.append(f"#{ref}")
    check(not dangling, "SVG url(#) 참조 자기완결",
          "" if not dangling else f"같은 SVG에 정의 없는 참조: {', '.join(sorted(set(dangling)))}")

    # 보고
    fails = [r for r in results if not r[0]]
    for ok, label, detail in results:
        print(f"{'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    print(f"\n읽기 시간(계산): 약 {mins}분")
    print(f"결과: {'전부 PASS' if not fails else f'FAIL {len(fails)}건 — 수정 후 재실행'}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
