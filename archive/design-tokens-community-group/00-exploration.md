# 탐색 기록

## 범위와 소스 고정

분석 대상은 `design-tokens/community-group`의 기본 브랜치 `main`이며, GitHub API로 확정한 커밋은 `16c902d9327c18290e956a21130c445f1b88c40f`다. 재귀 파일 트리로 후보를 선별한 뒤, 안내 문서·패키지 매니페스트·워크플로·스키마 번들러·Playground 핵심 코드·테스트만 raw API로 읽었다. 접근·미확인 경계는 [_source.md](_source.md)에 기록했다.

## 선정 파일과 선정 이유

| 범주 | 연 파일 | 선정 이유 |
| --- | --- | --- |
| 목적·거버넌스 | `README.md`, `CHARTER.md`, `CONTRIBUTING.md` | 레포의 공식 목적, 기여 자격과 보고서 발행 권한을 확인하기 위해 |
| 모노레포 실행 계약 | `package.json`, `pnpm-workspace.yaml` | 루트의 build/dev/test가 어느 패키지를 호출하는지 확인하기 위해 |
| 명세 생성·발행 | `technical-reports/package.json`, `README.md`, `format/index.html`, `format/file-format.md`, `resolver/index.html`, `resolver/introduction.md`, `.github/workflows/technical-reports.yml` | ReSpec 원본, 생성 진입점, 공개 발행 경계를 교차 확인하기 위해 |
| 스키마 | `schemas/package.json`, `schemas.config.json`, `scripts/bundle.ts`, 두 README/CONTRIBUTING, `src/2025.10/{format,resolver}.json` | 사람이 유지하는 분할 스키마가 어떤 산출물로 가는지 확인하기 위해 |
| 사이트·데모 | `www/package.json`, `README.md`, `astro.config.mjs`, `content.config.ts`, `pages/playground.astro`, TokenPlayground 및 resolver 코드 | 웹사이트의 실제 프레임워크, Playground의 입력·오류·상태 경계를 확인하기 위해 |
| 검증·미리보기 | `.github/workflows/pr.yml`, `netlify.toml`, `utils.test.ts`, `site.config.test.ts` | 자동 검증의 범위와 배포 전 관찰 가능한 증거를 구분하기 위해 |

## 확인된 기술 스택과 실제 진입점

- **pnpm 워크스페이스**: `schemas`, `technical-reports`, `www` 세 패키지를 묶는다. 루트 `build`는 기술 보고서를 먼저 빌드하고 사이트를 빌드하며, 루트 `dev`도 보고서 빌드 후 각 패키지의 `dev`를 병렬 실행한다. [E02][E03]
- **기술 보고서**: ReSpec이 `technical-reports`의 HTML/Markdown 원본을 `www/src/pages/TR/drafts/**`에 HTML로 생성한다. Format과 Resolver 원본 모두 상태를 `CG-DRAFT`·preview로 선언하고, 미리보기 초안은 직접 인용하거나 구현하지 말라고 적는다. [E04][E05][E06]
- **JSON Schema**: TypeScript 번들러가 `schemas.config.json`의 entry schema와 버전을 읽고, 모든 분할 JSON schema의 `$id`를 Hyperjump에 등록한 뒤 참조를 포함한 단일 JSON을 `schemas/dist`와 `www/public/schemas`에 쓴다. [E07][E08][E09]
- **웹사이트와 Playground**: `www`는 Astro + Preact 정적 사이트이며, `/playground`는 Preact 전용 클라이언트 컴포넌트를 마운트한다. Playground는 예제 JSON을 브라우저 메모리에 불러와 resolver 파일과 token 파일을 분리하고, 입력마다 유효성 검증·해결을 시도해 오류 또는 읽기 전용 diff를 보여 준다. [E10][E11][E12][E13]

## 확인된 핵심 흐름

1. 명세 편집자는 `technical-reports` 원본을 변경한다. root build가 ReSpec 결과를 draft 페이지에 만들고, Astro build가 사이트 결과물을 만든다. `main`에서 `technical-reports/**` 변경은 별도 Action의 세 원본(`index`, `format`, `color`)만 `gh-pages` 대상으로 전달한다. [E02][E04][E14]
2. 스키마 편집자는 버전별 분할 JSON·`$id`·config를 함께 변경한다. bundle script가 모든 JSON을 등록하고 config의 각 entry를 자체 포함 파일로 만든 뒤 두 출력 위치로 쓴다. [E07][E08][E09]
3. 일반 사이트 사용자는 Playground에서 preset을 고르고 JSON을 수정한다. client code가 `*.resolver.json` 존재, resolver의 버전·필수 필드, source 참조, merge 가능한 타입을 검사한다. 통과한 경우 현재 선택 context와 기본 context의 결과 diff를 계산한다. [E11][E12][E13]

## 문서·구현 교차 확인에서 발견한 주의점

- `technical-reports/README.md`는 `main`에 병합된 이 디렉터리의 source 파일 변경이 자동 배포된다고 설명하지만, 확인한 Action matrix에는 `resolver/index.html`이 없다. 따라서 Resolver의 `gh-pages` 자동 갱신은 이 워크플로만으로는 확인되지 않는다. 이는 문서 일반화와 실제 설정의 **근거 불일치/미확인**이다. [E14][E15]
- `CONTRIBUTING.md`의 보고서 버전 갱신 안내는 `technical-reports/TR/index.html`을 가리키지만, 고정 SHA의 재귀 트리에 그 경로는 없고 현재 진입점은 `technical-reports/index.html`, `format/index.html` 등이다. 또한 프로젝트 구조 표는 `schemas/`를 열거하지 않는다. 이 안내를 그대로 실행하기 전에 현재 경로를 재확인해야 한다. [E01][E16]
- PR CI는 lint·spellcheck·test만 실행한다. `build`, ReSpec `validate`, 정적 링크 검사, schema bundle 성공은 PR CI 설정에서 확인되지 않았으므로, PR 통과를 전체 공개 산출물 검증으로 해석하면 안 된다. [E17][E18]

## 미확인 범위

소스·설정 읽기로 확인할 수 없는 실제 배포 성공, 외부 서비스 권한과 게시 결과, 숨은 branch protection, 세부 명세의 전체 적합성은 미확인이다. 장문 사양·생성 HTML·예제 데이터의 전체 검토도 의도적으로 제외했다.
