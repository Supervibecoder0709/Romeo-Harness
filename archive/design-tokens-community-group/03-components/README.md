# 구성요소와 agent/skill 확인

## agent/skill 정의 파일

고정 SHA의 재귀 트리에서 `AGENTS.md`, `CLAUDE.md`, `SKILL.md`, `.claude/agents/**`, `.claude/skills/**`, `.agents/skills/**` 후보는 발견하지 못했다. 따라서 이 레포가 에이전트 또는 스킬을 실행·권한 부여하는 계약은 **확인되지 않으며**, 번역할 agent/skill 정의 파일도 없다. 이는 “정의가 없다”는 절대 주장보다, 이 SHA의 저장소 트리에서 해당 관례 경로를 찾지 못했다는 **탐색 결과**다. [E01]

## 실행 핵심 구성요소

### Root pnpm workspace

세 하위 패키지의 build, development server, lint, spellcheck, test를 묶는 실행 조정자다. 별도 런타임 서비스가 아니라 사람이 실행하거나 CI가 호출하는 command contract다. [E02][E03]

### Technical Reports / ReSpec

HTML과 Markdown 조각을 ReSpec으로 조립해 정적 명세 HTML을 만든다. Format과 Resolver는 source entry가 확인됐으며, preview 원본 자체는 표준 구현 근거가 아니라 작업 중 초안임을 명시한다. [E04][E06][E18]

### `@dtcg/schemas` bundle script

버전별 JSON Schema 조각을 `$id` 기준으로 등록하고 `$ref`를 포함한 self-contained 산출물로 번들한다. 작성 가능한 source와 배포 가능한 output을 분리하는 구성요소다. [E07][E09]

### `@dtcg/www` Astro site

정적 사이트를 build하고, schema bundle을 먼저 실행한다. Astro integration에는 sitemap, robots.txt, Pagefind, Preact, broken link checker가 포함되지만 이것들이 production에서 실제로 성공했는지는 미확인이다. [E10][E19]

### Token Playground demo resolver

브라우저에서 예제 design system JSON과 resolver JSON을 읽어 context별 결과를 보여 주는 Preact 데모다. 구현 파일 스스로 명세와 어긋날 수 있으므로 공식 명세를 우선하라는 경고를 둔다. 이 코드를 범용 production resolver로 채택해서는 안 된다. [E11][E12]

### GitHub Actions / Netlify 경계

PR CI는 코드 품질 검사, technical-reports Action은 일부 명세 source의 GitHub Pages 배포 설정, Netlify는 preview build 설정을 담당한다. 이들은 repository 밖의 권한과 상태를 바꾸는 경계이며 현재 성공 결과는 미확인이다. [E14][E17][E25]
