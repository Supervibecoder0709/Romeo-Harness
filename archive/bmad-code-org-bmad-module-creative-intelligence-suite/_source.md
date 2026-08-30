# Source fixation

- Origin URL: https://github.com/bmad-code-org/bmad-module-creative-intelligence-suite
- Ref: main
- Commit SHA: `0e4ff9233a792db1a1cd00f22a482f338168cdc3`
- License: MIT
- Analysis timestamp: 2026-08-24T03:49:24+0900

## 접근 방식과 한계

- GitHub REST API와 해당 SHA의 raw 파일만 읽었다. clone, 이슈/PR 작성, 설정 변경, secret 조회, 배포, 원격 테스트 실행은 하지 않았다.
- 재현 기준은 위 SHA이다. 이후 `main`의 내용, GitHub Actions 실행 결과, GitHub Pages 배포 상태, npm 배포물은 이 아카이브가 확인한 대상이 아니다.
- 이 저장소에는 BMad 호스트 런타임(설치기, `/cis-*` 명령 별칭 등록기, `_bmad/scripts/resolve_customization.py`, Party-Mode/Advanced Elicitation 구현)이 없다. 따라서 이 소스만으로 설치 성공, 명령 인식, 실제 파일 저장, 권한 제한을 확인할 수 없다. [E01][E04][E07]
- API 트리를 끝까지 열었으며(`truncated=false`), 후보 중 lockfile, 이미지, 중국어 번역본, 일반 커뮤니티/행동강령 문서, 변경 이력은 핵심 실행 경로 판단에서 제외했다. 테스트 디렉터리는 트리에 없었고, 별도 테스트 실행은 하지 않았다. [E02]

## 분석 범위

열어 본 핵심 파일은 `README.md`, `package.json`, `src/module.yaml`, `src/module-help.csv`, 6개 agent `SKILL.md` 및 `customize.toml`, 4개 workflow `SKILL.md` 및 `template.md`, 문서 빌드 스크립트, Astro 설정, 품질·문서배포·릴리스·Discord Actions, 그리고 사용/참조 문서다. 전체 근거 URL과 줄 범위는 [06-source-evidence.md](06-source-evidence.md)에 있다.

## 제외 후보와 사유

| 제외 범위 | 사유 |
| --- | --- |
| `package-lock.json` | 의존성 잠금 생성물이며 실행 계약은 `package.json`으로 확인 가능 |
| `website/public/**`, `website/src/styles/**`, 일반 Astro UI 컴포넌트 | 제품 기능보다 문서 사이트의 시각 표현에 해당 |
| `docs/zh-cn/**` | 영어 원문 문서의 중국어 번역본이라 중복 |
| `CHANGELOG.md`, `.github/ISSUE_TEMPLATE/**`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md` | 운영/커뮤니티 보조 자료이며 CIS의 agent/workflow 실행 계약은 아님 |
| 모든 CSV의 전체 행 | workflow가 각 CSV를 로드한다는 계약과 파일 존재만 확인했다. 각 방법론의 완전성·정확성은 평가하지 않았다. |
