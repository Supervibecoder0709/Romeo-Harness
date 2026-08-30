# 소스 고정 정보

- Origin URL: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- Ref: main
- Commit SHA: `bc826e2267a36d98a2dcf5231e16c30ff546770f`
- License: MIT
- Analysis timestamp: 2026-08-23T18:49:19Z

## 분석 기준

- GitHub REST API와 raw 파일 읽기만 사용했다. 대상 저장소를 clone하거나, 이슈/PR/릴리스/설정/시크릿을 변경하지 않았다.
- `main`의 기본 브랜치와 SHA는 API로 고정했다. 이 SHA의 커밋 메시지는 `docs: fix outdated manual sync steps in CONTRIBUTING.md (#450)`이며 커밋 시각은 2026-08-20T11:49:06Z이다. [E01]
- 트리에는 blob 662개가 있다. 핵심 소스·배포 CLI·테스트/CI·선택형 `stack/`을 우선 열었고, 대형 데이터 CSV, 번들 폰트, 스크린샷, 테스트 fixture와 원본의 복제본은 전체 내용을 열지 않았다. [E02]

## 접근 한계와 제외

- 이 아카이브는 고정 SHA의 정적 원문 분석이다. npm에 실제 배포된 패키지, GitHub Actions의 실제 실행 결과, 설치 후 사용자 시스템의 파일 변경, 외부 MCP 서버의 현재 동작은 실행·검증하지 않았다.
- `src/ui-ux-pro-max/`는 정본이고 `cli/assets/`, `.claude/skills/ui-ux-pro-max/{data,scripts}`는 동기화 복제본이다. 정본의 모든 CSV 192개 행과 모든 stack 행을 개별 검토하지 않았다. 구조·검증 계약은 코드와 테스트로 확인했다. [E03][E14]
- `cli/assets/`와 `src/`의 중복 파일, `.ttf` 폰트, 이미지/스크린샷, lockfile, 대형 fixture JSON, 전체 reference 자료는 기능 증거보다 배포 데이터이므로 제외했다. 동기화 CI가 이 중 핵심 데이터/스크립트 일치를 검사하는 것은 확인했다. [E11]
- `stack/`은 자체 실행 제품이 아니라 선택적으로 포함된 Claude Website Design Stack 예시다. 그 안의 `npx ...@latest` MCP 의존성, 외부 `frontend-design`/shadcn 서비스, 실제 브라우저 감사를 실행하지 않았다. [E18][E20]

근거 ID의 원문 위치와 URL은 [06-source-evidence.md](06-source-evidence.md)에 있다.
