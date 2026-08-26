# 탐색 기록

## 결론 요약

**확인된 사실:** CIS는 Node 패키지로 관리되는 BMad 모듈이다. 저장소 안의 핵심 산출물은 6개 페르소나 agent와 4개 로컬 workflow를 지시하는 Markdown skill, 그 기본값을 담은 TOML, 방법론 CSV, 결과 Markdown template이다. `main`에 독립 서버·CLI 진입점·데이터베이스·API handler는 없다. [E03][E04][E05]

**판단:** 따라서 이 모듈의 실제 실행 주체는 이 레포가 아닌 BMad 호스트/AI IDE다. 이 아카이브에서 “저장한다”, “실행한다”는 표현은 `SKILL.md`가 호스트에게 요청하는 동작이지, 이 레포의 JavaScript가 강제·검증하는 동작이라는 뜻이 아니다. [E04][E05]

## 탐색 범위와 후보 선정

| 후보군 | 실제로 연 파일 | 선정 이유 |
| --- | --- | --- |
| 사용자 안내 | `README.md`, `docs/tutorials/getting-started.md`, `docs/reference/{agents,configuration,workflows}.md` | 설치·호출·출력 주장과 소스의 차이를 찾기 위해 |
| 모듈 계약 | `src/module.yaml`, `src/module-help.csv` | 설치 선택 여부, agent roster, 외부 도구 선택, help catalog를 확인하기 위해 |
| agent 정의 | `src/skills/bmad-cis-agent-*/SKILL.md`, 각 `customize.toml` | 활성화·설정 병합·메뉴·페르소나·외부 skill 호출을 확인하기 위해 |
| workflow 정의 | `bmad-cis-{design-thinking,innovation-strategy,problem-solving,storytelling}/SKILL.md`, template 및 CSV 존재 | 입력, 단계, 체크포인트, 출력 경로·형식을 확인하기 위해 |
| 문서 실행 경로 | `package.json`, `tools/build-docs.mjs`, `website/astro.config.mjs`, `site-url.mjs` | 실제 Node 진입점과 build output을 확인하기 위해 |
| 검증·운영 | `.github/workflows/{quality,docs,release,discord}.yaml`, Discord helper | CI 범위, 배포·릴리스 권한, 외부 웹훅 경계를 확인하기 위해 |

## 확인된 진입점과 기술 스택

- `package.json`의 실제 스크립트 진입점은 `docs:build → node tools/build-docs.mjs`다. `test`는 애플리케이션 테스트가 아니라 ESLint, Markdown lint, Prettier 검사 묶음이다. Node 요구 버전은 `>=22.0.0`이다. [E03]
- `tools/build-docs.mjs`는 기존 `build/`를 삭제·재생성하고, `docs/`에서 `llms.txt`와 `llms-full.txt`를 만든 뒤 Astro를 빌드해 `build/site/`에 파일을 복사한다. [E10][E11]
- `src/module.yaml`은 BMad module code `cis`, 기본 미선택, Mermaid/Excalidraw/Gemini Nano/기타 이미지 생성 도구 선택지를 선언하며 6 agent를 `creative` team으로 등록한다. [E04]
- agent/workflow의 공통 활성화 계약은 외부 `_bmad/scripts/resolve_customization.py`로 기본·team·user TOML을 병합하고, 프로젝트의 `_bmad/cis/config.yaml`을 읽는 방식이다. 이 resolver와 config 생성기는 이 트리에 없다. [E05][E06]

## 핵심 흐름

1. 사용자는 BMad 호스트에서 모듈을 선택하고 agent 또는 workflow skill을 호출한다는 것이 문서의 주장이다. 이 저장소만으로 실제 alias 등록 여부는 확인하지 못했다. [E01][E04]
2. agent는 TOML 병합 후 페르소나를 채택하고, 메뉴의 `skill` 또는 `prompt`를 dispatch한다. [E05]
3. 4개 workflow는 host config와 선택적 `data` 문맥을 읽고, CSV 방법론 및 Markdown template을 사용한다. 각 `<template-output>` 직후 파일을 저장하고 사용자 선택을 기다리도록 지시한다. [E06]
4. 별도 문서 사이트 경로는 `npm run docs:build`와 GitHub Pages workflow다. 품질 workflow는 PR에서 정적 검사만 수행한다. [E03][E08][E10]

## 문서-소스 교차 확인 결과

| 항목 | 결론 | 근거 |
| --- | --- | --- |
| 로컬 workflow | design thinking, innovation strategy, problem solving, storytelling 4개는 실제 `SKILL.md`가 있다. | [E06] |
| brainstorming | Carson agent 메뉴는 `bmad-brainstorming`을 가리키지만 이 고정 SHA 트리에는 해당 skill 정의가 없다. 외부 BMad 의존성으로 보이나 제공 여부는 미확인이다. | [E02][E05] |
| presentation | Caravaggio agent는 7개의 직접 prompt 메뉴를 갖지만 module help catalog에는 없고, 전용 workflow `SKILL.md`도 없다. 문서의 “coming soon”과도 시점 차이가 있다. | [E02][E04][E05][E15] |
| 명령어 | README의 `/cis-problem-solve`, `/cis-innovation`과 튜토리얼의 `/cis-problem-solving`, `/cis-innovation-strategy`은 다르다. module source에는 alias 매핑이 없으므로 어느 명령이 현재 동작하는지 이 레포만으로 확정할 수 없다. | [E01][E02][E04][E12] |
| 환경변수 | reference 문서는 `BMAD_OUTPUT_DIR`, `BMAD_USER_NAME`, `BMAD_LANGUAGE` 우선순위를 주장하지만 열린 workflow 정의에는 config 파일·custom TOML 병합만 명시돼 있다. 호스트가 지원하는지 미확인이다. | [E06][E13] |
| 실행환경 | 패키지는 Node `>=22`, 문서 배포 workflow는 Node 20을 사용한다. 빌드 성공 여부는 실행하지 않았으므로 미확인이나, 운영 전에 정합성을 확인해야 한다. | [E03][E09] |

## 미확인 범위

- BMad installer가 `src/module.yaml`과 skills를 어떤 위치·명령 alias로 설치하는지
- `_bmad/scripts/resolve_customization.py`의 병합·명령 실행·파일 쓰기 권한 집행 방식
- 실제 GitHub Actions 실행 성공, Pages URL, npm 배포물과 릴리스 상태
- CSV 방법론의 실제 행 수·품질, LLM이 체크포인트를 준수하는지, 결과 파일이 실제로 쓰이는지
- secret 값, Discord webhook 수신 여부, GitHub environment protection(모두 의도적으로 열지 않음)

