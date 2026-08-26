# 소스 고정 정보

- Origin URL: https://github.com/dyoshikawa/rulesync
- Ref: `main`
- Commit SHA: `c3acceacec5463efe14ebb1b8be5fed5fa835e65`
- Analysis timestamp: `2026-08-23T18:47:49Z`

## 접근 방식과 한계

이 아카이브는 GitHub REST API와 고정 SHA의 raw 파일만 읽었다. 대상 저장소를 clone·수정하지 않았고, issue/PR·설정·secret·배포에는 접근하지 않았다.

소스 트리에는 1,000개가 넘는 TypeScript/테스트/문서 파일과 `.rulesync/skills/*/SKILL.md` 42개가 있다. 실행 계약, CLI 진입점, 생성·가져오기·변환·MCP 경계, 설정, CI/E2E, 실제 서브에이전트 5개와 대표 스킬 2개를 열어 교차 확인했다. 나머지 40개 스킬 정의, 전체 feature adapter 및 도구별 형식의 전수 내용, 개별 CI 실행 결과, npm·Homebrew·릴리스의 현재 배포 상태는 이 분석 범위에서 열거나 실행하지 않았으며, 본문에서 미확인으로 표시한다.

## 제외 후보와 이유

- `pnpm-lock.yaml`, `dist`에 해당하는 배포 산출물, 이미지: 실행 구조를 추가로 설명하지 않거나 고정 SHA의 소스 분석 범위를 넘으므로 제외했다.
- `docs/reference/cli-commands.md` 전체: 35KB의 명령 옵션 전문은 코드의 `src/cli/program.ts` 및 짧은 사용 문서로 핵심 계약을 검증하고, 전수 번역은 별도 문서화 작업으로 남겼다.
- `.rulesync/skills/`의 미열람 40개: 파일 수가 많아, 실행 코드와 직접 연결되는 `agent-team` 및 배포용 `skills/rulesync/SKILL.md`를 대표로 읽었다. 이 선택은 각 미열람 스킬의 행동·권한을 보증하지 않는다.
