# Source record

- Origin URL: https://github.com/Leonxlnx/taste-skill
- Ref: main
- Commit SHA: `72e299530e2eb31ed8da06181bc19f6c18a00821`
- Analysis timestamp: 2026-08-24T03:54:46+09:00

## 고정 범위와 접근 방법

분석은 GitHub 읽기 전용 API로만 수행했다. `main`의 커밋 SHA를 먼저 고정한 뒤 그 SHA의 재귀 트리(일반 파일 64개)와 선정한 파일 내용만 읽었다. 대상 저장소를 clone, 실행, 설치, 수정하거나 GitHub에 쓰기 작업을 하지 않았다.

## 접근 한계

- 이 아카이브는 문서형 에이전트 스킬의 **정의와 저장소 내 정적 계약**을 설명한다. 실제 모델이 이 지시를 준수하는지, 이미지 생성 품질, 생성 코드의 빌드·접근성·보안, `npx skills add`의 현재 동작은 실행 검증하지 않았다.
- `README.md`가 주장하는 `npx skills add`의 스캔·설치 동작은 이 저장소 안에 구현되어 있지 않다. 외부 CLI의 원문과 실행 결과를 열지 않았으므로 `UNVERIFIED_EXTERNAL_CLI`다.
- 재귀 트리에는 package manifest, lockfile, Dockerfile, Makefile/justfile, `.github/workflows/`가 없었다. 따라서 이 저장소 자체의 빌드, 테스트, CI, 배포 절차는 `NOT_PRESENT_IN_FIXED_TREE`이며 품질 보장은 확인할 수 없다.
- `research/`의 연구 주장과 외부 연구 인용은 몇 개의 안내/예시 파일만 읽었다. 논문 원문·실험 데이터·인용의 정확성은 독립 검증하지 않았다.

## 의도적으로 제외한 후보

- `assets/**`, `examples/**`: README를 꾸미는 이미지·로고·예시 렌더로, 실행 계약을 추가로 증명하지 않아 내용 열람에서 제외했다.
- `scripts/*.mjs`: README 자산 변환/스폰서 행 생성 스크립트이며, 스킬의 설치 또는 에이전트 실행 경로가 아니다. 정적 트리에서 존재만 확인했고 내용은 열지 않았다.
- `research/laziness/**`의 나머지 8개 세부 문서: 스킬 실행 계약이 아닌 배경 글이다. 연구 디렉터리 README, 참조 프롬프트, 실험 결과 파일만 표본으로 열었다.

근거 ID와 원문 위치는 [06-source-evidence.md](06-source-evidence.md)에 있다.
