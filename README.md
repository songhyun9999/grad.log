# grad.log — 학습 노트 블로그 (songhyun9999.github.io/grad.log)

공부한 것을 수식·그림과 함께 정리해 쌓아두는 개인 학습 노트 블로그.
GitHub Pages가 `main` 브랜치 루트를 그대로 서빙한다 (빌드 없음, `.nojekyll`).

**발행 담당**: `blog-publisher` 에이전트 (Claude Code 생태계). 정리된 마크다운을 받아
아래 규약대로 HTML 포스트를 만들고 index를 갱신한 뒤 커밋·푸시한다.

## 구조

```
index.html            홈 — 소개 히어로 + 최근 글 5개
archive.html          전체 글 목록 (연도별 .year-head 구분)
about.html            소개 페이지
assets/style.css      공용 디자인 시스템 — 모든 페이지가 이것 하나만 사용
templates/post.html   포스트 템플릿 ({{TITLE}}, {{SLUG}} 등 플레이스홀더)
posts/<slug>.html     글 본문 (템플릿 기반, 파일명은 영문 kebab-case)
```

모든 페이지 공통: 상단 내비게이션(Home / Archive / About), 🎓 파비콘, og 메타.

## 발행 규약 (blog-publisher 계약)

1. `templates/post.html`을 복사해 `posts/<slug>.html` 생성, 플레이스홀더 치환.
   - 수식: KaTeX 구분자 `$$…$$`(display) / `\(…\)`(inline). 수식 없는 글은 head의 KaTeX 3줄 삭제.
   - 그림: 인라인 SVG 권장, 색은 CSS 변수(`var(--accent)` 등) 사용.
2. 새 `<li>` 항목을 **두 곳**의 `<!-- posts:start -->` 바로 아래에 추가 (최신 글이 위):
   - `archive.html` — 전체 목록. 해가 바뀌면 목록 위에 `.year-head` + 새 `<ol>` 블록 신설.
   - `index.html` — 최근 글. **5개 초과 시 가장 오래된 `<li>` 제거** (archive에는 유지).
3. 커스텀 스타일은 새로 만들지 말 것 — `assets/style.css`의 기존 클래스
   (`.note`, `.tbl-wrap`, `.fig-row`, `.tag`, `h2 > .no` 등)만 사용한다.
   부족하면 style.css에 클래스를 추가하고 이 README에 기록.
4. 커밋 메시지: `post: <제목>` / 디자인 변경은 `design: …`.

## 품질 규약 (긴 글 = 본문 h2가 5개 이상인 글)

**발행 전 각색**: 노트/digest를 그대로 올리지 않는다. 재료는 먼저 블로그 글로 각색
(도입부 — 왜 읽을 가치가 있는가 2~4문장, 독자 동선에 맞는 흐름, 그림 스펙 삽입)을
거친 뒤 발행한다. 각색 담당은 생태계 `writing-agent`(kind=blog), 사실·수치는 verbatim.

**디자인 시스템 v2 참고**:
- 서체: Pretendard Variable(본문) + JetBrains Mono(데이터·라벨·코드) — head의 CDN 4줄 필수(템플릿에 포함).
- 콜아웃 2종: `.note`(인사이트, accent) / `.note warn`(주의·경고, 앰버) — "주의/경고/한계" 성격이면 warn.
- 스탯 값 대비: `.stat-value` 안에서 주인공 숫자만 크게, 비교 대상은 `<span class="dim">`, 연결어는 `<span class="vs">`.
- SVG 노드 도형 의미: ● 프로세스/주체(accent 원), ▭ 파일/산출물(rect), ◆ 네트워크(diamond) — provenance류 그림에서 일관 유지.

**구성 요소** (해당하면 적용):
- **목차** — 긴 글은 lede 아래 `.toc`(섹션 앵커 링크 `<a href="#s1">`)를 둔다. h2에 `id` 부여.
- **히어로 스탯** — 글의 결정적 수치 1~3개는 표에 묻지 말고 `.stat-row > .stat`
  (`.stat-value` 숫자 / `.stat-label` 설명 / `.stat-context` 비교 맥락)로 TL;DR 근처에 노출.
- **표 강조** — 결과 표에서 승부처 셀은 `td.hl`(또는 행 전체 `tr.hl-row`)로 하이라이트.
- **접기** — 용어 사전·부록·참고문헌성 섹션은 `<details><summary>제목</summary>…</details>`로 접는다.
- **이전/다음 글** — 글 하단에 `.post-nav`(`.dir` 방향 라벨 + 링크). 발행 시 인접 글과 상호 갱신.

**그림 규약** (인라인 SVG, 색은 CSS 변수만 — `var(--accent)`/`var(--muted)`/`var(--line)`/`var(--surface)`):
- **플로우 다이어그램** — 파이프라인·아키텍처 단계 설명용. 가로 박스(rx=8, fill=var(--surface),
  stroke=var(--line)) + 화살표(stroke=var(--muted), marker). 강조 단계만 stroke=var(--accent).
  라벨은 SVG `<text>`(fill=var(--ink), font-style 지정해 이탤릭 방지). `.fig-row`로 감싸고 `<figcaption>` 필수.
- **개념 그림** — 도메인 구조(그래프·시스템 관계) 설명용. 노드 원/사각 + 엣지 선, 스타일은 위와 동일.
- **수치 차트 주의** — 자릿수가 다른 극단 격차는 차트가 아니라 히어로 스탯으로(로그축 막대 금지).
  다계열 색상 구분 차트 금지(단일 강조색 + 무채색 대비만), 모든 마크에 직접 라벨(색만으로 정보 전달 금지).
- 모든 `<figure>`에 `<figcaption>`과 `<svg role="img" aria-label="…">` 필수. viewBox 사용(반응형).
