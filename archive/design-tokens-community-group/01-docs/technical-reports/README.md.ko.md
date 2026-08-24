# DTCG 기술 보고서

이 디렉터리에는 [Design Token Community Group(DTCG)의 기술 보고서](https://www.designtokens.org/TR/drafts/) 소스 코드가 있습니다.

<!-- TOC depthfrom:2 -->

- [로컬 미리보기](#local-previews)
- [편집](#editing)
- [배포](#deployments)

<!-- /TOC -->

## 로컬 미리보기

기술 보고서의 로컬 편집 내용을 실시간으로 미리 보려면 (저장소 루트에서) 다음을 실행하세요.

```
pnpm run dev
```

<http://localhost:8080/TR/drafts/>를 여세요.

## 편집

기술 보고서 생성에는 [W3C의 ReSpec 도구](https://respec.org/docs/)를 사용합니다. 단순 편집에는 HTML과 Markdown 지식으로 충분하지만, 작성자는 ReSpec 기능을 익히는 것을 권장합니다.

Format 명세 편집을 더 편리하게 하고 merge conflict 가능성을 줄이기 위해, 주요 장을 별도의 Markdown 파일로 나누었습니다. 그러면 `format/index.html`이 [ReSpec의 `data-include` 기능](https://respec.org/docs/#data-include)으로 모두 포함합니다.

예:

```html
<section
  data-include="./file-format.md"
  data-include-format="markdown"
></section>
```

## 배포

이 디렉터리의 source 파일 변경이 `main`에 merge되면 [`technical-reports` GitHub Action](../.github/workflows/technical-reports.yml)을 통해 [`https://www.designtokens.org/TR/drafts/`](https://www.designtokens.org/TR/drafts/)에 자동 배포됩니다. GitHub Pages에서 호스팅되며 build 출력은 [`gh-pages` 브랜치](https://github.com/design-tokens/community-group/tree/gh-pages)에서 찾을 수 있습니다.

또한 PR의 preview 배포 생성에는 Netlify를 사용합니다. 준비가 되면 Netlify가 preview URL이 포함된 댓글을 PR에 게시합니다.
