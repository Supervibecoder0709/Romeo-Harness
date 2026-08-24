# PM Harness 운영 메모

## 결론

이 레포를 Harness에서 다룰 때의 추천 실행 단위는 **“명세 원본 + 해당 version의 schema + 정적 사이트 출력”을 하나의 변경 묶음으로 검증하는 방식**이다. 특히 `2025.10`처럼 외부 도구가 준수 버전으로 읽을 값을 바꾸면, 문서만·schema만·사이트만 통과했다는 단일 증거로 공개를 판단하면 안 된다. root build가 technical reports와 site를 연결하고, site build가 schema bundle을 선행하기 때문이다. [E02][E07][E19]

## 확인된 사실

- **입력 계약**: schema에는 version, `$id`, entry schema, `$ref`가 함께 있으며 Resolver는 `version: "2025.10"`과 `resolutionOrder`를 요구한다. 새 schema version은 source directory, 모든 `$id`, version `const`, config entry를 같이 바꾸라는 기여 안내가 있다. [E08][E21][E27]
- **모델/에이전트 역할**: repository 내부 agent/skill 정의는 찾지 못했다. 따라서 별도 에이전트가 명세 편집·배포를 승인한다는 자동화 계약은 확인되지 않는다. [E01]
- **사람 승인 지점**: 기여 문서는 실질적 기여에 Community Group 가입을 요구하고, 보고서 발행은 “spec editor만” 수행하라고 명시한다. `gh-pages` 또는 Netlify처럼 외부 공개 상태를 바꾸는 실행 전에는 이 역할·대상 version·출력 URL을 사람이 승인해야 한다. [E16][E14][E25]
- **재실행 단위**: schema bundler는 config 전체 version entries를 순서대로 다시 번들하고, root build는 보고서 후 사이트를 다시 build한다. 깨진 source를 수정한 후 동일 명령을 재실행할 수 있다. [E09][E02]
- **현재 자동 검사**: PR CI는 lint, spellcheck, test만 실행한다. Vitest에서 확인한 테스트도 `prettyJSON` snapshot/parse와 social menu의 Discord link다. [E17][E23][E24]

## 권장 Harness gate

아래는 저장소가 이미 구현한 기능이 아니라, 확인된 경계 위에 얹는 **추천 운영 설계**다.

| Gate | 사람/자동화 역할 | 통과 증거 | 실패 시 복구 |
| --- | --- | --- | --- |
| 1. 변경 분류 | 사람이 “문서만 / schema 포함 / 공개 발행”을 분류 | 변경 파일 목록, 대상 버전 | 잘못 분류하면 작업을 중단하고 범위를 다시 분류 |
| 2. source 계약 검토 | 자동화가 `$id`, config entry, ReSpec source include를 검사; 사람이 결과 해석 | source diff와 version 일치 표 | source만 되돌리고 다시 검사; 생성물에 직접 패치하지 않음 |
| 3. build·검증 | 격리된 runner가 `pnpm run build`와 명세 `validate`를 각각 실행 | exit code, ReSpec/Schema 로그, output file 목록 | 의존성 또는 원본 오류를 수정한 새 실행에서 재시도 |
| 4. 게시 전 승인 | spec editor 또는 승인자가 version·대상 URL·공개 영향 확인 | 승인 기록, deploy target | 승인 없이는 `gh-pages`/Netlify writer를 호출하지 않음 |
| 5. 게시 후 readback | 자동화가 public URL, versioned schema URL, Action 결과를 읽기 전용으로 확인 | Action run URL/status, HTTP/내용 readback | 실패 시 공개 결과를 완료로 표시하지 않고 이전 안정 버전 유지 여부를 사람에게 확인 |

## 특히 주의할 운영 판단

1. **Preview와 stable을 혼동하지 말 것**: Format/Resolver 원본은 `isPreview: true`, `CG-DRAFT`이며 직접 구현 금지 경고가 있다. README에 `2025.10 Stable` 표가 있어도, 어떤 URL과 어떤 source가 release 산출물인지 공개 전 readback으로 판별해야 한다. [E04][E06][E28]
2. **Playground를 표준 준수 엔진으로 판매하지 말 것**: 구현 스스로 데모이며 명세와 동기화되지 않을 수 있다고 경고한다. PM은 playground의 화면 diff를 학습/탐색 증거로만 쓰고, 제품 resolver 적합성은 schema와 독립 conformance test로 판단해야 한다. [E12]
3. **CI의 녹색 상태를 배포 증거로 쓰지 말 것**: PR CI에는 build/validate가 없고, 기술 보고서 Pages action의 matrix는 Resolver를 열거하지 않는다. 공개 대상이 Resolver까지 포함하면 deploy action·`gh-pages` 결과·실제 URL까지 확인해야 한다. [E17][E14]
4. **문서의 파괴적 안내를 자동 실행하지 말 것**: 기여 문서의 `git clean -dfx`는 추적되지 않는 파일을 지운다고 경고한다. Harness는 이 명령을 자동 repair 단계로 포함하지 않고, 필요하면 대상 경로·백업·명시 승인 후 격리된 작업공간에서만 실행해야 한다. [E16]

## 확장 가능 지점

- PR CI에 `pnpm run build`와 `technical-reports`의 `validate`를 별도 읽기 전용 quality gate로 추가할 수 있다. 이는 **추천**이며 현재 설정에는 없다. [E17][E18]
- version release에 대해 “schema의 `$id` / ReSpec release metadata / `www/src/pages/TR/<version>` / 공개 URL”을 하나의 checklist artifact로 연결할 수 있다. 이는 **추천**이며 이 아카이브는 release automation의 존재를 확인하지 못했다.
- Resolver Pages 발행 필요성을 제품/표준 오너가 결정해야 한다. 필요하다면 workflow matrix에 포함하고, 변경 후 실제 `gh-pages`와 target URL을 readback하는 release gate가 필요하다. 이는 확인된 matrix 공백에 대한 **추천**이다. [E14]

## 미확인

Actions와 Netlify의 실제 권한·성공·rollback 방법, production host의 cache/atomic deploy, W3C spec-prod의 세부 동작은 읽은 저장소 파일만으로 확인하지 못했다. 따라서 위 gate의 게시 후 단계가 완료되기 전에는 “공개 완료”라고 부르지 않는다.
