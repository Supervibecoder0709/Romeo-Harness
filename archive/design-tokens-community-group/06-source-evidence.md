# 소스 근거

분석 기준 커밋은 `16c902d9327c18290e956a21130c445f1b88c40f`다. 아래 ID는 다른 문서의 `[E##]` 표기와 연결된다. `E01`은 GitHub 재귀 트리 API의 경로 목록 근거이므로 줄 범위가 없다.

| ID | 원문 URL (고정 SHA) | 파일·줄 범위 | 뒷받침하는 사실 |
| --- | --- | --- | --- |
| E01 | https://api.github.com/repos/design-tokens/community-group/git/trees/16c902d9327c18290e956a21130c445f1b88c40f?recursive=1 | 재귀 tree 전체 | 대상 SHA의 파일 인벤토리, agent/skill 관례 경로 부재, `technical-reports/TR/` 부재를 확인한 기준 |
| E02 | https://github.com/design-tokens/community-group/blob/16c902d9327c18290e956a21130c445f1b88c40f/package.json | L12-L24 | pnpm version과 root build/dev/lint/spellcheck/test script 계약 |
| E03 | https://github.com/design-tokens/community-group/blob/16c902d9327c18290e956a21130c445f1b88c40f/pnpm-workspace.yaml | L1-L7 | workspace package는 schemas, technical-reports, www |
| E04 | https://github.com/design-tokens/community-group/blob/16c902d9327c18290e956a21130c445f1b88c40f/technical-reports/format/index.html | L6-L19, L71-L92, L160-L193 | Format 2025.10 preview 설정, 목적, ReSpec include 구조 |
| E05 | https://github.com/design-tokens/community-group/blob/16c902d9327c18290e956a21130c445f1b88c40f/technical-reports/format/file-format.md | L1-L32 | JSON 교환 형식, MIME type, 확장자 권고 |
| E06 | https://github.com/design-tokens/community-group/blob/16c902d9327c18290e956a21130c445f1b88c40f/technical-reports/resolver/index.html | L6-L19, L52-L75, L77-L125 | Resolver preview 설정·목적·ReSpec include 구조 |
| E07 | https://github.com/design-tokens/community-group/blob/16c902d9327c18290e956a21130c445f1b88c40f/schemas/README.md | L3-L20, L45-L49 | schema의 분할 source, self-contained bundle, 두 출력 위치 |
| E08 | https://github.com/design-tokens/community-group/blob/16c902d9327c18290e956a21130c445f1b88c40f/schemas/schemas.config.json | L1-L20 | 2025.10 Format/Resolver entry와 source/output directory |
| E09 | https://github.com/design-tokens/community-group/blob/16c902d9327c18290e956a21130c445f1b88c40f/schemas/scripts/bundle.ts | L1-L20, L47-L113, L115-L137 | recursive collect, `$id` 등록, bundle/format/write, 오류 exit 1 |
| E10 | https://github.com/design-tokens/community-group/blob/16c902d9327c18290e956a21130c445f1b88c40f/www/package.json | L12-L39 | www dev/build/test와 Astro/Preact/Vitest 의존성 |
| E11 | https://github.com/design-tokens/community-group/blob/16c902d9327c18290e956a21130c445f1b88c40f/www/src/pages/playground.astro | L1-L7 | Preact client-only Playground route |
| E12 | https://github.com/design-tokens/community-group/blob/16c902d9327c18290e956a21130c445f1b88c40f/www/src/components/TokenPlayground/index.tsx | L13-L23, L34-L116, L139-L167, L185-L206 | preset load, browser state, edit/error flow, resolver file 분리 |
| E13 | https://github.com/design-tokens/community-group/blob/16c902d9327c18290e956a21130c445f1b88c40f/www/src/components/TokenPlayground/lib/create-resolver.ts | L1-L5, L16-L39, L57-L124 | demo 경고, resolver validation, source/context resolution 오류 |
| E14 | https://github.com/design-tokens/community-group/blob/16c902d9327c18290e956a21130c445f1b88c40f/.github/workflows/technical-reports.yml | L1-L30 | main/path trigger, index/format/color matrix, `gh-pages` target |
| E15 | https://github.com/design-tokens/community-group/blob/16c902d9327c18290e956a21130c445f1b88c40f/technical-reports/README.md | L13-L42 | root local preview, ReSpec, all-source auto-deploy 설명과 Netlify preview 설명 |
| E16 | https://github.com/design-tokens/community-group/blob/16c902d9327c18290e956a21130c445f1b88c40f/CONTRIBUTING.md | L1-L5, L27-L31, L33-L108 | CLA/기여, 로컬 명령, structure 표, spec editor만의 publish 절차와 destructive command 경고 |
| E17 | https://github.com/design-tokens/community-group/blob/16c902d9327c18290e956a21130c445f1b88c40f/.github/workflows/pr.yml | L1-L47 | PR CI가 lint/spellcheck/test만 실행 |
| E18 | https://github.com/design-tokens/community-group/blob/16c902d9327c18290e956a21130c445f1b88c40f/technical-reports/package.json | L1-L36 | ReSpec build/dev/validate script와 output path |
| E19 | https://github.com/design-tokens/community-group/blob/16c902d9327c18290e956a21130c445f1b88c40f/schemas/package.json | L1-L24 | schemas build, lint/typecheck 실행 계약 |
| E20 | https://github.com/design-tokens/community-group/blob/16c902d9327c18290e956a21130c445f1b88c40f/www/README.md | L1-L22 | website 로컬 실행과 main 자동 deploy 주장 |
| E21 | https://github.com/design-tokens/community-group/blob/16c902d9327c18290e956a21130c445f1b88c40f/schemas/src/2025.10/resolver.json | L1-L60 | Resolver 2025.10 version, required fields, sets/modifiers/resolutionOrder |
| E22 | https://github.com/design-tokens/community-group/blob/16c902d9327c18290e956a21130c445f1b88c40f/schemas/src/2025.10/format.json | L1-L104 | Format JSON Schema의 metadata, group, references 제약 |
| E23 | https://github.com/design-tokens/community-group/blob/16c902d9327c18290e956a21130c445f1b88c40f/www/src/components/TokenPlayground/lib/utils.test.ts | L1-L23 | prettyJSON snapshot 및 JSON parse 테스트 범위 |
| E24 | https://github.com/design-tokens/community-group/blob/16c902d9327c18290e956a21130c445f1b88c40f/www/src/site.config.test.ts | L1-L13 | social Discord link 테스트 범위 |
| E25 | https://github.com/design-tokens/community-group/blob/16c902d9327c18290e956a21130c445f1b88c40f/netlify.toml | L1-L17 | Netlify preview build/publish 설정 |
| E26 | https://github.com/design-tokens/community-group/blob/16c902d9327c18290e956a21130c445f1b88c40f/CHARTER.md | L1-L44, L82-L126 | DTCG scope, deliverables, CLA와 기여·공개 합의의 거버넌스 |
| E27 | https://github.com/design-tokens/community-group/blob/16c902d9327c18290e956a21130c445f1b88c40f/schemas/CONTRIBUTING.md | L1-L83 | 새 version에 필요한 source, `$id`, `const`, config, build의 연계 |
| E28 | https://github.com/design-tokens/community-group/blob/16c902d9327c18290e956a21130c445f1b88c40f/README.md | L1-L21, L94-L106 | 레포 목적, published version 표, version number 준수 표기 |

## 근거 한계

- URL은 원문 고정 SHA를 가리키지만, 이 아카이브는 GitHub API read-only 응답을 바탕으로 작성됐다. URL의 렌더링·Actions 실행 이력·외부 공개 URL은 별도로 확인하지 않았다.
- `E01`의 “부재” 근거는 해당 SHA의 재귀 트리 목록에서 경로를 찾지 못했다는 뜻이다. GitHub 외부 시스템이나 future commit의 부재를 뜻하지 않는다.
