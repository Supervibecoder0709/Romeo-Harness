# 소스 고정 기록

- Origin URL: https://github.com/farion1231/cc-switch
- Ref: main
- Commit SHA: `5ca9459d50ea4beea6a81bbc509de6ec5b6b09ca`
- License: MIT
- Analysis timestamp: 2026-08-23T18:48:59Z

## 수집 방식과 한계

- GitHub REST API로 기본 브랜치와 커밋 SHA를 확인하고, `git/trees/<SHA>?recursive=1`로 1,230개 blob의 경로만 인벤토리했다.
- 이후 이 SHA를 `ref`로 고정한 `contents` raw 읽기만 사용했다. 대상 저장소를 clone하거나, Issue/PR·설정·배포·secret을 변경하거나 조회하지 않았다.
- 이 아카이브도 실행하지 않았으므로 로컬 빌드, 실제 API 요청, 로그인/OAuth, 실제 파일 변경, GitHub Actions 실행 결과와 릴리스 산출물의 서명은 **미검증**이다.
- CI 및 release 워크플로의 소스에는 secret 이름과 사용 경로가 보이지만 secret 값에는 접근하지 않았고, 보안성이나 실제 서명 성공을 그 파일만으로 보장하지 않는다.

## 제외한 후보

- `assets/**`, `src-tauri/icons/**`, `docs/images/**`, `src/icons/extracted/**`: 정적 이미지·아이콘이라 실행 흐름을 증명하지 못해 제외했다.
- `pnpm-lock.yaml`, `src-tauri/Cargo.lock`: 의존성 잠금 생성물이라 실행 계약은 manifest로 확인했다.
- 다국어 README, 릴리스 노트, 전체 user manual, 전체 테스트: 중복 또는 범위가 너무 넓어 제외했다. 대신 실제 진입점·프록시·DB·Skill 명령·CI와 운영 문서 3개를 교차 확인했다.
- GitHub workflow 실행 이력, 외부 provider/skills.sh/GitHub 서버 응답, 업데이터 엔드포인트와 각 앱의 최신 설정 포맷은 이 고정 소스 읽기만으로 확인하지 못했다.
