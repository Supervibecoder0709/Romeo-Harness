# PM Harness 운영 메모

## 결론

이 저장소를 제품 작업에 도입한다면, **`uipro init`으로 바로 설치하지 말고 고정 버전의 임시 프로젝트 설치→생성 파일 검토→프로젝트 설치 승인** 순서가 가장 안전하다. 검색·설계 시스템 기능은 로컬 정적 데이터 기반이라 비교적 격리되어 있지만, 설치/갱신/삭제는 실제 프로젝트 또는 홈 디렉터리의 agent 지침과 파일을 바꾸며, 선택 `stack/`은 외부 MCP 패키지를 최신 태그로 실행한다. [E07][E08][E09][E18]

## 확인된 사실

### 입력 계약과 모델/에이전트 역할

- 주 skill은 UI 구조·시각 디자인·상호작용·접근성·반응형·타이포그래피·차트 작업에만 적용하고, 순수 백엔드/인프라/비시각 스크립트에는 적용하지 않도록 지시한다. [E04]
- 질의는 지배적인 의도 하나와 2~5개 의미 단어가 계약이다. 새 페이지/제품에는 `--design-system`, 특정 버그에는 `--domain`, 이미 아는 구현 기술에는 `--stack`이 권장된다. [E04]
- `design-review` subagent는 코드 추측 대신 브라우저에서 본 screenshot/console/measured value로만 finding을 작성하도록 정의돼 있다. 이는 Harness의 “완료는 관찰 증거로 판단” 원칙과 맞는다. [E18]

### 승인해야 할 지점

| 지점 | 영향 | 승인 전 확인 | 복구 |
|---|---|---|---|
| `uipro init` | 현재 프로젝트에 skill/data/scripts/sub-skill 생성 | 정확한 cwd, 플랫폼, 기존 `.claude`/`.agents` 영향 | Git diff 또는 설치 전 백업에서 복원 |
| `uipro init --force` | 기존 핵심 skill 파일 덮어쓰기 | 덮어쓸 정확한 파일과 사용자 커스텀 여부 | VCS/백업 필요; CLI 자체 롤백 없음 |
| `uipro init --global` | 홈 디렉터리 아래 여러 프로젝트에 영향을 줄 수 있는 지침 생성 | 대상 홈 경로와 조직 규칙 | 백업 또는 명시 uninstall |
| `uipro update` (버전 다름) | 전역 npm 패키지 변경 후 새 init 필요 | 새 릴리스, semver, npm 권한, 영향 프로젝트 | 이전 npm 버전 재설치 + 기존 skill 파일 복원 |
| `uipro uninstall` | 주 skill과 번들 sub-skills 재귀 삭제 | 제거 목록·platform·global 여부; prompt 응답 | 삭제 전 VCS/백업 필요 |
| `--persist --force` | `MASTER.md` 설계 결정 덮어쓰기 | 기존 Master/page override를 읽고 소유자 승인 | VCS/파일 백업에서 복원 |
| `stack/` MCP 승인 | `npx ...@latest`로 외부 패키지 실행, browser/shadcn 도구 연결 | lock/pin 정책, 네트워크/브라우저 권한, 외부 URL 범위 | MCP 설정 제거·프로세스 종료; 이미 발생한 외부 작업은 별도 확인 |

위 표의 행들은 코드에서 실제 쓰기/삭제/외부 실행 경로가 확인된 범위다. 설치 후 메시지 하나만으로 성공으로 볼 수 없고, 생성 파일과 실제 도구의 로드 상태를 readback해야 한다. [E04][E08][E09][E10][E18]

### 실행 단위와 증거·로그

- **검색 단위:** 한 query/도메인/stack. JSON `diagnostics`와 반환된 source identities를 작업 기록에 남기면, “검색 일치”와 “일반 fallback”을 구분할 수 있다. [E05][E06]
- **설계 단위:** 프로젝트 Master + 선택 page override. Master는 전역 기본값, page 파일은 예외라는 계층이므로 둘을 함께 읽어야 한다. [E04]
- **설치 단위:** 한 project root·한 assistant type·한 CLI version. CLI 출력의 folder 목록 외에 실제 생성된 SKILL 파일, scripts/data, agent가 로드한 경로를 확인한다.
- **UI 검증 단위:** URL 또는 file + 각 viewport. heuristic report는 자동 증거지만, taste/상호작용/edge case를 보장하지 않는다고 코드가 명시한다. [E18][E19]

### 재시도·복구

- 검색 0건은 좁은 질의 또는 명시 domain/stack으로 한 번 재시도하고, 실패하면 일치 없음으로 표시한다. 억지로 추천을 만들지 않는다. [E04]
- 다운로드 레거시 install은 API rate limit/네트워크 오류에서 bundle/template 경로로 fallback할 수 있다. 기본 init은 template이므로, “GitHub에서 최신을 받았을 것”이라고 가정하면 안 된다. [E08]
- 데이터 refresh workflow는 candidate/diff artifact만 만들고 repository write 권한을 갖지 않는다. 후보를 canonical data로 승격하는 것은 별도 인간 검토·변경 절차가 필요하다. [E15]

## 확인된 위험·문서 불일치

1. **메타데이터 드리프트:** `plugin.json`은 84 styles, `skill.json`은 84 styles/98 UX guidelines라고 하나, 현 주 skill은 79 searchable styles(50 active)·119 UX guidelines라고 한다. 현 `plugin.json`/`skill.json` version은 2.13.0이고 최신 release API는 v2.15.0이었다. 고정 SHA의 실제 런타임 수와 배포 metadata가 일치한다는 보장은 이 분석에서 확인되지 않았다. [E01][E04][E16]
2. **지속 저장 문서 불일치:** README의 persist 예시는 `--output-dir`를 생략하지만, 주 skill은 실행 cwd 오염 방지를 위해 항상 project root의 `--output-dir`를 전달하라고 한다. PM runbook은 주 skill 기준을 채택해야 한다. [E02][E04]
3. **Stack command 불일치:** `stack/.claude/commands/design-plan.md`는 `--domain web-vitals`를 예시로 쓰지만 `search.py`가 허용하는 domain은 `web`이며 `web-vitals`는 없다. 이 command만으로는 argparse 오류가 난다. Stack은 기본 도입 대상에서 제외하거나 command 수정 후 검증해야 한다. [E05][E18]
4. **삭제 범위:** uninstall은 config상 실제 경로와 legacy `<folder>/skills/` 양쪽을 검사하고 발견한 하위 skill directory를 재귀 삭제한다. “이 CLI만 만든 파일”을 cryptographic manifest로 식별하지 않으므로, 동일 이름의 사용자가 만든 skill과 충돌하지 않는지 사전 확인이 필요하다. [E10]
5. **CLI 문서 라이선스 불일치:** root repository와 `cli/package.json`은 MIT라고 선언하지만 `cli/README.md`는 CC-BY-NC-4.0이라고 적는다. 어떤 범위에 어떤 라이선스가 적용되는지는 이 정적 분석만으로 판정할 수 없으므로, 도입·재배포 전 maintainer의 명시를 확인해야 한다. [E07][E22]

## 추천 운영안

**추천: 프로젝트별 고정 버전, local install, readback gate, 그리고 stack은 별도 보안 검토 후 opt-in**.

이 방식이 현재 가장 알맞은 이유는 비용이 거의 없고, 설치의 파일 변경 범위를 특정 저장소로 좁히며, `--global`이 만드는 횡단 영향과 latest MCP 공급망 위험을 피하기 때문이다. `uipro init --ai <target>`에는 target 플랫폼과 cwd를 사전에 기록하고, `--force`/`--global`/`uninstall`은 명시 승인으로 제한한다. 검색 결과에는 query·domain·JSON diagnostics·source identities를 보존하고, UI 완료는 screenshot/console/report 같은 관찰 증거가 있어야 통과시킨다.

대안 1은 글로벌 설치다. 개인 장비에서 많은 실험 프로젝트를 빠르게 시작할 수 있지만, 지침 충돌과 버전 변경 영향이 넓어 팀/운영 프로젝트에는 추천하지 않는다. 대안 2는 `stack/`을 완전히 도입하는 방식이다. 실제 브라우저 검토가 필요한 프런트엔드 팀에는 가치가 있지만, 현재 `@latest` 외부 MCP 실행과 command 불일치를 정리하고, URL/브라우저 권한 및 audit artifact 보존 방식을 결정한 뒤에만 적합하다.

## 확장 전 확인 목록

- [ ] 사용자 프로젝트가 사용하는 agent 규약과 target install path를 실제로 확인했다.
- [ ] 설치할 npm version/release SHA, `--global` 여부, 기존 skill 충돌 여부를 승인받았다.
- [ ] `--force` 전 Master/skill 파일을 읽고 백업 또는 VCS 복원 지점을 확보했다.
- [ ] stack을 쓸 경우 MCP 패키지 버전 pin, 외부 URL/브라우저 데이터 범위, browser action 허용 범위를 결정했다.
- [ ] UI 결과는 적어도 대상 viewport screenshot, console error, keyboard/focus 및 핵심 플로우 관찰로 재확인한다.
