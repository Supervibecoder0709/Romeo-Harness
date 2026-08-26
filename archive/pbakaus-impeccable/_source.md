# Source record

- Origin URL: https://github.com/pbakaus/impeccable
- Ref: main
- Commit SHA: `56f44523f76efdcec813e67b38ee550e49b16f48`
- Analysis timestamp: 2026-08-23T18:49:10Z

## 접근 방식과 한계

- GitHub REST API와 raw 파일 읽기만 사용했다. clone, issue/PR 작성, 설정 변경, secret 조회, 배포는 수행하지 않았다.
- `main`은 위 SHA로 해석을 고정했다. 이후 `main`이 움직여도 이 아카이브의 근거 URL은 고정 SHA를 가리킨다.
- 재귀 tree API는 `truncated=false`로 응답했고 blob 경로 3,268개를 확인했다. 이 수는 공급자별 생성 배포본과 테스트 fixture를 포함한다.
- 이 작업 환경에서 대상 레포의 의존성을 설치하거나 `bun run test`/브라우저 E2E를 실행하지 않았다. 따라서 테스트 **정의와 CI 구성**은 확인했지만, 이 SHA에서의 실제 실행 통과 여부와 배포·npm 게시 상태는 미확인이다.
- GitHub Actions secret의 값은 열지 않았다. CI YAML에 secret 이름과 키가 없을 때 skip하는 조건만 기록했다.

## 제외한 후보와 이유

- `.agents/`, `.claude/`, `.cursor/`, `.gemini/`, `.github/skills/` 등은 `skill/` 원본을 공급자 형식으로 생성한 추적 배포물이다. 대표 배포 경로와 생성·동기화 계약은 열었지만, 같은 내용의 전 복제본은 중복이라 본문 분석 대상에서 제외했다. [E4] [E14]
- `dist/`, `build/`, 번들 JS, 대량 framework fixture와 lockfile은 생성물 또는 개별 회귀 입력이라 전문을 읽지 않았다. 각 범주의 존재와 검증 경로는 tree/테스트 계약으로만 확인했다.
- `site/`, `functions/`, `extension/`의 모든 구현과 private eval repository는 이 아카이브의 핵심 harness/CLI 경로를 설명하는 데 필요한 범위 밖이다. `AGENTS.md`가 해당 경로와 private eval의 존재를 말하지만, 각각의 런타임 동작은 미확인이다. [E5]

## 근거 상태 표기

- **확인됨**: 고정 SHA의 원문 코드·설정·테스트 정의에서 직접 확인.
- **추론**: 여러 확인된 파일을 연결한 동작 해석. 문서의 `추론` 문단에서만 쓴다.
- **미확인**: 원문을 열지 않았거나, 실행·외부 서비스·권한이 있어 이 읽기 전용 분석만으로 증명할 수 없는 항목.
