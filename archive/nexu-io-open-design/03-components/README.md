# 실행 구성요소와 agent/skill 정의

이 디렉터리는 고정 SHA에서 직접 확인한 `.claude` agent/skill 정의의 한국어 번역과, 번역 대상이 아닌 실행 핵심 구성요소의 짧은 설명을 함께 둔다. 제품의 기능적 `skills/` 357개나 모든 runtime definition을 번역한 디렉터리가 아니다. [S2]

## 실행 핵심 구성요소

- **Web UI (`apps/web`)**: Next.js/React surface다. 프로젝트, 대화, 파일 workspace, preview, Settings를 보여 주지만 project database의 독립 source of truth는 아니다. [S5]
- **Daemon (`apps/daemon`)**: Express + SQLite 권위 계층이다. `/api/*`, `od` CLI, project persistence, generated file, agent spawn과 SSE를 소유한다. [S8]
- **Runtime engine + definitions**: registry의 agent definition이 prompt delivery, executable, model/auth probe, stream format, sandbox/permission shape를 선언하고 shared engine이 lifecycle을 수행한다. Codex의 구체 계약은 표와 [od-contribute SKILL](od-contribute-SKILL.ko.md)이 아니라 `runtimes/defs/codex.ts` 근거를 보라. [S5], [S12]
- **Artifact write/preview**: manifest가 검증된 output을 project file로 쓰고 previewable entry를 iframe에서 보여 준다. 단순 chat summary가 deliverable 검증을 대신하지 않는다. [S14], [S18]
- **Packaged desktop**: Electron packaged outer entry가 namespace-scoped path를 준비하고 daemon·web sidecar 후 desktop shell을 시작한다. [S9]

## 번역 파일

- [od-contribute-SKILL.ko.md](od-contribute-SKILL.ko.md): `nexu-io/open-design` 기여를 위한 `.claude` skill의 구조 보존 번역이다. 이 아카이브에서는 실행하지 않았다. 원본은 file write와 GitHub PR/issue를 수행할 수 있으므로 일반 design-generation runtime과 권한을 섞어 해석하면 안 된다. [S20]
- [od-contribute-openai.ko.yaml](od-contribute-openai.ko.yaml): Codex picker용 metadata의 구조 보존 번역이다. [S21]

## 범위 경계

`od-contribute`는 source contribution flow다. 그것이 허용하는 Bash/Read/Write/Edit/AskUserQuestion/WebFetch는 해당 skill이 실행될 때의 권한·절차이며, OpenDesign의 모든 chat run 또는 모든 local CLI에 GitHub write 권한을 부여한다는 뜻이 아니다. [S20], [S21]
