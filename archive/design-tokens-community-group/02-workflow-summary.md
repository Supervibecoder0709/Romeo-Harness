# 워크플로 요약

## 1. 디자인 토큰 기술 보고서 제작·공개

**무엇을 하는가**: 도구 간 디자인 토큰 교환 형식과 context별 resolver를 ReSpec으로 웹 명세로 만든다. Format의 원본은 교환용 파일 형식을 설명하며, Resolver는 light/dark 같은 여러 context의 토큰 조합을 다룬다. 다만 현재 원본은 `CG-DRAFT`이며 “preview draft를 구현하지 말라”고 명시한다. [E04][E05]

**입력**: `technical-reports/{index,format,color,resolver}/`의 HTML과 Markdown 원본이다. `format/index.html`과 `resolver/index.html`은 각 장을 `data-include`로 조립한다. [E04][E06]

**처리 단계**: 루트 `pnpm run build`는 먼저 `@dtcg/tr`의 build를 실행한다. 이 패키지는 ReSpec을 네 report HTML에 실행하고 결과를 `www/src/pages/TR/drafts/**`에 쓴다. 이어 `@dtcg/www`의 build가 schema build 후 Astro 정적 build를 수행한다. [E02][E18][E19]

**출력/상태**: 로컬 개발에서는 `/TR/drafts/`를 미리 볼 수 있고, 문서상 `main` 병합 후 기술 보고서는 GitHub Pages의 `gh-pages`에서 제공된다. [E15][E20]

**실패·재시도**: `technical-reports` 패키지에는 `validate:*` ReSpec 명령이 있지만, 확인한 PR CI는 이를 호출하지 않는다. 빌드 또는 검증 실패 시 CI의 자동 재시도 정책은 설정 파일에서 확인되지 않았고, 사람이 수정 후 새 실행을 시작해야 하는 것으로 보인다. 후자는 **추론**이며 실제 Actions 정책은 미확인이다. [E18][E17]

**관찰 증거**: 재현 가능한 완료 증거는 ReSpec build/validate 로그, `www/src/pages/TR/drafts/**` 생성물, `gh-pages`의 대상 파일 및 실제 URL readback이다. 이 아카이브에서는 어떤 것도 실행·readback하지 않았으므로 **미검증**이다.

## 2. 버전 고정 JSON Schema 번들링

**무엇을 하는가**: 사람이 편집하기 쉬운 분할 DTCG JSON Schema를 도구가 배포하기 쉬운 단일 self-contained schema로 만든다. 현재 config에는 `2025.10`의 Format과 Resolver 두 entry가 있다. [E07][E08]

**입력**: `schemas/src/<version>/**.json`, `schemas/schemas.config.json`이다. Resolver schema는 `version: "2025.10"` 및 `resolutionOrder`를 필수로 하고, Format schema는 `$type`, `$extensions`, `$extends`, `$root`와 중첩 토큰/그룹 패턴을 표현한다. [E08][E21][E22]

**처리 단계**: `tsx scripts/bundle.ts`가 모든 JSON을 재귀 수집하고 `$id`가 있는 schema를 Hyperjump registry에 등록한다. config의 각 entry를 bundle하며 `$ref`가 포함된 출력 JSON을 Prettier로 정리해 쓴다. [E09][E19]

**출력/상태**: 각 entry 결과는 `schemas/dist/<version>/`과 `www/public/schemas/<version>/` 양쪽에 기록된다. 이 작업은 파일 시스템 상태를 바꾸며, 사이트 빌드가 이 작업을 선행 호출한다. [E07][E09][E19]

**실패·재시도**: source JSON 파싱, `$id` 등록, 참조 bundle, 파일 쓰기 중 하나가 실패하면 `main().catch`가 오류를 출력하고 exit code 1로 끝낸다. 자동 재시도는 코드에 없다. 수정 후 같은 build를 재실행할 수 있다. [E09]

**관찰 증거**: build 콘솔의 `Registered`, `Written`, `Done!` 메시지와 두 출력 위치의 버전별 JSON을 함께 확인해야 한다. 이 아카이브는 코드만 읽었으므로 실행 결과는 **미검증**이다. [E09]

## 3. designtokens.org와 브라우저 Playground

**무엇을 하는가**: Astro 정적 사이트로 기술 보고서·기여·학습 콘텐츠를 제공하고, Playground에서 token set과 resolver context가 어떻게 합쳐지는지 보인다. [E10][E11]

**입력**: 사이트 source/콘텐츠와 Playground의 Figma SDS 또는 GitHub Primer preset JSON, 사용자가 편집한 현재 JSON, modifier 선택값이다. [E11][E12]

**처리 단계**: `/playground` 페이지가 Preact client-only 컴포넌트를 붙인다. preset은 lazy import되고, 코드가 `*.resolver.json`과 token file을 분리한다. 편집 시 JSON parse → resolver schema 검증 → `apply(input)`을 실행하고, source set/modifier context를 순서대로 merge한다. [E11][E12]

**출력/상태**: 정상 입력은 기본 context와 선택 context의 resolved tokens를 읽기 전용 diff로 표시한다. 오류는 현재 파일별 화면 상태에 기록되어 표시한다. 확인한 코드에는 서버 요청·계정·저장소 저장·외부 API 호출이 없으므로, 이 Playground의 상태는 **브라우저 메모리 상태로 한정된 것으로 확인된다**. [E11][E12][E13]

**실패·재시도**: resolver 파일 없음, 지원하지 않는 version, 비어 있는 token map, 없는 source, 잘못된 default/context, 타입 불일치 merge는 오류를 낸다. 사용자가 JSON 또는 선택값을 고치면 다음 입력에서 다시 계산한다. [E11][E12][E13]

**관찰 증거**: 브라우저에서 입력별 error text 또는 diff 결과, `pnpm run test`의 Vitest 결과가 관찰 증거다. 현재 test는 `prettyJSON` snapshot/JSON parse 및 social Discord link를 확인할 뿐, full resolver 또는 배포 동작은 보장하지 않는다. [E23][E24][E17]

## 4. PR 검사와 발행 경계

PR CI는 lint, spellcheck, test 세 job을 실행한다. `technical-reports/**`가 `main`에 push되거나 수동 실행될 때는 W3C `spec-prod` Action이 matrix의 `index`, `format`, `color` 세 source를 `gh-pages` 대상으로 빌드·배포하도록 설정돼 있다. Netlify 설정은 preview build 명령과 `www/dist` publish directory를 선언한다. [E17][E14][E25]

중요한 경계는 **PR CI 통과 ≠ 공개 사이트/모든 보고서 배포 확인**이라는 점이다. Resolver는 기술 보고서 원본과 schema에는 존재하지만 확인한 Pages Action matrix에 없고, Netlify의 실제 연결·권한·최근 성공은 저장소 파일만으로 확인할 수 없다. [E06][E08][E14][E25]
