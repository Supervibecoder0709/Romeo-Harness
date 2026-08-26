# 소스 고정 기록

- Origin URL: https://github.com/anthropics/skills
- Ref: `main` (GitHub API가 반환한 기본 브랜치)
- Commit SHA: `3b3fad96af16a10759d930941b4520ba0c40edae`
- Analysis timestamp: 2026-08-24 03:49:12 KST (+0900)

## 재현 방법과 접근 범위

GitHub REST API로 `default_branch`를 확인한 뒤 `main`을 위 40자리 SHA로 해석하고, 그 SHA의 재귀 Git 트리를 읽었다. 이어서 선정한 Markdown·JSON·스크립트만 같은 SHA의 Contents API로 읽었다. 대상 저장소에 대해서는 clone, push, 이슈·PR 작성, 설정 변경, secret 조회, 배포를 하지 않았다. [S1], [S2]

분석 대상은 애플리케이션 하나가 아니라 Claude가 동적으로 읽는 **Skill 폴더 카탈로그**다. README는 각 skill이 `SKILL.md`의 메타데이터·지침을 가진 독립 폴더라고 설명하고, marketplace 설정은 이를 다섯 Claude Code 플러그인 묶음으로 노출한다. [S3], [S4]

## 확인한 범위

열어 확인한 원문은 루트 `README.md`, `.claude-plugin/marketplace.json`, `template/SKILL.md`, `spec/agent-skills-spec.md`, 19개 `skills/*/SKILL.md`, 그리고 실행 보조 스크립트 중 문서/평가/웹 아티팩트/웹 테스트/GIF/생성 예술 흐름을 대표하는 파일이다. 목록과 URL·줄 범위는 [06-source-evidence.md](06-source-evidence.md)에 있다.

## 접근 한계와 제외

- 고정 트리에는 루트 `package.json`, `pyproject.toml`, lockfile, `Makefile`, `Dockerfile`, `docker-compose*`, `.github/workflows/**`, 일반적인 애플리케이션 진입점이 없다. 따라서 이 아카이브는 이 저장소에 대해 단일 서버·CLI의 런타임이나 CI 통과를 주장하지 않는다. 이는 "없음"이 아니라 **고정 트리에서 해당 경로를 발견하지 못했다**는 범위 확인이다. [S2]
- `claude-api/SKILL.md` 및 그 하위 언어별·공유 참조 문서는 매우 크고 외부 API의 시점 의존성이 높다. 이 아카이브는 그 skill의 트리거·문서 라우팅·내장된 기준일 표기만 확인했으며, 모델 가격·가용성·API 세부가 현재도 맞는지는 검증하지 않았다. [S7]
- `docx`, `pdf`, `pptx`, `xlsx`는 README상 source-available이고 open source가 아니라고 설명한다. 해당 실행 보조 파일을 읽었지만 의존성 설치, 실제 문서 생성, 렌더링, 명령 실행은 수행하지 않았다. [S3], [S12]–[S15]
- 폰트 바이너리, Office XML schema, `shadcn-components.tar.gz`, 테마 PDF, 라이선스 전문, 예제·참조문서의 전체 본문은 핵심 실행 계약을 추가로 증명하지 않아 내용 분석에서 제외했다. 이들은 Git 트리에서 존재만 확인한 항목이다. [S2]
- 원격 실행 결과, 플러그인 설치 성공 여부, Claude.ai 유료 플랜에서의 실제 노출, 외부 `agentskills.io` 명세 본문, Marketplace의 이후 변경은 미확인이다.
