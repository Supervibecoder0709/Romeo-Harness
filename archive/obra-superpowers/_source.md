# Source record — obra/superpowers

- Origin URL: https://github.com/obra/superpowers
- Ref: main
- Commit SHA: `b36e0829c6d0140e93cfef2ca599b1b07d4a7797`
- License: MIT
- Analysis timestamp: 2026-08-24T03:47:39+09:00

## 분석 방법과 재현 경계

- GitHub 읽기 전용 API와 raw content만 사용했다. clone, Issue/PR 작성, 설정 변경, 배포, secret 조회는 하지 않았다.
- 먼저 `repos/obra/superpowers`의 기본 브랜치(`main`)와 `commits/main`의 SHA를 확인한 뒤, 재귀 tree API를 그 SHA로 고정해 탐색했다. tree 응답은 잘리지 않았고(`truncated: false`) blob 195개, 최상위 `skills/*/SKILL.md` 14개, `tests/` 파일 77개, GitHub Actions workflow 0개였다. [E01](06-source-evidence.md#e01) [E02](06-source-evidence.md#e02)
- 내용은 후보 파일만 열어 읽었다. 핵심으로 README·기여 규칙·매니페스트·부트스트랩 코드·선택적 visual companion·대표 테스트를 교차 확인했다. 실제로 연 원문 목록과 선정 이유는 [00-exploration.md](00-exploration.md)에 있다.

## 접근 한계와 미확인

- 이 아카이브는 고정 SHA의 소스 정적 분석이다. Codex/Claude/OpenCode/Pi/Hermes 등 실제 harness에서 설치·부트스트랩·자동 skill triggering이 현재도 작동하는지는 실행하지 않았으므로 **미확인**이다.
- 원문 `docs/testing.md`는 행동 평가가 별도 `superpowers-evals` 저장소의 `evals/`에서 이뤄진다고 설명하지만, 이 고정 tree에는 그 디렉터리가 없다. 외부 저장소의 평가 결과와 CI 실행 결과는 읽거나 실행하지 않았다. [E24](06-source-evidence.md#e24)
- 저장소 tree에 `.github/workflows/` 파일이 없으므로 이 SHA에서 GitHub Actions CI 계약은 확인되지 않는다. 다른 외부 CI, marketplace 배포, 패키지 발행 상태도 미확인이다. [E02](06-source-evidence.md#e02)
- `scripts/sync-to-codex-plugin.sh`, `scripts/package-codex-plugin.sh`, version bump 등에는 쓰기·push·PR 생성 성격의 경로가 있으나 실행하지 않았다. 따라서 그 경로의 실제 권한, 성공 여부, 외부 fork 상태는 미확인이다. [E22](06-source-evidence.md#e22)

## 의도적으로 제외한 후보

- 195개 전체 파일을 복사하지 않았다. `docs/superpowers/plans/`, `docs/superpowers/specs/`의 과거 설계·계획 기록은 현행 실행 계약을 직접 증명하지 않으므로 제외했다.
- lockfile, 이미지/SVG, issue/PR template, release note 전문, 지원 harness별 중복 설치 문서는 핵심 흐름을 직접 바꾸지 않거나 README와 매니페스트로 교차 확인되어 제외했다.
- `docs/porting-to-a-new-harness.md`는 827줄로, 이 아카이브에서는 harness 부트스트랩/배포의 확인 포인트만 근거로 사용했다. 전체 번역은 포함하지 않았다.

`[E##]` 표기는 [06-source-evidence.md](06-source-evidence.md)의 고정 SHA 원문 URL·줄 범위로 연결된다.
