# 소스 근거

고정 commit: https://github.com/MengTo/Skills/tree/4c716b516b6b0143f3037631306b3730d2832344  
원본: https://github.com/MengTo/Skills  
라인 번호는 고정 SHA의 raw 파일 기준이다. E17은 Git tree API JSON의 경로 집계이므로 일반 텍스트 줄 범위 대신 API 필드와 재현 단위를 기록했다.

| ID | 원문 URL | 파일·줄 범위 | 이 근거가 뒷받침하는 사실 |
| --- | --- | --- | --- |
| E01 | https://raw.githubusercontent.com/MengTo/Skills/4c716b516b6b0143f3037631306b3730d2832344/README.md | README.md:1-32 | collection 목적, flagship workflow, portable folder 설명 |
| E02 | https://raw.githubusercontent.com/MengTo/Skills/4c716b516b6b0143f3037631306b3730d2832344/README.md | README.md:36-43 | Codex/Claude/Cursor/other agent의 skill 선택·읽기 계약 |
| E03 | https://raw.githubusercontent.com/MengTo/Skills/4c716b516b6b0143f3037631306b3730d2832344/README.md | README.md:152-174 | skill folder contract와 procedural/default/acceptance convention |
| E04 | https://raw.githubusercontent.com/MengTo/Skills/4c716b516b6b0143f3037631306b3730d2832344/README.md | README.md:178-260 | README의 123개/5개 category와 collection별 문서상 수 |
| E05 | https://raw.githubusercontent.com/MengTo/Skills/4c716b516b6b0143f3037631306b3730d2832344/README.md | README.md:264-309 | 새 skill 작성과 maintenance ideas |
| E06 | https://raw.githubusercontent.com/MengTo/Skills/4c716b516b6b0143f3037631306b3730d2832344/CLAUDE.md | CLAUDE.md:7-42 | Claude 기준 folder convention, 안전·작성 workflow |
| E07 | https://raw.githubusercontent.com/MengTo/Skills/4c716b516b6b0143f3037631306b3730d2832344/agent-skills/game-development/README.md | agent-skills/game-development/README.md:1-62 | 게임 skill 선택표와 architecture/combat/asset/QA/release 경계 |
| E08 | https://raw.githubusercontent.com/MengTo/Skills/4c716b516b6b0143f3037631306b3730d2832344/agent-skills/codex/iterate-until-verified/SKILL.md | SKILL.md:1-156 | task contract, gate, work/judgment 분리, evidence loop, honest stop |
| E09 | https://raw.githubusercontent.com/MengTo/Skills/4c716b516b6b0143f3037631306b3730d2832344/agent-skills/codex/publish-project-to-github/SKILL.md | SKILL.md:1-228 | public/push/Pages authority, audit, verification, failure rules |
| E10 | https://raw.githubusercontent.com/MengTo/Skills/4c716b516b6b0143f3037631306b3730d2832344/agent-skills/game-development/ship-web-games/SKILL.md | SKILL.md:1-23 | exact commit release, production proof, rollback evidence |
| E11 | https://raw.githubusercontent.com/MengTo/Skills/4c716b516b6b0143f3037631306b3730d2832344/agent-skills/web-design/build-awwwards-quality-sites/SKILL.md | SKILL.md:1-65 | originality, asset provenance, accessibility, motion, WebGL, validation guardrails |
| E12 | https://raw.githubusercontent.com/MengTo/Skills/4c716b516b6b0143f3037631306b3730d2832344/scripts/validate-skill-demos.mjs | scripts/validate-skill-demos.mjs:8-20,60-185,188-232 | git skill discovery, demo contract, static checks, index checks, exit semantics |
| E13 | https://raw.githubusercontent.com/MengTo/Skills/4c716b516b6b0143f3037631306b3730d2832344/scripts/backfill-skill-demos.mjs | scripts/backfill-skill-demos.mjs:8-18,831-948 | force, source-derived preservation, demo/DEMOS write |
| E14 | https://raw.githubusercontent.com/MengTo/Skills/4c716b516b6b0143f3037631306b3730d2832344/scripts/build-demo-screenshot-gallery.mjs | scripts/build-demo-screenshot-gallery.mjs:8-18,56-68,86-127 | preview requirement, SCREENSHOTS.md/HTML generation |
| E15 | https://raw.githubusercontent.com/MengTo/Skills/4c716b516b6b0143f3037631306b3730d2832344/scripts/test-sync-neuform-security.mjs | scripts/test-sync-neuform-security.mjs:1-19,21-117,123-155 | IP/HTTPS/allowlist, sandbox/CSP, URL sanitization, manifest/checksum test |
| E16 | https://raw.githubusercontent.com/MengTo/Skills/4c716b516b6b0143f3037631306b3730d2832344/scripts/sync-neuform-skill-demos.mjs | scripts/sync-neuform-skill-demos.mjs:758-806,882-924,943-944 | manifest/write phase, dry-run, env/API/key/host setup, results |
| E17 | https://api.github.com/repos/MengTo/Skills/git/trees/4c716b516b6b0143f3037631306b3730d2832344?recursive=1 | tree[].path, 891 blob paths | SKILL.md 130, agents/openai.yaml 63, category counts 19/20/2/1/88, no .github/workflows candidate |
| E18 | https://raw.githubusercontent.com/MengTo/Skills/4c716b516b6b0143f3037631306b3730d2832344/agent-skills/codex/stitched-full-page-capture/scripts/stitch_full_page_capture.mjs | stitch helper:7-17,74-184 | manifest CLI, Playwright/ffmpeg/sips, images/manifest write and cleanup |
| E19 | https://raw.githubusercontent.com/MengTo/Skills/4c716b516b6b0143f3037631306b3730d2832344/agent-skills/codex/audit-reference-originality/scripts/build_evidence_inventory.py | inventory helper:1-90,112-163 | local site/reference inputs, skip dirs, hash/file classification |
| E20 | https://raw.githubusercontent.com/MengTo/Skills/4c716b516b6b0143f3037631306b3730d2832344/agent-skills/codex/iterate-until-verified/agents/openai.yaml | openai.yaml:1-4 | display_name, short_description, default_prompt metadata schema example |
| E21 | https://raw.githubusercontent.com/MengTo/Skills/4c716b516b6b0143f3037631306b3730d2832344/DEMOS.md | DEMOS.md:1-27,55-60 | 모든 tracked skill demo라는 설명과 총 89개라는 문서상 coverage |
