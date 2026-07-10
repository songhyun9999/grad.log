# study notes — songhyun9999.github.io

공부한 것을 수식·그림과 함께 정리해 쌓아두는 개인 학습 노트 블로그.
GitHub Pages가 `main` 브랜치 루트를 그대로 서빙한다 (빌드 없음, `.nojekyll`).

**발행 담당**: `blog-publisher` 에이전트 (Claude Code 생태계). 정리된 마크다운을 받아
아래 규약대로 HTML 포스트를 만들고 index를 갱신한 뒤 커밋·푸시한다.

## 구조

```
index.html            글 목록 (홈)
assets/style.css      공용 디자인 시스템 — 모든 페이지가 이것 하나만 사용
templates/post.html   포스트 템플릿 ({{TITLE}} 등 플레이스홀더)
posts/<slug>.html     글 본문 (템플릿 기반, 파일명은 영문 kebab-case)
```

## 발행 규약 (blog-publisher 계약)

1. `templates/post.html`을 복사해 `posts/<slug>.html` 생성, 플레이스홀더 치환.
   - 수식: KaTeX 구분자 `$$…$$`(display) / `\(…\)`(inline). 수식 없는 글은 head의 KaTeX 3줄 삭제.
   - 그림: 인라인 SVG 권장, 색은 CSS 변수(`var(--accent)` 등) 사용.
2. `index.html`의 `<!-- posts:start -->` 바로 아래에 새 `<li>` 항목 추가 (최신 글이 위).
3. 커스텀 스타일은 새로 만들지 말 것 — `assets/style.css`의 기존 클래스
   (`.note`, `.tbl-wrap`, `.fig-row`, `.tag`, `h2 > .no` 등)만 사용한다.
   부족하면 style.css에 클래스를 추가하고 이 README에 기록.
4. 커밋 메시지: `post: <제목>` / 디자인 변경은 `design: …`.
