# 소스 근거

고정 커밋: `e3d624baaf29dc1fc645aff3e38f03e564d2d6b1`
원문 기준 URL은 모두 이 SHA를 가리킨다. `[E##]`는 다른 아카이브 문서에서 쓰는 근거 ID다.

| ID | 원문 URL | 파일·줄 범위 | 뒷받침하는 사실 |
| --- | --- | --- | --- |
| E01 | https://github.com/vercel-labs/web-interface-guidelines/git/trees/e3d624baaf29dc1fc645aff3e38f03e564d2d6b1?recursive=1 | 재귀 tree 전체 | blob은 `AGENTS.md`, `LICENSE`, `README.md`, `command.md`, `install.sh` 5개뿐이다. 따라서 이 SHA에는 package/lockfile·테스트·CI·앱 런타임 코드가 없다. |
| E02 | https://github.com/vercel-labs/web-interface-guidelines/blob/e3d624baaf29dc1fc645aff3e38f03e564d2d6b1/README.md | L1-L197 | 가이드라인 범위, UI 원칙, Vercel 전용 카피, 에이전트 통합 안내. L11의 `maximum-scale=1` 제안도 포함한다. |
| E03 | https://github.com/vercel-labs/web-interface-guidelines/blob/e3d624baaf29dc1fc645aff3e38f03e564d2d6b1/AGENTS.md | L1-L155 | AI 프로젝트 지시문용 MUST/SHOULD/NEVER UI 규칙; L16은 `maximum-scale=1`을 금지 예로 든다. |
| E04 | https://github.com/vercel-labs/web-interface-guidelines/blob/e3d624baaf29dc1fc645aff3e38f03e564d2d6b1/command.md | L1-L167 | `description`, `<file-or-pattern>`, `$ARGUMENTS`, UI 검토 규칙과 금지 패턴. L153은 `maximum-scale=1`을 금지 항목으로 든다. |
| E05 | https://github.com/vercel-labs/web-interface-guidelines/blob/e3d624baaf29dc1fc645aff3e38f03e564d2d6b1/command.md | L168-L190 | 검토 출력은 파일별 `file:line` 형식, 간결한 이슈, 통과 시 `✓ pass`라는 계약. |
| E06 | https://github.com/vercel-labs/web-interface-guidelines/blob/e3d624baaf29dc1fc645aff3e38f03e564d2d6b1/install.sh | L1-L24 | Bash 진입점, `set -e`, TTY 색 처리, 설치 원격·파일명 상수. |
| E07 | https://github.com/vercel-labs/web-interface-guidelines/blob/e3d624baaf29dc1fc645aff3e38f03e564d2d6b1/install.sh | L27-L57 | Amp Code·Claude Code·Cursor·OpenCode를 감지하고 도구별 전역 경로에 `curl -o`로 명령 파일을 설치. |
| E08 | https://github.com/vercel-labs/web-interface-guidelines/blob/e3d624baaf29dc1fc645aff3e38f03e564d2d6b1/install.sh | L59-L76 | Windsurf marker 검사, 전역 `global_rules.md`에 내용 append. |
| E09 | https://github.com/vercel-labs/web-interface-guidelines/blob/e3d624baaf29dc1fc645aff3e38f03e564d2d6b1/install.sh | L19-L21 | `REPO_URL`이 고정 SHA가 아닌 `.../main`을 가리키고, payload는 `command.md`, 이름은 `web-interface-guidelines.md`이다. |
| E10 | https://github.com/vercel-labs/web-interface-guidelines/blob/e3d624baaf29dc1fc645aff3e38f03e564d2d6b1/install.sh | L78-L123 | Antigravity용 `SKILL.md` 변환 및 Gemini CLI용 TOML 변환·설치. |
| E11 | https://github.com/vercel-labs/web-interface-guidelines/blob/e3d624baaf29dc1fc645aff3e38f03e564d2d6b1/install.sh | L125-L143 | 지원 도구가 없으면 안내 후 `exit 1`; 하나 이상이면 완료와 명령 사용법 출력. |
| E12 | https://github.com/vercel-labs/web-interface-guidelines/blob/e3d624baaf29dc1fc645aff3e38f03e564d2d6b1/README.md | L173-L189 | 별도 `vercel-labs/agent-skills`의 `web-design-guidelines` 설치와 이 레포 `AGENTS.md` 다운로드를 안내. |
| E13 | https://github.com/vercel-labs/web-interface-guidelines/blob/e3d624baaf29dc1fc645aff3e38f03e564d2d6b1/LICENSE | L1-L21 | MIT License와 무보증 조건. |
