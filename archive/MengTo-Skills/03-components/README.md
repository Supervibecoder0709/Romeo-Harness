# 핵심 구성요소 번역·해설

이 디렉터리는 130개 전체 skill의 재번역본이 아니다. 코드·설정·테스트 경계까지 실제로 연 대표 skill 4개의 한국어 번역과 라이브러리의 중심 계약을 담는다.

| 파일 | 원문 | 선정 이유 |
| --- | --- | --- |
| iterate-until-verified.ko.md | agent-skills/codex/iterate-until-verified/SKILL.md | Harness의 contract, quality gate, evidence loop를 가장 직접적으로 정의 |
| publish-project-to-github.ko.md | agent-skills/codex/publish-project-to-github/SKILL.md | public/push/Pages의 고위험 외부 쓰기 승인/검증 경계 |
| ship-web-games.ko.md | agent-skills/game-development/ship-web-games/SKILL.md | local readiness와 deployed proof를 분리한 release 계약 |
| build-awwwards-quality-sites.ko.md | agent-skills/web-design/build-awwwards-quality-sites/SKILL.md | reference originality, asset provenance, accessibility, performance의 제작 경계 |

agents/openai.yaml은 63개 경로에 존재하나 이 아카이브에서는 대표 4개만 실제 본문을 열었다. 예시는 interface.display_name, short_description, default_prompt이며 특정 host에서의 discovery/실행 여부는 확인하지 않았다. [E20]
