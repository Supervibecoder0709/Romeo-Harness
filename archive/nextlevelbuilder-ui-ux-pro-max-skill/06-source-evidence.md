# 원문 근거 목록

분석 기준 SHA: `bc826e2267a36d98a2dcf5231e16c30ff546770f`. 링크는 모두 이 SHA에 고정돼 있다. 줄 범위는 이 아카이브 작성 시 GitHub raw 원문에 `nl -ba`를 적용해 확인했다.

| ID | 원문 URL | 파일·줄 범위 | 뒷받침하는 사실 |
|---|---|---|---|
| E01 | [commit](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/commit/bc826e2267a36d98a2dcf5231e16c30ff546770f) | commit metadata | main 해석 SHA와 커밋 시각/메시지 |
| E02 | [README](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/bc826e2267a36d98a2dcf5231e16c30ff546770f/README.md) | 219-295, 401-552, 572-649 | 설치/CLI/전제조건, persist 예시, 정본·catalog refresh·troubleshooting |
| E03 | [CLAUDE.md](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/bc826e2267a36d98a2dcf5231e16c30ff546770f/CLAUDE.md) | 41-103 | 정본 `src`, CLI/.claude 복제, sync rules |
| E04 | [주 Skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/bc826e2267a36d98a2dcf5231e16c30ff546770f/.claude/skills/ui-ux-pro-max/SKILL.md) | 1-214 | 적용 범위, 우선순위, 질의/재시도/저장/force 계약, 스킬 실제 수치 |
| E05 | [search.py](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/bc826e2267a36d98a2dcf5231e16c30ff546770f/src/ui-ux-pro-max/scripts/search.py) | 1-171 | CLI 인수, 0건 표현, design-system/stack/domain 분기, JSON 출력 |
| E06 | [core.py](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/bc826e2267a36d98a2dcf5231e16c30ff546770f/src/ui-ux-pro-max/scripts/core.py) | 14-213, 273-402, 405-463, 595-661 | CSV/stack registry, BM25, stable read, threshold/diagnostics, auto domain detection |
| E07 | [CLI package](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/bc826e2267a36d98a2dcf5231e16c30ff546770f/cli/package.json) | 1-62 | `uipro` binary, verify/data test scripts, prepublish gate, runtime dependencies |
| E08 | [CLI init](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/bc826e2267a36d98a2dcf5231e16c30ff546770f/cli/src/commands/init.ts) | 23-225; [update](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/bc826e2267a36d98a2dcf5231e16c30ff546770f/cli/src/commands/update.ts) 38-105 | init 기본 template 방식, legacy download fallback, cwd/global/force/update 동작 |
| E09 | [template utility](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/bc826e2267a36d98a2dcf5231e16c30ff546770f/cli/src/utils/template.ts) | 36-58, 128-325 | assistant mapping, 템플릿 렌더, 복사/덮어쓰기, home global 및 sub-skills |
| E10 | [uninstall](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/bc826e2267a36d98a2dcf5231e16c30ff546770f/cli/src/commands/uninstall.ts) | 18-176 | interactive confirmation, 실제/legacy path 검사, recursive delete |
| E11 | [asset-sync CI](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/bc826e2267a36d98a2dcf5231e16c30ff546770f/.github/workflows/check-asset-sync.yml) | 1-40 | 정본과 cli/.claude 복제본의 content sync check |
| E12 | [reasoning contract](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/bc826e2267a36d98a2dcf5231e16c30ff546770f/src/ui-ux-pro-max/scripts/reasoning_contract.py) | 1-123 | closed decision-rule grammar 및 결정적 적용; 임의 실행 없음 |
| E13 | [design system generator](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/bc826e2267a36d98a2dcf5231e16c30ff546770f/src/ui-ux-pro-max/scripts/design_system.py) | 257-604 | 다중 도메인 검색, style/color mode, 결과/source identity/dials |
| E14 | [data validator](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/bc826e2267a36d98a2dcf5231e16c30ff546770f/src/ui-ux-pro-max/scripts/validate_data.py) | 765-1087 | semantic/provenance/stack 계약과 실패 종료 |
| E15 | [catalog refresh workflow](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/bc826e2267a36d98a2dcf5231e16c30ff546770f/.github/workflows/refresh-catalogs.yml) | 3-19, 38-84, 159-217 | scheduled review-only candidate/diff, secret API key 사용, read-only repo permission |
| E16 | [metadata](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/bc826e2267a36d98a2dcf5231e16c30ff546770f/.claude-plugin/plugin.json) | 1-20; [skill.json](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/bc826e2267a36d98a2dcf5231e16c30ff546770f/skill.json) 1-41 | public plugin/skill version 및 숫자 claims; E04와의 드리프트 |
| E17 | [bundled skills tree](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/tree/bc826e2267a36d98a2dcf5231e16c30ff546770f/.claude/skills) | 각 `*/SKILL.md` | banner/brand/design-system/design/slides/ui-styling 보조 skill 정의 |
| E18 | [stack agent/settings/commands](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/bc826e2267a36d98a2dcf5231e16c30ff546770f/stack/.claude/agents/design-review.md) | 1-95; [design-plan](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/bc826e2267a36d98a2dcf5231e16c30ff546770f/stack/.claude/commands/design-plan.md) 1-26; [mcp](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/bc826e2267a36d98a2dcf5231e16c30ff546770f/stack/.mcp.json) 1-17 | browser-first review, command guidance, `npx ...@latest` MCP external boundary |
| E19 | [design audit](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/bc826e2267a36d98a2dcf5231e16c30ff546770f/stack/scripts/design-audit.mjs) | 1-19, 25-32, 50-133, 165-230 | URL/file input, 6 viewport screenshots, heuristic limits, report files/exit code |
| E20 | [stack setup](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/bc826e2267a36d98a2dcf5231e16c30ff546770f/stack/docs/SETUP.md) | 8-81 | MCP user approval, optional Figma/Magic keys, audit verification |
| E21 | [test workflow](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/bc826e2267a36d98a2dcf5231e16c30ff546770f/.github/workflows/tests.yml) | 1-80 | CI가 aggregate gate, Python regression, Playwright, gallery test/build를 정의 |
| E22 | [CLI README](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/bc826e2267a36d98a2dcf5231e16c30ff546770f/cli/README.md) | 77-101 | CLI README의 개발 명령 및 CC-BY-NC-4.0 라이선스 문구 |

## 테스트 근거 해석

`verify:data`와 CI의 **정의**는 확인했지만, 이 고정 SHA에서 CI가 실제로 통과했다는 결과는 조회/실행하지 않았다. 특히 `validate-agent-guide.py`는 192 product/color/reasoning 행, 스킬 수치, 20 platforms, 잠긴 JSON 예시 3개를 검사하며, `test_data_contracts.py`는 잘못된 decision rule·provenance·catalog drift가 실패하는지 검사한다. 이는 어떤 종류의 회귀를 방지하려는지의 근거이지, 실제 운영 UI의 정확성/접근성이나 현재 외부 API의 최신성을 보장하는 근거는 아니다. [E14][E21]
