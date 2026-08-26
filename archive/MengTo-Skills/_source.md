# Source lock

- Origin URL: https://github.com/MengTo/Skills
- Ref: main
- Commit SHA: `4c716b516b6b0143f3037631306b3730d2832344`
- Analysis timestamp: 2026-08-23T18:47:06Z

## 접근 방식과 한계

- GitHub REST API와 고정 SHA의 raw 파일만 읽었다. 대상 저장소를 clone하거나 issue/PR, 설정, secret, 배포를 변경하지 않았다.
- Git tree API에서 891개 blob 경로를 확인했다. agent-skills 아래 SKILL.md는 130개이며 컬렉션별 수는 codex 19, game-development 20, media 2, ui 1, web-design 88이다. 이 수치는 고정 SHA의 tree 경로 패턴을 세어 얻은 관찰값이다. [E17]
- README, CLAUDE 안내, 게임 컬렉션 안내, 대표 workflow/발행/검증 skill 4개, 최상위 데모 유지보수 스크립트 5개와 일부 helper script를 열었다. 130개 모든 SKILL.md 본문이나 97개 데모를 전부 열거나 실행하지는 않았다.
- 이 아카이브는 소스의 구조와 계약을 설명한다. 원격 데모의 실제 렌더링, Node/Playwright/ffmpeg 의존성 설치, 스크립트 실행 성공, 외부 서비스 API 상태는 검증하지 않았다.

## 제외한 후보와 이유

| 제외 범주 | 수/범위 | 이유 |
| --- | ---: | --- |
| 모든 개별 skill 본문 | 대표 4개를 제외한 126개 | 최상위 계약, 대표 workflow, 검증 코드, 외부 경계를 교차 확인했다. 제목과 경로만 확인한 skill의 세부 동작은 주장하지 않는다. |
| demo HTML, preview 이미지, assets | demo/index.html 97개와 binary/media 다수 | 시각 결과나 상호작용은 브라우저 실행이 필요하다. 파일 존재와 정적 validator 계약만 확인했다. |
| 자동 생성물/대형 본문 | SCREENSHOTS.html, gallery 이미지, tweet-corpus.jsonl 등 | 실행 핵심보다 자료·생성 결과 성격이 강하다. |
| CI 설정 | .github/workflows 후보 없음 | 고정 tree에서 workflow 경로를 찾지 못했다. CI가 없다고 단정하지 않고, 이 스냅샷에서 workflow 파일을 확인하지 못했다고 기록한다. |

## 문서-트리 불일치

README는 123개 skill, web-design 81개라고 적지만 [E04], 고정 tree의 경로 집계는 130개/88개다. DEMOS.md는 모든 tracked skill의 데모와 총 89개라고 서술하지만 [E21], validator는 현재 git에서 찾는 모든 SKILL.md에 demo, prompt, preview를 요구한다 [E12]. 이 아카이브에서 현재 구성 수와 데모 커버리지는 tree/검증 코드 관찰을 우선하며, 실제 validator 실행 결과는 미검증이다.
