# 구성요소 표

| 구성요소 | 종류 | 역할 | 입력 | 출력/상태변화 | 권한·외부 경계 | 원문 위치 | 근거 상태 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DTCG 거버넌스 | 문서/프로세스 | 명세 목적, W3C CLA 기여 자격, 공개 합의 절차를 정한다 | 참여자 기여·PR/Issue | 합의·기여 기록(외부 GitHub/W3C) | W3C CLA, GitHub, Discord | `CHARTER.md`, `CONTRIBUTING.md` | 확인됨 [E26][E16] |
| Root workspace | 실행 계약 | 세 package의 공통 build/dev/lint/test를 조정한다 | `pnpm` 명령 | 하위 package command 실행 | 로컬 Node/pnpm 파일 시스템 | `package.json`, `pnpm-workspace.yaml` | 확인됨 [E02][E03] |
| Technical Reports | 명세 source/빌드 | ReSpec으로 Format·Color·Resolver 보고서를 생성한다 | HTML, Markdown | `www/src/pages/TR/drafts/**` 생성 | ReSpec CLI, 로컬 파일 시스템 | `technical-reports/package.json`, `format/index.html`, `resolver/index.html` | 확인됨 [E18][E04][E06] |
| Format Module | 명세 source | 도구 간 토큰 교환 파일 형식을 설명한다 | Format HTML/Markdown | ReSpec document | 공개 명세 URL | `technical-reports/format/**` | 확인됨; preview 구현 금지 경고 [E04][E05] |
| Resolver Module | 명세 source | 여러 context에서 token을 다루는 방법을 설명한다 | Resolver HTML/Markdown | ReSpec document | 공개 명세 URL | `technical-reports/resolver/**` | 확인됨; Pages 자동 게시 여부 미확인 [E06][E15] |
| `@dtcg/schemas` | 스키마 package | 분할 schema를 version별 self-contained schema로 만든다 | config, JSON Schema, `$id`, `$ref` | `dist/**`, `www/public/schemas/**` 파일 쓰기 | Hyperjump, Node 파일 시스템 | `schemas/package.json`, `schemas.config.json`, `scripts/bundle.ts` | 확인됨; 실행 결과 미검증 [E19][E08][E09] |
| `@dtcg/www` | Astro website | designtokens.org 정적 사이트와 Playground route를 build한다 | Astro content/components, bundled schemas | `www/dist` 정적 build | Astro/Vite 및 배포 호스트 | `www/package.json`, `astro.config.mjs` | 확인됨; 실배포 미확인 [E10][E19] |
| Token Playground | Preact client component | JSON token/resolver를 해석하고 context diff를 보여 준다 | preset JSON, 편집 JSON, modifier 값 | 브라우저 메모리 error/files/input과 read-only diff | 브라우저 Monaco; 확인한 코드상 서버/저장소 없음 | `pages/playground.astro`, `TokenPlayground/**` | 확인됨; demo 구현 [E11][E12][E13] |
| PR CI | GitHub Action | lint, 맞춤법, test를 PR마다 검사한다 | PR checkout, pnpm deps | Actions job status | GitHub Actions runner | `.github/workflows/pr.yml` | 확인됨; build/validate 미포함 [E17] |
| Technical reports deploy | GitHub Action | main의 일부 보고서를 `gh-pages` 대상으로 ReSpec build/deploy한다 | main push `technical-reports/**` 또는 수동 실행 | GitHub Pages branch 변경 가능성 | W3C `spec-prod`, GitHub Pages | `.github/workflows/technical-reports.yml` | 설정 확인됨; 실행·권한·Resolver 포함 미확인 [E14] |
| Netlify preview | 호스팅 설정 | preview용 build 및 publish directory를 선언한다 | build command | `www/dist` deploy candidate | Netlify 계정/권한 | `netlify.toml` | 설정 확인됨; 연결·실행 결과 미확인 [E25] |

`agent`와 `skill`은 이 SHA의 관례 경로에서 정의 파일을 찾지 못했으므로 표의 실행 구성요소로 추가하지 않았다. [E01]
