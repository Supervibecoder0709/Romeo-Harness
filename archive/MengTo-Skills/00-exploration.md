# 탐색 기록

## 결론

이 저장소는 설치·서버·배포를 제공하는 애플리케이션이 아니라, 에이전트가 읽고 따르는 Markdown 기반의 이식 가능한 skill 라이브러리다. 핵심 실행 단위는 agent-skills/category/skill-name/SKILL.md이며, 최상위 Node 스크립트는 데모를 생성·동기화·검증·갤러리화하는 유지보수 도구다. [E01] [E03] [E12]

## 탐색 범위

| 항목 | 확인 결과 | 선정 이유 |
| --- | --- | --- |
| 원격 메타데이터 | default branch main, 고정 SHA 4c716b516b6b0143f3037631306b3730d2832344 | 재현 가능한 소스 기준을 먼저 고정 |
| Git tree | blob 891개, SKILL.md 130개, agents/openai.yaml 63개 | 실제 파일 구성·카테고리·후보 규모 확인 [E17] |
| 안내 문서 | README.md, CLAUDE.md, agent-skills/game-development/README.md | 라이브러리 목적, 폴더 계약, 사용/작성 원칙 확인 [E01] [E06] [E07] |
| 대표 skill | iterate-until-verified, publish-project-to-github, ship-web-games, build-awwwards-quality-sites | 품질 검증, 외부 쓰기, 릴리스, 디자인 제작의 고중심 경계 확인 [E08] [E09] [E10] [E11] |
| 유지보수 실행 경로 | backfill, validator, screenshot gallery, Neuform sync/security test | demo 생성·검증·외부 동기화의 코드 경계 확인 [E12] [E13] [E14] [E15] [E16] |

## 실제 진입점

1. 사람 또는 에이전트가 작업과 가장 좁게 맞는 SKILL.md를 선택해 읽는다. Codex는 행동 전에 관련 SKILL.md를 읽고, 다른 에이전트도 가장 좁은 skill부터 시작하라는 계약이다. [E02]
2. 해당 skill은 단계, 기본값, 함정, 완료 검사를 사람 언어로 제공한다. 예를 들어 iterate-until-verified는 원래 요청을 고정하고 관찰 가능한 gate로 바꾼 뒤 증거 기반 반복을 요구한다. [E08]
3. 시각/워크플로우 skill은 선택적으로 references, article, assets, scripts, demo를 붙일 수 있다. 이는 package import나 런타임 호출이 아니라 파일을 읽고 실행하는 운영 절차다. [E03]
4. 저장소 관리자는 데모를 채우고 screenshot gallery를 다시 만들고 validator를 실행한다. 이 도구들은 git ls-files로 현재 추적 SKILL.md를 찾기 때문에 git checkout에서의 실행을 전제한다. [E12] [E13] [E14]

## 기술 스택 및 외부 경계

- 본체: plain Markdown, folder-based skill package. package manifest, lockfile, Dockerfile, compose, CI workflow는 고정 tree의 후보 탐색에서 확인하지 못했다. [E01] [E17]
- 유지보수: Node ESM와 Node 표준 라이브러리, git, 파일 시스템. 일부 helper는 Python, Playwright, ffmpeg, macOS sips를 요구한다. [E12] [E18] [E19]
- 외부 서비스: 일부 skill은 Aura Assets, GitHub, Pages, Neuform을 안내하거나 사용한다. 특히 Neuform sync는 환경변수 또는 .env의 API URL과 anonymous key를 읽고 원격 API/허용 host를 사용한다. [E09] [E16]
- 권한 모델: 저장소 전체에 공통 실행 권한 모델은 없다. 권한은 개별 skill 지시문에 분산돼 있다. publish-project-to-github처럼 공개·push·Pages 변경이 가능한 skill은 명시 권한과 사후 read-back을 요구한다. [E09]

## 확인된 핵심 흐름

- 작업 playbook: 사용자 요청 → 가장 좁은 skill 선택 → SKILL.md 단계 수행 → skill별 산출물/검증 증거. [E02] [E03]
- 데모 유지보수: tracked skill 목록 → 누락 demo scaffold 생성(원본 파생 demo는 보존) → preview/prompt/접근성/경로/manifest 검사 → screenshot 문서·HTML gallery 생성. [E12] [E13] [E14]
- 외부 소스 demo 갱신: Neuform 대상 선정 → API/허용 host와 asset 점검, sandbox wrapper/manifest 생성 → dry-run이 아닐 때만 demo 파일 write → security test가 SSRF·비허용 host·sandbox/CSP·checksum 일부를 검사. [E15] [E16]

## 미확인 범위

- DEMOS.md의 모든 링크, 이미지, prompt, 97개 데모의 실제 렌더 및 validator 통과 여부
- 126개 미열람 skill의 정확한 입력, 외부 권한, 도구, 결과물
- CI 실행 여부와 release/배포 파이프라인의 존재
- Neuform API의 실제 접근 권한과 current public design, Aura Assets 및 GitHub Pages의 현재 상태
- 설치 문서가 없는 Codex/Claude/Cursor에서 이 폴더가 자동 discovery되는지

## 사실·해석 구분

- 확인된 사실: SKILL.md와 최상위 유지보수 스크립트가 존재하며 validator와 security test의 검사는 코드에서 확인했다. [E12] [E15]
- 해석: 이 저장소는 실행 가능한 제품보다 선택적으로 실행하는 표준작업서 라이브러리로 운영하는 편이 구조와 맞다. 이는 Markdown-first 계약과 package/CI 후보 부재를 함께 읽은 결론이다. [E01] [E03] [E17]
- 미확인: 개별 skill의 품질·완전성, 모든 demo의 실제 결과, CI 통과 상태.
