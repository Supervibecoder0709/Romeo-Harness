# 구성요소 표

`근거 상태`의 “확인됨”은 고정 SHA의 파일 내용이 존재한다는 뜻이며, 외부 도구에서의 실제 수행 또는 결과 품질까지 뜻하지 않는다.

| 구성요소 | 종류 | 역할 | 입력 | 출력/상태변화 | 권한·외부 경계 | 원문 위치 | 근거 상태 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `README.md` 설치 안내 | 문서 | 설치·선택 경로 안내 | repo URL, 선택적 install name | 외부 CLI 명령 제시 | `npx skills` 외부 CLI | README 107-139 | 파일은 확인됨, 설치는 미검증 |
| `.claude-plugin/plugin.json` | 플러그인 메타데이터 | taste-skill plugin 식별 | 없음 | name/version/keywords | Claude plugin 소비자 | plugin.json 1-18 | 확인됨 |
| `skill.sh` | 로컬 레지스트리 | 스킬 별 파일 경로 반환 | skill name | stdout 경로 | shell, 실제 실행 없음 | skill.sh 4-24 | 확인됨 |
| `design-taste-frontend` | 구현 지시문 | 랜딩/포트폴리오/리디자인 디자인 계약 | brief, 참조, 제약 | 코드 지시·pre-flight | 구현 에이전트, 권장 패키지 | taste-skill 1-1140 | 정의 확인, 결과 미검증 |
| `design-taste-frontend-v1` | 구현 지시문 | v1 하위 호환 | brief | 코드 지시 | 구현 에이전트 | taste-skill-v1 1-224 | 정의 확인, 결과 미검증 |
| `gpt-taste` | 구현 지시문 | AIDA·GSAP·변형 강화 | prompt | 코드 지시 | GPT/Codex, GSAP 권고 | gpt-tasteskill 1-67 | 정의 확인, 실제 Python 미확인 |
| `image-to-code` | 이미지→코드 지시문 | 이미지 생성·분석 후 구현 | 시각 중심 웹 brief | 참조 이미지와 코드 | 이미지 생성기, 코딩 에이전트 | image-to-code 1-1192 | 정의 확인, 산출물 미검증 |
| `imagegen-frontend-web` | 이미지 지시문 | 섹션별 웹 참조 이미지 | site type, section count | 가로 이미지 N장 | 이미지 생성기 | imagegen-web 1-976 | 정의 확인, 생성 미검증 |
| `imagegen-frontend-mobile` | 이미지 지시문 | 모바일 화면·흐름 이미지 | app type, platform, screen count | 모바일 이미지 N장 | 이미지 생성기 | imagegen-mobile 1-1419 | 정의 확인, 생성 미검증 |
| `brandkit` | 이미지 지시문 | 브랜드 키트 보드 | brand brief | 브랜드 보드 이미지 | 이미지 생성기 | brandkit 1-780 | 정의 확인, 생성 미검증 |
| `redesign-existing-projects` | 리디자인 지시문 | 감사 후 표적 개선 | 기존 프로젝트 | 개선 코드 | 대상 코드베이스 | redesign 1-178 | 정의 확인, 수정 미검증 |
| `high-end-visual-design` | 구현 지시문 | 부드러운 고급 UI·모션 | UI brief | 코드 지시 | 구현 에이전트 | soft 1-98 | 정의 확인, 결과 미검증 |
| `full-output-enforcement` | 출력 지시문 | 누락/placeholder 방지 | 요청 범위 | 완전 응답 또는 pause | 실행 모델의 토큰 한도 | output 1-49 | 정의 확인, 준수 미검증 |
| `minimalist-ui` | 구현 지시문 | 편집형 미니멀 UI | UI brief | 코드 지시 | 구현 에이전트 | minimalist 1-89 | 정의 확인, 결과 미검증 |
| `industrial-brutalist-ui` | 구현 지시문 | 산업/CRT 스타일 UI | UI brief | 코드 지시 | 구현 에이전트 | brutalist 1-92 | 정의 확인, 결과 미검증 |
| `stitch-design-taste` | 문서 생성 지시문 | Stitch용 DESIGN.md | project intent | DESIGN.md | Google Stitch, 선택적 MCP | stitch 1-184 | 정의 확인, 연동 미검증 |
| `DESIGN.md` | 예시 디자인 문서 | Taste Standard reference | dial values | 정적 디자인 규칙 | Stitch/코딩 에이전트 | stitch DESIGN 1-121 | 파일 확인, 적용 미검증 |

파일명 축약(`imagegen-web`, `soft` 등)의 완전 경로와 줄 범위는 [06-source-evidence.md](06-source-evidence.md)에 있다.
