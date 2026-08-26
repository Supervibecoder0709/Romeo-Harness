# 실행 핵심 구성요소 설명

## `AGENTS.md`

프로젝트가 AI coding agent에게 제공할 수 있는 정적 지시문이다. 인수·도구 호출·권한 선언은 없고, UI 결정을 위한 MUST/SHOULD/NEVER 규칙만 정의한다. 원문 전체의 한국어 번역은 [AGENTS.ko.md](AGENTS.ko.md)에 있다. [E03]

## `command.md`

AI 도구가 UI code review 명령으로 읽을 프롬프트다. frontmatter의 `argument-hint`는 `<file-or-pattern>`이고 본문은 `$ARGUMENTS`의 파일을 읽어 규칙 위반을 검사한 뒤 `file:line` 형식으로 결과를 쓰도록 한다. 실제 파일 읽기, 모델 선택, 권한, 명령 등록은 이 레포가 아니라 host AI tool의 책임이다. 원문 전체의 한국어 번역은 [command.ko.md](command.ko.md)에 있다. [E04][E05]

## `install.sh`

레포에서 실제로 실행 가능한 유일한 구성요소다. 감지된 로컬 AI 도구의 전역 파일 경로에 `command.md`를 내려받고, Antigravity/Gemini CLI에는 요구 형식으로 변환한다. 이 작업은 홈 디렉터리 쓰기와 네트워크 다운로드를 하므로, 자동 Harness에서는 명시적 사람 승인과 설치 뒤 readback이 필요하다. [E06]–[E11]

## 정의되지 않은 구성요소

이 SHA에는 별도 agent runner, skill implementation, server/API, queue, DB, CI, test가 없다. 따라서 이 레포 자체는 검토 결과를 저장하거나 UI를 검증·배포하지 않는다. [E01]
