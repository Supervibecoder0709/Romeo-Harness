# 소스 고정 기록

- Origin URL: https://github.com/design-tokens/community-group
- Ref: main
- Commit SHA: `16c902d9327c18290e956a21130c445f1b88c40f`
- Analysis timestamp: 2026-08-24T03:53:13+09:00

## 접근 방식과 한계

- GitHub REST API와 raw 파일 읽기만 사용했다. clone, Issue/PR 작성, 설정 변경, secret 조회, 배포, 로컬 의존성 설치와 테스트 실행은 하지 않았다.
- `main`의 API 조회 결과를 위 SHA로 고정한 뒤, 해당 SHA의 재귀 트리와 선정 파일만 읽었다. 따라서 이 아카이브의 사실 판단은 그 커밋 시점의 저장소 내용에 한정된다.
- GitHub Actions·Netlify·GitHub Pages의 실제 실행 로그, 권한, 배포 결과와 외부 공개 사이트의 현재 응답은 열어 보지 않았다. 문서 또는 워크플로 설정에 적힌 동작과 실제 운영 성공은 구분한다.

## 제외한 후보와 이유

- `pnpm-lock.yaml`, 이미지·폰트·ZIP, `www/public/TR/**`, `www/src/pages/TR/**`의 대형 생성 HTML: 실행 진입점이나 원본 명세가 아닌 잠재적 생성물·정적 자산이라 전체 다운로드를 하지 않았다.
- `technical-reports/**`의 세부 장·과거 회의록: 전체 명세 텍스트를 번역하는 범위는 아니므로, Format/Resolver의 진입 HTML과 핵심 입력 문서만 표본으로 열었다.
- 긴 Playground 예제와 스냅샷: 데모의 예제 데이터·표현 결과이며 핵심 제어 흐름이 아니므로 제외했다.
- Issue/PR 템플릿, devcontainer·에디터 설정: 기여 양식 또는 개발 편의 설정으로서 핵심 빌드·배포·데모 경로의 판정에는 직접 필요하지 않았다.

## 미확인으로 남긴 항목

- `technical-reports` Action과 Netlify의 실제 최근 성공 여부, 배포 권한·보호 규칙, 외부 사이트의 게시 상태
- `pnpm run build`, `pnpm run test`, ReSpec validation, schema bundle의 현재 SHA에서의 실제 통과 여부
- 공개 API 외의 비공개 운영 규칙, GitHub branch protection의 현재 설정, Discord/외부 서비스의 접근 권한

근거 표는 [06-source-evidence.md](06-source-evidence.md)에 있다.
