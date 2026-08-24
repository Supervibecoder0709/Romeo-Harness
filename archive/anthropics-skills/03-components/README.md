# 구성요소 문서 범위

이 레포의 가장 중요한 구성요소는 별도 agent binary가 아니라 19개 `SKILL.md` 정의다. [skill-definitions.ko.md](skill-definitions.ko.md)는 각 정의의 frontmatter를 번역했고, [executable-components.ko.md](executable-components.ko.md)는 그중 실제 스크립트로 확인한 실행·검증 보조 구성요소를 분리했다.

`skills/skill-creator/agents/`의 analyzer, comparator, grader는 agent 역할을 자연어로 정의하지만, 이 Git 트리에서 이들을 자동으로 배정·실행하는 중앙 orchestrator는 확인되지 않았다. 따라서 역할 정의와 실행 보장은 구분해야 한다. [S23]–[S25]

전체 구성요소 맵은 [../04-components-table.md](../04-components-table.md), 모든 원문 근거는 [../06-source-evidence.md](../06-source-evidence.md)에 있다.
