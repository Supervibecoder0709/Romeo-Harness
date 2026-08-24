# 구성요소 표

근거 상태의 **확인됨**은 고정 SHA 원문을 실제로 연 결과다. **추론**은 그 파일들의 연결 관계를 설명한 것이며, **미확인**은 실행 결과가 아니다.

| 구성요소 | 종류 | 역할 | 입력 | 출력/상태 변화 | 권한·외부 경계 | 원문 위치 | 근거 상태 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `impeccable` | user skill | frontend UI 디자인·검토·정제 요청을 23 sub-command로 route | chat command, target, project context | design 작업 지시, context 활용 | Bash로 bundled script/CLI 실행 허용 | `skill/SKILL.src.md:1-85` | 확인됨 [E7] |
| `init`/`document` | skill command | durable product/design context를 만들거나 기존 code에서 DESIGN.md를 문서화 | surface·project source·user answers | `PRODUCT.md`, `DESIGN.md` 및 sidecar | 프로젝트 파일 시스템 | `skill/SKILL.src.md:48-49,77`; `skill/agents/impeccable-documenter.md:21-33` | 확인됨 [E7] [E8] |
| CLI `impeccable` | Node binary | install/link/update/check, detect, ignores 라우팅 | argv | exit code, terminal output, 설치 작업 위임 | 설치 대상 harness 폴더; URL detect는 선택적 browser | `package.json:26-75`; `cli/bin/cli.js:1-102` | 확인됨 [E2] |
| detector | CLI engine | UI anti-pattern/quality 검출 | file/dir/URL, config/ignore | findings/JSON | optional Puppeteer, detector config | `cli/bin/cli.js:62-79`; `skill/scripts/detect.mjs:1-21` | 확인됨 [E2] [E11] |
| design hook | hook adapter | 편집 직후와 Stop 시 detector 결과를 agent에 전달 | stdin hook event, touched files | additional context, optional audit log | provider hook runtime, local files | `skill/scripts/hook.mjs:1-78`; `README.md:347-362` | 확인됨 [E1] [E10] |
| live coordinator | live CLI | live iteration 전 target/context/config을 gate하고 helper server/injection/poll 준비 | cwd/`--target`, config, PRODUCT/DESIGN | success/error JSON, roots manifest, injected page | local dev app, background helper server, browser script | `skill/scripts/live.mjs:1-210,338-365` | 확인됨 [E9] |
| live state paths | filesystem helper | live config/server/session/annotation 위치와 session-id 안전성 정의 | cwd, env, ID | `.impeccable/live/*` paths; stale pid cleanup | project file system/process liveness | `skill/scripts/lib/impeccable-paths.mjs:7-137` | 확인됨 [E11] |
| asset producer | subagent | 승인된 mock에서 재사용 가능한 raster asset 생산, 재디자인 금지 | mock/crop/output/dimensions/avoid list | asset manifest, output files, embedded prompt | image tool, project asset files | `skill/agents/impeccable-asset-producer.md:1-102` | 확인됨 [E8] |
| documenter | subagent | 실제 shipped artifact에서 DESIGN.md/sidecar 기록 | artifact, direction contract, PRODUCT.md | durable design system docs | project docs/files | `skill/agents/impeccable-documenter.md:1-33` | 확인됨 [E8] |
| finish reviewer | subagent | screenshot/approved comp/contract 기반 마지막 gate | screenshots, contract, product context, quality bar | `recapture`/`rebuild`/`fix`/`ship`, material fix list | image viewing/read-only review | `skill/agents/impeccable-finish-reviewer.md:1-47` | 확인됨 [E8] |
| manual edit applier | subagent | live manual copy-edit batch를 source에 원자적으로 반영 | leased event, source hints, batch/evidence | canonical JSON apply result, changed source | project source files; commit/push/build 금지 | `skill/agents/impeccable-manual-edit-applier.md:1-83` | 확인됨 [E8] |
| build transformer | build script | source skill을 provider별 artifact/ZIP로 변환하고 count/version/manifest를 검증 | `skill/`, transformers, registry | generated provider output/ZIP/build error | filesystem, generated root folders | `scripts/build.js:1-176` | 확인됨 [E4] |
| test-suite router | test runner | default/opt-in suite를 확장해 Bun/Node test 명령 실행 | suite args, env | command exit status | local runtime/provider APIs for opt-in paths | `scripts/run-tests.mjs:1-98`; `scripts/test-suites.mjs:4-50` | 확인됨 [E13] |
| GitHub CI | workflow | matrix test/build/generated-output validation 및 selective E2E | push/PR/schedule, changed paths | workflow status/artifacts | GitHub runners, actions cache, optional secrets | `.github/workflows/ci.yml:1-457` | 확인됨 [E12] |
| generated-output sync | workflow | main의 generated provider drift를 build/retry/commit/push | main push/workflow dispatch | generated commit or failure | write permission to repo contents | `.github/workflows/sync-generated-output.yml:1-136` | 확인됨 [E14] |
| release script | release automation | component별 version, build, tag, GitHub release preflight/실행 | component, working tree, remote/changelog/artifacts | tag/release, release notes | git remote, GitHub release, npm/store follow-up | `scripts/release.mjs:1-260` | 확인됨 [E6] |
