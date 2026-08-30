# Source fixation

- Origin URL: https://github.com/bmad-code-org/BMAD-METHOD
- Ref: v6.10.0
- Commit SHA: `081e64ee5aab2316b912883f7bee528ee143ce36`
- Analysis timestamp: 2026-08-30T14:32:46+0900
- License: MIT (code); BMad names, logos, and tagline are trademark-restricted

## 접근 방식과 한계

- **확인된 사실:** GitHub REST API로 `v6.10.0`이 위 SHA를 가리키는지 확인했고, Git tree API의 재귀 목록 743개가 `truncated=false`로 반환됐다. 이후 내용은 이 SHA의 raw 파일만 읽었다. clone, 설치, 이슈·PR 작성, 설정 변경, 배포는 하지 않았다. [E01][E02]
- **확인된 사실:** 이 소스는 npm CLI installer, built-in `core`/`bmm` 모듈, 외부 official-module registry를 함께 가진다. 실제 설치는 대상 프로젝트에 `_bmad/`와 선택한 IDE의 skill directory를 쓰므로, 이 아카이브는 설치 성공이나 런타임 실행을 증명하지 않는다. [E03][E04][E05]
- **미확인:** npm registry에 현재도 `6.10.0`이 배포되어 있는지, `npx bmad-method install`이 현 환경에서 성공하는지, Codex/Claude 등 각 런타임이 모든 SKILL 지시(특히 subagent·shell·파일 쓰기)를 같은 방식으로 수행하는지는 실행하지 않았다.
- **미확인:** 외부 module(CIS 포함)의 clone/cache, GitHub tag 해석, network/credential, CI 실행 결과 및 npm/GitHub Pages 배포 상태는 이 SHA의 정적 코드·설정만으로 확인하지 않았다.

## 분석 범위

`README.md`, 설치·모듈·agent·workflow-map 문서, `package.json`, root registry `bmad-modules.yaml`, core/BMM module manifest와 help catalog, installer의 install path/manifest/IDE platform 설정, Codex installer test, 46개 직접 installable SKILL 정의(13 Core + 33 BMM), BMM의 output-defining step files, license/trademark, CI 설정을 열어 교차 확인했다. 전체 근거는 [06-source-evidence.md](06-source-evidence.md)에 있다.

## 제외 후보와 사유

| 제외 범위 | 사유 |
| --- | --- |
| `package-lock.json`, 이미지·website 정적 assets, locale별 중복 번역 | 실행·설치 계약보다 잠금/표현/중복 번역에 해당한다. |
| `docs/{cs,fr,vi-vn,zh-cn}/**` | 영어 원문의 번역본이므로 한국어 번역과 구조 판별에서 중복이다. |
| 46개 SKILL이 참조하는 모든 방법론 CSV·template·step의 전문 | 전체 743 파일을 복제하지 않는다. 출력 경로·상태 변경을 판별하는 참조 파일만 열었다. 각 workflow의 세부 프롬프트 품질·도메인 방법론 완전성은 평가하지 않았다. |
| external official modules의 소스 | `bmad-modules.yaml`의 registry와 이미 아카이브된 CIS의 연결 계약만 확인했다. 외부 레포 실행을 이 본체의 증거로 승격하지 않는다. |
| 실제 installer 실행 | 설치는 프로젝트 파일을 쓰고 외부 모듈은 git cache를 갱신할 수 있어, 요청 경계(읽기 전용) 밖이다. |
