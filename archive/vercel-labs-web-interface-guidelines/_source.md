# 소스 고정 정보

- Origin URL: https://github.com/vercel-labs/web-interface-guidelines
- Ref: main
- Commit SHA: `e3d624baaf29dc1fc645aff3e38f03e564d2d6b1`
- License: MIT
- Analysis timestamp: 2026-08-24T03:48:13+09:00

## 접근 방식과 한계

- GitHub 읽기 전용 API로만 확인했다. 대상 레포는 clone하지 않았고, issue/PR·설정·secret·배포에 접근하거나 변경하지 않았다.
- 고정 SHA의 재귀 트리에서 확인한 blob은 `AGENTS.md`, `LICENSE`, `README.md`, `command.md`, `install.sh` 5개다. 이 5개 원문을 모두 열었다. [E01]
- 따라서 `package.json`, lockfile, 테스트, CI workflow, 배포 설정, 런타임 애플리케이션 코드는 이 커밋의 트리에 없음을 **확인**했다. 단, GitHub Actions의 실행 이력·외부 배포물·README가 링크한 별도 `vercel-labs/agent-skills` 레포는 범위 밖이라 **미확인**이다. [E01][E12]
- `install.sh`가 내려받는 원격 주소는 고정 SHA가 아닌 `main`이다. 이 아카이브는 해당 스크립트를 실행하지 않았으므로, 실제 설치 결과와 외부 도구별 동작은 **미검증**이다. [E09]

## 제외한 후보

| 경로/대상 | 제외 또는 미확인 사유 |
| --- | --- |
| `LICENSE` | MIT 사용 허가 원문이며 제품 동작·워크플로우 근거가 아니므로 번역/구성요소 분석 대상에서 제외했다. [E13] |
| GitHub Actions/테스트/패키지 설정 | 고정 SHA 트리에 파일이 없어 열 수 있는 대상이 없다. [E01] |
| `https://github.com/vercel-labs/agent-skills` | README가 설치 명령으로 링크한 별도 레포다. 본 요청의 대상 레포가 아니어서 열지 않았다. [E12] |
